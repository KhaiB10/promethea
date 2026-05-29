# Promethea Principles

These are the operating rules of the project. They exist so future-me, future-collaborators, and future-readers all know the bar.

## 1. Under-claim, over-deliver
Every figure, claim, and simulation result is labeled with its confidence level. Concepts are labeled as concepts. Simulations are labeled as simulations. We do not say "this reactor will" — we say "in this simulation, with these assumptions, the model produces…".

## 2. Reproducibility is non-negotiable
If a result is in the repo, someone with the same hardware and a `git clone` can reproduce it. No private data, no hand-edited intermediates, no "trust me" plots. Every figure has an input deck and a script behind it.

## 3. Stand on giants
Promethea uses OpenMC, MOOSE/Griffin, BISON, OpenFOAM, OpenModelica, and the ORNL MSRE archive. We do not reinvent solvers. We do not pretend to. We cite, attribute, and link.

## 4. Validate before innovate
Before publishing any novel result, we reproduce a published benchmark. The MSRE benchmark is the foundation. New design claims build on validated tooling, not on hope.

## 5. One question per cycle
Reactor design has infinite rabbit holes. We pick one well-formed question per iteration ("what's the minimum critical mass at this salt composition?"), answer it, log it, move on.

## 6. Open by default
Code: MIT. Docs: CC BY 4.0. Every milestone is announced publicly. The project is built in the open from day one; there is no "secret v2."

## 7. Safety is a property of the design, not the operator
Every design iteration must demonstrate passive, walk-away safety. If a reactor needs an alert human or a working network to be safe, it is not the kind of reactor Promethea is trying to build.

## 8. AI is a tool, not the goal
We use ML where it earns its place — sensor anomaly detection, continual adaptation, fault prediction. We do not put neural networks inside the safety-critical reactivity-control loop. Hebbian learning informs; classical control and physical feedback decide.

## 9. Serve the next person
Every artifact — code, doc, figure, video — is built so the next person can pick it up and go further. If a doc only makes sense to me, it is incomplete.

## 10. Stay grounded
This work is rooted in a conviction that good technology should serve the people who need it most. If a design choice optimizes for clever over useful, useful wins.
