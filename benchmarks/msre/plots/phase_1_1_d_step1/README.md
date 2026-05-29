# Phase 1.1.d step 1 — geometry verification plots

Generated from CI run [26667977773](https://github.com/KhaiB10/promethea/actions/runs/26667977773)
on commit `cd0e0a3`, post stringer half-channel orientation fix
(`ffb9488`).

These plots are the visual sanity check on the corrected stringer
geometry described in `STRINGER_GEOMETRY.md` and the corresponding code
fix in `geometry_het.py`.

## Plot inventory

### `01_stringer_unit_cell.png`
Single 5.5 × 5.5 cm window centered on one stringer, sliced at z = 0
(active-core midplane). Shows the four half-channels machined into each
face of the 5.08 × 5.08 cm graphite stringer:

- Each notch is **0.508 cm deep** into the stringer (perpendicular to
  the face), as TM-0728 §2.6 specifies.
- Each notch is **3.048 cm long** along the face (parallel to it),
  matching the "1.2 in" dimension.
- Top/bottom notches are oriented horizontally (long axis along X);
  left/right notches are oriented vertically (long axis along Y).

This is the verification that the half-channel orientation fix landed
correctly. Pre-fix, notches would have been deep narrow rectangles at
face midpoints (1.524 × 1.016 cm) instead of the shallow long slabs
shown here.

### `02_lattice_3x3.png`
~15.7 × 15.7 cm window showing a 3 × 3 stringer tile at z = 0. Shows how
adjacent stringers' facing half-channels combine into full **1.016 ×
3.048 cm** fuel channels between the stringers. Two control-rod thimbles
appear in the corners (positions 1 and 4 of the rod array at radius
7.62 cm).

### `03_core_xy_midplane.png`
Full 160 × 160 cm window showing the entire active-core cross-section
at z = 0:
- Yellow + dark-gray gridwork: graphite stringer lattice
- Yellow ring outside the lattice: salt downcomer
- Steel-blue ring: core can (INOR-8, 0.635 cm wall)
- Yellow annulus: outer salt downcomer
- Steel-blue ring: vessel wall (INOR-8, 1.42 cm wall)
- Four small circles in the center: rod thimbles (poison not visible at
  z = 0 because the inserted-rod tip is at z = +35.139 cm — below the
  tip, the bore is pure salt).

### `04_core_xy_above_rod_tip.png`
40 × 40 cm zoom window at z = +50 cm, **above the inserted-rod tip**.
Critical verification that the IRPhE configuration is correct:
- Top-left thimble (inserted, position 2): steel-blue thimble shell, copper
  Inconel cladding, **red Gd2O3-Al2O3 poison annulus**, yellow salt in
  the hollow center
- Top-right thimble (withdrawn, position 1): pure salt bore
- Bottom-left thimble (sample basket, position 3): tan basket-mix bore
  (homogenized 7.71% INOR-8 / 23.09% graphite / 69.20% salt)
- Bottom-right thimble (withdrawn, position 4): pure salt bore

Confirms that the `INSERTED_INDEX = 2` and `BASKET_INDEX = 3`
configuration in `build_geometry_het_critical` is producing the right
material layout in the right places.

### `05_core_xz_y_rod_row.png`
Vertical slice through y = +7.62 cm — the row containing two of the
four rod thimbles (positions 1 and 2). Shows:
- Tan band at the bottom: lower-head mix (Phase 1.1.c step 1)
- Yellow + dark-gray vertical stripes: graphite stringer lattice
  (slice cuts along the channel long axis, so stringers appear as solid
  vertical columns)
- Two steel-blue thimble columns flanking center: positions 1 and 2
- **Left thimble (inserted)**: red + copper poison column terminates at
  z = +35.139 cm (the rod tip). Below the tip the bore is pure salt.
- **Right thimble (withdrawn)**: pure salt bore from bottom to top.
- Yellow above the lattice: upper plenum (salt).

This plot is the top-level verification that the inserted-rod tip
elevation is correct and the IRPhE 4.4-inch insertion depth is
faithfully modeled.

## Color legend

| Color | Material |
|---|---|
| Gold | Fuel salt (LiF-BeF2-ZrF4-UF4 with U-235 enriched per IRPhE) |
| Dark gray | CGB graphite |
| Steel blue | INOR-8 (Hastelloy N) — vessel, can, thimbles |
| Copper / brown | Inconel-600 (rod cladding) |
| Red | Gd2O3-Al2O3 poison (control rod bushing) |
| Tan | Homogenized mixes (lower-head 90.8/9.2, sample basket) |

## Reproducing

From the repo root, after a successful Phase 1.1.c CI run (so the
cross-section cache and Docker image are warm):

```bash
gh workflow run benchmark-msre.yml --ref main -f mode=plot
```

Then download the `msre-plot-run-<n>` artifact from the run summary.
The five PNGs are in `out/plots/`.
