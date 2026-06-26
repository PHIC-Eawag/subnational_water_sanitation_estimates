# -------------------------------------------------------
# Distribution of sanitation predictions
# across income groups, SDG regions, and fragile contexts
#
# Figure 1: Income groups + Fragile context (combined)
#   Two stacked panels — BS (top), OD (bottom)
#   Groups: Low income | Lower middle income | Upper middle income
#           | Non-fragile | Fragile or Extremely Fragile
#
# Figure 2: SDG regions
#   Two stacked panels — BS (top), OD (bottom)
#
# Each panel: boxplot + uniform jitter
# -------------------------------------------------------

import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mc

# -------------------------------------------------------
# 1.  Paths
# -------------------------------------------------------

PRED_DIR   = "outputs/model_performance/predictions"
FIGURE_DIR = "outputs/figures"
os.makedirs(FIGURE_DIR, exist_ok=True)

BS_PRED = os.path.join(PRED_DIR, "basic_sanitation_tabpfn_lmic_predictions.csv")
OD_PRED = os.path.join(PRED_DIR, "open_defecation_tabpfn_lmic_predictions.csv")

# -------------------------------------------------------
# 2.  Plot settings
# -------------------------------------------------------

FIG_WIDTH = 7.09   # Nature Water double-column = 180 mm
PANEL_H   = 3.2    # inches per panel
DPI       = 300

BS_COLOUR = "#4393c3"
OD_COLOUR = "#d6604d"

BOX_ALPHA   = 0.12
BOX_LW      = 1.4
DARK_FACTOR = 0.60
MED_LW      = 2.2
JIT_ALPHA   = 0.35
JIT_SIZE    = 4      # uniform point size (pt²)
BOX_HALF    = 0.28   # half-width of each box

mpl.rcParams.update({
    "font.family":      "sans-serif",
    "font.sans-serif":  ["Arial", "Helvetica Neue", "Helvetica", "DejaVu Sans"],
    "font.size":        7,
    "axes.titlesize":   8,
    "axes.labelsize":   7,
    "xtick.labelsize":  7,
    "ytick.labelsize":  6,
    "legend.fontsize":  6,
    "figure.dpi":       DPI,
    "savefig.dpi":      DPI,
})

# -------------------------------------------------------
# 3.  Load data
# -------------------------------------------------------

print("Loading predictions …")
bs = pd.read_csv(BS_PRED)
od = pd.read_csv(OD_PRED)

for df, label in [(bs, "basic_sanitation"), (od, "open_defecation")]:
    print(f"  {label}: {len(df):,} rows")
    for col in ("median", "wb_income_group", "sdg_region", "fragile_context"):
        if col not in df.columns:
            raise ValueError(f"Column '{col}' missing from {label} predictions.")

# -------------------------------------------------------
# 4.  Group prep functions
# -------------------------------------------------------

INCOME_ORDER  = ["Low income", "Lower middle income", "Upper middle income"]
INCOME_LABELS = {"L": "Low income", "LM": "Lower middle income",
                 "UM": "Upper middle income"}

def prep_income(df):
    df = df.copy()
    df["group"] = df["wb_income_group"].map(INCOME_LABELS)
    return df[df["group"].notna()]

def prep_sdg(df):
    df = df.copy()
    df["group"] = df["sdg_region"].astype(str).str.strip()
    return df[df["group"].notna() & (df["group"] != "nan")]

FRAGILE_ORDER = ["Non-fragile", "Fragile or Extremely Fragile"]

def prep_fragile(df):
    df = df.copy()
    df["group"] = df["fragile_context"].apply(
        lambda x: "Fragile or Extremely Fragile"
        if isinstance(x, str) and x.strip() == "Fragile or Extremely Fragile"
        else "Non-fragile"
    )
    return df

# -------------------------------------------------------
# 5.  Core drawing helper
# -------------------------------------------------------

def dark(colour):
    return tuple(c * DARK_FACTOR for c in mc.to_rgb(colour))


def draw_box(ax, vals, x_pos, colour, rng):
    """Draw boxplot + uniform jitter at x_pos."""
    if len(vals) == 0:
        return

    dark_col = dark(colour)

    # Jitter — all points, uniform size, constrained within box width
    jitter = rng.uniform(-BOX_HALF * 0.85, BOX_HALF * 0.85, size=len(vals))
    ax.scatter(x_pos + jitter, vals,
               s=JIT_SIZE, color=colour,
               alpha=JIT_ALPHA, linewidths=0, zorder=1)

    # Box statistics
    q25, q50, q75 = np.percentile(vals, [25, 50, 75])
    iqr      = q75 - q25
    lo_fence = q25 - 1.5 * iqr
    hi_fence = q75 + 1.5 * iqr
    lo_whisk = vals[vals >= lo_fence].min()
    hi_whisk = vals[vals <= hi_fence].max()

    # Box: white fill + colour tint + dark border
    box_patch = mpatches.FancyBboxPatch(
        (x_pos - BOX_HALF, q25), BOX_HALF * 2, q75 - q25,
        boxstyle="square,pad=0",
        facecolor="white", edgecolor=dark_col,
        linewidth=BOX_LW, zorder=3,
    )
    ax.add_patch(box_patch)
    ax.fill_betweenx([q25, q75], x_pos - BOX_HALF, x_pos + BOX_HALF,
                     color=colour, alpha=BOX_ALPHA, zorder=4)

    # Median
    ax.plot([x_pos - BOX_HALF, x_pos + BOX_HALF], [q50, q50],
            color=dark_col, lw=MED_LW, zorder=5, solid_capstyle="butt")

    # Whiskers + caps
    cap_w = BOX_HALF * 0.45
    for y_box, y_whisk in [(q25, lo_whisk), (q75, hi_whisk)]:
        ax.plot([x_pos, x_pos], [y_box, y_whisk],
                color=dark_col, lw=0.9, zorder=3)
        ax.plot([x_pos - cap_w, x_pos + cap_w], [y_whisk, y_whisk],
                color=dark_col, lw=0.9, zorder=3)


def format_ax(ax, n, tick_labels, xlabel=None, panel_label=None, title=None,
              ylabel="Predicted proportion"):
    ax.set_xlim(-0.6, n - 0.4)
    ax.set_ylim(-0.02, 1.02)
    ax.set_xticks(range(n))
    ax.set_xticklabels(tick_labels, rotation=30, ha="right", fontsize=7)
    ax.set_ylabel(ylabel, fontsize=7)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=7, labelpad=4)
    ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", linewidth=0.4, color="#cccccc", zorder=0)
    if panel_label and title:
        ax.set_title(f"$\\bf{{{panel_label}}}$  {title}",
                     fontsize=8, loc="left", pad=4)


def make_stacked_figure(bs_data, od_data, group_order,
                        xlabel, figname,
                        separator_after=None,
                        fig_width=None):
    """
    Two stacked panels (BS top, OD bottom).

    Parameters
    ----------
    separator_after : int or None
        If set, draw a subtle vertical divider after this group index.
        Used to separate income groups from fragile context groups.
    """
    rng     = np.random.default_rng(42)
    present = [g for g in group_order
               if g in bs_data["group"].values or g in od_data["group"].values]
    n       = len(present)
    w       = fig_width or max(FIG_WIDTH, n * 0.95)

    fig, (ax_bs, ax_od) = plt.subplots(
        2, 1,
        figsize=(w, PANEL_H * 2 + 0.4),
        gridspec_kw={"hspace": 0.55},
    )

    for ax, df_g, colour, label, title, ylabel in [
        (ax_bs, bs_data, BS_COLOUR, "a", "Basic sanitation",
         "Predicted proportion of population using BS"),
        (ax_od, od_data, OD_COLOUR, "b", "Open defecation",
         "Predicted proportion of population practicing OD"),
    ]:
        for i, group in enumerate(present):
            mask = df_g["group"] == group
            vals = df_g.loc[mask, "median"].dropna().to_numpy()
            draw_box(ax, vals, i, colour, rng)

        # Subtle vertical separator between income and fragile groups
        if separator_after is not None:
            ax.axvline(x=separator_after + 0.5,
                       color="#aaaaaa", lw=0.8, ls="--", zorder=0)

        format_ax(ax, n, present,
                  xlabel=xlabel if ax is ax_od else None,
                  panel_label=label, title=title,
                  ylabel=ylabel)

    fig.subplots_adjust(left=0.10, right=0.97, top=0.95, bottom=0.18)
    for ext in ("pdf", "png"):
        out = os.path.join(FIGURE_DIR, f"{figname}.{ext}")
        fig.savefig(out, dpi=DPI, format=ext)
        print(f"  Saved: {out}")
    plt.close(fig)


# -------------------------------------------------------
# 6.  Figure 1 — Income groups + Fragile context
# -------------------------------------------------------

print("\nDrawing: income group + fragile context …")

bs_inc  = prep_income(bs)
od_inc  = prep_income(od)
bs_frag = prep_fragile(bs)
od_frag = prep_fragile(od)

# Concatenate income and fragile groups
bs_combined = pd.concat([bs_inc, bs_frag], ignore_index=True)
od_combined = pd.concat([od_inc, od_frag], ignore_index=True)

combined_order = INCOME_ORDER + FRAGILE_ORDER

make_stacked_figure(
    bs_data=bs_combined,
    od_data=od_combined,
    group_order=combined_order,
    xlabel=None,
    figname="fig_distribution_income_fragile",
    separator_after=len(INCOME_ORDER) - 1,  # dashed line after income groups
)

# -------------------------------------------------------
# 7.  Figure 2 — SDG regions
# -------------------------------------------------------

print("\nDrawing: SDG region …")

bs_sdg = prep_sdg(bs)
od_sdg = prep_sdg(od)

sdg_order = (
    bs_sdg.groupby("group")["median"]
    .median()
    .sort_values()
    .index.tolist()
)

make_stacked_figure(
    bs_data=bs_sdg,
    od_data=od_sdg,
    group_order=sdg_order,
    xlabel="SDG region",
    figname="fig_distribution_sdg_region",
)

print("\nDone.")
