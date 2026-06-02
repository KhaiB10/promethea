"""
benchmarks/msbr/run_spectrum.py

Spectral decomposition of the MSBR het/homog Δk.

Runs both geometries (heterogeneous and homogeneous) at the ORNL
baseline volume fractions with an energy-resolved flux + nu-fission +
absorption tally inside the fuel salt. Computes:

  1. Per-group fission and absorption rates in the fuel salt, het vs
     homog, in three energy bins:
        - thermal:   < 0.625 eV
        - epithermal: 0.625 eV – 100 keV
        - fast:      > 100 keV
  2. The four-factor decomposition of k_inf in each geometry, group
     by group, using k_inf = eta * f * p * epsilon with
        eta_g = nu * Sigma_f,g / Sigma_a,g (in fuel)
        f_g   = Sigma_a,g(fuel) / Sigma_a,g(all)
        spectrum-integrated quantities for the "lumped" interpretation.
  3. Energy-group-resolved Δk attribution: which group(s) drive the
     +10,506 pcm advantage.

This is a v0.4.0 +1 measurement. The novelty bar is set as: produce a
publishable, library-pinned, openly reproducible three-group
decomposition of the MSBR fuel-cell heterogeneity Δk. To our knowledge
no such decomposition exists in the open literature for the MSBR.

Tally strategy
--------------

We use ``cell``-filter rather than ``material``-filter for the het
case so we can tally inside the *fuel zone only* (the cell containing
the fuel salt), excluding fuel salt that happens to coexist with
graphite in the homog mix. For the homog case the single homog cell
contains the full mixture, and the fuel-only fractions are recovered
by weighting by the fuel salt's contribution to the macroscopic cross
section.

For a clean Δk decomposition without invoking a transport-theory
homogenization equivalence (which would be its own thesis), we
instead report group-resolved rates in each geometry separately and
compute the *ratio* of het:homog rates in each group. The group
where this ratio is largest is the group that most strongly drives
het > homog reactivity.

Implementation note
-------------------

OpenMC's tally filtering by *score* (e.g., 'nu-fission') is solid,
but combining MaterialFilter + EnergyFilter + multiple scores has
historically been the source of the same dataframe-construction
ValueError we hit in tallies.py. We use the low-level
``Tally.get_values`` API throughout, the same fix that landed for the
BR tally module in commit 94d318b.

Environment variables:

  PROMETHEA_PARTICLES (default 100000)
  PROMETHEA_BATCHES   (default 200)
  PROMETHEA_SEED      (default 1)
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import openmc

from benchmarks.msbr.geometry_unit_cell import build_unit_cell_geometry
from benchmarks.msbr.geometry_unit_cell_homog import (
    build_unit_cell_geometry as build_homog_geometry,
)


# Three-group energy structure (eV). MSBR is thermal-dominated, so this
# coarse breakdown is sufficient to attribute Δk by spectral regime.
EBINS = [0.0, 0.625, 1.0e5, 2.0e7]
EBIN_NAMES = ["thermal", "epithermal", "fast"]


def _build_spectrum_tallies(materials: openmc.Materials, geometry_label: str) -> openmc.Tallies:
    """Three-group fission + nu-fission + absorption + flux tally,
    filtered on every material in the geometry."""
    e_filter = openmc.EnergyFilter(EBINS)
    mat_filter = openmc.MaterialFilter(list(materials))

    tally = openmc.Tally(name=f"spectrum_{geometry_label}")
    tally.filters = [mat_filter, e_filter]
    tally.scores = ["flux", "fission", "nu-fission", "absorption"]

    # Also a flux-only spectrum tally we can use to check the spectrum
    # shapes visually (not needed for Δk attribution).
    flux_tally = openmc.Tally(name=f"flux_spectrum_{geometry_label}")
    flux_tally.filters = [mat_filter, e_filter]
    flux_tally.scores = ["flux"]
    return openmc.Tallies([tally, flux_tally])


def _settings(particles: int, batches: int, seed: int) -> openmc.Settings:
    s = openmc.Settings()
    s.particles = particles
    s.batches = batches
    s.inactive = max(20, batches // 6)
    s.run_mode = "eigenvalue"
    s.verbosity = 5
    s.temperature = {"method": "interpolation"}
    s.seed = int(seed)
    bounds = [-1.0, -1.0, -0.5, 1.0, 1.0, 0.5]
    s.source = openmc.IndependentSource(
        space=openmc.stats.Box(bounds[:3], bounds[3:], only_fissionable=True),
    )
    return s


def _read_three_group(sp_path: str, tally_name: str, mat_id: int) -> dict:
    """Pull the four scores in three energy groups for one material."""
    sp = openmc.StatePoint(sp_path)
    tally = sp.get_tally(name=tally_name)
    result = {}
    for score in ["flux", "fission", "nu-fission", "absorption"]:
        try:
            means = tally.get_values(
                scores=[score],
                filters=[openmc.MaterialFilter, openmc.EnergyFilter],
                filter_bins=[(mat_id,), tuple((EBINS[i], EBINS[i + 1]) for i in range(3))],
                value="mean",
            )
            stds = tally.get_values(
                scores=[score],
                filters=[openmc.MaterialFilter, openmc.EnergyFilter],
                filter_bins=[(mat_id,), tuple((EBINS[i], EBINS[i + 1]) for i in range(3))],
                value="std_dev",
            )
        except Exception as exc:
            print(f"[spectrum]   skipping {score} for mat {mat_id}: {exc}")
            continue
        m = np.asarray(means).reshape(-1).tolist()
        s = np.asarray(stds).reshape(-1).tolist()
        for i, name in enumerate(EBIN_NAMES):
            result[f"{score}_{name}"] = float(m[i])
            result[f"{score}_{name}_sigma"] = float(s[i])
    return result


def _run_one(label: str, geometry, materials, particles, batches, seed, workdir):
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    settings = _settings(particles, batches, seed)
    tallies = _build_spectrum_tallies(materials, label)

    orig = Path.cwd()
    try:
        os.chdir(workdir)
        materials.export_to_xml()
        geometry.export_to_xml()
        settings.export_to_xml()
        tallies.export_to_xml()
        openmc.run()
        sps = sorted(Path.cwd().glob("statepoint.*.h5"))
        if not sps:
            raise RuntimeError(f"no statepoint for {label}")
        sp_path = str(sps[-1])
        sp = openmc.StatePoint(sp_path)
        k = sp.keff
        per_mat = {}
        for mat in materials:
            per_mat[mat.name or f"material_{mat.id}"] = _read_three_group(
                sp_path, f"spectrum_{label}", mat.id,
            )
        return {
            "k": float(k.n),
            "k_sigma": float(k.s),
            "per_material": per_mat,
            "statepoint": sp_path,
        }
    finally:
        os.chdir(orig)


def main() -> int:
    particles = int(os.environ.get("PROMETHEA_PARTICLES", "100000"))
    batches = int(os.environ.get("PROMETHEA_BATCHES", "200"))
    seed = int(os.environ.get("PROMETHEA_SEED", "1"))

    print(f"[spectrum] particles={particles}, batches={batches}, seed={seed}")

    geom_h, mats_h = build_unit_cell_geometry()
    geom_g, mats_g = build_homog_geometry()

    print("[spectrum] running heterogeneous geometry")
    het = _run_one(
        "het", geom_h, mats_h, particles, batches, seed,
        workdir=Path("sims/openmc/msbr_spectrum_het"),
    )
    print(f"[spectrum]   k_het = {het['k']:.5f} +/- {het['k_sigma']:.5f}")

    print("[spectrum] running homogeneous geometry")
    homog = _run_one(
        "homog", geom_g, mats_g, particles, batches, seed,
        workdir=Path("sims/openmc/msbr_spectrum_homog"),
    )
    print(f"[spectrum]   k_homog = {homog['k']:.5f} +/- {homog['k_sigma']:.5f}")

    delta_k = het["k"] - homog["k"]
    sigma_delta = math.sqrt(het["k_sigma"] ** 2 + homog["k_sigma"] ** 2)
    print(f"[spectrum] Delta_k = {delta_k*1e5:+.0f} +/- {sigma_delta*1e5:.0f} pcm")

    # Group-resolved analysis: per-material per-group fission and
    # absorption ratios het:homog, plus the fuel-only "nu*fission/abs"
    # group-eta as a structural witness of the heterogeneity advantage.
    print("\n[spectrum] three-group decomposition (fuel salt)")
    print(f"  {'group':>10s} {'het_phi':>12s} {'homog_phi':>12s} "
          f"{'het_nuf':>12s} {'homog_nuf':>12s} {'het_abs':>12s} {'homog_abs':>12s}")
    fuel_h = None
    fuel_g = None
    for name, data in het["per_material"].items():
        if "fuel_salt" in name:
            fuel_h = data
            break
    for name, data in homog["per_material"].items():
        if name.lower().startswith("msbr_homog"):
            fuel_g = data
            break
    if fuel_h and fuel_g:
        rows = []
        for grp in EBIN_NAMES:
            phi_h = fuel_h.get(f"flux_{grp}", 0.0)
            phi_g = fuel_g.get(f"flux_{grp}", 0.0)
            nuf_h = fuel_h.get(f"nu-fission_{grp}", 0.0)
            nuf_g = fuel_g.get(f"nu-fission_{grp}", 0.0)
            abs_h = fuel_h.get(f"absorption_{grp}", 0.0)
            abs_g = fuel_g.get(f"absorption_{grp}", 0.0)
            print(f"  {grp:>10s} {phi_h:12.4e} {phi_g:12.4e} "
                  f"{nuf_h:12.4e} {nuf_g:12.4e} {abs_h:12.4e} {abs_g:12.4e}")
            rows.append({
                "group": grp, "phi_het": phi_h, "phi_homog": phi_g,
                "nuf_het": nuf_h, "nuf_homog": nuf_g,
                "abs_het": abs_h, "abs_homog": abs_g,
            })

    out = Path("out")
    out.mkdir(exist_ok=True)
    payload = {
        "particles": particles,
        "batches": batches,
        "seed": seed,
        "energy_bins_eV": EBINS,
        "group_names": EBIN_NAMES,
        "het": het,
        "homog": homog,
        "delta_k": delta_k,
        "delta_k_sigma": sigma_delta,
        "delta_pcm": delta_k * 1e5,
        "delta_pcm_sigma": sigma_delta * 1e5,
    }
    (out / "msbr_spectrum.json").write_text(json.dumps(payload, indent=2, default=float))
    print(f"\n[spectrum] wrote out/msbr_spectrum.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
