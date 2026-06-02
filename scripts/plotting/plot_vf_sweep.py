"""
scripts/plotting/plot_vf_sweep.py

Render the MSBR volume-fraction sweep as a Δk heatmap with the ORNL-1971
baseline marked. Reads benchmarks/msbr/results/msbr_vf_sweep.csv.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


ORNL_FUEL = 0.1222
ORNL_BLANKET = 0.0640


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default="benchmarks/msbr/results/msbr_vf_sweep.csv", type=Path)
    p.add_argument("--out", default="out/plots/msbr/vf_sweep_v04.png", type=Path)
    args = p.parse_args()

    rows = []
    with args.csv.open() as fh:
        for r in csv.DictReader(fh):
            if r.get("error"):
                continue
            rows.append({
                "f_fuel": float(r["f_fuel"]),
                "f_blanket": float(r["f_blanket"]),
                "delta_pcm": float(r["delta_pcm"]),
                "sigma_pcm": float(r["sigma_pcm"]),
                "k_het": float(r["k_het"]),
            })

    f_fuel_vals = sorted(set(r["f_fuel"] for r in rows))
    f_blank_vals = sorted(set(r["f_blanket"] for r in rows))
    Z = np.zeros((len(f_blank_vals), len(f_fuel_vals)))
    Khet = np.zeros_like(Z)
    for r in rows:
        i = f_blank_vals.index(r["f_blanket"])
        j = f_fuel_vals.index(r["f_fuel"])
        Z[i, j] = r["delta_pcm"]
        Khet[i, j] = r["k_het"]

    best = max(rows, key=lambda r: r["delta_pcm"])

    args.out.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), constrained_layout=True)

    # Panel 1: Δk heatmap
    ax = axes[0]
    im = ax.imshow(
        Z, origin="lower", aspect="auto",
        extent=[
            min(f_fuel_vals) - 0.005, max(f_fuel_vals) + 0.005,
            min(f_blank_vals) - 0.005, max(f_blank_vals) + 0.005,
        ],
        cmap="viridis",
    )
    # annotate each cell
    for r in rows:
        ax.text(
            r["f_fuel"], r["f_blanket"],
            f"{int(r['delta_pcm']):+d}\n±{int(r['sigma_pcm'])}",
            ha="center", va="center", fontsize=8.5, color="white",
            fontweight="bold",
        )
    # ORNL marker
    ax.plot(ORNL_FUEL, ORNL_BLANKET, marker="o", markersize=14,
            mfc="none", mec="red", mew=2.2, label="ORNL-1971 baseline")
    ax.plot(best["f_fuel"], best["f_blanket"], marker="*", markersize=18,
            mfc="gold", mec="black", mew=1.0, label="Δk max")
    ax.set_xlabel("fuel salt fraction")
    ax.set_ylabel("blanket salt fraction")
    ax.set_title("MSBR unit-cell Δk(het − homog) [pcm]")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.30),
              fontsize=9, ncol=2, frameon=False)
    cb = plt.colorbar(im, ax=ax, shrink=0.95)
    cb.set_label("Δk [pcm]")

    # Panel 2: k_het heatmap (for context — criticality landscape)
    ax = axes[1]
    im2 = ax.imshow(
        Khet, origin="lower", aspect="auto",
        extent=[
            min(f_fuel_vals) - 0.005, max(f_fuel_vals) + 0.005,
            min(f_blank_vals) - 0.005, max(f_blank_vals) + 0.005,
        ],
        cmap="plasma", vmin=0.6, vmax=1.6,
    )
    for r in rows:
        ax.text(
            r["f_fuel"], r["f_blanket"], f"{r['k_het']:.3f}",
            ha="center", va="center", fontsize=9, color="white",
            fontweight="bold",
        )
    # mark k=1 contour with simple per-row interpolation when feasible
    ax.plot(ORNL_FUEL, ORNL_BLANKET, marker="o", markersize=14,
            mfc="none", mec="cyan", mew=2.2, label="ORNL-1971 baseline")
    ax.plot(best["f_fuel"], best["f_blanket"], marker="*", markersize=18,
            mfc="gold", mec="black", mew=1.0, label="Δk max")
    ax.set_xlabel("fuel salt fraction")
    ax.set_ylabel("blanket salt fraction")
    ax.set_title("k_het (heterogeneous unit cell)")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.30),
              fontsize=9, ncol=2, frameon=False)
    cb2 = plt.colorbar(im2, ax=ax, shrink=0.95)
    cb2.set_label("k_het")

    fig.suptitle(
        "MSBR volume-fraction sweep — 3×3 grid (50k×120, seed=1, ENDF/B-VIII.0)",
        fontsize=11.5,
    )
    fig.savefig(args.out, dpi=150, bbox_inches="tight")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
