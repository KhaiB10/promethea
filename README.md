# Promethea

**An open-source, continual-learning autonomous control system for advanced molten-salt microreactors — and, eventually, a complete reference design of one.**

> *Prometheus stole fire from the gods and gave it to humanity. Promethea is the gift, not the thief — small, portable, and meant to be handed to whoever needs it.*

---

## What this is

Promethea is a public, end-to-end engineering project to design and simulate a community-scale molten-salt microreactor — and to build the AI-driven control system that makes it walk-away safe and autonomous.

It is being built by one person, in the open, on a workstation. Nothing here is, or ever will be, a real physical reactor. Everything here is software, simulation, and engineering documentation. The goal is not to build a reactor in a garage. The goal is to **produce the artifacts that make the next generation of small-reactor builders 10× more productive**, and to put a credible, reproducible design study on the internet for anyone to learn from, fork, or improve.

## Why

The grid is under stress from rising demand, aging hardware, and adversaries who have already pre-positioned inside critical infrastructure. Solar and storage solve part of the problem. Microreactors solve another part — dispatchable, energy-dense, weather-independent power small enough to live near the communities that need it.

Advanced reactor companies are tiny teams (often 20–50 engineers) and they are starved for: better open simulators, validated reference designs, modern controls research, and technically literate evangelists. A motivated independent contributor with the right tools can become a known quantity in this world in 12–18 months.

This is rooted in a conviction that **good technology should serve the people who need it most**, and that the asymmetry between *those with electricity* and *those without* will only grow in the AI era.

## The design

**Working concept (v0 — subject to revision):**

- **Type:** Chloride-salt, fast-spectrum, thorium-fueled microreactor
- **Power:** ~5 MWe / ~15 MWth (matches Westinghouse eVinci scale)
- **Primary:** NaCl–MgCl₂–ThCl₄ + HALEU starter (U-235 ~19.75%)
- **Secondary:** Heat-pipe array, eVinci-style (walk-away safe, no high-pressure water)
- **Power conversion:** Supercritical CO₂ Brayton cycle (~45% efficiency)
- **Refueling interval:** 8+ years
- **Spectrum:** Fast — no moderator, online actinide management possible
- **Control:** Continual-learning AI controller (hebbnet) running on embedded hardware, with classical PID/MPC fallback

This concept is positioned in a niche the major players have largely skipped: the intersection of **chloride + fast + thorium + microreactor scale**. Most thorium designs are fluoride/thermal (LFTR, Copenhagen Atomics, Seaborg). Most chloride fast reactors are uranium or waste-burning at utility scale (TerraPower MCFR, Moltex SSR-W, Elysium MCSFR). The combination at ~5 MWe is largely open ground in the published literature.

## The plan

**Phase 1 — Promethea Control (months 1–8).** Reproduce the MSRE benchmark in OpenMC + Griffin. Build a digital twin and a `promethea-gym` environment. Implement PID + MPC baselines. Train a hebbnet continual-learning controller. Publish.

**Phase 2 — Promethea Design (months 9–18).** Lock the v0 design parameters. Iterate the neutronics in OpenMC until cold criticality, breeding ratio, and temperature coefficient are all in spec. Couple to OpenFOAM for thermal-hydraulics. Run LOFA / LOHS / RIA transient cases. Bolt the Phase 1 controller onto the Phase 2 design. Publish.

**Phase 3 — Promethea System (months 19–30).** Balance of plant, fuel cycle, deployment scenarios, cost-of-electricity estimate. End-to-end reference report. Companion site and documentary-style writeup.

See [docs/ROADMAP.md](docs/ROADMAP.md) for the detailed milestone breakdown.

## How to follow / contribute

This repo is the source of truth. Every design decision, simulation input deck, controller checkpoint, and write-up lives here. The aim is for any reactor physicist, ML researcher, or curious engineer to clone the repo, run the code on their own workstation, and reproduce every claim.

- **Watch the repo** for milestone releases
- **Open issues** with questions, corrections, or suggestions
- **Pull requests welcome** — see [CONTRIBUTING.md](CONTRIBUTING.md)
- **Build log:** posted to the project blog and YouTube channel (links coming)

## Run it without a workstation

You don't need a Linux box to reproduce Promethea results.

- **GitHub Codespaces.** Click `Code → Codespaces → Create codespace on main`. The container builds OpenMC + the scientific stack automatically. Then in the terminal: `bash scripts/fetch_xs.sh` (one-time, ~4 GB), `python scripts/hello_reactor.py` (smoke test), `python benchmarks/msre/run_criticality.py` (full MSRE v0). Free tier covers it.
- **GitHub Actions.** The [`benchmark-msre`](.github/workflows/benchmark-msre.yml) workflow runs the full MSRE criticality benchmark on every push to `benchmarks/msre/**`, and can be triggered manually from the Actions tab with custom particle/batch counts. k-eff and PASS/REVIEW status are written to the run summary.

## What this is *not*

- This is not a real reactor. It is a simulation and engineering study.
- This is not an investment vehicle. There is no token, no company (yet), no fundraise.
- This is not an attempt to circumvent nuclear regulation. Any future physical work would go through the NRC like everyone else.
- This is not a claim of expertise. It is a public learning project that aims to produce real artifacts along the way.

## Built on the shoulders of

- **OpenMC** (LANL et al.) — Monte Carlo neutron transport
- **MOOSE / Griffin / BISON** (INL, ANL) — multiphysics framework, reactor physics, fuel performance
- **OpenFOAM** — computational fluid dynamics
- **OpenModelica** — systems modeling
- **hebbnet** — neuromorphic on-device continual learning ([github.com/KhaiB10/hebbnet](https://github.com/KhaiB10/hebbnet))
- **The ORNL MSRE archive** — 60 years on, still the foundational dataset for molten salt reactors
- **The openmsr community** — [github.com/openmsr](https://github.com/openmsr)

## License

Code: [MIT](LICENSE). Documents, designs, and figures: [CC BY 4.0](LICENSE-DOCS).

## Contact

Khai · Wichita, KS · [khaibustos10@gmail.com](mailto:khaibustos10@gmail.com)
