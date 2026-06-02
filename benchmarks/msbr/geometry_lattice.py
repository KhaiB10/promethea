"""
benchmarks/msbr/geometry_lattice.py

Full-core geometry for the two-fluid MSBR (1000 MWe reference).
Primary source: ORNL-4528 Fig 5.1 (vertical section), Fig 5.2
(horizontal section), §5.1 reactor description, Table 5.1 (20 kW/L
reference design column).

TOPOLOGY (corrected after Fig 5.1/5.2 re-read):

The MSBR is *not* a mixed fuel/blanket lattice. It is:

  - A fuel-cell core: 420 fuel cells on a 5 3/8 in triangular (hex)
    pitch, 10 ft 0 in diameter × 13 ft 3 in high
  - A blanket annulus: 252 blanket cells on a 5 11/16 in triangular
    pitch, in a ~1 ft thick annulus around the core (volume
    fractions 0.58 blanket salt / 0.42 graphite in that region)
  - A graphite reflector outside the blanket annulus
  - A modified Hastelloy N pressure vessel, 14 ft 0 in OD

Volume fractions inside the *core* region (Table 5.1, 20 kW/L):
  - 0.802 graphite, 0.134 fuel salt, 0.064 blanket salt

The 0.064 blanket-salt fraction inside the core comes from the
through-cell blanket flow that surrounds the inner fuel annulus
(see Fig 5.3 / geometry_unit_cell.py — the outer-bore region in the
unit cell is blanket salt, NOT fuel salt as drawn in the v0.4.0 alpha
unit cell). The unit cell will be corrected in a follow-up commit.

THIS SCAFFOLD ships the corrected topology — fuel hex lattice inside
core radius, blanket annulus, graphite reflector — with the unit cell
filled as fuel-only (still the alpha unit cell) for now. The next
prototype will fix the unit cell to embed blanket salt in the outer
bore so the core volume fractions hit Table 5.1.
"""
from __future__ import annotations

import math

import openmc

from . import materials as mats
from .geometry_unit_cell import (
    HEX_PITCH_CM,
    R_INNER_TUBE_ID_CM,
    R_INNER_TUBE_OD_CM,
    R_OUTER_BORE_CM,
)


# ---------------------------------------------------------------------------
# Core + blanket + vessel dimensions (cm) — ORNL-4528 Fig 5.1, Table 5.1
# ---------------------------------------------------------------------------

INCH_CM = 2.54
FT_CM = 30.48

# Core: 10 ft 0 in diam × 13 ft 3 in high
CORE_DIAMETER_CM = 10.0 * FT_CM            # 304.80
CORE_HEIGHT_CM = (13.0 + 3.0 / 12.0) * FT_CM  # 403.86
CORE_RADIUS_CM = CORE_DIAMETER_CM / 2.0    # 152.40

# Blanket annulus: ~1 ft thick (Table 5.1: "Blanket thickness, ft = 1.0"
# at the 20 kW/L design point — though the table label is partially
# scanned; figure 5.1 shows ~1 ft radial blanket)
BLANKET_THICKNESS_CM = 1.0 * FT_CM         # 30.48
BLANKET_OUTER_RADIUS_CM = CORE_RADIUS_CM + BLANKET_THICKNESS_CM  # 182.88

# Reflector: ORNL-4528 §5.1 references reflector graphite outside the
# blanket; Table 5.1 reports "Reflector thickness, ft = 0.5" at the
# 20 kW/L design column. Vessel OD is 14 ft 0 in = 426.72 cm, so vessel
# inner radius is taken as the blanket outer radius + reflector.
REFLECTOR_THICKNESS_CM = 0.5 * FT_CM       # 15.24
REFLECTOR_OUTER_RADIUS_CM = BLANKET_OUTER_RADIUS_CM + REFLECTOR_THICKNESS_CM  # 198.12

# Vessel: 14 ft 0 in OD (Fig 5.1, top label "14 ft 0 in DIAM" on
# pressure vessel). Wall thickness placeholder until §5 components
# read for primary number.
VESSEL_OD_CM = 14.0 * FT_CM                # 426.72
VESSEL_OUTER_RADIUS_CM = VESSEL_OD_CM / 2.0  # 213.36
VESSEL_WALL_CM = VESSEL_OUTER_RADIUS_CM - REFLECTOR_OUTER_RADIUS_CM  # ~15.24

# Hex-lattice ring count needed to fully cover the core radius
N_RINGS = math.ceil(CORE_RADIUS_CM / HEX_PITCH_CM) + 1


# ---------------------------------------------------------------------------
# Universe builders
# ---------------------------------------------------------------------------

def _build_fuel_cell_universe() -> openmc.Universe:
    """Concentric fuel/graphite unit cell (matches geometry_unit_cell)."""
    fuel_salt = mats.build_fuel_salt()
    graphite = mats.build_graphite()

    s_inner_id = openmc.ZCylinder(r=R_INNER_TUBE_ID_CM)
    s_inner_od = openmc.ZCylinder(r=R_INNER_TUBE_OD_CM)
    s_outer_bore = openmc.ZCylinder(r=R_OUTER_BORE_CM)

    c1 = openmc.Cell(name="fc_fuel_inner", fill=fuel_salt, region=-s_inner_id)
    c2 = openmc.Cell(name="fc_graphite_inner", fill=graphite,
                     region=+s_inner_id & -s_inner_od)
    c3 = openmc.Cell(name="fc_fuel_annulus", fill=fuel_salt,
                    region=+s_inner_od & -s_outer_bore)
    c4 = openmc.Cell(name="fc_graphite_outer", fill=graphite, region=+s_outer_bore)
    return openmc.Universe(name="fuel_cell", cells=[c1, c2, c3, c4])


def _build_outer_graphite_universe() -> openmc.Universe:
    graphite = mats.build_graphite()
    c = openmc.Cell(name="outer_graphite_fill", fill=graphite)
    return openmc.Universe(name="outer_graphite", cells=[c])


# ---------------------------------------------------------------------------
# Core geometry
# ---------------------------------------------------------------------------

def build_core_geometry() -> tuple[openmc.Geometry, openmc.Materials]:
    """Build full-core MSBR geometry: fuel lattice + blanket annulus
    + reflector + vessel + vacuum BC.

    Layout (radial, outward):
      r in [0, CORE_RADIUS]                : hex lattice of fuel cells
      r in [CORE_RADIUS, BLANKET_OUTER]    : blanket salt + graphite mix
                                              (homogenized at the 0.58/0.42
                                              volume fractions of Table 5.1)
      r in [BLANKET_OUTER, REFLECTOR_OUT]  : graphite reflector
      r in [REFLECTOR_OUT, VESSEL_OUT]     : Hastelloy N vessel wall

    Axial BCs: reflective top and bottom (1D-equivalent leakage handled
    in a later prototype with axial blanket and plenum regions).
    """
    fuel_u = _build_fuel_cell_universe()
    outer_graphite_u = _build_outer_graphite_universe()

    # Lattice (fills the entire bounding cylinder of the core; cells
    # outside the core circle will be cut off by the core surface).
    lattice_universes: list[list[openmc.Universe]] = []
    for ring in range(N_RINGS + 1):
        ring_size = 1 if ring == 0 else 6 * ring
        ring_center_distance = ring * HEX_PITCH_CM
        if ring_center_distance > CORE_RADIUS_CM:
            row = [outer_graphite_u for _ in range(ring_size)]
        else:
            row = [fuel_u for _ in range(ring_size)]
        lattice_universes.append(row)
    lattice_universes_outer_first = list(reversed(lattice_universes))

    lattice = openmc.HexLattice(name="msbr_fuel_lattice")
    lattice.center = (0.0, 0.0)
    lattice.pitch = (HEX_PITCH_CM,)
    lattice.orientation = "y"
    lattice.universes = lattice_universes_outer_first
    lattice.outer = outer_graphite_u

    # Homogenized blanket-annulus material (0.58 blanket salt / 0.42
    # graphite by volume, Table 5.1 blanket region values)
    blanket_homog = mats.build_blanket_region_homogenized()

    # Vessel material
    hastelloy = mats.build_hastelloy_n()
    graphite = mats.build_graphite()
    fuel_salt = mats.build_fuel_salt()

    # Radial surfaces
    s_core = openmc.ZCylinder(r=CORE_RADIUS_CM)
    s_blanket_out = openmc.ZCylinder(r=BLANKET_OUTER_RADIUS_CM)
    s_reflector_out = openmc.ZCylinder(r=REFLECTOR_OUTER_RADIUS_CM)
    s_vessel_out = openmc.ZCylinder(r=VESSEL_OUTER_RADIUS_CM,
                                    boundary_type="vacuum")

    # Axial surfaces (reflective placeholder — replace with axial blanket
    # + plenums in the next prototype)
    z_lo = openmc.ZPlane(z0=-CORE_HEIGHT_CM / 2.0, boundary_type="reflective")
    z_hi = openmc.ZPlane(z0=+CORE_HEIGHT_CM / 2.0, boundary_type="reflective")
    axial = +z_lo & -z_hi

    # Cells
    c_core = openmc.Cell(name="core_lattice", fill=lattice,
                         region=axial & -s_core)
    c_blanket = openmc.Cell(name="blanket_annulus", fill=blanket_homog,
                            region=axial & +s_core & -s_blanket_out)
    c_reflector = openmc.Cell(name="radial_reflector", fill=graphite,
                              region=axial & +s_blanket_out & -s_reflector_out)
    c_vessel = openmc.Cell(name="vessel_wall", fill=hastelloy,
                           region=axial & +s_reflector_out & -s_vessel_out)

    root = openmc.Universe(cells=[c_core, c_blanket, c_reflector, c_vessel])
    geometry = openmc.Geometry(root)

    materials = openmc.Materials([
        fuel_salt,
        mats.build_blanket_salt(),
        blanket_homog,
        graphite,
        hastelloy,
    ])
    return geometry, materials


if __name__ == "__main__":
    geom, matls = build_core_geometry()
    print("Core diameter (cm):          ", CORE_DIAMETER_CM)
    print("Core height (cm):            ", CORE_HEIGHT_CM)
    print("Blanket annulus thickness:    ", BLANKET_THICKNESS_CM)
    print("Reflector thickness:          ", REFLECTOR_THICKNESS_CM)
    print("Vessel OD (cm):               ", VESSEL_OD_CM)
    print("Hex pitch (cm):               ", HEX_PITCH_CM)
    print("Lattice rings:                ", N_RINGS)
    n_in_core = 1 + sum(6 * r for r in range(1, N_RINGS + 1)
                        if r * HEX_PITCH_CM <= CORE_RADIUS_CM)
    print("Approx in-core cells:         ", n_in_core, "(ORNL target: 420)")
    print("Materials:", [m.name for m in matls])
