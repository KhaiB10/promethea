"""
benchmarks/msre/run_criticality.py

Phase 1.1 acceptance test: run the homogenized MSRE v0 model in OpenMC
and report k-eff vs the published acceptance envelope.

Usage:
    python benchmarks/msre/run_criticality.py [--quick]

Outputs:
    sims/openmc/msre_v0/  (XML inputs, statepoint file)
    A summary line on stdout with k-eff and a PASS/FAIL banner.

Acceptance for the homogenized v0 model:
    k-eff in the range 1.00 - 1.15 (loose — this is a homogenized core,
    expect significantly higher than the heterogeneous benchmark value).

The heterogeneous-CSG follow-up (Phase 1.1.b) tightens this to:
    k-eff = 1.020 +/- 0.002 (matches published OpenMC CSG figures).
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

try:
    import openmc
except ImportError:
    print("ERROR: OpenMC is not installed in this environment.", file=sys.stderr)
    print("       Use the Docker image or `micromamba install -c conda-forge openmc`.",
          file=sys.stderr)
    sys.exit(1)

# Make the benchmarks/msre directory importable when run as a script.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from materials import build_all, BENCHMARK_TEMP_K  # noqa: E402
from geometry import build_geometry, ACTIVE_CORE_HEIGHT, CORE_RADIUS  # noqa: E402


def build_model(quick: bool = False) -> openmc.Model:
    mats_dict, mats = build_all(temperature_K=BENCHMARK_TEMP_K)
    geometry, extra_mats = build_geometry(mats_dict)
    for em in extra_mats:
        mats.append(em)

    settings = openmc.Settings()
    settings.temperature = {"method": "interpolation",
                            "range": (293.15, 1200.0)}
    if quick:
        settings.batches = 30
        settings.inactive = 10
        settings.particles = 5_000
    else:
        settings.batches = 120
        settings.inactive = 30
        settings.particles = 50_000

    # CI / env overrides — let the GitHub Actions workflow scale runs
    # without code edits. Inactive batches scale with total batches.
    env_batches = os.environ.get("PROMETHEA_BATCHES")
    env_particles = os.environ.get("PROMETHEA_PARTICLES")
    if env_batches:
        b = int(env_batches)
        settings.batches = b
        settings.inactive = max(10, b // 4)
    if env_particles:
        settings.particles = int(env_particles)
    print(f"[msre_v0] settings: batches={settings.batches} "
          f"inactive={settings.inactive} particles={settings.particles}")

    # Initial source — a thin slab through the middle of the active core,
    # restricted to fissionable material to get a fast initial guess.
    src_box = openmc.stats.Box(
        [-CORE_RADIUS * 0.8, -CORE_RADIUS * 0.8, ACTIVE_CORE_HEIGHT * 0.25],
        [+CORE_RADIUS * 0.8, +CORE_RADIUS * 0.8, ACTIVE_CORE_HEIGHT * 0.75],
        only_fissionable=True,
    )
    settings.source = openmc.IndependentSource(space=src_box)
    settings.output = {"summary": False}

    return openmc.Model(geometry=geometry, materials=mats, settings=settings)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true",
                        help="Fast smoke run (fewer batches/particles).")
    args = parser.parse_args()

    repo_root = _HERE.parents[1]
    run_dir = repo_root / "sims" / "openmc" / "msre_v0"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(run_dir)

    print(f"[msre_v0] Building model (quick={args.quick}) ...")
    model = build_model(quick=args.quick)

    print(f"[msre_v0] Running OpenMC in {run_dir} ...")
    sp_path = model.run(output=True)

    with openmc.StatePoint(sp_path) as sp:
        keff = sp.keff
        k = keff.nominal_value
        sd = keff.std_dev

    lo, hi = 1.00, 1.15
    passed = lo <= k <= hi
    banner = "PASS" if passed else "REVIEW"

    print()
    print("=" * 64)
    print(f"  k-eff (combined) = {k:.5f} +/- {sd:.5f}")
    print(f"  Acceptance envelope (homogenized v0): {lo:.2f} <= k <= {hi:.2f}")
    print(f"  Result: {banner}")
    print("=" * 64)
    if not passed:
        print("  Note: out-of-envelope does not necessarily mean a bug.")
        print("        Inspect material build, S(a,b) treatment, and source.")
        sys.exit(2)


if __name__ == "__main__":
    main()
