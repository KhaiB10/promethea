"""Phase 1.1.d step 3 — cross-section library k-eff comparison plot.

Generates a horizontal bar/errorbar chart of the three libraries vs the
Shen-Serpent target. Run once and commit the PNG.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent

# (label, k, sigma, run_id)
runs = [
    ("ENDF/B-VIII.0\n(baseline)", 1.01308, 0.00036, 26637499678),
    ("ENDF/B-VII.1",              1.01163, 0.00038, 26673557407),
    ("JEFF-3.3",                  1.01485, 0.00034, 26673563595),
]
shen = 1.02132
shen_sigma = 0.00003
irphe_exp = 0.99978

fig, ax = plt.subplots(figsize=(8.5, 4.6))

ys = np.arange(len(runs))[::-1]  # top = first
labels = [r[0] for r in runs]
ks = np.array([r[1] for r in runs])
sigs = np.array([r[2] for r in runs])

ax.errorbar(ks, ys, xerr=sigs, fmt="o", color="#1f77b4", capsize=4,
            markersize=8, linewidth=1.8, label="Promethea (this work)")

# Annotate each bar with k value + delta vs VIII.0
baseline = ks[0]
for i, (lbl, k, s, _) in enumerate(runs):
    y = ys[i]
    dpcm = (k - baseline) * 1e5
    if i == 0:
        ann = f"k = {k:.5f}\n(baseline)"
    else:
        sign = "+" if dpcm >= 0 else ""
        ann = f"k = {k:.5f}\n{sign}{dpcm:.0f} pcm vs VIII.0"
    ax.text(k + 0.0008, y, ann, va="center", ha="left", fontsize=9)

# Shen-Serpent reference line
ax.axvline(shen, color="#d62728", linestyle="--", linewidth=1.6,
           label=f"Shen-Serpent target = {shen:.5f}")
# Experimental
ax.axvline(irphe_exp, color="#2ca02c", linestyle=":", linewidth=1.4,
           label=f"IRPhE experimental = {irphe_exp:.5f}")

ax.set_yticks(ys)
ax.set_yticklabels(labels, fontsize=10)
ax.set_xlabel("k-effective (combined, het_critical, 100k × 100)")
ax.set_title("Phase 1.1.d step 3 — Cross-section library sensitivity\n"
             "B=0.3 ppm, sharp corners, IRPhE rod config")
ax.set_xlim(1.0090, 1.0235)
ax.grid(axis="x", alpha=0.35)
ax.legend(loc="lower right", fontsize=9, framealpha=0.95)

plt.tight_layout()
out = HERE / "xs_library_comparison.png"
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"wrote {out}")
