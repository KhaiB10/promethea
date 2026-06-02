# MSBR fuel-cell breeding ratio (v0.4.0)

**Status:** resolved. Third numerical anchor for v0.4.0.

**Configuration**

- Geometry: `geometry_unit_cell.py` (heterogeneous unit cell, single
  fuel-cell pitch, reflective BCs)
- Tally: `benchmarks/msbr/tallies.py` — MaterialFilter on fuel salt +
  blanket salt; nuclides {U233, U235, Th232, U234, Pa233}; scores
  {fission, absorption, (n,gamma)}; plus a 4-group flux spectrum tally
  on the same materials.
- Library: ENDF/B-VIII.0
- Statistics: 50 000 particles × 120 batches (100 active), seed=1, 900 K

**Definition**

Following ORNL-4528 §6.3:

    BR = 232Th(n,gamma)  /  233U_absorption

For the heterogeneous fuel-cell prototype, 232Th sits in both the
fuel salt and the blanket salt, while 233U sits only in the fuel salt.
The MaterialFilter sums automatically over both Th-bearing regions.

**Result**

| Quantity | Value | 1σ |
|----------|-------|-----|
| 232Th(n,γ) rate (per source n) | 4.262 × 10⁻¹ | ±2.2 × 10⁻⁴ |
| 233U absorption (per source n) | 5.058 × 10⁻¹ | ±2.7 × 10⁻⁴ |
| 233U fission (per source n)    | 4.547 × 10⁻¹ | ±2.4 × 10⁻⁴ |
| **BR (unit cell)**             | **0.8426** | **±0.0006** |

**Derived quantities**

| Quantity | Value | Notes |
|----------|-------|-------|
| α(233U) ≡ capture/fission | (abs−fis)/fis = 0.1124 ± 0.0008 | textbook range 0.09 – 0.13 |
| 233U fission fraction of total abs | fis/abs = 0.8989 ± 0.0007 | very thermal spectrum |

**Cross-reference**

| Source | BR | Notes |
|--------|-----|-------|
| This work (unit cell, VIII.0)        | 0.8426 ± 0.0006 | static, reflective BCs, no blanket peaking |
| ORNL-4528 (deterministic, full core) | 1.06            | full two-fluid geometry with Th blanket region |
| Rykhlevskii 2017 (Serpent 2, full core) | 1.054 (BOL)  | online reprocessing, full leakage |

**Interpretation**

The unit cell measures BR ≈ 0.84 because the heterogeneous fuel-cell
geometry concentrates flux in the fuel channel where 233U sits, not in
a distinct blanket layer where 232Th capture could outrun fissile
destruction. Reaching reactor-scale BR > 1 requires the two-fluid
core's full geometry: a separate Th-bearing blanket with its own
spatial flux peaking, plus leakage that the unit cell suppresses via
reflective BCs.

The unit-cell BR of 0.84 is reported here as an openly reproducible
neutron-balance signature of the heterogeneous fuel-cell geometry on
its own. It is **not** a reactor-level BR and should not be compared
to the ORNL/Rykhlevskii full-core numbers as if it were the same
quantity. v0.5.0 (full two-fluid core) is the appropriate scale for a
reactor BR comparison.

**Honest scope**

- This is a unit-cell BR, not a reactor BR.
- 233U is the only fissile in the inventory at t=0; depletion is not
  enabled in v0.4.0. Once depletion is wired in, contributions from
  235U / 239Pu / 241Pu would also appear (the tally module already
  reserves slots for them).
- No nu-fission tally yet, so η = ν Σ_f / Σ_a is left unreported (the
  tally scaffold reserves it for v0.5.0).

**Reproduce**

```
gh workflow run benchmark-msbr.yml --repo KhaiB10/promethea --ref main \
  -f mode=unit_cell \
  -f xs_library=endfb-viii.0 \
  -f seed=1 \
  -f particles=50000 \
  -f batches=120
```

CI run: 26811958529 (HEAD 94d318b).
