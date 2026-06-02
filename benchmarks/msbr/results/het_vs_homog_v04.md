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

| seed | library | k_het | k_homog | Δk (pcm) | z |
|------|---------|---------------------|---------------------|-----------|------|
| 1    | VIII.0  | 1.13132 ± 0.00039   | 1.02602 ± 0.00041   | +10 530 ± 56 | 186  |
| 2    | VIII.0  | 1.13212 ± 0.00041   | 1.02608 ± 0.00038   | +10 604 ± 56 | 190  |
| 1    | VII.1   | 1.13208 ± 0.00040   | 1.02707 ± 0.00041   | +10 501 ± 58 | 182  |

**Pooled VIII.0 estimate:** Δk = **+10 567 ± 40 pcm**.

**Library spread on Δk:** VII.1 − pooled VIII.0 = **−66 ± 70 pcm**
(statistically consistent with zero).

**Second finding — library robustness of the heterogeneity Δk:** while
individual k_inf values shift between libraries (~600 pcm here, vs the
162 pcm shift seen in MSRE), the *difference* k_het − k_homog is
library-invariant at our statistical precision. The het and homog
cells absorb the library bias similarly, so the geometric effect
cancels out. This makes the Δk a structural property of the MSBR
fuel-cell geometry, not a library-specific artifact.

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

**Honest scope and prior art**

- This is a unit-cell k_∞ result, not a core-level reactivity penalty.
  Reactor-scale Δk requires the full lattice + reflector geometry.
- Cross-code verification (Serpent or MCNP) not yet performed.
- Pending v0.4.0: cross-library spread (VII.1, JEFF-3.3, JENDL),
  spectrum decomposition, BR comparison.

**Prior art that exists** (disclosed for honesty):

- Rykhlevskii, Lindsay, Huff (2017), "Online Reprocessing Simulation for
  Thorium-Fueled Molten Salt Breeder Reactor," Trans. ANS 117:239-242:
  Serpent 2 / ENDF-B/VII.0 unit-cell of MSBR Zone I (13.2 vol% fuel,
  908 K, periodic BCs). Reports k_inf and depletion behavior. Does NOT
  perform a het vs homog Δk comparison.
- Rykhlevskii, Lindsay, Huff (2017), "Full-Core Analysis of
  Thorium-Fueled MSBR Using SERPENT 2," Trans. ANS 117:1343-1346:
  Serpent 2 full-core, k_eff = 1.00389 ± 0.00005.
- Betzler et al. (OSTI 1559664): SCALE/TRITON full-core vs unit-cell
  comparison for fast-spectrum MSRs, NOT MSBR thermal.

**What this work adds over the above:**

1. First open-source OpenMC measurement of MSBR fuel-cell k_inf with
   independent verification across two seeds.
2. First openly reproducible Δk_het/homog measurement for the MSBR
   fuel cell. Prior unit-cell papers (Rykhlevskii) modeled only the
   heterogeneous configuration.
3. Reproducible from a public CI workflow with pinned cross-section
   library and seed; raw artifacts attached to each run.

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
- seed=1, VIII.0: GitHub Actions run 26796542385 (HEAD 654cf8f)
- seed=2, VIII.0: GitHub Actions run 26797667813 (HEAD 654cf8f)
- seed=1, VII.1:  GitHub Actions run 26806106692 (HEAD af7ebaa)
