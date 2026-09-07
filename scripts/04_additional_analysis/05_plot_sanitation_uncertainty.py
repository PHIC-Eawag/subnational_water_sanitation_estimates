# -------------------------------------------------------
# Distribution of prediction UNCERTAINTY (90% PI width)
# across income groups, SDG regions, and fragile contexts
#
# Mirrors 05_plot_distributions.py but plots
# width_90 = q95 - q05 instead of median prediction.
#
# Figure 1: Income groups + Fragile context (combined)
# Figure 2: SDG regions
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
# 2.  Plot settings (identical to 05_plot_distributions.py)
# -------------------------------------------------------

FIG_WIDTH = 7.09
PANEL_H   = 3.2
DPI       = 300

BS_COLOUR = "#4393c3"
OD_COLOUR = "#d6604d"

BOX_ALPHA   = 0.12
BOX_LW      = 1.4
DARK_FACTOR = 0.60
MED_LW      = 2.2
JIT_ALPHA   = 0.35
JIT_SIZE    = 4
BOX_HALF    = 0.28

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
# 3.  Load data and compute 90% PI width
# -------------------------------------------------------

print("Loading predictions …")
bs = pd.read_csv(BS_PRED)
od = pd.read_csv(OD_PRED)

for df, label in [(bs, "basic_sanitation"), (od, "open_defecation")]:
    if "pi90_lower" not in df.columns or "pi90_upper" not in df.columns:
        raise ValueError(
            f"Columns 'pi90_lower' and 'pi90_upper' required but missing from {label} predictions."
        )
    df["width_90"] = df["pi90_upper"] - df["pi90_lower"]
    print(f"  {label}: {len(df):,} rows | "
          f"median width_90 = {df['width_90'].median():.3f}")

# -------------------------------------------------------
# 4.  Group prep functions (identical to 05_plot_distributions.py)
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
    if len(vals) == 0:
        return
    dark_col = dark(colour)
    jitter = rng.uniform(-BOX_HALF * 0.85, BOX_HALF * 0.85, size=len(vals))
    ax.scatter(x_pos + jitter, vals,
               s=JIT_SIZE, color=colour,
               alpha=JIT_ALPHA, linewidths=0, zorder=1)
    q25, q50, q75 = np.percentile(vals, [25, 50, 75])
    iqr      = q75 - q25
    lo_fence = q25 - 1.5 * iqr
    hi_fence = q75 + 1.5 * iqr
    lo_whisk = vals[vals >= lo_fence].min()
    hi_whisk = vals[vals <= hi_fence].max()
    # facecolor="none" so the jittered points behind show through the box
    box_patch = mpatches.FancyBboxPatch(
        (x_pos - BOX_HALF, q25), BOX_HALF * 2, q75 - q25,
        boxstyle="square,pad=0",
        facecolor="none", edgecolor=dark_col,
        linewidth=BOX_LW, zorder=3,
    )
    ax.add_patch(box_patch)
    ax.fill_betweenx([q25, q75], x_pos - BOX_HALF, x_pos + BOX_HALF,
                     color=colour, alpha=BOX_ALPHA, zorder=4)
    ax.plot([x_pos - BOX_HALF, x_pos + BOX_HALF], [q50, q50],
            color=dark_col, lw=MED_LW, zorder=5, solid_capstyle="butt")
    cap_w = BOX_HALF * 0.45
    for y_box, y_whisk in [(q25, lo_whisk), (q75, hi_whisk)]:
        ax.plot([x_pos, x_pos], [y_box, y_whisk],
                color=dark_col, lw=0.9, zorder=3)
        ax.plot([x_pos - cap_w, x_pos + cap_w], [y_whisk, y_whisk],
                color=dark_col, lw=0.9, zorder=3)


def format_ax(ax, n, tick_labels, xlabel=None, panel_label=None, title=None,
              ylabel="90% PI width (percentage points)"):
    ax.set_xlim(-0.6, n - 0.4)
    ax.set_ylim(-0.01, 1.01)
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
                        value_col="width_90",
                        separator_after=None,
                        fig_width=None):
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
         "90% PI width — basic sanitation"),
        (ax_od, od_data, OD_COLOUR, "b", "Open defecation",
         "90% PI width — open defecation"),
    ]:
        for i, group in enumerate(present):
            mask = df_g["group"] == group
            vals = df_g.loc[mask, value_col].dropna().to_numpy()
            draw_box(ax, vals, i, colour, rng)

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

print("\nDrawing: uncertainty by income group + fragile context …")

bs_inc  = prep_income(bs)
od_inc  = prep_income(od)
bs_frag = prep_fragile(bs)
od_frag = prep_fragile(od)

bs_combined = pd.concat([bs_inc, bs_frag], ignore_index=True)
od_combined = pd.concat([od_inc, od_frag], ignore_index=True)

combined_order = INCOME_ORDER + FRAGILE_ORDER

make_stacked_figure(
    bs_data=bs_combined,
    od_data=od_combined,
    group_order=combined_order,
    xlabel=None,
    figname="fig_uncertainty_income_fragile",
    separator_after=len(INCOME_ORDER) - 1,
)

# -------------------------------------------------------
# 7.  Figure 2 — SDG regions
# -------------------------------------------------------

print("\nDrawing: uncertainty by SDG region …")

bs_sdg = prep_sdg(bs)
od_sdg = prep_sdg(od)

# Order by median width_90 of basic sanitation (ascending)
sdg_order = (
    bs_sdg.groupby("group")["width_90"]
    .median()
    .sort_values()
    .index.tolist()
)

make_stacked_figure(
    bs_data=bs_sdg,
    od_data=od_sdg,
    group_order=sdg_order,
    xlabel="SDG region",
    figname="fig_uncertainty_sdg_region",
)

# -------------------------------------------------------
# 8.  Uncertainty vs coverage — scatter (one panel per outcome)
#     x = predicted proportion (median), y = 90% PI width.
#     A binned median trend is overlaid so the shape of the
#     relationship is legible despite heavy overplotting.
# -------------------------------------------------------

SCATTER_ALPHA = 0.35   # point opacity (higher = more pronounced)
SCATTER_SIZE  = 5
N_BINS        = 10     # coverage bins for the trend line
MIN_BIN_N     = 20     # minimum points in a bin to draw a trend marker


def binned_median_trend(x, y, n_bins=N_BINS, min_n=MIN_BIN_N):
    """Median y (with 25th/75th percentiles) within equal-width x bins on [0, 1]."""
    bins = np.linspace(0, 1, n_bins + 1)
    idx  = np.digitize(x, bins) - 1
    cen, med, q25, q75 = [], [], [], []
    for b in range(n_bins):
        sel = idx == b
        if sel.sum() >= min_n:
            yy = y[sel]
            # Anchor the marker at the actual median x of the points in the
            # bin (not the bin's geometric centre) — otherwise, when the
            # within-bin x-distribution is skewed (points pile up near 0% or
            # 100%), the marker is displaced horizontally from the data cloud.
            cen.append(np.median(x[sel]))
            med.append(np.median(yy))
            q25.append(np.percentile(yy, 25))
            q75.append(np.percentile(yy, 75))
    return np.array(cen), np.array(med), np.array(q25), np.array(q75)


def clean_xy(df):
    x = df["median"].to_numpy(dtype=float)
    y = df["width_90"].to_numpy(dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    return x[m], y[m]


print("\nDrawing: uncertainty vs coverage scatter …")

# Shared y-limit across panels for comparability (cap at 99th pct to avoid
# a few extreme widths stretching the axis).
_ymax = max(np.nanpercentile(bs["width_90"], 99),
            np.nanpercentile(od["width_90"], 99))
_ymax = float(np.ceil(_ymax * 20) / 20)  # round up to nearest 0.05

fig, (ax_bs, ax_od) = plt.subplots(
    2, 1, figsize=(FIG_WIDTH, PANEL_H * 2 + 0.4),
    gridspec_kw={"hspace": 0.45},
)

for ax, df, colour, label, title, xlab in [
    (ax_bs, bs, BS_COLOUR, "a", "Basic sanitation",
     "Predicted basic sanitation coverage (median)"),
    (ax_od, od, OD_COLOUR, "b", "Open defecation",
     "Predicted open defecation rate (median)"),
]:
    x, y = clean_xy(df)
    ax.scatter(x, y, s=SCATTER_SIZE, color=colour,
               alpha=SCATTER_ALPHA, linewidths=0, zorder=1)
    cen, med, q25, q75 = binned_median_trend(x, y)
    ax.plot(cen, med, color=dark(colour), lw=1.2, marker="o", ms=2.5,
            zorder=5, solid_capstyle="round", label="Binned median")

    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.005, _ymax)
    ax.set_xlabel(xlab, fontsize=7, labelpad=3)
    ax.set_ylabel("90% PI width (percentage points)", fontsize=7)
    ax.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(linewidth=0.4, color="#cccccc", zorder=0)
    ax.set_title(f"$\\bf{{{label}}}$  {title}", fontsize=8, loc="left", pad=4)

fig.subplots_adjust(left=0.10, right=0.97, top=0.95, bottom=0.12)
for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig_uncertainty_vs_coverage_scatter.{ext}")
    fig.savefig(out, dpi=DPI, format=ext)
    print(f"  Saved: {out}")
plt.close(fig)

# -------------------------------------------------------
# 9.  Uncertainty vs coverage — binned trend comparison (SUGGESTED)
#     Both outcomes on one axis: median 90% PI width across coverage
#     bins, with an IQR ribbon. This isolates the *relationship* (the
#     scatter's cloud is hard to read) and puts basic sanitation and
#     open defecation on the same axis so their uncertainty profiles
#     can be compared directly. Prediction intervals for a bounded
#     proportion are typically widest at mid-range coverage and narrow
#     near 0% / 100%, so this curve usually shows an inverted-U.
# -------------------------------------------------------

print("\nDrawing: uncertainty vs coverage trend comparison …")

fig, ax = plt.subplots(figsize=(FIG_WIDTH, PANEL_H + 0.5))

for df, colour, lab in [
    (bs, BS_COLOUR, "Basic sanitation"),
    (od, OD_COLOUR, "Open defecation"),
]:
    x, y = clean_xy(df)
    cen, med, q25, q75 = binned_median_trend(x, y)
    ax.fill_between(cen, q25, q75, color=colour, alpha=0.15, zorder=1)
    ax.plot(cen, med, color=dark(colour), lw=2.2, marker="o", ms=3.5,
            zorder=3, label=lab)

ax.set_xlim(-0.02, 1.02)
ax.set_ylim(bottom=0)
ax.set_xlabel("Predicted proportion — coverage (basic sanitation) / rate (open defecation)",
              fontsize=7, labelpad=3)
ax.set_ylabel("90% PI width — median (IQR band)", fontsize=7)
ax.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
ax.spines[["top", "right"]].set_visible(False)
ax.grid(linewidth=0.4, color="#cccccc", zorder=0)
ax.legend(frameon=False, loc="upper right")

fig.subplots_adjust(left=0.10, right=0.97, top=0.94, bottom=0.16)
for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig_uncertainty_vs_coverage_trend.{ext}")
    fig.savefig(out, dpi=DPI, format=ext)
    print(f"  Saved: {out}")
plt.close(fig)

print("\nDone.")

# -------------------------------------------------------
# 10. Uncertainty vs coverage — JMP data availability
#     Two-panel side-by-side figure (a = BS, b = OD).
#
#     Four groups per panel:
#       1. In training data + JMP 2024 available  → filled circle, outcome colour, PSU-scaled size
#       2. In training data + no JMP 2024          → filled triangle, outcome colour, PSU-scaled size
#       3. Not in training + JMP 2024 available   → open circle, grey, standard size
#       4. Not in training + no JMP 2024          → open triangle, grey, standard size
#
#     Training membership : NAME_0 / NAME_1 matched to country_cov / HH7_region_cov
#     JMP availability    : sanitation_basic / open_defecation column is not NaN
#     PSU weight          : n_psu_weight_scaled (median across clusters per district)
# -------------------------------------------------------

TRAIN_DIR = "data/processed/training_subcomponents"
BS_TRAIN  = os.path.join(TRAIN_DIR, "basic_sanitation_training_with_covariates_v2.csv")
OD_TRAIN  = os.path.join(TRAIN_DIR, "open_defecation_training_with_covariates_v2.csv")

# --- Colours and markers ---
# Dark = in training data, light = not in training data
# Triangle = no JMP 2024 estimate, circle = has JMP 2024 estimate

# BS: green palette
BS_DARK  = "#006837"   # dark green  — in training
BS_LIGHT = "#74c476"   # medium green — not in training (stronger, more legible)

# OD: orange-brown palette
OD_DARK  = "#7f2704"   # dark brown-orange — in training
OD_LIGHT = "#fd8d3c"   # medium orange     — not in training (stronger, more legible)

ALPHA_DARK  = 0.75
ALPHA_LIGHT = 0.40

MARKER_CIRCLE   = "o"  # has JMP 2024 estimate
MARKER_TRIANGLE = "^"  # no JMP 2024 estimate

OUTLINE_LW   = 0.6
SCATTER_SIZE = 10      # uniform size for all points

# Legend handle sizes
_LEG_S = 40


# Harmonise training country names (country_cov) to the prediction NAME_0
# spelling, so training membership is not lost to spelling differences
# (e.g. "North Macedonia" vs "Macedonia").
_NAME_FIXES = {
    "North Macedonia":                  "Macedonia",
    "Eswatini":                         "Swaziland",
    "Lao People's Democratic Republic": "Laos",
}


def _prep_jmp_figure_data(pred_df, train_csv, jmp_col):
    """
    Annotate prediction df with training membership, PSU weight, and JMP flag.
    Returns annotated copy of pred_df (one row per district).
    """
    # Load training data; aggregate PSU weight to one row per district
    tr = pd.read_csv(
        train_csv,
        usecols=lambda c: c in {"country_cov", "n_psu_weight_scaled"},
    )
    psu_agg = (
        tr.groupby("country_cov", sort=False)["n_psu_weight_scaled"]
        .median()
        .reset_index()
        .rename(columns={
            "country_cov":         "NAME_0",
            "n_psu_weight_scaled": "psu_weight",
        })
    )
    psu_agg["NAME_0"] = psu_agg["NAME_0"].replace(_NAME_FIXES)

    df = pred_df.copy()
    df = df.merge(psu_agg, on="NAME_0", how="left")

    df["in_training"] = df["psu_weight"].notna()
    df["jmp_avail"]   = df[jmp_col].notna()
    df["marker_size"] = SCATTER_SIZE

    return df


def _scatter_group(ax, df, mask, colour, marker, alpha, edgecolors, zorder=2):
    sub = df[mask & df["median"].notna() & df["width_90"].notna()]
    if sub.empty:
        return
    ax.scatter(
        sub["median"], sub["width_90"],
        s=sub["marker_size"],
        c=colour,
        marker=marker,
        alpha=alpha,
        linewidths=OUTLINE_LW,
        edgecolors=edgecolors,
        zorder=zorder,
    )


print("\nDrawing: uncertainty vs coverage — JMP availability …")

bs_jmp = _prep_jmp_figure_data(bs, BS_TRAIN, "sanitation_basic")
od_jmp = _prep_jmp_figure_data(od, OD_TRAIN, "open_defecation")

_ymax_jmp = max(np.nanpercentile(bs["width_90"], 99),
                np.nanpercentile(od["width_90"], 99))
_ymax_jmp = float(np.ceil(_ymax_jmp * 20) / 20)

fig, (ax_bs, ax_od) = plt.subplots(
    1, 2,
    figsize=(FIG_WIDTH, PANEL_H + 0.5),
    sharey=True,
)

for ax, df_j, c_dark, c_light, label, title, xlab in [
    (ax_bs, bs_jmp, BS_DARK, BS_LIGHT, "a", "Basic sanitation",
     "Predicted basic sanitation coverage (median)"),
    (ax_od, od_jmp, OD_DARK, OD_LIGHT, "b", "Open defecation",
     "Predicted open defecation rate (median)"),
]:
    # Light layer first (not in training) — drawn behind
    _scatter_group(ax, df_j,
                   mask=~df_j["in_training"] & df_j["jmp_avail"],
                   colour=c_light, marker=MARKER_CIRCLE,
                   alpha=ALPHA_LIGHT, edgecolors=dark(c_light), zorder=1)
    _scatter_group(ax, df_j,
                   mask=~df_j["in_training"] & ~df_j["jmp_avail"],
                   colour=c_light, marker=MARKER_TRIANGLE,
                   alpha=ALPHA_LIGHT, edgecolors=dark(c_light), zorder=2)

    # Dark layer (in training) — drawn on top
    _scatter_group(ax, df_j,
                   mask=df_j["in_training"] & df_j["jmp_avail"],
                   colour=c_dark, marker=MARKER_CIRCLE,
                   alpha=ALPHA_DARK, edgecolors=dark(c_dark), zorder=3)
    _scatter_group(ax, df_j,
                   mask=df_j["in_training"] & ~df_j["jmp_avail"],
                   colour=c_dark, marker=MARKER_TRIANGLE,
                   alpha=ALPHA_DARK, edgecolors=dark(c_dark), zorder=4)

    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.005, _ymax_jmp)
    ax.set_xlabel(xlab, fontsize=7, labelpad=3)
    ax.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(linewidth=0.4, color="#cccccc", zorder=0)
    ax.set_title(f"$\\bf{{{label}}}$  {title}", fontsize=8, loc="left", pad=4)

ax_bs.set_ylabel("90% PI width (percentage points)", fontsize=7)
ax_od.set_ylabel("")

# --- Shared legend (placed below the figure) ---
import matplotlib.lines as mlines

_D = "#444444"
_L = "#aaaaaa"

_leg_handles = [
    mlines.Line2D([], [], marker=MARKER_CIRCLE, color="w",
                  markerfacecolor=_D, markeredgecolor=dark(_D),
                  markeredgewidth=OUTLINE_LW, markersize=np.sqrt(_LEG_S),
                  label="In training data & JMP estimate available in 2024"),
    mlines.Line2D([], [], marker=MARKER_TRIANGLE, color="w",
                  markerfacecolor=_D, markeredgecolor=dark(_D),
                  markeredgewidth=OUTLINE_LW, markersize=np.sqrt(_LEG_S),
                  label="In training data but no JMP estimate in 2024"),
    mlines.Line2D([], [], marker=MARKER_CIRCLE, color="w",
                  markerfacecolor=_L, markeredgecolor=dark(_L),
                  markeredgewidth=OUTLINE_LW, markersize=np.sqrt(_LEG_S),
                  label="Not in training but JMP estimate available in 2024"),
    mlines.Line2D([], [], marker=MARKER_TRIANGLE, color="w",
                  markerfacecolor=_L, markeredgecolor=dark(_L),
                  markeredgewidth=OUTLINE_LW, markersize=np.sqrt(_LEG_S),
                  label="Not in training & no JMP estimate in 2024"),
]

fig.legend(
    handles=_leg_handles,
    loc="lower center",
    bbox_to_anchor=(0.5, -0.06),
    ncol=2,
    fontsize=6,
    frameon=False,
    handletextpad=0.5,
    columnspacing=1.5,
)

fig.subplots_adjust(left=0.10, right=0.97, top=0.93, bottom=0.20, wspace=0.10)
for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig_uncertainty_vs_coverage_jmp_availability.{ext}")
    fig.savefig(out, dpi=DPI, format=ext, bbox_inches="tight")
    print(f"  Saved: {out}")
plt.close(fig)

print("\nAll done.")

# -------------------------------------------------------
# 11. Count countries with no JMP 2024 national estimate
# -------------------------------------------------------

print("\n" + "="*55)
print("Section 11 — Countries with no JMP 2024 estimate")
print("="*55)

for df, outcome, jmp_col in [
    (bs, "Basic sanitation", "sanitation_basic"),
    (od, "Open defecation",  "open_defecation"),
]:
    country_jmp = (
        df.groupby("NAME_0")[jmp_col]
        .first()          # one JMP value per country (same for all districts)
        .reset_index()
    )
    n_total   = len(country_jmp)
    n_no_jmp  = country_jmp[jmp_col].isna().sum()
    n_has_jmp = n_total - n_no_jmp

    print(f"\n{outcome}:")
    print(f"  Total countries predicted : {n_total}")
    print(f"  With JMP 2024 estimate    : {n_has_jmp}")
    print(f"  Without JMP 2024 estimate : {n_no_jmp} "
          f"({100 * n_no_jmp / n_total:.1f}%)")

    no_jmp_countries = (
        country_jmp.loc[country_jmp[jmp_col].isna(), "NAME_0"]
        .sort_values().tolist()
    )
    print(f"  Countries without estimate: {no_jmp_countries}")

# -------------------------------------------------------
# 12. Uncertainty by DATA-AVAILABILITY stratum  (SUGGESTED)
#     Directly answers the "you could know where data is scarce without
#     the modelling" critique. Groups districts into the 2x2 evidence
#     strata (survey membership x JMP-2024 availability) and shows the
#     FULL distribution of 90% PI width within each.
#
#     The point of the figure is the *spread and overlap*: if data
#     scarcity mapped one-to-one onto uncertainty, each stratum would be
#     a tight band. Instead, the most data-poor stratum shows a wide
#     range — some gap districts are well-constrained by covariates,
#     others are not — which is exactly the information a data-inventory
#     map cannot provide. A reference line marks a "usable-precision"
#     threshold; the console reports what fraction of the most data-poor
#     stratum still falls below it.
# -------------------------------------------------------

print("\n" + "="*55)
print("Section 12 — Uncertainty by data-availability stratum")
print("="*55)

# Fixed 2x2 order, from most to least evidence
STRATUM_ORDER = [
    "Survey + JMP",
    "Survey, no JMP",
    "No survey, JMP",
    "No survey, no JMP",
]

# "Usable-precision" reference threshold for the annotation / fraction.
# 0.25 = a 90% interval no wider than 25 percentage points. Adjust to a
# value you can defend as decision-relevant for your use case.
USABLE_WIDTH = 0.25


def _assign_stratum(df):
    df = df.copy()
    df["group"] = np.select(
        [
            df["in_training"] & df["jmp_avail"],
            df["in_training"] & ~df["jmp_avail"],
            ~df["in_training"] & df["jmp_avail"],
        ],
        ["Survey + JMP", "Survey, no JMP", "No survey, JMP"],
        default="No survey, no JMP",
    )
    return df


bs_strat = _assign_stratum(bs_jmp)
od_strat = _assign_stratum(od_jmp)

# Console summary — the numbers to quote in the rebuttal / results
for name, df_s in [("Basic sanitation", bs_strat), ("Open defecation", od_strat)]:
    print(f"\n{name}:")
    for g in STRATUM_ORDER:
        w = df_s.loc[df_s["group"] == g, "width_90"].dropna()
        if len(w) == 0:
            continue
        frac_usable = (w < USABLE_WIDTH).mean()
        print(f"  {g:<18} n={len(w):>5}  "
              f"median={w.median():.2f}  IQR=[{w.quantile(.25):.2f},{w.quantile(.75):.2f}]  "
              f"range=[{w.min():.2f},{w.max():.2f}]  "
              f"%<{USABLE_WIDTH:.0%}={frac_usable:.0%}")

# --- Figure: two stacked panels, one box+jitter per stratum ---
rng = np.random.default_rng(42)
n   = len(STRATUM_ORDER)

fig, (ax_bs, ax_od) = plt.subplots(
    2, 1,
    figsize=(max(FIG_WIDTH, n * 1.15), PANEL_H * 2 + 0.4),
    gridspec_kw={"hspace": 0.55},
)

for ax, df_s, colour, label, title in [
    (ax_bs, bs_strat, BS_COLOUR, "a", "Basic sanitation"),
    (ax_od, od_strat, OD_COLOUR, "b", "Open defecation"),
]:
    for i, g in enumerate(STRATUM_ORDER):
        vals = df_s.loc[df_s["group"] == g, "width_90"].dropna().to_numpy()
        draw_box(ax, vals, i, colour, rng)

    # "Usable-precision" reference line
    ax.axhline(USABLE_WIDTH, color="#555555", lw=0.9, ls=":", zorder=6)
    ax.text(n - 0.45, USABLE_WIDTH + 0.01,
            f"{USABLE_WIDTH:.0%} width", fontsize=6, color="#555555",
            ha="right", va="bottom")

    format_ax(ax, n, STRATUM_ORDER,
              xlabel="Data availability" if ax is ax_od else None,
              panel_label=label, title=title,
              ylabel="90% PI width (percentage points)")

fig.subplots_adjust(left=0.10, right=0.97, top=0.95, bottom=0.18)
for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig_uncertainty_by_data_availability.{ext}")
    fig.savefig(out, dpi=DPI, format=ext)
    print(f"  Saved: {out}")
plt.close(fig)

print("\nSection 12 done.")

# -------------------------------------------------------
# 13. Combined 4-panel figure: uncertainty vs coverage scatter (top)
#     + survey / no-survey box plots (bottom).            (SUGGESTED)
#
#     Layout (2 rows x 2 columns):
#       a | b   scatter: 90% PI width vs predicted coverage
#       c | d   horizontal box: 90% PI width by survey membership
#     Columns: basic sanitation (left) | open defecation (right).
#
#     Scatter points are coloured by survey membership only (darker = in
#     training / has survey data, lighter = no survey). No marker shapes,
#     no legend: the box-plot category labels below (Survey / No survey),
#     drawn in the same two shades, double as the scatter's key. The
#     scatter y-axis and box x-axis share the same 90% PI-width scale so
#     the two rows read as one figure.
#
#     Horizontal box style mirrors draw_box_h in
#     04_plot_sanitation_predictions.py.
# -------------------------------------------------------

print("\n" + "="*55)
print("Section 13 — Combined scatter + survey/no-survey box")
print("="*55)


def draw_box_h(ax, vals, y_pos, colour, rng, box_half=BOX_HALF):
    """Horizontal boxplot + uniform jitter centred on y_pos (matches
    draw_box_h in 04_plot_sanitation_predictions.py)."""
    if len(vals) == 0:
        return
    dark_col = dark(colour)
    jitter = rng.uniform(-box_half * 0.85, box_half * 0.85, size=len(vals))
    ax.scatter(vals, y_pos + jitter,
               s=JIT_SIZE, c=colour, alpha=JIT_ALPHA,
               edgecolors=dark_col, linewidths=0.3, zorder=1)
    q25, q50, q75 = np.percentile(vals, [25, 50, 75])
    iqr      = q75 - q25
    lo_whisk = vals[vals >= q25 - 1.5 * iqr].min()
    hi_whisk = vals[vals <= q75 + 1.5 * iqr].max()
    box_patch = mpatches.FancyBboxPatch(
        (q25, y_pos - box_half), q75 - q25, box_half * 2,
        boxstyle="square,pad=0",
        facecolor="none", edgecolor=dark_col, linewidth=BOX_LW, zorder=3,
    )
    ax.add_patch(box_patch)
    ax.fill_between([q25, q75], y_pos - box_half, y_pos + box_half,
                    color=colour, alpha=BOX_ALPHA, zorder=4)
    ax.plot([q50, q50], [y_pos - box_half, y_pos + box_half],
            color=dark_col, lw=MED_LW, zorder=5, solid_capstyle="butt")
    cap_w = box_half * 0.45
    for x_box, x_whisk in [(q25, lo_whisk), (q75, hi_whisk)]:
        ax.plot([x_box, x_whisk], [y_pos, y_pos],
                color=dark_col, lw=0.9, zorder=3)
        ax.plot([x_whisk, x_whisk], [y_pos - cap_w, y_pos + cap_w],
                color=dark_col, lw=0.9, zorder=3)


# --- Survey / no-survey colour shades (uncertainty palettes) ---
_BS_UNC_CMAP = mc.LinearSegmentedColormap.from_list(
    "YlPu_custom", ["#ffffcc", "#c994c7", "#67001f"], N=256)
BS_SURVEY_C = mc.to_hex(_BS_UNC_CMAP(0.62))   # darker purple — has survey
BS_NOSURV_C = mc.to_hex(_BS_UNC_CMAP(0.30))   # lighter purple — no survey
OD_SURVEY_C = mc.to_hex(plt.get_cmap("YlOrRd")(0.78))  # darker red — has survey
OD_NOSURV_C = mc.to_hex(plt.get_cmap("YlOrRd")(0.40))  # lighter — no survey

SC_SIZE      = 5
SC_A_SURVEY  = 0.55
SC_A_NOSURV  = 0.40
BOX_HALF_H   = 0.30   # slimmer boxes for the 2-category panels

# Shared 90% PI-width scale across scatter (y) and box (x)
_wmax = max(np.nanpercentile(bs["width_90"], 99),
            np.nanpercentile(od["width_90"], 99))
_wmax = float(np.ceil(_wmax * 20) / 20)

rng = np.random.default_rng(42)

fig = plt.figure(figsize=(FIG_WIDTH, PANEL_H * 1.75))
gs  = fig.add_gridspec(
    2, 2, height_ratios=[2.7, 1.15],
    hspace=0.55, wspace=0.20,
    left=0.09, right=0.975, top=0.93, bottom=0.13,
)

for col, (df_j, surv_c, nos_c, sc_letter, bx_letter, title, xlab) in enumerate([
    (bs_jmp, BS_SURVEY_C, BS_NOSURV_C, "a", "c", "Basic sanitation",
     "Predicted basic sanitation coverage (median)"),
    (od_jmp, OD_SURVEY_C, OD_NOSURV_C, "b", "d", "Open defecation",
     "Predicted open defecation rate (median)"),
]):
    surv   = df_j["in_training"]
    n_surv = int(surv.sum())
    n_nos  = int((~surv).sum())

    # ---- Scatter (top) : coloured by survey membership only ----
    ax_s = fig.add_subplot(gs[0, col])
    ax_s.scatter(df_j.loc[~surv, "median"], df_j.loc[~surv, "width_90"],
                 s=SC_SIZE, color=nos_c, alpha=SC_A_NOSURV,
                 linewidths=0, zorder=1)
    ax_s.scatter(df_j.loc[surv, "median"], df_j.loc[surv, "width_90"],
                 s=SC_SIZE, color=surv_c, alpha=SC_A_SURVEY,
                 linewidths=0, zorder=2)
    ax_s.set_xlim(-0.02, 1.02)
    ax_s.set_ylim(-0.005, _wmax)
    ax_s.set_xlabel(xlab, fontsize=7, labelpad=3)
    if col == 0:
        ax_s.set_ylabel("90% PI width (percentage points)", fontsize=7)
    ax_s.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax_s.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax_s.spines[["top", "right"]].set_visible(False)
    ax_s.grid(linewidth=0.4, color="#cccccc", zorder=0)
    ax_s.set_title(f"$\\bf{{{sc_letter}}}$  {title}", fontsize=8, loc="left", pad=4)

    # ---- Box (bottom) : survey vs no survey, shares width scale ----
    ax_b = fig.add_subplot(gs[1, col])
    for k, (c, vals) in enumerate([
        (surv_c, df_j.loc[surv,  "width_90"].dropna().to_numpy()),
        (nos_c,  df_j.loc[~surv, "width_90"].dropna().to_numpy()),
    ]):
        draw_box_h(ax_b, vals, k, c, rng, box_half=BOX_HALF_H)
    ax_b.set_ylim(1.6, -0.6)            # "Survey" on top
    ax_b.set_xlim(-0.005, _wmax)
    ax_b.set_yticks([0, 1])
    ax_b.set_yticklabels([f"Survey\n(n={n_surv})", f"No survey\n(n={n_nos})"],
                         fontsize=6)
    ax_b.tick_params(axis="y", length=0)
    ax_b.set_xlabel("90% PI width", fontsize=7, labelpad=2)
    ax_b.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax_b.grid(axis="x", linewidth=0.4, color="#cccccc", zorder=0)
    ax_b.spines[["top", "right", "left"]].set_visible(False)
    ax_b.set_title(f"$\\bf{{{bx_letter}}}$", fontsize=8, loc="left", pad=3)

    # Console summary for the rebuttal
    ws = df_j.loc[surv,  "width_90"].dropna()
    wn = df_j.loc[~surv, "width_90"].dropna()
    print(f"\n{title}:")
    print(f"  Survey    n={len(ws):>5}  median={ws.median():.2f}  "
          f"IQR=[{ws.quantile(.25):.2f},{ws.quantile(.75):.2f}]")
    print(f"  No survey n={len(wn):>5}  median={wn.median():.2f}  "
          f"IQR=[{wn.quantile(.25):.2f},{wn.quantile(.75):.2f}]")

for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig_uncertainty_scatter_survey_box.{ext}")
    fig.savefig(out, dpi=DPI, format=ext)
    print(f"  Saved: {out}")
plt.close(fig)

print("\nSection 13 done.")

# -------------------------------------------------------
# 14. Combined figure: uncertainty-vs-coverage scatter (row 1)
#     + three box rows, each split into two categories:      (SUGGESTED)
#       survey vs no survey | JMP vs no JMP |
#       "no survey & no JMP" vs the rest.
#
#     Layout (4 rows x 2 columns):
#       a | b   scatter  — 90% PI width vs predicted coverage
#       c | d   box      — survey vs no survey
#       e | f   box      — JMP estimate vs no JMP estimate
#       g | h   box      — "no survey & no JMP" vs all other districts
#     Columns: basic sanitation (green, left) | open defecation (orange, right).
#
#     A single outcome colour is used throughout (no shape / shade
#     encoding); categories are named on each box's y-axis. The scatter
#     y-axis and the box x-axes share the 90% PI-width scale.
# -------------------------------------------------------

print("\n" + "="*55)
print("Section 14 — Scatter + survey / JMP / strata boxes")
print("="*55)

BOX_HALF_H2 = 0.30
SC_SIZE_14  = 5      # scatter point size
SC_ALPHA_14 = 0.40   # scatter point opacity

# Single shade per outcome (green / orange)
BS_SINGLE = "#1a9850"
OD_SINGLE = "#e6550d"


def _style_box_ax(ax, labels, wmax):
    ax.set_ylim(1.6, -0.6)
    ax.set_xlim(-0.005, wmax)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(labels, fontsize=6)
    ax.tick_params(axis="y", length=0)
    ax.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax.grid(axis="x", linewidth=0.4, color="#cccccc", zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)


# Shared 90% PI-width scale across the scatter (y) and the box panels (x).
# Fixed to the full 0-100% range for both outcomes.
_wmax14 = 1.0

rng = np.random.default_rng(42)

fig = plt.figure(figsize=(FIG_WIDTH, 8.0))
gs  = fig.add_gridspec(
    4, 2, height_ratios=[2.8, 1.0, 1.0, 1.0],
    hspace=0.45, wspace=0.14,
    left=0.16, right=0.975, top=0.955, bottom=0.055,
)

for col, (df_j, colr, letters, title, xlab) in enumerate([
    (bs_jmp, BS_SINGLE, ("a", "c", "e", "g"), "Basic sanitation",
     "Predicted basic sanitation coverage (median)"),
    (od_jmp, OD_SINGLE, ("b", "d", "f", "h"), "Open defecation",
     "Predicted open defecation rate (median)"),
]):
    in_tr = df_j["in_training"]
    jmp   = df_j["jmp_avail"]
    worst = ~in_tr & ~jmp

    # ---- Row 1: scatter (single shade) ----
    ax_s = fig.add_subplot(gs[0, col])
    ax_s.scatter(df_j["median"], df_j["width_90"],
                 s=SC_SIZE_14, c=colr, alpha=SC_ALPHA_14,
                 edgecolors=dark(colr), linewidths=0.3, zorder=1)
    ax_s.set_xlim(-0.02, 1.02)
    ax_s.set_ylim(-0.005, _wmax14)
    ax_s.set_xlabel(xlab, fontsize=7, labelpad=3)
    if col == 0:
        ax_s.set_ylabel("90% PI width (percentage points)", fontsize=7)
    ax_s.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax_s.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax_s.spines[["top", "right"]].set_visible(False)
    ax_s.grid(linewidth=0.4, color="#cccccc", zorder=0)
    ax_s.set_title(f"$\\bf{{{letters[0]}}}$  {title}", fontsize=8, loc="left", pad=4)

    # ---- Box rows: (letter, (name_top, mask_top), (name_bot, mask_bot)) ----
    # Category names are shown only on the left (basic sanitation) column;
    # the open-defecation column shows just the sample size (n=...).
    box_rows = [
        (letters[1],
         ("Survey data",       in_tr),
         ("No survey data",    ~in_tr)),
        (letters[2],
         ("JMP estimate",      jmp),
         ("No JMP estimate",   ~jmp)),
        (letters[3],
         ("Survey and/or JMP", ~worst),
         ("No survey &\nno JMP", worst)),
    ]

    for r, (letter, (name_top, m_top), (name_bot, m_bot)) in enumerate(box_rows, start=1):
        n_top, n_bot = int(m_top.sum()), int(m_bot.sum())
        if col == 0:
            lab_top = f"{name_top}\n(n={n_top})"
            lab_bot = f"{name_bot}\n(n={n_bot})"
        else:                       # open defecation — sample size only
            lab_top = f"n={n_top}"
            lab_bot = f"n={n_bot}"
        ax_b = fig.add_subplot(gs[r, col])
        draw_box_h(ax_b, df_j.loc[m_top, "width_90"].dropna().to_numpy(),
                   0, colr, rng, box_half=BOX_HALF_H2)
        draw_box_h(ax_b, df_j.loc[m_bot, "width_90"].dropna().to_numpy(),
                   1, colr, rng, box_half=BOX_HALF_H2)
        _style_box_ax(ax_b, [lab_top, lab_bot], _wmax14)
        ax_b.set_title(f"$\\bf{{{letter}}}$", fontsize=8, loc="left", pad=3)
        if r == 3:
            ax_b.set_xlabel("90% PI width", fontsize=7, labelpad=2)
        else:
            ax_b.set_xticklabels([])

    # Console summary
    print(f"\n{title}:")
    for lab, m in [("Survey", in_tr), ("No survey", ~in_tr),
                   ("JMP", jmp), ("No JMP", ~jmp),
                   ("Rest", ~worst), ("No survey&no JMP", worst)]:
        v = df_j.loc[m, "width_90"].dropna()
        print(f"  {lab:<16} n={len(v):>5}  median={v.median():.2f}  "
              f"IQR=[{v.quantile(.25):.2f},{v.quantile(.75):.2f}]")

for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig_uncertainty_scatter_jmp_strata.{ext}")
    fig.savefig(out, dpi=DPI, format=ext)
    print(f"  Saved: {out}")
plt.close(fig)

print("\nSection 14 done.")

# -------------------------------------------------------
# 15. Priority countries for data investment.              (SUGGESTED)
#     Top 10 data-gap countries ranked by the population living
#     under uncertain estimates, coloured by gap type.
#
#     Priority metric (per country):
#       burden = sum over districts of (population * 90% PI width)
#              = total population x population-weighted mean PI width
#     i.e. the population whose sanitation status is both unmeasured
#     and uncertain — where new data collection is most urgent.
#
#     Gap type (country-level; survey & JMP are national attributes):
#       No survey & no JMP  (compound gap — highest priority)
#       No survey only
#       No JMP only
#     Countries with both a recent survey and a JMP estimate are excluded.
#     Bar length = total population (millions); the population-weighted
#     mean PI width is annotated at the bar end. Colour = gap type on a
#     severity-graded red scale (compound gap darkest).
# -------------------------------------------------------

print("\n" + "="*55)
print("Section 15 — Priority countries for data investment")
print("="*55)

POP_COL = "worldpop_sum"

GAP_ORDER  = ["No survey & no JMP", "No survey only", "No JMP only"]
GAP_COLOUR = {
    "No survey & no JMP": "#a50f15",   # dark red — compound gap
    "No survey only":     "#fb6a4a",   # mid red
    "No JMP only":        "#fcae91",   # light red
}


def _gap_type(in_tr, jmp):
    if not in_tr and not jmp:
        return "No survey & no JMP"
    if not in_tr and jmp:
        return "No survey only"
    if in_tr and not jmp:
        return "No JMP only"
    return "Complete"          # both present — not a data gap


def _country_priority(df_j):
    d = df_j.dropna(subset=["width_90", POP_COL]).copy()
    d["pw"] = d[POP_COL] * d["width_90"]
    g = (d.groupby("NAME_0")
           .agg(pop=(POP_COL, "sum"),
                burden=("pw", "sum"),
                uw_width=("width_90", "mean"),
                med_width=("width_90", "median"),
                in_tr=("in_training", "first"),
                jmp=("jmp_avail", "first"),
                fragile=("fragile_context", "first"),
                n_dist=("width_90", "count"))
           .reset_index())
    g["wmean_width"] = g["burden"] / g["pop"]
    g["gap"] = [_gap_type(a, b) for a, b in zip(g["in_tr"], g["jmp"])]
    g["is_fragile"] = g["fragile"].astype(str).str.strip() == "Fragile or Extremely Fragile"
    return g[g["gap"] != "Complete"]


# Fragility colours
FRAG_COLOUR = {True: "#b2182b", False: "#4393c3"}   # fragile = red, non-fragile = blue
FRAG_LABEL  = {True: "Fragile or Extremely Fragile", False: "Non-fragile"}


COMPOUND = "No survey & no JMP"
TOP_N = 10

fig, (ax_bs, ax_od) = plt.subplots(
    2, 1, figsize=(FIG_WIDTH, 6.4),
    gridspec_kw={"hspace": 0.32},
)

for ax, df_j, letter, title in [
    (ax_bs, bs_jmp, "a", "Basic sanitation"),
    (ax_od, od_jmp, "b", "Open defecation"),
]:
    g = _country_priority(df_j)
    # Strict compound gap only (no recent survey AND no JMP estimate),
    # ranked by uncertainty (population-weighted mean 90% PI width).
    comp = g[g["gap"] == COMPOUND].copy()
    top = comp.nlargest(TOP_N, "wmean_width").sort_values("wmean_width", ascending=True)

    y = np.arange(len(top))
    colours = [FRAG_COLOUR[bool(f)] for f in top["is_fragile"]]
    ax.barh(y, top["wmean_width"], color=colours,
            edgecolor="#555555", linewidth=0.4, zorder=3, height=0.72)

    # Label each bar with the country's population (the context weight)
    xpad = 0.012
    for yi, xv, pop_m in zip(y, top["wmean_width"], top["pop"] / 1e6):
        pop_txt = f"{pop_m:.0f}M" if pop_m >= 1 else f"{pop_m*1000:.0f}k"
        ax.text(xv + xpad, yi, pop_txt, va="center", ha="left",
                fontsize=5.5, color="#333333")

    ax.set_yticks(y)
    ax.set_yticklabels(top["NAME_0"], fontsize=6.5)
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("Population-weighted mean 90% PI width", fontsize=7)
    ax.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax.tick_params(axis="y", length=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", linewidth=0.4, color="#cccccc", zorder=0)
    ax.set_title(f"$\\bf{{{letter}}}$  {title}", fontsize=8, loc="left", pad=4)

    print(f"\n{title} — compound-gap priority (top {TOP_N} by uncertainty):")
    for _, r in top.iloc[::-1].iterrows():
        print(f"  {r['NAME_0']:<24} wmean_PI={r['wmean_width']:.0%}  "
              f"pop={r['pop']/1e6:6.1f}M  "
              f"fragile={'Y' if r['is_fragile'] else 'N'}")

# Shared fragility legend
_frag_handles = [mpatches.Patch(facecolor=FRAG_COLOUR[k], edgecolor="#555555",
                                linewidth=0.4, label=FRAG_LABEL[k])
                 for k in (True, False)]
fig.legend(handles=_frag_handles, loc="lower center",
           bbox_to_anchor=(0.5, 0.0), ncol=2, fontsize=6,
           frameon=False, handletextpad=0.5, columnspacing=1.8)

fig.subplots_adjust(left=0.22, right=0.965, top=0.93, bottom=0.11)
for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig_priority_countries_data_investment.{ext}")
    fig.savefig(out, dpi=DPI, format=ext)
    print(f"  Saved: {out}")
plt.close(fig)

print("\nSection 15 done.")

# -------------------------------------------------------
# 16. Priority scatter: uncertainty vs population.         (SUGGESTED)
#     Alternative to the ranked bars — plots the two dimensions
#     directly for the strict compound-gap countries.
#
#       x = population-weighted mean 90% PI width (uncertainty)
#       y = total population (log scale)
#       colour = fragility status; each point labelled with the country
#
#     Top-right (high uncertainty AND large population) = most urgent
#     data-collection priority. Median reference lines split the plot
#     into priority quadrants.
# -------------------------------------------------------

print("\n" + "="*55)
print("Section 16 — Priority scatter (uncertainty vs population)")
print("="*55)


def _human_pop(x, _pos=None):
    if x >= 1e6:
        return f"{x/1e6:.0f}M"
    if x >= 1e3:
        return f"{x/1e3:.0f}k"
    return f"{x:.0f}"


def _declutter_labels(fig, anns, n_iter=200, pad=1.0):
    """Nudge annotation labels vertically (in points) until their rendered
    boxes no longer overlap. Adds a faint leader line for labels that end
    up far from their anchor."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    for _ in range(n_iter):
        moved = False
        boxes = [a.get_window_extent(r) for a in anns]
        for i in range(len(anns)):
            for j in range(i + 1, len(anns)):
                bi, bj = boxes[i], boxes[j]
                if bi.overlaps(bj):
                    dxi, dyi = anns[i].xyann
                    dxj, dyj = anns[j].xyann
                    if bi.y0 <= bj.y0:
                        anns[i].xyann = (dxi, dyi - pad)
                        anns[j].xyann = (dxj, dyj + pad)
                    else:
                        anns[i].xyann = (dxi, dyi + pad)
                        anns[j].xyann = (dxj, dyj - pad)
                    moved = True
        if not moved:
            break
        fig.canvas.draw()


PRIORITY_SHADE = "#d6a0a0"

fig, (ax_bs, ax_od) = plt.subplots(
    2, 1, figsize=(FIG_WIDTH, 7.4),
    gridspec_kw={"hspace": 0.34},
)

for ax, df_j, letter, title in [
    (ax_bs, bs_jmp, "a", "Basic sanitation"),
    (ax_od, od_jmp, "b", "Open defecation"),
]:
    g = _country_priority(df_j)
    comp = g[g["gap"] == COMPOUND].copy()

    x = comp["wmean_width"].to_numpy()
    ypop = comp["pop"].to_numpy()
    colours = [FRAG_COLOUR[bool(f)] for f in comp["is_fragile"]]

    ax.set_yscale("log")
    ax.set_xlim(0, 1.0)
    ax.set_ylim(ypop.min() * 0.5, ypop.max() * 2.4)
    ytop = ax.get_ylim()[1]

    # Median reference lines + shaded top-right "priority" quadrant
    x_med = np.median(x)
    y_med = np.median(ypop)
    ax.fill_between([x_med, 1.0], y_med, ytop, color=PRIORITY_SHADE,
                    alpha=0.14, linewidth=0, zorder=0)
    ax.axvline(x_med, color="#bbbbbb", lw=0.7, ls="--", zorder=1)
    ax.axhline(y_med, color="#bbbbbb", lw=0.7, ls="--", zorder=1)
    ax.annotate("higher priority", ((x_med + 1.0) / 2, ytop),
                xytext=(0, -8), textcoords="offset points",
                fontsize=6, style="italic", color="#9c5a5a",
                ha="center", va="top", zorder=2)

    ax.scatter(x, ypop, s=34, c=colours, edgecolors="#444444",
               linewidths=0.5, zorder=3)

    # Country labels — left of point if on the right side, else right
    anns = []
    for xi, yi, name in zip(x, ypop, comp["NAME_0"]):
        right = xi <= 0.72
        a = ax.annotate(
            name, (xi, yi),
            xytext=(4 if right else -4, 0),
            textcoords="offset points", fontsize=5.5,
            va="center", ha="left" if right else "right",
            color="#222222", zorder=4)
        anns.append(a)
    _declutter_labels(fig, anns)

    ax.set_xlabel("Population-weighted mean 90% PI width (uncertainty)", fontsize=7)
    ax.set_ylabel("Population (log scale)", fontsize=7)
    ax.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(_human_pop))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="both", linewidth=0.3, color="#e2e2e2", zorder=0)
    ax.set_title(f"$\\bf{{{letter}}}$  {title}", fontsize=8, loc="left", pad=4)

# Shared fragility legend
fig.legend(handles=_frag_handles, loc="lower center",
           bbox_to_anchor=(0.5, 0.0), ncol=2, fontsize=6,
           frameon=False, handletextpad=0.5, columnspacing=1.8)

fig.subplots_adjust(left=0.12, right=0.965, top=0.94, bottom=0.10)
for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig_priority_scatter_uncertainty_population.{ext}")
    fig.savefig(out, dpi=DPI, format=ext)
    print(f"  Saved: {out}")
plt.close(fig)

print("\nSection 16 done.")

# -------------------------------------------------------
# 17. Priority scatter for the broader "no subnational survey"      (SUGGESTED)
#     group — every country lacking a recent subnational survey
#     (regardless of JMP availability). ~45 countries per outcome,
#     so only the priority-quadrant countries (above-median
#     uncertainty AND above-median population) are labelled.
#
#       x = population-weighted mean 90% PI width (uncertainty)
#       y = total population (log scale)
#       colour = fragility status
# -------------------------------------------------------

print("\n" + "="*55)
print("Section 17 — Priority scatter (no subnational survey)")
print("="*55)

NO_SURVEY_GAPS = ("No survey only", "No survey & no JMP")

fig, (ax_bs, ax_od) = plt.subplots(
    2, 1, figsize=(FIG_WIDTH, 7.4),
    gridspec_kw={"hspace": 0.34},
)

for ax, df_j, letter, title in [
    (ax_bs, bs_jmp, "a", "Basic sanitation"),
    (ax_od, od_jmp, "b", "Open defecation"),
]:
    g = _country_priority(df_j)
    ns = g[g["gap"].isin(NO_SURVEY_GAPS)].copy()

    x = ns["wmean_width"].to_numpy()
    ypop = ns["pop"].to_numpy()
    colours = [FRAG_COLOUR[bool(f)] for f in ns["is_fragile"]]

    ax.set_yscale("log")
    ax.set_xlim(0, 1.0)
    ax.set_ylim(ypop.min() * 0.5, ypop.max() * 2.4)
    ytop = ax.get_ylim()[1]

    x_med = np.median(x)
    y_med = np.median(ypop)
    ax.fill_between([x_med, 1.0], y_med, ytop, color=PRIORITY_SHADE,
                    alpha=0.14, linewidth=0, zorder=0)
    ax.axvline(x_med, color="#bbbbbb", lw=0.7, ls="--", zorder=1)
    ax.axhline(y_med, color="#bbbbbb", lw=0.7, ls="--", zorder=1)
    ax.annotate("higher priority", ((x_med + 1.0) / 2, ytop),
                xytext=(0, -8), textcoords="offset points",
                fontsize=6, style="italic", color="#9c5a5a",
                ha="center", va="top", zorder=2)

    ax.scatter(x, ypop, s=28, c=colours, edgecolors="#444444",
               linewidths=0.5, zorder=3)

    # Label only priority-quadrant countries (above both medians)
    anns = []
    for xi, yi, name in zip(x, ypop, ns["NAME_0"]):
        if xi > x_med and yi > y_med:
            right = xi <= 0.72
            a = ax.annotate(
                name, (xi, yi),
                xytext=(4 if right else -4, 0),
                textcoords="offset points", fontsize=5.5,
                va="center", ha="left" if right else "right",
                color="#222222", zorder=4)
            anns.append(a)
    if anns:
        _declutter_labels(fig, anns)

    ax.set_xlabel("Population-weighted mean 90% PI width (uncertainty)", fontsize=7)
    ax.set_ylabel("Population (log scale)", fontsize=7)
    ax.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(_human_pop))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="both", linewidth=0.3, color="#e2e2e2", zorder=0)
    ax.set_title(f"$\\bf{{{letter}}}$  {title}", fontsize=8, loc="left", pad=4)

    n_priority = int(((x > x_med) & (ypop > y_med)).sum())
    print(f"\n{title} — {len(ns)} no-survey countries, "
          f"{n_priority} in priority quadrant:")
    pq = ns[(ns["wmean_width"] > x_med) & (ns["pop"] > y_med)] \
        .sort_values("wmean_width", ascending=False)
    for _, rr in pq.iterrows():
        print(f"  {rr['NAME_0']:<24} wmean_PI={rr['wmean_width']:.0%}  "
              f"pop={rr['pop']/1e6:6.1f}M  "
              f"fragile={'Y' if rr['is_fragile'] else 'N'}")

fig.legend(handles=_frag_handles, loc="lower center",
           bbox_to_anchor=(0.5, 0.0), ncol=2, fontsize=6,
           frameon=False, handletextpad=0.5, columnspacing=1.8)

fig.subplots_adjust(left=0.12, right=0.965, top=0.94, bottom=0.10)
for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig_priority_scatter_no_survey.{ext}")
    fig.savefig(out, dpi=DPI, format=ext)
    print(f"  Saved: {out}")
plt.close(fig)

print("\nSection 17 done.")

# -------------------------------------------------------
# 18. Robustness: population-weighted vs unweighted mean PI.  (SUGGESTED)
#     One point per predicted country. If the population weighting
#     changed the country-level uncertainty summary, points would
#     depart from the 1:1 line. Countries departing by >3 percentage
#     points are labelled.
#
#       x = unweighted mean 90% PI width (simple mean over districts)
#       y = population-weighted mean 90% PI width
#       colour = fragility status
# -------------------------------------------------------

print("\n" + "="*55)
print("Section 18 — Weighted vs unweighted mean PI (robustness)")
print("="*55)

LABEL_THRESH = 0.06   # label countries whose weighted/unweighted means
                      # differ by more than this (percentage points / 100)


def _country_wt_unw(df_j):
    d = df_j.dropna(subset=["width_90", POP_COL]).copy()
    d["pw"] = d[POP_COL] * d["width_90"]
    g = (d.groupby("NAME_0")
           .agg(unw=("width_90", "mean"),
                pw_sum=("pw", "sum"),
                pop=(POP_COL, "sum"),
                fragile=("fragile_context", "first"),
                n=("width_90", "count"))
           .reset_index())
    g["wt"] = g["pw_sum"] / g["pop"]
    g["is_fragile"] = g["fragile"].astype(str).str.strip() == "Fragile or Extremely Fragile"
    return g


fig, (ax_bs, ax_od) = plt.subplots(
    1, 2, figsize=(FIG_WIDTH, FIG_WIDTH / 2 + 0.5),
)

for ax, df_j, letter, title in [
    (ax_bs, bs_jmp, "a", "Basic sanitation"),
    (ax_od, od_jmp, "b", "Open defecation"),
]:
    g = _country_wt_unw(df_j)
    r = g["unw"].corr(g["wt"])
    mad = (g["wt"] - g["unw"]).abs().mean()

    ax.plot([0, 1], [0, 1], color="#999999", lw=0.8, ls="--", zorder=1)
    colours = [FRAG_COLOUR[bool(f)] for f in g["is_fragile"]]
    ax.scatter(g["unw"], g["wt"], s=18, c=colours,
               edgecolors="#444444", linewidths=0.4, zorder=3)

    # Label countries that depart from the 1:1 line
    anns = []
    for _, rr in g.iterrows():
        if abs(rr["wt"] - rr["unw"]) > LABEL_THRESH:
            a = ax.annotate(rr["NAME_0"], (rr["unw"], rr["wt"]),
                            xytext=(4, 0), textcoords="offset points",
                            fontsize=5.5, va="center", ha="left",
                            color="#222222", zorder=4)
            anns.append(a)
    if anns:
        _declutter_labels(fig, anns)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.set_xlabel("Unweighted mean 90% PI width", fontsize=7)
    if letter == "a":
        ax.set_ylabel("Population-weighted mean 90% PI width", fontsize=7)
    ax.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(linewidth=0.3, color="#e8e8e8", zorder=0)
    ax.set_title(f"$\\bf{{{letter}}}$  {title}", fontsize=8, loc="left", pad=4)
    ax.annotate(f"r = {r:.3f}\nmean |diff| = {mad:.1%}",
                (0.03, 0.97), xycoords="axes fraction", fontsize=5.5,
                ha="left", va="top", color="#555555")

    print(f"\n{title}: r={r:.3f}  mean|diff|={mad:.1%}  "
          f"(n={len(g)} countries)")
    big = g.loc[(g["wt"] - g["unw"]).abs() > LABEL_THRESH] \
        .assign(diff=lambda t: t["wt"] - t["unw"]) \
        .sort_values("diff")
    for _, rr in big.iterrows():
        print(f"  {rr['NAME_0']:<24} unw={rr['unw']:.0%}  wt={rr['wt']:.0%}  "
              f"diff={rr['wt']-rr['unw']:+.0%}")

fig.legend(handles=_frag_handles, loc="lower center",
           bbox_to_anchor=(0.5, 0.0), ncol=2, fontsize=6,
           frameon=False, handletextpad=0.5, columnspacing=1.8)

fig.subplots_adjust(left=0.09, right=0.98, top=0.92, bottom=0.16, wspace=0.18)
for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig_uncertainty_weighted_vs_unweighted.{ext}")
    fig.savefig(out, dpi=DPI, format=ext)
    print(f"  Saved: {out}")
plt.close(fig)

print("\nSection 18 done.")

# -------------------------------------------------------
# 19. Priority scatter, weighted vs unweighted, side by side.  (SUGGESTED)
#     Strict compound-gap countries. Left column uses the
#     population-weighted mean 90% PI width; right column the
#     unweighted (simple) mean. Rows = outcome. Lets the reader see
#     directly whether the weighting moves any country's priority.
# -------------------------------------------------------

print("\n" + "="*55)
print("Section 19 — Priority scatter: weighted vs unweighted")
print("="*55)

comp_bs = _country_priority(bs_jmp)
comp_bs = comp_bs[comp_bs["gap"] == COMPOUND].copy()
comp_od = _country_priority(od_jmp)
comp_od = comp_od[comp_od["gap"] == COMPOUND].copy()

fig, axes = plt.subplots(2, 2, figsize=(FIG_WIDTH, 7.4))

cells = [
    (axes[0, 0], comp_bs, "wmean_width", "a", "Basic sanitation"),
    (axes[0, 1], comp_bs, "uw_width",    "b", "Basic sanitation"),
    (axes[1, 0], comp_od, "wmean_width", "c", "Open defecation"),
    (axes[1, 1], comp_od, "uw_width",    "d", "Open defecation"),
]

for ax, comp, xcol, letter, title in cells:
    x = comp[xcol].to_numpy()
    ypop = comp["pop"].to_numpy()
    colours = [FRAG_COLOUR[bool(f)] for f in comp["is_fragile"]]

    ax.set_yscale("log")
    ax.set_xlim(0, 1.0)
    ax.set_ylim(ypop.min() * 0.5, ypop.max() * 2.6)
    ytop = ax.get_ylim()[1]

    x_med = np.median(x)
    y_med = np.median(ypop)
    ax.fill_between([x_med, 1.0], y_med, ytop, color=PRIORITY_SHADE,
                    alpha=0.14, linewidth=0, zorder=0)
    ax.axvline(x_med, color="#bbbbbb", lw=0.7, ls="--", zorder=1)
    ax.axhline(y_med, color="#bbbbbb", lw=0.7, ls="--", zorder=1)

    ax.scatter(x, ypop, s=24, c=colours, edgecolors="#444444",
               linewidths=0.5, zorder=3)

    anns = []
    for xi, yi, name in zip(x, ypop, comp["NAME_0"]):
        right = xi <= 0.68
        a = ax.annotate(name, (xi, yi),
                        xytext=(3.5 if right else -3.5, 0),
                        textcoords="offset points", fontsize=5,
                        va="center", ha="left" if right else "right",
                        color="#222222", zorder=4)
        anns.append(a)
    _declutter_labels(fig, anns)

    ax.set_xlabel("Mean 90% PI width", fontsize=7)
    if letter in ("a", "c"):
        ax.set_ylabel("Population (log scale)", fontsize=7)
    ax.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(_human_pop))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="both", linewidth=0.3, color="#e8e8e8", zorder=0)
    ax.set_title(f"$\\bf{{{letter}}}$  {title}", fontsize=7.5, loc="left", pad=4)

# Column headers
fig.text(0.29, 0.965, "Population-weighted", fontsize=8, fontweight="bold",
         ha="center")
fig.text(0.76, 0.965, "Unweighted", fontsize=8, fontweight="bold", ha="center")

fig.legend(handles=_frag_handles, loc="lower center",
           bbox_to_anchor=(0.5, 0.0), ncol=2, fontsize=6,
           frameon=False, handletextpad=0.5, columnspacing=1.8)

fig.subplots_adjust(left=0.10, right=0.985, top=0.92, bottom=0.09,
                    wspace=0.22, hspace=0.30)
for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR, f"fig_priority_scatter_weighted_vs_unweighted.{ext}")
    fig.savefig(out, dpi=DPI, format=ext)
    print(f"  Saved: {out}")
plt.close(fig)

print("\nSection 19 done.")

# -------------------------------------------------------
# 20. Priority scatter (UNWEIGHTED) — paper-consistent version    (SUGGESTED)
#     Identical to Section 16 but the x-axis uses the unweighted
#     (simple) mean 90% PI width across districts, matching the
#     unweighted convention used elsewhere in the paper.
# -------------------------------------------------------

print("\n" + "="*55)
print("Section 20 — Priority scatter (unweighted)")
print("="*55)

fig, (ax_bs, ax_od) = plt.subplots(
    2, 1, figsize=(FIG_WIDTH, 7.4),
    gridspec_kw={"hspace": 0.34},
)

for ax, df_j, letter, title in [
    (ax_bs, bs_jmp, "a", "Basic sanitation"),
    (ax_od, od_jmp, "b", "Open defecation"),
]:
    g = _country_priority(df_j)
    comp = g[g["gap"] == COMPOUND].copy()

    x = comp["med_width"].to_numpy()     # country median district PI width
    ypop = comp["pop"].to_numpy()
    colours = [FRAG_COLOUR[bool(f)] for f in comp["is_fragile"]]

    ax.set_yscale("log")
    ax.set_xlim(0, 1.0)
    ax.set_ylim(ypop.min() * 0.5, ypop.max() * 2.4)
    ytop = ax.get_ylim()[1]

    x_med = np.median(x)
    y_med = np.median(ypop)
    ax.fill_between([x_med, 1.0], y_med, ytop, color=PRIORITY_SHADE,
                    alpha=0.14, linewidth=0, zorder=0)
    ax.axvline(x_med, color="#bbbbbb", lw=0.7, ls="--", zorder=1)
    ax.axhline(y_med, color="#bbbbbb", lw=0.7, ls="--", zorder=1)
    ax.annotate("higher priority", ((x_med + 1.0) / 2, ytop),
                xytext=(0, -8), textcoords="offset points",
                fontsize=6, style="italic", color="#9c5a5a",
                ha="center", va="top", zorder=2)

    ax.scatter(x, ypop, s=34, c=colours, edgecolors="#444444",
               linewidths=0.5, zorder=3)

    anns = []
    for xi, yi, name in zip(x, ypop, comp["NAME_0"]):
        right = xi <= 0.72
        a = ax.annotate(
            name, (xi, yi),
            xytext=(4 if right else -4, 0),
            textcoords="offset points", fontsize=5.5,
            va="center", ha="left" if right else "right",
            color="#222222", zorder=4)
        anns.append(a)
    _declutter_labels(fig, anns)

    ax.set_xlabel("Median 90% PI width (uncertainty)", fontsize=7)
    ax.set_ylabel("Population (log scale)", fontsize=7)
    ax.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1, decimals=0))
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(_human_pop))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="both", linewidth=0.3, color="#e2e2e2", zorder=0)
    ax.set_title(f"$\\bf{{{letter}}}$  {title}", fontsize=8, loc="left", pad=4)

fig.legend(handles=_frag_handles, loc="lower center",
           bbox_to_anchor=(0.5, 0.0), ncol=2, fontsize=6,
           frameon=False, handletextpad=0.5, columnspacing=1.8)

fig.subplots_adjust(left=0.12, right=0.965, top=0.94, bottom=0.10)
for ext in ("pdf", "png"):
    out = os.path.join(FIGURE_DIR,
                       f"fig_priority_scatter_uncertainty_population_unweighted.{ext}")
    fig.savefig(out, dpi=DPI, format=ext)
    print(f"  Saved: {out}")
plt.close(fig)

print("\nSection 20 done.")
