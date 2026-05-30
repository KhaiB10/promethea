# Section 3 — Model Description (paper draft)

**Status:** Draft v1, 2026-05-30. Pre-senior-review.
**Scope:** Sections 3.1 through 3.4 of the working paper outline.
Section 3.5 (Method — parameterized sensitivity studies) lives in
PAPER_OUTLINE.md until promoted here.

---

## 3.1 Geometry

The Promethea model implements the MSRE first-criticality
configuration of 1965 June 1 in a fully heterogeneous, three-dimensional
constructive-solid-geometry (CSG) representation. The active core is
a graphite cylinder approximately 140 cm in diameter and 165 cm in
active length, containing 1140 vertical fuel channels organized as a
hexagonal lattice of two-channel-per-edge stringer assemblies per
Robertson (1965) Table 2.3 and ORNL-TM-0728 §2.6. The lattice pitch
is 5.08 cm (2.00 in) between adjacent stringer centerlines.

Each fuel channel is modeled as a vertical cylindrical bore of radius
0.635 cm (0.25 in) through the stringer body, with no fillet at the
channel-stringer interface. The fuel-channel corner geometry was
parameterized as a sensitivity-study variable
(`PROMETHEA_FILLET_R_CM`) and confirmed to contribute < 50 pcm to
k-effective across the 0.0–0.475 cm range, consistent with fuel-
fraction conservation (§5.2).

Four thimble positions occupy the central 7.62 cm-radius circle of
the active core:

- **Three control-rod thimbles** at the locations specified in
  Robertson (1965) Fig. 2.4. Each thimble is an INOR-8 annulus of
  inner radius 5.08 cm and outer radius 6.35 cm, modeled at full
  active-core height. In the first-criticality configuration, one
  rod is inserted to 4.4 in below the top of the active region and
  two rods are fully withdrawn; this is implemented as the absorber
  occupying the inner bore over the corresponding axial range, with
  the empty bore filled by helium fill-gas above the absorber
  positions.

- **One graphite sample assembly** at the fourth position. Per
  ORNL-TM-0728 §4.1 ("...three control-rod thimbles. The fourth
  position of the array is occupied by a graphite sample assembly"),
  this position is modeled as bulk CGB-grade graphite with no INOR-8
  shell around the basket exterior. Internal sample-rod hardware is
  not modeled in the canonical configuration. The decision to omit
  the basket-exterior INOR-8 shell — and the +1045 pcm reactivity
  consequence of incorrectly including one — is documented in §5
  and is the largest single methodology finding of this work.

The active core is surrounded by an INOR-8 vessel of inner radius
70.5 cm and outer radius 71.1 cm, an upper plenum of helium-fill-gas
height 33 cm, and a lower head of INOR-8 thickness 1.27 cm. The
vessel extends from the bottom of the lower head to the top of the
upper plenum, a total of 245 cm. The vessel exterior is a vacuum
boundary; thermal-shield and biological-shield structures are not
modeled and do not contribute to neutron multiplication.

## 3.2 Materials

### 3.2.1 Fuel salt

The fuel salt is the ⁷LiF–BeF₂–ZrF₄–UF₄ composition specified in
ORNL-TM-0728 Table 4.1, with U-235 enrichment 33.0 atom percent and
⁷Li enrichment 99.99 atom percent. The molar composition is

| Component | mole fraction |
|---|---:|
| ⁷LiF   | 0.650 |
| BeF₂   | 0.292 |
| ZrF₄   | 0.050 |
| UF₄    | 0.0080 |
| (residual U-238 in UF₄) | 0.00020 |

The salt density at the first-criticality temperature of 911 K is
2.323 g/cm³, with the temperature dependence of density taken from
ORNL-TM-0728 §5.2 (linear in T over the relevant range). The salt
fills all fuel channels, the gap volume between stringer assemblies,
and the upper-plenum-to-lower-head riser; total fuel-salt volume in
the modeled geometry is consistent with the 1.97 m³ critical-charge
inventory reported in Robertson (1965) §3.

### 3.2.2 Graphite

The graphite is CGB-grade per ORNL-TM-0728 §2.7, density 1.86 g/cm³,
with natural-boron impurity at 0.3 ± 0.1 ppm by mass. The boron-impurity
parameter (`PROMETHEA_BORON_PPM`) was confirmed by sensitivity study
(§5.2) to contribute < 200 pcm to k-effective across the literature
range 0.1–1.0 ppm; the canonical value of 0.3 ppm is the post-1964
production-grade specification documented in ORNL-TM-0728 §2.7
Table 2.5.

Graphite is also used as the matrix of the sample-basket assembly
described in §3.1, at the same density and boron content.

### 3.2.3 INOR-8

The vessel, control-rod thimbles, and other primary-loop structural
components are INOR-8, a Hastelloy-N predecessor with nominal mass
composition per ORNL-TM-0728 Table 2.9:

| Element | mass fraction |
|---|---:|
| Ni | 0.70 |
| Mo | 0.17 |
| Cr | 0.07 |
| Fe | 0.05 |
| (residual Mn, Si, C, B) | 0.01 |

Density is 8.79 g/cm³ at 911 K. The density is approximately constant
over the operating range and a temperature correction was not applied.

### 3.2.4 Other materials

The control-rod absorber is modeled as boron carbide (B₄C) at natural
boron isotopic abundance, density 2.52 g/cm³, per ORNL-TM-0728
§4.3. Helium fill-gas is modeled at 1 atm and 911 K (density
4.66 × 10⁻⁵ g/cm³).

## 3.3 Code and cross-section data

### 3.3.1 OpenMC

All calculations use OpenMC version 0.14 (Romano et al. 2015) compiled
from the upstream release branch with default Monte Carlo options.
The Promethea repository pins the OpenMC version through a Dockerfile
(`Dockerfile` in the repository root); every CI run rebuilds the
image from the same Dockerfile, so the OpenMC build itself is
bit-reproducible across runs.

### 3.3.2 Cross-section libraries

Three evaluated nuclear data libraries are supported by the Promethea
infrastructure:

- **ENDF/B-VIII.0** (Brown et al. 2018) — production canonical
  library. This is the library used by Yilmaz et al. (2024) and is
  the OpenMC official-data-libraries default.
- **ENDF/B-VII.1** (Chadwick et al. 2011) — library-matched comparison
  library, used by Shen et al. (2021) per Yilmaz et al. (2024) §3.
- **JEFF-3.3** (Plompen et al. 2020) — independent (European) evaluation
  used as a third-party cross-check.

Library archives are fetched from `openmc.org/official-data-libraries`
via the script `scripts/fetch_xs.sh`. The script accepts the library
key as its single argument; URLs are pinned and verified.

ENDF/B-VII.0 is not supported because no first-party OpenMC HDF5 build
is currently published; the LANL Box mirror distributes VII.0 only in
MCNP/ACE format. This is documented in `RESEARCH_LOG.md` and in the
`fetch_xs.sh` script header.

### 3.3.3 Calculation parameters

Unless otherwise noted, all canonical-configuration calculations use:

| Parameter | Value |
|---|---|
| Mode | `eigenvalue` (k-effective) |
| Source | Uniform fission-sampled over fuel-salt cells |
| Particles per batch | 200 000 (submission of record); 100 000 (sensitivity studies) |
| Inactive batches | 20 |
| Active batches | 200 (submission of record); 100 (sensitivity studies) |
| Boundary conditions | Vacuum on vessel exterior |
| Photon transport | Off |
| Thermal scattering | S(α,β) for graphite and ⁷LiF (where library-provided) |
| Random seed | Default OpenMC seed; runs are not yet replicated across seeds |

The submission-of-record k-effective uncertainty at 200 k × 200 active
batches is σ ≈ 15 pcm, dominated by counting statistics on the
combined estimator. The sensitivity-study configuration at 100 k × 100
active batches gives σ ≈ 30 pcm.

## 3.4 Continuous integration and reproducibility

The Promethea repository implements a GitHub Actions workflow,
`.github/workflows/benchmark-msre.yml`, that executes a complete
canonical-configuration calculation on every workflow dispatch on the
free `ubuntu-latest` runner. Inputs to the workflow are:

| Input | Default | Sensitivity-study range |
|---|---|---|
| `mode` | `het_critical` | — |
| `particles` | 100000 | up to 200000 |
| `batches` | 100 | up to 200 |
| `boron_ppm` | 0.3 | 0.1–1.0 |
| `fillet_radius_cm` | 0.0 | 0.0–0.475 |
| `xs_library` | `endfb-viii.0` | VII.1, VIII.0, JEFF-3.3 |
| `basket_shell` | `false` | true, false |

The concurrency-group key for the workflow includes every parameterised
input, so parallel sweeps at different configurations execute on
different free runners without clobbering each other's cache. The
cross-section library is cached per-library; first-run downloads
add ~3-7 min, subsequent runs at the same library hit the cache in
under one minute.

A canonical-configuration calculation from a fresh repository clone
runs in approximately 25 minutes at the sensitivity-study statistics
and approximately 85 minutes at the submission-of-record statistics.
Total free-CI cost per calculation is therefore approximately 0.4
to 1.4 runner-hours; the GitHub Free tier allowance of 2 000 runner-
minutes per month accommodates approximately 24 to 90 canonical
calculations per month per user account.

The repository is licensed MIT and all code, input files, output
artifacts, and CI run logs are publicly inspectable. The release of
record for this paper is tagged `v0.2.0` at commit (FILL).

---

## Notes on this draft

- §3.1 numbers (dimensions, density, vessel measurements) need a
  systematic cross-check pass against ORNL-TM-0728 before submission.
  I have transcribed them from the v0.1.0 Promethea geometry, but a
  second-source verification (the IRPhE handbook entry if obtainable,
  or Robertson 1965 Part V) is required before any senior reviewer
  signs off.
- §3.2.1 fuel-salt mole fractions: confirm against ORNL-TM-0728
  Table 4.1; my repository has 0.650/0.292/0.050/0.008 but the
  literature variation is large enough (some references put UF₄
  closer to 0.009) that a paper claim needs anchored to a specific
  table.
- §3.3.3: replication across random seeds (5 seeds × canonical
  configuration) is a future v0.3.0 task and a §5 sensitivity-study
  improvement; flag explicitly in §6 Discussion as a known limit.
- §3.4 runner-hour math is approximate; reconcile against actual
  CI usage statistics for the paper-of-record value.

These notes belong in `.local/PAPER_REVIEW_TODOS.md` for the next pass.
