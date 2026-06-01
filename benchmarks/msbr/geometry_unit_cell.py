"""
benchmarks/msbr/geometry_unit_cell.py

Single-cell prototype geometry for the two-fluid MSBR fuel element.
Primary source: ORNL-4528 Fig 6.7 + Table 5.1 fuel-cell dimensions.

This is a deliberately simplified CSG representation:

  Cylindrical concentric layers (approximating the hex prism with an
  equal-area cylinder), reflective boundary conditions on all sides.
  Computes k-infinity of a unit cell — NOT a reactor calculation.

Purpose: sanity-check that
  - the material recipes give plausible neutronics
  - the OpenMC nuclide library has 233U + 232Th + 7Li at the chosen
    temperature
  - the cell-level reactivity is in the expected ballpark
    (ORNL-4528 §6.4 reference cell with 0.2 mol% 233U, 27 mol% ThF4
    in fertile, 0.1648 fuel vol frac, 0.0585 fertile vol frac
    should be slightly subcritical at infinite-lattice; the *reactor*
    achieves k=1 via blanket, reflector, and fissile loading).

Subsequent prototypes will:
  - Use true hex prism via openmc.model.HexagonalPrism
  - Add the inner concentric fuel-flow tube (Fig 5.4 details)
  - Lattice into the full 420-cell core
  - Add blanket regions, reflector, vessel
  - Add reaction-rate tallies for BR validation

Cell geometry derived from ORNL-4528 Fig 6.7 + Table 5.1:
  - Outer hex pitch: 5 3/8 in across flats = 13.6525 cm
    (equal-area circle radius = pitch / sqrt(pi/(2*sqrt(3))) ≈ 7.165 cm)
  - Outer bore: 2 23/32 in = 6.9056 cm diam → r_outer_bore = 3.4528 cm
  - Concentric inner tube: 2 1/4 in OD = 5.715 cm → r_inner_OD = 2.8575 cm
                           1 1/4 in ID = 3.175 cm → r_inner_ID = 1.5875 cm
  - Cell height (axial slice): 1 cm (arbitrary slice; k_inf is intensive)

Layer ordering from center outward (Fig 6.7 with concentric inner tube):
  r < 1.5875       : fuel salt (inner bore, downflow)
  1.5875 - 2.8575  : graphite (inner tube wall, simplification)
  2.8575 - 3.4528  : fuel salt (annulus, upflow)
  3.4528 - 7.165   : graphite (main moderator block)
  Note: blanket salt in the actual design occupies separate cells
  (252 blanket cells alongside 420 fuel cells), not concentric here.
  In the §6.4 cell calculation, blanket appears as a fertile region
  around the unit. For the v0.4.0 scaffold, we use the simpler
  concentric pattern and add explicit blanket cells later.
"""
from __future__ import annotations

import openmc

from . import materials as mats


# ---------------------------------------------------------------------------
# Dimensions (cm), all derived from ORNL-4528 Fig 6.7 + Table 5.1
# ---------------------------------------------------------------------------

INCH_CM = 2.54

# Hex pitch across flats
HEX_PITCH_CM = 5.375 * INCH_CM             # 13.6525

# Equal-area circle radius for a hex prism (across-flats pitch p):
#   A_hex = (sqrt(3)/2) p^2 = pi r^2  ->  r = p * sqrt(sqrt(3) / (2 pi))
EQUAL_AREA_R_CM = HEX_PITCH_CM * (3 ** 0.25) / (2 * 3.141592653589793) ** 0.5
# Numerically: 7.165 cm

# Outer bore radius (fuel annulus outer boundary)
R_OUTER_BORE_CM = (2 + 23/32) * INCH_CM / 2.0      # 3.4528

# Concentric inner tube
R_INNER_TUBE_OD_CM = 2.25 * INCH_CM / 2.0          # 2.8575
R_INNER_TUBE_ID_CM = 1.25 * INCH_CM / 2.0          # 1.5875


def build_unit_cell_geometry() -> tuple[openmc.Geometry, openmc.Materials]:
    """Concentric cylindrical unit cell with reflective BCs.

    Returns the OpenMC geometry and the materials collection for the
    cell. Volume fractions are intentionally NOT tuned to match
    Table 6.2 (0.802/0.134/0.064) — this prototype tests the material
    library and tally pipeline, not the reactor configuration.
    """
    fuel_salt = mats.build_fuel_salt()
    graphite = mats.build_graphite()

    # Cylindrical surfaces
    s_inner_id = openmc.ZCylinder(r=R_INNER_TUBE_ID_CM)
    s_inner_od = openmc.ZCylinder(r=R_INNER_TUBE_OD_CM)
    s_outer_bore = openmc.ZCylinder(r=R_OUTER_BORE_CM)
    s_outer_pitch = openmc.ZCylinder(r=EQUAL_AREA_R_CM, boundary_type="reflective")

    # Axial cap surfaces (1 cm slab with reflective top/bottom)
    z_lo = openmc.ZPlane(z0=-0.5, boundary_type="reflective")
    z_hi = openmc.ZPlane(z0=+0.5, boundary_type="reflective")

    # Region template applied to every region
    axial = +z_lo & -z_hi

    c_fuel_inner = openmc.Cell(name="fuel_inner_bore", fill=fuel_salt,
                               region=axial & -s_inner_id)
    c_graphite_inner = openmc.Cell(name="graphite_inner_tube", fill=graphite,
                                   region=axial & +s_inner_id & -s_inner_od)
    c_fuel_annulus = openmc.Cell(name="fuel_annulus", fill=fuel_salt,
                                 region=axial & +s_inner_od & -s_outer_bore)
    c_graphite_outer = openmc.Cell(name="graphite_outer", fill=graphite,
                                   region=axial & +s_outer_bore & -s_outer_pitch)

    universe = openmc.Universe(cells=[
        c_fuel_inner, c_graphite_inner, c_fuel_annulus, c_graphite_outer,
    ])

    geometry = openmc.Geometry(universe)
    materials = openmc.Materials([fuel_salt, graphite])
    return geometry, materials


if __name__ == "__main__":
    geom, matls = build_unit_cell_geometry()
    print("Equal-area outer radius (cm):", EQUAL_AREA_R_CM)
    print("Outer bore radius (cm):     ", R_OUTER_BORE_CM)
    print("Inner tube OD (cm):         ", R_INNER_TUBE_OD_CM)
    print("Inner tube ID (cm):         ", R_INNER_TUBE_ID_CM)
    print("Materials:", [m.name for m in matls])
    print("Cells:", [c.name for c in geom.root_universe.cells.values()])
