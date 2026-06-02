"""
benchmarks/msbr/geometry_unit_cell_homog.py

Homogenized companion to geometry_unit_cell.py. Same outer envelope
(equal-area cylinder of the 5 3/8 in. hex pitch, axially periodic
1 cm slab, reflective BCs on all sides), but the three constituent
materials (fuel salt, graphite, blanket salt) are *volume-averaged*
into one mixture occupying the entire cell.

Purpose
-------

Quantify the heterogeneity penalty for the v0.4.0 MSBR fuel-cell
prototype. This is the canonical Monte Carlo experiment that asks:

    "How much reactivity does explicit fuel/graphite/blanket
     geometry buy you over a perfectly mixed cell with the
     SAME volume fractions?"

For thermal-spectrum graphite-moderated cells the answer is usually
positive and 1000+ pcm -- spatial self-shielding of 233U and the
ability of neutrons to thermalize in graphite before re-entering
the fuel both help k. The exact size for the MSBR cell at our
volume fractions is, to our knowledge, not published in any open
Monte Carlo benchmark.

Volume fractions used
---------------------

These match the *as-built* heterogeneous geometry, not ORNL Table 5.1.
The equal-area-cylinder approximation gives:

    fuel    : 0.1222
    graphite: 0.8138
    blanket : 0.0640

Using the as-built values (rather than ORNL's 0.134/0.802/0.064)
isolates the het/homog effect alone -- otherwise the comparison
also bakes in a renormalization of the fuel fraction.

Mixing rule
-----------

OpenMC supports density-weighted material mixing via
``openmc.Material.mix_materials`` with ``percent_type="vo"``. The
result is a single Material whose nuclide densities are the
volume-fraction-weighted sum of the inputs at their native
densities (Tables 3.1, 3.5 of ORNL-4528).
"""
from __future__ import annotations

import math

import openmc

from . import materials as mats
from .geometry_unit_cell import (
    EQUAL_AREA_R_CM,
    R_OUTER_BORE_CM,
    R_INNER_TUBE_ID_CM,
    R_INNER_TUBE_OD_CM,
    R_GRAPHITE_OD_CM,
)


# Computed once, matches the heterogeneous build exactly.
def _volume_fractions() -> dict[str, float]:
    A_tot = math.pi * EQUAL_AREA_R_CM ** 2
    A_fuel = math.pi * (
        R_INNER_TUBE_ID_CM ** 2
        + (R_OUTER_BORE_CM ** 2 - R_INNER_TUBE_OD_CM ** 2)
    )
    A_graphite = math.pi * (
        (R_INNER_TUBE_OD_CM ** 2 - R_INNER_TUBE_ID_CM ** 2)
        + (R_GRAPHITE_OD_CM ** 2 - R_OUTER_BORE_CM ** 2)
    )
    A_blanket = math.pi * (EQUAL_AREA_R_CM ** 2 - R_GRAPHITE_OD_CM ** 2)
    return {
        "fuel": A_fuel / A_tot,
        "graphite": A_graphite / A_tot,
        "blanket": A_blanket / A_tot,
    }


VF = _volume_fractions()


def build_homogenized_material() -> openmc.Material:
    """Volume-mix fuel salt + graphite + blanket salt into one Material.

    Uses OpenMC's built-in volume-percent mix. The result is named
    ``MSBR_homogenized`` for tally bookkeeping symmetry with the
    heterogeneous build.
    """
    fuel = mats.build_fuel_salt()
    graphite = mats.build_graphite()
    blanket = mats.build_blanket_salt()

    mixed = openmc.Material.mix_materials(
        [fuel, graphite, blanket],
        [VF["fuel"], VF["graphite"], VF["blanket"]],
        percent_type="vo",
        name="MSBR_homogenized",
    )
    return mixed


def build_unit_cell_geometry() -> tuple[openmc.Geometry, openmc.Materials]:
    """Single-region cell with the homogenized mixture filling everything.

    Returns the OpenMC geometry and materials collection.
    """
    mixed = build_homogenized_material()

    s_outer = openmc.ZCylinder(r=EQUAL_AREA_R_CM, boundary_type="reflective")
    z_lo = openmc.ZPlane(z0=-0.5, boundary_type="reflective")
    z_hi = openmc.ZPlane(z0=+0.5, boundary_type="reflective")

    cell = openmc.Cell(
        name="homogenized_cell",
        fill=mixed,
        region=-s_outer & +z_lo & -z_hi,
    )
    universe = openmc.Universe(cells=[cell])
    geometry = openmc.Geometry(universe)
    materials = openmc.Materials([mixed])
    return geometry, materials


if __name__ == "__main__":
    print("Homogenized MSBR unit cell")
    print("-" * 40)
    print(f"  fuel    vf = {VF['fuel']:.6f}")
    print(f"  graph   vf = {VF['graphite']:.6f}")
    print(f"  blanket vf = {VF['blanket']:.6f}")
    print(f"  sum        = {sum(VF.values()):.6f}")
    geom, matls = build_unit_cell_geometry()
    print()
    print("Materials:", [m.name for m in matls])
    print("Cells:", [c.name for c in geom.root_universe.cells.values()])
