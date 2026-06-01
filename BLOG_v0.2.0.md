# Promethea v0.2.0 — Open MSRE OpenMC benchmark closes the 1,045 pcm gap

I rebuilt the Molten Salt Reactor Experiment (MSRE, ORNL, 1965)
criticality benchmark from primary sources in OpenMC, an open-source
Monte Carlo neutron transport code. v0.2.0 (200k particles × 200
batches per run) reports:

- **ENDF/B-VIII.0 canonical:** k = 1.02364 ± 0.00016
- **ENDF/B-VII.1 library-matched:** k = 1.02202 ± 0.00019
- **Gap vs Shen-Serpent 2021 (same library):** +70 ± 39 pcm (2σ)
- **Gap vs Yilmaz CSG OpenMC 2024:** +242 pcm

The library-matched configuration agrees with the most recent
published Serpent benchmark (Shen et al. 2021) inside the 2-sigma
Monte Carlo statistical band.

## What got it there

The dominant defect that closed the gap was not the cross-section
library, not the boron content, and not corner geometry — all of
which the literature flags as the usual suspects. It was a single
spurious INOR-8 shell that an earlier version of the model placed
around the graphite sample-basket position. Removing it recovered
**+1,045 pcm** — about the worth of a real MSRE control rod — and
closed the gap.

The v0.2.0 audit also surfaced ~137 instances of "ORNL-TM-0728"
(typo for ORNL-TM-730, Haubenreich/Engel/Prince/Claiborne 1964)
across the repository and a direct primary-source endorsement of the
graphite-sample-assembly interpretation: TM-730 §4.2.1 states *"the
effect of the graphite sample holder was neglected in these
preliminary calculations."*

## Reproducing it

The whole thing runs on the free GitHub Actions ubuntu-latest
runner. From a clean clone:

```bash
gh workflow run benchmark-msre.yml -f mode=het_critical \
   -f particles=200000 -f batches=200 -f boron_ppm=0.3 \
   -f fillet_radius_cm=0.0 -f xs_library=endfb-viii.0 \
   -f basket_shell=false
```

Or locally with Docker — see the [release notes](https://github.com/KhaiB10/promethea/releases/tag/v0.2.0).

## What's next

- **v0.3.0** (Q2 2026, in progress): rounded-corner sensitivity
  (recovers the as-built TM-730 §2 fuel fraction f = 0.225) +
  multi-seed statistical envelope.
- **v0.4.0** (Q3/Q4 2026, scoping): the first public, CI-validated,
  two-fluid Molten-Salt Breeder Reactor neutronics model, validated
  against ORNL-4528 (Robertson/Briggs/Smith/Bettis 1968). Primary
  anchors: BR = 1.06, η(233U) = 2.225, α_overall = −4.34×10⁻⁵ /°K
  @ 900K. Scope is BOL k-eff + breeding ratio only.

## Asks of the community

1. **Pull the repo and check the model.** If you find an error,
   please open an issue. The whole point is that we get to a better
   answer in public.
2. **If you have prior two-fluid MSBR neutronics inputs** (UTK,
   Argonne, ORNL — Singh/Chvála 2017+2018, Feng/Cao/Davidson/Betzler
   2021, etc.), I would love to coordinate.
3. **If you are working on the IRPhE submission** for the MSRE
   benchmark and would value an OpenMC cross-check, the draft is at
   `docs/IRPHE_SUBMISSION_DRAFT.md` in the repo.

Full dated research log: [`RESEARCH_LOG.md`](https://github.com/KhaiB10/promethea/blob/main/RESEARCH_LOG.md).
Repo: [github.com/KhaiB10/promethea](https://github.com/KhaiB10/promethea).
License: MIT.

— [@KhaiB10](https://github.com/KhaiB10)
