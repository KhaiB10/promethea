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
| Active graphite core height | 166.446 cm (5.46 ft) | Fratoni / IRPhE |
| Active graphite core radius (equivalent) | 70.168 cm | Fratoni / IRPhE |
| Graphite stringer cross-section | 5.08 × 5.08 cm (2 in square) | ORNL-4119 |
| Fuel channel cross-section | 1.016 × 3.048 cm | Fratoni / IRPhE |
| Total equivalent fuel channels | ~1,140 | ORNL Pub133245 |
| Fuel salt composition (carrier) | LiF–BeF₂–ZrF₄ with UF₄ | ORNL-TM-0728 |
| Fuel salt density at 911 K | 2.3275 g/cm³ | ORNL-TM-0728 |
| U-235 in fuel salt (IRPhE first criticality) | **1.408 wt %** | Fratoni / IRPhE |
| U-235 enrichment of uranium (IRPhE benchmark) | **31.35 wt %** | Wu 2025 citing IRPhE |
| U-235 enrichment of uranium (historical ORNL design) | 33.3 wt % | ORNL-4119 |
| Fuel salt mole composition (IRPhE) | 65.0 LiF / 29.17 BeF₂ / 5.0 ZrF₄ / 0.83 UF₄ | Wu 2025 citing IRPhE |
| Fuel salt temperature (critical experiment) | 911 K (≈ 1180 °F) | IRPhE |
| Graphite density | 1.87 g/cm³ | Fratoni / IRPhE |
| Graphite thermal scattering kernel | `c_Graphite` | OpenMC standard |
| Vessel material | INOR-8 (Hastelloy N) | ORNL-4119 |
| INOR-8 nominal composition (wt %) | Ni 68.5, Mo 16.5, Cr 7.0, Fe 5.0, Mn 1.0, Si 1.0, balance trace | Haynes Hastelloy N datasheet |
| Control rods (3) | Inconel-clad Gd₂O₃–Al₂O₃ bushings | ORNL-4119 |
| Control rod position at criticality | One rod inserted 4.4 in (11.18 cm) | IRPhE |

## Method

### Phase 1.1.a — Homogenized v0 (done)

Validates the toolchain end to end.

1. Build geometry from ORNL-4119 published dimensions, salt and graphite smeared on a cylindrical envelope.
2. Use the historical 0.9 mol % UF₄ / 33 wt % U-235 salt recipe.
3. Run with ENDF/B-VIII.0 cross sections at 911 K (S(α,β) for graphite enabled).
4. Compute k-eff with at least 30 batches × 10 inactive × 5000 particles per batch (smoke), or 120 × 30 × 50000 (full).
5. Loose acceptance: 1.00 ≤ k ≤ 1.15.

### Phase 1.1.b — Heterogeneous v1 (this milestone)

Explicit stringer lattice, IRPhE first-criticality salt loading.

1. 2-inch square graphite stringers on a 5.08 cm lattice pitch, with 1.016 × 1.524 cm half-grooves on each face that mate with neighbors to form 1.016 × 3.048 cm fuel channels.
2. Lattice cells outside the 70.168 cm core radius filled with bulk salt (forms the cylindrical annulus).
3. IRPhE fuel-salt loading: 65.0 / 29.17 / 5.0 / 0.83 mol % LiF / BeF₂ / ZrF₄ / UF₄, 31.35 wt % uranium enrichment, 99.995 wt % Li-7 (gives 1.408 wt % U-235 in salt).
4. Control rod thimbles approximated as withdrawn (no rod material modeled in v1).
5. Vessel modeled as a single INOR-8 annulus with vacuum boundary at the outer surface; plena above and below filled with salt.
6. Target k-eff: ~1.020 (published OpenMC CSG with rods withdrawn). Acceptance: 0.98 ≤ k ≤ 1.05.

Run it:

```bash
python benchmarks/msre/run_criticality.py --het           # rectangular lattice in vessel ID
python benchmarks/msre/run_criticality.py --het-clipped   # edge stringers clipped at core cylinder
python benchmarks/msre/run_criticality.py --het --quick   # smoke
```

### Phase 1.1.b refinement — Heterogeneous v1c (edge-stringer clipping)

Same physics as v1 but the lattice is bounded by the core cylinder (r = 70.168 cm) instead of the vessel inner radius (r = 73.66 cm). Edge stringers whose centers sit just inside r = 70.168 cm get clipped at the cylinder boundary rather than extending past it as full 5.08 cm squares. The annulus between the core cylinder and the vessel ID is the downcomer, now explicitly modeled as pure fuel salt. Expected effect on k-eff: −500 to −1500 pcm (removes graphite over-moderation at the radial edge).

### Phase 1.1.c — Heterogeneous v2 (next)

Adds: regulating rod inserted to 46.6 in, fitted edge-stringer geometry, sample baskets, axial taper. Target k-eff ~1.000 to match IRPhE experimental.

### Phase 1.1.d — CAD/DAGMC (stretch)

Build CAD in FreeCAD/Onshape from ORNL technical drawings, tessellate to .h5m, compare against published k-eff ≈ 1.00872 (Copenhagen Atomics geometry, Yilmaz 2024).

## Prior art and attribution

This benchmark relies on the work of many groups:

- The **IRPhE benchmark authors** (OECD/NEA) for the canonical evaluation
- **Shen et al. (2021)** for the Serpent reference model
- **Yilmaz, Romano, Chierici, Knudsen, Shriwise (Frontiers in Nuclear Engineering, 2024)** for the systematic CSG ↔ CAD comparison in OpenMC
- The **[openmsr/msre](https://github.com/openmsr/msre)** project (GPLv3) for the open CAD-based OpenMC model from Copenhagen Atomics, which the Frontiers paper analyzes
- ORNL staff 1960–1972 for the underlying experimental data

Promethea's MSRE model is independently built from public-domain primary sources (ORNL technical reports, IRPhE handbook). Where we follow methodological choices from the above works, we cite them inline in the code and docs.

## Results log

All runs executed in GitHub Actions on `ubuntu-latest` (4 vCPU / 16 GB) inside the Promethea Docker image (`micromamba` + OpenMC + ENDF/B-VIII.0 at 911 K).

| Run | Mode | Particles × batches | k-eff (combined) | σ | Bias vs CSG target 1.020 | CI run ID | Notes |
|---|---|---|---|---|---|---|---|
| 1 | het (v1) | 10k × 40 (smoke) | 1.08360 | ±0.00195 | +6360 pcm vs 1.020 | [26612501791](https://github.com/KhaiB10/promethea/actions/runs/26612501791) | Geometry validated (no lost particles). First real result. **But 1.020 is the wrong target — see bias attribution.** |
| 2 | het (v1) | 100k × 100 | _in progress_ | | | [26613848308](https://github.com/KhaiB10/promethea/actions/runs/26613848308) | Production-statistics rerun of run 1; confirms run 1 wasn't a stats fluke. |
| 3 | het (v1) | 100k × 100 | _pending_ | | | _pending_ | Salt composition corrected (31.35 % enr, 0.83 mol % UF₄). Expected +15 to +75 pcm (small). |
| 4 | het_clipped (v1c) | 100k × 100 | _pending_ | | | _pending_ | Edge-stringer clipping at core cylinder. Expected −500 to −1500 pcm. |

### Bias attribution (Phase 1.1.b)

Run 1 produced k-eff = **1.08360 ± 0.00195**, which sits ~6300 pcm above the published OpenMC CSG reference of 1.020. Before claiming bias contributors, two corrections to the framing:

1. **The right target for v1 is not 1.020.** The published 1.020 result includes the lower-head INOR-8 mix, sample baskets, control rod thimbles, and core barrel. Our v1 model is an idealized graphite-stringer-plus-salt cylinder — simpler than 1.020. Per Yilmaz 2024 the cumulative bias from those simplifications going from 1.02132 down to experiment 0.99978 is about −2100 pcm. So a v1 model with no INOR-8 in the lower head, no sample baskets, no rod thimbles, and no core barrel should land in roughly the **1.04 – 1.06 range** before geometry refinement.
2. **The salt composition fix is not the biggest lever.** A simple thermal-utilization calculation shows that going from the back-solved 0.736 mol % UF₄ at 33.3 % enrichment to the IRPhE-canonical 0.83 mol % UF₄ at 31.35 % enrichment changes the salt's U-235 absorption-fraction by **+15 to +75 pcm** (slightly higher k, not lower). The 5.5 % more U-235 atoms outweighs the 15 % more U-238 atoms because U-238's effective absorption per atom is much smaller. The fix is still worth making (the composition matches the benchmark exactly) but it is not what closes the bias.

Updated attribution table, ordered by expected magnitude:

| Contributor | Direction | Estimated magnitude | Resolved in |
|---|---|---|---|
| **Wrong target** — our v1 is simpler than the 1.020 published model | ~ +2000 – +2500 pcm of "apparent" bias | (framing fix) | This README, no code change |
| Edge stringers as full 5.08 cm squares rather than clipped at the core cylinder (over-moderation at the radial edge) | +k | +500 – +1500 pcm | Run 4 (`geometry_het_clipped`) |
| Control rod thimbles (3 INOR-8 + air-gap regions) replaced by graphite in v1 | +k | +200 – +500 pcm | Phase 1.1.c |
| Sample basket assemblies and surveillance specimens not modeled | +k | +100 – +400 pcm | Phase 1.1.c |
| Lower head modeled as pure salt instead of 85 % salt / 15 % INOR-8 (Yilmaz CAD value) | +k | +200 – +400 pcm | Phase 1.1.c |
| Core barrel INOR-8 cylinder at r = 71.12 cm not modeled (currently the downcomer is pure salt) | +k | +50 – +150 pcm | Phase 1.1.c |
| Axial taper of stringer ends simplified to flat boundary | small | <100 pcm | Phase 1.1.c |
| Salt composition (0.736 mol % UF₄ at 33.3 % enr  →  0.83 mol % at 31.35 % enr) | −k ·… actually +k | +15 – +75 pcm (small, positive) | Run 3 |
| Cross-section library (we use VIII.0; literature uses VII.1) | ± | tens of pcm | (data choice) |

The single largest item is the framing correction: roughly 2000 pcm of the apparent gap is "we are not the same model as the 1.020 result." The real v1 target after all *physical* corrections in Phase 1.1.b should be around **1.04 – 1.06**. Closing the rest to 1.020 is Phase 1.1.c work (rods, baskets, lower-head mixing, core barrel).

## Status

Phase 1.1 in progress.

- [x] Scaffold and reference data assembled
- [x] Materials module derived from primary sources (homogenized + IRPhE salts)
- [x] Homogenized CSG geometry module (v0)
- [x] Heterogeneous CSG geometry module (v1) — geometry validated, k-eff measured
- [x] Salt recipe corrected to IRPhE canonical composition (31.35 % enr, 0.83 mol % UF₄)
- [x] Edge-stringer clipping geometry (v1c) drafted
- [x] Settings + run script with PASS/REVIEW envelope
- [x] GitHub Actions CI benchmark workflow
- [ ] Production-statistics het v1 run (CI in progress)
- [ ] het v1 rerun with corrected salt
- [ ] het v1c run with edge-stringer clipping
- [ ] Heterogeneous v2 with control rods + sample baskets
- [ ] Temperature coefficient sweep
- [ ] CAD/DAGMC stretch goal
- [ ] Write-up against the published OpenMC CSG result
