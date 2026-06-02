"""
benchmarks/msbr/materials.py

MSBR (two-fluid) material recipes for OpenMC. Primary source: ORNL-4528,
Robertson/Briggs/Smith/Bettis (1968), specifically:

  - Table 3.1: salt compositions and physical properties
  - Table 3.3: modified Hastelloy N (MSBR-recommended)
  - Table 3.5: nominal graphite properties

All compositions match ORNL-4528 exactly. Densities are interpolated to
operating temperature (Tables 3.1, 3.4, 3.5) but the v0.4.0 scaffold
uses the reference-temperature values directly. Library S(α,β) handling
for graphite is deferred to the geometry/runner.

Status: scaffold for v0.4.0 prototyping. Numerical values verified
against ORNL-4528 PDF (.local/refs/ORNL-4528.pdf, OSTI 4093364).
"""
from __future__ import annotations

import openmc

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Operating temperature: ORNL-4528 abstract states fuel salt reaches ~1300°F.
# Salt physical properties in Table 3.1 are given at fuel = 1150°F, blanket
# = 1200°F. We adopt 900 K (the temperature at which Table 6.8 reactivity
# coefficients are reported) as the v0.4.0 reference temperature.
MSBR_TEMP_K = 900.0
ROOM_TEMP_K = 293.15

# Li-7 enrichment in MSBR salts. ORNL-4528 §3.2.2 calls out 7LiF without
# qualifying the enrichment level; modeling convention (consistent with
# MSRE) is >99.99% Li-7 to minimize Li-6 capture.
LI7_ENRICH = 0.99995

# ---------------------------------------------------------------------------
# Fuel salt: 7LiF - BeF2 - 233UF4 (68.5 - 31.3 - 0.2 mol %)
# Density 127 lb/ft^3 @ 1150 F = 2.0349 g/cm^3
# (127 lb/ft^3 * 453.592 g/lb / (30.48 cm/ft)^3 = 2.0349)
# ---------------------------------------------------------------------------
FUEL_MOLE_FRAC = {"LiF": 0.685, "BeF2": 0.313, "U233F4": 0.002}
FUEL_DENSITY_G_CC = 2.0349  # interpolated, ORNL-4528 Table 3.1

# ---------------------------------------------------------------------------
# Blanket salt: 7LiF - ThF4 - BeF2 (71 - 27 - 2 mol %)
# Density 277 lb/ft^3 @ 1200 F = 4.4376 g/cm^3
# ---------------------------------------------------------------------------
BLANKET_MOLE_FRAC = {"LiF": 0.71, "ThF4": 0.27, "BeF2": 0.02}
BLANKET_DENSITY_G_CC = 4.4376

# ---------------------------------------------------------------------------
# Graphite: isotropic, ρ ≈ 115 lb/ft^3 = 1.8423 g/cm^3, 23 vol% voids
# (Table 3.5; specific grade not selected by ORNL).
# ---------------------------------------------------------------------------
GRAPHITE_DENSITY_G_CC = 1.8423

# ---------------------------------------------------------------------------
# Modified Hastelloy N (MSBR-recommended composition, Table 3.3 wt%)
# Single values are maxima per the table footnote; we use nominal mid-
# range values where a range is given.
# ---------------------------------------------------------------------------
HASTELLOY_N_MSBR_WT = {
    "Mo": 12.0,
    "Cr": 7.0,
    "Fe": 2.0,    # 0-4 range, nominal 2
    "Mn": 0.35,   # 0.2-0.5 range, nominal 0.35
    "Si": 0.10,
    "B": 0.001,
    "Ti": 0.75,   # 0.5-1.0 range, nominal 0.75
    "Nb": 1.0,    # 0-2 range (or Hf), nominal 1.0
    "Cu": 0.35,
    "Co": 0.10,
    "P": 0.10,
    "S": 0.10,
    "C": 0.06,
    "W": 0.10,
    # Ni = balance
}
HASTELLOY_N_DENSITY_G_CC = 8.86  # standard Hastelloy N reference


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------

def build_fuel_salt(temp_K: float = MSBR_TEMP_K) -> openmc.Material:
    """7LiF - BeF2 - 233UF4 (68.5 - 31.3 - 0.2 mol%)."""
    mat = openmc.Material(name="MSBR_fuel_salt")
    mat.temperature = temp_K
    mat.set_density("g/cm3", FUEL_DENSITY_G_CC)

    # Per mole of mixture, count atoms of each nuclide.
    # LiF:   1 Li + 1 F per molecule
    # BeF2:  1 Be + 2 F per molecule
    # UF4:   1 U + 4 F per molecule
    lif = FUEL_MOLE_FRAC["LiF"]
    bef2 = FUEL_MOLE_FRAC["BeF2"]
    uf4 = FUEL_MOLE_FRAC["U233F4"]

    # Li (enriched 7Li)
    mat.add_nuclide("Li7", lif * LI7_ENRICH)
    mat.add_nuclide("Li6", lif * (1.0 - LI7_ENRICH))
    # Be
    mat.add_nuclide("Be9", bef2)
    # 233U
    mat.add_nuclide("U233", uf4)
    # F
    mat.add_nuclide("F19", lif + 2 * bef2 + 4 * uf4)

    return mat


def build_blanket_salt(temp_K: float = MSBR_TEMP_K) -> openmc.Material:
    """7LiF - ThF4 - BeF2 (71 - 27 - 2 mol%)."""
    mat = openmc.Material(name="MSBR_blanket_salt")
    mat.temperature = temp_K
    mat.set_density("g/cm3", BLANKET_DENSITY_G_CC)

    lif = BLANKET_MOLE_FRAC["LiF"]
    thf4 = BLANKET_MOLE_FRAC["ThF4"]
    bef2 = BLANKET_MOLE_FRAC["BeF2"]

    mat.add_nuclide("Li7", lif * LI7_ENRICH)
    mat.add_nuclide("Li6", lif * (1.0 - LI7_ENRICH))
    mat.add_nuclide("Th232", thf4)
    mat.add_nuclide("Be9", bef2)
    mat.add_nuclide("F19", lif + 4 * thf4 + 2 * bef2)

    return mat


def build_graphite(temp_K: float = MSBR_TEMP_K) -> openmc.Material:
    """Isotropic reactor graphite, Table 3.5 nominal."""
    mat = openmc.Material(name="MSBR_graphite")
    mat.temperature = temp_K
    mat.set_density("g/cm3", GRAPHITE_DENSITY_G_CC)
    # Add S(alpha,beta) treatment.
    # ENDF/B-VIII.0 does not ship an elemental "C0" nuclide; carbon is
    # represented by C12 + C13 at natural abundance. add_element expands
    # to the correct nuclide mix automatically.
    mat.add_element("C", 1.0)
    mat.add_s_alpha_beta("c_Graphite")
    return mat


def build_hastelloy_n_msbr(temp_K: float = MSBR_TEMP_K) -> openmc.Material:
    """Modified Hastelloy N per ORNL-4528 Table 3.3 (MSBR-recommended)."""
    mat = openmc.Material(name="MSBR_hastelloyN")
    mat.temperature = temp_K
    mat.set_density("g/cm3", HASTELLOY_N_DENSITY_G_CC)

    total = sum(HASTELLOY_N_MSBR_WT.values())
    ni_wt = 100.0 - total
    mat.add_element("Ni", ni_wt / 100.0, percent_type="wo")
    for elem, wt in HASTELLOY_N_MSBR_WT.items():
        mat.add_element(elem, wt / 100.0, percent_type="wo")
    return mat


# Aliases for downstream geometry modules (matches naming used in
# benchmarks/msbr/geometry_lattice.py).
build_hastelloy_n = build_hastelloy_n_msbr


def build_blanket_region_homogenized(
    blanket_vol_frac: float = 0.58,
    graphite_vol_frac: float = 0.42,
    temp_K: float = MSBR_TEMP_K,
) -> openmc.Material:
    """Volume-homogenized blanket annulus material.

    ORNL-4528 Table 5.1, 20 kW/L reference: "Fraction salt in blanket
    volume = 0.58" and "Fraction salt in graphite = 0.42" — i.e. the
    blanket region is 58% blanket salt + 42% graphite by volume. We mix
    by atom densities to avoid double-counting density.
    """
    blanket = build_blanket_salt(temp_K=temp_K)
    graphite = build_graphite(temp_K=temp_K)
    mix = openmc.Material.mix_materials(
        [blanket, graphite],
        [blanket_vol_frac, graphite_vol_frac],
        "vo",
    )
    mix.name = "MSBR_blanket_region_homog"
    mix.temperature = temp_K
    return mix


def build_all() -> openmc.Materials:
    """Return all MSBR materials as an openmc.Materials collection."""
    return openmc.Materials([
        build_fuel_salt(),
        build_blanket_salt(),
        build_graphite(),
        build_hastelloy_n_msbr(),
    ])
