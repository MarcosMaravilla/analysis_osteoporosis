import os
from pathlib import Path

try:
    PROJECT_DIR = Path(__file__).resolve().parents[1]
except NameError:
    PROJECT_DIR = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_DIR / ".cache" / "matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FixedLocator, FuncFormatter


OUTPUTS_DIR = PROJECT_DIR / "outputs"
DATA_PATH = PROJECT_DIR / "data" / "processed" / "BD_Clean_Osteoporosis.parquet"


def main():
    OUTPUTS_DIR.mkdir(exist_ok=True)

    df = pd.read_parquet(DATA_PATH)
    bins = [49, 59, 69, 200]
    age_groups = ["50-59", "60-69", "70+"]
    df["age_group"] = pd.cut(df["edad"], bins=bins, labels=age_groups)
    df["sex_label"] = df["sexo"].map({0: "Hombres", 1: "Mujeres"})

    summary = (
        df.groupby(["age_group", "sex_label"], observed=True)
        .agg(
            n_total=("alteracion_osea", "count"),
            n_alteration=("alteracion_osea", "sum"),
        )
        .reset_index()
    )
    summary["pct_alteration"] = (
        summary["n_alteration"] / summary["n_total"] * 100
    )
    total_prev = df["alteracion_osea"].mean() * 100

    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "font.family": "DejaVu Sans",
            "axes.labelcolor": "#222222",
            "xtick.color": "#222222",
            "ytick.color": "#222222",
            "text.color": "#222222",
        }
    )

    colors = {
        "Hombres": "#78A9CF",
        "Mujeres": "#0756B5",
    }
    sexes = ["Hombres", "Mujeres"]
    x = np.arange(len(age_groups))
    bar_width = 0.34

    fig, ax = plt.subplots(figsize=(8.4, 5.4), dpi=300)
    fig.subplots_adjust(left=0.105, right=0.88, top=0.84, bottom=0.17)

    for i, sex in enumerate(sexes):
        subset = summary[summary["sex_label"] == sex].set_index("age_group")
        pct = [subset.loc[age_group, "pct_alteration"] for age_group in age_groups]
        n_vals = [subset.loc[age_group, "n_total"] for age_group in age_groups]
        offset = (i - 0.5) * bar_width

        bars = ax.bar(
            x + offset,
            pct,
            width=bar_width,
            color=colors[sex],
            edgecolor="white",
            linewidth=0.8,
            label=sex,
            zorder=3,
        )

        for bar, pct_val, n_val in zip(bars, pct, n_vals):
            caution = "†" if n_val < 20 else ""
            high_bar = pct_val >= 94
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                pct_val - 3.2 if high_bar else pct_val + 1.3,
                f"{pct_val:.1f}%{caution}",
                ha="center",
                va="top" if high_bar else "bottom",
                fontsize=8.5,
                fontfamily="DejaVu Sans",
                fontweight="semibold",
                color="white" if high_bar else colors[sex],
                clip_on=False,
                zorder=4,
            )

    ax.axhline(
        total_prev,
        color="#1F2933",
        linestyle="-",
        linewidth=1.0,
        alpha=0.9,
        zorder=2,
    )
    ax.text(
        1.008,
        total_prev + 1.0,
        f"Overall: {total_prev:.1f}%",
        transform=ax.get_yaxis_transform(),
        ha="left",
        va="bottom",
        fontsize=8.5,
        fontfamily="DejaVu Sans",
        color="#1F2933",
        clip_on=False,
    )

    ax.set_xlim(-0.55, len(age_groups) - 0.45)
    ax.set_ylim(0, 100)
    ax.set_xticks(x)
    ax.set_xticklabels(age_groups, fontsize=10, fontfamily="DejaVu Sans")
    ax.set_xlabel("Grupo de edad", fontsize=10, fontfamily="DejaVu Sans", labelpad=9)
    ax.set_ylabel(
        "Prevalencia de alteración ósea (%)",
        fontsize=10,
        fontfamily="DejaVu Sans",
        labelpad=9,
    )
    ax.yaxis.set_major_locator(FixedLocator([0, 20, 40, 60, 80, 100]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda val, _: f"{val:.0f}%"))

    ax.legend(
        loc="upper left",
        bbox_to_anchor=(0.012, 0.988),
        borderaxespad=0,
        frameon=False,
        fontsize=9,
        handlelength=1.2,
        handleheight=0.8,
        labelspacing=0.45,
    )

    ax.tick_params(axis="both", which="major", length=0, pad=6)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#D7DCE2", linestyle="-", linewidth=0.7)
    ax.xaxis.grid(False)

    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#222222")
    ax.spines["bottom"].set_linewidth(0.8)

    fig.suptitle(
        "Figure 4. Prevalence of Bone Alteration by Age Group and Sex",
        x=0.5,
        y=0.935,
        ha="center",
        fontsize=14,
        fontfamily="DejaVu Serif",
        fontweight="normal",
    )
    fig.text(
        0.105,
        0.055,
        "† Interpret with caution: n < 20",
        ha="left",
        va="center",
        fontsize=8.2,
        fontfamily="DejaVu Sans",
        color="#4B5563",
    )

    for ext, dpi in [("pdf", 300), ("png", 600)]:
        fig.savefig(
            OUTPUTS_DIR / f"figure4_prevalence_age_sex.{ext}",
            bbox_inches="tight",
            dpi=dpi,
            facecolor="white",
        )
    plt.close(fig)


if __name__ == "__main__":
    main()
