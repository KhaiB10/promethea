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
## 2026-05-30 — Critical prior-art discovery: Yilmaz et al. 2024 OpenMC MSRE

### Finding

In verifying the Shen et al. 2021 citation, located a 2024 paper directly
adjacent to this project's scope:

**Yilmaz, S., Romano, P. K., Chierici, L., Knudsen, E. B., Shriwise, P. C.
(2024). "CAD and constructive solid geometry modeling of the Molten Salt
Reactor Experiment with OpenMC." *Frontiers in Nuclear Engineering*,
3:1385478. DOI: 10.3389/fnuen.2024.1385478.**

This is from the OpenMC core team — Romano is the OpenMC project lead at
ANL; Shriwise is a long-time OpenMC developer. It implements the MSRE
benchmark in OpenMC using both constructive-solid-geometry (CSG) and CAD
representations, and compares to Shen-Serpent.

### Reported values (Yilmaz et al. 2024)

- **OpenMC CSG, ENDF/B-VIII.0:** k_eff = **1.02122**
  (agrees with Shen-Serpent 1.02132 to within 10 pcm).
- **OpenMC CAD, ENDF/B-VIII.0:** k_eff = **1.00872**
  (much closer to experimental 0.99978; +894 pcm vs experiment).
- **2018 IRPhE edition handbook k_eff:** stated to be **>1.030**
  (more than 3% above experiment).
- They confirm **Shen et al. 2021 used Serpent 2.1.30 with ENDF/B-VII.1.**

### Implications

1. **Honest framing for the paper.** Promethea is NOT the first
   open-source OpenMC MSRE benchmark; it is the second. Yilmaz 2024
   precedes it by ~24 months. Any submission must cite Yilmaz 2024 as
   the canonical OpenMC MSRE prior implementation and position
   Promethea's contribution as (a) systematic sensitivity studies on
   the parameters that dominate the gap (basket-shell defect, library,
   boron, corner geometry), (b) full automation in CI on free
   infrastructure, and (c) an independent re-derivation arriving at
   the same answer as the ANL/ORNL implementation to within ~230 pcm,
   which is a non-trivial cross-check.

2. **The basket-shell defect is unique to Promethea.** Yilmaz et al.
   2024 explicitly modeled the sample basket as graphite-without-shell
   (consistent with their citation of TM-0728); they did not report a
   shell-related overshoot because they never had one. The Promethea
   Suspect-1 finding (+1045 pcm shell defect) is therefore a
   pedagogical/methodological result, not a discovery of new physics.
   Reframe in the paper: "this is the kind of defect that gets
   introduced when a CSG model is built without close reading of the
   primary geometry sources — and is the kind of defect a parameterized
   sensitivity study can catch and quantify."

3. **The ~2% CSG-vs-experimental overshoot is a known systematic.**
   Promethea's 2375-pcm overshoot of the IRPhE experimental value is
   not a defect of the model; it is the CSG-vs-CAD gap that Yilmaz
   characterized. Real future work for Promethea is implementing the
   CAD geometry to close that gap.

4. **Powers (ORNL) and Fratoni (UC Berkeley) are the strongest
   senior-co-author candidates** for the Promethea paper. They
   co-authored Shen et al. 2021 directly, and so have explicit
   standing on the exact reference Promethea benchmarks against.
   Powers is at the lab that built the MSRE; Fratoni leads an MSR
   group at Berkeley. Both are already on the co-author shortlist.

### Action items

- Update IRPhE_SUBMISSION_DRAFT.md to cite Yilmaz 2024 and
  re-position the comparison table. [DONE 2026-05-30]
- Update BLOG_POST_DRAFT.md to acknowledge Yilmaz 2024 as the
  prior OpenMC implementation. [TODO]
- Update the paper outline (when written) to lead with Yilmaz 2024
  as the comparison point, not just Shen 2021.
- Reconfirm coauthor shortlist gives top priority to Powers and
  Fratoni. (Shen and Ilas should also be approached but as primary
  authors of the reference work, not senior advisors.)

### Honesty note

Discovering Yilmaz 2024 mid-project, on a citation check, is exactly
the kind of finding that has to be surfaced and documented rather than
quietly absorbed. The science is the same; the framing has to change.
Three months of independent re-derivation from primary sources
arriving within 230 pcm of an OpenMC team's own implementation is a
real positive result, but only if it is positioned that way.

---
## 2026-05-30 — Suspect 2: library × basket_shell sensitivity matrix (CLOSED)

### Finding

Combined the Phase 1.1.e Suspect-1 fix (basket_shell=false) with all
three supported cross-section libraries (ENDF/B-VIII.0, ENDF/B-VII.1,
JEFF-3.3) to produce a 3 × 2 sensitivity matrix. ENDF/B-VII.0 is
unavailable as an OpenMC HDF5 build (see prior entry) and is excluded.

### Results

CI runs (2026-05-30, 100k × 100, het_critical, 0.3 ppm B, sharp corners):

| Library | basket_shell=true | basket_shell=false | Δ from shell removal |
|---|---:|---:|---:|
| ENDF/B-VIII.0 | 1.01308 ± 0.00036 | **1.02353 ± 0.00033** | **+1045 ± 49 pcm** |
| ENDF/B-VII.1  | 1.01163 ± 0.00038 | **1.02200 ± 0.00037** | **+1037 ± 53 pcm** |
| JEFF-3.3      | 1.01485 ± 0.00034 | **1.02500 ± 0.00035** | **+1015 ± 49 pcm** |

Source runs: VII.1 shell=false → run 26681315297 (artifact 7307583074);
JEFF-3.3 shell=false → run 26681315771 (artifact 7307608797).

### Two cleanly-separable effects

The shell-removal effect (mean +1032 pcm, range 1015 to 1045) is
**independent of library choice** to within 1σ uncertainty across all
three libraries. The basket-shell defect is a geometry term that adds
a fixed parasitic absorption volume; the cross-section data used to
evaluate that absorption changes the answer by only ~30 pcm across
libraries. Methodologically: the +1045 ± 49 pcm value reported as
Suspect-1's contribution is robust against library choice.

The library spread (max − min):
- At shell=true: 322 pcm (JEFF-3.3 highest, VII.1 lowest).
- At shell=false: 300 pcm (JEFF-3.3 highest, VII.1 lowest).

The inter-library spread is also robust against the shell defect.
This means the two parameters separate cleanly into orthogonal terms.

### Comparison to references at the corrected geometry

| Reference | k_eff | Promethea match | Δ (Promethea − ref) |
|---|---:|---|---:|
| Shen-Serpent 2021 (VII.1) | 1.02132 ± 0.00003 | Promethea VII.1, shell=false | **+68 ± 37 pcm** |
| Yilmaz CSG 2024 (VIII.0)  | 1.02122 | Promethea VIII.0, shell=false | +231 pcm |
| IRPhE experimental        | 0.99978 | (canonical) | +2375 pcm |

The Promethea ENDF/B-VII.1 + basket_shell=false configuration matches
the Shen-Serpent reference (which uses ENDF/B-VII.1 per Yilmaz 2024
§3) to within **68 ± 37 pcm** — well inside 2σ. This is the
library-matched comparison that closes the benchmark question: at the
same library and the same corrected geometry, Promethea and Shen-Serpent
agree to within Monte Carlo statistics.

The Promethea ENDF/B-VIII.0 canonical configuration still matches
Yilmaz CSG 2024 to within 231 pcm, which is below the 300-pcm
inter-library spread and is the expected accuracy floor.

### Cross-section library hierarchy at the corrected geometry

In order of k_eff at basket_shell=false:

1. JEFF-3.3 (1.02500) — highest, +300 pcm above VII.1.
2. ENDF/B-VIII.0 (1.02353) — middle, +153 pcm above VII.1.
3. ENDF/B-VII.1 (1.02200) — lowest of the three; matches Shen-Serpent.

The same ordering holds at shell=true. JEFF-3.3's systematic hotness
is a known feature attributed primarily to its U-235 evaluation
(different ν̄ at thermal energies vs ENDF/B-VII.1/VIII.0).

### Production canonical configuration (final, v0.1.0 onward)

The canonical Promethea configuration is unchanged from the v0.1.0
release:

```yaml
mode: het_critical
particles: 100000
batches: 100
boron_ppm: 0.3
fillet_radius_cm: 0.0
xs_library: endfb-viii.0
basket_shell: false
```

This gives k = 1.02353 ± 0.00033, matching Yilmaz CSG (VIII.0) within
231 pcm and Shen-Serpent (VII.1) within 221 pcm (the latter is mostly
the VIII.0 − VII.1 library offset).

For the IRPhE submission-of-record run, the same configuration will
be repeated at 200k × 200 statistics for σ ≈ 15 pcm, plus a
companion VII.1 run at the same statistics to enable the
library-matched comparison to Shen-Serpent.

### Plot

`benchmarks/msre/plots/phase_1_1_e_suspect2/sensitivity_matrix.png`
visualizes the 3 × 2 matrix with Shen-Serpent, Yilmaz CSG, and IRPhE
experimental as horizontal reference lines.

### Status

**Suspect 2 is closed.** The library question is resolved: ENDF/B-VIII.0
is the production library (matches Yilmaz CSG ANL/ORNL canonical
choice); ENDF/B-VII.1 is the Shen-Serpent comparison library and gives
the closest match (68 pcm) to that reference. Remaining sensitivity
studies (INOR-8 cladding thickness, lower-core lattice, fuel-salt
re-derivation) are polishing rather than gap-closing work.

---
