"""
benchmarks/msbr/run_temp_sweep.py

Two-point temperature sweep on the heterogeneous MSBR unit cell.
Computes a finite-difference temperature coefficient:

    alpha = (1/k_ref) * (k_hi - k_lo) / (T_hi - T_lo)

with combined statistical uncertainty:

    sigma_alpha = (1/k_ref) * sqrt(sigma_k_hi^2 + sigma_k_lo^2) / dT

ORNL-4528 Table 6.8 reports an overall isothermal temperature
coefficient alpha_overall = -4.34e-5 per degree Kelvin for the
reference design (sum of fuel-salt and graphite contributions).
The UNIT CELL value will not match the reactor value -- there's no
blanket region, no leakage, and no reflector -- but the SIGN must
be negative (a strongly thermal-spectrum graphite-moderated 233U
cell is overwhelmingly driven by Doppler broadening of 232Th and
spectrum shifts as graphite heats up). A negative cell-level alpha
is a necessary-not-sufficient condition for the reactor alpha to
match.

Inputs (env vars):
  PROMETHEA_PARTICLES   particles per batch (default 20000)
  PROMETHEA_BATCHES     total batches (default 60)
  PROMETHEA_SEED        optional positive int for RNG
  PROMETHEA_TEMP_LO_K   low temperature in K (default 900)
  PROMETHEA_TEMP_HI_K   high temperature in K (default 1200)
  OPENMC_CROSS_SECTIONS path to cross_sections.xml (required)

Output:
  sims/openmc/msbr_temp_lo/    -- low-T statepoint
  sims/openmc/msbr_temp_hi/    -- high-T statepoint
  out/msbr_temp_sweep.log      -- captured stdout
  out/msbr_temp_sweep.json     -- structured result
"""
from __future__ import annotations

import json
import math
import os
import pathlib
import sys

import openmc

from .geometry_unit_cell import build_unit_cell_geometry


def _run_one(work_dir: pathlib.Path, temp_K: float, *,
             particles: int, batches: int, inactive: int,
             seed: int | None) -> tuple[float, float]:
    """Run a single eigenvalue calc at temp_K. Returns (k, sigma)."""
    work_dir.mkdir(parents=True, exist_ok=True)
    here = os.getcwd()
    os.chdir(work_dir)
    try:
        geometry, materials = build_unit_cell_geometry(temp_K=temp_K)
        settings = openmc.Settings()
        settings.particles = particles
        settings.batches = batches
        settings.inactive = inactive
        settings.run_mode = "eigenvalue"
        settings.verbosity = 6
        # Interpolate S(alpha,beta) between fixed-grid temperatures
        # in the library; required for temperatures between the
        # ENDF/B grid points (296/400/.../2000 K).
        settings.temperature = {"method": "interpolation"}
        if seed is not None:
            settings.seed = seed
        bounds = [-1.0, -1.0, -0.5, 1.0, 1.0, 0.5]
        settings.source = openmc.IndependentSource(
            space=openmc.stats.Box(bounds[:3], bounds[3:],
                                   only_fissionable=True)
        )

        materials.export_to_xml()
        geometry.export_to_xml()
        settings.export_to_xml()

        openmc.run()

        # Find the latest statepoint
        sps = sorted(pathlib.Path(".").glob("statepoint.*.h5"))
        if not sps:
            raise RuntimeError(f"no statepoint produced at T = {temp_K} K")
        sp = openmc.StatePoint(str(sps[-1]))
        return float(sp.keff.nominal_value), float(sp.keff.std_dev)
    finally:
        os.chdir(here)


def main() -> int:
    particles = int(os.environ.get("PROMETHEA_PARTICLES", 20000))
    batches = int(os.environ.get("PROMETHEA_BATCHES", 60))
    inactive = max(10, batches // 6)
    seed_env = os.environ.get("PROMETHEA_SEED", "").strip()
    seed = int(seed_env) if seed_env else None
    T_lo = float(os.environ.get("PROMETHEA_TEMP_LO_K", 900.0))
    T_hi = float(os.environ.get("PROMETHEA_TEMP_HI_K", 1200.0))

    if T_hi <= T_lo:
        print(f"[temp_sweep] ERROR: T_hi ({T_hi}) must exceed T_lo ({T_lo})")
        return 2

    print(f"[temp_sweep] particles/batch = {particles}")
    print(f"[temp_sweep] total batches   = {batches}  (inactive: {inactive})")
    print(f"[temp_sweep] T_lo = {T_lo} K")
    print(f"[temp_sweep] T_hi = {T_hi} K")
    if seed is not None:
        print(f"[temp_sweep] seed            = {seed}")

    repo_root = pathlib.Path.cwd()
    work_lo = repo_root / "sims/openmc/msbr_temp_lo"
    work_hi = repo_root / "sims/openmc/msbr_temp_hi"

    print(f"\n[temp_sweep] === low-T run @ {T_lo} K ===")
    k_lo, s_lo = _run_one(work_lo, T_lo,
                          particles=particles, batches=batches,
                          inactive=inactive, seed=seed)

    print(f"\n[temp_sweep] === high-T run @ {T_hi} K ===")
    k_hi, s_hi = _run_one(work_hi, T_hi,
                          particles=particles, batches=batches,
                          inactive=inactive, seed=seed)

    # Reference k for the (1/k) factor: arithmetic mean of the two.
    k_ref = 0.5 * (k_lo + k_hi)
    dT = T_hi - T_lo
    delta_k = k_hi - k_lo
    sigma_delta = math.sqrt(s_lo ** 2 + s_hi ** 2)
    alpha = delta_k / (k_ref * dT)
    sigma_alpha = sigma_delta / (k_ref * dT)
    z = abs(alpha) / sigma_alpha if sigma_alpha > 0 else float("inf")

    print("\n" + "=" * 56)
    print("MSBR unit-cell temperature coefficient (two-point FD)")
    print("=" * 56)
    print(f"  k({T_lo:.0f} K) = {k_lo:.5f} +/- {s_lo:.5f}")
    print(f"  k({T_hi:.0f} K) = {k_hi:.5f} +/- {s_hi:.5f}")
    print(f"  dT          = {dT:.0f} K")
    print(f"  Delta_k     = {delta_k:+.5f} +/- {sigma_delta:.5f}")
    print(f"  alpha       = ({alpha:+.3e} +/- {sigma_alpha:.1e}) /K")
    print(f"  z-score     = {z:.1f}")
    if alpha < 0 and z >= 3.0:
        print("  -> Negative and statistically significant (good sign)")
    elif z < 3.0:
        print("  -> NOT statistically resolved; increase statistics")
    print()
    print("Reference (ORNL-4528 Table 6.8, REACTOR not cell):")
    print("  alpha_overall = -4.34e-5 /K")

    out_dir = repo_root / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "msbr_temp_sweep.json").write_text(json.dumps({
        "T_lo_K": T_lo, "T_hi_K": T_hi,
        "k_lo": k_lo, "sigma_k_lo": s_lo,
        "k_hi": k_hi, "sigma_k_hi": s_hi,
        "delta_k": delta_k, "sigma_delta_k": sigma_delta,
        "alpha_per_K": alpha, "sigma_alpha_per_K": sigma_alpha,
        "z_score": z,
        "particles": particles, "batches": batches, "inactive": inactive,
        "seed": seed,
        "ornl_reactor_alpha_overall": -4.34e-5,
    }, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
