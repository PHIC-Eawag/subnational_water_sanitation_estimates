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
