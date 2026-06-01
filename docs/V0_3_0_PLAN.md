# Promethea v0.3.0 — Plan of Record

**Status:** drafted 2026-05-30, post-v0.2.0 tag
**Target window:** 2026-06 (after Romano response window closes)
**Predecessor:** v0.2.0 — "Submission-of-record statistics, Shen-matched comparison, TM-730 audit"

---

## Headline goals

v0.3.0 closes the two known limits that the v0.2.0 release notes list
in its **Known limits** section:

1. **Quantify the sharp-corner fuel-fraction systematic bias.** v0.2.0
   acknowledges that the canonical configuration uses `fillet_radius_cm
   = 0.0` (sharp corners, fuel fraction f = 0.240), but TM-730 §2
   (lines 1756–1761) specifies that the as-built MSRE used rounded
   corners with f = 0.225. v0.3.0 will execute the matching
   rounded-corner run at the submission-of-record statistics and
   report the resulting Δk.
2. **Characterize the statistical envelope on top of per-run σ.**
   v0.2.0 reports each canonical configuration as a single 200k × 200
   run with σ ≈ 16–19 pcm. v0.3.0 will repeat each canonical
   configuration 5 times with different random seeds and report
   (mean, sample std-dev, per-run σ) so that the cross-code agreement
   number (+70 ± 39 pcm vs Shen) is hardened against single-sample
   bias.

Neither item is gap-closing relative to the IRPhE experimental value
(which requires CAD geometry); both are credibility-hardening relative
to the published v0.2.0 cross-code comparisons.

## Non-goals

- CAD geometry. Out of v0.x scope and orthogonal to the contributions
  this project is making.
- New library beyond {VIII.0, VII.1, JEFF-3.3}. The three already in
  the workflow span the relevant cross-section library universe for
  MSRE.
- New cross-section evaluations (e.g. ENDF/B-VIII.1 when released).
  Reserved for v0.4.0 if the library lands during the v0.3.0 window;
  otherwise stays out.

---

## Workstream A — Rounded-corner f = 0.225 sensitivity

### Configuration

```yaml
mode: het_critical
particles: 200000
batches: 200
boron_ppm: 0.3
fillet_radius_cm: 0.475    # solves 8 * r^2 * (1 - π/4) = (0.240 - 0.225) * 5.08^2
xs_library: endfb-viii.0
basket_shell: false
```

The fillet plumbing already exists end-to-end: workflow input
`fillet_radius_cm` → `PROMETHEA_FILLET_RADIUS_CM` env var →
`benchmarks/msre/geometry_het.py:FUEL_CHANNEL_CORNER_R`. No code
changes required for Workstream A.

A companion VII.1 rounded-corner run is optional but recommended for
symmetry with the v0.2.0 canonical/library-matched pairing. If runner
time is tight, ship the VIII.0 number first and the VII.1 number as a
v0.3.1 follow-up.

### Expected magnitude

A rough analytical estimate: rounded corners reduce fuel inventory by
~6% of the bulk cross-section moderation effect. The MSRE
moderation-vs-poisoning balance gives k roughly proportional to fuel
density at this f-range, so a ~6–7% reduction in fuel inventory should
depress k by a measurable but bounded amount. Order-of-magnitude
estimate: **Δk ≈ −500 to −1500 pcm**, almost certainly negative,
moving the canonical Promethea result toward the experimental value
and toward the Yilmaz CAD result (k = 1.00872).

If the result is much smaller than this (< 100 pcm), revisit the
geometry to confirm the fillet is actually being applied. If it's
much larger (> 2000 pcm), revisit the analytical estimate — there
may be additional second-order effects (spectrum hardening, leakage)
that warrant a §6 Discussion paragraph in the paper draft.

### Deliverables

- One submission-of-record artifact: `msre-het_critical-endfb-viii.0-run-N`
  with `fillet_radius_cm = 0.475`, checked into
  `benchmarks/msre/runs/v0.3.0_submission/viii0_rounded_corners.log`.
- A new entry in `RESEARCH_LOG.md` reporting Δk and updating the
  v0.2.0 Known-Limits-list status.
- A new row in the IRPhE submission draft k-eff comparison table.
- A new §6.3 Discussion paragraph in `docs/PAPER_OUTLINE.md` /
  paper draft: "Sensitivity of k-effective to the as-built channel
  geometry: sharp-corner vs rounded-corner fuel volume fraction."

### Risk

Low. The geometry plumbing has been exercised in earlier sensitivity
sweeps (Phase 1.1.c step 2 ran `fillet_radius_cm = 0.475` at lower
statistics and produced a reasonable k-eff). No new code paths.

---

## Workstream B — Multi-seed statistical envelope

### Code change required

Add a `PROMETHEA_SEED` env var that maps to `openmc.Settings.seed`,
plus a corresponding workflow input. Insertion point is
`benchmarks/msre/run_criticality.py` immediately after the particle
override block (around line 148):

```python
# Optional explicit seed for multi-seed envelope characterization.
env_seed = os.environ.get("PROMETHEA_SEED")
if env_seed:
    settings.seed = int(env_seed)
    print(f"[msre_{mode}] seed: {settings.seed}")
```

The corresponding workflow input:

```yaml
seed:
  description: "RNG seed (positive int). Omit/0 to let OpenMC default. Use 1..5 for the v0.3.0 envelope sweep."
  required: false
  default: "0"
```

And the env-var pass-through:

```yaml
SEED: ${{ github.event.inputs.seed || '0' }}
...
-e PROMETHEA_SEED=$SEED \
```

Include `seed` in the concurrency-group hash so parallel envelope
runs don't preempt each other.

### Configuration

5 dispatches, one per seed ∈ {1, 2, 3, 4, 5}, at the v0.2.0
submission-of-record canonical:

```yaml
mode: het_critical
particles: 200000
batches: 200
boron_ppm: 0.3
fillet_radius_cm: 0.0          # sharp corners — matches v0.2.0 headline
xs_library: endfb-viii.0
basket_shell: false
seed: <1, 2, 3, 4, 5>           # one dispatch per seed
```

Optionally repeat the same 5-seed envelope at `xs_library = endfb-vii.1`
for direct library-matched envelope characterization. This doubles
runner cost; do only if v0.2.0 headline is being challenged.

### Expected magnitude

Per-run σ at 200k × 200 is ~16 pcm (VIII.0). For 5 independent seeds
the sample standard deviation σ_seed should land in the same ballpark
(15–25 pcm) if the run is well-converged. A σ_seed much larger than
the per-run σ (e.g. 40+ pcm) would indicate undersampling of the
fission-source distribution and would warrant raising inactive-batch
count.

The Romano-facing claim becomes:
**k = 1.02364 ± σ_seed (5-seed) ± 0.00016 (per-run)** — a strictly
stronger statement than v0.2.0.

### Deliverables

- 5 (or 10 with VII.1) checked-in artifacts under
  `benchmarks/msre/runs/v0.3.0_envelope/`.
- A small reduction script `benchmarks/msre/runs/v0.3.0_envelope/reduce.py`
  that extracts k-eff from each log and writes a CSV (`envelope.csv`)
  plus the summary statistics (mean, sample std-dev, min, max).
- A new entry in `RESEARCH_LOG.md` reporting the envelope.
- An update to the IRPhE submission draft's "submission-of-record"
  table replacing the single-run σ with (mean ± σ_seed) ± σ_per-run.

### Risk

Low–moderate. The code change is ~5 lines and well-contained. The
unknown is whether OpenMC v0.15.x correctly fans out its RNG given a
seed input — verify on one quick (5k × 30) run first that two
different seed values produce two different k-eff means at the
1-pcm-or-greater level. If the seed plumbing turns out to be a
no-op, fall back to running multiple independent dispatches with
slightly different `particles` counts (e.g. 200000, 199999, 200001,
…) which guarantees independent random walks at the cost of slightly
inconsistent statistics.

---

## Dispatch checklist

When v0.3.0 work begins:

1. **Pre-flight**
   - [ ] Confirm v0.2.0 release URL is being shared in any external
         outreach (Romano email, blog post).
   - [ ] Confirm GH Actions runner minutes budget for the month is
         not at risk (Workstream B uses ~10 hours of runner time at
         85 min/run × 5–10 runs).
   - [ ] Open a v0.3.0 milestone on GitHub with both workstreams as
         issues.

2. **Workstream A (no code change)**
   - [ ] Dispatch the VIII.0 rounded-corner run with the
         configuration above.
   - [ ] If runner capacity allows, dispatch the VII.1 companion in
         parallel.
   - [ ] On completion, run the same artifact-download + k-eff
         extraction flow used for v0.2.0.
   - [ ] Commit run logs to `benchmarks/msre/runs/v0.3.0_submission/`.
   - [ ] Append RESEARCH_LOG entry.

3. **Workstream B (small code change)**
   - [x] Add `PROMETHEA_SEED` plumbing (run_criticality.py + workflow yml). *(2026-06-01)*
   - [ ] Quick verification: 5k × 30 dispatch at seed=1 vs seed=2 →
         expect two different k-eff means.
   - [ ] If the verification passes, dispatch 5 seeds at the
         submission-of-record statistics.
   - [ ] Write `reduce.py` and `envelope.csv`.
   - [ ] Commit + RESEARCH_LOG entry + update IRPhE submission table.

4. **Closeout**
   - [ ] Update v0.2.0 Known-Limits list with cross-references to the
         v0.3.0 results (don't remove items — leave them with "→
         resolved in v0.3.0" notes for documentation hygiene).
   - [ ] Tag v0.3.0.
   - [ ] Publish v0.3.0 GitHub Release.
   - [ ] Append v0.3.0 Update paragraph to Romano follow-up (if the
         thread is still active by then).

---

## Open questions

- Should v0.3.0 also fold in the **inactive-batch convergence study**
  that the IRPhE items-to-resolve list flagged? Doing so adds a third
  workstream of ~similar size. The Romano email mentions a draft
  outline, not a finished paper, so v0.3.0 can stay focused on the
  two stated workstreams; convergence study can be a v0.3.1 polish.
- Should v0.3.0 ship a small "promethea-cli" script that wraps the
  Docker run command into a friendlier interface for outside
  reproducers? Out of scope for v0.3.0 but worth a tracking issue.

---

## Provenance

- v0.2.0 release notes: `.local/V0_2_0_RELEASE_NOTES_FINAL.md`,
  `Known limits` section.
- TM-730 audit: `.local/TM730_AUDIT.md`, commit `e4fd5b1`.
- Submission-of-record runs: `benchmarks/msre/runs/v0.2.0_submission/`.
- Fillet plumbing reference: `benchmarks/msre/geometry_het.py:60-95`.
- Settings plumbing reference: `benchmarks/msre/run_criticality.py:126-160`.
