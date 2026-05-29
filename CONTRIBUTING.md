# Contributing to Promethea

Welcome. Promethea is built in the open, and contributions of any kind — issues, corrections, simulation runs, doc improvements, alternative designs — are wanted.

## Ground rules

1. **Reproducibility first.** Every PR with a numerical result must include the input deck or script that produced it.
2. **Honest claims.** Concepts labeled as concepts. Simulations labeled as simulations. No marketing language.
3. **Cite your sources.** If you base work on a paper, link it.
4. **Be kind.** This is a learning project. Patient explanations beat dunks.

## What kinds of contributions help most

- **Corrections.** Bad physics, bad assumptions, bad code — find them, open an issue.
- **Benchmarks.** If you have access to a published MSR/microreactor benchmark and can help validate the Promethea model against it, that is gold.
- **Alternative designs.** Fork the v0 spec, swap parameters, run the simulation, send a PR.
- **Docs.** Glossary entries, tutorials, install troubleshooting for various OS combos.
- **Tooling.** CI, Docker, environment pinning, automated regression tests.

## Workflow

1. Open an issue describing what you want to do
2. Fork, branch (`feat/<short-name>` or `fix/<short-name>`)
3. Commit small, write clear messages
4. Open a PR; link the issue

## Code style

- Python: PEP 8 via `ruff`, type hints encouraged
- Notebooks: clear outputs before commit
- Input decks: comments at the top explaining what's being run and against what reference

## Safety / scope

Promethea is a simulation and engineering study. We do not host, distribute, or assist with:
- Actual nuclear material handling
- Operational reactor control software (the controllers here are research artifacts only)
- Anything that would be export-controlled under EAR / ITAR

If you are unsure whether a contribution falls under these, ask first.
