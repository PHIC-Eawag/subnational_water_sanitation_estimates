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
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# -------------------------------------------------------
# 1.  Paths
# -------------------------------------------------------

SHP_DIR = os.path.expanduser(
    "~/Documents/GitHub/mapping_sanitation_access_LMICs/outputs/02_boundary_files"
)
FIGURE_DIR = "outputs/figures"
os.makedirs(FIGURE_DIR, exist_ok=True)

BOUNDARY_SHP = os.path.join(SHP_DIR, "all_selected_boundaries_for_sampling_v2.shp")

# -------------------------------------------------------
# 2.  Style
# -------------------------------------------------------

EQUAL_EARTH_CRS = "+proj=eqearth +lon_0=0 +datum=WGS84 +units=m +no_defs"

# Nature Water double-column = 180 mm = 7.09 in
# At 300 DPI this is 2127 px wide — correct for print submission.
# Font sizes are in points (1/72 in), so 6 pt on a 7.09 in figure
# is correct journal body size.
FIG_WIDTH  = 7.09
FIG_HEIGHT = 3.9
DPI        = 300

MICS_COLOUR = "#2166ac"
DHS_COLOUR  = "#d6604d"
HI_COLOUR   = "#d9d9d9"

mpl.rcParams.update({
    "font.family":      "sans-serif",
    "font.sans-serif":  ["Arial", "Helvetica Neue", "Helvetica", "DejaVu Sans"],
    "font.size":        1.2,
    "axes.titlesize":   1.4,
    "legend.fontsize":  1.2,
    "figure.dpi":       DPI,
    "savefig.dpi":      DPI,
    # Prevent matplotlib from adding any default edge colours
    "patch.edgecolor":  "none",
    "patch.linewidth":  0,
})

MICS_SOURCES = {"GADM_other", "GADM_wq", "MICS", "MICS_other", "other"}

# -------------------------------------------------------
# 3.  Load and prepare shapefile
# -------------------------------------------------------

print("Loading boundary shapefile …")
gdf = gpd.read_file(BOUNDARY_SHP)
print(f"  {len(gdf):,} regions | CRS: {gdf.crs}")
print(f"  Source values: {gdf['source'].unique().tolist()}")

for _col in ("GID_0", "NAME_0", "ISO", "COUNTRY", "country"):
    if _col in gdf.columns:
        COUNTRY_COL = _col
        break
else:
    raise ValueError("No country column found in boundary shapefile.")

gdf["source_group"] = gdf["source"].apply(
    lambda s: "MICS" if s in MICS_SOURCES else ("DHS" if s == "DHS" else "Other")
)

print(f"  MICS regions : {(gdf['source_group'] == 'MICS').sum():,}")
print(f"  DHS regions  : {(gdf['source_group'] == 'DHS').sum():,}")

# -------------------------------------------------------
# 4.  Reproject
# -------------------------------------------------------

print("Reprojecting …")
gdf     = gdf.to_crs(EQUAL_EARTH_CRS)
borders = gdf[[COUNTRY_COL, "geometry"]].dissolve(by=COUNTRY_COL)

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

# World background — edgecolor and linewidth both silenced explicitly
world.plot(ax=ax, color=HI_COLOUR, edgecolor="none", linewidth=0, zorder=0)

# MICS regions
gdf[gdf["source_group"] == "MICS"].plot(
    ax=ax, color=MICS_COLOUR, edgecolor="none", linewidth=0, zorder=1,
)

# DHS regions
gdf[gdf["source_group"] == "DHS"].plot(
    ax=ax, color=DHS_COLOUR, edgecolor="none", linewidth=0, zorder=1,
)

# Thin country border overlay drawn last
borders.boundary.plot(
    ax=ax, linewidth=0.2, edgecolor="#555555", zorder=2,
)

legend_handles = [
    mpatches.Patch(facecolor=MICS_COLOUR, edgecolor="none", label="MICS"),
    mpatches.Patch(facecolor=DHS_COLOUR,  edgecolor="none", label="DHS"),
    mpatches.Patch(facecolor=HI_COLOUR,   edgecolor="#aaaaaa", linewidth=0.3,
                   label="Not in training data"),
]
ax.legend(
    handles=legend_handles,
    loc="lower left",
    fontsize= 5,
    frameon=False,
    handlelength=1.0,
    handleheight=0.9,
    borderpad=0,
    labelspacing=0.3,
)

# Save — PDF is vector and has no DPI concept; PNG at 300 DPI for submission
for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig3_training_data_coverage.{ext}")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", pad_inches=0.02, format=ext)
    print(f"  Saved: {out}")
plt.close(fig)

print("\nDone.")