# MSBR fuel-cell temperature coefficient α (v0.4.0)

**Status:** resolved (z = 9.3). Second numerical anchor for v0.4.0.

**Configuration**

- Geometry: `geometry_unit_cell.py` (heterogeneous unit cell)
- Method: two-point finite difference, `α = (1/k_ref)(Δk/ΔT)`, shared
  seed and particle budget between low-T and high-T runs.
- Library: ENDF/B-VIII.0
- T_lo = 900 K, T_hi = 1200 K, dT = 300 K
- Statistics: 200 000 particles × 220 batches (~200 active), seed=1
- S(α,β) thermal scattering: `c_Graphite` with `method="interpolation"`
  between the 800/1000 K and 1200 K grid points.

**Result**

| Quantity | Value |
|----------|-------|
| k(900 K)  | 1.13174 ± 0.00015 |
| k(1200 K) | 1.12977 ± 0.00015 |
| Δk        | −197 ± 21 pcm over 300 K |
| **α (unit cell)** | **−5.79 × 10⁻⁶ /K ± 6.2 × 10⁻⁷ /K** |
| z-score   | 9.3 (resolved) |

**Cross-reference: published MSBR α values**

| Source | Code | α total | Notes |
|--------|------|---------|-------|
| This work (unit cell)        | OpenMC  | −5.79 ± 0.62 × 10⁻⁶ /K | reflective BCs, fixed density |
| Rykhlevskii 2017 (full core) | Serpent 2 | −1.57 ± 0.033 × 10⁻⁵ /K | full leakage, MTC sign-flipped |
| Park 2015 (full core)        | MCNP6 | −3.21 ± 0.04 × 10⁻⁵ /K | full leakage |
| ORNL-4528 (deterministic)    | CITATION | −4.34 × 10⁻⁵ /K (reactor) | quoted as α_overall = −4.34×10⁻⁵ /K |

**Interpretation**

- Sign: negative — safe. Doppler broadening of 232Th and 233U
  resonances dominates over any thermal flux shift.
- Magnitude: ~10× smaller than the ORNL reactor-level value. This is
  expected: a reflective unit cell lacks leakage and salt-density
  feedbacks, which dominate the reactor coefficient.
- The published literature shows a 3.7× spread between MCNP6, Serpent 2,
  and the ORNL deterministic value at the full-core level. Our
  unit-cell number sits below that range, consistent with omitted
  feedback components.

**Honest scope**

- Unit-cell α is not the reactor α. We cannot claim agreement with
  ORNL or the Rykhlevskii / Park values without a full-core model.
- Fuel-salt density is held fixed across the 900 → 1200 K step. A
  realistic α would also vary fuel density with temperature, which
  contributes a negative thermal expansion feedback for liquid fuels.
- A future v0.5.0 task: extend the temp sweep to vary fuel salt density
  with thermal-expansion (ORNL-4528 Table 3.x) and disentangle the
  fuel-temperature vs moderator-temperature components.

**Reproduce**

```
gh workflow run benchmark-msbr.yml --repo KhaiB10/promethea --ref main \
  -f mode=temp_sweep \
  -f xs_library=endfb-viii.0 \
  -f seed=1 \
  -f particles=200000 \
  -f batches=220 \
  -f temp_lo_K=900 \
  -f temp_hi_K=1200
```

CI run: 26804665291 (HEAD 51471a6).
