"""
benchmarks/msbr/geometry_vf_sweep.py

Volume-fraction-parameterized heterogeneous unit cell.

This is the same fuel-cell topology as ``geometry_unit_cell.py``
(concentric: fuel-bore / inner-graphite-tube / fuel-annulus /
outer-graphite-block / interstitial-blanket, reflective BCs, equal-area
cylinder approximation of the hex prism), but the **radii are solved
from target volume fractions** so we can sweep the geometry without
hand-tuning ORNL-4528 dimensions.

The point of this module is to ask: did ORNL's 1971 choice of volume
fractions (0.802 graphite / 0.134 fuel / 0.064 blanket — Table 5.1)
maximize the heterogeneity Δk advantage, or is there a better
configuration that v0.4.0's machinery can find?

Parameterization
----------------

Three free parameters with one constraint (they sum to 1):

    f_fuel + f_graphite + f_blanket = 1

We expose ``f_fuel`` and ``f_blanket`` as the independent variables;
``f_graphite = 1 - f_fuel - f_blanket`` follows.

Inside the *fuel* fraction we keep the topological feature that makes
this an MSBR cell (not an LWR pin): the fuel salt is split across
two radii — an inner downflow bore and an outer upflow annulus,
separated by a thin graphite inner tube. We fix the inner-bore /
annulus split at the original ORNL ratio:

    A_inner_bore / A_total_fuel = R_INNER_TUBE_ID^2
                                  / (R_INNER_TUBE_ID^2 + R_OUTER_BORE^2 - R_INNER_TUBE_OD^2)
                                ≈ 0.4015   (from the ORNL dimensions)

and the graphite inner-tube thickness is preserved as a fixed fraction
of total graphite:

    A_inner_graphite_tube / A_total_graphite ≈ 0.1350   (from ORNL)

These two ratios are baked in as constants below; the user only sweeps
the three macroscopic volume fractions.

Geometry build order
--------------------

Given (f_fuel, f_blanket), with f_graphite = 1 − f_fuel − f_blanket:

  1. R_pitch is fixed to the same equal-area-cylinder radius as the
     ORNL-4528 baseline (~7.165 cm).
  2. Solve A_total = π R_pitch^2.
  3. A_blanket = f_blanket * A_total
     → R_graphite_OD = sqrt(R_pitch^2 - A_blanket/π)
  4. A_fuel  = f_fuel  * A_total
  5. A_graphite = f_graphite * A_total
  6. Apportion:
       A_inner_bore   = R_INNER_BORE_RATIO * A_fuel
       A_fuel_annulus = (1 - R_INNER_BORE_RATIO) * A_fuel
       A_inner_tube_graphite = R_INNER_TUBE_RATIO * A_graphite
       A_outer_block_graphite = (1 - R_INNER_TUBE_RATIO) * A_graphite
  7. Convert areas back to radii using:
       R_inner_id = sqrt(A_inner_bore / π)
       R_inner_od = sqrt((A_inner_bore + A_inner_tube_graphite) / π)
       R_outer_bore = sqrt((A_inner_bore + A_inner_tube_graphite + A_fuel_annulus) / π)

R_graphite_OD must satisfy R_outer_bore < R_graphite_OD < R_pitch by
construction. We validate and raise on inconsistent inputs.
"""
from __future__ import annotations

import math

import openmc

from . import materials as mats
from .geometry_unit_cell import (
    EQUAL_AREA_R_CM,
    R_INNER_TUBE_ID_CM,
    R_INNER_TUBE_OD_CM,
    R_OUTER_BORE_CM,
    R_GRAPHITE_OD_CM,
)


# Fixed topological ratios inherited from ORNL-4528 Fig 6.7 / Table 5.1
_A_total = math.pi * EQUAL_AREA_R_CM ** 2
_A_inner_bore = math.pi * R_INNER_TUBE_ID_CM ** 2
_A_inner_tube = math.pi * (R_INNER_TUBE_OD_CM ** 2 - R_INNER_TUBE_ID_CM ** 2)
_A_fuel_annulus = math.pi * (R_OUTER_BORE_CM ** 2 - R_INNER_TUBE_OD_CM ** 2)
_A_graphite_outer = math.pi * (R_GRAPHITE_OD_CM ** 2 - R_OUTER_BORE_CM ** 2)
_A_total_fuel = _A_inner_bore + _A_fuel_annulus
_A_total_graphite = _A_inner_tube + _A_graphite_outer

#: Fraction of total fuel area that sits in the inner downflow bore.
R_INNER_BORE_RATIO: float = _A_inner_bore / _A_total_fuel  # ~0.241

#: Fraction of total graphite area that sits in the inner tube wall
#: (the rest is the outer hex moderator block).
R_INNER_TUBE_RATIO: float = _A_inner_tube / _A_total_graphite  # ~0.014

# ORNL baseline reference for documentation / comparison
ORNL_VF = {
    "fuel": _A_total_fuel / _A_total,
    "graphite": _A_total_graphite / _A_total,
    "blanket": (_A_total - _A_total_fuel - _A_total_graphite) / _A_total,
}


def vf_from_geometry() -> dict:
    """Return the baseline (ORNL) volume fractions in the same dict
    schema as ``build_vf_geometry`` accepts."""
    return dict(ORNL_VF)


def build_vf_geometry(
    f_fuel: float,
    f_blanket: float,
    *,
    temp_K: float | None = None,
) -> tuple[openmc.Geometry, openmc.Materials, dict]:
    """Build the heterogeneous unit cell with target volume fractions.

    Parameters
    ----------
    f_fuel:
        Target fuel-salt volume fraction (0 < f_fuel < 1).
    f_blanket:
        Target blanket-salt volume fraction (0 < f_blanket < 1).
    temp_K:
        Material temperature (K). Defaults to the package MSBR
        reference temperature.

    Returns
    -------
    (geometry, materials, info)
        ``info`` is a dict with the achieved volume fractions and
        radii, for logging and result-file metadata.

    Raises
    ------
    ValueError
        If the requested fractions are infeasible (would produce a
        non-monotonic radius sequence) or out of bounds.
    """
    if not (0.0 < f_fuel < 1.0):
        raise ValueError(f"f_fuel out of range: {f_fuel}")
    if not (0.0 < f_blanket < 1.0):
        raise ValueError(f"f_blanket out of range: {f_blanket}")
    f_graphite = 1.0 - f_fuel - f_blanket
    if f_graphite <= 0.0:
        raise ValueError(
            f"f_graphite would be {f_graphite}; (f_fuel + f_blanket) "
            "must be < 1."
        )
    if f_graphite < 0.50:
        raise ValueError(
            f"f_graphite={f_graphite:.4f} below 0.50 floor — this is "
            "not a thermal-spectrum graphite-moderated MSBR anymore."
        )

    if temp_K is None:
        temp_K = mats.MSBR_TEMP_K

    R_pitch = EQUAL_AREA_R_CM
    A_total = math.pi * R_pitch * R_pitch

    A_fuel = f_fuel * A_total
    A_graphite = f_graphite * A_total
    A_blanket = f_blanket * A_total

    A_inner_bore = R_INNER_BORE_RATIO * A_fuel
    A_fuel_annulus = A_fuel - A_inner_bore
    A_inner_tube_graphite = R_INNER_TUBE_RATIO * A_graphite
    A_outer_block_graphite = A_graphite - A_inner_tube_graphite

    # Cumulative areas → radii
    A_cum_inner_id = A_inner_bore
    A_cum_inner_od = A_cum_inner_id + A_inner_tube_graphite
    A_cum_outer_bore = A_cum_inner_od + A_fuel_annulus
    A_cum_graphite_od = A_cum_outer_bore + A_outer_block_graphite

    R_inner_id = math.sqrt(A_cum_inner_id / math.pi)
    R_inner_od = math.sqrt(A_cum_inner_od / math.pi)
    R_outer_bore = math.sqrt(A_cum_outer_bore / math.pi)
    R_graphite_od = math.sqrt(A_cum_graphite_od / math.pi)

    # Sanity checks: monotonic increasing radii
    radii = [R_inner_id, R_inner_od, R_outer_bore, R_graphite_od, R_pitch]
    for i in range(len(radii) - 1):
        if not (radii[i] < radii[i + 1]):
            raise ValueError(
                f"Non-monotonic radii at index {i}: {radii} — infeasible "
                f"(f_fuel={f_fuel}, f_blanket={f_blanket})."
            )

    # Materials
    fuel_salt = mats.build_fuel_salt(temp_K=temp_K)
    graphite = mats.build_graphite(temp_K=temp_K)
    blanket_salt = mats.build_blanket_salt(temp_K=temp_K)

    # Surfaces
    s_inner_id = openmc.ZCylinder(r=R_inner_id)
    s_inner_od = openmc.ZCylinder(r=R_inner_od)
    s_outer_bore = openmc.ZCylinder(r=R_outer_bore)
    s_graphite_od = openmc.ZCylinder(r=R_graphite_od)
    s_outer_pitch = openmc.ZCylinder(r=R_pitch, boundary_type="reflective")

    z_lo = openmc.ZPlane(z0=-0.5, boundary_type="reflective")
    z_hi = openmc.ZPlane(z0=+0.5, boundary_type="reflective")
    axial = +z_lo & -z_hi

    c_fuel_inner = openmc.Cell(
        name="fuel_inner_bore",
        fill=fuel_salt,
        region=axial & -s_inner_id,
    )
    c_graphite_inner = openmc.Cell(
        name="graphite_inner_tube",
        fill=graphite,
        region=axial & +s_inner_id & -s_inner_od,
    )
    c_fuel_annulus = openmc.Cell(
        name="fuel_annulus",
        fill=fuel_salt,
        region=axial & +s_inner_od & -s_outer_bore,
    )
    c_graphite_outer = openmc.Cell(
        name="graphite_outer",
        fill=graphite,
        region=axial & +s_outer_bore & -s_graphite_od,
    )
    c_blanket = openmc.Cell(
        name="blanket_interstitial",
        fill=blanket_salt,
        region=axial & +s_graphite_od & -s_outer_pitch,
    )

    universe = openmc.Universe(cells=[
        c_fuel_inner, c_graphite_inner, c_fuel_annulus,
        c_graphite_outer, c_blanket,
    ])
    geometry = openmc.Geometry(universe)
    materials = openmc.Materials([fuel_salt, graphite, blanket_salt])

    info = {
        "f_fuel": f_fuel,
        "f_graphite": f_graphite,
        "f_blanket": f_blanket,
        "temp_K": temp_K,
        "R_inner_id_cm": R_inner_id,
        "R_inner_od_cm": R_inner_od,
        "R_outer_bore_cm": R_outer_bore,
        "R_graphite_od_cm": R_graphite_od,
        "R_pitch_cm": R_pitch,
        "achieved_f_fuel": (A_cum_inner_id + A_fuel_annulus) / A_total,
        "achieved_f_graphite":
            (A_inner_tube_graphite + A_outer_block_graphite) / A_total,
        "achieved_f_blanket": (A_total - A_cum_graphite_od) / A_total,
    }
    return geometry, materials, info


def build_vf_geometry_homog(
    f_fuel: float,
    f_blanket: float,
    *,
    temp_K: float | None = None,
) -> tuple[openmc.Geometry, openmc.Materials, dict]:
    """Build the homogenized counterpart of ``build_vf_geometry``.

    Volume-mixes the same materials at the same fractions into a
    single-region cell with reflective BCs. Used to compute the
    heterogeneity Δk at each grid point.
    """
    if temp_K is None:
        temp_K = mats.MSBR_TEMP_K

    f_graphite = 1.0 - f_fuel - f_blanket

    # Use the same S(α,β) workaround as geometry_unit_cell_homog: build
    # graphite *without* the c_Graphite thermal-scatter table for the
    # volume mix step (OpenMC.mix_materials rejects materials carrying
    # an S(α,β) table), then re-attach c_Graphite to the resulting
    # homogenized material so carbon nuclides still see the law.
    from .geometry_unit_cell_homog import _build_graphite_bare

    fuel_salt = mats.build_fuel_salt(temp_K=temp_K)
    graphite_bare = _build_graphite_bare(temp_K=temp_K)
    blanket_salt = mats.build_blanket_salt(temp_K=temp_K)

    homog = openmc.Material.mix_materials(
        [fuel_salt, graphite_bare, blanket_salt],
        [f_fuel, f_graphite, f_blanket],
        percent_type="vo",
        name=f"MSBR_homog_f{f_fuel:.3f}_b{f_blanket:.3f}",
    )
    homog.add_s_alpha_beta("c_Graphite")

    R_pitch = EQUAL_AREA_R_CM
    s_outer = openmc.ZCylinder(r=R_pitch, boundary_type="reflective")
    z_lo = openmc.ZPlane(z0=-0.5, boundary_type="reflective")
    z_hi = openmc.ZPlane(z0=+0.5, boundary_type="reflective")

    cell = openmc.Cell(
        name="msbr_homog_cell",
        fill=homog,
        region=+z_lo & -z_hi & -s_outer,
    )
    universe = openmc.Universe(cells=[cell])
    geometry = openmc.Geometry(universe)
    materials = openmc.Materials([homog])

    info = {
        "f_fuel": f_fuel,
        "f_graphite": f_graphite,
        "f_blanket": f_blanket,
        "temp_K": temp_K,
        "homog_material": homog.name,
    }
    return geometry, materials, info


__all__ = [
    "build_vf_geometry",
    "build_vf_geometry_homog",
    "vf_from_geometry",
    "ORNL_VF",
    "R_INNER_BORE_RATIO",
    "R_INNER_TUBE_RATIO",
]
