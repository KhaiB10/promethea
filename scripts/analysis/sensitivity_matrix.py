"""
scripts/analysis/sensitivity_matrix.py

Build the MSRE k-eff sensitivity matrix figure for v0.3.0 / paper
Section 5. The matrix summarizes how the canonical k-eff
(1.02364 ± 0.00016, ENDF/B-VIII.0 canonical, 200k x 200) responds to
the dominant model perturbations we have actually measured.

Sources for every number in this script
---------------------------------------

- Canonical 200k x 200 VIII.0 run k = 1.02364 +/- 0.00016
  (BLOG_POST_DRAFT.md, V0_3_0_PLAN.md)
- Library-matched VII.1 run k = 1.02202 +/- 0.00019
  -> delta_lib = (1.02202 - 1.02364) * 1e5 = -162 pcm
- 5-seed envelope (Workstream B): mean 1.02380, between-seed stdev
  ~42 pcm, pooled within-seed sigma ~49 pcm. Reported as a *spread*,
  not a directional perturbation. (V0_3_0_WORKSTREAM_B_RESULTS.md)
- Rounded-corner fillet (Workstream A, fillet_radius_cm = 0.475,
  fuel fraction f = 0.225 to match TM-730 Sec 2): result PENDING
  (50k x 120 run still queued at time of writing). Shown as an
  empty cell with an explicit "pending" label.
- Basket shell removal (basket_shell = false): adopted as canonical
  in v0.3.0 -- it IS the baseline. Drawn as the reference column
  (delta = 0 by definition).

The figure is a horizontal bar plot. Each bar = mean shift from
canonical in pcm, with an error whisker = 1-sigma propagation:

    sigma_delta = sqrt(sigma_perturbed^2 + sigma_canonical^2)

Pending rows are drawn in gray with a hatched bar of width 0 and a
"pending" annotation. This keeps the figure honest about what is
measured vs in-flight.

Output: out/sensitivity_matrix.png (300 dpi, paper-grade)
"""
from __future__ import annotations

import math
import pathlib
from dataclasses import dataclass

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


# ---------------------------------------------------------------------------
# Canonical reference and measured perturbations
# ---------------------------------------------------------------------------

K_CANONICAL = 1.02364
SIGMA_CANONICAL = 0.00016


@dataclass(frozen=True)
class Perturbation:
    label: str          # short label shown on y-axis
    detail: str         # one-line annotation shown to right of bar
    k: float | None     # measured k of the perturbed run, or None if pending
    sigma: float        # 1-sigma on the perturbed k (or on the *spread*)
    is_spread: bool = False   # True for items reported as symmetric ± spread
    pending: bool = False


# Order: top to bottom on the figure. We place "library" at the top
# (largest measured effect), then geometry items, then RNG (smallest).
PERTURBATIONS: list[Perturbation] = [
    Perturbation(
        label="XS library: VII.1",
        detail="ENDF/B-VII.1 library-matched, 200k x 200",
        k=1.02202,
        sigma=0.00019,
    ),
    Perturbation(
        label="Rounded fillet (f=0.225)",
        detail="fillet_radius_cm = 0.475, TM-730 matched fuel fraction",
        k=None,
        sigma=0.0,
        pending=True,
    ),
    Perturbation(
        label="Basket shell: present",
        detail="basket_shell = true (vs canonical false)",
        k=None,
        sigma=0.0,
        pending=True,
    ),
    Perturbation(
        label="RNG seed envelope",
        detail="5 seeds at 50k x 120, between-seed stdev",
        k=1.02380,        # mean of 5-seed envelope
        sigma=0.00042,    # between-seed stdev (treated as a spread)
        is_spread=True,
    ),
]


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def _pcm(delta_k: float) -> float:
    return delta_k * 1.0e5


def main(out_path: str = "out/sensitivity_matrix.png") -> str:
    n = len(PERTURBATIONS)
    # Wide figure: plot panel on the left, detail text panel on right.
    fig, ax = plt.subplots(figsize=(11.5, 0.78 * n + 2.0))
    # Manual margins so footnote and right-side labels both have room.
    fig.subplots_adjust(left=0.16, right=0.55, top=0.86, bottom=0.18)

    y = np.arange(n)[::-1]  # top -> bottom = first -> last
    measured_color = "#1f4e79"
    pending_color = "#9ca0a8"
    spread_color = "#5b8c5a"

    max_abs_pcm = 0.0
    for yi, p in zip(y, PERTURBATIONS):
        if p.pending:
            # Light hatched marker at zero so the row reads as a row,
            # not as missing data. Numeric/configuration text appears
            # in the right-side columns.
            ax.scatter(
                [0.0], [yi], marker="x", s=60,
                color=pending_color, linewidths=1.5,
            )
            continue

        delta = _pcm(p.k - K_CANONICAL)
        # 1-sigma on the shift (independent runs)
        sigma_delta = _pcm(math.sqrt(p.sigma ** 2 + SIGMA_CANONICAL ** 2))

        if p.is_spread:
            # Reported as +/- spread; draw a centered error bar at zero
            # with the spread as the whisker and a small marker.
            ax.errorbar(
                0.0, yi, xerr=_pcm(p.sigma),
                fmt="o", color=spread_color, ecolor=spread_color,
                elinewidth=2.4, capsize=6, markersize=6,
            )
            max_abs_pcm = max(max_abs_pcm, _pcm(p.sigma))
        else:
            color = measured_color if delta < 0 else "#a04040"
            ax.barh(
                yi, delta, height=0.55,
                color=color, edgecolor="black", linewidth=0.6,
            )
            ax.errorbar(
                delta, yi, xerr=sigma_delta,
                fmt="none", ecolor="black", elinewidth=1.0, capsize=4,
            )
            max_abs_pcm = max(max_abs_pcm, abs(delta) + sigma_delta)

    # Y axis: labels
    ax.set_yticks(y)
    ax.set_yticklabels([p.label for p in PERTURBATIONS])

    # X axis: pcm
    pad = max(40.0, 0.15 * max_abs_pcm)
    ax.set_xlim(-max_abs_pcm - pad, max_abs_pcm + pad)
    ax.axvline(0.0, color="black", linewidth=0.8)
    ax.set_xlabel(r"$\Delta k_\mathrm{eff}$ vs canonical (pcm)")

    # Right-side annotations: placed in figure (not data) coords so
    # they don't depend on x-axis limits. Two columns: numeric shift
    # + descriptive detail.
    # Figure y-coord for each row, derived from data y via axes transform.
    fig_x_num = 0.58    # numeric shift column
    fig_x_det = 0.70    # descriptive detail column
    for yi, p in zip(y, PERTURBATIONS):
        # Convert data y to figure coords
        _, fig_y = fig.transFigure.inverted().transform(
            ax.transData.transform((0.0, yi))
        )
        if p.pending:
            fig.text(
                fig_x_num, fig_y, "pending",
                va="center", ha="left", fontsize=9,
                color=pending_color, fontstyle="italic",
            )
            fig.text(
                fig_x_det, fig_y, p.detail,
                va="center", ha="left", fontsize=8.5,
                color="#555555",
            )
            continue
        if p.is_spread:
            num_txt = f"+/- {_pcm(p.sigma):.0f} pcm"
        else:
            delta = _pcm(p.k - K_CANONICAL)
            sigma_delta = _pcm(math.sqrt(p.sigma ** 2 + SIGMA_CANONICAL ** 2))
            num_txt = f"{delta:+.0f} +/- {sigma_delta:.0f} pcm"
        fig.text(
            fig_x_num, fig_y, num_txt,
            va="center", ha="left", fontsize=9, color="#222222",
            fontweight="bold",
        )
        fig.text(
            fig_x_det, fig_y, p.detail,
            va="center", ha="left", fontsize=8.5, color="#555555",
        )

    # Title block
    ax.set_title(
        "MSRE k-eff sensitivity matrix\n"
        f"Reference: ENDF/B-VIII.0 canonical, 200k x 200, "
        f"k = {K_CANONICAL:.5f} +/- {SIGMA_CANONICAL:.5f}",
        fontsize=11, pad=10,
    )

    # Light grid only on x
    ax.xaxis.grid(True, linestyle=":", linewidth=0.5, color="#cccccc")
    ax.set_axisbelow(True)

    # Spines: trim top/right
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    # Footnote
    fig.text(
        0.02, 0.05,
        "Bars: measured shifts (black whisker = combined 1 sigma).  "
        "Green dot+whisker: RNG seed spread (between-seed stdev).  "
        "Gray x: pending CI run.\n"
        "Source data: docs/V0_3_0_WORKSTREAM_B_RESULTS.md, docs/BLOG_POST_DRAFT.md.",
        fontsize=7.5, color="#555555",
    )

    # Column headers above the right-side text panel. Placed below the
    # title (top=0.86) and above the first row (~0.78 in fig coords).
    fig.text(
        fig_x_num, 0.79, "Shift",
        va="bottom", ha="left", fontsize=9, fontweight="bold", color="#222222",
    )
    fig.text(
        fig_x_det, 0.79, "Configuration",
        va="bottom", ha="left", fontsize=9, fontweight="bold", color="#222222",
    )

    out = pathlib.Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return str(out)


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "out/sensitivity_matrix.png"
    path = main(target)
    print(f"Wrote {path}")
