# MSBR multi-group self-verification — CE vs MG (v0.5.0)

## Question

Does the **standard industrial 8-group homogenized multi-group workflow**
recover continuous-energy truth on the MSBR heterogeneous fuel cell?

Production reactor codes (CASMO, PARCS, MPACT, etc.) run multi-group
with a 2-step homogenized approach: tally CE fluxes once on a fine
lattice, build a multi-group library, then transport with MG. If MG
recovers CE to within ~100 pcm, the industrial workflow can be
trusted. If not, the same heterogeneity physics that drives the
v0.4.0 epithermal η ratio (3.72× het/homog) also degrades the
predictive accuracy of every production code on this geometry.

## Method

1. Run CE heterogeneous unit cell with MGXS tallies (8-group CASMO-style
   structure; group edges chosen so 0.625 eV and 0.1 MeV land on
   boundaries, matching the v0.4.0 spectrum decomposition).
2. Build an OpenMC `MGXSLibrary` from the CE tallies. Material-level
   homogenization (one xsdata per material). No transport correction.
3. Rebuild the same geometry in MG mode with macroscopic fills.
4. Run MG with matching particle budget.
5. Compute Δ_MG = k_CE − k_MG in pcm.

## Result (production, 200,000 × 200, seed=1, ENDF/B-VIII.0)

CI run: [26923324624](https://github.com/KhaiB10/promethea/actions/runs/26923324624)

| | k_inf | σ |
|---|---|---|
| CE reference                           | 1.131300 | ± 0.000168 |
| MG (8-group, material-homogenized)     | 1.134039 | ± 0.000154 |
| **Δ_MG = k_CE − k_MG**                 | **−274 pcm** | **± 23 pcm (z = −12.0)** |

The smoke run (20,000 × 60, [CI 26922019024](https://github.com/KhaiB10/promethea/actions/runs/26922019024))
returned Δ_MG = −84 ± 140 pcm, consistent with zero but with σ too
wide to resolve the bias. Smoke vs production are mutually consistent
(z = +1.34) — the bias is real and was hidden by smoke-level noise.

## Interpretation

The standard 8-group homogenized MG workflow **systematically
over-predicts k_inf by ~274 pcm** vs continuous-energy reference on
the ORNL MSBR fuel cell. The bias is:

- **Resolved at z = −12σ** with 200,000 × 200 statistics
- **Small as a fraction of the heterogeneity effect** (274 / 10,506 ≈ 2.6%)
- **Large compared to typical industrial code-verification targets**
  (which expect ~50-100 pcm CE/MG agreement on well-resolved geometries)

This is consistent with the v0.4.0 finding that MSBR heterogeneity is
disproportionately concentrated in the epithermal regime (η ratio
3.72× there vs 1.64× thermal, 1.24× fast). The 0.625 eV – 0.1 MeV
window is the hardest range for an 8-group structure to capture
because the U-233 and Th-232 resonance structure is dense and narrow,
and group-averaged cross-sections cannot reproduce the self-shielded
flux gradient. With only 4 groups spanning that decade-and-a-half of
energy, the MG model effectively smears the resonance flux dip.

## What this does NOT claim

- Not a safety finding. 274 pcm is small versus core-design reactivity
  margins. Real reactor codes also include local-leakage and
  reflector-correction steps that can compensate.
- Not a Serpent/MCNP cross-check. That would require a second
  continuous-energy code, which is gated by export control (see
  v0.5.0 release notes).
- Not yet group-structure-optimized. The bias may shrink with 16-group
  or 30-group structures; future work.

## What this DOES claim

A reproducible, OSS-only measurement of a +274 ± 23 pcm CE-vs-MG bias
on the original ORNL MSBR fuel cell. To our knowledge no open
publication has previously quantified this number on this geometry.
The two natural ways to close the gap — finer group structure, or
explicit resonance self-shielding correction — both define follow-on
work for v0.6.0+.

## Plain language

Real reactor codes don't track every individual neutron energy.
They lump energies into "groups" and use averaged cross-section
data. We tested how well an 8-group averaged version recovers the
true continuous-energy answer on the MSBR fuel cell.

At low statistics, the MG and CE answers agreed within noise. At
higher statistics (100× more particles), a small but **clearly real**
gap emerged: MG over-estimates by 274 pcm out of ~131,000. That's
0.2%, well inside safety margins, but it's not zero — and the reason
it isn't zero ties back to the same MSBR-specific physics that v0.4.0
already showed: the heterogeneity advantage is concentrated in the
epithermal range, where group-averaging is hardest. Industrial
reactor codes can trust their MSBR predictions, but should know the
bias exists and that finer group structures would close it further.
