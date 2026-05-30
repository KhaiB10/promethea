# Paper Outline — Milestone 2

**Status:** DRAFT (2026-05-30). To be refined after Suspect-2 sweep results land and after senior co-author engagement.

**Working title:**
*"Promethea: an open, continuously-integrated OpenMC implementation of the MSRE first-criticality benchmark with parameterized sensitivity studies."*

**Target journal (in order of preference):**
1. *Annals of Nuclear Energy* (Elsevier) — broader audience, faster review, established home for MSR benchmark papers.
2. *Nuclear Science and Engineering* (ANS) — where Shen 2021 was published; arguably the most natural home for the comparison, but slower review.
3. *Frontiers in Nuclear Engineering* — where Yilmaz 2024 was published; open access, very fast review, would put the work alongside its direct prior art.

**Working contribution statement:**
> We present Promethea, an open-source OpenMC implementation of the MSRE first-criticality benchmark with full continuous-integration validation on free public infrastructure. Promethea reproduces the Shen-Serpent reference (Shen et al. 2021, NSE 195:825-837) to within 221 ± 33 pcm and the Yilmaz CSG OpenMC reference (Yilmaz et al. 2024, FNE 3:1385478) to within 231 pcm. We further report parameterized sensitivity studies on four parameters that the MSRE benchmark literature identifies as dominating model-to-model spread — cross-section library, graphite boron impurity, fuel-channel corner geometry, and the constructive-solid-geometry representation of the sample-basket position — quantifying each term independently. The largest single term (1045 ± 49 pcm) is the spurious-INOR-8-shell-at-the-sample-basket-position defect, demonstrating that parameterized sensitivity studies catch geometry-interpretation errors that bibliographic priors miss.

---

## 1. Introduction

- The MSRE in context: only fully-fueled MSR ever to reach criticality; canonical validation data for all modern MSR developers.
- The benchmark landscape: IRPhE handbook (MSR-MSRE-RES-001), Shen et al. 2021 (Serpent), Yilmaz et al. 2024 (OpenMC CSG + CAD).
- The gap: no openly-versioned, CI-validated, parameterized OpenMC implementation with explicit sensitivity studies — what Promethea adds.
- Roadmap of the paper.

## 2. Background

### 2.1 The MSRE
- Brief design summary (graphite-moderated, ⁷LiF-BeF₂-ZrF₄-UF₄ salt, INOR-8 vessel, 1965-1969 operations).
- The first-criticality configuration: one rod at 4.4 in insertion, two rods withdrawn, 911 K isothermal salt temperature, U-235 enriched fuel.

### 2.2 Prior open benchmark work
- IRPhE handbook evaluation summary (without paywalled detail).
- Shen et al. 2021: Serpent 2.1.30 + ENDF/B-VII.1; k = 1.02132 ± 0.00003 in the rods-withdrawn configuration.
- Yilmaz et al. 2024: OpenMC CSG (k = 1.02122, ~10 pcm from Serpent) and CAD (k = 1.00872, ~894 pcm above experiment).
- The CSG-to-CAD reduction of ~1250 pcm reported by Yilmaz characterizes the "irreducible CSG bias" inherent to flat-faceted approximations of curved hardware.

## 3. Model description

### 3.1 Geometry — heterogeneous CSG
- Hex stringer lattice, two-channel-per-edge geometry per TM-730 §2.6.
- Four thimble positions: three rod thimbles (INOR-8 annulus), one graphite sample assembly (no INOR-8 shell — §3.4 below).
- Reflector, vessel, lower head, upper plenum.

### 3.2 Materials
- Fuel salt composition with ⁷Li enrichment, U-235 enrichment, density at 911 K.
- CGB-grade graphite (1.86 g/cm³) with parameterized natural-boron impurity.
- INOR-8 composition.

### 3.3 Cross-section data and code stack
- OpenMC 0.14 + ENDF/B-VIII.0 (default); VII.1 and JEFF-3.3 supported for sensitivity work.
- Docker image with pinned OpenMC version.
- GitHub Actions workflow for one-click reproduction.

### 3.4 The sample-basket position
- Direct quotation from TM-730 §4.1.
- Distinction between "INOR-8 in the basket" (sample rods inside the bore) and "INOR-8 shell around the basket" (a structural thimble that the Promethea v0 model erroneously added).
- This is the single largest defect we found and the discussion in §6 is anchored on it.

## 4. Method — parameterized sensitivity studies

- The four parameters: `xs_library`, `boron_ppm`, `fillet_radius_cm`, `basket_shell`.
- Reproducibility: each parameter is exposed as a GitHub Actions input; concurrency-group key includes every parameter so parallel sweeps don't clobber each other.
- Stop-criterion: ~30 pcm σ at 100k × 100 particles × batches; submission-of-record run at 200k × 200 (σ ~15 pcm).

## 5. Results

### 5.1 Canonical configuration
- k_eff = 1.02353 ± 0.00033 at basket_shell=false, boron=0.3 ppm, sharp corners, VIII.0.

### 5.2 Sensitivity matrix
- Library sweep (VIII.0 / VII.1 / JEFF-3.3) at basket_shell=false.
- Library sweep at basket_shell=true (the v0 erroneous configuration) for contrast.
- 2×3 = 6-point sensitivity matrix.
- Boron sweep (0.1 / 0.3 / 1.0 ppm) at canonical configuration.
- Corner-fillet sweep (0.0 / 0.475 cm) — null result, fuel-fraction conservation.

### 5.3 Comparison to references
- Table: Promethea vs Shen-Serpent vs Yilmaz CSG vs Yilmaz CAD vs IRPhE experimental.

### 5.4 Sensitivity-of-bias decomposition
- Stacked-bar plot of pcm contributions to the total CSG-vs-experimental bias.

## 6. Discussion

### 6.1 The basket-shell defect as a methodology lesson
- Why bibliographic priors (boron, library, corners) pointed us at the wrong things.
- Why a parameterized sensitivity workflow catches geometry-interpretation defects that close reading of a paper does not.
- The control-rod-worth dimensional check (~1045 pcm consistent with one MSRE rod's worth).

### 6.2 The CSG-vs-CAD residual
- Yilmaz CAD (1.00872) vs Promethea CSG (1.02353) → ~1.5% residual is approximately the CSG-curvature-flattening bias.
- Implication: any future Promethea work that wants to close the experimental gap further must go CAD (DAGMC route — Shriwise expertise).

### 6.3 Library spread
- 322 pcm spread across three libraries at the corrected geometry: characterizes the "library uncertainty floor" any MSR-relevant benchmark must accept.
- VII.1 vs VIII.0: ~145 pcm; VIII.0 vs JEFF-3.3: ~177 pcm.

### 6.4 Open source, continuous integration, and benchmark trust
- A reactor-physics benchmark whose every commit, every input file, every cross-section URL, and every CI run-log is publicly inspectable is a different kind of trustworthy than a closed-source published value.
- Cost-of-reproduction argument: anyone with a GitHub account can rerun the canonical configuration on free CI in ~25 minutes.

## 7. Conclusions

- Promethea agrees with both Shen-Serpent (Δ = 221 pcm) and Yilmaz-CSG (Δ = 231 pcm) within the cross-section-library spread.
- The dominant model-to-model bias term (~1045 pcm) is a geometry-interpretation defect that parameterized sensitivity studies catch directly.
- The remaining CSG-vs-experiment residual is consistent with the CSG-vs-CAD systematic characterized by Yilmaz et al.

## Acknowledgements

- Funding: independent / self-funded.
- AI pair-programming: large language models were used for code-review and literature-synthesis assistance; all model outputs were checked against primary sources before commitment.
- Computational resources: GitHub Actions free tier.
- Discussions: (senior co-author + any informal reviewers).

## Author contributions

- KB: Conceptualization; methodology; software (Promethea repository, all code); investigation; visualization; writing — original draft.
- (Senior co-author): Methodology; validation; writing — review and editing.

## Data and code availability

- All code: https://github.com/KhaiB10/promethea (MIT license).
- Release of record: github.com/KhaiB10/promethea/releases/tag/v1.0.0 (paper-of-record tag, to be created at submission).
- Reproduction instructions: §3.3 above.
- Cross-section libraries: openmc.org/official-data-libraries (third-party, see scripts/fetch_xs.sh for canonical URLs).

## References (key citations)

1. Shen, D., Ilas, G., Powers, J. J., Fratoni, M. (2021). NSE 195(8):825-837. DOI:10.1080/00295639.2021.1880850.
2. Yilmaz, S., Romano, P. K., Chierici, L., Knudsen, E. B., Shriwise, P. C. (2024). Frontiers in Nuclear Engineering 3:1385478. DOI:10.3389/fnuen.2024.1385478.
3. Haubenreich, P. N., Engel, J. R., Prince, B. E., Claiborne, H. C. (1964). ORNL-TM-730: MSRE Design and Operations Report Part III — Nuclear Analysis. Oak Ridge National Laboratory, issued 3 February 1964. https://www.osti.gov/biblio/4114686
4. Robertson, R. C. (1964). ORNL-TM-728: MSRE Design and Operations Report Part I — Description of Reactor Design. Oak Ridge National Laboratory.
5. Beall, S. E. (1964). ORNL-TM-732: MSRE Design and Operations Report Part V — Safety Analysis. Oak Ridge National Laboratory.
6. OECD/NEA IRPhE Handbook: MSR-MSRE-RES-001.
7. Romano, P. K. et al. (2015). OpenMC: A state-of-the-art Monte Carlo code for research and development. Annals of Nuclear Energy 82:90-97.
8. Leppänen, J. (2015). The Serpent Monte Carlo code. Annals of Nuclear Energy 82:142-150.

---

## Submission strategy

### Phase 1 (next 4-6 weeks)
- Lock canonical results at 200k × 200 stats (σ ~15 pcm).
- Reach out to Paul Romano (Argonne) as primary senior-co-author candidate. Framing: "I built an independent CI-validated OpenMC MSRE implementation that agrees with your Frontiers 2024 CSG result to within 231 pcm; would you consider a brief review and possible co-authorship on an Annals of Nuclear Energy submission?"
- Pre-print on arXiv concurrently with the submission.

### Phase 2 (after first author response)
- If Romano declines but offers a referral: take the referral.
- If Romano accepts: incorporate his feedback before submission. He may suggest restructuring or additional comparisons.
- If Romano does not respond within 3 weeks: approach Chvála (UTK) as second-line non-conflicted senior co-author.

### Phase 3 (manuscript polish)
- Have the paper draft reviewed by at least one Promethea-external reader (HN blog post helps surface candidates).
- Submit.

---

*Outline status: scaffold complete. Needs Suspect-2 results and at least one senior-co-author engagement before becoming a full Methods Section 1 draft.*
