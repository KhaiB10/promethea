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

    # Build edge arrays for pcolormesh so each value sits at a true cell center.
    def cell_edges(vals):
        e = [vals[0] - (vals[1] - vals[0]) / 2]
        for i in range(len(vals) - 1):
            e.append((vals[i] + vals[i + 1]) / 2)
        e.append(vals[-1] + (vals[-1] - vals[-2]) / 2)
        return np.array(e)
    fuel_edges = cell_edges(f_fuel_vals)
    blank_edges = cell_edges(f_blank_vals)

    args.out.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), constrained_layout=True)

    # Panel 1: Δk heatmap
    ax = axes[0]
    im = ax.pcolormesh(
        fuel_edges, blank_edges, Z,
        cmap="viridis", shading="flat",
    )
    # text at cell center, with row-dependent offset for highlighted cells so markers don't overlap
    for r in rows:
        is_best = abs(r["f_fuel"]-best["f_fuel"])<1e-6 and abs(r["f_blanket"]-best["f_blanket"])<1e-6
        is_ornl = abs(r["f_fuel"]-ORNL_FUEL)<1e-6 and abs(r["f_blanket"]-ORNL_BLANKET)<1e-6
        # cell half-height in blanket axis
        i = f_blank_vals.index(r["f_blanket"])
        cell_h = blank_edges[i + 1] - blank_edges[i]
        dy = +cell_h * 0.20 if (is_best or is_ornl) else 0.0
        ax.text(
            r["f_fuel"], r["f_blanket"] + dy,
            f"{int(r['delta_pcm']):+d}\n±{int(r['sigma_pcm'])}",
            ha="center", va="center", fontsize=8.5, color="white",
            fontweight="bold",
        )
    # markers placed below text inside their cell
    ornl_i = f_blank_vals.index(ORNL_BLANKET)
    ornl_dy = -0.25 * (blank_edges[ornl_i + 1] - blank_edges[ornl_i])
    best_i = f_blank_vals.index(best["f_blanket"])
    best_dy = -0.25 * (blank_edges[best_i + 1] - blank_edges[best_i])
    ax.plot(ORNL_FUEL, ORNL_BLANKET + ornl_dy, marker="o", markersize=10,
            mfc="none", mec="red", mew=2.2, label="ORNL-1971 baseline")
    ax.plot(best["f_fuel"], best["f_blanket"] + best_dy, marker="*", markersize=14,
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
    im2 = ax.pcolormesh(
        fuel_edges, blank_edges, Khet,
        cmap="plasma", vmin=0.6, vmax=1.6, shading="flat",
    )
    for r in rows:
        is_best = abs(r["f_fuel"]-best["f_fuel"])<1e-6 and abs(r["f_blanket"]-best["f_blanket"])<1e-6
        is_ornl = abs(r["f_fuel"]-ORNL_FUEL)<1e-6 and abs(r["f_blanket"]-ORNL_BLANKET)<1e-6
        i = f_blank_vals.index(r["f_blanket"])
        cell_h = blank_edges[i + 1] - blank_edges[i]
        dy = +cell_h * 0.20 if (is_best or is_ornl) else 0.0
        ax.text(
            r["f_fuel"], r["f_blanket"] + dy, f"{r['k_het']:.3f}",
            ha="center", va="center", fontsize=9, color="white",
            fontweight="bold",
        )
    ax.plot(ORNL_FUEL, ORNL_BLANKET + ornl_dy, marker="o", markersize=10,
            mfc="none", mec="cyan", mew=2.2, label="ORNL-1971 baseline")
    ax.plot(best["f_fuel"], best["f_blanket"] + best_dy, marker="*", markersize=14,
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
