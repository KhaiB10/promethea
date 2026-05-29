# MSRE Benchmark

The Molten Salt Reactor Experiment (Oak Ridge, 1965–1969) is the gold-standard validation target for any MSR code. Before Promethea claims anything novel, it must reproduce known MSRE values.

## Goal
Reproduce the published MSRE k-eff and isothermal temperature coefficient of reactivity within ~1 % using OpenMC.

## References
- ORNL-4812 — *MSRE Design and Operations Report*
- ORNL-TM-0728 — *MSRE Fuel Salt Compositions*
- ORNL-TM-0732 — *MSRE Operating Experience*
- All available on osti.gov

## Plan
1. Build OpenMC geometry of MSRE core (graphite stringers, fuel salt channels, INOR-8 vessel)
2. Use published fuel salt composition: LiF–BeF₂–ZrF₄–UF₄ (65–29.1–5–0.9 mol%)
3. Compute k-eff at startup conditions (650 °C, clean fuel)
4. Compute α_T (temperature coefficient) by perturbation
5. Compare against ORNL-published values

## Status
Not started. Phase 1.1.
