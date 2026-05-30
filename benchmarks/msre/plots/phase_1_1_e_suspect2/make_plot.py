"""Phase 1.1.e Suspect 2: sensitivity matrix of (library) x (basket_shell).

Produces sensitivity_matrix.png — a grouped bar chart showing how the
basket-shell defect interacts with cross-section library choice. The
+1045 pcm shell effect is dominant; the library spread (~320 pcm) is
sub-dominant. The plot makes that hierarchy visually unambiguous and
provides the figure used in IRPHE_SUBMISSION_DRAFT.md and PAPER_OUTLINE.md.

All k-eff values come from artifact runs at 100k particles, 100 batches,
het_critical mode, 0.3 ppm graphite boron, sharp corners.

Source runs (GitHub Actions):
- VIII.0, shell=true:   Phase 1.1.d step 1 baseline (see PHASE_1_1_C_PLAN.md)
- VII.1,  shell=true:   Phase 1.1.d step 3 (run 26676xxx)
- JEFF-3.3, shell=true: Phase 1.1.d step 3
- VIII.0, shell=false:  Phase 1.1.e Suspect 1 (run 26678973305)
- VII.1,  shell=false:  Phase 1.1.e Suspect 2 (run 26681315297)
- JEFF-3.3, shell=false: Phase 1.1.e Suspect 2 (run 26681315771)
"""

from __future__ import annotations

import os

import matplotlib.pyplot as plt
import numpy as np

# (k_eff, sigma) per (library, shell)
DATA = {
    ("endfb-viii.0", True):  (1.01308, 0.00036),
    ("endfb-viii.0", False): (1.02353, 0.00033),
    ("endfb-vii.1",  True):  (1.01163, 0.00038),
    ("endfb-vii.1",  False): (1.02200, 0.00037),
    ("jeff-3.3",     True):  (1.01485, 0.00034),
    ("jeff-3.3",     False): (None, None),   # filled at runtime
}

# References for horizontal lines
SHEN_K = 1.02132
SHEN_S = 0.00003
YILMAZ_CSG = 1.02122
IRPHE_EXP = 0.99978


def make_plot(jeff_off_k: float, jeff_off_s: float, out_path: str) -> None:
    DATA[("jeff-3.3", False)] = (jeff_off_k, jeff_off_s)

    libraries = ["endfb-viii.0", "endfb-vii.1", "jeff-3.3"]
    pretty = {"endfb-viii.0": "ENDF/B-VIII.0", "endfb-vii.1": "ENDF/B-VII.1", "jeff-3.3": "JEFF-3.3"}

    n = len(libraries)
    x = np.arange(n)
    w = 0.36

    fig, ax = plt.subplots(figsize=(10.5, 6.5))

    k_on  = [DATA[(lib, True)][0]  for lib in libraries]
    s_on  = [DATA[(lib, True)][1]  for lib in libraries]
    k_off = [DATA[(lib, False)][0] for lib in libraries]
    s_off = [DATA[(lib, False)][1] for lib in libraries]

    bars_on = ax.bar(x - w/2, k_on, w, yerr=s_on, capsize=4,
                     color="#c0c0c0", edgecolor="#404040",
                     label="basket_shell = true (Phase 1.1.c default — erroneous)")
    bars_off = ax.bar(x + w/2, k_off, w, yerr=s_off, capsize=4,
                      color="#2e7d32", edgecolor="#1b3a1f",
                      label="basket_shell = false (Phase 1.1.e canonical)")

    # Annotate every bar with its k-eff value
    for bar, k in zip(bars_on, k_on):
        ax.text(bar.get_x() + bar.get_width()/2, k + 0.0015,
                f"{k:.5f}", ha="center", va="bottom", fontsize=8.5, color="#404040")
    for bar, k in zip(bars_off, k_off):
        ax.text(bar.get_x() + bar.get_width()/2, k + 0.0015,
                f"{k:.5f}", ha="center", va="bottom", fontsize=8.5, color="#1b3a1f",
                weight="bold")

    # Reference horizontal lines
    ax.axhline(SHEN_K, color="#c62828", linestyle="--", linewidth=1.4,
               label=f"Shen-Serpent 2021 (VII.1): k = {SHEN_K:.5f}")
    ax.axhline(YILMAZ_CSG, color="#1565c0", linestyle=":", linewidth=1.4,
               label=f"Yilmaz CSG 2024 (VIII.0): k = {YILMAZ_CSG:.5f}")
    ax.axhline(IRPHE_EXP, color="#6a1b9a", linestyle="-.", linewidth=1.2,
               label=f"IRPhE experimental: k = {IRPHE_EXP:.5f}")

    ax.set_xticks(x)
    ax.set_xticklabels([pretty[lib] for lib in libraries], fontsize=10.5)
    ax.set_ylabel("k-effective (combined)", fontsize=11)
    ax.set_title(
        "Phase 1.1.e Suspect 2 — sensitivity matrix:\n"
        "cross-section library × basket-shell configuration",
        fontsize=12)
    ax.set_ylim(0.995, 1.035)
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    ax.legend(loc="lower right", fontsize=9, framealpha=0.92)

    # Footer annotation
    fig.text(0.5, 0.01,
             "100k particles × 100 active batches | het_critical mode | "
             "0.3 ppm graphite B | sharp channel corners | OpenMC 0.14",
             ha="center", fontsize=8.5, color="#555555")

    plt.tight_layout(rect=[0, 0.03, 1, 1])
    plt.savefig(out_path, dpi=150)
    print(f"[plot] wrote {out_path}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        jeff_off_k = float(sys.argv[1])
        jeff_off_s = float(sys.argv[2])
    else:
        # placeholder pending run completion
        jeff_off_k = 1.02500
        jeff_off_s = 0.00035
    out_path = os.path.join(os.path.dirname(__file__), "sensitivity_matrix.png")
    make_plot(jeff_off_k, jeff_off_s, out_path)
