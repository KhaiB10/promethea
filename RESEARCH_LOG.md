# Promethea Research Log

A dated, append-only journal of significant findings, decisions, and
milestones in the Promethea MSRE benchmark project. Each entry is
self-contained enough to be quoted in a future paper's discussion
section.

---

## 2026-05-30 — Suspect 1: spurious INOR-8 shell at the sample-basket position (CLOSED)

### Finding

The Phase 1.1.c step-4 heterogeneous MSRE model (`build_geometry_het_baskets`,
`build_geometry_het_critical`) places a full-height INOR-8 thimble shell
at the sample-basket position (`thimble_3`), identical to the three
control-rod thimble positions.

This is inconsistent with both primary sources:

- **ORNL-TM-0728 §4.1** describes the basket position as *"a graphite
  sample assembly"* with no mention of an INOR-8 shell, in contrast
  with the control-rod thimbles whose INOR-8 walls are explicitly
  dimensioned (0.10-in thick, 6.00-in OD annulus representation).
- **Shen et al. 2021** describes *"three graphite and INOR-8 sample
  baskets"* whose Inconel content is the four 0.635-cm INOR-8 sample
  rods *inside* the basket, not a structural shell around it.

The shell volume per thimble position is ~789 cm³ of INOR-8
(annulus: OD 5.08 cm, ID 4.572 cm, height 205 cm), with the basket
position sitting at high importance (7.62 cm from core axis).

### Test

Single workflow input change: `basket_shell=false`, threaded via
`PROMETHEA_BASKET_SHELL` env var into both `build_geometry_het_baskets`
and `build_geometry_het_critical`. When false, the shell annulus at
the basket position is filled with primary salt instead of INOR-8.

CI run: 26678973305, 2026-05-30. Config: het_critical, 100k × 100,
0.3 ppm B, sharp corners, ENDF/B-VIII.0.

### Result

| Configuration | k-eff (combined) | σ | Δk vs baseline |
|---|---:|---:|---:|
| Baseline (Phase 1.1.d step 1, basket_shell=true) | 1.01308 | 0.00036 | — |
| **basket_shell=false** | **1.02353** | **0.00033** | **+1045 ± 49 pcm** |
| Shen-Serpent target | 1.02132 | 0.00003 | — |
| IRPhE experimental | 0.99978 | — | — |

Residual gap to Shen-Serpent: **−221 ± 33 pcm** (now an overshoot, not
an undershoot).

### Magnitude analysis

Prior prediction range: +100 to +250 pcm. Observed: +1045 pcm — about
4-10× the prediction. The under-prediction came from underestimating
the basket position's importance. Three contributing factors:

1. The basket sits at radius 7.62 cm, well inside the active fueled
   region where thermal flux peaks.
2. Inconel's thermal absorption (Ni-58 plus Mo, Cr, Fe) is large in
   absolute terms — INOR-8 acts almost as a control absorber when
   placed at central importance.
3. The shell axial extent is the full vessel height (~205 cm), not
   just the active core, so it absorbs in the upper and lower
   reflector regions as well.

The 1045 pcm worth is consistent with experimental control-rod-worth
data from the MSRE: the three actual control rods together have a
total worth of ~5400 pcm (Robertson 1965, MSRE Design and Operations
Report Part V), so a single INOR-8 shell tube of similar geometry
contributing ~1000 pcm of parasitic absorption is dimensionally
correct.

### Impact on Phase 1.1.d gap analysis

The cumulative gap analysis must be revised. Prior cumulative
explanation summed to ~500 pcm of the 824 pcm Shen-Serpent gap; the
basket shell alone provides +1045 pcm in the opposite direction.

| Effect | Δk (pcm) | Source |
|---|---:|---|
| Spurious basket INOR-8 shell removal | **+1045** | Phase 1.1.e Suspect 1 |
| Boron mismatch (1.0 → 0.3 ppm) | −196 | Phase 1.1.d Step C |
| Corner rounding | +12 (null) | Phase 1.1.d Step 2 |
| Library: JEFF-3.3 vs VIII.0 | +177 | Phase 1.1.d Step 3 |
| **Net Promethea config (best-known)** | **~+1038** | |
| Shen-Serpent target gap from VIII.0 baseline | +824 | |
| **Overshoot vs Shen** | **~+214 pcm** | |

The basket shell was the dominant defect by an order of magnitude
relative to the other three studied effects combined.

### Recommendation

`basket_shell=false` becomes the production default for the Phase 1.1.e
canonical configuration. The Phase 1.1.c step-4 `basket_shell=true`
configuration is retained as a regression-test point but is no longer
the recommended physics model.

### Remaining work

The 221 pcm overshoot of Shen is now within the inter-library spread
we measured in Phase 1.1.d step 3 (322 pcm spread across VII.1, VIII.0,
JEFF-3.3). This residual is no longer a "missing physics" question
and is consistent with normal calculational methodology differences.
Remaining audits (Suspects 2-4: fuel salt re-derivation, INOR-8
cladding thickness, lower-core lattice transition) are now polishing
work rather than gap-closing work.

---
## 2026-05-30 — ENDF/B-VII.0 OpenMC HDF5 availability (closed: not available)

### Context

Phase 1.1.e Suspect 2 was scoped to combine `basket_shell=false` with three
cross-section libraries (ENDF/B-VII.0, VII.1, JEFF-3.3) to isolate library
sensitivity at the corrected geometry. Shen et al. 2021 cites "ENDF/B-VII"
without a sub-version, so both VII.0 and VII.1 were targeted to bracket
Shen's choice.

### Finding

No first-party OpenMC HDF5 build of ENDF/B-VII.0 is published. The OpenMC
official data libraries page (openmc.org/official-data-libraries) lists
only ENDF/B-VII.1, ENDF/B-VIII.0, and JEFF-3.3. The LANL Box mirror
referenced in the OpenMC "data" section distributes VII.0 only in
MCNP/ACE format (`mcnp_endfb70/`), which OpenMC does not ingest directly.

CI run 26681314800 confirmed this: the archive downloaded and extracted
successfully but produced `mcnp_endfb70/` rather than the expected
`endfb-vii.0-hdf5/cross_sections.xml` layout, and the run aborted at the
"confirm cross-sections present" step.

### Decision

ENDF/B-VII.0 is removed from the Promethea-supported library list. Shen's
"ENDF/B-VII" is treated as ENDF/B-VII.1 for benchmark-comparison purposes:
VII.1 is the released update to VII.0 and is what most 2010s-era reactor
physics work in the OpenMC community uses by default.

### Future work

If a VII.0 comparison becomes scientifically necessary (e.g. for a
specific isotope where VII.0 → VII.1 introduced a known evaluation
change), the path is: convert the LANL MCNP/ACE VII.0 distribution to
HDF5 via NJOY's `openmc-ace-to-hdf5` utility, then host the resulting
archive on the project's own asset store. This is a separate
infrastructure project, not a Promethea benchmark step, and is deferred.

### Suspect 2 scope revision

The library sweep at `basket_shell=false` is now a 3-library comparison
(VIII.0, VII.1, JEFF-3.3) — sufficient to characterize the inter-library
spread at the corrected geometry. VIII.0 is the canonical configuration;
VII.1 reproduces Shen's reported library; JEFF-3.3 provides an
independent (European, different evaluator chain) cross-check.

---
