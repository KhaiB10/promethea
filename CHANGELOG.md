# Promethea v0.5.0 — Cross-verification (library invariance + CE vs MG bias)

v0.5.0 closes two referee-grade questions left open by v0.4.0:

1. **Library invariance.** The +10,500 pcm heterogeneity Δk reported
   in v0.4.0 was measured under ENDF/B-VII.1 and VIII.0 (both US
   evaluations). v0.5.0 adds **JEFF-3.3** (OECD/NEA) and finds three-
   library agreement to within statistical noise.

   | library | Δk (pcm) |
   |---|---|
   | ENDF/B-VII.1 (v0.4.0)       | +10,501 ± 58 |
   | ENDF/B-VIII.0 (pooled 3 seeds, v0.4.0) | +10,506 ± 18 |
   | JEFF-3.3 (v0.5.0)            | +10,575 ± 57 |
   | **three-library pool**       | **+10,511 ± 16** (χ² = 1.37 / 2 dof) |

   The +10,500 pcm heterogeneity is library-invariant across two
   evaluation families. Library-artifact critique closed.

2. **CE vs MG bias.** Production reactor codes run multi-group with
   homogenized cross-sections. v0.5.0 builds an 8-group MGXS library
   from the CE flux on the heterogeneous cell and runs MG transport
   on the same geometry. Result at 200,000 × 200 statistics:

   - k_CE = 1.131300 ± 0.000168
   - k_MG = 1.134039 ± 0.000154
   - **Δ_MG = k_CE − k_MG = −274 ± 23 pcm (z = −12σ)**

   The standard industrial homogenized 8-group workflow systematically
   over-predicts k_inf by 274 pcm on the ORNL MSBR cell. Small versus
   core-level reactivity margins (≈0.2%), but resolved at z = 12 and
   non-zero. Likely traceable to the same epithermal heterogeneity
   physics that v0.4.0 identified — group-averaging cannot resolve
   the narrow 232Th / 233U resonance structure in the 0.625 eV – 0.1
   MeV window.

## Why the Serpent 2 cross-check is not in this release

Serpent 2 is distributed via RSICC and OECD/NEA Data Bank under
single-user, non-commercial, export-controlled licenses, and cannot
be redistributed in a public CI image. Same gating applies to MCNP6.
We pivoted to OpenMC self-verification (CE vs MG) — which production
reactor-physics shops also use for code verification — to keep the
entire result chain reproducible from a public GitHub Actions run.

## What audits passed before tag

- JEFF-3.3 run reproduced the heterogeneity Δk within 1σ of pooled VIII.0
- MG smoke (20k × 60) and MG production (200k × 200) mutually consistent (z = +1.3)
- Pooled stats arithmetic re-derived from raw k values, matches doc
- Three-library χ² = 1.37 / 2 dof verified

## What's open for v0.6.0+

- **16-group / 30-group MG runs** to characterize how Δ_MG scales with
  group count. Open question: does the bias collapse to <50 pcm at
  finer resolution, or does the homogenization itself leave residual?
- **Local Serpent 2 cross-check** if/when an RSICC license is granted.
- **Burnup / breeding ratio over time** (the BR(t) → 1.0 question that
  Rykhlevskii 2017 measured for the single-fluid simplified geometry).

---

# Promethea v0.4.0 — MSBR pivot, first measurements


## What's new

Promethea pivots from MSRE-only to a multi-reactor benchmark framework,
with the **Two-Fluid Molten Salt Breeder Reactor (MSBR)** as the second
benchmark. v0.4.0 ships three first-light measurements on the MSBR
fuel-cell geometry, all reproducible from public CI:

| Quantity | Value | σ | Status |
|----------|-------|---|--------|
| k_∞ heterogeneous, VIII.0, 900 K (seed=1) | 1.13132 | ±0.00039 | ✓ landed |
| k_∞ heterogeneous, VIII.0, 900 K (seed=2) | 1.13212 | ±0.00041 | ✓ landed |
| k_∞ homogenized, VIII.0, 900 K (seed=1)   | 1.02602 | ±0.00041 | ✓ landed |
| k_∞ homogenized, VIII.0, 900 K (seed=2)   | 1.02608 | ±0.00038 | ✓ landed |
| k_∞ heterogeneous, VIII.0, 900 K (seed=3, 200k×200) | 1.13175 | ±0.00015 | ✓ landed |
| k_∞ homogenized, VIII.0, 900 K (seed=3, 200k×200)   | 1.02684 | ±0.00013 | ✓ landed |
| **Δk_het/homog (pooled, 3 VIII.0 seeds)** | **+10,506 pcm** | **±18 pcm** | **✓ measured** |
| k(900 K) unit cell, VIII.0, 200k×220 | 1.13174 | ±0.00015 | ✓ landed |
| k(1200 K) unit cell, VIII.0, 200k×220 | 1.12977 | ±0.00015 | ✓ landed |
| **α_T unit cell, 900→1200 K, VIII.0** | **−5.79 × 10⁻⁶ /K** | **±6.2 × 10⁻⁷ /K** | **✓ resolved (z=9.3)** |
| **k_∞ VII.1 het (seed=1)** | **1.13208** | **±0.00040** | **✓ landed** |
| **k_∞ VII.1 homog (seed=1)** | **1.02707** | **±0.00041** | **✓ landed** |
| **Δk VII.1 (seed=1)** | **+10,501 pcm** | **±58 pcm** | **✓ landed** |
| **Δk library spread (VII.1 − VIII.0 pooled)** | **−5 pcm** | **±61 pcm** | **✓ consistent with zero** |
| **BR (unit cell, VIII.0, seed=1)** | **0.8426** | **±0.0006** | **✓ measured** |
| 232Th(n,γ) rate, VIII.0 | 4.262×10⁻¹ | ±2.2×10⁻⁴ | ✓ |
| 233U absorption rate, VIII.0 | 5.058×10⁻¹ | ±2.7×10⁻⁴ | ✓ |
| α(233U) capture/fission | 0.1124 | ±0.0008 | ✓ |

## Headline result

**The MSBR fuel-cell heterogeneity geometry contributes Δk = +10,506 ±
18 pcm to k_∞ versus the same materials volume-mixed at identical volume
fractions** (fuel 0.1222 / graphite 0.8138 / blanket 0.0640). ENDF/B-VIII.0,
900 K with S(α,β) interpolation, pooled over three seeds (50 000 × 120
for seeds 1 and 2, 200 000 × 200 for seed=3 precision lock). χ² of the
three-measurement pool is 3.81 over 2 dof — internally consistent.

**Second finding (cross-library robustness):** The Δk measurement repeated
at ENDF/B-VII.1 returns +10,501 ± 58 pcm — statistically consistent with
the pooled VIII.0 value (library spread −5 ± 61 pcm, z = −0.09). While
individual k_inf values shift by ~600 pcm between libraries (a known
result for thermal Th systems), **the heterogeneity Δk is library-invariant
to within ±60 pcm.** This is a stronger structural claim than the
magnitude alone.

**Third finding (temperature coefficient sign):** Two-point finite
difference on the heterogeneous unit cell yields α = −5.79 × 10⁻⁶ /K
(z = 9.3, resolved). Sign is negative — Doppler-dominated and safe.
Magnitude is ~10× smaller than the ORNL reactor-level value (−4.34 ×
10⁻⁵ /K), as expected for a reflective unit cell with no leakage or
salt-density feedback. Public Monte Carlo full-core values already
disagree by 3.7× (Rykhlevskii Serpent 2: −1.57 × 10⁻⁵; Park MCNP6:
−3.21 × 10⁻⁵; ORNL deterministic: −4.34 × 10⁻⁵), so the unit-cell
number is published as a reproducible reference point, not a
full-reactor result.

### Why this is candidate-novel

To our knowledge — based on searches of the OpenMC publication list,
the OpenMC Discourse MSBR thread, IAEA Th-fuel-cycle status documents,
ORNL holdings, and the Rykhlevskii ARFC MSBR bibliography — **no prior
open Monte Carlo paper reports the heterogeneity-vs-homogenization Δk
for the MSBR fuel cell at quantified statistical confidence.** The
qualitative result (het > homog in Th breeders) is textbook physics
(IAEA TE-1450 §4); the openly reproducible number is the contribution.

### Honest scope

- This is a **unit-cell k_∞** result, not a core-level reactivity penalty.
- **Cross-code verification** (Serpent / MCNP) not yet performed.
  Rykhlevskii et al. (2017) Trans. ANS 117:239 reports Serpent 2 unit
  cell k_inf at a similar but not identical geometry (13.2 vol% fuel
  vs. our 12.22 vol%); direct cross-code comparison is deferred to
  v0.5.0.
- The +10.6 % Δk magnitude is consistent with hand calculations of
  fuel dilution × loss of spatial self-shielding in an 81-vol% graphite
  cell, but cross-code agreement would harden the magnitude.

## Fourth finding (volume-fraction landscape)

A 3×3 unit-cell sweep over (f_fuel, f_blanket) shows the heterogeneity
Δk is **strongly geometry-dependent**, and the ORNL-1971 design choice
is decisively not the unit-cell Δk maximum:

- ORNL baseline grid point: Δk = +10,484 ± 60 pcm (matches the pooled
  het_vs_homog measurement at z = +0.4σ — independent cross-check).
- Δk-max corner (f_fuel=0.183, f_blanket=0.115): Δk = +13,793 ± 42 pcm
  (pooled over seeds 1 and 2).
- Offset above ORNL: **+3,287 ± 46 pcm (z = +71.9σ)**.

The Δk landscape is monotone in both f_fuel and f_blanket and falls
monotonically in f_graphite across the sampled grid. **This is not a
normative claim that the corner is a better reactor** — k_het at the
corner is 1.022 (no leakage margin), and the ORNL design balances
reactivity, breeding ratio, and reprocessing economics. The finding
is quantitative: the open-data heterogeneity-Δk landscape is now
mapped on the original MSBR fuel cell for the first time.

## Fifth finding (epithermal carries the Δk advantage)

Three-group spectrum decomposition (thermal <0.625 eV / epithermal
0.625 eV – 0.1 MeV / fast >0.1 MeV) on the heterogeneous vs homogenized
geometries returns an intra-geometry η = νΣf/Σa ratio of:

| group | η_het | η_homog | het/homog |
|---|---|---|---|
| thermal     | 2.124 | 1.293 | **1.64** |
| epithermal  | 2.058 | 0.553 | **3.72** |
| fast        | 0.535 | 0.433 | **1.24** |

Hardened at 200,000 × 200 batches; reproduces the 20k smoke values to
three decimals. **The epithermal regime carries the disproportionate
advantage** that drives the +10,500 pcm heterogeneity Δk — homogenizing
the geometry collapses η_epi from 2.06 to 0.55 (factor 3.7×), while
thermal η only drops 39% and fast η only drops 19%. The mechanism
is spatial self-shielding: in the heterogeneous geometry, fissile
nuclei in the fuel channel see an enriched epithermal flux because
resonance capture in graphite-region 232Th is geometrically removed
from them, whereas in the homogenized mixture every fissile nucleus
sits adjacent to fertile capture cross-sections.

## Pre-tag audit (all 9 audits passed)

Before tagging, every numerical result was independently recomputed
or reproduced:

1. Geometry math at all 9 vf_sweep grid points (fractions match to 6 decimals)
2. ORNL grid point matches pooled measurement (z = +0.4σ)
3. Δk-max corner reproduces across seed 1 and seed 2 (pooled +13,793 ± 42 pcm)
4. Spectrum η ratios hardened at 200,000 × 200 (1.64 / 3.72 / 1.24 reproduce)
5. Spectrum module: η is intensive, intra-geometry comparison is volume-normalization safe
6. Pooled 3-seed Δk arithmetic (+10,506.4 ± 17.9 pcm, χ² = 3.81 / 2 dof)
7. BR recomputed by hand from 232Th(n,γ) / 233U_abs (0.8426 ± 0.0006 exact)
8. α temperature coefficient sign verified negative, |z| = 9.3
9. ORNL volume fractions cross-checked vs ORNL-4528 / Rykhlevskii 2017:
   model represents the original **two-fluid** ORNL-4528 design
   (0.122 fuel + 0.064 blanket + 0.814 graphite), distinct from the
   later single-fluid Rykhlevskii simplification (0.132 fuel + 0.868
   graphite, no blanket annulus). Both are valid; the distinction is
   now explicit in the geometry docstring and release notes.

## What else is in v0.4.0

- **Homogenization scaffold** (`benchmarks/msbr/geometry_unit_cell_homog.py`):
  builds a single-region cell with volume-mixed fuel/graphite/blanket
  at identical volume fractions to the heterogeneous build. Mixing
  workaround applied for OpenMC's S(α,β) restriction.
- **Temperature sweep scaffold** (`benchmarks/msbr/run_temp_sweep.py`):
  two-point finite difference α = (1/k_ref)(Δk/ΔT) sharing seed and
  particles between the lo-T and hi-T eigenvalue calculations.
- **Breeding tally module** (`benchmarks/msbr/tallies.py`): material
  filter over 233U / 235U / Th232 / U234 / Pa233 with fission /
  absorption / (n,γ) scores and 4-group spectrum tallies. Writes
  `out/msbr_breeding.txt`.
- **Workflow modes**: `unit_cell`, `homog_cell`, `het_vs_homog`,
  `temp_sweep`, and the default `plot` mode for geometry visualization.
- **Disk-cleanup CI step** added so the runner survives the OpenMC
  ENDF/B-VIII.0 library extraction.

## v0.2.0 / v0.3.0 carry-forward (MSRE)

- MSRE canonical (VIII.0, 200k×200): k = 1.02364 ± 0.00016
- MSRE library-matched (VII.1, 200k×200): k = 1.02202 ± 0.00019
- MSRE 5-seed envelope: mean 1.02380, between-seed σ 42 pcm
- MSRE sensitivity matrix figure (sensitivity_matrix.png)

## Reproduce

```
# Headline Δk measurement (50k × 120, ~12 min):
gh workflow run benchmark-msbr.yml --repo KhaiB10/promethea --ref main \
  -f mode=het_vs_homog -f xs_library=endfb-viii.0 -f seed=1 \
  -f particles=50000 -f batches=120

# Temperature coefficient (200k × 220, ~50 min):
gh workflow run benchmark-msbr.yml --repo KhaiB10/promethea --ref main \
  -f mode=temp_sweep -f xs_library=endfb-viii.0 -f seed=1 \
  -f particles=200000 -f batches=220 \
  -f temp_lo_K=900 -f temp_hi_K=1200
```

## Acknowledgements / prior art

Rykhlevskii, Lindsay, Huff (2017) Serpent 2 MSBR unit cell and full-core
work (UIUC ARFC) is the closest related public Monte Carlo modeling of
the MSBR. Their geometry parameters are similar but not identical
(13.2 vol% fuel vs our 12.22 vol%, 908 K vs 900 K, ENDF/B-VII.0 vs
VIII.0). Their work focused on online reprocessing / depletion; this
work focuses on benchmark-quality static measurements with explicit
uncertainty quantification.

ORNL-4528 (1971) remains the historical anchor: reactor-level
α_overall = −4.34×10⁻⁵/K, BR = 1.06, η_233U = 2.225.

## Context: where this fits in 2026 thorium-MSR landscape

China's SINAP TMSR-LF1 at Wuwei (2 MWth, full power June 2024)
confirmed the first experimental thorium-to-uranium fuel conversion in
a running molten-salt reactor in November 2025 (CSIS analysis of
China's 15th Five-Year Plan; CAS announcements). SINAP's roadmap calls
for 10 MW commercial demonstrators by 2030, 100 MWth + closed Th-U
fuel cycle by 2040, TMSRs >=10% of Chinese grid by 2050. The actual
numerical k_eff / α / BR signatures of TMSR-LF1 are not openly
published.

The Western open-data side is thin: the only well-known open Monte
Carlo MSBR work is UIUC/ARFC (Rykhlevskii et al. 2017) using Serpent 2
focused on online reprocessing. Promethea v0.4.0 fills a specific gap:
**reproducible, CI-driven, library-pinned static k_inf / Δk / α / BR
benchmarks on the original ORNL MSBR fuel-cell geometry using a
completely open code (OpenMC) and open libraries (ENDF/B-VIII.0 and
VII.1).** Different reactor than TMSR-LF1, but same physics class
(thermal-spectrum graphite-moderated Th-MSR), and openly verifiable
in a way that the SINAP measurements cannot be.
