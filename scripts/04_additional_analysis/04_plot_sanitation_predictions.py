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

# Read the retrained (_v2) predictions and write figures under a v2 subfolder,
# so this analysis uses the corrected sanitation labelling and does not
# overwrite prior figures. Repo paths only (never switchdrive).
PRED_DIR   = "outputs/model_performance/v2/predictions"
FIGURE_DIR = "outputs/figures/v2"
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

    # Box: transparent fill + colour tint + dark border
    # (facecolor="none" so the jittered points behind show through the box)
    box_patch = mpatches.FancyBboxPatch(
        (x_pos - BOX_HALF, q25), BOX_HALF * 2, q75 - q25,
        boxstyle="square,pad=0",
        facecolor="none", edgecolor=dark_col,
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


def _labels_with_n(groups, df, sep="\n"):
    """Append '(n=<count>)' — number of admin-1 regions — to each category label.

    Counts come from df['group'] (one row per admin-1 region), so they match the
    region counts reported in the descriptive statistics.
    """
    counts = df["group"].value_counts()
    return [f"{g}{sep}(n={int(counts.get(g, 0))})" for g in groups]


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
    n           = len(present)
    tick_labels = _labels_with_n(present, bs_data, sep="\n")
    w           = fig_width or max(FIG_WIDTH, n * 0.95)

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

        format_ax(ax, n, tick_labels,
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

# -------------------------------------------------------
# 8.  Horizontal box-plot figure (green / orange)
#
#     Basic sanitation = green, open defecation = orange, matching the
#     colours used in 02_map_sanitation_predictions.py (green endpoint of
#     BS_CMAP, orange midpoint of OD_CMAP).
#
#     One combined figure with the three groupings stacked vertically:
#         SDG regions      (top)
#         Income group     (middle)
#         Fragile context  (bottom)
#     Two columns, left = at least basic sanitation, right = open defecation.
#     Each grouping is labelled vertically on the far left. Same transparent
#     boxes + uniform jitter as the panels above, drawn horizontally.
# -------------------------------------------------------

BS_GREEN  = "#1a9850"   # green endpoint of the basic-sanitation map palette
OD_ORANGE = "#fd8d3c"   # orange midpoint of the open-defecation map palette


def draw_box_h(ax, vals, y_pos, colour, rng):
    """Draw a horizontal boxplot + uniform jitter centred on y_pos."""
    if len(vals) == 0:
        return

    dark_col = dark(colour)

    # Jitter — all points, uniform size, constrained within box height
    jitter = rng.uniform(-BOX_HALF * 0.85, BOX_HALF * 0.85, size=len(vals))
    ax.scatter(vals, y_pos + jitter,
               s=JIT_SIZE, color=colour,
               alpha=JIT_ALPHA, linewidths=0, zorder=1)

    # Box statistics
    q25, q50, q75 = np.percentile(vals, [25, 50, 75])
    iqr      = q75 - q25
    lo_fence = q25 - 1.5 * iqr
    hi_fence = q75 + 1.5 * iqr
    lo_whisk = vals[vals >= lo_fence].min()
    hi_whisk = vals[vals <= hi_fence].max()

    # Box: transparent fill + colour tint + dark border
    box_patch = mpatches.FancyBboxPatch(
        (q25, y_pos - BOX_HALF), q75 - q25, BOX_HALF * 2,
        boxstyle="square,pad=0",
        facecolor="none", edgecolor=dark_col,
        linewidth=BOX_LW, zorder=3,
    )
    ax.add_patch(box_patch)
    ax.fill_between([q25, q75], y_pos - BOX_HALF, y_pos + BOX_HALF,
                    color=colour, alpha=BOX_ALPHA, zorder=4)

    # Median
    ax.plot([q50, q50], [y_pos - BOX_HALF, y_pos + BOX_HALF],
            color=dark_col, lw=MED_LW, zorder=5, solid_capstyle="butt")

    # Whiskers + caps
    cap_w = BOX_HALF * 0.45
    for x_box, x_whisk in [(q25, lo_whisk), (q75, hi_whisk)]:
        ax.plot([x_box, x_whisk], [y_pos, y_pos],
                color=dark_col, lw=0.9, zorder=3)
        ax.plot([x_whisk, x_whisk], [y_pos - cap_w, y_pos + cap_w],
                color=dark_col, lw=0.9, zorder=3)


def make_horizontal_figure(blocks, figname):
    """
    One stacked figure of horizontal box plots.

    Parameters
    ----------
    blocks : list of (block_label, group_order, bs_data, od_data)
        Each entry becomes one row-block, drawn top to bottom. Categories
        run top to bottom within a block (first item of group_order at top).
    """
    rng = np.random.default_rng(42)

    # Resolve which categories are actually present, per block
    presents = []
    for _label, order, bs_d, od_d in blocks:
        present = [g for g in order
                   if g in bs_d["group"].values or g in od_d["group"].values]
        presents.append(present)
    counts   = [len(p) for p in presents]
    n_blocks = len(blocks)
    total    = sum(counts)

    # Nature Water: double-column figures are 180 mm (= FIG_WIDTH, 7.09 in)
    # wide, with all text between 5 and 7 pt in a sans-serif face. Height
    # scales with the total number of categories plus fixed allowances (inches)
    # for the column headers (top) and the x-axis (bottom).
    HEADER_FS = 7      # bold column headers
    BLOCK_FS  = 7      # rotated grouping labels
    TICK_FS   = 6      # category (y) tick labels
    # Each category label is two lines (name + "(n=…)"), so allow ~0.40 in per
    # row to stop them overlapping. Wide left margin fits long SDG region names;
    # a real gap between the two columns keeps the headers from touching.
    row_h   = 0.40
    top_in  = 0.50     # column headers
    bot_in  = 0.55     # x tick labels + axis label
    fig_h   = total * row_h + top_in + bot_in
    fig     = plt.figure(figsize=(FIG_WIDTH, fig_h))

    gs = fig.add_gridspec(
        n_blocks, 2,
        height_ratios=counts,
        hspace=0.55, wspace=0.22,
        left=0.36, right=0.965,
        top=1 - top_in / fig_h, bottom=bot_in / fig_h,
    )

    left_axes = []
    for i, ((block_label, order, bs_d, od_d), present) in enumerate(
            zip(blocks, presents)):
        n = len(present)
        for j, (df_g, colour, col_title) in enumerate([
            (bs_d, BS_GREEN,  "At least basic sanitation"),
            (od_d, OD_ORANGE, "Open defecation"),
        ]):
            ax = fig.add_subplot(gs[i, j])

            for k, group in enumerate(present):
                mask = df_g["group"] == group
                vals = df_g.loc[mask, "median"].dropna().to_numpy()
                draw_box_h(ax, vals, k, colour, rng)

            ax.set_ylim(n - 0.5, -0.5)     # invert so first category is on top
            ax.set_xlim(-0.02, 1.02)
            ax.set_yticks(range(n))

            if j == 0:
                ax.set_yticklabels(_labels_with_n(present, bs_d, sep="\n"),
                                   fontsize=TICK_FS)
                left_axes.append(ax)
            else:
                ax.set_yticklabels([])
            ax.tick_params(axis="y", length=0)

            ax.xaxis.set_major_formatter(
                mpl.ticker.PercentFormatter(xmax=1, decimals=0))
            ax.grid(axis="x", linewidth=0.4, color="#cccccc", zorder=0)
            ax.spines[["top", "right", "left"]].set_visible(False)

            # x tick labels + axis label only on the bottom block
            if i == n_blocks - 1:
                ax.set_xlabel("Predicted proportion (%)", fontsize=7)
            else:
                ax.set_xticklabels([])

            # Column headers on the top block only
            if i == 0:
                ax.set_title(col_title, fontsize=HEADER_FS,
                             fontweight="bold", pad=5)

    # Rotated grouping labels on the far left, centred on each block
    for ax, (block_label, *_rest) in zip(left_axes, blocks):
        pos = ax.get_position()
        y_center = (pos.y0 + pos.y1) / 2
        fig.text(0.02, y_center, block_label, rotation=90,
                 va="center", ha="center", fontsize=BLOCK_FS, fontweight="bold")

    for ext in ("pdf", "png"):
        out = os.path.join(FIGURE_DIR, f"{figname}.{ext}")
        fig.savefig(out, dpi=DPI, format=ext)
        print(f"  Saved: {out}")
    plt.close(fig)


print("\nDrawing horizontal box plots (SDG region / income / fragile) …")

# SDG regions ordered by basic-sanitation median (highest at top)
sdg_order_desc = (
    bs_sdg.groupby("group")["median"]
    .median()
    .sort_values(ascending=False)
    .index.tolist()
)

make_horizontal_figure(
    blocks=[
        ("SDG regions",     sdg_order_desc, bs_sdg,  od_sdg),
        ("Income group",    INCOME_ORDER,   bs_inc,  od_inc),
        ("Fragile context", FRAGILE_ORDER,  bs_frag, od_frag),
    ],
    figname="fig_distribution_horizontal_combined",
)

print("\nDone (horizontal box plots).")

# -------------------------------------------------------
# 9.  Horizontal box plots — median vs. 90% prediction-interval width
#
#     Experiment: instead of BS vs. OD side by side, show for a single
#     outcome the predicted proportion (left) next to its uncertainty
#     (right = width of the 90% prediction interval).
#
#     Colours match the map figures in 02_map_sanitation_predictions.py:
#         BS median      = green   (BS_CMAP endpoint)
#         BS uncertainty = purple  (BS_UNC_CMAP, YlPu)
#         OD median      = orange  (OD_CMAP midpoint)
#         OD uncertainty = orange/red (OD_UNC_CMAP, YlOrRd)
#
#     One figure per outcome, three groupings stacked as above.
# -------------------------------------------------------

# Uncertainty = width of the 90% prediction interval
for _df in (bs_inc, od_inc, bs_frag, od_frag, bs_sdg, od_sdg):
    _df["pi_width"] = _df["pi90_upper"] - _df["pi90_lower"]

# Sample the actual map colourmaps so the box colours match the maps.
_BS_UNC_CMAP = mc.LinearSegmentedColormap.from_list(
    "YlPu_custom", ["#ffffcc", "#c994c7", "#67001f"], N=256)
BS_UNC_PURPLE = mc.to_hex(_BS_UNC_CMAP(0.55))      # purple
OD_UNC_RED    = mc.to_hex(plt.get_cmap("YlOrRd")(0.65))  # orange/red


def make_horizontal_metric_figure(blocks, columns, figname):
    """
    Stacked horizontal box plots for one outcome, several value columns.

    Parameters
    ----------
    blocks : list of (block_label, group_order, data_df)
    columns : list of dict, each with keys
        col     : value column to plot
        colour  : point/box colour
        title   : bold column header (top block); may contain "\\n"
        xlabel  : x-axis label (bottom block)
        xmax    : fixed x-axis maximum, or None to derive from the data
    """
    rng = np.random.default_rng(42)

    presents = []
    for _label, order, df_g in blocks:
        present = [g for g in order if g in df_g["group"].values]
        presents.append(present)
    counts   = [len(p) for p in presents]
    n_blocks = len(blocks)
    total    = sum(counts)

    # x-axis maximum per column, shared across blocks
    col_xmax = []
    for spec in columns:
        if spec.get("xmax") is not None:
            col_xmax.append(spec["xmax"])
        else:
            vmax = 0.0
            for _l, _o, df_g in blocks:
                v = df_g[spec["col"]].dropna()
                if len(v):
                    vmax = max(vmax, float(v.max()))
            col_xmax.append(np.ceil(vmax * 10) / 10)

    row_h  = 0.34
    top_in = 0.35     # single-line (a)/(b) panel letters
    bot_in = 0.55     # x tick labels + axis label
    fig_h  = total * row_h + top_in + bot_in
    fig    = plt.figure(figsize=(FIG_WIDTH, fig_h))

    gs = fig.add_gridspec(
        n_blocks, len(columns),
        height_ratios=counts,
        hspace=0.40, wspace=0.10,
        left=0.27, right=0.975,
        top=1 - top_in / fig_h, bottom=bot_in / fig_h,
    )

    left_axes = []
    for i, ((block_label, order, df_g), present) in enumerate(
            zip(blocks, presents)):
        n = len(present)
        for j, spec in enumerate(columns):
            ax = fig.add_subplot(gs[i, j])

            for k, group in enumerate(present):
                mask = df_g["group"] == group
                vals = df_g.loc[mask, spec["col"]].dropna().to_numpy()
                draw_box_h(ax, vals, k, spec["colour"], rng)

            xmax = col_xmax[j]
            ax.set_ylim(n - 0.5, -0.5)
            ax.set_xlim(-0.02 * xmax, xmax * 1.02)
            ax.set_yticks(range(n))

            if j == 0:
                ax.set_yticklabels(_labels_with_n(present, df_g, sep="\n"),
                                   fontsize=6)
                left_axes.append(ax)
            else:
                ax.set_yticklabels([])
            ax.tick_params(axis="y", length=0)

            # Show plain numbers on a 0–100 scale; the unit (percent for the
            # proportion column, percentage points for the interval-width
            # column) is carried by the axis label rather than a "%" suffix.
            ax.xaxis.set_major_formatter(
                mpl.ticker.FuncFormatter(lambda x, _pos: f"{x * 100:.0f}"))
            ax.grid(axis="x", linewidth=0.4, color="#cccccc", zorder=0)
            ax.spines[["top", "right", "left"]].set_visible(False)

            if i == n_blocks - 1:
                ax.set_xlabel(spec["xlabel"], fontsize=7)
            else:
                ax.set_xticklabels([])

            # Panel letters (a)/(b); the descriptive text lives in the caption.
            if i == 0:
                ax.set_title(spec["title"], fontsize=8,
                             fontweight="bold", pad=6, loc="left")

    for ax, (block_label, *_rest) in zip(left_axes, blocks):
        pos = ax.get_position()
        y_center = (pos.y0 + pos.y1) / 2
        fig.text(0.02, y_center, block_label, rotation=90,
                 va="center", ha="center", fontsize=8, fontweight="bold")

    for ext in ("pdf", "png"):
        out = os.path.join(FIGURE_DIR, f"{figname}.{ext}")
        fig.savefig(out, dpi=DPI, format=ext)
        print(f"  Saved: {out}")
    plt.close(fig)


print("\nDrawing horizontal box plots — median vs. 90% PI width …")

UNC_XLABEL = "90% prediction interval width (p.p.)"

# Basic sanitation: green proportion | purple uncertainty
make_horizontal_metric_figure(
    blocks=[
        ("SDG regions",      sdg_order_desc, bs_sdg),
        ("Income group",     INCOME_ORDER,   bs_inc),
        ("Fragility status", FRAGILE_ORDER,  bs_frag),
    ],
    columns=[
        {"col": "median",   "colour": BS_GREEN,      "xmax": 1.0,
         "title": "(a)",
         "xlabel": "Predicted proportion (%)"},
        {"col": "pi_width", "colour": BS_UNC_PURPLE, "xmax": None,
         "title": "(b)", "xlabel": UNC_XLABEL},
    ],
    figname="fig_distribution_horizontal_bs_uncertainty",
)

# Open defecation: orange proportion | orange/red uncertainty
make_horizontal_metric_figure(
    blocks=[
        ("SDG regions",      sdg_order_desc, od_sdg),
        ("Income group",     INCOME_ORDER,   od_inc),
        ("Fragility status", FRAGILE_ORDER,  od_frag),
    ],
    columns=[
        {"col": "median",   "colour": OD_ORANGE,  "xmax": 1.0,
         "title": "(a)",
         "xlabel": "Predicted proportion (%)"},
        {"col": "pi_width", "colour": OD_UNC_RED, "xmax": None,
         "title": "(b)", "xlabel": UNC_XLABEL},
    ],
    figname="fig_distribution_horizontal_od_uncertainty",
)

print("\nDone (median vs. uncertainty box plots).")

# -------------------------------------------------------
# 10. Country-level dumbbell plot — BS and OD side by side
#
#     Three stacked blocks (rows):
#       Top    — Extreme predictions (lowest BS coverage / highest OD rate)
#       Middle — Top N countries by HIGHEST within-country variation
#       Bottom — Top N countries by HIGHEST median 90% PI width (most uncertain)
#     Two columns: Basic sanitation (left) | Open defecation (right)
#
#     Each row within a block = one country.
#     Visual encoding per row:
#       Transparent bar : min(pi90_lower) → max(pi90_upper) across districts
#                         (full uncertainty envelope)
#       Dumbbell line   : min → max of district-level predicted medians
#       Filled dot      : country median prediction
# -------------------------------------------------------

TOP_N         = 10
MIN_DISTRICTS = 3   # minimum districts to include a country


def _draw_country_row(ax, df_country, y_pos, colour):
    """Uncertainty envelope bar + district-median dumbbell for one country."""
    sub = df_country.dropna(subset=["median", "pi90_lower", "pi90_upper"])
    if len(sub) < 2:
        return

    med_vals = sub["median"].to_numpy()
    lo_vals  = sub["pi90_lower"].to_numpy()
    hi_vals  = sub["pi90_upper"].to_numpy()

    # Transparent bar: full PI envelope (min lower bound → max upper bound)
    bar_lo = float(lo_vals.min())
    bar_hi = float(hi_vals.max())
    ax.barh(y_pos, bar_hi - bar_lo, left=bar_lo, height=0.50,
            color=colour, alpha=0.20, linewidth=0, zorder=1)

    # Dumbbell: range of district point estimates
    vmin  = float(med_vals.min())
    vmed  = float(np.median(med_vals))
    vmax  = float(med_vals.max())
    dcol  = dark(colour)
    tick_h = 0.15
    ax.plot([vmin, vmax], [y_pos, y_pos],
            color=dcol, lw=1.6, alpha=0.85, solid_capstyle="round", zorder=2)
    for x in (vmin, vmax):
        ax.plot([x, x], [y_pos - tick_h, y_pos + tick_h],
                color=dcol, lw=1.1, alpha=0.90, zorder=3)
    ax.scatter([vmed], [y_pos], s=26, color=dcol, linewidths=0, zorder=4)


def _country_stats(df, min_districts=MIN_DISTRICTS):
    """Return per-country summary; filter to countries with enough districts."""
    d = df.assign(pi_width=df["pi90_upper"] - df["pi90_lower"])
    return (
        d.groupby("NAME_0")
        .agg(n=("median", "count"),
             median_cov=("median", "median"),
             range_cov=("median", lambda x: x.max() - x.min()),
             median_pi_width=("pi_width", "median"))
        .reset_index()
        .query("n >= @min_districts")
    )


def make_country_side_by_side(
        bs_df, od_df, bs_colour, od_colour,
        bs_low, bs_var, bs_unc, od_low, od_var, od_unc,
        figname):
    """
    3-row × 2-col dumbbell figure.
    Rows = blocks (extreme coverage, highest within-country variation,
    most uncertain predictions).
    Cols = outcome (BS left, OD right).
    Country lists differ per outcome and block.
    """
    block_labels = ["Lowest sanitation service use",
                    "Highest within-country variation",
                    "Most uncertain predictions"]
    col_blocks   = [
        (bs_df, bs_colour, "Basic sanitation",  [bs_low,  bs_var,  bs_unc]),
        (od_df, od_colour, "Open defecation",   [od_low,  od_var,  od_unc]),
    ]
    n_blocks = len(block_labels)

    # Pre-compute district counts per country per outcome
    def _n_map(df):
        return df.groupby("NAME_0")["median"].count().to_dict()

    bs_n = _n_map(bs_df)
    od_n = _n_map(od_df)
    n_maps = [bs_n, od_n]

    n_block = [
        max(len(bs_low), len(od_low)),
        max(len(bs_var), len(od_var)),
        max(len(bs_unc), len(od_unc)),
    ]
    total = sum(n_block)

    row_h  = 0.30
    top_in = 0.52
    bot_in = 0.48
    fig_h  = total * row_h + top_in + bot_in

    fig = plt.figure(figsize=(FIG_WIDTH, fig_h))
    gs  = fig.add_gridspec(
        n_blocks, 2,
        height_ratios=n_block,
        hspace=0.04,
        wspace=0.42,          # wider gap so OD labels don't overlap BS plot
        left=0.30, right=0.975,
        top=1 - top_in / fig_h,
        bottom=bot_in / fig_h,
    )

    left_axes = []

    for row in range(n_blocks):
        for col, (df_out, colour, col_title, country_blocks) in enumerate(col_blocks):
            ax = fig.add_subplot(gs[row, col])
            countries = country_blocks[row]
            present   = [c for c in countries if c in df_out["NAME_0"].values]
            n_map     = n_maps[col]
            n = len(present)

            for k, country in enumerate(present):
                sub = df_out[df_out["NAME_0"] == country]
                _draw_country_row(ax, sub, k, colour)

            ax.set_ylim(n - 0.5, -0.5)
            ax.set_xlim(-0.02, 1.02)
            ax.set_yticks(range(n))

            # Labels with (n=X) district count on both columns
            tick_labels = [
                f"{c}  (n={n_map.get(c, 0)})" for c in present
            ]
            ax.set_yticklabels(tick_labels, fontsize=5.5)
            if col == 0:
                left_axes.append(ax)
            ax.yaxis.set_tick_params(length=0)

            ax.xaxis.set_major_formatter(
                mpl.ticker.PercentFormatter(xmax=1, decimals=0))
            ax.grid(axis="x", linewidth=0.4, color="#cccccc", zorder=0)
            ax.spines[["top", "right", "left"]].set_visible(False)

            if row == n_blocks - 1:
                ax.set_xlabel("Predicted proportion", fontsize=7)
            else:
                ax.set_xticklabels([])
            if row == 0:
                ax.set_title(col_title, fontsize=7.5,
                             fontweight="bold", pad=6)

    # Single-line block labels rotated 90° on far left
    for ax, blk_label in zip(left_axes, block_labels):
        pos = ax.get_position()
        fig.text(0.01, (pos.y0 + pos.y1) / 2, blk_label,
                 rotation=90, va="center", ha="center",
                 fontsize=7, fontweight="bold")

    for ext in ("pdf", "png"):
        out = os.path.join(FIGURE_DIR, f"{figname}.{ext}")
        fig.savefig(out, dpi=DPI, format=ext, bbox_inches="tight")
        print(f"  Saved: {out}")
    plt.close(fig)


print("\nDrawing country-level dumbbell plots (BS + OD side by side) …")

bs_stats = _country_stats(bs)
od_stats = _country_stats(od)

bs_low  = (bs_stats.nsmallest(TOP_N, "median_cov")
           .sort_values("median_cov", ascending=True)["NAME_0"].tolist())
bs_var  = (bs_stats.nlargest(TOP_N, "range_cov")
           .sort_values("range_cov", ascending=False)["NAME_0"].tolist())
od_low  = (od_stats.nlargest(TOP_N, "median_cov")
           .sort_values("median_cov", ascending=False)["NAME_0"].tolist())
od_var  = (od_stats.nlargest(TOP_N, "range_cov")
           .sort_values("range_cov", ascending=False)["NAME_0"].tolist())
# Bottom block: most uncertain countries (highest median 90% PI width)
bs_unc  = (bs_stats.nlargest(TOP_N, "median_pi_width")
           .sort_values("median_pi_width", ascending=False)["NAME_0"].tolist())
od_unc  = (od_stats.nlargest(TOP_N, "median_pi_width")
           .sort_values("median_pi_width", ascending=False)["NAME_0"].tolist())

print(f"  BS lowest BS coverage : {bs_low}")
print(f"  OD highest OD rate    : {od_low}")
print(f"  BS highest variation  : {bs_var}")
print(f"  OD highest variation  : {od_var}")
print(f"  BS most uncertain     : {bs_unc}")
print(f"  OD most uncertain     : {od_unc}")

make_country_side_by_side(
    bs_df=bs, od_df=od,
    bs_colour=BS_GREEN, od_colour=OD_ORANGE,
    bs_low=bs_low, bs_var=bs_var, bs_unc=bs_unc,
    od_low=od_low, od_var=od_var, od_unc=od_unc,
    figname="fig_country_dumbbell_bs_od",
)

print("\nDone (country-level dumbbell plots).")
