"""
benchmarks/msbr/tallies.py

Reaction-rate tallies for the MSBR breeding ratio (BR) and related
neutron-balance diagnostics. Primary source: ORNL-4528 §6.3 (neutron
balance) and Table 6.3, which gives the reference-design BR = 1.06.

Definition adopted here
-----------------------

Following ORNL-4528 §6.3 (and the standard breeder-reactor convention):

    BR = (production of fissile per neutron generation)
         / (destruction of fissile per neutron generation)

For the two-fluid 233U/Th MSBR the only fertile capture path that
produces new fissile is

    232Th (n,gamma) -> 233Th -> ... -> 233U

and the only fissile destruction path is absorption on 233U:

    233U + n -> {fission, (n,gamma) -> 234U}

So in tally terms (per source neutron, normalized identically):

    BR = R_capture(232Th)  /  R_absorption(233U)

where R_absorption = R_fission + R_capture for 233U. We tally fission
and capture separately so we can also report eta (neutrons produced
per fissile absorption) and the fission fraction in 233U vs Th-bred
isotopes if/when they appear in the depletion chain.

Tally filter strategy
---------------------

We tally on a MaterialFilter, NOT a CellFilter, because the same
materials (fuel salt, blanket salt) appear in multiple cells of the
full-core lattice. A material filter automatically sums over every
cell the material fills.

For the unit cell prototype, "fuel salt" appears in two cells (inner
bore + annulus) and "blanket salt" in one cell. For the full core,
the same recipe is reused across hundreds of lattice cells; the tally
still works because OpenMC tracks rates per material.

Usage
-----

    from .tallies import build_breeding_tallies
    from .materials import build_fuel_salt, build_blanket_salt

    fuel = build_fuel_salt()
    blanket = build_blanket_salt()
    tallies = build_breeding_tallies(fuel_salt=fuel, blanket_salt=blanket)
    tallies.export_to_xml()  # or pass into openmc.Model

After the run, results are extracted with:

    summary = read_breeding_results("statepoint.X.h5",
                                    fuel_salt=fuel,
                                    blanket_salt=blanket)
    print(summary)  # {"BR": ..., "BR_sigma": ..., "eta": ..., ...}
"""
from __future__ import annotations

from typing import Iterable

import openmc


# Reaction MT numbers / score strings. We use openmc's named scores
# where they exist; everything else is by MT.
SCORES = ["fission", "absorption", "(n,gamma)"]

# Isotopes of interest. For the v0.4.0 first-light run only 233U and
# 232Th are present in the material recipes; 234U / 233Pa appear if/when
# depletion is added. We tally them anyway so the same module works
# unchanged once depletion is wired in.
NUCLIDES_FISSILE = ["U233", "U235"]
NUCLIDES_FERTILE = ["Th232", "U234", "Pa233"]


def build_breeding_tallies(
    *,
    fuel_salt: openmc.Material,
    blanket_salt: openmc.Material | None = None,
) -> openmc.Tallies:
    """Build the BR tally set.

    Parameters
    ----------
    fuel_salt:
        The OpenMC ``Material`` for the fuel salt (233U-bearing). Must
        be the same object that is attached to the geometry, so that
        the material filter resolves correctly.
    blanket_salt:
        Optional blanket-salt material (232Th-bearing). For the unit
        cell prototype this is the interstitial salt; for the full
        core it is the annular blanket. If omitted, only the fuel
        salt is tallied (useful for sanity-checking against an
        all-fuel-only run).

    Returns
    -------
    openmc.Tallies
        A tallies collection ready to ``.export_to_xml()``.
    """
    materials = [fuel_salt]
    if blanket_salt is not None:
        materials.append(blanket_salt)

    mat_filter = openmc.MaterialFilter(materials)
    nuclides = NUCLIDES_FISSILE + NUCLIDES_FERTILE

    # Single tally with all nuclides + all scores, filtered by material.
    # Slicing happens in read_breeding_results.
    rxn = openmc.Tally(name="msbr_breeding_rates")
    rxn.filters = [mat_filter]
    rxn.nuclides = nuclides
    rxn.scores = SCORES

    # Optional: spectrum tally for plotting (cheap, helps verify
    # thermal spectrum). Energy bins chosen to match the IAEA WLUP
    # 4-group structure for quick eyeballing.
    spectrum = openmc.Tally(name="msbr_spectrum")
    spectrum.filters = [
        mat_filter,
        openmc.EnergyFilter([0.0, 0.625, 5.53e3, 8.21e5, 2.0e7]),
    ]
    spectrum.scores = ["flux"]

    return openmc.Tallies([rxn, spectrum])


def read_breeding_results(
    statepoint_path: str,
    *,
    fuel_salt: openmc.Material,
    blanket_salt: openmc.Material | None = None,
) -> dict:
    """Extract BR + supporting diagnostics from a finished statepoint.

    Returns a dict with keys:
        BR, BR_sigma             - breeding ratio + 1-sigma
        eta, eta_sigma           - neutrons produced per fissile abs.
                                   (requires nu-fission; reported as
                                   None for the v0.4.0 first-light
                                   build since we don't tally nu yet)
        capture_th232            - 232Th(n,gamma) rate (per source n)
        capture_th232_sigma      - 1-sigma on above
        absorption_u233          - 233U absorption rate (per source n)
        absorption_u233_sigma    - 1-sigma on above
        fission_u233             - 233U fission rate
        fission_u233_sigma       - 1-sigma
        spectrum                 - dict mapping material name to a 4-bin
                                   flux array (thermal/epi/fast/highest)

    Errors are propagated assuming the fission/capture tallies are
    statistically independent (true to first order for separate scores
    in the same tally) using:

        BR = N / D
        sigma_BR / BR = sqrt((sigma_N/N)^2 + (sigma_D/D)^2)
    """
    import numpy as np

    sp = openmc.StatePoint(statepoint_path)
    tally = sp.get_tally(name="msbr_breeding_rates")

    def _rate(nuclide: str, score: str, mat: openmc.Material) -> tuple[float, float]:
        """Return (mean, std_dev) for (nuclide, score, material)."""
        df = tally.get_pandas_dataframe()
        # MaterialFilter labels rows by the material *id*, which openmc
        # writes as 'material' in the dataframe.
        mask = (
            (df["material"] == mat.id)
            & (df["nuclide"] == nuclide)
            & (df["score"] == score)
        )
        row = df[mask]
        if row.empty:
            return 0.0, 0.0
        return float(row["mean"].iloc[0]), float(row["std. dev."].iloc[0])

    # Numerator: 232Th(n,gamma) summed over all materials that contain Th
    cap_th_total, cap_th_var = 0.0, 0.0
    for mat in [fuel_salt, blanket_salt]:
        if mat is None:
            continue
        m, s = _rate("Th232", "(n,gamma)", mat)
        cap_th_total += m
        cap_th_var += s * s

    cap_th_sigma = cap_th_var ** 0.5

    # Denominator: 233U absorption in the fuel salt (the only place
    # 233U appears in either prototype).
    abs_u233, abs_u233_sigma = _rate("U233", "absorption", fuel_salt)
    fis_u233, fis_u233_sigma = _rate("U233", "fission", fuel_salt)

    if abs_u233 > 0.0:
        br = cap_th_total / abs_u233
        # Independent-relative-error propagation
        rel_n = (cap_th_sigma / cap_th_total) if cap_th_total > 0 else 0.0
        rel_d = abs_u233_sigma / abs_u233
        br_sigma = br * (rel_n ** 2 + rel_d ** 2) ** 0.5
    else:
        br, br_sigma = float("nan"), float("nan")

    # Spectrum (optional, won't crash if not present)
    spectrum_data: dict[str, list[float]] = {}
    try:
        spec = sp.get_tally(name="msbr_spectrum")
        df = spec.get_pandas_dataframe()
        for mat in [fuel_salt, blanket_salt]:
            if mat is None:
                continue
            rows = df[df["material"] == mat.id].sort_values("energy low [eV]")
            spectrum_data[mat.name or f"material_{mat.id}"] = rows["mean"].tolist()
    except Exception:
        pass

    return {
        "BR": br,
        "BR_sigma": br_sigma,
        "eta": None,  # requires nu-fission tally, deferred
        "eta_sigma": None,
        "capture_th232": cap_th_total,
        "capture_th232_sigma": cap_th_sigma,
        "absorption_u233": abs_u233,
        "absorption_u233_sigma": abs_u233_sigma,
        "fission_u233": fis_u233,
        "fission_u233_sigma": fis_u233_sigma,
        "spectrum": spectrum_data,
    }


def format_summary(results: dict) -> str:
    """Pretty-print BR results for CI step summaries / logs."""
    lines = []
    lines.append("MSBR breeding-ratio summary")
    lines.append("-" * 40)
    if results["BR"] == results["BR"]:  # not NaN
        lines.append(f"  BR = {results['BR']:.4f} +/- {results['BR_sigma']:.4f}")
    else:
        lines.append("  BR = (undefined; 233U absorption was zero)")
    lines.append(
        f"  232Th(n,g) = {results['capture_th232']:.4e}"
        f" +/- {results['capture_th232_sigma']:.2e}"
    )
    lines.append(
        f"  233U abs   = {results['absorption_u233']:.4e}"
        f" +/- {results['absorption_u233_sigma']:.2e}"
    )
    lines.append(
        f"  233U fis   = {results['fission_u233']:.4e}"
        f" +/- {results['fission_u233_sigma']:.2e}"
    )
    if results["spectrum"]:
        lines.append("")
        lines.append("  4-group flux (thermal / epi / fast / fastest):")
        for mat_name, bins in results["spectrum"].items():
            bins_s = "  ".join(f"{b:.3e}" for b in bins)
            lines.append(f"    {mat_name:18s}  {bins_s}")
    lines.append("")
    lines.append("ORNL-4528 reference design (Table 6.3): BR = 1.06")
    return "\n".join(lines)


__all__ = [
    "build_breeding_tallies",
    "read_breeding_results",
    "format_summary",
    "NUCLIDES_FISSILE",
    "NUCLIDES_FERTILE",
    "SCORES",
]
