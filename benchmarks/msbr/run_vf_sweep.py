"""
benchmarks/msbr/run_vf_sweep.py

Volume-fraction sweep driver. For each (f_fuel, f_blanket) grid point
this script:

  1. Builds the heterogeneous geometry at the target volume fractions.
  2. Runs OpenMC k_inf.
  3. Builds the volume-mixed homogeneous companion at the same
     fractions.
  4. Runs OpenMC k_inf on it.
  5. Computes Δk = k_het − k_homog with combined-σ.

A single CSV is emitted to ``out/msbr_vf_sweep.csv`` with one row per
grid point, plus a JSON log of all geometry metadata for downstream
analysis. The CSV is the input for ``scripts/analysis/vf_sweep.py``,
which fits a 2-D surface and locates the Δk maximum.

The grid is intentionally coarse for a first run — 9 points around
the ORNL baseline (3×3 in (f_fuel, f_blanket) space, ±50 % about the
ORNL values, clamped to f_graphite ≥ 0.70). Refine once the macro
structure of the Δk surface is known.

Environment variables (set by the CI workflow):

  PROMETHEA_PARTICLES  per-batch particle count (default 50000)
  PROMETHEA_BATCHES    total batches (default 120)
  PROMETHEA_SEED       random seed (default 1)
  PROMETHEA_VF_GRID    "coarse" (default), "fine", or "single"
                       fine = 5x5 grid (25 points), expensive
                       single = one point at ORNL baseline (smoke test)

Run inside the same Docker image as the rest of the v0.4.0 runners.
"""
from __future__ import annotations

import csv
import json
import math
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import openmc

from benchmarks.msbr.geometry_vf_sweep import (
    ORNL_VF,
    build_vf_geometry,
    build_vf_geometry_homog,
)


def run_eigenvalue(
    *,
    geometry: openmc.Geometry,
    materials: openmc.Materials,
    particles: int,
    batches: int,
    seed: int,
    cwd: Path,
    tag: str,
) -> tuple[float, float]:
    """Run a single OpenMC eigenvalue calculation in ``cwd`` and return
    (k_combined, sigma_k_combined).

    Side-effect-free aside from writing OpenMC XML/H5 into ``cwd``.
    """
    inactive = max(10, batches // 6)
    settings = openmc.Settings()
    settings.particles = particles
    settings.batches = batches
    settings.inactive = inactive
    settings.run_mode = "eigenvalue"
    settings.verbosity = 5
    settings.temperature = {"method": "interpolation"}
    settings.seed = int(seed)
    bounds = [-1.0, -1.0, -0.5, 1.0, 1.0, 0.5]
    settings.source = openmc.IndependentSource(
        space=openmc.stats.Box(bounds[:3], bounds[3:], only_fissionable=True),
    )

    orig_cwd = Path.cwd()
    try:
        os.chdir(cwd)
        materials.export_to_xml()
        geometry.export_to_xml()
        settings.export_to_xml()
        openmc.run()
        sp_paths = sorted(Path.cwd().glob("statepoint.*.h5"))
        if not sp_paths:
            raise RuntimeError(f"no statepoint produced for {tag}")
        sp = openmc.StatePoint(str(sp_paths[-1]))
        k = sp.keff
        return float(k.n), float(k.s)
    finally:
        os.chdir(orig_cwd)


# -----------------------------------------------------------------------------
# Grid definition
# -----------------------------------------------------------------------------

ORNL_FUEL = ORNL_VF["fuel"]      # ~0.1222
ORNL_BLANKET = ORNL_VF["blanket"]  # ~0.0640


def _coarse_grid() -> list[tuple[float, float]]:
    """3x3 grid around the ORNL baseline."""
    fuels = [ORNL_FUEL * 0.6, ORNL_FUEL, ORNL_FUEL * 1.5]
    blankets = [ORNL_BLANKET * 0.5, ORNL_BLANKET, ORNL_BLANKET * 1.8]
    pts = []
    for f in fuels:
        for b in blankets:
            if (1.0 - f - b) >= 0.70:
                pts.append((f, b))
    return pts


def _fine_grid() -> list[tuple[float, float]]:
    """5x5 grid covering a wider region, clamped to graphite >= 0.70."""
    fuels = [0.05, 0.09, ORNL_FUEL, 0.18, 0.25]
    blankets = [0.02, 0.05, ORNL_BLANKET, 0.10, 0.18]
    pts = []
    for f in fuels:
        for b in blankets:
            if (1.0 - f - b) >= 0.70:
                pts.append((f, b))
    return pts


def _single_grid() -> list[tuple[float, float]]:
    return [(ORNL_FUEL, ORNL_BLANKET)]


def _corner_grid() -> list[tuple[float, float]]:
    """Just the high-fuel/high-blanket corner from the coarse 3×3 grid.

    Used to reproduce the v0.4.0 Δk-max grid point with an independent
    seed for confirmation."""
    return [(0.1832, 0.1152)]


def get_grid() -> list[tuple[float, float]]:
    mode = os.environ.get("PROMETHEA_VF_GRID", "coarse").strip().lower()
    if mode == "fine":
        return _fine_grid()
    if mode == "single":
        return _single_grid()
    if mode == "corner":
        return _corner_grid()
    return _coarse_grid()


# -----------------------------------------------------------------------------
# Per-point runner
# -----------------------------------------------------------------------------

def _run_one(
    f_fuel: float,
    f_blanket: float,
    *,
    particles: int,
    batches: int,
    seed: int,
    workdir_root: Path,
) -> dict:
    """Run het + homog at this (f_fuel, f_blanket); return result dict."""
    point_tag = f"f{f_fuel:.4f}_b{f_blanket:.4f}"
    point_dir = workdir_root / point_tag
    point_dir.mkdir(parents=True, exist_ok=True)

    # --- HET ---
    het_dir = point_dir / "het"
    het_dir.mkdir(exist_ok=True)
    geom_h, mats_h, info_h = build_vf_geometry(f_fuel, f_blanket)
    k_het, sigma_het = run_eigenvalue(
        geometry=geom_h,
        materials=mats_h,
        particles=particles,
        batches=batches,
        seed=seed,
        cwd=het_dir,
        tag=f"het_{point_tag}",
    )

    # --- HOMOG ---
    homog_dir = point_dir / "homog"
    homog_dir.mkdir(exist_ok=True)
    geom_g, mats_g, info_g = build_vf_geometry_homog(f_fuel, f_blanket)
    k_homog, sigma_homog = run_eigenvalue(
        geometry=geom_g,
        materials=mats_g,
        particles=particles,
        batches=batches,
        seed=seed,
        cwd=homog_dir,
        tag=f"homog_{point_tag}",
    )

    delta_k = k_het - k_homog
    sigma_delta = math.sqrt(sigma_het ** 2 + sigma_homog ** 2)
    delta_pcm = delta_k * 1e5
    sigma_pcm = sigma_delta * 1e5

    return {
        "f_fuel": f_fuel,
        "f_blanket": f_blanket,
        "f_graphite": 1.0 - f_fuel - f_blanket,
        "k_het": k_het,
        "sigma_k_het": sigma_het,
        "k_homog": k_homog,
        "sigma_k_homog": sigma_homog,
        "delta_k": delta_k,
        "sigma_delta_k": sigma_delta,
        "delta_pcm": delta_pcm,
        "sigma_pcm": sigma_pcm,
        "info_het": info_h,
        "info_homog": info_g,
    }


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> int:
    particles = int(os.environ.get("PROMETHEA_PARTICLES", "50000"))
    batches = int(os.environ.get("PROMETHEA_BATCHES", "120"))
    seed = int(os.environ.get("PROMETHEA_SEED", "1"))

    grid = get_grid()
    grid_name = os.environ.get("PROMETHEA_VF_GRID", "coarse")

    out_root = Path("sims/openmc/msbr_vf_sweep")
    out_root.mkdir(parents=True, exist_ok=True)
    results_dir = Path("out")
    results_dir.mkdir(exist_ok=True)

    print(f"[vf_sweep] grid={grid_name}  points={len(grid)}")
    print(f"[vf_sweep] particles={particles}  batches={batches}  seed={seed}")
    print(f"[vf_sweep] ORNL baseline: f_fuel={ORNL_FUEL:.4f} "
          f"f_blanket={ORNL_BLANKET:.4f} "
          f"f_graphite={1 - ORNL_FUEL - ORNL_BLANKET:.4f}")
    print()

    rows: list[dict] = []
    t0 = time.time()
    for i, (f_fuel, f_blanket) in enumerate(grid, 1):
        print(f"[vf_sweep] ---- point {i}/{len(grid)}: "
              f"f_fuel={f_fuel:.4f} f_blanket={f_blanket:.4f} "
              f"f_graphite={1 - f_fuel - f_blanket:.4f} ----")
        sys.stdout.flush()
        try:
            row = _run_one(
                f_fuel, f_blanket,
                particles=particles, batches=batches, seed=seed,
                workdir_root=out_root,
            )
        except Exception as exc:
            print(f"[vf_sweep]   FAIL at this point: {type(exc).__name__}: {exc}")
            row = {
                "f_fuel": f_fuel,
                "f_blanket": f_blanket,
                "f_graphite": 1.0 - f_fuel - f_blanket,
                "error": f"{type(exc).__name__}: {exc}",
            }
        else:
            print(f"[vf_sweep]   k_het={row['k_het']:.5f} +/- {row['sigma_k_het']:.5f}")
            print(f"[vf_sweep]   k_homog={row['k_homog']:.5f} +/- {row['sigma_k_homog']:.5f}")
            print(f"[vf_sweep]   Delta_k={row['delta_pcm']:+.0f} +/- {row['sigma_pcm']:.0f} pcm")
        rows.append(row)
        # Free disk between points so we don't run out
        for sub in (out_root.glob("*/het/statepoint.*.h5"),
                    out_root.glob("*/homog/statepoint.*.h5")):
            for sp in sub:
                # Keep only the most recent point's statepoints for forensics
                if sp.parent.parent.name != f"f{f_fuel:.4f}_b{f_blanket:.4f}":
                    try:
                        sp.unlink()
                    except OSError:
                        pass

    elapsed = time.time() - t0
    print(f"\n[vf_sweep] done in {elapsed/60:.1f} min")

    # ------ Write CSV ------
    csv_path = results_dir / "msbr_vf_sweep.csv"
    fieldnames = [
        "f_fuel", "f_blanket", "f_graphite",
        "k_het", "sigma_k_het",
        "k_homog", "sigma_k_homog",
        "delta_k", "sigma_delta_k",
        "delta_pcm", "sigma_pcm",
        "error",
    ]
    with csv_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})
    print(f"[vf_sweep] wrote {csv_path}")

    # ------ Write JSON log (full metadata) ------
    json_path = results_dir / "msbr_vf_sweep.json"
    payload = {
        "grid": grid_name,
        "particles": particles,
        "batches": batches,
        "seed": seed,
        "ornl_baseline": {
            "f_fuel": ORNL_FUEL,
            "f_blanket": ORNL_BLANKET,
            "f_graphite": 1.0 - ORNL_FUEL - ORNL_BLANKET,
        },
        "points": rows,
    }
    json_path.write_text(json.dumps(payload, indent=2, default=float))
    print(f"[vf_sweep] wrote {json_path}")

    # ------ Stdout summary ------
    print("\n[vf_sweep] summary table")
    print(f"  {'f_fuel':>8s} {'f_blanket':>9s} {'f_graphite':>10s} "
          f"{'k_het':>10s} {'k_homog':>10s} {'Delta_k pcm':>14s}")
    for r in rows:
        if "error" in r:
            print(f"  {r['f_fuel']:8.4f} {r['f_blanket']:9.4f} "
                  f"{r['f_graphite']:10.4f}   FAIL: {r['error']}")
        else:
            print(f"  {r['f_fuel']:8.4f} {r['f_blanket']:9.4f} "
                  f"{r['f_graphite']:10.4f} "
                  f"{r['k_het']:10.5f} {r['k_homog']:10.5f} "
                  f"{r['delta_pcm']:+8.0f} +/-{r['sigma_pcm']:5.0f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
