"""
benchmarks/msre/geometry_het.py

Heterogeneous MSRE core geometry (Phase 1.1.b).

This is the explicit-stringer model. Each graphite block is rendered as a
2-inch-square cell on a 2-inch lattice pitch; the inter-stringer fuel
channels are formed by the half-grooves cut into each face.

Approximations in this v1 heterogeneous build
---------------------------------------------
1. Square lattice extent is fit inside a cylindrical core radius of
   70.168 cm by simply masking cells whose centers fall outside that
   radius. The IRPhE benchmark uses a fitted edge-stringer geometry that
   tracks the cylinder boundary more faithfully; that refinement is
   deferred to 1.1.c.
2. Control rods are NOT modeled in this v1. The IRPhE first-criticality
   scenario has two rods at their upper (withdrawn) limit and one at
   46.6 in. We approximate as all three withdrawn for v1, then add the
   shim rod insertion in 1.1.c. Expected effect: about +500 pcm vs the
   experiment, i.e. our v1 k-eff target is roughly 1.020 (the published
   OpenMC CSG figure with rods withdrawn) rather than the experimental
   1.000.
3. The axial taper region at the top and bottom of the stringers is
   simplified to a flat boundary; this contributes <100 pcm bias
   according to the Fratoni sensitivity table.
4. Sample baskets are not modeled.

References
----------
- Fratoni, M., MSRE Criticality Benchmark, ORNL MSR Workshop 2023,
  session 5. Provides the canonical IRPhE dimensions.
- Yilmaz et al. (2024), Frontiers in Nuclear Engineering, "Criticality
  benchmarking of OpenMC against the Molten Salt Reactor Experiment."
  Published OpenMC CSG result: k = 1.020.
- ORNL-TM-730, MSRE Design and Operations Report, Part III.

Acceptance for this heterogeneous v1
------------------------------------
k-eff in the range 0.98 - 1.05  (loose; targets ~1.02)
"""
from __future__ import annotations

import math
import os
from typing import Dict, List

import openmc

# ---------------------------------------------------------------------------
# Canonical IRPhE dimensions (cm unless stated)
# ---------------------------------------------------------------------------

STRINGER_PITCH      = 5.08          # 2 inches square lattice pitch
STRINGER_SIDE       = 5.08          # stringer is also 2 inches square
# Half-channel cut into each face of every stringer.
# TM-730 §2.6 (Haubenreich et al. 1964): "Four half-channels 0.2- by 1.2-in. in each
# 2- by 2-in. graphite block." Shen et al. 2021: full channels formed between
# paired faces are 1.016 cm by 3.048 cm.
#
# Geometric meaning of each dimension on a single half-channel:
#   - depth INTO stringer (perpendicular to face) = 0.2 in = 0.508 cm
#   - length ALONG face   (parallel to face)      = 1.2 in = 3.048 cm
#
# Two facing half-channels combine into one full channel 1.016 cm wide
# (= 2 × 0.508) and 3.048 cm long. Sharp-corner fuel fraction:
#   4 × (0.508 × 3.048) / 5.08² = 6.194 / 25.806 = 0.240 ✓ (TM-730 §2.6)
FUEL_CHANNEL_DEPTH  = 0.508         # half-groove depth into stringer (0.2 in)
FUEL_CHANNEL_LENGTH = 3.048         # half-groove length along face   (1.2 in)

# Half-channel inner-corner rounding (TM-730 §2.6, Shen 2021).
# TM-730: "rounding the corners of the channels reduced the [fuel] fraction
# to 0.225" (from 0.240 for sharp corners). Shen 2021 §2 likewise notes
# "channels 1.016 cm by 3.048 cm with rounded corners". The two inner
# corners of each half-channel notch (where the notch floor meets the end
# walls) are filleted with quarter-circle arcs. Solving for the radius
# that takes fuel fraction 0.240 -> 0.225 across 8 corners per stringer:
#   8 * r^2 * (1 - pi/4) = (0.240 - 0.225) * 5.08^2
#   r ~= 0.475 cm   (about 93% of the 0.508 cm half-channel depth)
# Disabled (radius = 0) keeps the sharp-corner Phase 1.1.c geometry; set
# PROMETHEA_FILLET_RADIUS_CM in the environment to enable.
FUEL_CHANNEL_CORNER_R = float(os.environ.get("PROMETHEA_FILLET_RADIUS_CM", "0.0"))

ACTIVE_CORE_HEIGHT  = 166.446       # IRPhE graphite-active height
CORE_RADIUS         = 70.168        # IRPhE active-core equivalent radius

# Vessel, core can, and downcomer dimensions
# All from ORNL-TM-730 Table 3.1 (20-region IRPhE core model).
#
# Region I (Core can):       r = 27.75 to 28.00 in  =>  70.485 to 71.12 cm
# Region F (Downcomer):      r = 28.00 to 29.00 in  =>  71.12  to 73.66 cm
# Region B (Vessel wall):    r = 29.00 to 29.56 in  =>  73.66  to 75.08 cm
CORE_CAN_IR         = 70.485        # 27.75 in core can inner radius
CORE_CAN_OR         = 71.12         # 28.00 in core can outer radius (= 56 in OD / 2)
VESSEL_ID           = 73.66         # 29.00 in vessel inner radius
VESSEL_WALL         = 1.42          # 0.56 in INOR-8 wall (TM-730 Region B)

# Control rod thimble dimensions (ORNL-TM-730 §4.1).
# Each thimble has 2.00 in OD x 0.10 in wall = 5.08 cm OD, 0.254 cm wall.
# (Derived from the homogenized 6.00 in OD x 0.10 in thick annulus that
# preserves both volume and outside surface area for 3 thimbles.)
# Poison cylinder: 1.08 in OD x 0.12 in wall = 2.743 cm OD, 0.305 cm wall.
THIMBLE_OD          = 5.08          # 2.00 in OD
THIMBLE_WALL        = 0.254         # 0.10 in
THIMBLE_OR          = THIMBLE_OD / 2.0
THIMBLE_IR          = THIMBLE_OR - THIMBLE_WALL
POISON_OD           = 2.743         # 1.08 in OD
POISON_WALL         = 0.305         # 0.12 in
POISON_OR           = POISON_OD / 2.0
POISON_IR           = POISON_OR - POISON_WALL

# Control-rod axial positions (ORNL-TM-730, Shen et al. 2021).
# TM-730 datum: z = 0 at core bottom; active core extends 0 -> 65.53 in =
# 0 -> 166.45 cm. Our model places z = 0 at the *center* of the active core,
# so TM-730 z must be shifted by -ACTIVE_CORE_HEIGHT/2 = -83.225 cm to land
# in our datum.
# - All three rods fully withdrawn:  rod tip at TM-730 z = 129.54 cm
#                                    -> our z = +46.315 cm
# - One rod inserted 4.4 in:         rod tip at TM-730 z = 118.364 cm
#                                    -> our z = +35.139 cm
ROD_TIP_WITHDRAWN_Z = 129.54 - (ACTIVE_CORE_HEIGHT / 2.0)  # +46.315 cm
ROD_TIP_INSERTED_Z  = 118.364 - (ACTIVE_CORE_HEIGHT / 2.0) # +35.139 cm

# 2x2 control rod array layout (ORNL-TM-730 Fig 3.2, Shen Fig 2).
# Three control rod thimbles and one sample basket are arranged in a
# square 2x2 pattern around the reactor centerline. Each position sits
# one stringer pitch off the centerline in both x and y -> rod centers at
# (±pitch/2, ±pitch/2). Since pitch = 5.08 cm and thimble OD = 5.08 cm,
# the thimble at (+pitch/2, +pitch/2) is tangent to those at the other
# three positions. The IRPhE-Fig 3.2 layout shows them slightly separated
# with the actual center-to-center spacing equal to about 3 pitches —
# i.e. rod centers at (±1.5 * pitch, ±1.5 * pitch) = (±7.62, ±7.62) cm.
# That position is consistent with the TM-730 Table 3.1 Region K
# homogenized thimble annulus at r = 7.37-7.62 cm.
ROD_ARRAY_OFFSET    = 1.5 * STRINGER_PITCH   # 7.62 cm from centerline on each axis
VESSEL_OR           = VESSEL_ID + VESSEL_WALL
PLENUM_HEIGHT       = 40.64         # 16 in upper and lower plena (approximate)
TOTAL_VESSEL_HEIGHT = ACTIVE_CORE_HEIGHT + 2 * PLENUM_HEIGHT
# Legacy alias — some earlier code used a single "core barrel" name. The
# core barrel of MSRE *is* the core can; we keep the alias to avoid breakage.
CORE_BARREL_OR      = CORE_CAN_OR


# ---------------------------------------------------------------------------
# Stringer unit cell
# ---------------------------------------------------------------------------

def _build_stringer_universe(mats: Dict[str, openmc.Material]) -> openmc.Universe:
    """
    One 5.08 x 5.08 cm graphite stringer cell viewed from above.

    Geometry: a square graphite block with a rectangular fuel-salt notch
    cut into the centerline of each of the four faces. Adjacent stringers
    share notches to form full 1.016 x 3.048 cm fuel channels.

    The notches are modeled as four axis-aligned rectangular boxes that
    cut into the graphite. Outside the lattice cell, salt fills the rest
    of the universe (so notches at the cell boundary continue smoothly
    into the neighbor's notch).
    """
    graphite = mats["graphite"]
    salt     = mats["salt"]

    half_pitch = STRINGER_PITCH / 2.0       # 2.540
    notch_depth = FUEL_CHANNEL_DEPTH        # 0.508 into the stringer
    half_length = FUEL_CHANNEL_LENGTH / 2.0 # 1.524 along the face
    r = FUEL_CHANNEL_CORNER_R               # fillet radius (0 = sharp)

    # Four notch surfaces, one per face.
    # Each notch is `notch_depth` deep INTO the stringer (perpendicular to
    # the face) and `2*half_length` long ALONG the face (parallel to it).
    #
    # +X face (right): the notch is the strip of x near the right face,
    #                  centered on y=0.
    x_in_R  = openmc.XPlane(half_pitch - notch_depth)
    y_lo_x  = openmc.YPlane(-half_length)
    y_hi_x  = openmc.YPlane(+half_length)
    notch_R = +x_in_R & +y_lo_x & -y_hi_x

    # -X face (left): mirror of +X face about x=0.
    x_in_L  = openmc.XPlane(-half_pitch + notch_depth)
    notch_L = -x_in_L & +y_lo_x & -y_hi_x

    # +Y face (top in 2D): notch is the strip of y near the top face,
    #                      centered on x=0.
    y_in_T  = openmc.YPlane(half_pitch - notch_depth)
    x_lo_y  = openmc.XPlane(-half_length)
    x_hi_y  = openmc.XPlane(+half_length)
    notch_T = +y_in_T & +x_lo_y & -x_hi_y

    # -Y face (bottom in 2D): mirror of +Y face about y=0.
    y_in_B  = openmc.YPlane(-half_pitch + notch_depth)
    notch_B = -y_in_B & +x_lo_y & -x_hi_y

    salt_region = notch_R | notch_L | notch_T | notch_B

    # ---- Inner-corner rounding (TM-730 §2.6, Shen 2021) -------------------
    # The two inner corners of each half-channel notch (where the floor meets
    # the end walls) get filleted with quarter-circle arcs of radius r. We
    # take fuel out of those corners by intersecting the salt region with
    # the complement of each "sliver" (corner-square minus quarter-disc).
    #
    # Per-corner sliver geometry, e.g. +X face, +y end:
    #   sharp inner corner at (x_in_R, +half_length)
    #   bounding square: x in [x_in_R, x_in_R + r], y in [+half_length - r, +half_length]
    #   fillet disc center: (x_in_R + r, +half_length - r), radius r
    #   sliver = (bounding square) AND (outside the disc)
    if r > 0.0:
        if r > notch_depth or r > half_length:
            raise ValueError(
                f"fillet radius {r} cm exceeds half-channel depth ({notch_depth}) "
                f"or half-length ({half_length})"
            )
        x_in_R_v = half_pitch - notch_depth
        x_in_L_v = -half_pitch + notch_depth
        y_in_T_v = half_pitch - notch_depth
        y_in_B_v = -half_pitch + notch_depth

        slivers = []

        # +X face notch: two inner corners at (x_in_R_v, +/- half_length)
        for sy in (+1.0, -1.0):
            cx = x_in_R_v + r
            cy = sy * (half_length - r)
            disc = openmc.ZCylinder(x0=cx, y0=cy, r=r)
            sq = (+openmc.XPlane(x_in_R_v) & -openmc.XPlane(x_in_R_v + r))
            if sy > 0:
                sq = sq & (+openmc.YPlane(half_length - r) & -openmc.YPlane(half_length))
            else:
                sq = sq & (+openmc.YPlane(-half_length) & -openmc.YPlane(-half_length + r))
            slivers.append(sq & +disc)

        # -X face notch: corners at (x_in_L_v, +/- half_length)
        for sy in (+1.0, -1.0):
            cx = x_in_L_v - r
            cy = sy * (half_length - r)
            disc = openmc.ZCylinder(x0=cx, y0=cy, r=r)
            sq = (+openmc.XPlane(x_in_L_v - r) & -openmc.XPlane(x_in_L_v))
            if sy > 0:
                sq = sq & (+openmc.YPlane(half_length - r) & -openmc.YPlane(half_length))
            else:
                sq = sq & (+openmc.YPlane(-half_length) & -openmc.YPlane(-half_length + r))
            slivers.append(sq & +disc)

        # +Y face notch: corners at (+/- half_length, y_in_T_v)
        for sx in (+1.0, -1.0):
            cx = sx * (half_length - r)
            cy = y_in_T_v + r
            disc = openmc.ZCylinder(x0=cx, y0=cy, r=r)
            sq = (+openmc.YPlane(y_in_T_v) & -openmc.YPlane(y_in_T_v + r))
            if sx > 0:
                sq = sq & (+openmc.XPlane(half_length - r) & -openmc.XPlane(half_length))
            else:
                sq = sq & (+openmc.XPlane(-half_length) & -openmc.XPlane(-half_length + r))
            slivers.append(sq & +disc)

        # -Y face notch: corners at (+/- half_length, y_in_B_v)
        for sx in (+1.0, -1.0):
            cx = sx * (half_length - r)
            cy = y_in_B_v - r
            disc = openmc.ZCylinder(x0=cx, y0=cy, r=r)
            sq = (+openmc.YPlane(y_in_B_v - r) & -openmc.YPlane(y_in_B_v))
            if sx > 0:
                sq = sq & (+openmc.XPlane(half_length - r) & -openmc.XPlane(half_length))
            else:
                sq = sq & (+openmc.XPlane(-half_length) & -openmc.XPlane(-half_length + r))
            slivers.append(sq & +disc)

        # Remove slivers from the salt region (so graphite fills them).
        for sl in slivers:
            salt_region = salt_region & ~sl

    salt_cell = openmc.Cell(name="stringer_notch_salt",
                            fill=salt, region=salt_region)
    graphite_cell = openmc.Cell(name="stringer_graphite",
                                fill=graphite, region=~salt_region)

    return openmc.Universe(cells=[salt_cell, graphite_cell])


def _build_pure_salt_universe(mats: Dict[str, openmc.Material]) -> openmc.Universe:
    """Universe used for lattice cells outside the core-radius mask."""
    c = openmc.Cell(name="outer_salt", fill=mats["salt"])
    return openmc.Universe(cells=[c])


# ---------------------------------------------------------------------------
# Core lattice
# ---------------------------------------------------------------------------

def _build_core_lattice(mats: Dict[str, openmc.Material]) -> openmc.RectLattice:
    """
    Square lattice of graphite stringers. Lattice extent is chosen so the
    inscribed circle of radius CORE_RADIUS is fully covered. Cells whose
    centers lie outside the core radius are filled with pure salt.
    """
    stringer_uni = _build_stringer_universe(mats)
    salt_uni     = _build_pure_salt_universe(mats)

    # Number of cells per side so the lattice covers the core circle.
    n = 2 * int(math.ceil(CORE_RADIUS / STRINGER_PITCH)) + 1   # odd, centered

    lattice = openmc.RectLattice(name="msre_core_lattice")
    lattice.pitch = (STRINGER_PITCH, STRINGER_PITCH)
    lattice.lower_left = (-n * STRINGER_PITCH / 2.0,
                          -n * STRINGER_PITCH / 2.0)

    half_n = n // 2
    rows: List[List[openmc.Universe]] = []
    for j in range(n):
        row: List[openmc.Universe] = []
        # cell center y for row j (lattice index 0 is bottom)
        yc = (j - half_n) * STRINGER_PITCH
        for i in range(n):
            xc = (i - half_n) * STRINGER_PITCH
            if math.hypot(xc, yc) <= CORE_RADIUS:
                row.append(stringer_uni)
            else:
                row.append(salt_uni)
        rows.append(row)
    # OpenMC expects rows from top to bottom (y descending).
    lattice.universes = list(reversed(rows))
    lattice.outer = salt_uni
    return lattice


# ---------------------------------------------------------------------------
# Top-level geometry
# ---------------------------------------------------------------------------

def build_geometry_het(mats: Dict[str, openmc.Material]):
    """
    Build the heterogeneous MSRE geometry and return (geometry, extra_mats).
    """
    # --- Surfaces ---
    half_h = ACTIVE_CORE_HEIGHT / 2.0

    # Axial bounds of the active core (graphite + lattice region).
    core_bot   = openmc.ZPlane(-half_h, name="active_core_bottom")
    core_top   = openmc.ZPlane(+half_h, name="active_core_top")

    # Vessel and outer boundary.
    vessel_inner = openmc.ZCylinder(r=VESSEL_ID,  name="vessel_inner")
    vessel_outer = openmc.ZCylinder(r=VESSEL_OR,  name="vessel_outer",
                                    boundary_type="vacuum")
    vessel_bot   = openmc.ZPlane(-half_h - PLENUM_HEIGHT,
                                 name="vessel_bottom", boundary_type="vacuum")
    vessel_top   = openmc.ZPlane(+half_h + PLENUM_HEIGHT,
                                 name="vessel_top",    boundary_type="vacuum")

    # --- Lattice cell ---
    #
    # The lattice is placed inside a single cylindrical cell that spans the
    # full vessel ID radius and the active-core height. The lattice itself
    # has lattice.outer = salt_uni, so any track that exits the rectangular
    # lattice extent (but stays inside the vessel cylinder) finds pure salt
    # without ambiguity.
    #
    # This avoids the lost-particle issue we hit when the lattice cell was
    # bounded by a rectangle (lat_x/y planes) and a separate salt-annulus
    # cell tried to fill the corners between the rectangle and the vessel
    # cylinder. The corner geometry created surface ambiguity that lost
    # particles at the lat_x/y planes.
    lattice = _build_core_lattice(mats)

    lattice_cell = openmc.Cell(
        name="core_lattice_cell",
        fill=lattice,
        region=(-vessel_inner & +core_bot & -core_top),
    )

    # Upper plenum (fuel salt).
    upper_plenum = openmc.Cell(
        name="upper_plenum",
        fill=mats["salt"],
        region=(-vessel_inner & +core_top & -vessel_top),
    )
    lower_plenum = openmc.Cell(
        name="lower_plenum",
        fill=mats["salt"],
        region=(-vessel_inner & -core_bot & +vessel_bot),
    )

    # Vessel wall.
    vessel_wall = openmc.Cell(
        name="vessel_wall",
        fill=mats["inor"],
        region=(+vessel_inner & -vessel_outer
                & +vessel_bot & -vessel_top),
    )

    root = openmc.Universe(cells=[
        lattice_cell,
        upper_plenum, lower_plenum, vessel_wall,
    ])
    return openmc.Geometry(root), []


# ---------------------------------------------------------------------------
# v2 geometry: edge-stringer clipping at the core cylinder
# ---------------------------------------------------------------------------

def build_geometry_het_clipped(mats: Dict[str, openmc.Material]):
    """
    Same heterogeneous MSRE geometry as build_geometry_het, but the lattice
    is clipped at the core cylinder (r = CORE_RADIUS = 70.168 cm) rather
    than at the vessel inner radius.

    Why the change
    --------------
    In v1 the lattice cell spanned the full vessel-ID cylinder, so every
    lattice position inside the rectangular grid was either a graphite
    stringer (if its center sat within 70.168 cm of the axis) or pure
    salt. Two physical inaccuracies followed:

    1. Edge stringers whose centers sit just inside the core radius
       extend past r = 70.168 cm. We model them as full 5.08 cm squares,
       so they over-represent graphite at the radial edge and over-moderate
       leaking neutrons. Net effect: k-eff biased high by roughly +500 to
       +1500 pcm (Fratoni sensitivity table).

    2. The radial annulus between r = 70.168 cm and r = vessel_inner
       (73.66 cm) is the downcomer. In v1 it was filled by the lattice's
       outer=pure-salt universe, so material was right but the cell
       boundary did not match the IRPhE benchmark geometry exactly.

    Both are fixed by introducing a core_outer cylinder at CORE_RADIUS
    and splitting the active-core radial region into
      - lattice_cell      : inside core_outer
      - downcomer_cell    : between core_outer and vessel_inner
    The lattice's outer=salt_uni still handles lattice positions whose
    cell-center is outside the lattice rectangle but inside the core
    cylinder (the small slivers at the cylinder edge).
    """
    half_h = ACTIVE_CORE_HEIGHT / 2.0

    core_bot   = openmc.ZPlane(-half_h, name="active_core_bottom")
    core_top   = openmc.ZPlane(+half_h, name="active_core_top")
    core_outer = openmc.ZCylinder(r=CORE_RADIUS, name="core_cylinder")

    vessel_inner = openmc.ZCylinder(r=VESSEL_ID,  name="vessel_inner")
    vessel_outer = openmc.ZCylinder(r=VESSEL_OR,  name="vessel_outer",
                                    boundary_type="vacuum")
    vessel_bot   = openmc.ZPlane(-half_h - PLENUM_HEIGHT,
                                 name="vessel_bottom", boundary_type="vacuum")
    vessel_top   = openmc.ZPlane(+half_h + PLENUM_HEIGHT,
                                 name="vessel_top",    boundary_type="vacuum")

    lattice = _build_core_lattice(mats)

    # Lattice region: cylinder of CORE_RADIUS, active-core axial extent.
    lattice_cell = openmc.Cell(
        name="core_lattice_cell",
        fill=lattice,
        region=(-core_outer & +core_bot & -core_top),
    )

    # Downcomer / radial-reflector annulus, pure salt at active-core height.
    downcomer_cell = openmc.Cell(
        name="core_downcomer",
        fill=mats["salt"],
        region=(+core_outer & -vessel_inner & +core_bot & -core_top),
    )

    upper_plenum = openmc.Cell(
        name="upper_plenum",
        fill=mats["salt"],
        region=(-vessel_inner & +core_top & -vessel_top),
    )
    lower_plenum = openmc.Cell(
        name="lower_plenum",
        fill=mats["salt"],
        region=(-vessel_inner & -core_bot & +vessel_bot),
    )

    vessel_wall = openmc.Cell(
        name="vessel_wall",
        fill=mats["inor"],
        region=(+vessel_inner & -vessel_outer
                & +vessel_bot & -vessel_top),
    )

    root = openmc.Universe(cells=[
        lattice_cell, downcomer_cell,
        upper_plenum, lower_plenum, vessel_wall,
    ])
    return openmc.Geometry(root), []


# ---------------------------------------------------------------------------
# v1c-lh geometry: clipped lattice + lower-head 90.8% salt / 9.2% INOR-8 mix
# ---------------------------------------------------------------------------

def build_geometry_het_lh(mats: Dict[str, openmc.Material]):
    """
    Phase 1.1.c step 1: clipped heterogeneous geometry plus a homogenized
    lower-head region.

    Geometry is identical to build_geometry_het_clipped() except the
    lower_plenum cell is filled with mats["lower_head_mix"] (90.8 % salt /
    9.2 % INOR-8 by volume, per Shen et al. 2021 IRPhE CSG) instead of
    pure fuel salt.

    Rationale
    ---------
    The physical lower head contains 48 anti-swirl vanes and a grid plate
    that supports the graphite stringers. In the IRPhE CSG model this
    detail is captured by a homogenized mix rather than explicit
    structural cells. Adding the mix is the smallest, lowest-risk step
    toward the published 1.020 target: the change is local, well-defined,
    and the expected delta is in the range -100 to -300 pcm (Yilmaz 2024
    reports "more than 100 pcm" for the 9.2 -> 15 % variant; the 0 ->
    9.2 % step we are taking here should be the larger of the two).

    Other Phase 1.1.c additions (core can, sample baskets, control rod
    thimbles, rod insertion) are deferred to subsequent steps so each
    feature's k-eff contribution can be measured independently.
    """
    half_h = ACTIVE_CORE_HEIGHT / 2.0

    core_bot   = openmc.ZPlane(-half_h, name="active_core_bottom")
    core_top   = openmc.ZPlane(+half_h, name="active_core_top")
    core_outer = openmc.ZCylinder(r=CORE_RADIUS, name="core_cylinder")

    vessel_inner = openmc.ZCylinder(r=VESSEL_ID,  name="vessel_inner")
    vessel_outer = openmc.ZCylinder(r=VESSEL_OR,  name="vessel_outer",
                                    boundary_type="vacuum")
    vessel_bot   = openmc.ZPlane(-half_h - PLENUM_HEIGHT,
                                 name="vessel_bottom", boundary_type="vacuum")
    vessel_top   = openmc.ZPlane(+half_h + PLENUM_HEIGHT,
                                 name="vessel_top",    boundary_type="vacuum")

    lattice = _build_core_lattice(mats)

    lattice_cell = openmc.Cell(
        name="core_lattice_cell",
        fill=lattice,
        region=(-core_outer & +core_bot & -core_top),
    )

    downcomer_cell = openmc.Cell(
        name="core_downcomer",
        fill=mats["salt"],
        region=(+core_outer & -vessel_inner & +core_bot & -core_top),
    )

    upper_plenum = openmc.Cell(
        name="upper_plenum",
        fill=mats["salt"],
        region=(-vessel_inner & +core_top & -vessel_top),
    )

    # Lower head: homogenized 90.8 % salt / 9.2 % INOR-8 by volume.
    lower_head = openmc.Cell(
        name="lower_head_mix",
        fill=mats["lower_head_mix"],
        region=(-vessel_inner & -core_bot & +vessel_bot),
    )

    vessel_wall = openmc.Cell(
        name="vessel_wall",
        fill=mats["inor"],
        region=(+vessel_inner & -vessel_outer
                & +vessel_bot & -vessel_top),
    )

    root = openmc.Universe(cells=[
        lattice_cell, downcomer_cell,
        upper_plenum, lower_head, vessel_wall,
    ])
    return openmc.Geometry(root), []


# ---------------------------------------------------------------------------
# v1c-can geometry: clipped lattice + lower-head mix + INOR-8 core can
# ---------------------------------------------------------------------------

def build_geometry_het_can(mats: Dict[str, openmc.Material]):
    """
    Phase 1.1.c step 2: het_lh + an explicit INOR-8 core can between the
    graphite stringer assembly and the salt downcomer.

    Radial structure inside the active core height
    -----------------------------------------------
    r = 0      ->  70.168 cm:  graphite stringer lattice (in fuel salt)
    r = 70.168 -> 70.485 cm:   thin salt film (0.317 cm; between lattice edge
                               and core can inner radius)
    r = 70.485 -> 71.12 cm:    core can (INOR-8, 0.635 cm wall, TM-730 Region I)
    r = 71.12  -> 73.66 cm:    downcomer salt (TM-730 Region F)
    r = 73.66  -> 75.08 cm:    reactor vessel wall (INOR-8, 1.42 cm)

    Axially, the core can spans the active core height (-half_h to +half_h).
    Above and below it, the upper plenum and lower head extend to the
    vacuum boundaries; no can section is modeled inside the heads because
    TM-730 Table 3.1 shows region I (core can) bounded by 0 to 65.53 in,
    matching the active core.

    Expected k-eff delta vs het_lh: roughly -200 to -500 pcm. The INOR-8
    is a parasitic absorber at the radial boundary, where leaking thermal
    neutrons would otherwise reflect off salt and return to the core.
    """
    half_h = ACTIVE_CORE_HEIGHT / 2.0

    core_bot   = openmc.ZPlane(-half_h, name="active_core_bottom")
    core_top   = openmc.ZPlane(+half_h, name="active_core_top")
    core_outer = openmc.ZCylinder(r=CORE_RADIUS,  name="core_cylinder")
    can_inner  = openmc.ZCylinder(r=CORE_CAN_IR,  name="core_can_inner")
    can_outer  = openmc.ZCylinder(r=CORE_CAN_OR,  name="core_can_outer")

    vessel_inner = openmc.ZCylinder(r=VESSEL_ID,  name="vessel_inner")
    vessel_outer = openmc.ZCylinder(r=VESSEL_OR,  name="vessel_outer",
                                    boundary_type="vacuum")
    vessel_bot   = openmc.ZPlane(-half_h - PLENUM_HEIGHT,
                                 name="vessel_bottom", boundary_type="vacuum")
    vessel_top   = openmc.ZPlane(+half_h + PLENUM_HEIGHT,
                                 name="vessel_top",    boundary_type="vacuum")

    lattice = _build_core_lattice(mats)

    # Graphite lattice inside the core cylinder (r < 70.168 cm)
    lattice_cell = openmc.Cell(
        name="core_lattice_cell",
        fill=lattice,
        region=(-core_outer & +core_bot & -core_top),
    )

    # Thin salt film between lattice edge and core can inner wall
    salt_film = openmc.Cell(
        name="core_can_inner_salt_film",
        fill=mats["salt"],
        region=(+core_outer & -can_inner & +core_bot & -core_top),
    )

    # Core can: INOR-8 cylindrical shell (TM-730 Region I)
    core_can = openmc.Cell(
        name="core_can",
        fill=mats["inor"],
        region=(+can_inner & -can_outer & +core_bot & -core_top),
    )

    # True downcomer: salt annulus from can OD to vessel ID (TM-730 Region F)
    downcomer_cell = openmc.Cell(
        name="core_downcomer",
        fill=mats["salt"],
        region=(+can_outer & -vessel_inner & +core_bot & -core_top),
    )

    upper_plenum = openmc.Cell(
        name="upper_plenum",
        fill=mats["salt"],
        region=(-vessel_inner & +core_top & -vessel_top),
    )

    # Lower head: 90.8 % salt / 9.2 % INOR-8 by volume.
    lower_head = openmc.Cell(
        name="lower_head_mix",
        fill=mats["lower_head_mix"],
        region=(-vessel_inner & -core_bot & +vessel_bot),
    )

    vessel_wall = openmc.Cell(
        name="vessel_wall",
        fill=mats["inor"],
        region=(+vessel_inner & -vessel_outer
                & +vessel_bot & -vessel_top),
    )

    root = openmc.Universe(cells=[
        lattice_cell, salt_film, core_can, downcomer_cell,
        upper_plenum, lower_head, vessel_wall,
    ])
    return openmc.Geometry(root), []


def build_geometry_het_rods_out(mats: Dict[str, openmc.Material]):
    """
    Phase 1.1.c step 3: het_can + four explicit control rod thimbles in the
    fully-withdrawn position (rods parked above the active core).

    Layout (ORNL-TM-730 §4.1, Fig 3.2; Shen et al. 2021 Fig 2)
    -----------------------------------------------------------
    A 2x2 square array of vertical thimbles centered at
        (+/-7.62, +/-7.62) cm    (ROD_ARRAY_OFFSET = 1.5 * stringer pitch)
    Three positions hold cadmium-loaded control rods (Gd2O3/Al2O3 poison)
    and one holds the sample basket. For step 3 all four positions are
    treated as plain INOR-8 thimbles with a salt-filled bore — the rods
    are fully withdrawn, so the active core sees only the structural
    tube + salt bore (no poison present in the active region).

    Each thimble:
        OD = 5.08 cm  (2.00 in, ORNL-TM-730 §4.1)
        wall = 0.254 cm (0.10 in)
        bore: salt-filled

    The thimbles span the full vessel height (active core + lower head +
    upper plenum). Inside the lower head mix region the thimble shell
    sits in salt/INOR-8 mix; inside the core lattice region the thimble
    bodies are explicitly excluded from the graphite lattice cell.

    Expected k-eff delta vs het_can: roughly -100 to -200 pcm. Empty
    INOR-8 thimbles still absorb some thermal neutrons, and replacing
    ~4 stringer-cell volumes of graphite + salt with steel + bore salt
    perturbs the local moderation slightly.
    """
    half_h = ACTIVE_CORE_HEIGHT / 2.0

    core_bot   = openmc.ZPlane(-half_h, name="active_core_bottom")
    core_top   = openmc.ZPlane(+half_h, name="active_core_top")
    core_outer = openmc.ZCylinder(r=CORE_RADIUS,  name="core_cylinder")
    can_inner  = openmc.ZCylinder(r=CORE_CAN_IR,  name="core_can_inner")
    can_outer  = openmc.ZCylinder(r=CORE_CAN_OR,  name="core_can_outer")

    vessel_inner = openmc.ZCylinder(r=VESSEL_ID,  name="vessel_inner")
    vessel_outer = openmc.ZCylinder(r=VESSEL_OR,  name="vessel_outer",
                                    boundary_type="vacuum")
    vessel_bot   = openmc.ZPlane(-half_h - PLENUM_HEIGHT,
                                 name="vessel_bottom", boundary_type="vacuum")
    vessel_top   = openmc.ZPlane(+half_h + PLENUM_HEIGHT,
                                 name="vessel_top",    boundary_type="vacuum")

    # Four thimble positions: 2x2 array at (+/-ROD_ARRAY_OFFSET, +/-ROD_ARRAY_OFFSET).
    thimble_positions = [
        (+ROD_ARRAY_OFFSET, +ROD_ARRAY_OFFSET),
        (+ROD_ARRAY_OFFSET, -ROD_ARRAY_OFFSET),
        (-ROD_ARRAY_OFFSET, +ROD_ARRAY_OFFSET),
        (-ROD_ARRAY_OFFSET, -ROD_ARRAY_OFFSET),
    ]

    # Build the thimble surface pairs and the union region used to carve them
    # out of every cell they pass through.
    thimble_outer_surfs = []
    thimble_inner_surfs = []
    for i, (x, y) in enumerate(thimble_positions):
        thimble_outer_surfs.append(
            openmc.ZCylinder(x0=x, y0=y, r=THIMBLE_OR,
                             name=f"thimble_{i}_outer")
        )
        thimble_inner_surfs.append(
            openmc.ZCylinder(x0=x, y0=y, r=THIMBLE_IR,
                             name=f"thimble_{i}_inner")
        )

    # "outside all four thimbles" region (used to subtract from background cells).
    outside_thimbles = (+thimble_outer_surfs[0]
                        & +thimble_outer_surfs[1]
                        & +thimble_outer_surfs[2]
                        & +thimble_outer_surfs[3])

    lattice = _build_core_lattice(mats)

    # Graphite lattice inside the core cylinder, minus the four thimble shafts.
    lattice_cell = openmc.Cell(
        name="core_lattice_cell",
        fill=lattice,
        region=(-core_outer & +core_bot & -core_top & outside_thimbles),
    )

    # Thin salt film between lattice edge and core can inner wall (minus thimbles
    # — the thimbles are at r ~ 7.62 cm, well inside this region, so the film is
    # untouched, but we apply the carve for safety in case of future geometry edits).
    salt_film = openmc.Cell(
        name="core_can_inner_salt_film",
        fill=mats["salt"],
        region=(+core_outer & -can_inner & +core_bot & -core_top
                & outside_thimbles),
    )

    # Core can: INOR-8 cylindrical shell (TM-730 Region I)
    core_can = openmc.Cell(
        name="core_can",
        fill=mats["inor"],
        region=(+can_inner & -can_outer & +core_bot & -core_top),
    )

    # True downcomer: salt annulus from can OD to vessel ID (TM-730 Region F)
    downcomer_cell = openmc.Cell(
        name="core_downcomer",
        fill=mats["salt"],
        region=(+can_outer & -vessel_inner & +core_bot & -core_top),
    )

    # Upper plenum: salt + thimble shafts continuing up
    upper_plenum = openmc.Cell(
        name="upper_plenum",
        fill=mats["salt"],
        region=(-vessel_inner & +core_top & -vessel_top & outside_thimbles),
    )

    # Lower head mix: salt+INOR-8 mix, with thimble shafts continuing down
    lower_head = openmc.Cell(
        name="lower_head_mix",
        fill=mats["lower_head_mix"],
        region=(-vessel_inner & -core_bot & +vessel_bot & outside_thimbles),
    )

    vessel_wall = openmc.Cell(
        name="vessel_wall",
        fill=mats["inor"],
        region=(+vessel_inner & -vessel_outer
                & +vessel_bot & -vessel_top),
    )

    # Explicit thimble cells: INOR-8 shell + salt bore, full vessel height.
    thimble_cells = []
    for i, _ in enumerate(thimble_positions):
        bore = openmc.Cell(
            name=f"thimble_{i}_bore_salt",
            fill=mats["salt"],
            region=(-thimble_inner_surfs[i] & +vessel_bot & -vessel_top),
        )
        shell = openmc.Cell(
            name=f"thimble_{i}_shell",
            fill=mats["inor"],
            region=(+thimble_inner_surfs[i] & -thimble_outer_surfs[i]
                    & +vessel_bot & -vessel_top),
        )
        thimble_cells += [bore, shell]

    root = openmc.Universe(cells=[
        lattice_cell, salt_film, core_can, downcomer_cell,
        upper_plenum, lower_head, vessel_wall,
        *thimble_cells,
    ])
    return openmc.Geometry(root), []


def build_geometry_het_baskets(mats: Dict[str, openmc.Material]):
    """
    Phase 1.1.c step 4: het_rods_out + sample basket fill at the 4th array
    position.

    Three positions of the 2x2 thimble array hold control rods (here, plain
    INOR-8 thimbles with salt-filled bores since rods are withdrawn). The
    fourth position (chosen here as the (-,-) corner; the choice is arbitrary
    by 4-fold symmetry of the layout) holds the surveillance/sample
    assembly: same 5.08 cm OD INOR-8 thimble shell, but its bore is filled
    with a homogenized graphite + INOR-8 + salt mixture over the active core
    height to represent the four-INOR-8-rod and five-graphite-bar contents
    of each basket (Shen et al. 2021).

    Above and below the active core the basket bore reverts to pure salt.

    Expected k-eff delta vs het_rods_out: roughly -100 to -300 pcm. The
    extra graphite in the basket adds a small moderation boost in the
    central core, but the INOR-8 specimens are parasitic absorbers; the
    net effect in published IRPhE analyses is negative on k-eff.
    """
    half_h = ACTIVE_CORE_HEIGHT / 2.0

    core_bot   = openmc.ZPlane(-half_h, name="active_core_bottom")
    core_top   = openmc.ZPlane(+half_h, name="active_core_top")
    core_outer = openmc.ZCylinder(r=CORE_RADIUS,  name="core_cylinder")
    can_inner  = openmc.ZCylinder(r=CORE_CAN_IR,  name="core_can_inner")
    can_outer  = openmc.ZCylinder(r=CORE_CAN_OR,  name="core_can_outer")

    vessel_inner = openmc.ZCylinder(r=VESSEL_ID,  name="vessel_inner")
    vessel_outer = openmc.ZCylinder(r=VESSEL_OR,  name="vessel_outer",
                                    boundary_type="vacuum")
    vessel_bot   = openmc.ZPlane(-half_h - PLENUM_HEIGHT,
                                 name="vessel_bottom", boundary_type="vacuum")
    vessel_top   = openmc.ZPlane(+half_h + PLENUM_HEIGHT,
                                 name="vessel_top",    boundary_type="vacuum")

    # Four thimble positions. Index 3 (the (-,-) corner) holds the sample
    # basket; positions 0, 1, 2 are plain salt-bore thimbles.
    thimble_positions = [
        (+ROD_ARRAY_OFFSET, +ROD_ARRAY_OFFSET),
        (+ROD_ARRAY_OFFSET, -ROD_ARRAY_OFFSET),
        (-ROD_ARRAY_OFFSET, +ROD_ARRAY_OFFSET),
        (-ROD_ARRAY_OFFSET, -ROD_ARRAY_OFFSET),  # <- sample basket
    ]
    BASKET_INDEX = 3

    # Phase 1.1.e Suspect-1 audit:
    # TM-730 §4.1 says the 4th position is occupied by a "graphite sample
    # assembly" — it does NOT describe an INOR-8 shell at this position,
    # only at the three control-rod thimble positions. Shen 2021 similarly
    # describes the sample baskets as "graphite and INOR-8 sample baskets"
    # whose contents (graphite bars + INOR-8 specimens) are the only
    # Inconel in the basket, not a shell.
    # Set PROMETHEA_BASKET_SHELL=false to model the basket without the
    # INOR-8 thimble shell (default: true, matches Phase 1.1.c step 4).
    BASKET_HAS_SHELL = os.environ.get(
        "PROMETHEA_BASKET_SHELL", "true"
    ).lower() not in ("false", "0", "no")

    thimble_outer_surfs = []
    thimble_inner_surfs = []
    for i, (x, y) in enumerate(thimble_positions):
        thimble_outer_surfs.append(
            openmc.ZCylinder(x0=x, y0=y, r=THIMBLE_OR,
                             name=f"thimble_{i}_outer")
        )
        thimble_inner_surfs.append(
            openmc.ZCylinder(x0=x, y0=y, r=THIMBLE_IR,
                             name=f"thimble_{i}_inner")
        )

    outside_thimbles = (+thimble_outer_surfs[0]
                        & +thimble_outer_surfs[1]
                        & +thimble_outer_surfs[2]
                        & +thimble_outer_surfs[3])

    lattice = _build_core_lattice(mats)

    lattice_cell = openmc.Cell(
        name="core_lattice_cell",
        fill=lattice,
        region=(-core_outer & +core_bot & -core_top & outside_thimbles),
    )

    salt_film = openmc.Cell(
        name="core_can_inner_salt_film",
        fill=mats["salt"],
        region=(+core_outer & -can_inner & +core_bot & -core_top
                & outside_thimbles),
    )

    core_can = openmc.Cell(
        name="core_can",
        fill=mats["inor"],
        region=(+can_inner & -can_outer & +core_bot & -core_top),
    )

    downcomer_cell = openmc.Cell(
        name="core_downcomer",
        fill=mats["salt"],
        region=(+can_outer & -vessel_inner & +core_bot & -core_top),
    )

    upper_plenum = openmc.Cell(
        name="upper_plenum",
        fill=mats["salt"],
        region=(-vessel_inner & +core_top & -vessel_top & outside_thimbles),
    )

    lower_head = openmc.Cell(
        name="lower_head_mix",
        fill=mats["lower_head_mix"],
        region=(-vessel_inner & -core_bot & +vessel_bot & outside_thimbles),
    )

    vessel_wall = openmc.Cell(
        name="vessel_wall",
        fill=mats["inor"],
        region=(+vessel_inner & -vessel_outer
                & +vessel_bot & -vessel_top),
    )

    # Thimble cells. Thimbles 0, 1, 2 are full-height salt-bore.
    # Thimble at BASKET_INDEX has a basket-mix bore over the active core
    # and salt bore above/below.
    thimble_cells = []
    for i, _ in enumerate(thimble_positions):
        is_basket = (i == BASKET_INDEX)
        # Shell fill: Inconel for control-rod thimbles, and for the basket
        # only if BASKET_HAS_SHELL is true. Otherwise the shell annulus is
        # filled with the same material as the bore at that height (salt
        # outside the basket-mix axial range, basket-mix inside it). For
        # simplicity we fill the shell annulus with salt across the full
        # vessel height when the basket has no shell — the small overlap
        # with the basket-mix axial range is a sub-1% correction.
        if is_basket and not BASKET_HAS_SHELL:
            shell_fill = mats["salt"]
            shell_name = f"thimble_{i}_shell_NO_INOR_salt"
        else:
            shell_fill = mats["inor"]
            shell_name = f"thimble_{i}_shell"

        shell = openmc.Cell(
            name=shell_name,
            fill=shell_fill,
            region=(+thimble_inner_surfs[i] & -thimble_outer_surfs[i]
                    & +vessel_bot & -vessel_top),
        )
        thimble_cells.append(shell)

        if i == BASKET_INDEX:
            # Active-core bore: sample-basket homogenized mix
            basket_active = openmc.Cell(
                name=f"thimble_{i}_bore_basket_mix",
                fill=mats["sample_basket_mix"],
                region=(-thimble_inner_surfs[i]
                        & +core_bot & -core_top),
            )
            # Below active core: pure salt
            basket_below = openmc.Cell(
                name=f"thimble_{i}_bore_below_salt",
                fill=mats["salt"],
                region=(-thimble_inner_surfs[i]
                        & +vessel_bot & -core_bot),
            )
            # Above active core: pure salt
            basket_above = openmc.Cell(
                name=f"thimble_{i}_bore_above_salt",
                fill=mats["salt"],
                region=(-thimble_inner_surfs[i]
                        & +core_top & -vessel_top),
            )
            thimble_cells += [basket_active, basket_below, basket_above]
        else:
            bore = openmc.Cell(
                name=f"thimble_{i}_bore_salt",
                fill=mats["salt"],
                region=(-thimble_inner_surfs[i] & +vessel_bot & -vessel_top),
            )
            thimble_cells.append(bore)

    root = openmc.Universe(cells=[
        lattice_cell, salt_film, core_can, downcomer_cell,
        upper_plenum, lower_head, vessel_wall,
        *thimble_cells,
    ])
    return openmc.Geometry(root), []


def build_geometry_het_critical(mats: Dict[str, openmc.Material]):
    """
    Phase 1.1.c step 5: full IRPhE first-criticality configuration.

    Differences from het_baskets:
      - 2 control rod thimbles (positions 0, 1) are plain salt-bore (rods
        fully withdrawn -- poison parked above the active core where it has
        negligible effect; tip at TM-730 z = 129.54 cm, our z = +46.315 cm,
        i.e. only slightly above core center where the lattice still acts as
        a moderator. The IRPhE Serpent model approximates these withdrawn
        rods as simply absent, so we do the same: empty salt-bore thimbles).
      - 1 control rod thimble (position 2) has the rod inserted 4.4 inches
        below its withdrawn position. Poison tip at TM-730 z = 118.364 cm
        = our z = +35.139 cm. Poison cylinder extends from the tip upward.
      - 1 sample basket assembly (position 3, same as het_baskets).

    Inserted rod model (per ORNL-TM-730 sec 4.1, Shen et al. 2021):
      - Hollow Gd2O3/Al2O3 70/30 wt%% poison cylinder:
            OD = 2.743 cm (1.08 in)
            wall = 0.305 cm (0.12 in)
            ID = 2.133 cm
      - Inconel-600 cladding around the poison column (modeled as an
        annulus from poison_OR to thimble_IR; conservative simplification
        of the real flexible-hose construction).
      - Inside the poison ID: salt (the bushing has a hollow center).
      - The poison column extends from the tip elevation up to the top
        of the vessel; in the inserted configuration the upper boundary
        is approximated as the vessel top.

    Expected k-eff delta vs het_baskets: roughly -1000 to -1500 pcm.
    The single inserted Gd2O3 poison rod is the largest single negative
    reactivity contributor in the entire benchmark. If the previous
    steps land near 1.04-1.06, this step should bring k toward the
    IRPhE Serpent target of 1.02132.
    """
    half_h = ACTIVE_CORE_HEIGHT / 2.0

    core_bot   = openmc.ZPlane(-half_h, name="active_core_bottom")
    core_top   = openmc.ZPlane(+half_h, name="active_core_top")
    core_outer = openmc.ZCylinder(r=CORE_RADIUS,  name="core_cylinder")
    can_inner  = openmc.ZCylinder(r=CORE_CAN_IR,  name="core_can_inner")
    can_outer  = openmc.ZCylinder(r=CORE_CAN_OR,  name="core_can_outer")

    vessel_inner = openmc.ZCylinder(r=VESSEL_ID,  name="vessel_inner")
    vessel_outer = openmc.ZCylinder(r=VESSEL_OR,  name="vessel_outer",
                                    boundary_type="vacuum")
    vessel_bot   = openmc.ZPlane(-half_h - PLENUM_HEIGHT,
                                 name="vessel_bottom", boundary_type="vacuum")
    vessel_top   = openmc.ZPlane(+half_h + PLENUM_HEIGHT,
                                 name="vessel_top",    boundary_type="vacuum")

    # Position 2 is the inserted rod; position 3 is the sample basket.
    # The choice is arbitrary by 4-fold symmetry; pick adjacent corners so
    # the inserted rod and basket are not diagonally opposite (closer to
    # the IRPhE figure arrangement).
    thimble_positions = [
        (+ROD_ARRAY_OFFSET, +ROD_ARRAY_OFFSET),   # 0: withdrawn
        (+ROD_ARRAY_OFFSET, -ROD_ARRAY_OFFSET),   # 1: withdrawn
        (-ROD_ARRAY_OFFSET, +ROD_ARRAY_OFFSET),   # 2: inserted 4.4 in
        (-ROD_ARRAY_OFFSET, -ROD_ARRAY_OFFSET),   # 3: sample basket
    ]
    INSERTED_INDEX = 2
    BASKET_INDEX   = 3

    # Phase 1.1.e Suspect-1: optional removal of INOR-8 shell on the
    # sample-basket position only (see het_baskets docstring for rationale).
    BASKET_HAS_SHELL = os.environ.get(
        "PROMETHEA_BASKET_SHELL", "true"
    ).lower() not in ("false", "0", "no")

    thimble_outer_surfs = []
    thimble_inner_surfs = []
    for i, (x, y) in enumerate(thimble_positions):
        thimble_outer_surfs.append(
            openmc.ZCylinder(x0=x, y0=y, r=THIMBLE_OR,
                             name=f"thimble_{i}_outer")
        )
        thimble_inner_surfs.append(
            openmc.ZCylinder(x0=x, y0=y, r=THIMBLE_IR,
                             name=f"thimble_{i}_inner")
        )

    # Poison cylinder (for the single inserted rod): outer & inner radii.
    px, py = thimble_positions[INSERTED_INDEX]
    poison_outer_surf = openmc.ZCylinder(x0=px, y0=py, r=POISON_OR,
                                         name="poison_outer")
    poison_inner_surf = openmc.ZCylinder(x0=px, y0=py, r=POISON_IR,
                                         name="poison_inner")
    poison_tip_plane  = openmc.ZPlane(ROD_TIP_INSERTED_Z,
                                      name="poison_tip")

    outside_thimbles = (+thimble_outer_surfs[0]
                        & +thimble_outer_surfs[1]
                        & +thimble_outer_surfs[2]
                        & +thimble_outer_surfs[3])

    lattice = _build_core_lattice(mats)

    lattice_cell = openmc.Cell(
        name="core_lattice_cell",
        fill=lattice,
        region=(-core_outer & +core_bot & -core_top & outside_thimbles),
    )

    salt_film = openmc.Cell(
        name="core_can_inner_salt_film",
        fill=mats["salt"],
        region=(+core_outer & -can_inner & +core_bot & -core_top
                & outside_thimbles),
    )

    core_can = openmc.Cell(
        name="core_can",
        fill=mats["inor"],
        region=(+can_inner & -can_outer & +core_bot & -core_top),
    )

    downcomer_cell = openmc.Cell(
        name="core_downcomer",
        fill=mats["salt"],
        region=(+can_outer & -vessel_inner & +core_bot & -core_top),
    )

    upper_plenum = openmc.Cell(
        name="upper_plenum",
        fill=mats["salt"],
        region=(-vessel_inner & +core_top & -vessel_top & outside_thimbles),
    )

    lower_head = openmc.Cell(
        name="lower_head_mix",
        fill=mats["lower_head_mix"],
        region=(-vessel_inner & -core_bot & +vessel_bot & outside_thimbles),
    )

    vessel_wall = openmc.Cell(
        name="vessel_wall",
        fill=mats["inor"],
        region=(+vessel_inner & -vessel_outer
                & +vessel_bot & -vessel_top),
    )

    thimble_cells = []
    for i, _ in enumerate(thimble_positions):
        is_basket = (i == BASKET_INDEX)
        if is_basket and not BASKET_HAS_SHELL:
            shell_fill = mats["salt"]
            shell_name = f"thimble_{i}_shell_NO_INOR_salt"
        else:
            shell_fill = mats["inor"]
            shell_name = f"thimble_{i}_shell"
        shell = openmc.Cell(
            name=shell_name,
            fill=shell_fill,
            region=(+thimble_inner_surfs[i] & -thimble_outer_surfs[i]
                    & +vessel_bot & -vessel_top),
        )
        thimble_cells.append(shell)

        if i == INSERTED_INDEX:
            # Below the poison tip: pure salt fills the entire bore.
            below_tip = openmc.Cell(
                name=f"thimble_{i}_bore_below_tip",
                fill=mats["salt"],
                region=(-thimble_inner_surfs[i]
                        & +vessel_bot & -poison_tip_plane),
            )
            # Above the tip: salt outside poison_OD, poison annulus,
            # salt inside poison_ID.
            #   inside the bore (r < thimble_IR), above the tip:
            #     r < poison_IR:      salt (poison is hollow)
            #     poison_IR < r < poison_OR: Gd2O3/Al2O3 bushing
            #     poison_OR < r < thimble_IR: Inconel-600 cladding/structure
            poison_inside = openmc.Cell(
                name=f"thimble_{i}_poison_inner_salt",
                fill=mats["salt"],
                region=(-poison_inner_surf
                        & +poison_tip_plane & -vessel_top),
            )
            poison_annulus = openmc.Cell(
                name=f"thimble_{i}_poison_bushing",
                fill=mats["bushing"],
                region=(+poison_inner_surf & -poison_outer_surf
                        & +poison_tip_plane & -vessel_top),
            )
            poison_outer = openmc.Cell(
                name=f"thimble_{i}_poison_cladding",
                fill=mats["inconel"],
                region=(+poison_outer_surf & -thimble_inner_surfs[i]
                        & +poison_tip_plane & -vessel_top),
            )
            thimble_cells += [below_tip, poison_inside,
                              poison_annulus, poison_outer]

        elif i == BASKET_INDEX:
            basket_active = openmc.Cell(
                name=f"thimble_{i}_bore_basket_mix",
                fill=mats["sample_basket_mix"],
                region=(-thimble_inner_surfs[i]
                        & +core_bot & -core_top),
            )
            basket_below = openmc.Cell(
                name=f"thimble_{i}_bore_below_salt",
                fill=mats["salt"],
                region=(-thimble_inner_surfs[i]
                        & +vessel_bot & -core_bot),
            )
            basket_above = openmc.Cell(
                name=f"thimble_{i}_bore_above_salt",
                fill=mats["salt"],
                region=(-thimble_inner_surfs[i]
                        & +core_top & -vessel_top),
            )
            thimble_cells += [basket_active, basket_below, basket_above]
        else:
            # Withdrawn rod -> plain salt-bore thimble.
            bore = openmc.Cell(
                name=f"thimble_{i}_bore_salt",
                fill=mats["salt"],
                region=(-thimble_inner_surfs[i] & +vessel_bot & -vessel_top),
            )
            thimble_cells.append(bore)

    root = openmc.Universe(cells=[
        lattice_cell, salt_film, core_can, downcomer_cell,
        upper_plenum, lower_head, vessel_wall,
        *thimble_cells,
    ])
    return openmc.Geometry(root), []


# Re-export geometry constants under canonical names for convenience.
ACTIVE_CORE_HEIGHT_HET = ACTIVE_CORE_HEIGHT
CORE_RADIUS_HET = CORE_RADIUS


if __name__ == "__main__":
    # Smoke check: build geometry with minimal materials and report
    # how many stringer cells were populated.
    import sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
    from materials import build_all
    mats_dict, _ = build_all(irphe=True)
    geom, _ = build_geometry_het(mats_dict)
    n_cells = sum(1 for _ in geom.get_all_cells().values())
    print(f"Heterogeneous MSRE geometry built. Cell count = {n_cells}")
