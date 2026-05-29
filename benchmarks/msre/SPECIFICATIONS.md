# MSRE Specification Sheet — Primary Sources

All numerical values here are derived from publicly available ORNL technical reports and the OECD/NEA IRPhE evaluation. US Government technical reports authored by federal employees are public domain.

## 1. Core geometry

| Parameter | Value | Reference |
|---|---|---|
| Active core height | 348.2 cm (11.42 ft) | ORNL-4119, IRPhE |
| Active core diameter | 274.3 cm (9 ft) | ORNL-4119, IRPhE |
| Graphite stringer cross-section | 5.08 × 5.08 cm (2 × 2 in) nominal | ORNL-4119 |
| Fuel salt channel cross-section | Roughly half-cylinder grooves on stringer faces | ORNL-4119 |
| Salt volume fraction in core | ~22.5 % | ORNL-4119 |
| Graphite volume fraction in core | ~76.0 % | ORNL-4119 |
| Number of graphite stringers | ~512 | ORNL-4119 |
| Number of control rod thimbles | 3 (triangular arrangement) | ORNL-4119 |
| Reactor vessel inner diameter | ~147.3 cm (58 in) | ORNL-4119 |
| Reactor vessel wall thickness | ~2.22 cm (7/8 in) INOR-8 | ORNL-4119 |
| Upper / lower head | Hemispherical, INOR-8 | ORNL-4119 |
| Lower head modeling (CSG benchmark) | Homogenized: 90.8 vol % fuel salt + 9.2 vol % INOR-8 | IRPhE |

## 2. Fuel salt (zero-power criticality, June 1965)

Composition (mole fractions):

| Component | Mole % | Notes |
|---|---|---|
| LiF (Li-7 enriched, ≥99.99 %) | 65.0 | |
| BeF₂ | 29.1 | |
| ZrF₄ | 5.0 | Suppresses UO₂ precipitation if oxygen enters salt |
| UF₄ | 0.9 | Fuel; ~33 % enriched U-235 in original loading |

Density at 911 K: **2.3275 g/cm³** (ORNL-TM-0728)
Operating temperature for benchmark: **911 K** (= 638 °C = 1180 °F)

## 3. Moderator graphite

| Parameter | Value | Reference |
|---|---|---|
| Grade | CGB graphite, Carbon Products Division of Union Carbide | ORNL-4119 |
| Density | 1.86 g/cm³ | ORNL-4119 |
| Boron impurity | ~0.3 ppm | ORNL-4119 |
| Thermal scattering kernel | `c_Graphite` (OpenMC built-in) | OpenMC docs |

## 4. INOR-8 (Hastelloy N) — structural alloy

Nominal composition (wt %, mid-range of spec):

| Element | wt % | Notes |
|---|---|---|
| Ni | 68.5 | Balance |
| Mo | 16.5 | Range 15–18 |
| Cr | 7.0 | Range 6–8 |
| Fe | 5.0 | Max |
| Mn | 1.0 | Max |
| Si | 1.0 | Max |
| C | 0.06 | Range 0.04–0.08 |
| Al + Ti | 0.5 | Combined |
| W | 0.5 | Max |
| Cu | 0.35 | Max |
| Co | 0.2 | Max |
| P | 0.015 | Max |
| S | 0.02 | Max |
| B | 0.010 | Max |

Density: **8.79 g/cm³**
Source: Haynes International Hastelloy N alloy datasheet (current spec).

## 5. Control rods

Three identical rods in a triangular pattern.

| Parameter | Value | Reference |
|---|---|---|
| Rod composition | Stacked Gd₂O₃–Al₂O₃ ceramic bushings | ORNL-4119 |
| Bushing composition | 70 wt % Gd₂O₃ + 30 wt % Al₂O₃ | ORNL-4119 |
| Cladding | Inconel-600 | ORNL-4119 |
| Triangular pitch | 10.16 cm between rod centers (4 in) | ORNL-4119 |
| At criticality (June 1965) | Rod #1 inserted 11.18 cm; other two fully withdrawn | IRPhE |

## 6. Operating conditions for benchmark

| Parameter | Value |
|---|---|
| Power | Zero-power critical (no fission heating) |
| Salt circulation | Static (stagnant) for the zero-power benchmark |
| Fuel temperature | 911 K |
| Graphite temperature | 911 K (isothermal) |
| Cover gas | Helium at 1 atm |

## 7. Cross-section library

Primary: **ENDF/B-VIII.0** (HDF5 form, OpenMC native).
Comparison runs may also use ENDF/B-VII.1 and JEFF 3.3 for sensitivity studies.

## 8. Expected results (acceptance criteria)

The first Promethea CSG run should produce:

- **k-eff = 1.020 ± 0.002** (matches published OpenMC CSG values within statistical uncertainty + cross-section variation)
- **Fuel temperature coefficient α_T,fuel ≈ –3 to –4 × 10⁻⁵ K⁻¹** (must be negative; magnitude per ORNL-4119 Part III)
- **Graphite temperature coefficient α_T,graphite ≈ +1 × 10⁻⁵ K⁻¹** (positive, smaller magnitude than fuel — net coefficient remains negative)

If the run lands inside these envelopes, the toolchain is validated and Phase 1.2 (digital twin) can begin.

## References

- **ORNL-4119:** *MSRE Design and Operations Report, Part III — Nuclear Analysis*. R.J. Kedl et al. (1965). [osti.gov/servlets/purl/4114686](https://www.osti.gov/servlets/purl/4114686/helpdisclaimer.pdf)
- **ORNL-TM-0728:** *MSRE Fuel Salt Compositions and Physical Properties*.
- **ORNL-4812:** *MSRE Design and Operations Report*.
- **IRPhE Handbook**, MSR-MSRE-RESR-001, OECD/NEA.
- **Yilmaz et al. (2024):** *CAD and constructive solid geometry modeling of the Molten Salt Reactor Experiment with OpenMC*. Frontiers in Nuclear Engineering. [frontiersin.org/articles/10.3389/fnuen.2024.1385478](https://www.frontiersin.org/journals/nuclear-engineering/articles/10.3389/fnuen.2024.1385478/full)
- **Shen et al. (2021):** Serpent benchmark of the MSRE.
- **Haynes International Hastelloy N alloy datasheet.**
