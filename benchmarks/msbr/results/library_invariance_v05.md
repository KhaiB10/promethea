# MSBR heterogeneity Δk — three-library invariance (v0.5.0)

## Question

Does the +10,500 pcm heterogeneity Δk reported in v0.4.0 survive a
**third** independent international evaluation? VII.1 and VIII.0 are
both US (ENDF/B) and share substantial development heritage. JEFF-3.3
is OECD/NEA and the leading European evaluation.

## Result

CI run: [26862229474](https://github.com/KhaiB10/promethea/actions/runs/26862229474)
(het_vs_homog, 50,000 × 120, seed=1, ENDF/B → JEFF-3.3, ~27 min)

| library | k_het | k_homog | Δk (pcm) |
|---|---|---|---|
| ENDF/B-VII.1 (seed=1, v0.4.0) | 1.12943 ± 0.00041 | 1.02442 ± 0.00041 | +10,501 ± 58 |
| ENDF/B-VIII.0 (pooled 3 seeds, v0.4.0) | — | — | +10,506 ± 18 |
| **JEFF-3.3 (seed=1, v0.5.0)** | **1.13241 ± 0.00043** | **1.02666 ± 0.00037** | **+10,575 ± 57** |

### Pairwise consistency

| comparison | Δ (pcm) | z |
|---|---|---|
| JEFF-3.3 − ENDF/B-VIII.0 (pooled) | +69 ± 60 | +1.15 |
| JEFF-3.3 − ENDF/B-VII.1 | +74 ± 81 | +0.91 |
| ENDF/B-VII.1 − ENDF/B-VIII.0 (pooled) | −5 ± 61 | −0.09 |

### Three-library pool

Inverse-variance weighted pool: **Δk = +10,511 ± 16 pcm**, χ² = 1.37
on 2 degrees of freedom (consistent with a single underlying value).

## What this means

Two independent **evaluation families** — US ENDF/B and OECD JEFF —
agree on the MSBR heterogeneity Δk to within 1.2σ. The +10,500 pcm
finding is not a single-library artifact of ENDF/B-VIII.0; it is a
robust feature of the underlying physics that survives both:

- intra-family evaluation revision (VII.1 → VIII.0, no significant shift)
- inter-family evaluation switch (ENDF/B → JEFF, +70 pcm, within noise)

This is the strongest defense against the "your number is just a
library artifact" critique that a referee would raise.

## Plain language

There are two big "catalogs" of nuclear-reaction data the whole world
uses: ENDF/B (American) and JEFF (European). Both are built by
different teams, from largely overlapping but not identical
experiments. If a Monte Carlo result depends on a particular catalog,
it might be measuring the catalog instead of the physics.

We ran the same MSBR fuel-cell measurement with three different
catalogs (two ENDF/B versions plus JEFF-3.3). All three return the
same heterogeneity Δk to within statistical noise. The +10,500 pcm
heterogeneity advantage is a property of the geometry, not of a
particular catalog.
