# -------------------------------------------------------
# Grouped SHAP importance (regrouped categories)
#
# Re-aggregates the existing per-predictor SHAP importances (n=250 subsample,
# the values used in the manuscript) into the revised category scheme — it does
# NOT recompute SHAP. The base feature->category map is read from the model
# training script (single source of truth) and then regrouped:
#   * JMP + wastewater            -> "Sanitation"
#   * wetlands + peatland         -> "Hydrology & Soil"
#   * topography + vegetation     -> "Terrain & vegetation"
# -------------------------------------------------------

import os
import re
import ast
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

TRAIN_SCRIPT = "scripts/03_model_training/02b_tabpfn_loco_cv_sanitation.py"
IMP = {
    "basic_sanitation": ("outputs/descriptive_statistics/v2/"
                         "basic_sanitation_tabpfn_shap_importance_k45_n250.csv"),
    "open_defecation":  ("outputs/descriptive_statistics/v2/"
                         "open_defecation_tabpfn_shap_importance_k90_n250.csv"),
}
FIGURE_DIR = "outputs/figures/v2"
os.makedirs(FIGURE_DIR, exist_ok=True)

TITLES = {"basic_sanitation": "Basic sanitation", "open_defecation": "Open defecation"}

# -------------------------------------------------------
# 1.  Base map (from training script) + regroup rules
# -------------------------------------------------------

_src = open(TRAIN_SCRIPT).read()
FEATURE_CATEGORY_MAP = ast.literal_eval(
    re.search(r"FEATURE_CATEGORY_MAP\s*=\s*(\{.*?\n\})", _src, re.S).group(1))

WASTEWATER = {"ww_collection_percent", "ww_treatment_percent", "ww_reuse_percent"}
TO_HYDRO   = {"TootchiEtAl_WetlandsRegularlyFlooded", "CIFOR_TropicalPeatlandExtent"}

def regroup(feature, cat):
    if cat == "JMP" or feature in WASTEWATER:
        return "National sanitation estimates"
    if feature in TO_HYDRO:
        return "Hydrology & Soil"
    if cat in ("Topography", "Vegetation texture", "Vegetation coverage"):
        return "Terrain & vegetation"
    return cat

NEW_MAP = {f: regroup(f, c) for f, c in FEATURE_CATEGORY_MAP.items()}

COLOURS = {
    "National sanitation estimates": "#c51b7d",
    "Human presence":              "#d6604d",
    "Terrain & vegetation":        "#1b7837",
    "Climate":                     "#4393c3",
    "Hydrology & Soil":            "#5aae61",
    "Socio-economic & governance": "#e08214",
    "Region size":                 "#878787",
}

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica Neue", "Helvetica", "DejaVu Sans"],
    "font.size": 8, "figure.dpi": 300, "savefig.dpi": 300,
})

# -------------------------------------------------------
# 2.  Aggregate + plot
# -------------------------------------------------------

def shares(outcome):
    d = pd.read_csv(IMP[outcome])
    col = "mean_abs_shap" if "mean_abs_shap" in d.columns else d.columns[-1]
    d["grp"] = d["feature"].map(NEW_MAP)
    if d["grp"].isna().any():
        raise ValueError(f"Unmapped features: {d.loc[d['grp'].isna(),'feature'].tolist()}")
    g = d.groupby("grp")[col].agg(total="sum", n="count")
    g["share"] = g["total"] / g["total"].sum() * 100
    return g.sort_values("share")   # ascending for barh (largest on top)

fig, axes = plt.subplots(2, 1, figsize=(7.0, 8.4))
for ax, outcome, letter in [(axes[0], "basic_sanitation", "a"),
                            (axes[1], "open_defecation", "b")]:
    g = shares(outcome)
    ax.barh(g.index, g["share"],
            color=[COLOURS[c] for c in g.index], edgecolor="none")
    for y, (grp, r) in enumerate(g.iterrows()):
        ax.text(r["share"] + 0.6, y, f"{r['share']:.1f}%  (n={int(r['n'])})",
                va="center", ha="left", fontsize=7)
    ax.set_xlim(0, max(g["share"]) * 1.28)
    ax.set_xlabel("Share of total mean |SHAP| (%)")
    ax.set_title(f"$\\bf{{{letter}}}$  {TITLES[outcome]}", loc="left", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)

fig.tight_layout()
for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig_shap_grouped_importance.{ext}")
    fig.savefig(out, bbox_inches="tight", format=ext)
    print("saved:", out)
plt.close(fig)
