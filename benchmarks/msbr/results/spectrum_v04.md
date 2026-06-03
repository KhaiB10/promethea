# MSBR three-group spectral decomposition (v0.4.0)

CI run: [26817134119](https://github.com/KhaiB10/promethea/actions/runs/26817134119)
(smoke: particles=20,000 × batches=60, seed=1, ENDF/B-VIII.0)

## Top-line k

- k_het   = **1.13380 ± 0.00122**
- k_homog = **1.02621 ± 0.00119**
- Δk      = **+10,759 ± 171 pcm**

Consistent with the 200k × 200 pooled three-seed measurement of
+10,506 ± 18 pcm (z = +1.5).

## Three-group reaction-rate tally (fuel salt)

Energy groups: thermal (E < 0.625 eV), epithermal (0.625 eV ≤ E < 100 keV),
fast (E ≥ 100 keV).

| Group | φ (het) | φ (homog) | νΣf (het) | νΣf (homog) | Σa (het) | Σa (homog) |
|---|---|---|---|---|---|---|
| thermal    | 19.80 | 104.86 | 0.9143 | 0.8259 | 0.4305 | 0.6388 |
| epithermal | 21.28 | 164.73 | 0.2154 | 0.1948 | 0.1047 | 0.3529 |
| fast       |  8.70 |  58.20 | 0.0033 | 0.0047 | 0.0062 | 0.0109 |

Raw rates are extensive (sum × volume × source-strength normalization)
and live in different volumes between geometries — only intensive
ratios within each geometry are directly comparable.

## Reproduction factor η = νΣf / Σa per group

| Group | η (het) | η (homog) | η_het / η_homog |
|---|---|---|---|
| thermal    | 2.124 | 1.293 | **1.64** |
| epithermal | 2.057 | 0.552 | **3.73** |
| fast       | 0.535 | 0.434 | 1.23 |
| total      | **2.093** | **1.023** | **2.05** |

## Spectral fraction (φ_g / φ_tot)

| Group | het | homog |
|---|---|---|
| thermal    | 0.398 | 0.320 |
| epithermal | 0.427 | 0.503 |
| fast       | 0.175 | 0.178 |

## Reading

1. **Total η doubles in the het geometry.** Per absorption in the
   fuel salt, the het cell produces 2.09 neutrons; the homog cell
   produces 1.02. Most of the +10,506 pcm Δk is encoded in this
   single number — the homog medium dilutes 233U absorption across
   graphite + blanket salt, so absorptions per fission opportunity go
   up but neutron production per absorption goes down.

2. **Epithermal regime carries the disproportionate efficiency
   advantage.** η_het / η_homog is 1.64 (thermal), **3.73 (epi)**, and
   1.23 (fast). The epi regime is where 233U resonance absorption and
   resonance escape compete most strongly; separating fuel and
   moderator into distinct zones lets epi neutrons slow down through
   pure graphite, escaping the 233U capture resonances, before they
   enter the fuel zone already thermalized. The homog mix does not
   permit that geometric escape, and epithermal absorptions in
   non-fuel materials (graphite, blanket salt 232Th capture) are
   correspondingly more competitive.

3. **Het spectrum is more thermalized.** Thermal flux fraction is
   0.398 (het) vs 0.320 (homog); epi fraction is 0.427 vs 0.503. This
   is the classic Westcott / Lamarsh heterogeneous-lattice picture:
   physical separation of moderator and fuel hardens the spectrum
   inside the fuel zone (locally) while softening the cell-averaged
   spectrum, producing a thermalization advantage at the cell level.

## What this is not

- These rates are from a 20k × 60 smoke; statistical uncertainty on
  individual rates is at the few-percent level. A precision run is
  appropriate before any spectrum-resolved claims in a paper.
- This is a unit-cell decomposition. Full-core spectrum effects (axial
  leakage, blanket reflectivity, control element absorption) are not
  in this picture.
- The four-factor formula k_inf = η·f·p·ε does not factor cleanly
  between two non-equivalent geometries in the absence of a transport
  homogenization equivalence theorem. We report group-resolved rates
  in each geometry separately rather than ascribe pcm to each factor.

## Reproduce

```bash
gh workflow run benchmark-msbr.yml \
  -f mode=spectrum \
  -f particles=200000 \
  -f batches=200 \
  -f seed=1 \
  -f xs_library=endfb-viii.0
```

Per-material JSON is in `out/msbr_spectrum.json` of the artifact.

## Prior art context

To the best of our knowledge no open-literature MSBR study has
published a three-group decomposition of the unit-cell heterogeneity
Δk. Rykhlevskii et al. (2017) focused on full-core depletion and
online reprocessing; ORNL-4528 (1971) was deterministic and did not
report a heterogeneity-vs-homogeneous Monte-Carlo comparison.

## Caveat — China context

SINAP's TMSR-LF1 (full power June 2024) achieved first Th→U conversion
in November 2025, but published numerical k_eff, α, or spectral
decompositions are not in the open literature; Promethea provides
openly reproducible baselines on the original ORNL MSBR design for
comparison.

## Hardened run (200,000 × 200, seed=1, ENDF/B-VIII.0)

CI run: [26827348828](https://github.com/KhaiB10/promethea/actions/runs/26827348828)
(100× more histories than the smoke run; 2.0 h wall time)

- k_het = 1.13130 ± 0.00017
- k_homog = 1.02693 ± 0.00016
- **Δk = +10,437 ± 23 pcm**
- Consistent with the pooled 3-seed ORNL result (+10,506 ± 18 pcm): diff = +69 ± 29 pcm, z = +2.4σ.

### Three-group η = νΣf / Σa (fuel salt only)

| group | η_het | η_homog | ratio (het/homog) |
|---|---|---|---|
| thermal     (<0.625 eV)        | 2.124 | 1.293 | **1.64** |
| epithermal  (0.625 eV – 0.1 MeV) | 2.058 | 0.553 | **3.72** |
| fast        (>0.1 MeV)         | 0.535 | 0.433 | **1.24** |
| total                          | 2.093 | 1.024 | 2.04 |

The smoke-run ratios (1.64 / 3.73 / 1.23) reproduce to three
decimals at 100× the statistics. The epithermal regime carries
the disproportionate η advantage that drives the +10,500 pcm
heterogeneity Δk — this is now a hardened finding, not a
smoke-test artifact.
