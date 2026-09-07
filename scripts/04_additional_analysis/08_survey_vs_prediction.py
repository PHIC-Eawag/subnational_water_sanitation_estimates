# -------------------------------------------------------
# Compare observed survey estimates with model predictions
#
# Purpose: give users of the prediction dataset a basis for deciding whether
# to rely on the full model predictions or to fall back on the original survey
# estimates where these exist. For each surveyed region we compare the
# observed estimate (outcome_value, attached to the survey-fitted polygon in
# 07_map_survey_estimates.py) with the model's predicted value aggregated to
# that same footprint.
#
# NOTE: predictions are the FINAL in-sample predictions, so these agreement
# statistics are a face-validity / consistency check, not an out-of-sample
# accuracy assessment. Survey years span 2015-2024 while predictions are for
# 2024, so part of any disagreement reflects genuine temporal change rather
# than model error (see year-coloured scatter).
#
# Method — spatial overlay (no name matching)
# -------------------------------------------
# Predictions exist at GADM admin-1; survey regions do not always coincide
# with GADM admin-1 (different sources, admin levels, and boundary vintages).
# We therefore overlay each survey polygon on the GADM prediction polygons
# and take the AREA-WEIGHTED mean prediction over the intersection. This one
# operation covers every case:
#   * survey ≈ one GADM unit   -> returns that unit's prediction (direct 1:1)
#   * survey finer than GADM   -> several survey obs share one prediction
#   * survey coarser/misaligned-> area-weighted blend of overlapping units
# It needs no name matching, so it keeps the finer/custom survey regions that
# a name-only join would drop (and which skew to higher coverage).
#
# Boundary concordance is summarised per region by the Jaccard index
# (intersection-over-union, IoU; Jaccard 1912) of the survey polygon and its
# single best-overlapping GADM unit. IoU is reported as a diagnostic and used
# only to define a robustness subset (IoU >= 0.9), NOT as an inclusion gate.
# Motivation for reconciling incompatible zones: change-of-support problem
# (Gotway & Young 2002, JASA) / MAUP (Openshaw 1984).
#
# Weighting: area-weighted is the default (consistent with the rest of the
# paper, which does not use population weights). A population-weighted variant
# is reported alongside as a sensitivity check. Predictions are the FINAL
# in-sample predictions.
# -------------------------------------------------------

import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt

# -------------------------------------------------------
# 1.  Paths
# -------------------------------------------------------

PRED_DIR   = "outputs/model_performance/v2/predictions"
SHP_DIR    = "data/processed/survey_boundaries"
EST_DIR    = "outputs/survey_estimates"          # written by script 07
FIGURE_DIR = "outputs/figures/v2"
os.makedirs(FIGURE_DIR, exist_ok=True)

GADM_SHP = os.path.join(SHP_DIR, "gadm_lmic_pred_2024.shp")

OUTCOMES = [
    {"name": "basic_sanitation",
     "gpkg":  os.path.join(EST_DIR, "survey_estimates_basic_sanitation.gpkg"),
     "pred":  os.path.join(PRED_DIR, "basic_sanitation_tabpfn_lmic_predictions.csv"),
     "label": "at least basic sanitation", "colour": "#1a9850"},
    {"name": "open_defecation",
     "gpkg":  os.path.join(EST_DIR, "survey_estimates_open_defecation.gpkg"),
     "pred":  os.path.join(PRED_DIR, "open_defecation_tabpfn_lmic_predictions.csv"),
     "label": "open defecation", "colour": "#fd8d3c"},
]

EQUAL_AREA_CRS = "EPSG:8857"   # Equal Earth (equal-area) — matches repo area_km2
IOU_ROBUST     = 0.90          # subset treated as clean 1:1 for the robustness row

mpl.rcParams.update({
    "font.family":     "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica Neue", "Helvetica", "DejaVu Sans"],
    "font.size":       7, "axes.titlesize": 8, "figure.dpi": 300, "savefig.dpi": 300,
})

# -------------------------------------------------------
# 2.  Helpers
# -------------------------------------------------------

def load_predictions(gadm_shp, pred_csv):
    """GADM admin-1 geometry + predicted value + population, in equal-area CRS."""
    pred = pd.read_csv(pred_csv, usecols=["GID_1", "median", "worldpop_sum"])
    gadm = gpd.read_file(gadm_shp)[["GID_1", "geometry"]]
    gadm = gadm.merge(pred, on="GID_1", how="inner").to_crs(EQUAL_AREA_CRS)
    gadm["geometry"] = gadm.geometry.buffer(0)          # fix any invalid rings
    gadm["gadm_area"] = gadm.geometry.area
    gadm = gadm.rename(columns={"median": "pred", "worldpop_sum": "gadm_pop"})
    return gadm


def load_survey(gpkg):
    sv = gpd.read_file(gpkg)[["join_key", "country", "estimate",
                              "survey_year", "geometry"]]
    sv = sv.to_crs(EQUAL_AREA_CRS)
    sv["geometry"] = sv.geometry.buffer(0)
    sv["survey_area"] = sv.geometry.area
    return sv


def overlay_predict(sv, gadm):
    """Return per-survey-region observed/predicted table via areal overlay."""
    inter = gpd.overlay(
        sv[["join_key", "country", "estimate", "survey_area", "geometry"]],
        gadm[["GID_1", "pred", "gadm_pop", "gadm_area", "geometry"]],
        how="intersection", keep_geom_type=True,
    )
    inter["piece_area"] = inter.geometry.area
    # population in each intersection piece, assuming uniform density within GADM
    inter["piece_pop"] = inter["gadm_pop"] * (inter["piece_area"] / inter["gadm_area"])

    def agg(g):
        aw = np.average(g["pred"], weights=g["piece_area"])
        pw = (np.average(g["pred"], weights=g["piece_pop"])
              if g["piece_pop"].sum() > 0 else np.nan)
        # IoU vs the single best-overlapping GADM unit
        top = g.loc[g["piece_area"].idxmax()]
        iou = top["piece_area"] / (g["survey_area"].iloc[0] + top["gadm_area"]
                                   - top["piece_area"])
        return pd.Series({"pred_area": aw, "pred_pop": pw, "iou": iou,
                          "n_gadm": len(g)})

    out = inter.groupby("join_key").apply(agg, include_groups=False).reset_index()
    out = sv[["join_key", "country", "estimate", "survey_year"]].merge(
        out, on="join_key", how="left")
    return out


def agreement(obs, pred):
    obs, pred = np.asarray(obs, float), np.asarray(pred, float)
    m = ~(np.isnan(obs) | np.isnan(pred))
    obs, pred = obs[m], pred[m]
    err = pred - obs
    ss_res = np.sum(err ** 2)
    ss_tot = np.sum((obs - obs.mean()) ** 2)
    return {
        "n":          len(obs),
        "pearson_r":  round(np.corrcoef(obs, pred)[0, 1], 3),
        "R2_vs_1to1": round(1 - ss_res / ss_tot, 3),
        "MAE_pp":     round(np.mean(np.abs(err)) * 100, 1),
        "RMSE_pp":    round(np.sqrt(np.mean(err ** 2)) * 100, 1),
        "bias_pp":    round(np.mean(err) * 100, 1),   # predicted − observed
    }


# -------------------------------------------------------
# 3.  Run per outcome
# -------------------------------------------------------

all_stats = []
panels = []

for spec in OUTCOMES:
    print(f"\n=== {spec['name']} ===")
    gadm = load_predictions(GADM_SHP, spec["pred"])
    sv   = load_survey(spec["gpkg"])
    print(f"  survey regions: {len(sv)} | GADM units: {len(gadm)}")

    tab = overlay_predict(sv, gadm)
    n_nomatch = tab["pred_area"].isna().sum()
    if n_nomatch:
        print(f"  survey regions with no GADM overlap (dropped): {n_nomatch}")
    tab = tab.dropna(subset=["pred_area"])

    tab.to_csv(os.path.join(EST_DIR, f"survey_vs_prediction_{spec['name']}.csv"),
               index=False)

    robust = tab[tab["iou"] >= IOU_ROBUST]
    rows = [
        ("full set — area-weighted",       agreement(tab["estimate"], tab["pred_area"])),
        ("full set — population-weighted",  agreement(tab["estimate"], tab["pred_pop"])),
        (f"IoU≥{IOU_ROBUST} subset — area-weighted",
                                            agreement(robust["estimate"], robust["pred_area"])),
    ]
    # threshold sensitivity (area-weighted)
    for thr in (0.5, 0.7, 0.9):
        sub = tab[tab["iou"] >= thr]
        rows.append((f"  sensitivity IoU≥{thr} — area-weighted",
                     agreement(sub["estimate"], sub["pred_area"])))

    # agreement by survey-year bin — predictions are for 2024, so older surveys
    # are expected to diverge because of genuine change, not model error.
    year_bins = pd.cut(tab["survey_year"], [2014, 2018, 2021, 2024],
                       labels=["2015-2018", "2019-2021", "2022-2024"])
    for lab, sub in tab.groupby(year_bins, observed=True):
        rows.append((f"  survey years {lab} — area-weighted",
                     agreement(sub["estimate"], sub["pred_area"])))

    print(f"  {'subset':42s} {'n':>4} {'r':>6} {'R2':>6} {'MAE':>5} {'RMSE':>5} {'bias':>6}")
    for name, s in rows:
        print(f"  {name:42s} {s['n']:>4} {s['pearson_r']:>6} {s['R2_vs_1to1']:>6} "
              f"{s['MAE_pp']:>5} {s['RMSE_pp']:>5} {s['bias_pp']:>6}")
        all_stats.append({"outcome": spec["name"], "subset": name.strip(), **s})

    panels.append((spec, tab, robust))

pd.DataFrame(all_stats).to_csv(
    os.path.join(EST_DIR, "survey_vs_prediction_agreement_stats.csv"), index=False)

# -------------------------------------------------------
# 4.  Scatter figure
#     colour = survey year (predictions are 2024; older surveys may differ
#              because of genuine change, not model error)
#     size   = boundary concordance (IoU); smaller = less survey/GADM overlap,
#              i.e. a less reliable spatial match. A floor keeps low-IoU points
#              visible rather than vanishing.
# -------------------------------------------------------

SIZE_MIN, SIZE_MAX = 4, 26          # pt² for IoU 0 .. 1
YEAR_MIN, YEAR_MAX = 2015, 2024
# plasma reversed: the abundant recent (2022-2024) surveys render dark and
# stand out, while the sparse older surveys are light — a thin dark edge keeps
# the light points visible on the white background.
CMAP = "plasma_r"

def iou_to_size(iou):
    return SIZE_MIN + np.clip(iou, 0, 1) * (SIZE_MAX - SIZE_MIN)

fig, axes = plt.subplots(1, 2, figsize=(7.09, 3.7))
for ax, (spec, tab, robust), letter, title in zip(
        axes, panels, ["a", "b"], ["Basic sanitation", "Open defecation"]):
    sc = ax.scatter(tab["estimate"] * 100, tab["pred_area"] * 100,
                    c=tab["survey_year"], cmap=CMAP,
                    vmin=YEAR_MIN, vmax=YEAR_MAX,
                    s=iou_to_size(tab["iou"]), alpha=0.72,
                    linewidths=0.25, edgecolors="#333333")
    ax.plot([0, 100], [0, 100], ls="--", lw=0.8, color="#555555", zorder=0)
    s = agreement(tab["estimate"], tab["pred_area"])
    ax.set_title(f"$\\bf{{{letter}}}$  {title}", loc="left", fontsize=9)
    ax.set_xlabel("Observed (survey), %")
    ax.set_ylabel("Predicted, %")
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.set_aspect("equal")
    ax.text(0.04, 0.96,
            f"n={s['n']}\nMAE={s['MAE_pp'] / 100:.2f}",
            transform=ax.transAxes, va="top", ha="left", fontsize=6)
    ax.spines[["top", "right"]].set_visible(False)

# Year colourbar (integer ticks)
cbar = fig.colorbar(sc, ax=axes, shrink=0.7, pad=0.02,
                    ticks=range(YEAR_MIN, YEAR_MAX + 1, 2))
cbar.set_label("Survey year", fontsize=7)

# Size legend for IoU (boundary concordance)
handles = [plt.scatter([], [], s=iou_to_size(v), color="#888888",
                       alpha=0.72, linewidths=0.25, edgecolors="#333333",
                       label=f"{v:.2f}")
           for v in (0.25, 0.50, 1.00)]
axes[0].legend(handles=handles, title="Boundary\nconcordance (IoU)",
               loc="lower right", fontsize=5.5, title_fontsize=5.5,
               frameon=False, labelspacing=1.1, borderpad=0.8)

for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig_survey_vs_prediction.{ext}")
    fig.savefig(out, dpi=300, bbox_inches="tight", format=ext)
    print(f"\nSaved: {out}")
plt.close(fig)

print("\nDone.")
