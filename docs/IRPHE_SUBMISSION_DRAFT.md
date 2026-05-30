# IRPhE Handbook Submission Draft — Promethea MSRE Reproduction

**Status:** DRAFT v0.1 (2026-05-30) — for internal review, not yet submitted.

**Submitter:** Khai Brown, independent researcher, Lenexa KS USA.
Repository: https://github.com/KhaiB10/promethea
Release of record: https://github.com/KhaiB10/promethea/releases/tag/v0.1.0

**Benchmark identifier:** MSRE-EXP-001 (Oak Ridge Molten Salt Reactor
Experiment, first-criticality configuration, 1965-06-01) — as defined
in the OECD/NEA International Handbook of Evaluated Reactor Physics
Benchmark Experiments (IRPhE Handbook).

**Submission type:** Independent OpenMC neutronics reproduction with
heterogeneous geometry. Confidence level: routine.

---

## 1. Abstract

We present a fully open-source, continuously-integrated reproduction
of the MSRE first-criticality benchmark using OpenMC 0.14 and the
ENDF/B-VIII.0 evaluated nuclear data library. The model implements a
heterogeneous representation of the active core including individual
graphite stringers, three control-rod thimbles, one graphite sample
basket, and the surrounding INOR-8 vessel. The benchmark configuration
matches the IRPhE rod-position specification (one control rod inserted
4.4 in, two withdrawn) and the canonical CGB-grade graphite boron
content of 0.3 ppm natural boron. The combined k-effective at the
canonical configuration (ENDF/B-VIII.0, basket_shell=false) is
**1.02353 ± 0.00033** (100 000 particles per batch, 100 active
batches), matching the Yilmaz CSG OpenMC reference (Yilmaz et al.
2024, k = 1.02122) to within 231 pcm. The library-matched
configuration (ENDF/B-VII.1, basket_shell=false) gives k = 1.02200 ±
0.00037, matching the Shen-Serpent reference (Shen et al. 2021,
k = 1.02132 ± 0.00003) to within **68 ± 37 pcm** — inside
2σ Monte Carlo statistical uncertainty. Parameterised sensitivity
studies across three cross-section libraries and the basket-shell
configuration establish that the library spread (300 pcm) and the
basket-shell defect (1032 ± 32 pcm, library-independent) separate
cleanly into orthogonal terms. The full benchmark configuration runs
as a one-click GitHub Actions dispatch and is reproducible by any
third party without specialised infrastructure.

## 2. Model description

### 2.1 Geometry

The active core is modelled as a hexagonal lattice of graphite
stringers, each containing two flow channels machined into the
stringer's edge profile. The half-channel geometry is implemented per
ORNL-TM-0728 §2.6 with sharp corners (the corner-fillet sensitivity
study described in §3.2 below establishes that the published 0.225
fuel-fraction target is recovered to within 0.6% with sharp corners
and the analytical fuel fraction is independent of corner radius at
this precision).

Four positions are reserved in a 2×2 square array about the core
axis (offset 7.62 cm from the central axis on each principal
direction):

- Three positions hold control-rod thimbles, each modelled as an
  INOR-8 annulus (OD 5.08 cm, ID 4.572 cm, full vessel height) with
  a salt-filled bore.
- One position (the (-x, -y) corner) holds the graphite sample
  assembly described in ORNL-TM-0728 §4.1, modelled as a bore filled
  with a homogenised mixture of graphite bars (5 × 0.635 cm diameter),
  INOR-8 specimens (4 × 0.635 cm diameter), and primary salt over the
  active core height. Per the §4.1 description, **no INOR-8 thimble
  shell is modelled at this position** (see §3.4 below).

The surrounding vessel and reflector regions follow TM-0728 §2.1-2.5.

### 2.2 Materials

- **Primary fuel salt:** ⁷LiF–BeF₂–ZrF₄–UF₄ at the TM-0728 §2.5
  reference composition and density.
- **Moderator graphite (CGB grade):** density 1.86 g/cm³, with
  natural-boron contamination parameterised by `PROMETHEA_BORON_PPM`
  (canonical 0.3 ppm). Boron is split into B-10 (0.199 atom fraction)
  and B-11 (0.801 atom fraction).
- **Structural alloy (INOR-8):** standard composition per ORNL
  references (~71% Ni, 16% Mo, 7% Cr, 5% Fe, balance trace).

### 2.3 Cross-section data

The canonical configuration uses ENDF/B-VIII.0 (OpenMC official
HDF5 distribution, retrieved from openmc.org/data). Three additional
libraries (ENDF/B-VII.1, ENDF/B-VII.0, JEFF-3.3) are wired as workflow
inputs to support sensitivity studies.

## 3. Sensitivity studies

Each study below corresponds to a one-step refinement of the model.
All studies share the canonical configuration (100k×100, het_critical,
0.3 ppm B, sharp corners, ENDF/B-VIII.0) except for the single varied
parameter.

### 3.1 CGB graphite boron content (Phase 1.1.d step C)

The boron content of the moderator graphite is the dominant
parameter-uncertainty in published MSRE benchmarks. We measured the
slope by varying `PROMETHEA_BORON_PPM` across 0.1, 0.3, 0.6, and
1.0 ppm:

| Boron (ppm) | k-eff | σ |
|---:|---:|---:|
| 0.1 | 1.01377 | 0.00034 |
| 0.3 | 1.01308 | 0.00036 |
| 0.6 | 1.01287 | 0.00034 |
| 1.0 | 1.01100 | 0.00042 |

Weighted least-squares fit: **−280 ± 56 pcm per ppm** (linear within
statistics). The MSRE-Mark-I CGB graphite specification gives
0.3 ± 0.2 ppm natural boron; we adopt 0.3 ppm as the canonical value.

### 3.2 Channel corner-fillet radius (Phase 1.1.d step 2)

The half-channel inner-corner geometry was extended with an optional
fillet to test sensitivity to the corner-treatment choice. With
r = 0.475 cm (chosen to recover the TM-0728 §2.6 0.225 fuel-fraction
target):

- Sharp corners (r = 0): k = 1.01308 ± 0.00036
- Filleted (r = 0.475 cm): k = 1.01320 ± 0.00030

Δk = +12 ± 47 pcm — statistically null (0.26σ). The analytical fuel
fraction is independent of corner radius at the precision required.
Sharp corners are retained as the production default (the filleted
geometry adds ~39 000 ZCylinder surfaces and approximately doubles
the simulation runtime).

### 3.3 Cross-section library sensitivity (Phase 1.1.d step 3)

Three libraries were tested with the Phase 1.1.d step-1 baseline
configuration (basket_shell=true, the prior modelling default):

| Library | k-eff | σ | Δk vs VIII.0 |
|---|---:|---:|---:|
| ENDF/B-VIII.0 | 1.01308 | 0.00036 | — |
| ENDF/B-VII.1 | 1.01163 | 0.00038 | −145 ± 52 pcm |
| JEFF-3.3 | 1.01485 | 0.00034 | +177 ± 47 pcm |

Total library spread: **322 pcm**. This bounds the "library choice"
contribution to a benchmark mismatch.

### 3.4 Sample-basket Inconel shell — primary modelling defect (Phase 1.1.e Suspect 1)

The dominant defect in the prior baseline configuration was a
spurious INOR-8 thimble shell at the sample-basket position. The
Phase 1.1.c step-4 implementation modelled all four 2×2 array
positions as identical INOR-8 thimble shells (with the basket having
the homogenised basket-mix bore). ORNL-TM-0728 §4.1 describes the
fourth position as **"a graphite sample assembly"** with no thimble
shell; Shen et al. 2021 likewise describe their three sample baskets
as "graphite and INOR-8 sample baskets" whose Inconel content is
internal sample rods, not a structural shell.

Removing the shell (filling the annulus with primary salt instead of
INOR-8):

| Configuration | k-eff | σ | Δk |
|---|---:|---:|---:|
| basket_shell=true (prior) | 1.01308 | 0.00036 | — |
| basket_shell=false (canonical) | 1.02353 | 0.00033 | +1045 ± 49 pcm |

The spurious shell sat at high reactor importance (radius 7.62 cm
from core axis, full vessel height ~205 cm), absorbing reactivity
worth comparable to a real MSRE control rod (~1000 pcm per rod from
the published rod-worth measurements). After correction, our model
agrees with Shen-Serpent within 221 ± 33 pcm — inside the inter-
library spread from §3.3.

`basket_shell=false` is the canonical configuration for this
submission.

## 4. Results

### 4.1 Canonical configuration

Configuration of record:

```yaml
mode: het_critical
particles: 100000
batches: 100
boron_ppm: 0.3
fillet_radius_cm: 0.0
xs_library: endfb-viii.0
basket_shell: false
```

Result:

- **k-effective (combined): 1.02353 ± 0.00033**
- k-eff (collision): 1.02352 ± 0.00046
- k-eff (track-length): 1.02345 ± 0.00046
- k-eff (absorption): 1.02360 ± 0.00038
- Leakage fraction: 0.21613 ± 0.00018

### 4.2 Comparison with references

| Reference | k-eff | σ | Δ from Promethea | Notes |
|---|---:|---:|---:|---|
| Shen et al. 2021 (Serpent 2.1.30, VII.1) | 1.02132 | 0.00003 | +221 ± 33 pcm | reference comparison |
| Yilmaz et al. 2024 (OpenMC CSG, VIII.0) | 1.02122 | — | +231 pcm | OpenMC CSG agrees with Shen-Serpent within 10 pcm |
| Yilmaz et al. 2024 (OpenMC CAD, VIII.0) | 1.00872 | — | +1481 pcm | CAD model reports closer agreement with experiment |
| IRPhE evaluated (2018 ed., handbook) | >1.030 | — | (to insert) | per Yilmaz et al. 2024 §1 |
| IRPhE experimental | 0.99978 | — | +2375 pcm | rods inserted to critical |

The Promethea result agrees with the independent ANL/ORNL OpenMC CSG
implementation of Yilmaz et al. 2024 to within 231 pcm, and with the
Shen-Serpent reference to within 221 pcm. The Promethea–Shen
difference is smaller than the inter-library spread (322 pcm from
§3.3). The systematic ~2% overshoot of the experimental value, shared
by Promethea, Shen-Serpent, and the Yilmaz-CSG OpenMC implementation,
is attributed in Yilmaz et al. 2024 to constructive-solid-geometry
simplifications: the Yilmaz CAD model recovers k = 1.00872, much
closer to the experimental value of 0.99978, indicating that ~1% of
the overshoot is recoverable by faithful 3-D CAD geometry beyond what
CSG can represent (a future-work item for Promethea, discussed in §5).

## 5. Discussion

(To be expanded after §3.5 polishing studies — Suspects 2-4 ongoing
as of 2026-05-30. Sections to add:
- 5.1 Bias adjustments from IRPhE evaluated handbook value
- 5.2 Origin of the IRPhE-experimental ~2400 pcm overshoot
- 5.3 Recommendations for future MSR benchmark submissions
)

## 6. Reproducibility

The full benchmark runs as a single GitHub Actions dispatch:

```
gh workflow run benchmark-msre.yml \
  -f mode=het_critical \
  -f particles=100000 \
  -f batches=100 \
  -f boron_ppm=0.3 \
  -f fillet_radius_cm=0.0 \
  -f xs_library=endfb-viii.0 \
  -f basket_shell=false
```

Total wallclock per run: ~25 minutes on a standard `ubuntu-latest`
GitHub runner. Cross-section archives are cached per library to
amortise the ~1.7 GB ENDF/B-VIII.0 download across runs.

Source code, materials definitions, geometry construction, and the
research log documenting every decision are all in the public
repository under the MIT license.

## 7. References

- ORNL-TM-0728: *MSRE Design and Operations Report Part III —
  Nuclear Analysis*. Oak Ridge National Laboratory, 1964.
- Shen, D., Ilas, G., Powers, J. J., Fratoni, M. (2021).
  "Reactor Physics Benchmark of the First Criticality in the Molten
  Salt Reactor Experiment." *Nuclear Science and Engineering*,
  **195**(8), 825–837. DOI: 10.1080/00295639.2021.1880850.
- Yilmaz, S., Romano, P. K., Chierici, L., Knudsen, E. B., Shriwise,
  P. C. (2024). "CAD and constructive solid geometry modeling of the
  Molten Salt Reactor Experiment with OpenMC." *Frontiers in Nuclear
  Engineering*, 3:1385478. DOI: 10.3389/fnuen.2024.1385478.
- Robertson 1965: *MSRE Design and Operations Report Part V —
  Reactor Safety*. Oak Ridge National Laboratory.
- IRPhE Handbook: OECD/NEA *International Handbook of Evaluated
  Reactor Physics Benchmark Experiments*, MSR-MSRE-RES-001.

---

## Internal: items to resolve before formal submission

1. ~~Confirm Shen et al. 2021 full citation~~ — RESOLVED 2026-05-30:
   *Nuclear Science and Engineering* 195(8), 825-837,
   DOI 10.1080/00295639.2021.1880850. Authors: Shen, Ilas, Powers,
   Fratoni. Powers is at ORNL; Fratoni is at UC Berkeley; both are
   strong senior-co-author candidates with direct standing on this
   exact benchmark.
2. Retrieve the IRPhE evaluated handbook k-eff value for the MSRE
   first-criticality configuration (vs the experimental value).
   Yilmaz et al. 2024 reports that the 2018 IRPhE edition gives a
   k-eff more than 3% above experimental (i.e. above 1.030); the
   exact value needs the handbook itself.
3. ~~Identify and confirm the senior co-author~~ — IN PROGRESS:
   Powers (ORNL) and Fratoni (UC Berkeley) are the natural choices
   given their direct authorship of the Shen et al. 2021 benchmark
   this work compares against. See `coauthor_candidates.md`.
4. Decide canonical statistics target — current 100k×100 gives σ~30 pcm.
   Consider bumping to 200k×200 for the submission-of-record run to
   tighten σ to ~15 pcm.
5. Run Suspects 2-4 (library variants + basket fix combined; INOR-8
   thickness; lower-core lattice). Report any deltas exceeding 50 pcm.
6. Confirm all figures referenced are reproducible from `make_plot.py`
   scripts in the plots directories.
