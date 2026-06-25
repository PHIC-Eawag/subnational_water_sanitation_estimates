# -------------------------------------------------------
# Sanitation predictions — publication-quality maps
# Target journal: Nature Water
#
# Saves one PDF + PNG per panel:
#   fig1a_basic_sanitation_median.pdf/png
#   fig1b_open_defecation_median.pdf/png
#   fig2a_basic_sanitation_uncertainty.pdf/png
#   fig2b_open_defecation_uncertainty.pdf/png
#
# Projection : Equal Earth
# -------------------------------------------------------

import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize, LinearSegmentedColormap
from matplotlib.cm import ScalarMappable

# -------------------------------------------------------
# 1.  Paths
# -------------------------------------------------------

SHP_DIR    = os.path.expanduser(
    "~/Documents/GitHub/mapping_sanitation_access_LMICs/data/GADM36_boundaries"
)
PRED_DIR   = "outputs/04_model_performance/predictions"
FIGURE_DIR = "outputs/figures"
os.makedirs(FIGURE_DIR, exist_ok=True)

BS_PRED = os.path.join(PRED_DIR, "basic_sanitation_tabpfn_lmic_predictions.csv")
OD_PRED = os.path.join(PRED_DIR, "open_defecation_tabpfn_lmic_predictions.csv")

# -------------------------------------------------------
# 2.  Settings
# -------------------------------------------------------

EQUAL_EARTH_CRS = "+proj=eqearth +lon_0=0 +datum=WGS84 +units=m +no_defs"

# Each panel is one full double-column width.
# Equal Earth aspect ≈ 1.97:1 — map height derived from width.
# Extra height added below for colourbar + legend.
FIG_WIDTH   = 7.09                    # 180 mm
MAP_H       = FIG_WIDTH / 1.97        # ≈ 3.60 in
EXTRA_H     = 0.60                    # colourbar + legend below map
FIG_HEIGHT  = MAP_H + EXTRA_H        # ≈ 4.20 in per panel
DPI         = 100

NODATA_COLOUR = "#bdbdbd"
HI_COLOUR     = "#d9d9d9"

mpl.rcParams.update({
    "font.family":      "sans-serif",
    "font.sans-serif":  ["Arial", "Helvetica Neue", "Helvetica", "DejaVu Sans"],
    "font.size":        7,
    "axes.titlesize":   8,
    "axes.labelsize":   7,
    "xtick.labelsize":  6,
    "ytick.labelsize":  6,
    "legend.fontsize":  6,
    "figure.dpi":       DPI,
    "savefig.dpi":      DPI,
    "patch.edgecolor":  "none",
    "patch.linewidth":  0,
})

# -------------------------------------------------------
# 3.  Colourmaps
# -------------------------------------------------------

BS_CMAP = LinearSegmentedColormap.from_list(
    "RdYlGn_custom", ["#d73027", "#ffffbf", "#1a9850"], N=256
)
OD_CMAP = LinearSegmentedColormap.from_list(
    "BlOrRd_custom", ["#2166ac", "#fd8d3c", "#bd0026"], N=256
)
BS_UNC_CMAP = LinearSegmentedColormap.from_list(
    "YlPu_custom", ["#ffffcc", "#c994c7", "#67001f"], N=256
)
OD_UNC_CMAP = "YlOrRd"

# -------------------------------------------------------
# 4.  Load data
# -------------------------------------------------------

print("Loading shapefile …")
gdf = gpd.read_file(os.path.join(SHP_DIR, "gadm_lmics_final.shp"))

if "GID_1" not in gdf.columns:
    raise ValueError(f"GID_1 not found. Columns: {gdf.columns.tolist()}")

for _col in ("GID_0", "NAME_0", "ISO", "COUNTRY"):
    if _col in gdf.columns:
        COUNTRY_COL = _col
        break
else:
    raise ValueError("No country column found.")

print("Loading predictions …")
bs_df = pd.read_csv(BS_PRED)
od_df = pd.read_csv(OD_PRED)

gdf_bs = gdf.merge(bs_df[["GID_1","median","pi90_lower","pi90_upper"]], on="GID_1", how="left")
gdf_od = gdf.merge(od_df[["GID_1","median","pi90_lower","pi90_upper"]], on="GID_1", how="left")
gdf_bs["pi_width"] = gdf_bs["pi90_upper"] - gdf_bs["pi90_lower"]
gdf_od["pi_width"] = gdf_od["pi90_upper"] - gdf_od["pi90_lower"]

print("Reprojecting …")
gdf_bs = gdf_bs.to_crs(EQUAL_EARTH_CRS)
gdf_od = gdf_od.to_crs(EQUAL_EARTH_CRS)
borders_bs = gdf_bs[[COUNTRY_COL,"geometry"]].dissolve(by=COUNTRY_COL)
borders_od = gdf_od[[COUNTRY_COL,"geometry"]].dissolve(by=COUNTRY_COL)

print("Loading world background …")
world = gpd.read_file(
    "https://naturalearth.s3.amazonaws.com/110m_cultural/"
    "ne_110m_admin_0_countries.zip"
).to_crs(EQUAL_EARTH_CRS)

wx_min, wy_min, wx_max, wy_max = world.total_bounds

# -------------------------------------------------------
# 5.  Single-panel draw function
# -------------------------------------------------------

def save_panel(filename, gdf_panel, col, cmap, vmin, vmax,
               borders, panel_label, full_title, cbar_label,
               cbar_ticks=None, cbar_fmt="{:.0%}"):

    fig = plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))

    # Map axes occupies the top portion
    map_ax = fig.add_axes([0.01, EXTRA_H / FIG_HEIGHT + 0.04,
                           0.98, MAP_H / FIG_HEIGHT - 0.04])
    map_ax.set_xlim(wx_min, wx_max)
    map_ax.set_ylim(wy_min, wy_max)
    map_ax.set_aspect(1)
    map_ax.axis("off")

    norm = Normalize(vmin=vmin, vmax=vmax)

    world.plot(ax=map_ax, color=HI_COLOUR, edgecolor="none", linewidth=0, zorder=0)

    no_pred = gdf_panel[gdf_panel[col].isna()]
    if len(no_pred):
        no_pred.plot(ax=map_ax, color=NODATA_COLOUR, edgecolor="none",
                     linewidth=0, zorder=1)

    gdf_panel[gdf_panel[col].notna()].plot(
        ax=map_ax, column=col, cmap=cmap, norm=norm,
        edgecolor="none", linewidth=0, zorder=2,
    )

    borders.boundary.plot(ax=map_ax, linewidth=0.08, edgecolor="#555555", zorder=3)

    map_ax.set_title(
        f"$\\bf{{{panel_label}}}$  {full_title}",
        fontsize=8, loc="left", pad=1.5,
    )

    # Colourbar axes — centred strip below the map, half the previous width
    cbar_ax = fig.add_axes([0.35, 0.13, 0.30, 0.035])
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, cax=cbar_ax, orientation="horizontal")
    cbar.set_label(cbar_label, fontsize=6, labelpad=1)
    cbar.ax.tick_params(labelsize=5.5, length=1, width=0.3)
    cbar.outline.set_linewidth(0.3)

    if cbar_ticks is None:
        cbar_ticks = np.linspace(vmin, vmax, 6)
    cbar.set_ticks(cbar_ticks)
    cbar.set_ticklabels([cbar_fmt.format(t) for t in cbar_ticks])

    # Legend — left of figure, below colourbar
    if len(no_pred):
        legend_handles = [
            mpatches.Patch(facecolor=NODATA_COLOUR, edgecolor="none",
                           label="No prediction data")
        ]
        map_ax.legend(
            handles=legend_handles,
            loc="upper left",
            fontsize=4.5,
            frameon=False,
            handlelength=1.0,
            handleheight=0.8,
            borderpad=0,
            labelspacing=0.3,
        )

    for ext in ("pdf", "png"):
        out = os.path.join(FIGURE_DIR, f"{filename}.{ext}")
        fig.savefig(out, dpi=DPI, format=ext)
        print(f"  Saved: {out}")
    plt.close(fig)


# -------------------------------------------------------
# 6.  Draw all four panels
# -------------------------------------------------------

print("\nDrawing fig1a — basic sanitation median …")
save_panel(
    filename="fig1a_basic_sanitation_median",
    gdf_panel=gdf_bs, col="median", cmap=BS_CMAP, vmin=0, vmax=1,
    borders=borders_bs, panel_label="a", full_title="Basic sanitation",
    cbar_label="Estimated proportion of population with basic sanitation",
    cbar_ticks=[0.0, 0.25, 0.50, 0.75, 1.0],
)

print("Drawing fig1b — open defecation median …")
save_panel(
    filename="fig1b_open_defecation_median",
    gdf_panel=gdf_od, col="median", cmap=OD_CMAP, vmin=0, vmax=1,
    borders=borders_od, panel_label="b", full_title="Open defecation",
    cbar_label="Estimated proportion of population practising open defecation",
    cbar_ticks=[0.0, 0.25, 0.50, 0.75, 1.0],
)

pi_max = max(
    float(gdf_bs["pi_width"].quantile(0.99)),
    float(gdf_od["pi_width"].quantile(0.99)),
)
pi_max = np.ceil(pi_max * 20) / 20
print(f"\n  Shared PI width scale: 0 – {pi_max:.2f}")
cbar_ticks_pp = list(np.linspace(0, pi_max, 6))

print("Drawing fig2a — basic sanitation uncertainty …")
save_panel(
    filename="fig2a_basic_sanitation_uncertainty",
    gdf_panel=gdf_bs, col="pi_width", cmap=BS_UNC_CMAP, vmin=0, vmax=pi_max,
    borders=borders_bs, panel_label="a",
    full_title="Basic sanitation — 90% prediction interval",
    cbar_label="90% prediction interval width",
    cbar_ticks=cbar_ticks_pp,
)

print("Drawing fig2b — open defecation uncertainty …")
save_panel(
    filename="fig2b_open_defecation_uncertainty",
    gdf_panel=gdf_od, col="pi_width", cmap=OD_UNC_CMAP, vmin=0, vmax=pi_max,
    borders=borders_od, panel_label="b",
    full_title="Open defecation — 90% prediction interval",
    cbar_label="90% prediction interval width",
    cbar_ticks=cbar_ticks_pp,
)

print("\nDone.")