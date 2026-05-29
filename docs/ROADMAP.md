# Promethea Roadmap

This document tracks the full three-phase plan. Update with each milestone.

## Phase 1 — Promethea Control (months 1–8)

**Objective:** Become a credible voice in ML-for-advanced-reactor-controls. Ship a public, runnable artifact: a digital twin of a known reference reactor with classical and learned controllers running on it.

### 1.1 Toolchain & benchmark (month 1)
- [ ] Install OpenMC, MOOSE/Griffin, OpenFOAM, OpenModelica in a reproducible Linux env (Docker / Conda)
- [ ] Pull and read MSRE reference docs (ORNL-4812, ORNL-TM series)
- [ ] Reproduce a published MSRE k-eff and temperature-coefficient benchmark in OpenMC within ~1 %
- [ ] **Deliverable:** `benchmarks/msre/` with input decks, results, and a notebook
- [ ] **Milestone:** "Promethea reproduces the MSRE benchmark"

### 1.2 Digital twin (months 2–3)
- [ ] Couple OpenMC neutronics to MOOSE thermal-hydraulics for MSRE geometry
- [ ] Add delayed-precursor drift model (the molten-salt twist — precursors flow downstream)
- [ ] Implement realistic sensor noise + actuator delays
- [ ] Wrap as a Gymnasium-compatible environment (`promethea-gym`)
- [ ] **Deliverable:** `gym/` package, pip-installable
- [ ] **Milestone:** Runnable `promethea-gym` env on GitHub

### 1.3 Baseline controllers (month 4)
- [ ] Classical PID for power set-point tracking
- [ ] MPC (linear, around an operating point) for load-following
- [ ] Scenario suite: load follow, xenon transient, sensor degradation, partial flow loss
- [ ] **Deliverable:** `controllers/baselines/` with benchmark results
- [ ] **Milestone:** Published baseline numbers on each scenario

### 1.4 Hebbnet controller v1 (months 5–6)
- [ ] Anomaly detection on sensor streams (easiest; pure unsupervised)
- [ ] Adaptive load-following (set-point tracking under disturbance)
- [ ] Sensor-drift compensation via online Hebbian update (gradient-free, the differentiator)
- [ ] **Deliverable:** `controllers/hebbnet/` with trained checkpoints
- [ ] **Milestone:** Hebbnet matches or beats PID/MPC on ≥1 scenario, demonstrably learns online

### 1.5 Write-up & release (months 7–8)
- [ ] Polish docs, install instructions, tutorial notebooks
- [ ] Paper draft (target: ANS Winter Meeting OR arXiv + ICAPP 2027)
- [ ] 20-minute walkthrough video
- [ ] Outreach: email INL/ANL ML-controls leads, post to r/nuclear, share with openmsr
- [ ] **Milestone:** Promethea Control v1.0 release

---

## Phase 2 — Promethea Design (months 9–18)

**Objective:** Move from "controlling someone else's reactor" to "designing our own." Produce a self-consistent neutronics + thermal-hydraulics design with a defensible safety basis.

### 2.1 Literature review & parameter selection (month 9)
- [ ] Deep-read Elysium MCSFR, TerraPower MCFR, Moltex SSR papers
- [ ] Lock v0 design spec (salt chemistry, geometry envelope, fuel loading)
- [ ] **Deliverable:** `arch/PROMETHEA-v0-SPEC.md`

### 2.2 Cold criticality (months 10–11)
- [ ] k-eff at startup with reasonable reactivity margin
- [ ] Breeding ratio ≥ 1.0 (Th-232 → U-233)
- [ ] Strongly negative temperature coefficient (non-negotiable)
- [ ] Fast-fluence on structural materials over 8-year life
- [ ] **Milestone:** Self-consistent neutronics

### 2.3 Thermal-hydraulics (months 12–13)
- [ ] OpenFOAM coupling
- [ ] Fuel salt stays liquid everywhere, no boiling at heat-pipe boundary
- [ ] Heat-pipe interface modeled
- [ ] **Milestone:** Steady-state thermal envelope verified

### 2.4 Transients & safety (months 14–15)
- [ ] LOFA — loss of flow accident
- [ ] LOHS — loss of heat sink
- [ ] RIA — reactivity insertion accident
- [ ] Demonstrate walk-away passive safety
- [ ] **Milestone:** Defensible safety basis

### 2.5 Integration (months 16–18)
- [ ] Run Phase 1 hebbnet controller on Phase 2 design
- [ ] Compare against PID/MPC baselines on the new design
- [ ] Paper #2 draft
- [ ] **Milestone:** Promethea v1.0 — design + control, integrated

---

## Phase 3 — Promethea System (months 19–30)

**Objective:** End-to-end reference system — design, control, balance of plant, fuel cycle, deployment story.

### 3.1 Balance of plant (months 19–21)
- [ ] Heat-pipe secondary loop in detail
- [ ] sCO₂ Brayton cycle
- [ ] OpenModelica grid interconnection
- [ ] **Milestone:** End-to-end heat-to-electricity simulation

### 3.2 Operations & fuel cycle (months 22–24)
- [ ] Online actinide management model
- [ ] Refueling cycle, waste streams
- [ ] LCOE estimate
- [ ] **Milestone:** Defensible cost number

### 3.3 Deployment scenarios (months 25–27)
- [ ] Case A: data center pod
- [ ] Case B: rural community grid backup
- [ ] Case C: disaster-resilience deployment
- [ ] NRC Part 53 regulatory pathway analysis
- [ ] **Milestone:** "How this would actually be deployed" document

### 3.4 Capstone (months 28–30)
- [ ] Comprehensive technical report (ORNL-style design study, open)
- [ ] Interactive web design explorer
- [ ] Long-form documentary-style writeup/video
- [ ] **Milestone:** Promethea v2.0
