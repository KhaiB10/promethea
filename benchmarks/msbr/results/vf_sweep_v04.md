# MSBR unit-cell volume-fraction sweep (v0.4.0)

CI run: [26816868814](https://github.com/KhaiB10/promethea/actions/runs/26816868814)
(50,000 particles × 120 batches per point, seed=1, ENDF/B-VIII.0, 125.6 min total)

## Grid

3×3 in (f_fuel, f_blanket) around the ORNL-1971 baseline:

- f_fuel ∈ {0.0733, 0.1222, 0.1832}  (×0.6, ×1.0, ×1.5 of ORNL)
- f_blanket ∈ {0.0320, 0.0640, 0.1152}  (×0.5, ×1.0, ×1.8 of ORNL)
- f_graphite = 1 − f_fuel − f_blanket
- Geometry shape (basket / shell radii) held fixed at ORNL values; only volume fractions varied.

## Full result table

| f_fuel | f_blanket | f_graphite | k_het | k_homog | Δk (pcm) |
|---|---|---|---|---|---|
| 0.0733 | 0.0320 | 0.8947 | 1.21776 ± 0.00036 | 1.15567 ± 0.00046 | +6,209 ± 59 |
| 0.0733 | 0.0640 | 0.8627 | 0.90698 ± 0.00036 | 0.81347 ± 0.00032 | +9,352 ± 48 |
| 0.0733 | 0.1152 | 0.8115 | 0.64532 ± 0.00032 | 0.54322 ± 0.00029 | +10,210 ± 43 |
| 0.1222 | 0.0320 | 0.8458 | 1.42398 ± 0.00045 | 1.35759 ± 0.00049 | +6,639 ± 66 |
| **0.1222** | **0.0640** | **0.8138** | **1.13167 ± 0.00042** | **1.02683 ± 0.00044** | **+10,484 ± 60**  (ORNL) |
| 0.1222 | 0.1152 | 0.7626 | 0.85489 ± 0.00035 | 0.73195 ± 0.00032 | +12,294 ± 47 |
| 0.1832 | 0.0320 | 0.7848 | 1.55419 ± 0.00047 | 1.48471 ± 0.00046 | +6,948 ± 65 |
| 0.1832 | 0.0640 | 0.7528 | 1.29109 ± 0.00043 | 1.17809 ± 0.00045 | +11,300 ± 62 |
| **0.1832** | **0.1152** | **0.7016** | **1.02200 ± 0.00045** | **0.88318 ± 0.00042** | **+13,882 ± 61**  (Δk max) |

## Δk maximum vs ORNL baseline

- ORNL: Δk = **+10,484 ± 60 pcm**
- Δk-max corner (f_fuel=0.183, f_blanket=0.115): Δk = **+13,882 ± 61 pcm**
- Offset: **+3,398 ± 86 pcm**
- **z-score: +39.7** (vastly more than 5σ)

The +10,506 pcm pooled VIII.0 measurement at the ORNL baseline
(three seeds, 200k × 200) is reproduced at this single-seed
50k × 120 grid-point at +10,484 ± 60 pcm. The grid Δk maximum
at the opposite corner exceeds it by 32%.

## Quadratic surface fit

Δk(f_fuel, f_blanket) = a + b·x + c·y + d·x² + e·y² + f·xy
fit residual RMS = 69 pcm (within statistical noise).

Analytic stationary point (concave-down: **maximum**):

- f_fuel = 0.3604, f_blanket = 0.1433
- Δk(fit) = **+16,030 pcm**

This fitted optimum lies **outside the sampled grid** and should be
treated as an extrapolation, not a measurement. A confirmation
run at the corner (and beyond) is the next step. The qualitative
direction — push f_fuel and f_blanket higher, push f_graphite lower —
is unambiguous from the grid alone.

## Reading

The unit-cell heterogeneity Δk is *strongly* dependent on volume
fractions, and the ORNL-1971 1971 design choice is decisively not the
unit-cell Δk optimum. Δk grows monotonically in both f_fuel (more
fissionable material) and f_blanket (more 232Th to "punish" the homog
geometry, where 232Th capture competes with fission everywhere). It
falls monotonically in f_graphite (the more moderator there is, the
more both geometries thermalize, narrowing the gap).

The four corners of the grid produce a 2.24× spread in Δk
(+6,209 to +13,882 pcm) with stable monotone behaviour. This is a
publishable optimization landscape on the original MSBR design.

## What this is NOT a claim of

Unit-cell Δk is **not** core reactivity. ORNL traded:

- **Reactivity vs. breeding ratio**: more blanket fraction in a finite
  reactor means more 232Th captures and a *higher* breeding ratio, but
  also bigger 233Pa inventory and slower reprocessing margin.
- **Reactivity vs. reactor period and reprocessing economics**: the
  ORNL 1971 design fixed reprocessing-cycle time at ~10 days; a
  high-blanket high-fuel geometry would change the salt inventory and
  the reprocessing cost basis materially.
- **k_het ≠ k_eff**: this is an infinite-medium unit cell. The
  high-Δk corner has k_het = 1.022, which would be sub-critical in a
  finite reactor with leakage. The ORNL baseline (k_het = 1.13) has
  the appropriate margin above 1 to survive leakage in the full core.

So the finding is *quantitative* (the unit-cell heterogeneity Δk
landscape has a maximum 3,398 pcm above the ORNL baseline at
z=+39.7σ), but the *normative* claim — that the corner is a better
reactor design — is **not** asserted.

## Reproduce

```bash
gh workflow run benchmark-msbr.yml \
  -f mode=vf_sweep \
  -f vf_grid=coarse \
  -f particles=50000 \
  -f batches=120 \
  -f seed=1 \
  -f xs_library=endfb-viii.0
```

CSV: `out/msbr_vf_sweep.csv` (artifact)
JSON: `out/msbr_vf_sweep.json` (artifact)
Analyzer: `scripts/analysis/vf_sweep.py`

## Prior art context

To our knowledge no open-literature MSBR study has previously
mapped the heterogeneity-Δk landscape across (f_fuel, f_blanket).
Rykhlevskii et al. (2017) studied online reprocessing in the
nominal geometry only; ORNL-4528 (1971) used deterministic
two-group methods and did not perform a Monte-Carlo unit-cell
sweep at all. SINAP's TMSR-LF1 has not published comparable
numerical sweeps.

## Δk-max corner reproduction (seed=2)

CI run: [26827238443](https://github.com/KhaiB10/promethea/actions/runs/26827238443)
(corner grid, 50,000 × 120, seed=2, ENDF/B-VIII.0, 11.6 min)

| seed | k_het | k_homog | Δk (pcm) |
|---|---|---|---|
| 1 | 1.02200 ± 0.00045 | 0.88318 ± 0.00042 | +13,882 ± 61 |
| 2 | 1.02069 ± 0.00039 | 0.88357 ± 0.00042 | +13,712 ± 58 |
| **pooled** | — | — | **+13,793 ± 42** |

Seed-to-seed difference: +170 ± 84 pcm (z = +2.0σ, within MC variation).
Pooled corner Δk = +13,793 ± 42 pcm.
Pooled corner − ORNL pooled (+10,506 ± 18) = **+3,287 ± 46 pcm (z = +71.9σ)**.

The Δk-max corner is reproduced across two independent seeds; the
+3,287 pcm offset from the ORNL baseline is not single-seed luck.

## Caveat — China context

China's TMSR-LF1 (Wuwei, 2 MWth, full power June 2024; first
Th→U conversion November 2025) achieved a practical demonstration
of MSR Th-U operation, but published quantitative volume-fraction
optimization data on any MSR design is not in the open literature.
Promethea fills the gap on the original ORNL MSBR design.
