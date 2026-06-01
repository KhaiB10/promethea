"""
benchmarks/msbr/geometry_lattice.py

Full-core hex lattice extension of the two-fluid MSBR unit cell.
Primary source: ORNL-4528 Fig 5.4 + Table 5.1, §5.1 reactor description.

Geometry:
  - 10 ft (304.8 cm) diameter active core, 13 ft 3 in (403.86 cm) high
  - 420 fuel cells + 252 blanket cells on a 5 3/8 in hex pitch
  - This prototype lattices the unit-cell universe across the hex grid,
    treats blanket cells as fertile-salt-filled hex prisms, and wraps
    the core in a graphite reflector (placeholder thickness).
  - Vessel and downcomer regions are deferred to the next prototype.

CSG choices:
  - True hex prism via openmc.model.HexagonalPrism (no equal-area
    cylinder approximation at the lattice level)
  - Fuel-cell universe = unit_cell module (concentric cylinders inside
    the hex)
  - Blanket-cell universe = single hex prism filled with blanket salt
  - Lattice is openmc.HexLattice in y-orientation (flat-top)
  - Outer boundary: vacuum on the radial reflector outer surface,
    reflective on axial caps (1D-equivalent axial leakage handled later)

This is a scaffold: k-eff will not match BR=1.06 until the fissile
loading, blanket-cell placement, and reflector dimensions are tuned to
ORNL Table 6.2 (0.802 graphite / 0.134 fuel salt / 0.064 blanket salt
core volume fractions, 1.26 kg fissile/MWe specific inventory).
"""
from __future__ import annotations

import openmc

from . import materials as mats
from .geometry_unit_cell import (
    EQUAL_AREA_R_CM,
    HEX_PITCH_CM,
    R_INNER_TUBE_ID_CM,
    R_INNER_TUBE_OD_CM,
    R_OUTER_BORE_CM,
)


# ---------------------------------------------------------------------------
# Core dimensions (cm) — ORNL-4528 Table 5.1
# ---------------------------------------------------------------------------

INCH_CM = 2.54
FT_CM = 30.48

CORE_DIAMETER_CM = 10.0 * FT_CM            # 304.8
CORE_HEIGHT_CM = (13.0 + 3.0 / 12.0) * FT_CM  # 13 ft 3 in = 403.86
CORE_RADIUS_CM = CORE_DIAMETER_CM / 2.0    # 152.4

# Reflector — ORNL §5.1 cites ~2 ft graphite reflector; we use a
# placeholder annulus until §5 components read confirms.
REFLECTOR_THICKNESS_CM = 2.0 * FT_CM       # 60.96
VESSEL_RADIUS_CM = CORE_RADIUS_CM + REFLECTOR_THICKNESS_CM

# Lattice geometry: hex rings to cover the core radius.
# For a flat-top hex lattice on across-flats pitch p, the maximum
# distance from center to a ring-n cell center is ~n * p. The number
# of rings needed is ceil(core_radius / pitch).
import math

N_RINGS = math.ceil(CORE_RADIUS_CM / HEX_PITCH_CM) + 1


def _build_fuel_cell_universe() -> openmc.Universe:
    """Concentric fuel/graphite unit cell inside an implicit hex outline.

    Note: cells use cylindrical surfaces only; the surrounding hex
    boundary comes from the lattice cell itself. The fill-outside
    region is set to graphite to occupy the hex corners.
    """
    fuel_salt = mats.build_fuel_salt()
    graphite = mats.build_graphite()

    s_inner_id = openmc.ZCylinder(r=R_INNER_TUBE_ID_CM)
    s_inner_od = openmc.ZCylinder(r=R_INNER_TUBE_OD_CM)
    s_outer_bore = openmc.ZCylinder(r=R_OUTER_BORE_CM)

    c_fuel_inner = openmc.Cell(name="fc_fuel_inner", fill=fuel_salt,
                               region=-s_inner_id)
    c_graphite_inner = openmc.Cell(name="fc_graphite_inner", fill=graphite,
                                   region=+s_inner_id & -s_inner_od)
    c_fuel_annulus = openmc.Cell(name="fc_fuel_annulus", fill=fuel_salt,
                                 region=+s_inner_od & -s_outer_bore)
    c_graphite_outer = openmc.Cell(name="fc_graphite_outer", fill=graphite,
                                   region=+s_outer_bore)

    return openmc.Universe(name="fuel_cell",
                           cells=[c_fuel_inner, c_graphite_inner,
                                  c_fuel_annulus, c_graphite_outer])


def _build_blanket_cell_universe() -> openmc.Universe:
    """Hex cell entirely filled with blanket salt (simplified)."""
    blanket = mats.build_blanket_salt()
    c = openmc.Cell(name="bc_blanket", fill=blanket)
    return openmc.Universe(name="blanket_cell", cells=[c])


def _build_outer_universe() -> openmc.Universe:
    """Universe for lattice positions outside the active core (reflector graphite)."""
    graphite = mats.build_graphite()
    c = openmc.Cell(name="outer_graphite", fill=graphite)
    return openmc.Universe(name="outer", cells=[c])


def _is_blanket_position(ring: int, idx: int, ring_size: int) -> bool:
    """Crude blanket-vs-fuel assignment until ORNL Fig 5.4 is digitized.

    ORNL-4528 specifies 420 fuel + 252 blanket cells (ratio 5:3). We
    approximate by tagging every third cell on each ring as blanket;
    the actual layout has blanket cells clustered radially. This is a
    placeholder for the v0.4.0 scaffold and will be replaced once
    Fig 5.4 coordinates are extracted.
    """
    if ring_size == 0:
        return False
    return (idx % 3) == 0 and ring > 0


def build_core_geometry() -> tuple[openmc.Geometry, openmc.Materials]:
    """Build a hex-lattice core + reflector + vacuum boundary.

    The output is a single-assembly approximation of the MSBR core:
    a hex lattice of fuel and blanket universes, centered at the
    origin, embedded in a cylindrical reflector annulus, with vacuum
    radial BC and reflective axial BCs.
    """
    fuel_u = _build_fuel_cell_universe()
    blanket_u = _build_blanket_cell_universe()
    outer_u = _build_outer_universe()

    # Build lattice rings: ring 0 is center (1 cell), ring k has 6*k cells.
    lattice_universes: list[list[openmc.Universe]] = []
    for ring in range(N_RINGS + 1):
        ring_size = 1 if ring == 0 else 6 * ring
        # Switch to outer reflector once we're past core radius
        ring_center_distance = ring * HEX_PITCH_CM
        if ring_center_distance > CORE_RADIUS_CM:
            row = [outer_u for _ in range(ring_size)]
        else:
            row = [
                blanket_u if _is_blanket_position(ring, i, ring_size) else fuel_u
                for i in range(ring_size)
            ]
        lattice_universes.append(row)
    # HexLattice expects rings ordered outer-first
    lattice_universes_outer_first = list(reversed(lattice_universes))

    lattice = openmc.HexLattice(name="msbr_core_lattice")
    lattice.center = (0.0, 0.0)
    lattice.pitch = (HEX_PITCH_CM,)
    lattice.orientation = "y"
    lattice.universes = lattice_universes_outer_first
    lattice.outer = outer_u

    # Bounding surfaces
    s_core_outer = openmc.ZCylinder(r=CORE_RADIUS_CM)
    s_vessel = openmc.ZCylinder(r=VESSEL_RADIUS_CM, boundary_type="vacuum")
    z_lo = openmc.ZPlane(z0=-CORE_HEIGHT_CM / 2.0, boundary_type="reflective")
    z_hi = openmc.ZPlane(z0=+CORE_HEIGHT_CM / 2.0, boundary_type="reflective")
    axial = +z_lo & -z_hi

    # Lattice fills entire axial slab; reflector is the radial annulus
    # outside the core radius but inside the vessel.
    c_lattice = openmc.Cell(name="core_lattice", fill=lattice,
                            region=axial & -s_core_outer)
    graphite = mats.build_graphite()
    c_reflector = openmc.Cell(name="radial_reflector", fill=graphite,
                              region=axial & +s_core_outer & -s_vessel)

    root = openmc.Universe(cells=[c_lattice, c_reflector])
    geometry = openmc.Geometry(root)

    fuel_salt = mats.build_fuel_salt()
    blanket_salt = mats.build_blanket_salt()
    materials = openmc.Materials([fuel_salt, blanket_salt, graphite])
    return geometry, materials


if __name__ == "__main__":
    geom, matls = build_core_geometry()
    print("Core diameter (cm):     ", CORE_DIAMETER_CM)
    print("Core height (cm):       ", CORE_HEIGHT_CM)
    print("Reflector thickness (cm):", REFLECTOR_THICKNESS_CM)
    print("Hex pitch (cm):         ", HEX_PITCH_CM)
    print("Lattice rings:          ", N_RINGS)
    total_cells = 1 + sum(6 * r for r in range(1, N_RINGS + 1))
    print("Approx lattice cells:   ", total_cells)
    print("Materials:", [m.name for m in matls])
