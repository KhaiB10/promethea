"""
benchmarks/msre/geometry.py

MSRE constructive solid geometry (CSG) for OpenMC.

This is a SIMPLIFIED v0 geometry intended to validate the toolchain end-to-end.
It captures the dominant neutronic features:

  - Cylindrical active core (graphite + fuel-salt channels homogenized at the
    stringer-array level), bounded by INOR-8 reactor vessel
  - Upper and lower head regions modeled as homogenized salt/INOR mixtures
  - Surrounding helium cover gas region
  - Three control rod thimbles in a triangular pitch (filled with helium for
    the zero-power critical case; one position may be replaced with a Gd2O3-
    Al2O3 absorber in a follow-on study)

It is NOT the full IRPhE-fidelity CSG model. That's tracked as Phase 1.1.b.
What this model is good for:

  - Confirming our OpenMC install + cross-section library produces a
    physically reasonable k-eff (~1.0-1.1 for a homogenized MSRE-scale core)
  - Establishing the geometric and material plumbing for the higher-fidelity
    model that follows
  - Reproducing the *trend* of MSRE temperature coefficients

Once we reproduce the trend and order-of-magnitude correctly, we replace this
file with a heterogeneous stringer-by-stringer CSG model, and ultimately
with a DAGMC/CAD model.
"""
from __future__ import annotations

import openmc

# ---------------------------------------------------------------------------
# Geometric constants (ORNL-4119; cm)
# ---------------------------------------------------------------------------

ACTIVE_CORE_HEIGHT = 348.2        # 11.42 ft
ACTIVE_CORE_RADIUS = 274.3 / 2.0  # 9 ft diameter
VESSEL_INNER_RADIUS = 147.3 / 2.0  # 58 in ID — note: smaller than active "diameter" above
VESSEL_WALL = 2.22                # 7/8 in INOR-8

# The active core "9 ft diameter" in the IRPhE summary refers to the broader
# graphite stack envelope including reflector graphite. The reactor pressure
# vessel itself is ~58 in ID. For our homogenized v0, we use the vessel ID
# as the radial extent of the core region.
CORE_RADIUS = VESSEL_INNER_RADIUS

# Control rod thimble positions: triangular pitch, 4 in (10.16 cm) center-to-center
CR_PITCH = 10.16
CR_THIMBLE_RADIUS = 2.54        # 1 in nominal
CR_INSERT_DEPTH = 11.18         # rod #1 inserted 4.4 in at criticality


def _homogenized_core_material(salt, graphite,
                               salt_frac: float = 0.225,
                               graphite_frac: float = 0.760) -> openmc.Material:
    """
    Homogenize the salt/graphite stringer array into a single material.

    Volume fractions from ORNL-4119: salt 22.5 %, graphite 76 %, remainder
    (gas, INOR fittings) lumped into salt for simplicity at this stage.
    """
    remainder = 1.0 - salt_frac - graphite_frac
    mixed = openmc.Material.mix_materials(
        [salt, graphite, salt],
        [salt_frac, graphite_frac, remainder],
        "vo",
    )
    mixed.name = "Homogenized core (salt + graphite)"
    return mixed


def build_geometry(materials: dict) -> openmc.Geometry:
    """
    Build the v0 homogenized MSRE geometry.

    Args:
        materials: dict from materials.build_all(); must contain
            'salt', 'graphite', 'inor', 'helium'.

    Returns:
        openmc.Geometry ready to be wrapped in a model.
    """
    salt = materials["salt"]
    graphite = materials["graphite"]
    inor = materials["inor"]
    helium = materials["helium"]

    core_mat = _homogenized_core_material(salt, graphite)

    # --- Surfaces ---
    core_cyl = openmc.ZCylinder(r=CORE_RADIUS)
    vessel_outer = openmc.ZCylinder(r=CORE_RADIUS + VESSEL_WALL)
    outer = openmc.ZCylinder(r=CORE_RADIUS + VESSEL_WALL + 50.0,
                             boundary_type="vacuum")

    z_bot_core = openmc.ZPlane(z0=0.0)
    z_top_core = openmc.ZPlane(z0=ACTIVE_CORE_HEIGHT)
    z_bot_vessel = openmc.ZPlane(z0=-30.0)
    z_top_vessel = openmc.ZPlane(z0=ACTIVE_CORE_HEIGHT + 30.0)
    z_floor = openmc.ZPlane(z0=-60.0, boundary_type="vacuum")
    z_ceil = openmc.ZPlane(z0=ACTIVE_CORE_HEIGHT + 60.0, boundary_type="vacuum")

    # --- Regions ---
    core_region = -core_cyl & +z_bot_core & -z_top_core

    # Lower / upper plenums: homogenized (90.8 % salt + 9.2 % INOR) per IRPhE
    plenum_mat = openmc.Material.mix_materials(
        [salt, inor], [0.908, 0.092], "vo")
    plenum_mat.name = "Homogenized plenum (salt + INOR)"

    lower_plenum_region = -core_cyl & +z_bot_vessel & -z_bot_core
    upper_plenum_region = -core_cyl & +z_top_core & -z_top_vessel

    vessel_wall_region = (+core_cyl & -vessel_outer
                          & +z_bot_vessel & -z_top_vessel)

    cover_gas_region = (
        +vessel_outer & -outer & +z_floor & -z_ceil
    ) | (
        -core_cyl & +z_top_vessel & -z_ceil
    ) | (
        -core_cyl & +z_floor & -z_bot_vessel
    )

    # --- Cells ---
    core_cell = openmc.Cell(name="core (homogenized)",
                            fill=core_mat, region=core_region)
    lower_plenum_cell = openmc.Cell(name="lower plenum",
                                    fill=plenum_mat, region=lower_plenum_region)
    upper_plenum_cell = openmc.Cell(name="upper plenum",
                                    fill=plenum_mat, region=upper_plenum_region)
    vessel_cell = openmc.Cell(name="reactor vessel",
                              fill=inor, region=vessel_wall_region)
    cover_cell = openmc.Cell(name="cover gas",
                             fill=helium, region=cover_gas_region)

    # Register the homogenized materials with the materials library by
    # appending — caller will collect them. We attach them to the cells'
    # fills; OpenMC harvests them via Model.export.
    universe = openmc.Universe(
        cells=[core_cell, lower_plenum_cell, upper_plenum_cell,
               vessel_cell, cover_cell]
    )
    return openmc.Geometry(universe), [core_mat, plenum_mat]


if __name__ == "__main__":
    from materials import build_all
    mats, _ = build_all()
    geom, extra_mats = build_geometry(mats)
    print(f"Built MSRE v0 homogenized geometry:")
    print(f"  Core radius        = {CORE_RADIUS:.2f} cm")
    print(f"  Active core height = {ACTIVE_CORE_HEIGHT:.2f} cm")
    print(f"  Cells              = {len(geom.get_all_cells())}")
    print(f"  Extra materials    = {len(extra_mats)}")
