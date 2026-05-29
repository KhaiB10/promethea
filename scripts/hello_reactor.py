"""
hello_reactor.py — the Promethea toolchain smoke test.

Runs a classic PWR fuel pin-cell criticality calculation in OpenMC.
Geometry, materials, and expected k-inf are taken from the
OpenMC documentation's canonical "first model" example, which is itself
representative of a Westinghouse 17x17 PWR assembly pin cell:

    UO2 fuel pellet (3.0% U-235 enriched), Zircaloy clad, light water moderator.
    Expected k-inf ~ 1.18 (cold, clean, no boron).

Purpose: prove that OpenMC, the cross-section library, and the Python
bindings are all wired up correctly. This is NOT a Promethea design
simulation — it is a "does the toolchain run" check.

Run:
    python scripts/hello_reactor.py

Outputs:
    sims/openmc/hello_reactor/  (geometry, materials, settings, tallies)
    statepoint.<N>.h5           (results)
    A line on stdout with k-eff and uncertainty.
"""

from __future__ import annotations
import os
import shutil
import sys
from pathlib import Path

try:
    import openmc
except ImportError:
    print("ERROR: OpenMC is not installed in this environment.", file=sys.stderr)
    print("       Use the Docker image (see Dockerfile) or install via conda-forge:", file=sys.stderr)
    print("           micromamba install -c conda-forge openmc", file=sys.stderr)
    sys.exit(1)


def build_materials() -> openmc.Materials:
    """PWR pin-cell materials: 3.0 wt% enriched UO2, Zr clad, water moderator."""
    uo2 = openmc.Material(name="UO2 fuel, 3.0 w/o U-235")
    uo2.set_density("g/cm3", 10.29769)
    uo2.add_element("U", 1.0, enrichment=3.0)
    uo2.add_element("O", 2.0)

    zirc = openmc.Material(name="Zircaloy-4 clad")
    zirc.set_density("g/cm3", 6.55)
    zirc.add_element("Zr", 0.9823, "wo")
    zirc.add_element("Sn", 0.0145, "wo")
    zirc.add_element("Fe", 0.0021, "wo")
    zirc.add_element("Cr", 0.0010, "wo")

    water = openmc.Material(name="Light water moderator")
    water.set_density("g/cm3", 0.740582)
    water.add_element("H", 2.0)
    water.add_element("O", 1.0)
    water.add_s_alpha_beta("c_H_in_H2O")  # thermal scattering treatment

    return openmc.Materials([uo2, zirc, water])


def build_geometry(materials: openmc.Materials) -> openmc.Geometry:
    """Single PWR pin cell, reflective boundaries (infinite lattice)."""
    uo2, zirc, water = materials

    # Pin dimensions (cm) — typical 17x17 PWR
    r_fuel = 0.39218
    r_clad_inner = 0.40005
    r_clad_outer = 0.45720
    pitch = 1.25984  # square lattice

    fuel_or = openmc.ZCylinder(r=r_fuel)
    clad_ir = openmc.ZCylinder(r=r_clad_inner)
    clad_or = openmc.ZCylinder(r=r_clad_outer)

    half = pitch / 2.0
    left = openmc.XPlane(x0=-half, boundary_type="reflective")
    right = openmc.XPlane(x0=+half, boundary_type="reflective")
    bottom = openmc.YPlane(y0=-half, boundary_type="reflective")
    top = openmc.YPlane(y0=+half, boundary_type="reflective")

    fuel_region = -fuel_or
    gap_region = +fuel_or & -clad_ir
    clad_region = +clad_ir & -clad_or
    mod_region = +clad_or & +left & -right & +bottom & -top

    fuel_cell = openmc.Cell(name="fuel", fill=uo2, region=fuel_region)
    gap_cell = openmc.Cell(name="gap", region=gap_region)  # void
    clad_cell = openmc.Cell(name="clad", fill=zirc, region=clad_region)
    mod_cell = openmc.Cell(name="moderator", fill=water, region=mod_region)

    return openmc.Geometry([fuel_cell, gap_cell, clad_cell, mod_cell])


def build_settings() -> openmc.Settings:
    s = openmc.Settings()
    s.batches = 100
    s.inactive = 20
    s.particles = 5_000
    # Initial source: uniform over the fuel region
    bounds = [-0.39218, -0.39218, -1.0, 0.39218, 0.39218, 1.0]
    s.source = openmc.IndependentSource(
        space=openmc.stats.Box(bounds[:3], bounds[3:], only_fissionable=True)
    )
    s.output = {"summary": False}
    return s


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    run_dir = repo_root / "sims" / "openmc" / "hello_reactor"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(run_dir)

    materials = build_materials()
    geometry = build_geometry(materials)
    settings = build_settings()

    model = openmc.Model(geometry=geometry, materials=materials, settings=settings)
    print(f"[hello_reactor] Running OpenMC in {run_dir} ...")
    sp_path = model.run(output=True)

    with openmc.StatePoint(sp_path) as sp:
        keff = sp.keff
        print()
        print("=" * 60)
        print(f"  k-eff (combined estimator) = {keff.nominal_value:.5f} "
              f"+/- {keff.std_dev:.5f}")
        print(f"  Expected (cold, clean PWR pin cell): k-inf ~ 1.18")
        print("=" * 60)

    print("\n[hello_reactor] Toolchain check PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
