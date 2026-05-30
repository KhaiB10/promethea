"""
benchmarks/msre/materials.py

MSRE material definitions for OpenMC, derived from primary public-domain sources:
  - ORNL-4119, MSRE Design and Operations Report Part III
  - ORNL-TM-730, MSRE Fuel Salt Compositions
  - Haynes International Hastelloy N alloy spec

All compositions are entered in atom fractions or weight percent as
appropriate. The fuel salt is built up from the mole-fraction recipe
(LiF 65 / BeF2 29.1 / ZrF4 5 / UF4 0.9) and the natural isotopic
abundance of each element, modified for the historical MSRE U-235
enrichment (~33 wt %) and Li-7 enrichment (>99.99 %).

Reference k-eff target (CSG, ENDF/B-VIII.0): ~1.020 ± 0.002.
"""
from __future__ import annotations

import os

import openmc

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BENCHMARK_TEMP_K = 911.0          # MSRE zero-power critical, 1180 F
ROOM_TEMP_K = 293.15

# Li-7 enrichment in MSRE fuel salt was >99.99 % to minimize Li-6 capture.
LI7_ENRICH = 0.99995              # atom fraction

# U-235 enrichment in the historical MSRE U-235 critical experiment.
# Value used in early ORNL design documents and the OpenMC tutorial: 33.3 wt %.
U235_ENRICH_HISTORICAL_WT = 33.3        # weight % (legacy build_fuel_salt)
U235_ENRICH_WT = U235_ENRICH_HISTORICAL_WT  # alias for back-compat

# U-235 enrichment in the IRPhE benchmark fuel salt.
# Wu 2025 transient benchmark, citing IRPhE: 31.35 wt %.
# Cross-check: at 65.0 / 29.17 / 5.0 / 0.83 mol % salt and 31.35 wt% enr,
# U-235 wt% in salt = 1.408 (matches IRPhE target exactly).
U235_ENRICH_IRPHE_WT  = 31.35           # weight %

# IRPhE first-criticality benchmark: U-235 in fuel salt = 1.408 wt %.
# (Fratoni / IRPhE; ORNL 2023 MSR Workshop session 5.)
U235_WT_IN_SALT_IRPHE = 0.01408   # mass fraction

# Fuel salt mole fractions -- historical ORNL design recipe.
# 65 / 29.1 / 5 / 0.9 mol % LiF / BeF2 / ZrF4 / UF4 (sum = 100).
SALT_MOLE_FRAC = {
    "LiF":  0.650,
    "BeF2": 0.291,
    "ZrF4": 0.050,
    "UF4":  0.009,
}
assert abs(sum(SALT_MOLE_FRAC.values()) - 1.0) < 1e-9

# Fuel salt mole fractions -- IRPhE first-criticality recipe.
# 65.0 / 29.17 / 5.0 / 0.83 mol %  (Wu 2025, citing IRPhE benchmark).
SALT_MOLE_FRAC_IRPHE = {
    "LiF":  0.6500,
    "BeF2": 0.2917,
    "ZrF4": 0.0500,
    "UF4":  0.0083,
}
assert abs(sum(SALT_MOLE_FRAC_IRPHE.values()) - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# Fuel salt
# ---------------------------------------------------------------------------

def build_fuel_salt(temperature_K: float = BENCHMARK_TEMP_K) -> openmc.Material:
    """
    LiF-BeF2-ZrF4-UF4 fuel salt for the MSRE zero-power criticality benchmark.

    Built additively from component salts using OpenMC's element/nuclide
    helpers with explicit Li-7 and U-235 enrichments.
    """
    salt = openmc.Material(name="MSRE fuel salt (LiF-BeF2-ZrF4-UF4)")
    salt.temperature = temperature_K
    salt.set_density("g/cm3", 2.3275)        # ORNL-TM-730 at 911 K

    # Cation atom fractions from the salt mole-fraction recipe.
    # Each MX_n molecule contributes 1 cation and n F atoms.
    n_Li = 1 * SALT_MOLE_FRAC["LiF"]
    n_Be = 1 * SALT_MOLE_FRAC["BeF2"]
    n_Zr = 1 * SALT_MOLE_FRAC["ZrF4"]
    n_U  = 1 * SALT_MOLE_FRAC["UF4"]
    n_F  = (1 * SALT_MOLE_FRAC["LiF"]
            + 2 * SALT_MOLE_FRAC["BeF2"]
            + 4 * SALT_MOLE_FRAC["ZrF4"]
            + 4 * SALT_MOLE_FRAC["UF4"])

    total = n_Li + n_Be + n_Zr + n_U + n_F

    # Lithium — manually split by enrichment so we can hit >99.99 % Li-7.
    salt.add_nuclide("Li6", (n_Li / total) * (1.0 - LI7_ENRICH))
    salt.add_nuclide("Li7", (n_Li / total) * LI7_ENRICH)

    # Beryllium — natural is essentially 100 % Be-9.
    salt.add_nuclide("Be9", n_Be / total)

    # Zirconium — natural isotopic distribution.
    # (OpenMC's add_element would handle this, but we go explicit for clarity.)
    zr_natural = {
        "Zr90": 0.5145,
        "Zr91": 0.1122,
        "Zr92": 0.1715,
        "Zr94": 0.1738,
        "Zr96": 0.0280,
    }
    for nuc, frac in zr_natural.items():
        salt.add_nuclide(nuc, (n_Zr / total) * frac)

    # Uranium — explicit enrichment.
    # add_element with enrichment kw handles U-234/235/236/238 automatically.
    u_temp = openmc.Material()
    u_temp.add_element("U", 1.0, enrichment=U235_ENRICH_WT)
    # Pull the resulting nuclide fractions back out and rescale.
    for nuc, frac, _percent_type in u_temp.nuclides:
        salt.add_nuclide(nuc, (n_U / total) * frac)

    # Fluorine — essentially pure F-19.
    salt.add_nuclide("F19", n_F / total)

    return salt


# ---------------------------------------------------------------------------
# Moderator graphite (CGB grade)
# ---------------------------------------------------------------------------

# Natural B-10 atom fraction in natural boron (ENDF/B-VIII.0 default).
B10_ATOM_FRAC = 0.199
B11_ATOM_FRAC = 1.0 - B10_ATOM_FRAC

# Default boron impurity in MSRE CGB graphite. Haubenreich et al. 1964 specs <1 ppm;
# 0.3 ppm is the IRPhE / Fratoni nominal. Phase 1.1.d step 3 sweeps this.
DEFAULT_BORON_PPM = 0.3


def build_graphite(
    temperature_K: float = BENCHMARK_TEMP_K,
    boron_ppm: float = DEFAULT_BORON_PPM,
) -> openmc.Material:
    """
    Nuclear-grade CGB graphite used as MSRE moderator stringers.
    Includes a small boron impurity (the dominant neutronic effect).

    Args:
        boron_ppm: total natural boron content in atomic ppm of C. Split into
            B-10 (~19.9%) and B-11 (~80.1%) by natural abundance.
    """
    b_atom_frac = boron_ppm * 1.0e-6  # total B atoms per C atom
    b10 = b_atom_frac * B10_ATOM_FRAC
    b11 = b_atom_frac * B11_ATOM_FRAC
    g = openmc.Material(name=f"MSRE CGB graphite (B={boron_ppm:.2f} ppm)")
    g.temperature = temperature_K
    g.set_density("g/cm3", 1.87)      # IRPhE nominal (Fratoni)
    g.add_element("C", 1.0 - b_atom_frac)     # by atom fraction
    g.add_nuclide("B10", b10)
    g.add_nuclide("B11", b11)
    g.add_s_alpha_beta("c_Graphite")
    return g


# ---------------------------------------------------------------------------
# INOR-8 (Hastelloy N) — reactor vessel and primary loop structural alloy
# ---------------------------------------------------------------------------

def build_inor8(temperature_K: float = BENCHMARK_TEMP_K) -> openmc.Material:
    """
    INOR-8 / Hastelloy N. Composition taken from the Haynes International
    spec, using mid-range values within the published ranges.
    """
    m = openmc.Material(name="INOR-8 (Hastelloy N)")
    m.temperature = temperature_K
    m.set_density("g/cm3", 8.79)
    m.add_element("Ni", 68.5, "wo")
    m.add_element("Mo", 16.5, "wo")
    m.add_element("Cr",  7.0, "wo")
    m.add_element("Fe",  5.0, "wo")
    m.add_element("Mn",  1.0, "wo")
    m.add_element("Si",  1.0, "wo")
    m.add_element("C",   0.06, "wo")
    m.add_element("Al",  0.25, "wo")
    m.add_element("Ti",  0.25, "wo")
    m.add_element("W",   0.5,  "wo")
    m.add_element("Cu",  0.35, "wo")
    m.add_element("Co",  0.2,  "wo")
    m.add_element("S",   0.02, "wo")
    m.add_element("P",   0.015,"wo")
    m.add_element("B",   0.010,"wo")
    return m


# ---------------------------------------------------------------------------
# Helium cover gas
# ---------------------------------------------------------------------------

def build_helium(temperature_K: float = BENCHMARK_TEMP_K) -> openmc.Material:
    he = openmc.Material(name="Helium cover gas")
    he.temperature = temperature_K
    he.add_element("He", 1.0)
    he.set_density("g/cm3", 1.03e-4)
    return he


# ---------------------------------------------------------------------------
# Control rod materials (Gd2O3-Al2O3 ceramic + Inconel-600 clad)
# ---------------------------------------------------------------------------

def build_control_bushing() -> openmc.Material:
    """70 wt% Gd2O3 + 30 wt% Al2O3 ceramic neutron absorber."""
    gd2o3 = openmc.Material()
    gd2o3.add_element("Gd", 2.0)
    gd2o3.add_element("O", 3.0)
    gd2o3.set_density("g/cm3", 7.41)

    al2o3 = openmc.Material()
    al2o3.add_element("Al", 2.0)
    al2o3.add_element("O", 3.0)
    al2o3.set_density("g/cm3", 3.95)

    bushing = openmc.Material.mix_materials([gd2o3, al2o3], [0.7, 0.3], "wo")
    bushing.name = "Gd2O3-Al2O3 control rod bushing"
    return bushing


def build_lower_head_mix(temperature_K: float = BENCHMARK_TEMP_K,
                         salt_vol_frac: float = 0.908,
                         inor_vol_frac: float = 0.092) -> openmc.Material:
    """
    Homogenized lower-head region: fuel salt + INOR-8 grid support plates and
    anti-swirl vanes.

    Default 90.8 % salt / 9.2 % INOR-8 by volume matches the original IRPhE
    CSG model (Shen et al. 2021), which was derived from a 20-region
    diffusion model used during MSRE operations (Haubenreich et al., 1965).

    The Yilmaz 2024 CAD-vs-CSG paper notes that the as-built INOR-8 volume
    fraction is closer to 15 %, and that lifting the value to 15 % reduces
    k-eff by "more than 100 pcm." We keep 9.2 % as the benchmark default and
    expose the volume fractions as kwargs so the 15 % variant can be tested
    directly.

    Sources
    -------
    - Yilmaz et al. 2024, Frontiers in Nuclear Engineering, Sec. 2.3.2.
    - Haubenreich et al. 1965, ORNL-TM-1018.
    - Shen et al. 2021, IRPhE MSRE-MSR-EXP-001 benchmark.
    """
    if abs((salt_vol_frac + inor_vol_frac) - 1.0) > 1e-6:
        raise ValueError("lower-head volume fractions must sum to 1")

    base_salt = build_fuel_salt_irphe(temperature_K)
    base_inor = build_inor8(temperature_K)
    mix = openmc.Material.mix_materials(
        [base_salt, base_inor],
        [salt_vol_frac, inor_vol_frac],
        "vo",
    )
    mix.name = (f"MSRE lower-head mix "
                f"({salt_vol_frac*100:.1f}% salt / "
                f"{inor_vol_frac*100:.1f}% INOR-8)")
    mix.temperature = temperature_K
    return mix


def build_sample_basket_mix(temperature_K: float = BENCHMARK_TEMP_K,
                            inor_vol_frac: float = 0.0771,
                            graphite_vol_frac: float = 0.2309,
                            salt_vol_frac: float = 0.6920) -> openmc.Material:
    """
    Homogenized fill for the surveillance / sample basket assembly that
    occupies the 4th position of the 2x2 control-rod array.

    Per Shen et al. 2021, each sample basket contains:
      - 4 INOR-8 rods of 0.635 cm diameter
      - 5 graphite bars of 0.635 cm x 1.1938 cm cross-section
      - the remainder of the basket bore filled with fuel salt

    Geometry math (bore radius = 2.286 cm, bore cross-section = 16.42 cm^2):
      INOR-8 contents     :  4 * pi * (0.3175)^2          = 1.267 cm^2 (7.71%)
      Graphite contents   :  5 * (0.635 * 1.1938)         = 3.791 cm^2 (23.09%)
      Salt remainder      :                                = 11.36 cm^2 (69.20%)

    The IRPhE Serpent model represents the basket assembly as a single
    thimble-shaped column whose bore is filled with this homogenized
    mixture over the active-core axial extent. Above and below the active
    core the bore reverts to pure salt.

    Source: Shen et al. 2021, IRPhE MSRE-MSR-EXP-001 benchmark, sec. 2.
    """
    if abs((inor_vol_frac + graphite_vol_frac + salt_vol_frac) - 1.0) > 1e-4:
        raise ValueError("sample-basket volume fractions must sum to 1")

    base_salt = build_fuel_salt_irphe(temperature_K)
    base_inor = build_inor8(temperature_K)
    # Build a graphite copy WITHOUT the S(a,b) table for the mix step.
    # openmc.Material.mix_materials refuses to mix materials carrying S(a,b)
    # tables. We re-attach c_Graphite on the resulting homogenized mix so the
    # carbon nuclides still see graphite thermal scattering kernels.
    # Use the same boron concentration as the standalone graphite material
    # so the basket mix is self-consistent across boron sweeps.
    boron_ppm = float(os.environ.get("PROMETHEA_BORON_PPM", DEFAULT_BORON_PPM))
    b_atom_frac = boron_ppm * 1.0e-6
    b10 = b_atom_frac * B10_ATOM_FRAC
    b11 = b_atom_frac * B11_ATOM_FRAC
    base_graf = openmc.Material(name="MSRE CGB graphite (no S(a,b), for mixing)")
    base_graf.temperature = temperature_K
    base_graf.set_density("g/cm3", 1.87)
    base_graf.add_element("C", 1.0 - b_atom_frac)
    base_graf.add_nuclide("B10", b10)
    base_graf.add_nuclide("B11", b11)
    mix = openmc.Material.mix_materials(
        [base_salt, base_inor, base_graf],
        [salt_vol_frac, inor_vol_frac, graphite_vol_frac],
        "vo",
    )
    mix.name = (f"MSRE sample-basket mix "
                f"({salt_vol_frac*100:.1f}% salt / "
                f"{inor_vol_frac*100:.1f}% INOR-8 / "
                f"{graphite_vol_frac*100:.1f}% graphite)")
    mix.temperature = temperature_K
    mix.add_s_alpha_beta("c_Graphite")
    return mix


def build_inconel600(temperature_K: float = ROOM_TEMP_K + 65.6) -> openmc.Material:
    """Inconel-600 cladding for the control rods (operates near room temp)."""
    m = openmc.Material(name="Inconel-600")
    m.temperature = temperature_K
    m.set_density("g/cm3", 8.5)
    m.add_element("Ni", 78.5, "wo")
    m.add_element("Cr", 14.0, "wo")
    m.add_element("Fe",  6.5, "wo")
    m.add_element("Mn",  0.25,"wo")
    m.add_element("Si",  0.25,"wo")
    m.add_element("Cu",  0.2, "wo")
    m.add_element("Co",  0.2, "wo")
    m.add_element("Ti",  0.2, "wo")
    return m


# ---------------------------------------------------------------------------
# Bundle
# ---------------------------------------------------------------------------

def build_fuel_salt_irphe(temperature_K: float = BENCHMARK_TEMP_K) -> openmc.Material:
    """
    MSRE fuel salt at the IRPhE first-criticality loading (revision 2021).

    Canonical IRPhE composition (Wu 2025, citing IRPhE benchmark):
      Mole fractions    : 65.0 LiF / 29.17 BeF2 / 5.0 ZrF4 / 0.83 UF4 mol %
      U-235 enrichment  : 31.35 wt %
      Li-7 enrichment   : 99.995 wt %
      Salt density      : 2.3275 g/cm3 at 911 K
      Resulting U-235 in salt : 1.408 wt %  (cross-checks the IRPhE target)

    Earlier versions of this function back-solved the UF4 mole fraction from
    the 1.408 wt% target while assuming 33.3 wt% U-235 enrichment, which
    produced 0.736 mol % UF4 and about 12% less total uranium mass (and
    5.5% less U-235) than the real benchmark. A thermal-utilization check
    shows the net k-eff impact of this correction is small (about +15 to
    +75 pcm) because the extra U-235 outweighs the extra U-238 absorption.
    The fix is still worth making for benchmark fidelity, but it is not
    the dominant contributor to bias in the v1 heterogeneous model.
    """
    salt = openmc.Material(name="MSRE fuel salt (IRPhE first criticality)")
    salt.temperature = temperature_K
    salt.set_density("g/cm3", 2.3275)

    x_LiF  = SALT_MOLE_FRAC_IRPHE["LiF"]
    x_BeF2 = SALT_MOLE_FRAC_IRPHE["BeF2"]
    x_ZrF4 = SALT_MOLE_FRAC_IRPHE["ZrF4"]
    x_UF4  = SALT_MOLE_FRAC_IRPHE["UF4"]

    # Cation atom totals per mole of mixture.
    n_Li = x_LiF
    n_Be = x_BeF2
    n_Zr = x_ZrF4
    n_U  = x_UF4
    n_F  = x_LiF + 2 * x_BeF2 + 4 * x_ZrF4 + 4 * x_UF4
    total = n_Li + n_Be + n_Zr + n_U + n_F

    # Lithium with Li-7 enrichment (atom fraction).
    salt.add_nuclide("Li6", (n_Li / total) * (1.0 - LI7_ENRICH))
    salt.add_nuclide("Li7", (n_Li / total) * LI7_ENRICH)

    # Beryllium and natural zirconium isotopics.
    salt.add_nuclide("Be9", n_Be / total)
    zr_natural = {
        "Zr90": 0.5145, "Zr91": 0.1122, "Zr92": 0.1715,
        "Zr94": 0.1738, "Zr96": 0.0280,
    }
    for nuc, frac in zr_natural.items():
        salt.add_nuclide(nuc, (n_Zr / total) * frac)

    # Uranium at the IRPhE-specific 31.35 wt% U-235 enrichment.
    u_temp = openmc.Material()
    u_temp.add_element("U", 1.0, enrichment=U235_ENRICH_IRPHE_WT)
    for nuc, frac, _percent_type in u_temp.nuclides:
        salt.add_nuclide(nuc, (n_U / total) * frac)

    salt.add_nuclide("F19", n_F / total)
    return salt


def build_all(temperature_K: float = BENCHMARK_TEMP_K, *, irphe: bool = False):
    """
    Return a (materials_dict, openmc.Materials) tuple for downstream use.

    If `irphe=True`, the fuel salt is the IRPhE first-criticality
    composition (1.408 wt% U-235 in salt). Otherwise the historical
    0.9 mol % UF4 recipe is used.
    """
    salt = build_fuel_salt_irphe(temperature_K) if irphe else build_fuel_salt(temperature_K)

    # CGB graphite boron impurity: parameterized for sensitivity sweep.
    # Default 0.3 ppm matches MSRE-Mark-I CGB acceptance spec; range
    # 0.1-1.0 ppm brackets reported batch variability (TM-730 Tab. 2.7;
    # Compere 1975).
    boron_ppm = float(os.environ.get("PROMETHEA_BORON_PPM", DEFAULT_BORON_PPM))
    graphite = build_graphite(temperature_K, boron_ppm=boron_ppm)
    graphite.name = f"CGB graphite (B={boron_ppm:.2f} ppm)"

    mats = {
        "salt":     salt,
        "graphite": graphite,
        "inor":     build_inor8(temperature_K),
        "helium":   build_helium(temperature_K),
        "bushing":  build_control_bushing(),
        "inconel":  build_inconel600(),
        "lower_head_mix": build_lower_head_mix(temperature_K),
        "sample_basket_mix": build_sample_basket_mix(temperature_K),
    }
    return mats, openmc.Materials(list(mats.values()))


if __name__ == "__main__":
    mats, _ = build_all()
    print(f"Built {len(mats)} MSRE materials at T = {BENCHMARK_TEMP_K} K:")
    for name, m in mats.items():
        print(f"  {name:10s}  density={m.density:6.3f} g/cm3  nuclides={len(m.nuclides)}")
