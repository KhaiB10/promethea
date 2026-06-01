# Promethea v0.4.0 — MSBR Two-Fluid Scope

**Status:** drafted 2026-06-01, supersedes V0_4_0_SCOPE.md (S/U vs CAD decision)
**Target window:** 2026-Q3/Q4 (after v0.3.0 closes seed envelope + rounded-corner work)

---

## Why this document exists

The original v0.4.0 scope (TSUNAMI S/U vs CAD migration) recommended
Option 1 (S/U) as a polish step on the existing MSRE benchmark. That
recommendation is now superseded.

The pivot: after v0.3.0 ships the Romano co-authorship paper, the MSRE
work is methodologically complete. Continuing to polish MSRE is
diminishing returns. The next-order question — and the one no public
open-source project has answered — is **the Molten-Salt Breeder Reactor**.

MSBR refers to a family of ORNL conceptual designs (~1000 MWe class,
Th-U breeder). Two distinct variants exist in the primary literature:

- **Two-fluid MSBR** (ORNL-4528, Robertson/Briggs/Smith/Bettis, 1968):
  separate fuel and blanket salts in interpenetrating graphite
  channels. Higher theoretical breeding ratio but ORNL ultimately
  abandoned this variant because the two-fluid graphite element
  fabrication was judged impractical at the time.
- **Single-fluid MSBR** (ORNL-4541, Robertson, 1971): combined fissile
  and fertile in one salt. ORNL's final recommended design. Lower
  breeding ratio but mechanically tractable.

**v0.4.0 targets the two-fluid variant (ORNL-4528).** Rationale: the
single-fluid design has been recomputed openly several times (it is
essentially "a different MSRE"); the two-fluid graphite-element
neutronics has not. Modeling the abandoned variant openly is the
uniquely useful contribution — it lets the community ask, with modern
tools, whether the 1968 fabrication concern is the true limit on
breeding performance, or whether the physics case for the two-fluid
layout deserves a second look.

No public, CI-validated two-fluid MSBR neutronics model exists
anywhere. Promethea v0.4.0 will be the first.

---

## Why two-fluid first (not single-fluid)

Two paths were considered:

**Option A: single-fluid MSBR snapshot first** — simpler geometry,
faster to a k-eff number, validates pipeline before adding complexity.

**Option B (chosen): two-fluid from the start** — harder, slower, but
this is the geometry that *defines* MSBR. A single-fluid MSBR model
is just "a different MSRE." Only the two-fluid configuration carries
the breeding-ratio physics that makes MSBR scientifically interesting.

Rationale for B: the open-source niche we are filling is "MSBR as
designed, openly verifiable." Shipping a single-fluid placeholder
muddies the contribution. Better to take longer and ship the real
thing.

---

## Scope: what v0.4.0 ships

### Core deliverable
Static, beginning-of-life (BOL), two-fluid MSBR k-eff and breeding
ratio model, validated against Robertson 1971 design values within
documented uncertainty bands.

### Geometry (the hard part)
- Inner fuel salt region: LiF-BeF2-UF4-ThF4 (fissile, no Th)
- Graphite moderator with two-fluid passages (fuel channels + blanket channels)
- Outer blanket salt region: LiF-BeF2-ThF4 (fertile, no U)
- INOR-8 / Hastelloy-N structural envelope
- Reflector and vessel per ORNL-4541 Chapter 3

The graphite element design is the novel CSG work. MSRE was single
stringer with uniform passage. MSBR has interpenetrating fuel and
blanket flow channels through the same graphite block. CSG
representation will require a unit-cell repeating pattern, similar
to MSRE basket but more complex.

### Physics targets
- k-eff at BOL ± documented uncertainty
- Breeding ratio (fissile produced / fissile consumed at BOL)
- Power density distribution (radial + axial)
- Fuel salt vs blanket salt fluence split

### Validation targets (revised 2026-06-01 after literature survey)

**Primary:** Robertson/Briggs/Smith/Bettis 1968 ORNL-4528 design values: k-eff, BR

**Independent recomputes available for cross-validation:**
1. Singh/Lish/Chvála/Upadhyaya 2017 (Nuclear Engineering and Technology, DOI 10.1016/J.NET.2017.06.003) — dynamic model "revised to accurately reflect the design exemplified in ORNL-4528"
2. Singh/Lish/Wheeler/Chvála/Upadhyaya 2018 (Nuclear Technology, DOI 10.1080/00295450.2017.1416879) — expanded dynamic modeling and performance analysis
3. Nezhad et al. 2022 MSiBR (Annals of Nuclear Energy) — thorium-fueled two-fluid molten-salt iso-breeder "similar to the two-fluid MSBR documented in ORNL-4528"
4. Feng/Cao/Davidson/Betzler 2021 (ANL+ORNL, OSTI 1826364) — Shift code applied to detailed MSBR model with explicit geometries
5. Kasten/Bettis et al. 1969 (Nuclear Engineering and Design, DOI 10.1016/0029-5493(69)90057-0) — graphite behavior and MSBR performance, contemporary recompute work

**Acceptable agreement bands:**
- k-eff: ±500 pcm vs ORNL-4528 design value
- BR: ±0.02 vs ORNL-4528 design value
- Cross-check: agreement with Singh/Chvála dynamic-model BOL state within same bands

### Explicit non-goals for v0.4.0
- **No continuous reprocessing.** BOL snapshot only. Pa-233 removal,
  online fission product extraction, U-233 isolation chemistry — all
  deferred to v0.5.0+.
- **No depletion / burnup.** Static composition.
- **No thermal-hydraulics coupling.** Fixed temperatures from
  ORNL-4541 nominal operating conditions.
- **No safety analysis.** k-eff and BR are the only physics outputs.

---

## Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| Two-fluid CSG geometry too complex for unit-cell approach | High | Prototype on simplified 2D slice first; consult Erik Knudsen (CAD_to_OpenMC) if blocked |
| No experimental benchmark for ground truth | Medium | Document explicitly; validation is "agreement with published calculations" not "agreement with measurement" |
| Robertson 1971 cross-section libraries not available openly | Medium | Use ENDF/B-VIII.0 + VII.1 as in MSRE work; document library-shift sensitivity |
| Breeding ratio is more sensitive to library choice than k-eff | Medium | S/U analysis on BR is a v0.5.0 item; v0.4.0 just reports point value with library variance |
| Scope blowout if continuous reprocessing creep | High | Hard line: BOL snapshot only. Reprocessing = v0.5.0 explicit milestone |

---

## Sequencing relative to existing roadmap

- **v0.3.0 (in progress):** seed envelope + rounded-corner f=0.225 → Romano paper. **Ships first, no change.**
- **v0.4.0 (this doc):** MSBR two-fluid BOL k-eff + BR
- **v0.5.0:** MSBR depletion + Pa-233 removal model
- **v0.6.0:** MSBR thermal-hydraulics coupling (deferred from MSRE)

The S/U vs CAD migration question is **not abandoned** — it returns as a
tooling decision when v0.4.0 geometry forces the issue. CAD-based
geometry (via Erik Knudsen's CAD_to_OpenMC) may become necessary
if the two-fluid graphite element exceeds practical CSG complexity.
That decision is made *during* v0.4.0 prototyping, not in advance.

---

## Co-author implications

- **Romano (Argonne):** v0.3.0 paper proceeds as planned. v0.4.0 is
  separate work, separate paper.
- **Chierici (Copenhagen Atomics):** MSBR work is squarely in their
  domain. Outreach order may shift — Chierici becomes a stronger
  v0.4.0 collaboration candidate than v0.3.0.
- **Knudsen (Copenhagen Atomics, CAD_to_OpenMC):** reserved for v0.5.0
  in prior dossier; may pull forward to v0.4.0 if CSG hits its limit.

---

## Success criteria

v0.4.0 ships when:
1. Two-fluid MSBR geometry runs end-to-end in CI on free GitHub runner
2. k-eff and BR reported with documented uncertainty
3. Validation table comparing Promethea numbers to Robertson 1971 + ≥1 recompute
4. PHASE_2_PLAN.md or equivalent committed for v0.5.0 reprocessing work
5. Tagged v0.4.0 release with run logs and full provenance

---

## Open questions to resolve before kickoff

1. ~~ORNL-4541 PDF acquisition~~ — **RESOLVED 2026-06-01.** ORNL-4528 (two-fluid, our primary) and ORNL-4541 (single-fluid, secondary reference) both openly hosted: ORNL-4528 via OSTI biblio/4093364; ORNL-4541 via flibe.com/public PDF mirror + UNT Digital Library.
2. ~~ENDF/B-VIII.0 graphite thermal scattering coverage~~ — **RESOLVED 2026-06-01.** S(α,β) graphite tables exist at 700K, 800K, 1000K, 1200K, 1600K (LANL NJOY processing, LA-UR-18-25096). MSBR operating temp ~973K (700°C) brackets cleanly. Use grph10.86t (800K) and grph10.87t (1000K) for interpolation, or 1000K directly.
3. Two-fluid CSG approach: nested universes per unit cell, or lattice-of-lattices? **Open.** Prototype both on a simplified 2D slice before committing.
4. BR calculation tally setup in OpenMC — verify reaction-rate tally approach matches ORNL-4528 methodology. **Open.** Needs ORNL-4528 read-through first.
5. ~~Survey the literature for prior two-fluid MSBR recomputes~~ — **RESOLVED 2026-06-01.** At least 5 prior modeling efforts touch ORNL-4528: Singh/Lish/Chvála 2017+2018 (UTK, dynamics), Nezhad 2022 MSiBR (Annals of Nuclear Energy), Feng/Cao/Davidson/Betzler 2021 (ANL+ORNL, Shift). Validation strategy is "agreement with ORNL-4528 + cross-check against ≥2 independent recomputes" — strong defensive posture.
6. **NEW:** Confirm with Chvála (UTK) whether his group's static neutronics inputs to the 2017/2018 dynamic model are publicly available. If yes, that's a direct numerical comparison target. If no, Promethea v0.4.0 becomes the *first public* static neutronics for ORNL-4528 — strictly stronger contribution claim.
