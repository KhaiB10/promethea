"""
scripts/analysis/vf_sweep.py

Analyze the MSBR volume-fraction sweep CSV produced by
``benchmarks.msbr.run_vf_sweep``.

Reads ``benchmarks/msbr/results/msbr_vf_sweep.csv`` (or an explicit path)
and:

  1. Finds the grid point with maximum Δk.
  2. Compares that maximum against the ORNL-1971 baseline
     (f_fuel = 0.1222, f_blanket = 0.0640).
  3. Reports the offset in pcm and the z-score
     ``(Δk_max − Δk_ORNL) / sqrt(σ_max² + σ_ORNL²)``.
  4. If a fine enough grid is present, fits a quadratic surface
     ``Δk(f_fuel, f_blanket)`` and reports the analytic maximum.
  5. Emits a results doc fragment in Markdown.

Usage:
    python scripts/analysis/vf_sweep.py [--csv PATH] [--out PATH]

A non-zero z-score above ~5 means the ORNL choice is *measurably*
sub-optimal in the unit-cell sense. Anything above ~3 is at least worth
flagging as a candidate finding.

Note: a unit-cell Δk maximum is **not** the same as a reactor optimum.
ORNL-1971 traded a fraction of unit-cell reactivity for breeding-ratio
and reprocessing-cycle headroom in the full core. The point of this
analysis is only to *quantify* the trade, not to claim the ORNL design
was wrong.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np


ORNL_FUEL = 0.1222
ORNL_BLANKET = 0.0640


def _load(csv_path: Path) -> list[dict]:
    rows = []
    with csv_path.open() as fh:
        for r in csv.DictReader(fh):
            if r.get("error"):
                continue
            try:
                rows.append({
                    "f_fuel": float(r["f_fuel"]),
                    "f_blanket": float(r["f_blanket"]),
                    "f_graphite": float(r["f_graphite"]),
                    "delta_pcm": float(r["delta_pcm"]),
                    "sigma_pcm": float(r["sigma_pcm"]),
                    "k_het": float(r["k_het"]),
                    "k_homog": float(r["k_homog"]),
                })
            except (KeyError, ValueError):
                continue
    return rows


def _find_ornl_row(rows: list[dict], tol: float = 1.0e-3) -> dict | None:
    """Return the row closest to the ORNL baseline, if within `tol`."""
    if not rows:
        return None
    best = min(
        rows,
        key=lambda r: (r["f_fuel"] - ORNL_FUEL) ** 2
                      + (r["f_blanket"] - ORNL_BLANKET) ** 2,
    )
    d = math.hypot(best["f_fuel"] - ORNL_FUEL, best["f_blanket"] - ORNL_BLANKET)
    return best if d <= tol else None


def _fit_quadratic(rows: list[dict]) -> dict | None:
    """Fit Δk(x,y) = a + b*x + c*y + d*x² + e*y² + f*x*y.

    Returns dict with the analytic stationary point and fit residuals,
    or None if the system is rank-deficient.
    """
    if len(rows) < 6:
        return None
    x = np.array([r["f_fuel"] for r in rows])
    y = np.array([r["f_blanket"] for r in rows])
    z = np.array([r["delta_pcm"] for r in rows])
    A = np.column_stack([np.ones_like(x), x, y, x * x, y * y, x * y])
    try:
        coef, *_ = np.linalg.lstsq(A, z, rcond=None)
    except np.linalg.LinAlgError:
        return None
    a, b, c, d, e, f = coef
    # Stationary point: ∂/∂x = b + 2dx + fy = 0; ∂/∂y = c + 2ey + fx = 0
    M = np.array([[2 * d, f], [f, 2 * e]])
    rhs = np.array([-b, -c])
    if abs(np.linalg.det(M)) < 1.0e-12:
        return {"coef": coef.tolist(), "stationary": None}
    xs, ys = np.linalg.solve(M, rhs)
    z_at = a + b * xs + c * ys + d * xs * xs + e * ys * ys + f * xs * ys
    pred = A @ coef
    residuals = z - pred
    return {
        "coef": coef.tolist(),
        "stationary": {"f_fuel": float(xs), "f_blanket": float(ys), "delta_pcm": float(z_at)},
        "residual_rms": float(np.sqrt(np.mean(residuals ** 2))),
        "is_maximum": bool(d < 0 and e < 0 and (4 * d * e - f * f) > 0),
    }


def analyze(csv_path: Path, out_md: Path | None = None) -> dict:
    rows = _load(csv_path)
    if not rows:
        raise SystemExit(f"no usable rows in {csv_path}")

    # Maximum Δk grid point.
    best = max(rows, key=lambda r: r["delta_pcm"])
    # ORNL baseline (closest grid point, if present).
    ornl = _find_ornl_row(rows)

    if ornl is not None:
        d_pcm = best["delta_pcm"] - ornl["delta_pcm"]
        s_pcm = math.sqrt(best["sigma_pcm"] ** 2 + ornl["sigma_pcm"] ** 2)
        z = d_pcm / s_pcm if s_pcm > 0 else float("inf")
    else:
        d_pcm = s_pcm = z = None

    quad = _fit_quadratic(rows)

    print(f"[vf_sweep] {len(rows)} usable grid points")
    print(f"[vf_sweep] Δk-max grid point:")
    print(f"           f_fuel={best['f_fuel']:.4f}, f_blanket={best['f_blanket']:.4f}")
    print(f"           Δk = {best['delta_pcm']:+.0f} ± {best['sigma_pcm']:.0f} pcm")
    if ornl is not None:
        print(f"[vf_sweep] ORNL baseline grid point:")
        print(f"           f_fuel={ornl['f_fuel']:.4f}, f_blanket={ornl['f_blanket']:.4f}")
        print(f"           Δk = {ornl['delta_pcm']:+.0f} ± {ornl['sigma_pcm']:.0f} pcm")
        print(f"[vf_sweep] offset: {d_pcm:+.0f} ± {s_pcm:.0f} pcm  (z = {z:+.2f})")
    if quad and quad.get("stationary"):
        s = quad["stationary"]
        kind = "MAX" if quad["is_maximum"] else "saddle/min"
        print(f"[vf_sweep] quadratic fit stationary point ({kind}):")
        print(f"           f_fuel={s['f_fuel']:.4f}, f_blanket={s['f_blanket']:.4f}")
        print(f"           Δk(fit) = {s['delta_pcm']:+.0f} pcm")
        print(f"           residual rms = {quad['residual_rms']:.0f} pcm")

    payload = {
        "n_points": len(rows),
        "grid_max": best,
        "ornl_baseline_grid_point": ornl,
        "offset_pcm": d_pcm,
        "offset_sigma_pcm": s_pcm,
        "z_score": z,
        "quadratic_fit": quad,
    }

    if out_md is not None:
        out_md.parent.mkdir(parents=True, exist_ok=True)
        with out_md.open("w") as fh:
            fh.write("# MSBR unit-cell volume-fraction sweep (v0.4.0)\n\n")
            fh.write(f"Grid points scanned: **{len(rows)}**\n\n")
            fh.write("## Δk-maximum grid point\n\n")
            fh.write(f"- f_fuel = {best['f_fuel']:.4f}\n")
            fh.write(f"- f_blanket = {best['f_blanket']:.4f}\n")
            fh.write(f"- f_graphite = {best['f_graphite']:.4f}\n")
            fh.write(f"- Δk = **{best['delta_pcm']:+.0f} ± {best['sigma_pcm']:.0f} pcm**\n\n")
            if ornl is not None:
                fh.write("## Versus ORNL-1971 baseline\n\n")
                fh.write(f"- ORNL baseline grid point: f_fuel={ornl['f_fuel']:.4f}, f_blanket={ornl['f_blanket']:.4f}\n")
                fh.write(f"- ORNL Δk = {ornl['delta_pcm']:+.0f} ± {ornl['sigma_pcm']:.0f} pcm\n")
                fh.write(f"- Offset: **{d_pcm:+.0f} ± {s_pcm:.0f} pcm**  (z = {z:+.2f})\n\n")
            if quad and quad.get("stationary"):
                s = quad["stationary"]
                kind = "**maximum**" if quad["is_maximum"] else "saddle/minimum"
                fh.write("## Quadratic surface fit\n\n")
                fh.write(f"Analytic stationary point ({kind}):\n\n")
                fh.write(f"- f_fuel = {s['f_fuel']:.4f}\n")
                fh.write(f"- f_blanket = {s['f_blanket']:.4f}\n")
                fh.write(f"- Δk(fit) = {s['delta_pcm']:+.0f} pcm\n")
                fh.write(f"- residual RMS = {quad['residual_rms']:.0f} pcm\n\n")
            fh.write("## Interpretation\n\n")
            fh.write("Unit-cell Δk is *not* the full-core reactivity. ORNL-1971\n")
            fh.write("traded unit-cell heterogeneity gain for breeding-ratio and\n")
            fh.write("reprocessing-cycle margin in the integrated core design.\n")
            fh.write("This sweep only quantifies the unit-cell trade.\n")
        print(f"[vf_sweep] wrote {out_md}")

    return payload


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--csv",
        default="benchmarks/msbr/results/msbr_vf_sweep.csv",
        type=Path,
    )
    p.add_argument(
        "--out",
        default="benchmarks/msbr/results/vf_sweep_v04.md",
        type=Path,
    )
    p.add_argument(
        "--json-out",
        default="out/vf_sweep_analysis.json",
        type=Path,
    )
    args = p.parse_args()
    payload = analyze(args.csv, args.out)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, default=float))
    print(f"[vf_sweep] wrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
