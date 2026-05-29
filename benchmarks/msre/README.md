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
| U-235 enrichment of uranium | 33.3 wt % | ORNL-4119 |
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
3. IRPhE fuel-salt loading (1.408 wt % U-235 in salt, back-solved to a 0.736 mol % UF₄ recipe), 33.3 wt % uranium enrichment, 99.995 at % Li-7.
4. Control rod thimbles approximated as withdrawn (no rod material modeled in v1).
5. Vessel modeled as a single INOR-8 annulus with vacuum boundary at the outer surface; plena above and below filled with salt.
6. Target k-eff: ~1.020 (published OpenMC CSG with rods withdrawn). Acceptance: 0.98 ≤ k ≤ 1.05.

Run it:

```bash
python benchmarks/msre/run_criticality.py --het          # full run
python benchmarks/msre/run_criticality.py --het --quick  # smoke
```

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

## Status

Phase 1.1 in progress.

- [x] Scaffold and reference data assembled
- [x] Materials module derived from primary sources (homogenized + IRPhE salts)
- [x] Homogenized CSG geometry module (v0)
- [x] Heterogeneous CSG geometry module (v1) — this milestone
- [x] Settings + run script with PASS/REVIEW envelope
- [x] GitHub Actions CI benchmark workflow
- [ ] First successful heterogeneous criticality run (CI in progress)
- [ ] Heterogeneous v2 with control rods + sample baskets
- [ ] Temperature coefficient sweep
- [ ] CAD/DAGMC stretch goal
- [ ] Write-up against the published OpenMC CSG result
