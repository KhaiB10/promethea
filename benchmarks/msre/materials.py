"""
benchmarks/msre/materials.py

MSRE material definitions for OpenMC, derived from primary public-domain sources:
  - ORNL-4119, MSRE Design and Operations Report Part III
  - ORNL-TM-0728, MSRE Fuel Salt Compositions
  - Haynes International Hastelloy N alloy spec

All compositions are entered in atom fractions or weight percent as
appropriate. The fuel salt is built up from the mole-fraction recipe
(LiF 65 / BeF2 29.1 / ZrF4 5 / UF4 0.9) and the natural isotopic
abundance of each element, modified for the historical MSRE U-235
enrichment (~33 wt %) and Li-7 enrichment (>99.99 %).

Reference k-eff target (CSG, ENDF/B-VIII.0): ~1.020 ± 0.002.
"""
from __future__ import annotations

import openmc

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BENCHMARK_TEMP_K = 911.0          # MSRE zero-power critical, 1180 F
ROOM_TEMP_K = 293.15

# Li-7 enrichment in MSRE fuel salt was >99.99 % to minimize Li-6 capture.
LI7_ENRICH = 0.99995              # atom fraction

# U-235 enrichment in the initial U-235 loading (clean salt, zero-power).
# Historical value for the U-235 critical experiment: 33.3 wt %.
U235_ENRICH_WT = 33.3             # weight %

# IRPhE first-criticality benchmark: U-235 in fuel salt = 1.408 wt %.
# (Fratoni / IRPhE; see ORNL 2023 MSR Workshop session 5.)
U235_WT_IN_SALT_IRPHE = 0.01408   # mass fraction

# Fuel salt mole fractions
SALT_MOLE_FRAC = {
    "LiF":  0.650,
    "BeF2": 0.291,
    "ZrF4": 0.050,
    "UF4":  0.009,
}
assert abs(sum(SALT_MOLE_FRAC.values()) - 1.0) < 1e-9


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
    salt.set_density("g/cm3", 2.3275)        # ORNL-TM-0728 at 911 K

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

def build_graphite(temperature_K: float = BENCHMARK_TEMP_K) -> openmc.Material:
    """
    Nuclear-grade CGB graphite used as MSRE moderator stringers.
    Includes a small boron impurity (the dominant neutronic effect).
    """
    g = openmc.Material(name="MSRE CGB graphite")
    g.temperature = temperature_K
    g.set_density("g/cm3", 1.87)      # IRPhE nominal (Fratoni)
    g.add_element("C", 0.9999997)     # by atom fraction
    g.add_nuclide("B10", 0.06e-6)     # ~0.3 ppm natural B by weight
    g.add_nuclide("B11", 0.24e-6)
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
    MSRE fuel salt at the IRPhE first-criticality loading.

    The benchmark fixes:
      U-235 mass fraction in salt = 1.408 wt %
      U-235 enrichment of the U   = 33.3 wt %
      Salt density                = 2.3275 g/cm3
      Carrier salt mole ratio     = 65 LiF / 29.2 BeF2 / 5 ZrF4 / (balance UF4)
      Li-7 enrichment             = 99.995 at %  (>99.99 % spec)

    The UF4 mole fraction is back-solved from the 1.408 wt % U-235 target
    instead of taken from the original 0.9 mol % pump-fill recipe, which
    corresponds to a more uranium-rich salt (closer to 2.5 wt % U-235).
    """
    salt = openmc.Material(name="MSRE fuel salt (IRPhE first criticality)")
    salt.temperature = temperature_K
    salt.set_density("g/cm3", 2.3275)

    # Molar masses (g/mol) of the four carrier salts. Using natural Li/Be/Zr
    # plus the explicit enriched-U mass for UF4.
    M_F   = 18.998
    M_Li  = 6.94    # natural -- close enough; we override isotopics below
    M_Be  = 9.012
    M_Zr  = 91.224
    M_U   = 235.044 * 0.333 + 238.051 * (1.0 - 0.333)   # 33.3% enriched U
    M_LiF  = M_Li + M_F
    M_BeF2 = M_Be + 2 * M_F
    M_ZrF4 = M_Zr + 4 * M_F
    M_UF4  = M_U  + 4 * M_F

    # Carrier salt mole ratios (sum to 99.2 mol %; UF4 takes the balance).
    # Solve for x_UF4 such that
    #   (mass U-235) / (mass salt) = 1.408 wt %
    # where mass-fraction-of-U-235 = 0.333 * mass-fraction-of-U.
    # Let xU = mole fraction UF4 and let the non-UF4 ratios be fixed at
    # (65 : 29.2 : 5) normalized to (1 - xU). Then
    #   wU = xU * M_U / (xU * M_UF4 + (1-xU) * M_carrier_avg)
    # where M_carrier_avg is the mole-weighted molar mass of LiF+BeF2+ZrF4.
    x_LiF_ratio  = 65.0 / 99.2
    x_BeF2_ratio = 29.2 / 99.2
    x_ZrF4_ratio = 5.0  / 99.2
    M_carrier_avg = (x_LiF_ratio  * M_LiF
                     + x_BeF2_ratio * M_BeF2
                     + x_ZrF4_ratio * M_ZrF4)

    # Target U-235 weight fraction in salt = 0.01408.
    # 0.01408 = 0.333 * (xU * M_U) / (xU * M_UF4 + (1 - xU) * M_carrier_avg)
    # => xU = 0.01408 * M_carrier_avg / (0.333 * M_U - 0.01408 * (M_UF4 - M_carrier_avg))
    target_wU235 = U235_WT_IN_SALT_IRPHE
    num = target_wU235 * M_carrier_avg
    den = 0.333 * M_U - target_wU235 * (M_UF4 - M_carrier_avg)
    xU = num / den
    x_LiF  = (1.0 - xU) * x_LiF_ratio
    x_BeF2 = (1.0 - xU) * x_BeF2_ratio
    x_ZrF4 = (1.0 - xU) * x_ZrF4_ratio
    x_UF4  = xU

    n_Li = x_LiF
    n_Be = x_BeF2
    n_Zr = x_ZrF4
    n_U  = x_UF4
    n_F  = x_LiF + 2 * x_BeF2 + 4 * x_ZrF4 + 4 * x_UF4
    total = n_Li + n_Be + n_Zr + n_U + n_F

    salt.add_nuclide("Li6", (n_Li / total) * (1.0 - LI7_ENRICH))
    salt.add_nuclide("Li7", (n_Li / total) * LI7_ENRICH)
    salt.add_nuclide("Be9", n_Be / total)
    zr_natural = {
        "Zr90": 0.5145, "Zr91": 0.1122, "Zr92": 0.1715,
        "Zr94": 0.1738, "Zr96": 0.0280,
    }
    for nuc, frac in zr_natural.items():
        salt.add_nuclide(nuc, (n_Zr / total) * frac)
    u_temp = openmc.Material()
    u_temp.add_element("U", 1.0, enrichment=U235_ENRICH_WT)
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
    mats = {
        "salt":     salt,
        "graphite": build_graphite(temperature_K),
        "inor":     build_inor8(temperature_K),
        "helium":   build_helium(temperature_K),
        "bushing":  build_control_bushing(),
        "inconel":  build_inconel600(),
    }
    return mats, openmc.Materials(list(mats.values()))


if __name__ == "__main__":
    mats, _ = build_all()
    print(f"Built {len(mats)} MSRE materials at T = {BENCHMARK_TEMP_K} K:")
    for name, m in mats.items():
        print(f"  {name:10s}  density={m.density:6.3f} g/cm3  nuclides={len(m.nuclides)}")
