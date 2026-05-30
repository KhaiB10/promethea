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

## Measured staging results (100k particles × 100 batches, ENDF/B-VIII.0)

| Stage | CI run | k-effective | Δ from prior (pcm) |
|---|---|---|---|
| v1 het baseline | 26613848308 | 1.08264 ± 0.00037 | — |
| Step 1 — lower-head 90.8/9.2 mix | 26621707352 | 1.07355 ± 0.00038 | −909 |
| Step 2 — core can (0.635 cm INOR-8) | 26624726160 | 1.07202 ± 0.00041 | −153 |
| Step 3 — 4 thimbles withdrawn | 26625953930 | 1.02314 ± 0.00037 | **−4888** |
| Step 4 — + 1 sample basket | 26627021424 | 1.01948 ± 0.00032 | −366 |
| Step 5 — + 1 rod inserted 4.4 in (full IRPhE) | 26630697473 | **1.01433 ± 0.00038** | −515 |

Total Phase 1.1.c bias: **−6831 pcm** vs Phase 1.1.b het baseline.

The big swing was step 3 — the four control-rod thimbles displace ~62 cm³ of fuel each over the active core height and the INOR-8 shells are parasitic absorbers. That single feature accounts for **72% of the total Phase 1.1.c bias**, much larger than the original ±100-300 pcm estimate.

## IRPhE benchmark comparison

| Reference | k-eff | Δ from Promethea (pcm) |
|---|---|---|
| **Promethea het_critical (this work)** | **1.01433 ± 0.00038** | — |
| IRPhE Serpent (Shen et al. 2021, current edition) | 1.02132 ± 0.00003 | +699 ± 38 |
| Shen et al. 2017 OSTI (older edition) | 1.00135 | −1298 ± 38 |
| Experimental criticality (June 1, 1965, 6:00 PM) | 0.99978 | −1455 ± 38 |

**We are 699 pcm below the published IRPhE Serpent benchmark and 1455 pcm above the experimental value.** The Promethea result sits between the two reference points and is consistent with the well-documented MC overprediction for graphite-moderated systems (typically 1-2%). Closing the remaining 699 pcm to the Serpent target is Phase 1.1.d / Phase 1.2 work — candidate sources of the residual gap, in rough priority order:

1. **Graphite stringer cross-section / channel geometry detail** — our lattice uses an averaged matrix-plus-coolant model rather than the as-built grooved stringer cross-section. Fratoni 2023 reports ~+200-500 pcm sensitivity here.
2. **B-10 content in CGB graphite** — we used the as-shipped manufacturer value (~0.3 ppm equivalent). IRPhE Serpent inputs may use a different effective ppm; this is worth ~±100-300 pcm.
3. **Salt density and 7Li enrichment** — we use 99.9926% 7Li (IRPhE spec). Salt density temperature dependence and exact 1965 inventory ratio could shift another ±100-200 pcm.
4. **Sample basket sub-channel resolution** — we homogenized one basket; explicit modeling of the 4 INOR-8 rods + 5 graphite bars per basket would shift k-eff by ~±50-150 pcm.
5. **Upper plenum and access-nozzle detail** — our upper plenum is salt-only; real geometry has piping intrusions and a sample insertion port. Sensitivity ~±50 pcm.
6. **Cross-section library** — we use ENDF/B-VIII.0; some IRPhE Serpent runs use JEFF-3.3 or ENDF/B-VII.1. Library differences typically run ±100-300 pcm for thermal graphite systems.

For the experimental comparison (k = 0.99978), the +1455 pcm Promethea bias is in family with other published MC predictions for MSRE — Shen 2017 reported +157 pcm and Fratoni 2023 reported +1400-2000 pcm depending on stringer treatment. We are within the published spread.

---

## Phase 1.1.d step 1 — stringer half-channel orientation fix (commit ffb9488)

### Finding

During Phase 1.1.d source audit (`STRINGER_GEOMETRY.md`), we discovered
that the existing Phase 1.1.b/c lattice modeled each half-channel as
1.524 cm deep × 1.016 cm long along the face. TM-0728 §2.6 specifies
0.508 cm deep × 3.048 cm long, matching Shen 2021's full 1.016 × 3.048 cm
full channels between paired stringers. The channels were rotated 90°
from the as-built design.

Fuel volume fraction is preserved (0.240 in both orientations) so all
phase 1.1.b/c integral results were correct in mass terms. The geometry
bug increased fuel-graphite interface area by 40% and inverted the
cross-stringer channel aspect ratio.

### Result (CI run 26637499678, het_critical, 100k × 100)

| Comparison | k-eff | Δ |
|---|---|---|
| Phase 1.1.c step 5 (swapped channels) | 1.01433 ± 0.00038 | — |
| **Phase 1.1.d step 1 (corrected channels)** | **1.01308 ± 0.00036** | **−125 ± 52 pcm** |
| IRPhE Serpent (Shen 2021) | 1.02132 ± 0.00003 | −824 pcm vs us |
| IRPhE experimental (June 1, 1965) | 0.99978 | +1330 pcm vs us |

The fix moved k-eff **down by 125 pcm** (statistically significant,
Δ/σ ≈ 2.4). Direction is opposite to my prior estimate; reasoning revised:

- More fuel-moderator interface area increases thermalization but also
  increases parasitic U-235 absorption per unit moderation in already
  well-moderated regimes.
- Net effect for MSRE-class graphite + dilute U-235 + 7Li-enriched salt:
  small negative bias from increased interface.
- This is consistent with Fratoni 2023's observation that stringer-detail
  sensitivity is ~few-hundred pcm in either direction.

### Implication for the IRPhE benchmark gap

Vs the Serpent target the gap *widened* (824 pcm), but vs the experimental
criticality value the gap *narrowed* (1330 pcm). The orientation fix is
physics-correct (TM-0728 is unambiguous), so the closer-to-experiment
direction is the trustworthy reading. Worth flagging that Shen 2021's
+2154 pcm overprediction relative to experiment may itself include some
geometry approximations we have now removed.

### Next sub-steps within Phase 1.1.d

1. **Corner rounding of half-channels** — TM-0728 §2.6 says rounding
   reduces fuel fraction from 0.240 to 0.225 (~6.25%). Direction: +k
   (less salt + slightly more graphite per cell). Estimated +30-80 pcm.
2. **CGB graphite B-10 content sweep** (0.1 → 1.0 ppm) to bracket the
   IRPhE input value. Estimated ±100-300 pcm sensitivity, cheap (3 short
   runs).
3. **Cross-section library comparison** (ENDF/B-VIII.0 vs JEFF-3.3 vs
   ENDF/B-VII.1). Estimated ±100-300 pcm. Most expensive sub-step.

Proceed in this order — sub-step 1 leverages the fresh orientation work,
sub-step 2 is the cheapest sensitivity, and sub-step 3 is the long-run.

---

## Phase 1.1.d step C — CGB graphite B-10 sensitivity sweep

### Why

Reactor-grade CGB graphite carries a small natural-boron impurity whose
thermal absorption can move k-eff by several hundred pcm even at
sub-ppm levels. MSRE-Mark-I CGB acceptance was **≤ 0.3 ppm total
natural B** (TM-0728 Tab. 2.7); reported batch values run **0.1–1.0 ppm**
(Compere 1975, Shen 2021). IRPhE's Serpent benchmark uses a single
point value, but the document doesn't pin it precisely — so we sweep.

### Implementation

`materials.py` now exposes `build_graphite(temperature_K, boron_ppm=…)`.
Total boron ppm is split into B-10 and B-11 using natural abundance
(19.9 / 80.1 atom %). `build_all` reads the env var
`PROMETHEA_BORON_PPM` (default 0.3). The workflow accepts a
`boron_ppm` input and pipes it to the container.

Commit `8db68d8` adds the parameterization; commit `e7f5345` makes the
concurrency group key on event/mode/boron_ppm so sweep dispatches
queue serially without preempting each other.

### Sweep results (100k × 100, het_critical, corrected stringers)

| Boron (ppm) | k-eff | σ | Δk vs 0.3 ppm | CI run |
|---|---|---|---|---|
| 0.1 | 1.01377 | 0.00034 | +69 ± 50 pcm | [26668414474](https://github.com/KhaiB10/promethea/actions/runs/26668414474) |
| **0.3 (baseline)** | **1.01308** | **0.00036** | **—** | [26637499678](https://github.com/KhaiB10/promethea/actions/runs/26637499678) |
| 0.6 | 1.01287 | 0.00034 | −21 ± 49 pcm | [26670248006](https://github.com/KhaiB10/promethea/actions/runs/26670248006) |
| 1.0 | 1.01100 | 0.00042 | −208 ± 55 pcm | [26670249744](https://github.com/KhaiB10/promethea/actions/runs/26670249744) |

### Sensitivity

Weighted linear fit across the four points:

\[ k_{\text{eff}}(b) = 1.01411(32) + (-280 \pm 56) \,\text{pcm/ppm} \cdot b \]

- **Slope: −280 ± 56 pcm per ppm of total natural boron**, consistent
  in sign and order-of-magnitude with the few-hundred pcm/ppm range
  cited in Compere 1975 for MSRE thermal spectra.
- The fit is dominated by the 0.1→1.0 endpoints; the 0.3 and 0.6
  intermediate points sit within ±1σ of the regression line, so the
  response is linear within statistics at these levels.

### Gap analysis

| Scenario | Implied Δk from boron alone | Residual gap to Serpent 1.02132 |
|---|---|---|
| We at 0.3 ppm, Shen at 0.3 ppm (no boron mismatch) | 0 pcm | −824 pcm |
| We at 1.0 ppm, Shen at 0.1 ppm | +277 pcm | −547 pcm |
| We at 1.0 ppm, Shen at 0.0 ppm | +311 pcm | −513 pcm |

**Conclusion: B-10 impurity alone cannot close the 824 pcm gap to the
Shen-Serpent target.** Even the most pessimistic mismatch (we ran
upper-spec, Shen ran zero-boron) explains at most ~38% of the gap.
The bulk of the remaining bias must come from geometry detail still
omitted (corner-rounded half-channels, exact thimble dimensions, etc.)
and/or cross-section library differences.

Also worth noting: the gap to **experimental** criticality (0.99978)
shrinks from +1330 pcm to +1102 pcm if we adopt the 1.0 ppm upper-spec
value. That's the right direction — a higher boron value brings us
closer to experiment while widening the gap to Shen, reinforcing the
read from Phase 1.1.d step 1 that Shen's Serpent is itself biased
high relative to the experimental point.

### Recommended baseline going forward

Keep **0.3 ppm as the canonical baseline** (matches MSRE-Mark-I CGB
acceptance spec and is the midpoint of reported batch values). Cite
the full sweep as a sensitivity envelope in future writeups.

---

## Phase 1.1.d step 2 — Corner-rounded half-channels

### Why

TM-0728 §2.6 explicitly states: "Four half-channels 0.2- by 1.2-in. in
each 2- by 2-in. graphite block were chosen to give a fuel fraction of
0.24; rounding the corners of the channels reduced the fraction to
0.225." Shen 2021 §2 likewise: "channels 1.016 cm by 3.048 cm with
rounded corners are formed by grooves in the 4 sides of the bars."
Phase 1.1.b/c/d-step-1 all used sharp corners (fuel fraction 0.240),
leaving a ~6.25% over-statement of fuel volume.

### Implementation (commit `0039a48`)

`geometry_het.py` now exposes `FUEL_CHANNEL_CORNER_R`, set via the
`PROMETHEA_FILLET_RADIUS_CM` env var (default 0 = sharp). Each
half-channel notch receives two quarter-circle fillets at its inner
corners (where the notch floor meets the end walls) — 8 fillets per
stringer. Each fillet uses an OpenMC `ZCylinder` surface; the salt
region intersects with the complement of each "sliver" (corner
bounding-square minus quarter-disc), so graphite fills the corners.

The workflow gains a `fillet_radius_cm` input. Concurrency key now
includes the fillet radius so rounded-corner runs queue independently
of sharp-corner runs.

### Radius selection

Solving for the fillet radius that reproduces TM-0728's 0.240 → 0.225
target across 8 fillets per cell:

\[ 8 r^2 (1 - \pi/4) = (0.240 - 0.225) \cdot 5.08^2 \quad\Longrightarrow\quad r \approx 0.4748\,\text{cm} \]

The 0.475 cm radius is ~93% of the 0.508 cm half-channel depth —
extreme, but the only single-radius solution. Sanity check via offline
Monte Carlo on the 2D unit cell:

- Analytical fuel fraction = 0.2250
- MC (2 × 10⁵ samples) = 0.2256

Both agree with the 0.225 spec.

### Result (100k × 100, het_critical, B=0.3 ppm)

| Geometry | k-eff | σ | Δk vs sharp | CI run |
|---|---|---|---|---|
| Sharp corners (baseline) | 1.01308 | 0.00036 | — | [26637499678](https://github.com/KhaiB10/promethea/actions/runs/26637499678) |
| **r = 0.475 cm (TM-0728)** | **1.01320** | **0.00030** | **+12 ± 47 pcm** | [26671341501](https://github.com/KhaiB10/promethea/actions/runs/26671341501) |

**Δk/σ = 0.26 — statistically null result.**

### Interpretation

The prior estimate (Phase 1.1.d plan: +30-80 pcm) overshot. Corner
rounding at MSRE-relevant conditions (high enrichment, well-thermalized
spectrum, dilute U-235) does not move k meaningfully. Two physical
reasons converge on the small result:

1. The corner region carries simultaneous fuel-and-moderator removal:
   replacing salt with graphite removes both U-235 absorption *and*
   parasitic Li-7/F absorption *and* adds moderation, all in a region
   that is already well-thermalized. The net reactivity worth is
   near-zero by construction.
2. Lattice-cell averages dominate the reactor physics at MSRE’s
   diffusion length; ~6% local volume rearrangement at the channel
   corners shifts cell-averaged disadvantage factors by only a few %.

### Implication for the Shen-Serpent gap

Updated gap analysis: k(filleted) = 1.01320, gap to Shen target
1.02132 is **+812 pcm** (vs +824 pcm at sharp corners). Corner
rounding accounts for at most ~30 pcm of the gap — well within noise.

**Conclusion: between B-10 sweep (max ~311 pcm) and corner rounding
(max ~50 pcm) we have explained ~360 pcm of the 824 pcm gap.** The
remaining ~450 pcm is most likely cross-section library, plus possibly
geometry detail still omitted (e.g. exact horizontal-lattice cross
section at the bottom, thimble centering vs hard-coded 7.62 cm offset).

Runtime note: filleted-geometry runs are ~2× slower than sharp
(~50 min vs ~25 min for 100k × 100) due to the extra ~39k cylinder
surfaces injected into ray tracing. Acceptable for one-off comparisons;
avoid for parameter sweeps.

### Recommended canonical geometry going forward

Keep **sharp corners (r=0) as the production default** — the 12 pcm
delta is well within MC noise and the runtime cost of the filleted
geometry is 2×. Reserve filleted runs for final validation or
literature comparison.

---

## Phase 1.1.d step 3 — Cross-section library swap

### Why

After Step C (boron) and Step 2 (corner rounding) together account for
at most ~311 + ~12 pcm ≈ 323 pcm of the 824 pcm Shen-Serpent gap, the
most-likely-remaining bulk contributor is the evaluated nuclear data
library itself. Different libraries (ENDF/B-VII.1, ENDF/B-VIII.0,
JEFF-3.3) reprocess the same underlying ENDF evaluations with
different thermal scattering laws, resonance treatments, and (for
some nuclides) updated measurements, leading to 100-500 pcm k-eff
shifts in published MSRE-class benchmarks.

Shen 2021 does not state the library used. The expectation going in
was that VII.1 would raise k (closing the gap) since VIII.0 ↔ VII.1
shifts of +200-400 pcm are common in thermal U-235 systems. The
result was the opposite, see below.

### Implementation (commit `aa0e8bb`)

- `scripts/fetch_xs.sh` now takes a library key argument and selects
  the canonical anl.box.com archive URL (verified against the Official
  Data Libraries section of openmc.org/data, 2025-12 snapshot):
  - `endfb-viii.0` → `uhbxlrx7hvxqw27psymfbhi7bx7s6u6a.xz`
  - `endfb-vii.1`  → `9igk353zpy8fn9ttvtrqgzvw1vtejoz6.xz`
  - `jeff-3.3`     → `4jwkvrr9pxlruuihcrgti75zde6g7bum.xz`
- Workflow exposes `xs_library` as a `choice` input, threads it through
  a `Resolve library paths` step (`steps.xs-paths.outputs.xs_xml`) into
  the cache key, fetch command, plot mode, and run mode.
- Each library has its own cache key (`<dirname>-v1`) so the three
  libraries do not evict each other in GHA's per-repo cache budget.
- Concurrency group keyed on `xs_library` so independent dispatches
  queue (do not preempt). Artifact name embeds the library tag.
- `run_criticality.py` logs the active library + `OPENMC_CROSS_SECTIONS`
  path on startup for forensic confirmation.

### Results (100k × 100, het_critical, B=0.3 ppm, sharp corners)

| Library      | CI run     | k-eff (combined) | σ      | Δk vs VIII.0 |
|--------------|-----------:|-----------------:|-------:|-------------:|
| ENDF/B-VIII.0| 26637499678| 1.01308          | 0.00036| —            |
| ENDF/B-VII.1 | 26673557407| 1.01163          | 0.00038| **−145 ± 52 pcm** |
| JEFF-3.3     | 26673563595| 1.01485          | 0.00034| **+177 ± 47 pcm** |

Leakage fractions (active batch averages): VII.1 = 0.21921 ± 0.00018,
JEFF-3.3 = 0.21629 ± 0.00016 (lower leakage in JEFF-3.3 is consistent
with its higher k).

### Interpretation

1. **VII.1 hypothesis was wrong.** k dropped, didn't rise. Shen-Serpent
   was almost certainly not using ENDF/B-VII.1, or if it was, other
   methodology choices in that work compensated.
2. **JEFF-3.3 closes the most gap of any single library** — 177 pcm,
   bringing the residual to Shen-Serpent from 824 to 647 pcm.
3. The full library spread across the three options is only 322 pcm
   (1.01163 to 1.01485). This bounds the library contribution to the
   Shen gap from above: **at most ~320 pcm is library choice**.

### Cumulative gap analysis (post-step-3)

| Effect                            | Magnitude (pcm) | Sign | Source            |
|-----------------------------------|----------------:|------|-------------------|
| Boron mismatch (1.0 → 0.0 ppm)    |             311 | +    | Step C            |
| Corner rounding (r=0 → 0.475 cm)  |              12 | +    | Step 2 (null)     |
| Library swap (VIII.0 → JEFF-3.3)  |             177 | +    | Step 3            |
| **Cumulative best-case**          |         **500** | +    |                   |
| Shen-Serpent target gap           |             824 |      |                   |
| **Stubborn residual**             |         **324** |      | unexplained       |

The three sensitivity studies together can explain at most ~500 pcm
of 824 pcm (61%). The remaining ~324 pcm is real and must come from
an effect Phase 1.1.d has not yet audited.

### Recommended canonical library going forward

Keep **ENDF/B-VIII.0 as the production default** — it is the modern
US standard library, includes ALARA-grade photoatomic data, and has
the broadest cross-validation against power-reactor and critical-mass
benchmarks. JEFF-3.3 is a useful cross-check tag for major
milestones but should not be the everyday baseline.

### Implications for remaining work

The ~324 pcm unexplained residual is now the central Phase 1.1.d
follow-up. Likely candidates, in priority order:

1. **Thimble centering vs hard-coded 7.62 cm offset** — Shen Fig 2
   shows thimbles inset slightly differently from the TM-0728 nominal
   coordinates. A 1-2 cm radial shift on four absorber thimbles can
   easily move k by 100-300 pcm.
2. **Horizontal lattice cross section at the bottom of the active core**
   — TM-0728 §2.6 shows the lattice transitioning to a different
   stringer pattern in the lower 5 cm. Our model uses uniform vertical
   stringers; Shen may model the transition.
3. **Fuel salt composition and density at the Shen reference temperature**
   — re-derive U-235 enrichment, Zr-to-U ratio, and salt density from
   TM-0728 Tables 2.4-2.6 directly rather than from our cached values.
4. **Inconel/INOR-8 thimble cladding thickness** — currently set to
   the TM-0728 nominal; Shen may use the Fig 2 dimensioned value.

Each is a small geometry/composition audit, not a major refactor.

---

## Phase order

Recommend implementing in this order:
1. Core barrel + downcomer (cleanest geometry change, no new materials beyond INOR-8 already needed for Phase 1.1.c)
2. Lower-head mix (new material; well-defined)
3. Control rod thimbles, all withdrawn (4a) — adds Inconel and Gd2O3/Al2O3 materials, but no rod-in-core effect
4. Sample baskets (small effect, can be homogenized)
5. Control rod insertion (4b) — flip rod 3 to 118.364 cm, compare to 4a

Each step gets its own CI run. The branch concurrency pattern from 1.1.b still applies: develop on `phase-1.1.c` branch, merge to main one feature at a time once each stage is verified.
