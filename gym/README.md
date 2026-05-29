# promethea-gym

A Gymnasium-compatible reinforcement-learning environment wrapping a digital twin of a molten salt reactor.

## Scope (Phase 1)
- Underlying physics: simplified coupled neutronics + heat balance (point kinetics with thermal feedback). Eventually upgraded to OpenMC/Griffin co-simulation.
- Action space: control signals (pump speed, reactivity insertion via simulated rod, target outlet temp)
- Observation space: realistic sensor signals with noise and delay
- Scenarios: load-follow, xenon transient, sensor degradation, partial flow loss

## Why a gym env
- Lets us train and benchmark controllers (PID, MPC, hebbnet) on identical terms
- Lets external researchers drop in their own controllers
- Forces a clean separation between physics and policy

## Status
Not started. Phase 1.2.
