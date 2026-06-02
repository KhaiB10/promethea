"""
scripts/analysis/het_vs_homog.py

Pair the heterogeneous and homogenized MSBR unit-cell k_inf
statepoints and report the heterogeneity penalty:

    Delta_k = k_het - k_homog
    sigma_Delta = sqrt(sigma_het^2 + sigma_homog^2)

If both runs use the same RNG seed they are NOT statistically
independent, but for the volume fractions and geometry topologies
used here the per-statepoint correlation is small (the two cells
share no particle-history state). Treating them as independent is
the standard practice for Monte Carlo het/homog studies and is
what we adopt.

Usage
-----

    python3 scripts/analysis/het_vs_homog.py \\
        --het  sims/openmc/msbr_unit_cell/statepoint.60.h5 \\
        --homog sims/openmc/msbr_homog_cell/statepoint.60.h5

Output is a human-readable block printed to stdout and a JSON
sidecar at out/het_vs_homog.json for downstream figures.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys


def _read_keff(sp_path: str) -> tuple[float, float]:
    """Extract combined k-eff (mean, std) from an OpenMC statepoint."""
    import openmc  # imported lazily so the script imports without OpenMC

    sp = openmc.StatePoint(sp_path)
    k = sp.keff
    # openmc.UFloat exposes .nominal_value and .std_dev
    return float(k.nominal_value), float(k.std_dev)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--het", required=True, help="heterogeneous statepoint .h5")
    p.add_argument("--homog", required=True, help="homogenized statepoint .h5")
    p.add_argument("--out", default="out/het_vs_homog.json",
                   help="output JSON path")
    args = p.parse_args()

    k_het, sig_het = _read_keff(args.het)
    k_homog, sig_homog = _read_keff(args.homog)

    delta = k_het - k_homog
    sig_delta = math.sqrt(sig_het ** 2 + sig_homog ** 2)
    pcm = delta * 1.0e5
    pcm_sig = sig_delta * 1.0e5

    # Determine significance: > 3 sigma considered a real effect.
    z = abs(delta) / sig_delta if sig_delta > 0 else float("inf")

    print("MSBR unit-cell heterogeneity study")
    print("=" * 50)
    print(f"  k_het    = {k_het:.5f} +/- {sig_het:.5f}")
    print(f"  k_homog  = {k_homog:.5f} +/- {sig_homog:.5f}")
    print(f"  Delta_k  = {delta:+.5f} +/- {sig_delta:.5f}")
    print(f"           = {pcm:+.0f} +/- {pcm_sig:.0f} pcm")
    print(f"  z-score  = {z:.1f}")
    if z >= 3.0:
        print(f"  -> Statistically significant heterogeneity effect")
    elif z >= 2.0:
        print(f"  -> Marginal effect (2-3 sigma); increase statistics")
    else:
        print(f"  -> Not statistically resolved")
    print()
    print("Interpretation: positive Delta_k indicates the explicit")
    print("fuel/graphite/blanket geometry adds reactivity vs a")
    print("perfectly mixed cell at the same volume fractions.")

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "k_het": k_het, "sigma_het": sig_het,
        "k_homog": k_homog, "sigma_homog": sig_homog,
        "delta_k": delta, "sigma_delta": sig_delta,
        "delta_pcm": pcm, "sigma_pcm": pcm_sig,
        "z_score": z,
    }, indent=2) + "\n")
    print(f"\nWrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
