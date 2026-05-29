# MSRE Benchmark

The Molten Salt Reactor Experiment (Oak Ridge, 1965–1969) is the canonical validation target for any MSR simulation code. Before Promethea claims anything novel, the toolchain must reproduce known MSRE quantities.

## What we are validating against

The official reference is the **IRPhE MSRE benchmark** in the *International Handbook of Evaluated Reactor Physics Benchmark Experiments* (OECD/NEA), based on the zero-power critical experiment of June 1965 with U-235 fuel.

**Published k-eff values:**

| Source | k-eff | Notes |
|---|---|---|
| IRPhE benchmark, post-bias | **0.99978** | The "experimental" value |
| Shen et al. (2021), Serpent + ENDF/B-VII.1 | 1.02132 ± 0.00003 | Standard CSG reference, ~2 % high vs experiment |
| Yilmaz et al. (2024), OpenMC CSG | within 10 pcm of Serpent | Documents the conversion |
| Yilmaz et al. (2024), OpenMC CAD (Copenhagen Atomics geometry) | **1.00872** | Much closer to experiment than CSG |

The ~2 % bias in the CSG model is a known artifact of geometric simplifications (homogenized lower head, no anti-swirl vanes, simplified surveillance assembly). The CAD-based DAGMC model removes most of that bias.

**Target for Promethea v0 of this benchmark:** reproduce the *CSG* result (k-eff in the 1.020 ± 0.002 range) using OpenMC + ENDF/B-VIII.0. Match the published OpenMC CSG figure within ~50 pcm. That proves our toolchain is consistent with the literature.

**Stretch (Phase 1.1.b):** integrate a CAD/DAGMC geometry to close the ~2 % gap to experiment.

## Core reference data

| Quantity | Value | Source |
|---|---|---|
| Active core height | 11.42 ft (348.2 cm) | ORNL-4119, IRPhE |
| Active core diameter | 9 ft (274.3 cm) | ORNL-4119, IRPhE |
| Fuel salt composition | LiF–BeF₂–ZrF₄–UF₄, 65–29.1–5–0.9 mol % | ORNL-TM-0728 |
| Fuel salt density at 911 K | 2.3275 g/cm³ | ORNL-TM-0728 |
| Fuel salt temperature (critical experiment) | 911 K (≈ 1180 °F) | IRPhE |
| Graphite density | 1.86 g/cm³ | ORNL-4119 |
| Graphite thermal scattering kernel | `c_Graphite` | OpenMC standard |
| Vessel material | INOR-8 (Hastelloy N) | ORNL-4119 |
| INOR-8 nominal composition (wt %) | Ni 68.5, Mo 16.5, Cr 7.0, Fe 5.0, Mn 1.0, Si 1.0, balance trace | Haynes Hastelloy N datasheet |
| Control rods (3) | Inconel-clad Gd₂O₃–Al₂O₃ bushings | ORNL-4119 |
| Control rod position at criticality | One rod inserted 4.4 in (11.18 cm) | IRPhE |

## Method

Phase 1.1.a — **CSG model** (fully reproducible from primary sources):

1. Build geometry from ORNL-4119 published dimensions
2. Use isotopic compositions derived from ORNL-TM-0728 (we re-derive; do not copy from openmsr)
3. Run with ENDF/B-VIII.0 cross sections at 911 K (S(α,β) for graphite enabled)
4. Compute k-eff with at least 100 batches × 50 inactive × 50,000 particles per batch
5. Compare to the published OpenMC CSG result

Phase 1.1.b — **CAD/DAGMC model** (stretch goal):

1. Build CAD in FreeCAD or Onshape using ORNL technical drawings
2. Export STEP → tessellate to .h5m using DAGMC
3. Run same OpenMC simulation against the CAD geometry
4. Compare to the published k-eff ≈ 1.00872 result

## Prior art and attribution

This benchmark relies on the work of many groups:

- The **IRPhE benchmark authors** (OECD/NEA) for the canonical evaluation
- **Shen et al. (2021)** for the Serpent reference model
- **Yilmaz, Romano, Chierici, Knudsen, Shriwise (Frontiers in Nuclear Engineering, 2024)** for the systematic CSG ↔ CAD comparison in OpenMC
- The **[openmsr/msre](https://github.com/openmsr/msre)** project (GPLv3) for the open CAD-based OpenMC model from Copenhagen Atomics, which the Frontiers paper analyzes
- ORNL staff 1960–1972 for the underlying experimental data

Promethea's MSRE model is independently built from public-domain primary sources (ORNL technical reports, IRPhE handbook). Where we follow methodological choices from the above works, we cite them inline in the code and docs.

## Status

Phase 1.1 in progress.

- [x] Scaffold and reference data assembled
- [ ] Materials module derived from primary sources
- [ ] CSG geometry module
- [ ] Settings + tallies module
- [ ] First criticality run, compare to published OpenMC CSG k-eff
- [ ] Temperature coefficient sweep
- [ ] Documentation of results
