# -------------------------------------------------------
# Within-country inequality: observed vs predicted
#
# Parallel to the coverage comparison (Fig. S6): for each country, the
# within-country range (max - min across that country's surveyed admin-1
# regions) of the OBSERVED survey estimates vs the MODEL predictions, computed
# over the SAME matched regions (like-for-like). Shows that the model captures
# where inequality is greatest (correlation) but compresses its magnitude
# (points below the 1:1 line).
#
# Reads the region-matched comparison written by 08_survey_vs_prediction.py;
# does not recompute the overlay.
# -------------------------------------------------------

import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

EST_DIR    = "outputs/survey_estimates"
FIGURE_DIR = "outputs/figures/v2"
os.makedirs(FIGURE_DIR, exist_ok=True)

MIN_REGIONS = 3
OUTCOMES = [
    {"name": "basic_sanitation", "label": "at least basic sanitation", "colour": "#1a9850"},
    {"name": "open_defecation",  "label": "open defecation",           "colour": "#fd8d3c"},
]

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica Neue", "Helvetica", "DejaVu Sans"],
    "font.size": 8, "figure.dpi": 300, "savefig.dpi": 300,
})


def country_ranges(outcome):
    t = pd.read_csv(os.path.join(EST_DIR, f"survey_vs_prediction_{outcome}.csv"))
    t = t.dropna(subset=["pred_area"])
    g = (t.groupby("country")
           .agg(n=("estimate", "count"),
                obs_range=("estimate", lambda x: (x.max() - x.min()) * 100),
                pred_range=("pred_area", lambda x: (x.max() - x.min()) * 100),
                survey_year=("survey_year", "median"),
                iou=("iou", "mean"))
           .reset_index())
    return g[g["n"] >= MIN_REGIONS].copy()


# colour = survey year, size = mean boundary concordance (IoU) — as in Fig. S6
SIZE_MIN, SIZE_MAX = 8, 42
YEAR_MIN, YEAR_MAX = 2015, 2024
CMAP = "plasma_r"
def iou_to_size(v):
    return SIZE_MIN + np.clip(v, 0, 1) * (SIZE_MAX - SIZE_MIN)

fig, axes = plt.subplots(1, 2, figsize=(7.09, 3.8))
all_out = []
for ax, spec, letter, title in zip(
        axes, OUTCOMES, ["a", "b"], ["Basic sanitation", "Open defecation"]):
    g = country_ranges(spec["name"])
    g["outcome"] = spec["name"]
    all_out.append(g)

    sc = ax.scatter(g["obs_range"], g["pred_range"],
                    c=g["survey_year"], cmap=CMAP, vmin=YEAR_MIN, vmax=YEAR_MAX,
                    s=iou_to_size(g["iou"]), alpha=0.82,
                    linewidths=0.3, edgecolors="#333333")
    hi = max(g["obs_range"].max(), g["pred_range"].max()) * 1.05
    ax.plot([0, hi], [0, hi], ls="--", lw=0.8, color="#555555", zorder=0)
    ax.set_xlim(0, hi); ax.set_ylim(0, hi); ax.set_aspect("equal")

    ax.text(0.04, 0.96,
            f"n={len(g)} countries\nobs median={g['obs_range'].median():.0f} pp\n"
            f"pred median={g['pred_range'].median():.0f} pp",
            transform=ax.transAxes, va="top", ha="left", fontsize=6)
    ax.set_title(f"$\\bf{{{letter}}}$  {title}", loc="left", fontsize=9)
    ax.set_xlabel("Observed range (survey), p.p.")
    ax.set_ylabel("Predicted range, p.p.")
    ax.spines[["top", "right"]].set_visible(False)

cbar = fig.colorbar(sc, ax=axes, shrink=0.7, pad=0.02,
                    ticks=range(YEAR_MIN, YEAR_MAX + 1, 2))
cbar.set_label("Survey year", fontsize=7)

handles = [plt.scatter([], [], s=iou_to_size(v), color="#888888",
                       alpha=0.82, linewidths=0.3, edgecolors="#333333",
                       label=f"{v:.2f}")
           for v in (0.50, 0.75, 1.00)]
axes[0].legend(handles=handles, title="Boundary concordance (IoU)",
               loc="upper left", bbox_to_anchor=(0.03, 0.78),
               fontsize=5.5, title_fontsize=5.5,
               frameon=False, labelspacing=1.1, borderpad=0.6)

for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig_within_country_range_comparison.{ext}")
    fig.savefig(out, bbox_inches="tight", format=ext)
    print("saved:", out)
plt.close(fig)

# Per-country values (to append to Data S4)
csv = os.path.join(EST_DIR, "within_country_range_observed_vs_predicted.csv")
pd.concat(all_out, ignore_index=True).to_csv(csv, index=False)
print("saved:", csv)
