# Phase 1.1.c — Detailed Geometry Plan

## Goal

Close the remaining bias between Phase 1.1.b het v1 (~1.04-1.06 expected) and the published IRPhE OpenMC CSG result (~1.020) by adding the four features v1 deliberately omits:

1. Lower-head INOR-8 mix (85% salt / 15% INOR-8 by volume)
2. Core barrel (INOR-8 cylinder between graphite core and vessel)
3. Sample baskets (3 baskets near core center)
4. Control rod thimbles (3 equidistant, with poison rods at IRPhE-specified positions)

Expected cumulative effect: ~-2000 pcm (negative) bringing v1 down from ~1.04-1.06 to ~1.02-1.04.

---

## Reference dimensions (primary sources)

### Reactor vessel and core barrel

| Component | Dimension | Source |
|---|---|---|
| Reactor vessel inner diameter | 147.32 cm (58 in) | [Shen progress paper](https://www.osti.gov/servlets/purl/1413611) |
| Reactor vessel height | ~239 cm | Shen |
| Core barrel ("can") outer diameter | 142.24 cm (56 in) | [ORNL TRANSFORM model](https://info.ornl.gov/sites/publications/Files/Pub133245.pdf) |
| Downcomer annulus thickness | ~2.54 cm (1 in) | derived (147.32 - 142.24)/2 |
| Downcomer height | ~162.6 cm (64 in) from flow distributor to lower plenum | ORNL TRANSFORM |
| Core barrel thickness | TBD — currently estimated at 0.95-1.27 cm (3/8-1/2 in) typical for INOR-8 vessels | Need IRPhE benchmark spec |
| Graphite core radius (effective) | 70.168 cm ± 0.2 | [Fratoni 2023](https://msrworkshop2023.ornl.gov/wp-content/uploads/2016/09/presentation-session-5-Fratoni.pdf) |
| Graphite core height | 166.446 cm ± 1 | Fratoni |

### Lower head

| Component | Spec | Source |
|---|---|---|
| Homogenized composition | 85% fuel salt + 15% INOR-8 by volume | [Yilmaz 2024](https://www.frontiersin.org/journals/nuclear-engineering/articles/10.3389/fnuen.2024.1385478/full) |
| Previous (wrong) CSG composition | 90.8% salt + 9.2% INOR-8 | Yilmaz 2024 |
| Contents represented | Grid support plates + 48 anti-swirl vanes (INOR-8) | Yilmaz, Shen |
| Axial extent below core | TBD (need exact cm) | — |
| k-eff impact of fix (9.2% → 15% INOR-8) | "more than 100 pcm" (negative) | Yilmaz 2024 |

### Sample baskets

| Component | Spec | Source |
|---|---|---|
| Number | 3 | Shen |
| Location | Near core center | Shen |
| Per basket | 4 × INOR-8 rods (0.635 cm dia) + 5 graphite bars (0.635 × 1.1938 cm cross section) | Shen |
| Radial position | TBD — need IRPhE benchmark | — |
| Axial extent | TBD — need IRPhE benchmark | — |

### Control rod thimbles

| Component | Spec | Source |
|---|---|---|
| Number | 3, equidistant from core centerline | Shen |
| Poison material | 70 wt% Gd2O3 + 30 wt% Al2O3 | Shen |
| Poison cladding | Inconel | Shen |
| Poison form | Hollow circular cylinders, ~1 in (~2.54 cm) OD | Shen, IAEA |
| Rod position, 2 withdrawn rods | 129.54 cm axial | Shen |
| Rod position, 1 inserted rod | 118.364 cm axial (4.4 inches inserted) | Shen, Yilmaz |
| Difference (insertion depth) | 11.176 cm = 4.4 in | Shen |
| Thimble outer/inner diameter | TBD — typically ~5 cm OD | Need IRPhE |
| Radial position from core centerline | TBD — need IRPhE | — |

---

## Dimensions resolved from ORNL-TM-0728 (MSRE Design Report Part III)

Table 3.1 of TM-0728 (the canonical 20-region core model) gives the IRPhE benchmark dimensions in inches. Converted to cm:

| Region | Inner r (cm) | Outer r (cm) | Bottom z (in) | Top z (in) | Composition (vol %) | Identity |
|---|---:|---:|---:|---:|---|---|
| F | 71.12  | 73.66  | 0.00    | 67.47 | 100 % fuel | Downcomer (salt annulus) |
| I | 70.485 | 71.12  | 0.00    | 65.53 | 100 % INOR-8 | **Core can** (0.25 in / 0.635 cm wall) |
| B | 73.66  | 75.08  | -9.14   | 74.92 | 100 % INOR-8 | Vessel side wall (0.56 in / 1.42 cm) |
| P | 0      | 73.66  | -9.14   | -1.41 | 90.8 % fuel / 9.2 % INOR-8 | **Bottom head mix** (already in v1c-lh) |
| K | 7.37   | 7.62   | -1.41   | 74.92 | 100 % INOR-8 | Simulated thimble annulus (homogenized) |

Key conclusions:
- **Core can: 70.485 cm ID, 71.12 cm OD, 0.635 cm wall, 166.45 cm height.**
- Salt gap between graphite outer (70.168 cm) and core can inner (70.485 cm) is only 0.317 cm — a thin film, neutronically negligible but the geometry needs to handle it.
- Vessel inner radius confirmed at 73.66 cm (29 in), wall 1.42 cm (0.56 in).
- Bottom head composition 90.8/9.2 confirmed exactly — step 1 lower-head mix is the right number.

## Control rod geometry (ORNL-TM-0728 §4.1, Shen Fig 2)

- **Poison cylinder: 1.08 in OD × 0.12 in wall = 2.743 cm OD, 0.305 cm wall, hollow.**
- Material: 70 wt % Gd2O3 + 30 wt % Al2O3 ceramic.
- INOR-8 thimble (clads the poison): individual thimble dimensions implied by the homogenized equivalent (6.00 in OD × 0.10 in thick annulus at r = 2.90-3.00 in homogenizes all three thimbles' INOR-8 mass + outside surface).
- **Three control rod thimbles + one graphite sample basket arranged as a 2×2 square array** centered on the reactor centerline (Fig 3.2, Shen Fig 2).
- Each array position occupies a full graphite-stringer lattice cell (5.08 cm pitch).
- Withdrawn z = 129.54 cm; inserted (criticality) z = 118.364 cm (4.4 in inserted).

## Sample basket geometry (Shen Fig 2)

- 3 sample baskets occupying the fourth position of the 2×2 array (same lattice cell as a control rod would).
- Per basket: 4 INOR-8 rods (0.635 cm dia) + 5 graphite bars (0.635 × 1.1938 cm).
- All three baskets sit inside one 5.08 cm lattice cell.

## What's still ambiguous

1. **2×2 array spacing**: 1 pitch (5.08 cm) vs 2 pitches (10.16 cm) center-to-center. Need higher-res view of Fig 3.2 or the IRPhE handbook.
2. **Sample basket axial extent**: estimate full active core height as first cut.
3. **Thimble extension above active core**: thimbles extend up to the access port; first cut, terminate at the upper plenum boundary.

None of these are blockers — reasonable defaults can land step 2 and step 3, and the dominant effect (presence vs absence) is captured.

---

## Geometry implementation sketch

```python
# Phase 1.1.c additions to build_geometry_het_clipped():

# 1. Core barrel — INOR-8 cylinder
core_barrel_or = ZCylinder(r=71.12)   # 142.24/2 cm
core_barrel_ir = ZCylinder(r=70.17)   # graphite core radius
core_barrel_cell = Cell(region=+core_barrel_ir & -core_barrel_or, fill=inor8)

# 2. Downcomer — fuel salt in annulus
vessel_ir = ZCylinder(r=73.66)        # 147.32/2 cm
downcomer_cell = Cell(region=+core_barrel_or & -vessel_ir, fill=fuel_salt)

# 3. Lower head — homogenized 85% salt + 15% INOR-8
lower_head_mix = Material()
lower_head_mix.add_mix(fuel_salt, 0.85, inor8, 0.15, frac_type='vo')
# bounded by vessel cylinder and z below core bottom

# 4. Sample baskets — 3 cylindrical regions near center
# Each basket homogenized as (4 INOR-8 rods + 5 graphite bars + salt)
# Approximated as small cylinders at TBD radial positions

# 5. Control rod thimbles — 3 vertical Inconel cylinders
# At equidistant radial positions ~half-radius from center
# Poison cylinder fills thimble from z=top down to:
#   rod 1:  z = 129.54 cm  (withdrawn)
#   rod 2:  z = 129.54 cm  (withdrawn)
#   rod 3:  z = 118.364 cm (inserted 4.4 in)
```

---

## Expected bias breakdown (revised)

| Step | Feature added | Estimated Δρ (pcm) | Cumulative k-eff |
|---|---|---|---|
| Phase 1.1.b het v1 | (baseline) | 0 | ~1.04-1.06 (TBD from 100k run) |
| Phase 1.1.c step 1 | + core barrel (INOR-8) | ~-300 to -600 (absorber + thinner salt downcomer) | — |
| Phase 1.1.c step 2 | + lower-head 15% INOR-8 mix | ~-100 to -300 (Yilmaz: "more than 100 pcm") | — |
| Phase 1.1.c step 3 | + sample baskets (INOR-8 + graphite) | ~-100 to -300 (small parasitic absorber) | — |
| Phase 1.1.c step 4 | + control rod thimbles (1 inserted 4.4 in) | ~-1000 to -1500 (Gd poison is strong) | — |
| Phase 1.1.c target | | total ~-2000 pcm | ~1.02-1.04 |

The control rod insertion dominates. Step 4 should be staged as two sub-cases:
- **4a**: All three rods fully withdrawn (poison absent from core) — small bias
- **4b**: One rod inserted 4.4 in (matches IRPhE criticality state) — full ~1.020 target

---

## Phase order

Recommend implementing in this order:
1. Core barrel + downcomer (cleanest geometry change, no new materials beyond INOR-8 already needed for Phase 1.1.c)
2. Lower-head mix (new material; well-defined)
3. Control rod thimbles, all withdrawn (4a) — adds Inconel and Gd2O3/Al2O3 materials, but no rod-in-core effect
4. Sample baskets (small effect, can be homogenized)
5. Control rod insertion (4b) — flip rod 3 to 118.364 cm, compare to 4a

Each step gets its own CI run. The branch concurrency pattern from 1.1.b still applies: develop on `phase-1.1.c` branch, merge to main one feature at a time once each stage is verified.
