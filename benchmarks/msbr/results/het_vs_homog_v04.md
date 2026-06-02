# MSBR fuel-cell heterogeneity Δk (v0.4.0 first measurement)

**Status:** candidate-novel — first openly reproducible Monte Carlo
measurement of the MSBR fuel-cell het/homog Δk magnitude.

**Configuration**

- Geometry: `geometry_unit_cell.py` (heterogeneous, ORNL-4528 5 3/8 in.
  hex pitch, axially periodic 1 cm slab, reflective BCs) vs
  `geometry_unit_cell_homog.py` (volume-mixed fuel + graphite + blanket
  filling the same outer envelope)
- Volume fractions (as-built equal-area cylinder): fuel 0.1222 /
  graphite 0.8138 / blanket 0.0640
- Library: ENDF/B-VIII.0
- Temperature: 900 K (S(α,β) interpolation between 800/1000 K)
- Statistics: 50 000 particles × 120 batches (100 active), 2 seeds

**Results**

| seed | k_het | k_homog | Δk (pcm) | z |
|------|---------------------|---------------------|-----------|------|
| 1    | 1.13132 ± 0.00039   | 1.02602 ± 0.00041   | +10 530 ± 56 | 186  |
| 2    | 1.13212 ± 0.00041   | 1.02608 ± 0.00038   | +10 604 ± 56 | 190  |

**Pooled estimate:** Δk = **+10 567 ± 40 pcm**.

**Interpretation**

- Sign: positive — explicit fuel/graphite/blanket geometry adds
  reactivity vs a perfectly mixed cell at the same volume fractions.
  This is expected in any thermal Th breeder (IAEA TE-1450 §4;
  world-nuclear.org Th briefing).
- Magnitude: +10.6 % Δk. Large compared to LWR pin cells (~1–2 % Δk)
  because the cell is unusually graphite-rich (81 vol%) and U-233 in the
  homog case is diluted by ~8× by volume relative to the het fuel zone,
  destroying the spatial self-shielding and resonance escape advantage
  of explicit fuel zones.
- Reproducibility: two independent seeds agree within 74 pcm
  (well under 2σ of the difference).

**Honest scope**

- This is a unit-cell k_∞ result, not a core-level reactivity penalty.
  Reactor-scale Δk requires the full lattice + reflector geometry.
- Cross-code verification (Serpent or MCNP) not yet performed.
- Pending v0.4.0: cross-library spread (VII.1, JEFF-3.3, JENDL),
  spectrum decomposition, BR comparison.

**Reproduce**

```
gh workflow run benchmark-msbr.yml --repo KhaiB10/promethea --ref main \
  -f mode=het_vs_homog \
  -f xs_library=endfb-viii.0 \
  -f seed=1 \
  -f particles=50000 \
  -f batches=120
```

CI runs (this measurement):
- seed=1: GitHub Actions run 26796542385 (HEAD 654cf8f)
- seed=2: GitHub Actions run 26797667813 (HEAD 654cf8f)
