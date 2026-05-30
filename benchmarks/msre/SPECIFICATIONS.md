# MSRE Specification Sheet — Primary Sources

All numerical values here are derived from publicly available ORNL technical reports and the OECD/NEA IRPhE evaluation. US Government technical reports authored by federal employees are public domain.

## 1. Core geometry

| Parameter | Value | Reference |
|---|---|---|
| Active graphite core height | **166.446 ± 1 cm** (5.46 ft) | Fratoni / IRPhE |
| Active graphite core radius (equivalent) | **70.168 ± 0.2 cm** | Fratoni / IRPhE |
| Graphite stringer cross-section | 5.08 × 5.08 cm (2 × 2 in) | ORNL-4119 |
| Lattice pitch | 5.08 cm (2 in) square | ORNL-4119 |
| Fuel channel cross-section | **1.016 ± 0.127 cm × 3.048 ± 0.127 cm** (rectangular, formed by mating half-grooves on stringer faces) | Fratoni / IRPhE |
| Approximate channel count | ~1,140 equivalent full channels | ORNL TRANSFORM report (Pub133245) |
| Salt volume fraction in core (homogenized) | ~22.5 % | ORNL-4119 |
| Graphite volume fraction in core (homogenized) | ~76.0 % | ORNL-4119 |
| Number of control rod thimbles | 3 (triangular, near core axis) | ORNL-4119 |
| Core barrel OD | 142.24 cm (56 in) | ORNL Pub133245 |
| Reactor vessel ID | **147.32 cm (58 in)** | ORNL Pub133245 |
| Annular downcomer height | ~162.6 cm (64 in) | ORNL Pub133245 |
| Upper / lower head | Hemispherical, INOR-8 | ORNL-4119 |
| Lower head modeling (CSG benchmark) | Homogenized: 90.8 vol % fuel salt + 9.2 vol % INOR-8 | IRPhE |

Note on heights — earlier draft of this sheet listed the active core height as 348.2 cm, which conflated the *vessel* extent (vessel ID 58 in by ~6.6 ft total) with the *graphite-active* extent. The graphite-active height per IRPhE/Fratoni is 166.446 cm; the homogenized v0 model uses the larger envelope to keep flux escape losses bounded, while the heterogeneous v1 model uses the canonical 166.446 cm.

## 2. Fuel salt (zero-power criticality, June 1965)

Two compositions appear in the literature; both are supported in `materials.py`:

### 2a. Historical pump-fill recipe

| Component | Mole % | Notes |
|---|---|---|
| LiF (Li-7 enriched, ≥99.99 %) | 65.0 | |
| BeF₂ | 29.1 | |
| ZrF₄ | 5.0 | Suppresses UO₂ precipitation if oxygen enters salt |
| UF₄ | 0.9 | Fuel; 33.3 wt % U-235 enrichment |

This is the recipe used by `build_fuel_salt()` and the homogenized v0 model. It corresponds to roughly 2.5 wt % U-235 in salt.

### 2b. IRPhE first-criticality loading (used by heterogeneous v1)

| Component | Mole % | Notes |
|---|---|---|
| LiF (Li-7 enriched, 99.995 at %) | 65.04 | |
| BeF₂ | 29.22 | |
| ZrF₄ | 5.00 | |
| UF₄ | 0.736 | Back-solved to hit the IRPhE 1.408 wt % U-235-in-salt target |

**U-235 mass fraction in salt: 1.408 wt %** (Fratoni / IRPhE).
U-235 enrichment of the uranium: **33.3 wt %**.
This is the configuration used by `build_fuel_salt_irphe()` and the heterogeneous v1 model.

Density at 911 K (both recipes): **2.3275 ± 0.0160 g/cm³** (ORNL-TM-730)
Operating temperature for benchmark: **911 K** (= 638 °C = 1180 °F)

## 3. Moderator graphite

| Parameter | Value | Reference |
|---|---|---|
| Grade | CGB graphite, Carbon Products Division of Union Carbide | ORNL-4119 |
| Density | **1.87 ± 0.02 g/cm³** | Fratoni / IRPhE |
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

The Promethea benchmark suite has two acceptance gates.

### 8a. Homogenized v0 (Phase 1.1.a)
- **k-eff in 1.00 ≤ k ≤ 1.15** (loose envelope; homogenization biases k-eff upward)
- Purpose: validate the toolchain (cross-section linking, material build, S(α,β) kernel, source convergence)

### 8b. Heterogeneous v1 (Phase 1.1.b — this milestone)
- **k-eff in 0.98 ≤ k ≤ 1.05**, target **~1.020 ± 0.002** (matches published OpenMC CSG with rods withdrawn — Yilmaz 2024, Fratoni 2023)
- Three control rod thimbles approximated as withdrawn (deferred to v2)
- Sample baskets not modeled (deferred to v2)
- Axial taper region simplified

### 8c. Heterogeneous v2 (Phase 1.1.c — future)
- **k-eff in 0.995 ≤ k ≤ 1.010**, target **~1.000** (matches IRPhE experimental k-eff)
- Adds: regulating rod inserted to 46.6 in, fitted edge-stringer geometry, sample baskets, axial taper

### 8d. Temperature coefficients (Phase 1.1.d — future)
- **Fuel temperature coefficient α_T,fuel ≈ –3 to –4 × 10⁻⁵ K⁻¹** (must be negative; ORNL-4119 Part III)
- **Graphite temperature coefficient α_T,graphite ≈ +1 × 10⁻⁵ K⁻¹** (positive but smaller magnitude than fuel — net coefficient remains negative)

When 8b lands inside its envelope, the toolchain is validated for Phase 1.2 (digital twin) work in parallel.

## References

- **ORNL-4119:** *MSRE Design and Operations Report, Part III — Nuclear Analysis*. R.J. Kedl et al. (1965). [osti.gov/servlets/purl/4114686](https://www.osti.gov/servlets/purl/4114686/helpdisclaimer.pdf)
- **ORNL-TM-730:** *MSRE Fuel Salt Compositions and Physical Properties*.
- **ORNL-4812:** *MSRE Design and Operations Report*.
- **IRPhE Handbook**, MSR-MSRE-RESR-001, OECD/NEA.
- **Yilmaz et al. (2024):** *CAD and constructive solid geometry modeling of the Molten Salt Reactor Experiment with OpenMC*. Frontiers in Nuclear Engineering. [frontiersin.org/articles/10.3389/fnuen.2024.1385478](https://www.frontiersin.org/journals/nuclear-engineering/articles/10.3389/fnuen.2024.1385478/full)
- **Shen et al. (2021):** Serpent benchmark of the MSRE.
- **Haynes International Hastelloy N alloy datasheet.**
