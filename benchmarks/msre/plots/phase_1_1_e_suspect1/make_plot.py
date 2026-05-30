"""Phase 1.1.e Suspect-1 — basket-shell removal closes the Shen-Serpent gap.

Horizontal error-bar plot showing the dramatic +1045 pcm jump from
removing the spurious INOR-8 shell at the sample-basket position.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent

# (label, k, sigma, run_id)
runs = [
    ("Phase 1.1.d step 1\n(basket_shell=true,\nENDF/B-VIII.0 baseline)", 1.01308, 0.00036, 26637499678),
    ("Phase 1.1.e Suspect 1\n(basket_shell=false)",                       1.02353, 0.00033, 26678973305),
]
shen = 1.02132
irphe_exp = 0.99978

fig, ax = plt.subplots(figsize=(10.5, 5.0))

ys = np.arange(len(runs))[::-1]
labels = [r[0] for r in runs]
ks = np.array([r[1] for r in runs])
sigs = np.array([r[2] for r in runs])

# Color the "after" point green to emphasize the closing
colors = ["#888888", "#2ca02c"]
for i, (lbl, k, s, rid) in enumerate(runs):
    ax.errorbar([k], [ys[i]], xerr=[s], fmt="o", color=colors[i],
                capsize=5, markersize=10, linewidth=2.0)

# Annotations placed to the LEFT of points to avoid overlap with the
# Shen line and legend.
baseline = ks[0]
for i, (lbl, k, s, _) in enumerate(runs):
    y = ys[i]
    if i == 0:
        ann = f"k = {k:.5f}\n(baseline)\n824 pcm below Shen"
    else:
        dpcm = (k - baseline) * 1e5
        gap_shen = (k - shen) * 1e5
        ann = (f"k = {k:.5f}\n"
               f"+{dpcm:.0f} pcm vs baseline\n"
               f"{gap_shen:+.0f} pcm vs Shen")
    ax.text(k - 0.0012, y, ann, va="center", ha="right", fontsize=10,
            bbox=dict(boxstyle="round,pad=0.35", fc="white",
                      ec=colors[i], lw=1.2, alpha=0.95))

# Reference lines
ax.axvline(shen, color="#d62728", linestyle="--", linewidth=1.8,
           label=f"Shen-Serpent target = {shen:.5f}")
ax.axvline(irphe_exp, color="#1f77b4", linestyle=":", linewidth=1.4,
           label=f"IRPhE experimental = {irphe_exp:.5f}")

ax.set_yticks(ys)
ax.set_yticklabels(labels, fontsize=9.5)
ax.set_xlabel("k-effective (combined, het_critical, 100k × 100)")
ax.set_title("Phase 1.1.e Suspect 1 — Removing the spurious basket INOR-8 shell\n"
             "closes the Shen-Serpent gap by +1045 pcm in a single change",
             fontsize=11)
ax.set_xlim(0.994, 1.038)
ax.grid(axis="x", alpha=0.35)
# Highlight the shaded "agreement band" of +/- inter-library spread
ax.axvspan(shen - 0.00322, shen + 0.00322, alpha=0.10, color="#d62728",
           label="Inter-library spread (Phase 1.1.d step 3, ±322 pcm)")
ax.legend(loc="center left", bbox_to_anchor=(0.0, 0.5), fontsize=9, framealpha=0.95)

plt.tight_layout()
out = HERE / "basket_shell_removal.png"
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"wrote {out}")
