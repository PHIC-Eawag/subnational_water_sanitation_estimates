# -------------------------------------------------------
# Map raw (observed) survey sanitation estimates
#
# Reattaches the region-level survey estimates (outcome_value) used to
# train the models to the boundary polygons they were sampled over, and
# draws a choropleth of the *observed* estimates — the survey-data
# counterpart to the modelled prediction maps.
#
# This also writes a reusable "survey estimate + geometry" layer
# (GeoPackage) that the survey-vs-prediction comparison (Task B) builds on.
#
# Why a rejoin is needed
# ----------------------
# The survey estimate lives in the training CSV keyed by
# (country_cov, HH7_region_cov); the geometry lives in the sampling
# shapefile. There is no stored polygon id linking the two, so we
# reconstruct the region key. The key that ended up in the training data
# is a *coalesced* region name built during covariate sampling
# (01_data_preparation/03_sampling_geospatial_data.ipynb, cell
# `standardise_region_fields`):
#     HH7 = first non-empty of
#           [HH7, MICSGEO, DHSREGEN, REGNAME, adm1_name, ADM1_EN, NAME_1]
# We replay that coalescing on the shapefile, normalise names, join on
# (country, region_key), and fall back to a within-country fuzzy match for
# the residual DHS spelling differences.
# -------------------------------------------------------

import os
import re
import unicodedata
from difflib import SequenceMatcher

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# -------------------------------------------------------
# 1.  Paths
# -------------------------------------------------------

TRAIN_DIR   = "data/processed/training_subcomponents"
SHP_DIR     = "data/processed/survey_boundaries"
FIGURE_DIR  = "outputs/figures/v2"
OUTPUT_DIR  = "outputs/survey_estimates"
os.makedirs(FIGURE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

BOUNDARY_SHP = os.path.join(SHP_DIR, "all_selected_boundaries_for_sampling_v2.shp")

OUTCOMES = [
    {"name": "basic_sanitation",
     "train": "basic_sanitation_training_with_covariates_v2.csv",
     "label": "Subnational survey estimates of\nat least basic sanitation",
     "cmap":  "Greens"},
    {"name": "open_defecation",
     "train": "open_defecation_training_with_covariates_v2.csv",
     "label": "Subnational survey estimates of\nopen defecation",
     "cmap":  "Oranges"},
]

# -------------------------------------------------------
# 2.  Plot style (matches 01_map_sanitation_training_data.py)
# -------------------------------------------------------

EQUAL_EARTH_CRS = "+proj=eqearth +lon_0=0 +datum=WGS84 +units=m +no_defs"
FIG_WIDTH, FIG_HEIGHT, DPI = 7.09, 3.5, 300
WORLD_COLOUR = "#e6e6e6"   # background countries
NODATA_EDGE  = "#999999"

mpl.rcParams.update({
    "font.family":     "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica Neue", "Helvetica", "DejaVu Sans"],
    "font.size":       7,
    "axes.titlesize":  8,
    "figure.dpi":      DPI,
    "savefig.dpi":     DPI,
    "hatch.linewidth": 0.3,
})

# Priority order for the coalesced region name (see cell `standardise_region_fields`)
REGION_NAME_PRIORITY = ["HH7", "MICSGEO", "DHSREGEN", "REGNAME",
                        "adm1_name", "ADM1_EN", "NAME_1"]
FUZZY_CUTOFF = 0.88   # within-country Jaro-ish ratio for the fuzzy fallback

# -------------------------------------------------------
# 3.  Name-key helpers
# -------------------------------------------------------

_EMPTY = {"", "none", "nan", "null", "na"}


def clean_key(x):
    """Accent-strip / lowercase / de-punctuate a name (mirrors clean_key in
    01_data_preparation/02_matching_survey_gadm_names.qmd)."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return ""
    s = str(x).replace("\r", " ").replace("\n", " ").strip().lower()
    if s in _EMPTY:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def coalesce_region_name(row):
    """First non-empty value across the priority name fields."""
    for col in REGION_NAME_PRIORITY:
        if col in row.index:
            v = row[col]
            if v is not None and str(v).strip().lower() not in _EMPTY:
                return v
    return None


def best_fuzzy(target, candidates):
    """Return (candidate, score) for the closest candidate string, or (None, 0)."""
    best, best_score = None, 0.0
    for c in candidates:
        score = SequenceMatcher(None, target, c).ratio()
        if score > best_score:
            best, best_score = c, score
    return best, best_score


# -------------------------------------------------------
# 4.  Load boundaries and build the region key
# -------------------------------------------------------

print("Loading boundary shapefile …")
bnd = gpd.read_file(BOUNDARY_SHP)
print(f"  {len(bnd):,} boundary polygons | CRS: {bnd.crs}")

bnd["region_name"] = bnd.apply(coalesce_region_name, axis=1)
bnd["country_key"] = bnd["country"].map(clean_key)
bnd["region_key"]  = bnd["region_name"].map(clean_key)
bnd["join_key"]    = bnd["country_key"] + "||" + bnd["region_key"]

# Dissolve any duplicate (country, region) polygons into one geometry so each
# surveyed region maps to a single feature.
bnd = (bnd[["country", "country_key", "region_name", "region_key",
            "join_key", "geometry"]]
       .dissolve(by="join_key", aggfunc="first")
       .reset_index())
print(f"  {len(bnd):,} unique surveyed regions after dissolve")


# -------------------------------------------------------
# 5.  Join survey estimates and draw one map per outcome
# -------------------------------------------------------

def load_estimates(train_file):
    """Region-level observed estimate keyed by (country_cov, HH7_region_cov).

    Averaged where a region has >1 row (e.g. multiple survey rounds); simple
    (unweighted) mean, consistent with the rest of the paper which does not
    apply population weights.
    """
    df = pd.read_csv(os.path.join(TRAIN_DIR, train_file),
                     usecols=["country_cov", "HH7_region_cov",
                              "outcome_value", "n_households", "analysis_year"])
    df = df.dropna(subset=["outcome_value"])
    df["join_key"] = df["country_cov"].map(clean_key) + "||" + \
                     df["HH7_region_cov"].map(clean_key)
    g = (df.groupby("join_key")
           .agg(estimate=("outcome_value", "mean"),
                survey_year=("analysis_year", "max"),   # most recent survey year
                n_rows=("outcome_value", "size"),
                n_households=("n_households", "sum"),
                country_cov=("country_cov", "first"),
                region_cov=("HH7_region_cov", "first"))
           .reset_index())
    return g


def attach_estimates(bnd, est):
    """Exact join on join_key, then within-country fuzzy fallback for the rest.

    Returns (boundaries_with_estimate, unmatched_estimates_dataframe).
    """
    b = bnd.copy()
    est_i = est.set_index("join_key")
    b["estimate"]    = b["join_key"].map(est_i["estimate"])
    b["survey_year"] = b["join_key"].map(est_i["survey_year"])

    matched_keys = set(est.loc[est["join_key"].isin(b["join_key"]), "join_key"])
    unmatched = est[~est["join_key"].isin(matched_keys)].copy()

    # Fuzzy fallback: for each unmatched estimate, find the closest still-empty
    # boundary region within the same country.
    fuzzy_hits = 0
    unmatched_rows = []
    for _, row in unmatched.iterrows():
        ckey = clean_key(row["country_cov"])
        rkey = clean_key(row["region_cov"])
        pool = b[(b["country_key"] == ckey) & (b["estimate"].isna())]
        if len(pool):
            cand, score = best_fuzzy(rkey, pool["region_key"].tolist())
            if score >= FUZZY_CUTOFF:
                idx = pool.index[pool["region_key"] == cand][0]
                b.loc[idx, "estimate"]    = row["estimate"]
                b.loc[idx, "survey_year"] = row["survey_year"]
                fuzzy_hits += 1
                continue
        unmatched_rows.append(row)

    n_est = len(est)
    n_matched = n_est - len(unmatched_rows)
    print(f"    estimates matched to geometry: {n_matched}/{n_est} "
          f"({n_matched / n_est * 100:.0f}%)  "
          f"[exact {len(matched_keys)}, fuzzy {fuzzy_hits}]")
    return b, pd.DataFrame(unmatched_rows)


joined = {}
for spec in OUTCOMES:
    print(f"\n=== {spec['name']} ===")
    est = load_estimates(spec["train"])
    b, unmatched = attach_estimates(bnd, est)

    # Save the joined survey-estimate + geometry layer (reused by Task B) and
    # any unmatched estimates for manual review.
    b_out = b.dropna(subset=["estimate"]).to_crs("EPSG:4326")
    gpkg = os.path.join(OUTPUT_DIR, f"survey_estimates_{spec['name']}.gpkg")
    b_out.to_file(gpkg, driver="GPKG")
    if len(unmatched):
        unmatched.to_csv(
            os.path.join(OUTPUT_DIR, f"unmatched_estimates_{spec['name']}.csv"),
            index=False)
    print(f"    saved: {gpkg} ({len(b_out)} regions)")
    joined[spec["name"]] = b.to_crs(EQUAL_EARTH_CRS)

# -------------------------------------------------------
# 6.  Background layers — LMIC extent (data gaps) vs non-LMIC
#
#     The LMIC prediction footprint is filled as "data gap" first; surveyed
#     regions are drawn on top, so any LMIC area not covered by a survey shows
#     through as a data gap. Everything outside the LMIC set is "Not an LMIC".
# -------------------------------------------------------

print("\nLoading world background + LMIC extent …")
world = gpd.read_file(
    "https://naturalearth.s3.amazonaws.com/110m_cultural/"
    "ne_110m_admin_0_countries.zip"
).to_crs(EQUAL_EARTH_CRS)

# LMIC extent taken directly from the GADM prediction footprint (exact, all
# 130 countries) rather than matched by ISO code to the coarse world layer.
gadm = gpd.read_file(os.path.join(SHP_DIR, "gadm_lmic_pred_2024.shp")).to_crs(EQUAL_EARTH_CRS)
lmic = gadm.dissolve(by="GID_0")[["geometry"]].reset_index()
print(f"  LMIC extent: {len(lmic)} countries")

# -------------------------------------------------------
# 7.  Combined figure — a) basic sanitation (top), b) open defecation (bottom)
# -------------------------------------------------------

NOT_LMIC_COLOUR = "#f0f0f0"   # very light: background countries outside the LMIC set
GAP_COLOUR      = "#8c8c8c"   # distinctly darker mid-grey: LMIC areas with no data

fig, axes = plt.subplots(2, 1, figsize=(FIG_WIDTH, 6.5))
for ax, letter, spec in [(axes[0], "a", OUTCOMES[0]),
                         (axes[1], "b", OUTCOMES[1])]:
    ax.set_aspect("equal")
    ax.axis("off")
    # Non-LMIC background: light fill + faint diagonal hatch so it reads as
    # "out of scope" and stays distinct from low (near-white) data values.
    world.plot(ax=ax, facecolor=NOT_LMIC_COLOUR, edgecolor="#c2c2c2",
               hatch="////", linewidth=0, zorder=0)
    lmic.plot(ax=ax, color=GAP_COLOUR, linewidth=0, zorder=1)         # LMIC = data-gap base

    b_map = joined[spec["name"]]
    b_map[b_map["estimate"].notna()].plot(
        ax=ax, column="estimate", cmap=spec["cmap"], vmin=0, vmax=1,
        linewidth=0.05, edgecolor="white", zorder=2, legend=True,
        legend_kwds={"label": spec["label"], "shrink": 0.55,
                     "orientation": "vertical",
                     "format": mpl.ticker.PercentFormatter(xmax=1, decimals=0)},
    )
    world.boundary.plot(ax=ax, linewidth=0.22, edgecolor="#777777", zorder=3)
    ax.set_title(f"$\\bf{{{letter}}}$", loc="left", fontsize=8, pad=1)

# Shared categorical legend, anchored directly beneath map b
cat_handles = [
    mpatches.Patch(facecolor=GAP_COLOUR, edgecolor="none",
                   label="Low- and middle-income areas not represented in survey data"),
    mpatches.Patch(facecolor=NOT_LMIC_COLOUR, edgecolor="#cccccc",
                   label="Not classified as low- and middle-income areas in 2024"),
]
axes[1].legend(handles=cat_handles, loc="upper center", bbox_to_anchor=(0.5, -0.02),
               ncol=2, fontsize=6, frameon=False, handlelength=1.4, handleheight=1.0,
               columnspacing=2.0)

fig.subplots_adjust(hspace=-0.12)
for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig_survey_estimates_combined.{ext}")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", format=ext)
    print(f"saved: {out}")
plt.close(fig)

print("\nDone.")
