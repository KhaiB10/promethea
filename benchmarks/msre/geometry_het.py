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
- ORNL-TM-0728, MSRE Design and Operations Report, Part III.

Acceptance for this heterogeneous v1
------------------------------------
k-eff in the range 0.98 - 1.05  (loose; targets ~1.02)
"""
from __future__ import annotations

import math
from typing import Dict, List

import openmc

# ---------------------------------------------------------------------------
# Canonical IRPhE dimensions (cm unless stated)
# ---------------------------------------------------------------------------

STRINGER_PITCH      = 5.08          # 2 inches square lattice pitch
STRINGER_SIDE       = 5.08          # stringer is also 2 inches square
FUEL_CHANNEL_WIDTH  = 1.016         # half-groove width on each face
FUEL_CHANNEL_DEPTH  = 3.048 / 2.0   # half-groove depth (1.524 cm into each stringer)

ACTIVE_CORE_HEIGHT  = 166.446       # IRPhE graphite-active height
CORE_RADIUS         = 70.168        # IRPhE active-core equivalent radius

# Vessel and downcomer
CORE_BARREL_OR      = 142.24 / 2.0  # 56 in OD core barrel
VESSEL_ID           = 147.32 / 2.0  # 58 in ID vessel
VESSEL_WALL         = 1.27          # 0.5 in INOR-8 wall (typical)
VESSEL_OR           = VESSEL_ID + VESSEL_WALL
PLENUM_HEIGHT       = 40.64         # 16 in upper and lower plena (approximate)
TOTAL_VESSEL_HEIGHT = ACTIVE_CORE_HEIGHT + 2 * PLENUM_HEIGHT


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

    half_pitch = STRINGER_PITCH / 2.0     # 2.54
    half_chan  = FUEL_CHANNEL_WIDTH / 2.0  # 0.508
    notch_depth = FUEL_CHANNEL_DEPTH       # 1.524 into the stringer

    # Four notch surfaces, one per face.
    # +X face (right)
    x_in_R  = openmc.XPlane(half_pitch - notch_depth)
    y_lo_R  = openmc.YPlane(-half_chan)
    y_hi_R  = openmc.YPlane(+half_chan)
    notch_R = +x_in_R & +y_lo_R & -y_hi_R

    # -X face (left)
    x_in_L  = openmc.XPlane(-half_pitch + notch_depth)
    notch_L = -x_in_L & +y_lo_R & -y_hi_R

    # +Y face (top in 2D)
    y_in_T  = openmc.YPlane(half_pitch - notch_depth)
    x_lo_T  = openmc.XPlane(-half_chan)
    x_hi_T  = openmc.XPlane(+half_chan)
    notch_T = +y_in_T & +x_lo_T & -x_hi_T

    # -Y face (bottom in 2D)
    y_in_B  = openmc.YPlane(-half_pitch + notch_depth)
    notch_B = -y_in_B & +x_lo_T & -x_hi_T

    salt_region = notch_R | notch_L | notch_T | notch_B

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

    # Lattice region: a cylinder of radius CORE_RADIUS, height ACTIVE_CORE_HEIGHT,
    # centered at z = 0.
    core_outer = openmc.ZCylinder(r=CORE_RADIUS, name="core_lattice_outer")
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
    lattice = _build_core_lattice(mats)
    # The lattice must be enclosed in its own bounding cell to be placed.
    lat_extent = (lattice.lower_left[0], lattice.lower_left[1])
    n_cells_per_side = len(lattice.universes)
    lat_x_min = openmc.XPlane(lat_extent[0])
    lat_x_max = openmc.XPlane(lat_extent[0] + n_cells_per_side * STRINGER_PITCH)
    lat_y_min = openmc.YPlane(lat_extent[1])
    lat_y_max = openmc.YPlane(lat_extent[1] + n_cells_per_side * STRINGER_PITCH)

    lattice_cell = openmc.Cell(
        name="core_lattice_cell",
        fill=lattice,
        region=(+lat_x_min & -lat_x_max & +lat_y_min & -lat_y_max
                & +core_bot & -core_top),
    )

    # Salt outside the lattice but still inside the vessel ID, within the
    # active-core axial extent (this is the annular gap between the
    # square lattice envelope and the cylindrical vessel ID).
    salt_annulus_cell = openmc.Cell(
        name="core_salt_annulus",
        fill=mats["salt"],
        region=(-vessel_inner
                & ~(+lat_x_min & -lat_x_max & +lat_y_min & -lat_y_max)
                & +core_bot & -core_top),
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
        lattice_cell, salt_annulus_cell,
        upper_plenum, lower_plenum, vessel_wall,
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
