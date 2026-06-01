# MSBR — Two-Fluid Molten-Salt Breeder Reactor (v0.4.0 scaffold)

**Status:** scaffold only. Not yet a working model. See
[`docs/V0_4_0_MSBR_SCOPE.md`](../../docs/V0_4_0_MSBR_SCOPE.md) for the
plan-of-record.

## Primary source

Robertson, R. C.; Briggs, R. B.; Smith, O. L.; Bettis, E. S.
*Two-Fluid Molten-Salt Breeder Reactor Design Study (Status as of
January 1, 1968).* ORNL-4528, Oak Ridge National Laboratory, August
1970. OSTI biblio: <https://www.osti.gov/biblio/4093364>. PDF mirror:
<https://energyfromthorium.com/pdf/ORNL-4528.pdf>.

Note: ORNL-4528 documents the **two-fluid** variant, which ORNL set
aside in August 1967 to pursue the single-fluid concept (ORNL-4541,
1971). Promethea v0.4.0 targets the two-fluid variant specifically
because it has not been openly recomputed in modern Monte Carlo since
the original ORNL work.

## Validation anchors (ORNL-4528 Tables 6.2 + 6.8 @ 20 kW/L)

| Quantity                                  | ORNL-4528  | Acceptable band |
|-------------------------------------------|------------|-----------------|
| Breeding ratio                            | 1.06       | ±0.02           |
| Specific inventory (kg fissile / MWe)     | 1.26       | ±10%            |
| Specific power (MWt / kg fissile)         | 1.77       | ±10%            |
| Mean η of 233U                            | 2.225      | ±2%             |
| Mean η of 235U                            | 1.981      | ±2%             |
| Fissions in fuel stream (fraction)        | 0.996      | ±0.005          |
| Thermal-group fission fraction            | 0.846      | ±0.02           |
| Power density, gross (kW/L)               | 19         | input           |
| Power density in fuel salt (kW/L)         | 140        | derived check   |
| α_moderator (×10⁻⁵ /°K @ 900K)            | +1.66      | sign-correct    |
| α_fertile salt (×10⁻⁵ /°K @ 900K)         | +2.05      | sign-correct    |
| α_fuel salt (×10⁻⁵ /°K @ 900K)            | −8.05      | sign-correct    |
| **α_overall (×10⁻⁵ /°K @ 900K)**          | **−4.34**  | **±20%**        |

Full neutron balance to 0.1% per nuclide is in ORNL-4528 Table 6.3 and
is the direct OpenMC reaction-rate tally validation target.

## Reference design (ORNL-4528 §5.1, Table 5.1)

Single reactor module @ 20 kW/L, 556 MWt (1000 MWe plant = 4 modules):

- Core: 10 ft diam × 13 ft 3 in tall (304.8 cm × 403.86 cm)
- 420 fuel cells on 5 3/8 in (13.6525 cm) HEX triangular pitch
- 252 blanket cells, 5 3/8 in × 3 1/16 in (7.7788 cm) ID
- Fuel cell unit (Fig 6.7):
  - Outer hex tube: 5 3/8 in across flats, 2 23/32 in (6.9056 cm) bore
  - Concentric inner tube: 2 1/4 in (5.715 cm) OD × 1 1/4 in (3.175 cm) ID
  - Fuel flows down inner bore, up annulus
- Core volume fractions: 0.802 graphite / 0.134 fuel salt / 0.064 blanket salt
- Blanket region volume fractions: 0.58 salt / 0.42 graphite
- Reflector: 6 in (15.24 cm)
- Vessel: modified Hastelloy N (Table 3.3)

## Salts (ORNL-4528 Table 3.1)

- **Fuel salt:** 7LiF–BeF2–233UF4 (68.5–31.3–0.2 mol%)
  - ρ ≈ 127 lb/ft³ ≈ 2.035 g/cm³ @ 1150°F (894 K)
  - T_liq = 842°F (723 K)
- **Blanket salt:** 7LiF–ThF4–BeF2 (71–27–2 mol%)
  - ρ ≈ 277 lb/ft³ ≈ 4.437 g/cm³ @ 1200°F (922 K)
  - T_liq = 1040°F (833 K)
- **Coolant salt** (not in neutronics): NaBF4–NaF (92–8 mol%)

## Graphite (ORNL-4528 Table 3.5)

- Isotropic, special grade (specific supplier not selected in 1968)
- ρ ≈ 115 lb/ft³ ≈ 1.842 g/cm³ at room temperature
- ~23 vol% voids
- Useful life: 5.1×10²² n/cm² (E > 50 keV) per 1968 study

## Files (scaffold)

- `materials.py` — MSBR salt + graphite + Hastelloy N material recipes
- `geometry_unit_cell.py` — single fuel cell unit cell (Fig 6.7),
  reflective BC, prototype of the CSG approach
- `run_unit_cell.py` — small driver: compute k-infinity of one cell

These are deliberately minimal. The full assembly geometry + tally
suite + CI integration come after the unit-cell sanity check passes.
