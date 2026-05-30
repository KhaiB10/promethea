# MSRE graphite stringer geometry — primary-source audit

**Phase**: 1.1.d step 1
**Status**: Design audit, pre-implementation
**Author**: Promethea team, 2026-05-29

---

## 1. Canonical dimensions

The MSRE active-core moderator is an array of vertical graphite stringers
arranged on a square lattice. Each stringer is a square cross-section bar
with grooves machined into the centerline of all four faces. Adjacent
stringers face each other so that two opposing grooves form a full fuel
channel.

### TM-730 Section 2.6 (Haubenreich et al. 1964, ORNL-TM-730, p. 14)

> "Four half-channels 0.2- by 1.2-in. in each 2- by 2-in. graphite block were
> chosen to give a fuel fraction of 0.24; rounding the corners of the
> channels reduced the fraction to 0.225."

### TM-730 Section 3.1 (p. 15)

> "The channeled region of the core consists of 2-in.-square, vertical
> graphite stringers, with half-channels machined in each face to provide
> fuel passages."

### Shen et al. 2021 (OSTI 1413611, p. 4)

> "The vertical graphite matrix is an assembly of vertical bars whose
> horizontal cross section is a square with a side length of 5.08 cm.
> Channels 1.016 cm by 3.048 cm with rounded corners are formed by grooves
> in the 4 sides of the bars."

## 2. Numerical values (cm)

| Quantity | Imperial | SI | Source |
|---|---|---|---|
| Stringer side length | 2.0 in | **5.08 cm** | TM-730 §3.1, Shen 2021 |
| Stringer pitch (square lattice) | 2.0 in | **5.08 cm** | TM-730 §3.1 |
| Half-channel depth into stringer | 0.2 in | **0.508 cm** | TM-730 §2.6 |
| Half-channel length along face | 1.2 in | **3.048 cm** | TM-730 §2.6 |
| Full channel width (between paired stringers) | 0.4 in | **1.016 cm** | TM-730 §2.6, Shen 2021 |
| Full channel length | 1.2 in | **3.048 cm** | TM-730 §2.6, Shen 2021 |
| Fuel volume fraction (sharp corners) | — | **0.240** | TM-730 §2.6 |
| Fuel volume fraction (rounded corners, as-built) | — | **0.225** | TM-730 §2.6 |
| Active core height | 65.53 in | **166.45 cm** | TM-730 Table 3.1 |

## 3. Cross-section sketch (looking down a single stringer)

```
                  +Y
                   |
     +---------+---------+----+
     |         |  notch  |    |
     |         | 3.048   |    |        Channel orientation:
     |         |  long   |    |        - 0.508 cm deep INTO stringer
     |         |  0.508  |    |        - 3.048 cm long ALONG the face
     |         |   deep  |    |
+----+         +----+----+    +----+
|notch|              |             |
|3.048|              |             |
|long |              |  graphite   |   --- +X
|0.508|              |  body       |
|deep |              |             |
+----+         +----+----+    +----+
     |         |   deep  |    |
     |         |  0.508  |    |
     |         |  long   |    |
     |         | 3.048   |    |
     |         |  notch  |    |
     +---------+---------+----+
                   |
                  -Y
```

Each face has ONE notch. The 0.508 cm dimension is the depth *into* the
stringer (perpendicular to the face). The 3.048 cm dimension is the length
*along* the face (parallel to the face), centered on the face midpoint.

When two stringers are adjacent in +X, their facing notches combine into a
full 1.016 cm wide × 3.048 cm long fuel channel that spans both stringers'
notch depth (0.508 + 0.508 = 1.016 cm).

## 4. Existing implementation (Phase 1.1.b/c) — bug discovered

The current `_build_stringer_universe` in `geometry_het.py` defines:

```python
FUEL_CHANNEL_WIDTH  = 1.016         # half-groove width on each face
FUEL_CHANNEL_DEPTH  = 3.048 / 2.0   # half-groove depth (1.524 cm into each stringer)
```

with the +X face notch defined as the region

```
x > (half_pitch - notch_depth) = 2.540 - 1.524 = 1.016
AND  -0.508 < y < +0.508
```

This makes each notch **1.524 cm deep × 1.016 cm long**, which is the
correct channel dimensions **rotated 90°**. The depth and the along-face
length have been swapped relative to TM-730.

### Effect on fuel volume fraction

Per stringer:
- 4 notches × (1.524 × 1.016) = 6.194 cm² (current code)
- 4 notches × (0.508 × 3.048) = 6.194 cm² (correct geometry)
- Stringer cell area: 5.08² = 25.806 cm²
- Fuel fraction: 0.240 in both cases ✓

Fuel and graphite mass are correct. The bug is purely geometric.

### Effect on channel-graphite surface area

Channel perimeter (one notch):
- Current code: 2 × (1.524 + 1.016) = 5.080 cm
- Correct: 2 × (0.508 + 3.048) = 7.112 cm

Per stringer cell, the salt-graphite interface increases from 4 × 5.080 =
20.32 cm to 4 × 7.112 = 28.45 cm, a **40% increase in fuel-moderator
interface area**.

### Effect on channel-channel coupling between adjacent stringers

In the correct geometry, two adjacent stringers facing each other in +X
form a single 1.016 × 3.048 cm rectangular channel that extends a total
of 1.016 cm in the X direction (0.508 cm into each stringer). The channel
runs 3.048 cm in Y, centered on the stringer face midpoint.

In the current (buggy) code, two adjacent stringers form a 2.032 × 1.016 cm
channel: 2 × 1.524 = 3.048 cm in X (way deeper than physical), but only
1.016 cm in Y. The channel is rotated and the fuel slab between adjacent
stringers is much thicker and shorter than it should be.

## 5. Expected reactivity impact of the fix

Going from the current swapped geometry to the correct geometry:
- **Same fuel and graphite masses** (volumes preserved)
- **More fuel-moderator interface area** (+40%)
- **Thinner fuel slabs between adjacent stringers** (channel is 1.016 cm
  wide vs 2.032 cm in current code) — less self-shielding in salt, more
  thermal flux peaking in moderator preferentially absorbed by fuel
- Higher disadvantage factor for U-235; less U-238 / Th-232 epithermal
  capture per unit fuel

Direction: **+ k-eff** (small positive). Magnitude estimate from MSRE
literature for the channel-orientation effect alone is hard to bracket
exactly, but bounded by the total stringer-detail sensitivity reported by
Fratoni 2023 of ~+200-500 pcm.

## 6. Corner rounding (separate sub-step)

The TM-730 design rounds the channel corners to convert the 0.24 sharp-
corner fuel fraction to 0.225 as-built. That's a 6.25% reduction in fuel
volume. Round corners can be modeled in OpenMC as a fillet between the
two perpendicular notch surfaces, but native OpenMC primitives don't
support fillets directly. Three options:

1. **Approximate rounded corners with cylinders** at each of the four
   inside corners of each notch. Each notch has four corners; the fillet
   radius needed to drop fuel fraction from 0.24 to 0.225 in a 0.508 ×
   3.048 cm rectangle is r = 0.179 cm (matches a typical machinable
   fillet ~0.07 in).
2. **Reduce the channel rectangle** to 0.508 × 2.857 cm (= 0.225/0.240 ×
   3.048). This preserves fuel volume fraction without modeling rounding
   geometry. Rough but fast.
3. **Skip corner rounding** and accept the 0.24 fuel fraction. Simplest;
   adds ~+50 pcm vs the as-built 0.225 fraction, which is small relative
   to the swapped-orientation fix.

Plan: implement **option 1** (proper fillets) as a follow-on if the
corrected sharp-corner geometry overshoots the IRPhE Serpent target. If
sharp corners undershoot, use option 3.

## 7. Implementation plan for the fix

1. Rename `FUEL_CHANNEL_WIDTH` → `FUEL_CHANNEL_LENGTH` (3.048 cm).
2. Rename `FUEL_CHANNEL_DEPTH` → `FUEL_CHANNEL_DEPTH` (0.508 cm) — keep the
   name but change the value.
3. Update `_build_stringer_universe`:
   - +X face notch: `x > 2.54 − 0.508 = 2.032` AND `−1.524 < y < +1.524`
   - −X face notch: `x < −2.032` AND `−1.524 < y < +1.524`
   - +Y face notch: `−1.524 < x < +1.524` AND `y > +2.032`
   - −Y face notch: `−1.524 < x < +1.524` AND `y < −2.032`
4. Run unit-cell volume check: confirm fuel fraction = 0.240.
5. Shakedown run at 10k × 50 to verify no overlaps, no lost particles.
6. Production run at 100k × 100 → compare to step 5 baseline (1.01433).
7. If overshoots Serpent target (1.02132), add corner rounding (option 1).
   If undershoots, document and proceed to Phase 1.1.d step 2.

## 8. Confidence and verification checklist

- [x] Stringer side and pitch verified against TM-730 §3.1 and Shen 2021
- [x] Half-channel depth and length verified against TM-730 §2.6
- [x] Full channel cross-section verified against Shen 2021 explicit
      "1.016 cm by 3.048 cm"
- [x] Sharp-corner fuel fraction algebra verified: 4 × 0.508 × 3.048 /
      5.08² = 0.240 ✓
- [x] Existing code re-read; orientation bug confirmed against canonical
      geometry
- [ ] Pin-cell mass verification after fix (done in implementation step 4)
- [ ] No-overlap, no-lost-particles confirmation (done in step 5)

## 9. References

1. Robertson, R. C. (1965). *MSRE Design and Operations Report Part I:
   Description of Reactor Design.* ORNL-TM-730. §2.6, §3.1, Table 3.1.
   https://www.osti.gov/servlets/purl/4114686
2. Shen, D. et al. (2017, 2021). *Molten-Salt Reactor Experiment (MSRE)
   Zero-Power First Critical Experiment with U-235.* IRPhE benchmark,
   OSTI 1413611. https://www.osti.gov/servlets/purl/1413611
3. Yilmaz, T. (2024). MSRE benchmark with OpenMC. *Frontiers in Nuclear
   Engineering* 3:1385478.
4. Fratoni, M. (2023). *MSRE benchmark sensitivities.* MSR Workshop 2023,
   Session 5.
   https://msrworkshop2023.ornl.gov/wp-content/uploads/2016/09/presentation-session-5-Fratoni.pdf
