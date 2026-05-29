# Controllers

This is where the I&C (instrumentation and control) research lives.

## Layout
- `baselines/` — classical control (PID, MPC). The bar we have to beat.
- `hebbnet/` — continual-learning controllers built on the hebbnet library.

## Design philosophy
1. **Classical controllers handle safety-critical actions.** Always.
2. **Learned controllers handle optimization and adaptation.** Anomaly detection, sensor-drift compensation, efficiency tuning under load following.
3. **Every learned controller has a classical fallback.** If the network produces an out-of-envelope action, the fallback overrides.

## Why hebbnet
Conventional deep-RL controllers train offline, freeze, and deploy. They cannot adapt to sensor drift, fuel composition changes, or aging components during the 8-year refueling cycle.

Hebbian / gradient-free continual learning can update weights *during deployment* based on local correlations — no backprop, no labeled data, no GPU. This is well-suited to long-lived autonomous systems where the operating envelope drifts and where backprop on safety-critical hardware is a non-starter.

## Status
Not started. Phase 1.3 and 1.4.
