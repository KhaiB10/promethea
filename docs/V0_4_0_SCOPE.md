# Promethea v0.4.0 — Scope Decision

**Status:** drafted 2026-05-31, post-v0.2.0 tag and v0.3.0 plan
**Target window:** 2026-Q3 (after v0.3.0 closes the rounded-corner sensitivity and multi-seed envelope work)

---

## Why this document exists

The v0.2.0 release defines Promethea's contribution against the current
literature landscape: an open, CI-validated, parameterized OpenMC
CSG reproduction of the MSRE first-criticality benchmark. The v0.3.0
plan closes the two known statistical/geometric defects that v0.2.0
admits in its Known Limits section. After v0.3.0 ships, the project
is methodologically complete as a "CSG reproducibility benchmark."

To stay relevant for Milestone 2 (peer-reviewed paper) and Milestone
3 (ARE generalization), v0.4.0 needs to **add a new capability** that
moves Promethea forward against the comparables. Two candidates are
on the table, identified during the 2026-05-31 landscape audit
(`session 2026-05-31`).

Pick one. Both are valuable. They are not parallel-executable on a
single-developer budget.

---

## Option 1 — TSUNAMI-style S/U analysis on top of the sensitivity matrix

### What it adds

The v0.2.0 sensitivity matrix sweeps four parameters
(`xs_library`, `boron_ppm`, `fillet_radius_cm`, `basket_shell`) and
reports Δk for each cell. A TSUNAMI-style **sensitivity/uncertainty
(S/U) analysis** turns those Δk values into a covariance-propagated
uncertainty budget — first-order sensitivity coefficients
(Δk/Δσ × σ_covariance) integrated against the ENDF/B-VIII.0
covariance matrix, then summed across nuclide-reaction pairs to give
a total uncertainty estimate on k-effective from cross-section data
alone.

This is what Bostelmann & Skutnik 2022 (*Nuclear Technology*) did
with SCALE/Shift/TSUNAMI for the MSRE benchmark. It is the formal
sensitivity machinery used in the IRPhEP Handbook evaluations
themselves. Promethea v0.4.0 doing this with **OpenMC** instead of
SCALE puts it in a strictly different methodological category than
the openmsr/msre community fork (no S/U), the Yilmaz 2024 paper
(geometry-only comparison), and the Chierici 2025 Copenhagen Atomics
paper (depletion + isotopics, no S/U headline).

### How OpenMC enables this

OpenMC has native sensitivity-tally support through the `Tally` API
with `sensitivities` keyword and the `derivative` filter. There are
two paths:

- **GPT-Free** (Generalized Perturbation Theory, no adjoint): native
  to OpenMC 0.13+, computes first-order sensitivities of any tally
  to nuclide cross-sections via track-length estimators. No SCALE,
  no Shift, no adjoint solve required.
- **MGXS pre-processing**: dump multi-group cross-sections, post-
  process them through scipy/numpy against a downloaded ENDF/B-VIII.0
  covariance file (NJOY-generated or downloaded from NNDC).

The GPT-Free path is the cleaner OpenMC-idiomatic approach. Path
length per run is similar to existing canonical runs (sensitivity
tallies add ~10-20% wall time). Cost: ~1.5 hr per S/U run on the
free runner.

### Estimated effort

| Task | Estimate |
|---|---|
| Add `sensitivities=['total', 'capture', 'fission', 'nu-fission']` to canonical model | 1 day |
| Add post-processing script that reads sensitivity tallies and propagates against covariance | 2-3 days |
| Download + integrate the ENDF/B-VIII.0 covariance file | 1 day (NNDC has these; some NJOY work may be needed) |
| Validation against Bostelmann & Skutnik 2022 published uncertainty values | 2-3 days |
| Writeup as new paper §4.5 + figure | 1-2 days |
| **Total** | **~2 weeks of focused work** |

### Risk

- **Moderate.** The OpenMC sensitivity-tally interface works but is
  used less frequently than core neutronics tallies. Documentation
  is good but not exhaustive. There is a risk of spending a week on
  edge cases.
- **Covariance data pedigree.** The ENDF/B-VIII.0 covariance file
  has known gaps for some nuclides (especially fluorine reactions
  important for MSR salt physics). Bostelmann & Skutnik 2022 hit this
  and noted it; Promethea would need to replicate their treatment or
  document the gap.
- **Low novelty risk.** Bostelmann already did this for MSRE. The
  novelty here is "doing it open-source in OpenMC with full CI";
  that is a real but smaller delta than CAD migration.

### Paper positioning

- New §4.5 in the *Annals of Nuclear Energy* paper:
  "Cross-section uncertainty contribution to k-effective via OpenMC
  generalized perturbation theory."
- Adds ~1500 words and one figure (uncertainty pie chart by
  nuclide-reaction).
- Strengthens the methodology section against referee criticism that
  the +70 ± 39 pcm headline doesn't account for cross-section
  uncertainty (which is typically ~300-500 pcm for this benchmark).
- Romano is a natural reviewer / co-author for this; Bostelmann &
  Skutnik are conflicted-but-citeable.

---

## Option 2 — CAD migration to close the experimental gap

### What it adds

The v0.2.0 CSG geometry leaves a ~2400 pcm gap to the IRPhE
experimental value. Yilmaz et al. 2024 demonstrated that CAD
geometry closes ~1500 pcm of that (their CAD result is k=1.00872 vs
experimental 0.99978, a residual ~900 pcm gap which is the
library-bias floor). Promethea v0.4.0 closing the same gap would put
the project at the **same geometric fidelity as Yilmaz CAD, but with
full CI reproducibility on free runners** — a genuinely new capability
that no public OpenMC MSRE model has.

The path is well-trodden: import the openmsr/msre CAD model
(GPLv3, MIT-compatible-with-attribution per `GPLv3 § 7(a)`) through
Knudsen's CAD_to_OpenMC tool (JOSS 2025), and re-run the canonical
configuration on the meshed geometry.

### How CAD_to_OpenMC enables this

CAD_to_OpenMC is a pip-installable Python package
(`pip install --pre cad-to-openmc`) that converts STEP files to DAGMC
HDF5 meshes that OpenMC can run directly. The openmsr/msre repo
already provides the MSRE STEP files. The conversion produces a
DAGMC `.h5m` geometry file that becomes the runtime geometry instead
of the existing CSG `Geometry` object.

The remaining work is:
- Map openmsr/msre's material assignments (named by part prefix) to
  Promethea's material definitions in `materials.py`.
- Tune the CAD_to_OpenMC mesh refinement to balance fidelity vs
  runtime.
- Confirm that the DAGMC mesh runs reproducibly on the CI runner
  (the .h5m file may be too large for CI storage; would need a
  fetch-on-demand step similar to `scripts/fetch_xs.sh`).
- Validate against Yilmaz CAD k=1.00872 ± their σ.

### Estimated effort

| Task | Estimate |
|---|---|
| Set up CAD_to_OpenMC + DAGMC dependencies in the Docker image | 2 days |
| Import openmsr/msre STEP files + map materials | 3-4 days |
| First successful CAD run (any statistics) + debug geometry artifacts | 3-5 days (CAD-to-mesh debugging is unpredictable) |
| Tune mesh refinement to match Yilmaz CAD result within reasonable σ | 3-5 days |
| Re-build the CI workflow to handle a CAD path (mesh file fetch, longer wall time) | 2 days |
| Validation + writeup as new paper §4.6 / §5 | 1 week |
| **Total** | **~4-6 weeks of focused work** |

### Risk

- **Moderate-to-high.** CAD-to-mesh conversion has more failure
  modes than CSG (overlapping volumes, coincident surfaces, mesh
  refinement instabilities). The Yilmaz 2024 paper hit several of
  these and documented them; Promethea would likely hit similar
  issues.
- **CI runtime risk.** Yilmaz reports their CAD runs took ~5x longer
  than their CSG runs at equivalent statistics. A 200k × 200 CAD run
  could be ~7 hours on a free runner — at the edge of the per-job
  6-hour limit. May require dropping to 100k × 100 for the CI
  canonical and reserving 200k × 200 for self-hosted dispatch.
- **Dependency risk.** CAD_to_OpenMC is at v0.x and actively
  developed; pinning a working version is essential.
- **Higher novelty.** This is a genuinely new capability — no public
  OpenMC MSRE has full CI reproducibility on a CAD geometry. Strong
  contribution.

### Paper positioning

- New §4.6 / §5 in the paper: "CAD geometry migration via
  CAD_to_OpenMC: bridging the CSG-to-experimental gap."
- Reports a new headline number (target: within ~100 pcm of Yilmaz
  CAD).
- Strengthens the contribution against the most common referee
  objection ("the CSG over-prediction is well-known; what new does
  this add?") by demonstrating that the open Promethea pipeline can
  also close the CSG-vs-CAD gap.
- Knudsen (CAD_to_OpenMC author) becomes a natural co-author candidate.
- Possible second paper specifically on the CAD migration
  (e.g., *Frontiers in Nuclear Engineering* or *Nuclear Engineering
  and Design*).

---

## Recommendation

**Pick Option 1 (TSUNAMI/S-U) for v0.4.0.**

Reasoning:

1. **Lower effort** (~2 weeks vs ~4-6 weeks). v0.4.0 needs to ship
   before the *Annals of Nuclear Energy* submission window closes,
   not after.
2. **Higher methodology delta vs the existing comparables.** The S/U
   addition makes Promethea formally comparable to Bostelmann &
   Skutnik 2022 (SCALE-based), which no public OpenMC MSRE
   reproduction has matched. It directly answers the "what about
   cross-section uncertainty?" referee question that *will* come up.
3. **Sets up a natural Romano-aligned story.** OpenMC GPT-Free is
   Romano's tool; using it strengthens the case for Romano
   co-authorship.
4. **CAD migration becomes v0.5.0** — a strictly stronger story for
   a *follow-on* paper or a longer methods paper. Doing it after the
   first paper means it ships when the project has citation
   credibility, not before.

**Reserve Option 2 (CAD) for v0.5.0** with Knudsen as a target
co-author and an explicit framing as "geometric fidelity follow-on
to the v0.2-v0.4 CSG paper."

If Romano declines or doesn't respond and you pivot to Chierici as
primary co-author, the calculus changes — Chierici's group at
Copenhagen Atomics already does S/U work via EQL0D, so the
methodological delta would be smaller; the CAD migration becomes
more attractive because Knudsen (also at Copenhagen Atomics) is a
natural co-author. Revisit this decision if the Romano window
closes without response.

---

## Open questions

- **OpenMC version pin.** Both options require careful OpenMC
  version pinning. v0.15.x has the sensitivity-tally interface but
  some quirks in derivative filters. Confirm the canonical version
  before either option starts.
- **Covariance data source.** Bostelmann used SCALE's ENDF/B-VIII.0
  covariance; Promethea needs the same data in OpenMC-readable form.
  Path: NJOY processing of ENDF/B-VIII.0 covariance into multigroup
  matrices, or download from a pre-computed source (NDS, NNDC).
- **Whether to fold the multi-seed envelope (v0.3.0 Workstream B)
  into the S/U analysis as a "Monte Carlo statistical" uncertainty
  contribution.** Likely yes — the paper §4.5 should report total
  uncertainty = stat ⊕ cross-section ⊕ geometry, where geometry is
  bounded by the rounded-corner sensitivity (v0.3.0 Workstream A).

---

## Provenance

- v0.2.0 release notes (Known Limits section): `.local/V0_2_0_RELEASE_NOTES_FINAL.md`
- v0.3.0 plan: `docs/V0_3_0_PLAN.md`
- Landscape audit (2026-05-31): conversation context for this session
- Comparables: Bostelmann & Skutnik 2022 (SCALE, *Nucl. Tech.*),
  Yilmaz et al. 2024 (OpenMC CSG + CAD, *Frontiers Nucl. Eng.*),
  Chierici et al. 2025 (OpenMC + Serpent + EQL0D, *Frontiers Nucl. Eng.*).
- OpenMC sensitivity tallies: https://docs.openmc.org/en/stable/usersguide/tallies.html#sensitivity-tallies
- CAD_to_OpenMC: https://joss.theoj.org/papers/10.21105/joss.07710.pdf
- openmsr/msre CAD model: https://github.com/openmsr/msre
