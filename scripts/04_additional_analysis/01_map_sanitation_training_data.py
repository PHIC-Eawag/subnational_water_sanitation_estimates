# -------------------------------------------------------
# Sanitation training data — survey source coverage map
#
# Colours shapefile regions by data source:
#   MICS (incl. GADM_other, GADM_wq, MICS, MICS_other, other)
#   DHS
#
# Projection : Equal Earth
# -------------------------------------------------------

import os
from pathlib import Path
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# -------------------------------------------------------
# 1.  Paths
# -------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SHP_DIR      = PROJECT_ROOT / "data/processed/survey_boundaries"
FIGURE_DIR = "outputs/figures"
os.makedirs(FIGURE_DIR, exist_ok=True)

BOUNDARY_SHP = os.path.join(SHP_DIR, "all_selected_boundaries_for_sampling_v2.shp")

# -------------------------------------------------------
# 2.  Style
# -------------------------------------------------------

EQUAL_EARTH_CRS = "+proj=eqearth +lon_0=0 +datum=WGS84 +units=m +no_defs"

FIG_WIDTH  = 7.09
FIG_HEIGHT = 3.5
DPI        = 300

MICS_COLOUR = "#2166ac"   # blue
DHS_COLOUR  = "#d6604d"   # red-orange
HI_COLOUR   = "#d9d9d9"   # grey world background

mpl.rcParams.update({
    "font.family":      "sans-serif",
    "font.sans-serif":  ["Arial", "Helvetica Neue", "Helvetica", "DejaVu Sans"],
    "font.size":        7,
    "axes.titlesize":   8,
    "figure.dpi":       DPI,
    "savefig.dpi":      DPI,
})

MICS_SOURCES = {"GADM_other", "GADM_wq", "MICS", "MICS_other", "other"}

# -------------------------------------------------------
# 3.  Load and prepare shapefile
# -------------------------------------------------------

print("Loading boundary shapefile …")
gdf = gpd.read_file(BOUNDARY_SHP)
print(f"  {len(gdf):,} regions | CRS: {gdf.crs}")
print(f"  Source values: {gdf['source'].unique().tolist()}")

# Identify country column for border dissolve
for _col in ("GID_0", "NAME_0", "ISO", "COUNTRY", "country"):
    if _col in gdf.columns:
        COUNTRY_COL = _col
        break
else:
    raise ValueError("No country column found in boundary shapefile.")

# Group source into MICS / DHS
gdf["source_group"] = gdf["source"].apply(
    lambda s: "MICS" if s in MICS_SOURCES else ("DHS" if s == "DHS" else "Other")
)

print(f"  MICS regions : {(gdf['source_group'] == 'MICS').sum():,}")
print(f"  DHS regions  : {(gdf['source_group'] == 'DHS').sum():,}")

# -------------------------------------------------------
# 4.  Reproject
# -------------------------------------------------------

print("Reprojecting …")
gdf      = gdf.to_crs(EQUAL_EARTH_CRS)
borders  = gdf[[COUNTRY_COL, "geometry"]].dissolve(by=COUNTRY_COL)

print("Loading world background …")
world = gpd.read_file(
    "https://naturalearth.s3.amazonaws.com/110m_cultural/"
    "ne_110m_admin_0_countries.zip"
)
world = world.to_crs(EQUAL_EARTH_CRS)

# -------------------------------------------------------
# 5.  Plot
# -------------------------------------------------------

print("Drawing map …")

fig, ax = plt.subplots(1, 1, figsize=(FIG_WIDTH, FIG_HEIGHT))
ax.set_aspect("equal")
ax.axis("off")

# World background
world.plot(ax=ax, color=HI_COLOUR, linewidth=0, zorder=0)

# MICS regions
gdf[gdf["source_group"] == "MICS"].plot(
    ax=ax, color=MICS_COLOUR, linewidth=0, zorder=1,
)

# DHS regions
gdf[gdf["source_group"] == "DHS"].plot(
    ax=ax, color=DHS_COLOUR, linewidth=0, zorder=1,
)

# Country borders
borders.boundary.plot(
    ax=ax, linewidth=0.25, edgecolor="#333333", zorder=2,
)

legend_handles = [
    mpatches.Patch(facecolor=MICS_COLOUR, edgecolor="none", label="MICS"),
    mpatches.Patch(facecolor=DHS_COLOUR,  edgecolor="none", label="DHS"),
    mpatches.Patch(facecolor=HI_COLOUR,   edgecolor="none", label="Not in training data"),
]
ax.legend(handles=legend_handles, loc="lower left", fontsize=6,
          frameon=False, handlelength=1.2, handleheight=1.0)

for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig3_training_data_coverage.{ext}")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", format=ext)
    print(f"  Saved: {out}")
plt.close(fig)

print("\nDone.")