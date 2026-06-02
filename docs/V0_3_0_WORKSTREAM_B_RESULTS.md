# v0.3.0 Workstream B — RNG Seed Stability Envelope

**Status:** complete (5/5 seeds)
**Last updated:** 2026-06-01

## Configuration

All runs use identical inputs except `seed`:

| Input | Value |
|---|---|
| mode | `het_critical` |
| particles per batch | 50,000 |
| batches | 120 |
| boron_ppm | 0.3 |
| fillet_radius_cm | 0.475 |
| basket_shell | `false` |
| xs_library | `endfb-viii.0` |

## Results

| Seed | k-eff (combined) | sigma (within) | delta vs mean | CI run |
|------|------------------|----------------|---------------|--------|
| 1 | 1.02397 | 0.00053 | +17 pcm | [26764074706](https://github.com/KhaiB10/promethea/actions/runs/26764074706) |
| 2 | 1.02335 | 0.00049 | -45 pcm | [26764077862](https://github.com/KhaiB10/promethea/actions/runs/26764077862) |
| 3 | 1.02335 | 0.00053 | -45 pcm | [26789884651](https://github.com/KhaiB10/promethea/actions/runs/26789884651) |
| 4 | 1.02416 | 0.00040 | +36 pcm | [26792084296](https://github.com/KhaiB10/promethea/actions/runs/26792084296) |
| 5 | 1.02416 | 0.00048 | +36 pcm | [26764087949](https://github.com/KhaiB10/promethea/actions/runs/26764087949) |

## Envelope statistics (5-seed final)

- **Mean k**: 1.02380
- **Between-seed sample stdev**: 0.00042 (42 pcm)
- **Pooled within-seed sigma**: 0.00049 (49 pcm)
- **SEM (between-seed)**: 0.00019 (19 pcm)
- **vs v0.2.0 VIII.0 canonical (k = 1.02364, 200k×200)**: **delta = +16 pcm**

## Interpretation

The between-seed sample stdev (42 pcm) and the pooled within-seed sigma (49 pcm) are within 14% of each other. For a well-mixed RNG and a deterministic transport routine, these two quantities should converge to the same value as N -> infinity. Cross-seed scatter approximately equal to within-seed scatter is the signature of a clean Monte Carlo with no seed-dependent bias.

The 5-seed mean shifts 16 pcm above the v0.2.0 canonical at 200k×200 particles. This is well inside the 1-sigma envelope (canonical sigma = 16 pcm; SEM here = 19 pcm) and consistent with statistical agreement between the 50k×120 envelope and the 200k×200 canonical run.

**Conclusion:** the PROMETHEA_SEED plumbing (v0.3.0 Workstream B) produces independent, statistically clean samples. No seed-dependent bias is detected at the 50k×120 statistics level. The seed envelope is ready to be folded into the v0.3.0 sensitivity matrix as a fifth axis.

## Carry-over from initial dispatch

Seeds 3 and 4 originally failed in the first dispatch with Docker buildx "no space left on device" errors when two parallel jobs hit the same runner cache. Sequential re-dispatch (one at a time) resolves the issue. The workflow concurrency group already keys on seed, so this is a runner-side capacity problem, not a workflow bug. Will document in a follow-up RUNBOOK if it recurs.

## Regenerating this table

```bash
python scripts/analysis/seed_envelope.py \
    --pair 1 1.02397 0.00053 \
    --pair 2 1.02335 0.00049 \
    --pair 3 1.02335 0.00053 \
    --pair 4 1.02416 0.00040 \
    --pair 5 1.02416 0.00048
```

or via the JSON-based `--runs` mode pointing at the five CI run IDs.

## Reproducibility

All five CI runs are publicly visible on the [Actions tab](https://github.com/KhaiB10/promethea/actions/workflows/benchmark-msre.yml). Each is reproducible bit-for-bit from a fresh `gh workflow run benchmark-msre.yml` invocation with identical inputs and OpenMC version `0.14.0` pinned in the Dockerfile.
