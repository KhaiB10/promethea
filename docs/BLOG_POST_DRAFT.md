# Closing a 1,045 pcm gap in a 1960s reactor benchmark, in public, from a laptop

## TL;DR

I rebuilt the Molten Salt Reactor Experiment (MSRE, ORNL, 1965)
criticality benchmark from primary sources in OpenMC, an open-source
Monte Carlo neutron transport code. After three months of iteration
in public on GitHub, the v0.2.0 release (200k particles × 200 batches
per run, May 2026) reports:

- **ENDF/B-VIII.0 canonical:** k = 1.02364 ± 0.00016
- **ENDF/B-VII.1 library-matched:** k = 1.02202 ± 0.00019
- **Gap vs Shen-Serpent 2021 (same library):** +70 ± 39 pcm (2σ)
- **Gap vs Yilmaz CSG OpenMC 2024:** +242 pcm

The library-matched configuration agrees with the most recent
published Serpent benchmark (Shen et al. 2021) inside the 2-sigma
Monte Carlo statistical band. The model is fully open and runs as a
one-click reproduction on free GitHub Actions infrastructure.

The dominant defect that got the project there was not boron content,
not the cross-section library, and not corner geometry — all of which
the literature flags as the usual suspects. It was a single spurious
INOR-8 shell that an earlier version of the model placed around the
graphite sample-basket position. Removing it recovered +1,045 pcm —
about the worth of a real MSRE control rod — and closed the gap.
Documentation, code, plots, and the full dated research log are all in
the open at
[github.com/KhaiB10/promethea](https://github.com/KhaiB10/promethea).

Secondary finding, surfaced during the v0.2.0 audit: the project's
primary-source citations had ~137 instances of "ORNL-TM-0728"
(typo for ORNL-TM-730, Haubenreich/Engel/Prince/Claiborne 1964). The
audit also surfaced a direct primary-source endorsement of the
graphite-sample-assembly interpretation: TM-730 §4.2.1 states
*"the effect of the graphite sample holder was neglected in these
preliminary calculations."* Provenance was corrected throughout the
repository in commit `e4fd5b1`.

## Why bother

The MSRE was the only molten-salt reactor that ever achieved sustained
criticality. It ran from 1965 to 1969 at Oak Ridge, demonstrated
on-line refueling, ran on U-235 and U-233 fuel salts, and was shut down
not for any technical failure but because the federal program funding
liquid-fuel reactors was redirected to liquid-metal fast breeders.

Every modern molten-salt-reactor company — Kairos, Terrestrial Energy,
ThorCon, Moltex, TerraPower's MCFR group, Copenhagen Atomics — has the
MSRE as their canonical validation data set, the same way every PWR
designer benchmarks against TMI-2 thermohydraulics and every fast-spectrum
designer benchmarks against EBR-II. If you cannot reproduce the MSRE's
critical configuration to within ~1% k-eff using your code of choice,
your code is not yet usable for design.

The three open benchmarks against MSRE that I am aware of are:

- **IRPhE handbook MSR-MSRE-RES-001** — the official OECD/NEA evaluated
  benchmark; k_eff_exp = 0.99978 ± reported uncertainty.
- **Shen et al. 2021** — a Serpent 2.1.30 + ENDF/B-VII.1 re-derivation
  that reports k = 1.02132 ± 0.00003 in a "rods withdrawn"
  configuration. (Nuclear Science and Engineering, 195(8), 825-837.)
- **Yilmaz et al. 2024** — the ANL/ORNL OpenMC team's own MSRE
  implementation comparing constructive-solid-geometry (CSG) and CAD
  representations. Their CSG OpenMC model reports k = 1.02122 (within
  10 pcm of Shen-Serpent); their CAD model reports k = 1.00872 (much
  closer to the experimental value). (Frontiers in Nuclear Engineering,
  3:1385478.)

What I wanted to add was: (a) a third independent OpenMC
implementation, built from scratch from the same primary sources, as
a cross-check on the Yilmaz CSG result; (b) systematic, parameterized
sensitivity studies on the four parameters that the literature flags
as dominating the gap; and (c) a fully automated, free-infrastructure
CI workflow so anyone with a GitHub account can reproduce the
calculation. So that became the project.

## What I had to work with

Stage one of the build had access to:

- ORNL-TM-730 (the 1965 MSRE design report, scanned PDF on OSTI.gov)
- Shen et al. 2021 (the comparison paper)
- The IRPhE handbook entry summary (full evaluation is paywalled
  through OECD/NEA)
- OpenMC documentation and an ENDF/B-VIII.0 HDF5 cross-section library
- A GitHub Actions free tier (4 vCPU, 16 GB RAM, ~25 min per 100k×100
  particle run)
- Several months of late nights, an LLM pair-programming
  partner, and the willingness to be wrong in public

The MSRE active core is roughly 137 cm in diameter by 168 cm tall — a graphite cylinder
about the size of a residential refrigerator, with 1,140 vertical fuel
channels milled through 504 graphite stringer assemblies. The fuel
salt is LiF-BeF₂-ZrF₄-UF₄, the cladding is INOR-8 (a Hastelloy-N
predecessor), and the control elements are gadolinium-bearing absorber
rods in INOR-8 thimbles. Every one of those dimensions, isotopic
fractions, and material compositions has to be re-derived from the
TM-730 report and matched, exactly, to what the model puts on the
geometry.

## The wrong answer first

Phase 1.1.c of the project produced a heterogeneous model with all
four "thimble positions" (three control rods plus one graphite sample
basket) modeled the same way: an INOR-8 annular shell from the bottom
to the top of the vessel.

This gave k = 1.01308 ± 0.00036 in the canonical configuration. Shen
reports 1.02132. The gap was 824 pcm — about a third of a typical
PWR control-rod bank worth. Big enough to mean the model was wrong.

I went after the suspects in order of literature suggestion. None of
them was a smoking gun:

| Effect | Predicted Δk | Measured Δk |
|---|---:|---:|
| Boron impurity in graphite (1.0 → 0.3 ppm) | +150 to +300 pcm | -196 pcm (wrong sign) |
| Corner-rounding fillets on fuel channels | +50 to +150 pcm | +12 pcm (null) |
| Cross-section library (VIII.0 → JEFF-3.3) | unknown | +177 pcm |
| Library: VIII.0 → VII.1 (Shen's library) | unknown | -145 pcm |

The cumulative explanation from three sensitivity studies summed to
~500 pcm out of an 824-pcm gap. The remaining 300 pcm was unaccounted
for, and the only effect of the right sign — library change — was
quantitatively too small.

## The actual killer

I went back to TM-730 §4.1 and read the sentence I had skimmed
the first three times:

> "Three control-rod thimbles ... The fourth position of the array
> is occupied by a graphite sample assembly."

And then to Shen et al. 2021:

> "Three graphite and INOR-8 sample baskets..."

Shen's INOR-8 in the basket is the four 0.635-cm sample rods *inside*
the basket — not a structural shell around it. The Phase 1.1.c model
had a basket whose position was wrapped in a full-height INOR-8
thimble shell, ~789 cm³ of Inconel, sitting at radius 7.62 cm from the
core axis, where the thermal flux peaks.

INOR-8 contains 70% Ni, 17% Mo, 7% Cr, 5% Fe. Ni-58, Mo-95, and Cr-52
are all parasitic absorbers in a thermal spectrum. A control rod is
literally an absorber sitting at high importance, and this shell was
the same volume and the same material as one, just thinner — but
in the most reactivity-sensitive part of the core.

I gated the shell behind a single environment variable, parameterized
the GitHub Actions workflow to control it, and ran with it off:

```
basket_shell=false → k_eff = 1.02353 ± 0.00033
```

Compared to the baseline of 1.01308, that's **+1,045 ± 49 pcm**.

The residual to Shen-Serpent is now −221 ± 33 pcm — within the spread
I had already measured across three cross-section libraries (322 pcm).
The residual to IRPhE experimental is about +2,375 pcm, which is the
expected rods-out vs. rods-critical worth and matches Shen's
configuration choice.

## What this means and what it doesn't

What it means:

- The gap was not in the physics. It was in the geometry interpretation.
- The MSRE's "fourth position" is graphite, not metal, and any model
  that gets this wrong over-absorbs at high importance.
- One person, one laptop, OpenMC, ~3 months of part-time effort, and
  free-tier CI is enough to land at the same k-effective as the
  state-of-the-art published Serpent benchmark of the same reactor,
  to within 70 pcm at the v0.2.0 statistics, with every dimension,
  every isotope, and every commit publicly reproducible.
- Promethea agrees with the ANL/ORNL OpenMC CSG implementation
  (Yilmaz et al. 2024) to within ~242 pcm. That is a non-trivial
  cross-check: two independently developed OpenMC models of the same
  reactor, built from the same primary sources, converging on the
  same answer. The basket-shell defect would have been very hard to
  catch without an automated sensitivity workflow.
- The v0.1.0 → v0.2.0 jump (from 100k×100 to 200k×200 statistics)
  reproduced the v0.1.0 means within 11 pcm and 2 pcm respectively,
  with the per-run statistical uncertainty shrinking by a factor of 2
  as expected (√4). The model is converged at the v0.2.0 sample size.

What it does not mean:

- I am not a credentialed nuclear engineer. I have a high-school
  education and a self-taught reactor-physics habit. Every result in
  this project will need senior review from someone at a national
  lab, a university group, or an industry team before it can be
  submitted for peer-reviewed publication.
- This is a critical-configuration k-eff result. It is not a depletion
  result, not a fuel-cycle result, not a thermal-hydraulics result,
  not a kinetics result. Those are entire separate projects.
- The 70 pcm overshoot of Shen at v0.2.0 statistics is inside the
  2-sigma Monte Carlo band, but the residual structure of that gap
  (library-by-library breakdown, sensitivity to each free parameter)
  is the work of the v0.3.0 sensitivity matrix — not yet fully
  characterized term-by-term.
- The IRPhE handbook is paywalled; I do not yet have access to the
  evaluator's full geometry write-up to confirm that my dimensional
  re-derivation from TM-730 is identical to theirs. Some of the
  v0.2.0 residual could be that.

## What's next

**v0.3.0** (in progress, Q3 2026): two workstreams that close the
two known limits the v0.2.0 release notes admit.
*Workstream A* dispatches the canonical configuration at the
rounded-corner fuel-fraction (TM-730 f=0.225, fillet_radius=0.475 cm)
to quantify the ~7% systematic over-prediction relative to the
as-built MSRE geometry.
*Workstream B* runs a 5-seed statistical envelope at submission stats
to separate per-run Monte Carlo noise from any seed-dependent bias.
This closes the v0.2.0 "single-seed" caveat.

**Submission package.** An IRPhE Handbook submission documenting
this OpenMC implementation as an independent re-evaluation of the
MSRE benchmark is at `docs/IRPHE_SUBMISSION_DRAFT.md` in the repo.
The §4.2.1 section is now anchored to the TM-730 primary-source
quote on the graphite sample assembly.

**First-author paper.** Targeting *Annals of Nuclear Energy* or
*Nuclear Science and Engineering*. The angle is not "I beat Shen" —
it is "an open, reproducible OpenMC MSRE benchmark with parameterized
sensitivity studies on the four parameters that matter most, and a
full CI-validated provenance chain back to the 1964 primary source."
Co-author outreach in progress with senior researchers at the
relevant national-lab and industry MSR groups.

**v0.4.0** (Q3/Q4 2026, scoping): the next-order question is whether
an open OpenMC pipeline can extend from "verifies a 1965 experiment"
to "verifies a 1968 design that was never built." v0.4.0 will be
the first public, CI-validated, two-fluid Molten-Salt Breeder Reactor
(MSBR) neutronics model, validated against Robertson/Briggs/Smith/
Bettis 1968 (ORNL-4528). The two-fluid variant was abandoned by ORNL
in 1967 due to graphite-element fabrication concerns and has not
been openly recomputed in modern Monte Carlo since. Primary-source
validation anchors from ORNL-4528 Tables 6.2 and 6.8: breeding ratio
1.06; specific inventory 1.26 kg fissile/MWe; mean η of 233U = 2.225;
overall temperature coefficient −4.34×10⁻⁵ /°K @ 900K. Scope is BOL
k-eff + breeding ratio + neutron balance only — no reprocessing, no
depletion, no thermal-hydraulics. Those come in v0.5.0+ as separately
scoped milestones.

## What I learned

The thing that closed the gap was not a more sophisticated method.
It was reading the primary source one more time.

I had read TM-730 §4.1 at least four times before I noticed the
"graphite sample assembly" phrase and understood what it meant
structurally. The literature on what to look for in MSRE-benchmark
discrepancies kept pointing me at boron and at libraries because
those are the things the literature talks about — and so my prior
on where the gap was kept pulling me toward those. The shell defect
was not in anyone's literature because nobody else had made that
particular geometry mistake.

The lesson is: when your prior keeps producing the wrong answer,
the prior is wrong, not the experiment. Read the source again.

The v0.2.0 cycle reinforced this. The TM-730 audit — forced by
reaching milestone-2 numerical targets and needing to defend the
geometry choices in a paper draft — turned up ~137 instances of a
stale report-number typo and a primary-source quote that the
§4.2.1 section of the IRPhE draft now anchors to. The numbers
were already right. The provenance got there second. That order is
backwards, and that's the lesson going into v0.4.0: get provenance
right before you trust the number.

## Reproducing this

```
git clone https://github.com/KhaiB10/promethea.git
cd promethea
# Cross-section library setup (one-time, ~4 GB):
bash scripts/fetch_xs.sh endfb-viii.0
# Run the canonical configuration locally:
docker build -t promethea .
docker run --rm -v $PWD:/work -w /work \
  -e PROMETHEA_BORON_PPM=0.3 \
  -e PROMETHEA_FILLET_R_CM=0.0 \
  -e PROMETHEA_BASKET_SHELL=false \
  -e OPENMC_CROSS_SECTIONS=/work/data/xs/endfb-viii.0-hdf5/cross_sections.xml \
  promethea python benchmarks/msre/run_criticality.py \
    --mode het_critical --particles 200000 --batches 200
```

Or run it on GitHub Actions: the workflow `benchmark-msre.yml` accepts
every parameter as an input (mode, particles, batches, boron_ppm,
fillet_radius_cm, xs_library, basket_shell, seed), runs on the free
ubuntu-latest runner, and produces a step summary with k-eff and a
tail of the OpenMC log.

The v0.2.0 release is at
[github.com/KhaiB10/promethea/releases/tag/v0.2.0](https://github.com/KhaiB10/promethea/releases/tag/v0.2.0)
and carries the 200k×200 submission-of-record run logs in
`benchmarks/msre/runs/v0.2.0_submission/`.

If you find an error in the model — and there are still errors in the
model — please open an issue. The whole point is that we get to a
better answer in public, and that requires people pointing at the
specific places I got it wrong.

---

*Discussion welcome at [github.com/KhaiB10/promethea/discussions](https://github.com/KhaiB10/promethea/discussions).
The full dated research log is at `RESEARCH_LOG.md`; the IRPhE
submission draft is at `docs/IRPHE_SUBMISSION_DRAFT.md`; the canonical
plots are in `benchmarks/msre/plots/`. All MIT-licensed.*
