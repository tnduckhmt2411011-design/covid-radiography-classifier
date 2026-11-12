"""Sinh 8 biểu đồ của bộ slide bảo vệ từ CSV/JSON gốc.

Mỗi hàm ghi rõ tệp nguồn trong docstring. Không hàm nào nhận tham số số: giá trị
đọc qua ``slides.data`` tại thời điểm dựng. Hình xuất PNG 200 DPI, nền trùng nền
slide để ghép không thấy khung.

Bố cục: nhãn trục ngang nằm trên dòng nguồn; nguồn ở mép dưới; mốc nền ghi ở góc
trên phải để không đè lên thanh hay nhãn trục.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter

import matplotlib.patheffects as path_effects

from . import data as D

OUT_DIR = Path(__file__).resolve().parent / "figures"

PAPER = "#F7F4EE"
INK = "#161D26"
INK_SOFT = "#4A5560"
TEAL = "#0F766E"
TEAL_LIGHT = "#7FBFB6"
AMBER = "#B45309"
LINE = "#D8D2C4"

DPI = 200


def _comma(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def _frame(width_px: int, height_px: int, *, left: float, bottom: float = 0.30, top: float = 0.90):
    fig = plt.figure(figsize=(width_px / DPI, height_px / DPI), dpi=DPI, facecolor=PAPER)
    ax = fig.add_axes((left, bottom, 1 - left - 0.035, top - bottom))
    ax.set_facecolor(PAPER)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(LINE)
        ax.spines[side].set_linewidth(1.0)
    ax.tick_params(colors=INK_SOFT, labelsize=7.2, length=0, pad=5)
    return fig, ax


def _save(fig, name: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    fig.savefig(path, dpi=DPI, facecolor=PAPER)
    plt.close(fig)
    return path


def _caption(fig, text: str) -> None:
    fig.text(0.012, 0.030, text, ha="left", va="bottom", fontsize=6.8, color=INK_SOFT)


def _note(fig, text: str) -> None:
    fig.text(0.985, 0.955, text, ha="right", va="center", fontsize=6.8, color=AMBER)


def _xlabel(ax, text: str, *, size: float = 7.6) -> None:
    ax.set_xlabel(text, fontsize=size, color=INK_SOFT, labelpad=4)


def _xgrid(ax) -> None:
    ax.xaxis.grid(True, color=LINE, linewidth=0.7, alpha=0.7)
    ax.set_axisbelow(True)


def _comma_axis(ax, digits: int = 2) -> None:
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: _comma(value, digits)))


def _label_after(ax, y, x, text, *, ha: str = "left") -> None:
    ax.annotate(
        text,
        xy=(x, y),
        xytext=(7 if ha == "left" else -7, 0),
        textcoords="offset points",
        ha=ha,
        va="center",
        fontsize=8.4,
        color=INK,
        fontweight="bold",
        annotation_clip=False,
        path_effects=[path_effects.withStroke(linewidth=3.0, foreground=PAPER)],
    )


def _baseline(ax, value: float, short: str | None = None) -> None:
    ax.axvline(value, color=AMBER, linestyle=(0, (4, 3)), linewidth=1.4, zorder=2)
    if short is None:
        return
    ax.annotate(
        short,
        xy=(value, 1.012),
        xycoords=("data", "axes fraction"),
        xytext=(2, 0),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=7.0,
        color=AMBER,
        annotation_clip=False,
    )


def _rows(ax, labels, values, errors, colors, height=0.44):
    bars = ax.barh(
        labels,
        values,
        height=height,
        color=colors,
        xerr=errors,
        error_kw={"ecolor": INK, "elinewidth": 1.5, "capsize": 4.5, "capthick": 1.5},
        zorder=3,
    )
    return bars


def fig_rq1_ci() -> Path:
    """Nguồn: results/report_rq1/r1_summary.csv, results/b0_majority, results/a0_shortcut."""
    rows = sorted(D.D["rq1"], key=lambda item: item["macro_f1"])
    labels = {
        "hist": "Histogram (64)",
        "glcmlbp": "GLCM + LBP (88)",
        "hog": "HOG (10.404)",
        "ghep": "Ghép (152)",
    }
    fig, ax = _frame(1000, 372, left=0.205)
    values = [row["macro_f1"] for row in rows]
    errors = [
        [row["macro_f1"] - row["ci"][0] for row in rows],
        [row["ci"][1] - row["macro_f1"] for row in rows],
    ]
    bars = _rows(
        ax,
        [labels[row["key"]] for row in rows],
        values,
        errors,
        [TEAL if row["key"] == "ghep" else TEAL_LIGHT for row in rows],
    )
    for bar, row in zip(bars, rows):
        _label_after(ax, bar.get_y() + bar.get_height() / 2, row["ci"][1], D.fmt(row["macro_f1"]))
    baselines = D.D["baselines"]
    _baseline(ax, baselines["b0"], "B0")
    _baseline(ax, baselines["a0"], "A0")
    _note(fig, f"mốc nền: B0 = {D.fmt(baselines['b0'])} · A0 = {D.fmt(baselines['a0'])}")
    ax.set_xlim(0, 1.0)
    ax.set_ylim(-0.55, 3.55)
    _xlabel(ax, "Macro-F1 trên validation (n = 3.174 ảnh, 3 seed)")
    _xgrid(ax)
    _comma_axis(ax)
    _caption(fig, "Nguồn: results/report_rq1/r1_summary.csv · thanh sai số là CI 95% bootstrap 2.000 lần")
    return _save(fig, "fig_rq1_ci.png")


def fig_rq1_delta() -> Path:
    """Nguồn: results/report_rq1/r1_bootstrap_vs_reference.csv."""
    rows = [row for row in D.D["rq1"] if row["delta"]]
    rows.sort(key=lambda item: item["delta"]["diff"])
    labels = {"glcmlbp": "GLCM + LBP", "hog": "HOG", "ghep": "Ghép"}
    fig, ax = _frame(1000, 330, left=0.145)
    values = [row["delta"]["diff"] for row in rows]
    errors = [
        [row["delta"]["diff"] - row["delta"]["ci"][0] for row in rows],
        [row["delta"]["ci"][1] - row["delta"]["diff"] for row in rows],
    ]
    bars = _rows(
        ax,
        [labels[row["key"]] for row in rows],
        values,
        errors,
        [AMBER if row["delta"]["contains_zero"] else TEAL for row in rows],
        height=0.38,
    )
    for bar, row in zip(bars, rows):
        delta = row["delta"]["diff"]
        anchor = row["delta"]["ci"][1] if delta >= 0 else row["delta"]["ci"][0]
        _label_after(
            ax,
            bar.get_y() + bar.get_height() / 2,
            anchor,
            D.fmt_delta(delta),
            ha="left" if delta >= 0 else "right",
        )
    ax.axvline(0, color=INK, linewidth=1.0, zorder=4)
    ax.axvline(0.005, color=INK_SOFT, linestyle=(0, (2, 3)), linewidth=1.0, zorder=2)
    ax.annotate(
        "ngưỡng Δ ≥ 0,005",
        xy=(0.005, 1.012),
        xycoords=("data", "axes fraction"),
        xytext=(2, 0),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=7.0,
        color=INK_SOFT,
        annotation_clip=False,
    )
    ax.set_xlim(-0.075, 0.125)
    _xlabel(ax, "Chênh lệch macro-F1 so với histogram (CI 95%)")
    _xgrid(ax)
    _comma_axis(ax, 2)
    _caption(fig, "Nguồn: results/report_rq1/r1_bootstrap_vs_reference.csv · cam = khoảng tin cậy chứa 0")
    return _save(fig, "fig_rq1_delta.png")


def fig_rq2_ci() -> Path:
    """Nguồn: results/report_rq2/r1_summary.csv."""
    rows = sorted(D.D["rq2"], key=lambda item: item["macro_f1"])
    names = {
        "lr": "Logistic Regression",
        "knn": "k-NN",
        "dt": "Decision Tree",
        "rf": "Random Forest",
        "gb": "Gradient Boosting",
        "svm": "SVM RBF",
    }
    fig, ax = _frame(1000, 372, left=0.215)
    values = [row["macro_f1"] for row in rows]
    errors = [
        [row["macro_f1"] - row["ci"][0] for row in rows],
        [row["ci"][1] - row["macro_f1"] for row in rows],
    ]
    bars = _rows(
        ax,
        [names[row["key"]] for row in rows],
        values,
        errors,
        [TEAL if row["key"] == "svm" else TEAL_LIGHT for row in rows],
    )
    for bar, row in zip(bars, rows):
        _label_after(ax, bar.get_y() + bar.get_height() / 2, row["ci"][1], D.fmt(row["macro_f1"]))
    rf = next(row for row in D.D["rq2"] if row["key"] == "rf")
    _baseline(ax, rf["macro_f1"])
    _note(fig, f"mốc nền: RF = {D.fmt(rf['macro_f1'])}")
    ax.set_xlim(0, 1.08)
    ax.set_ylim(-0.55, 5.55)
    _xlabel(ax, "Macro-F1 trên validation (nhóm đặc trưng ghép, 152 chiều)")
    _xgrid(ax)
    _comma_axis(ax)
    _caption(fig, "Nguồn: results/report_rq2/r1_summary.csv · SVM là mô hình tất định, chạy một lần")
    return _save(fig, "fig_rq2_ci.png")


def fig_rq3_scenarios() -> Path:
    """Nguồn: results/report_rq3/r1_summary.csv."""
    order = ["orig_to_orig", "lung_to_lung", "out_to_out", "orig_to_lung", "orig_to_out"]
    names = {
        "orig_to_orig": "Gốc → gốc",
        "lung_to_lung": "Chỉ phổi → chỉ phổi",
        "out_to_out": "Ngoài phổi → ngoài phổi",
        "orig_to_lung": "Gốc → chỉ phổi",
        "orig_to_out": "Gốc → ngoài phổi",
    }
    scenarios = D.D["rq3"]["scenarios"]
    fig, ax = _frame(1000, 380, left=0.265)
    values = [scenarios[key]["macro_f1"] for key in order]
    errors = [
        [scenarios[key]["macro_f1"] - scenarios[key]["ci"][0] for key in order],
        [scenarios[key]["ci"][1] - scenarios[key]["macro_f1"] for key in order],
    ]
    highlight = {"orig_to_orig": TEAL, "lung_to_lung": TEAL_LIGHT, "out_to_out": TEAL_LIGHT}
    bars = _rows(
        ax,
        [names[key] for key in order],
        values,
        errors,
        [highlight.get(key, TEAL_LIGHT) for key in order],
    )
    for bar, key in zip(bars, order):
        _label_after(ax, bar.get_y() + bar.get_height() / 2, scenarios[key]["ci"][1], D.fmt(values[order.index(key)]))
    baselines = D.D["baselines"]
    ax.set_xlim(0, 1.08)
    ax.set_ylim(-0.55, 4.55)
    _xlabel(ax, "Macro-F1 trên validation (n = 3.174 ảnh)")
    _xgrid(ax)
    _comma_axis(ax)
    _caption(
        fig,
        "Nguồn: results/report_rq3/r1_summary.csv · mốc nền "
        f"B0 = {D.fmt(baselines['b0'])} · A0 = {D.fmt(baselines['a0'])}",
    )
    return _save(fig, "fig_rq3_scenarios.png")


def fig_rq3_perm() -> Path:
    """Nguồn: results/rq3_permutation_importance.csv."""
    modes = D.D["permutation"]
    blocks = ["hist_64", "glcm_60", "lbp_28"]
    labels = {"hist_64": "Histogram (64)", "glcm_60": "GLCM (60)", "lbp_28": "LBP (28)"}
    series = {"lung_only": ("Chỉ phổi", TEAL), "outside_only": ("Ngoài phổi", AMBER)}
    fig, ax = _frame(1000, 340, left=0.175, bottom=0.30, top=0.86)
    height = 0.34
    top = 0.0
    for offset, (mode, (label, color)) in zip((-height / 2, height / 2), series.items()):
        lookup = {block["block"]: block["importance"] for block in modes[mode]}
        positions = [index + offset for index in range(len(blocks))]
        bars = ax.barh(positions, [lookup[block] for block in blocks], height=height, color=color, label=label, zorder=3)
        for bar, block in zip(bars, blocks):
            value = lookup[block]
            top = max(top, value)
            _label_after(ax, bar.get_y() + bar.get_height() / 2, value, D.fmt(value))
    ax.set_yticks(range(len(blocks)), [labels[block] for block in blocks])
    ax.legend(frameon=False, fontsize=7.4, loc="upper center", bbox_to_anchor=(0.5, 1.20), ncol=2, handlelength=1.2)
    ax.set_xlim(0, 0.62)
    _xlabel(ax, "Mức giảm macro-F1 khi xáo trộn khối đặc trưng")
    _xgrid(ax)
    _comma_axis(ax)
    _caption(fig, "Nguồn: results/rq3_permutation_importance.csv · 10 lần xáo trộn mỗi khối")
    return _save(fig, "fig_rq3_perm.png")


def fig_brightness() -> Path:
    """Nguồn: results/eda/brightness_by_class.csv."""
    order = ["COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"]
    rows = sorted(D.D["brightness"], key=lambda row: order.index(row["label"]))
    fig, ax = _frame(820, 360, left=0.25, bottom=0.32)
    for index, row in enumerate(rows):
        ax.plot([row["q1"], row["q3"]], [index, index], color=TEAL_LIGHT, linewidth=11, solid_capstyle="butt", zorder=2)
        ax.plot([row["mean"], row["mean"]], [index - 0.22, index + 0.22], color=TEAL, linewidth=2.4, zorder=3)
        _label_after(ax, index, row["q3"] + 2, D.fmt(row["mean"], 1))
    ax.set_yticks(range(len(rows)), [D.CLASS_VI[row["label"]] for row in rows])
    ax.set_xlim(100, 182)
    ax.set_ylim(-0.6, 3.6)
    _xlabel(ax, "Độ sáng trung bình (0–255)", size=7.4)
    _xgrid(ax)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f}"))
    covid = next(row for row in rows if row["label"] == "COVID")
    _caption(fig, f"Nguồn: results/eda/brightness_by_class.csv · AUC COVID/nền {D.fmt(covid['auc_vs_rest'])}")
    return _save(fig, "fig_brightness.png")


def fig_test_confusion() -> Path:
    """Nguồn: results/final_test/metrics.json."""
    matrix = D.D["test"]["matrix"]
    short = ["COVID", "Lung Op.", "Normal", "Viral Pn."]
    fig = plt.figure(figsize=(700 / DPI, 470 / DPI), dpi=DPI, facecolor=PAPER)
    ax = fig.add_axes((0.21, 0.315, 0.76, 0.60))
    ax.set_facecolor(PAPER)
    peak = max(max(row) for row in matrix)
    for row_index, row in enumerate(matrix):
        for col_index, value in enumerate(row):
            share = value / peak
            diagonal = row_index == col_index
            ax.add_patch(
                Rectangle(
                    (col_index, len(matrix) - 1 - row_index),
                    1,
                    1,
                    facecolor=TEAL if diagonal else "#E4DACB",
                    alpha=(0.22 + 0.62 * share) if diagonal else (0.18 + 0.62 * share),
                    edgecolor=PAPER,
                    linewidth=2,
                )
            )
            ax.text(
                col_index + 0.5,
                len(matrix) - 1 - row_index + 0.5,
                f"{value:,}".replace(",", "."),
                ha="center",
                va="center",
                fontsize=8.8,
                color=INK,
                fontweight="bold",
            )
    for (row_index, col_index) in ((1, 2), (2, 1)):
        ax.add_patch(
            Rectangle(
                (col_index, len(matrix) - 1 - row_index),
                1,
                1,
                facecolor="none",
                edgecolor=AMBER,
                linewidth=2.4,
            )
        )
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_xticks([i + 0.5 for i in range(4)], short, fontsize=7.4)
    ax.set_yticks([4 - i - 0.5 for i in range(4)], short, fontsize=7.4)
    ax.set_xlabel("Cột: nhãn dự đoán · Hàng: nhãn thật", fontsize=7.6, color=INK_SOFT, labelpad=6)
    ax.tick_params(length=0, colors=INK_SOFT)
    for spine in ax.spines.values():
        spine.set_visible(False)
    _caption(fig, "Nguồn: results/final_test/metrics.json · cam: Normal ↔ Lung Opacity")
    return _save(fig, "fig_test_confusion.png")


def fig_test_gap() -> Path:
    """Nguồn: results/final_test/final_test_report.json (ci95, macro_f1)."""
    test = D.D["test"]
    low, high = D.D["test_ci"]
    fig, ax = _frame(900, 310, left=0.045, bottom=0.38, top=0.82)
    ax.plot([low, high], [0, 0], color=INK, linewidth=1.8, solid_capstyle="round", zorder=3)
    ax.plot([low, low], [-0.13, 0.13], color=INK, linewidth=1.8, zorder=3)
    ax.plot([high, high], [-0.13, 0.13], color=INK, linewidth=1.8, zorder=3)
    ax.scatter([test["macro_f1"]], [0], s=110, color=TEAL, zorder=5)
    ax.annotate(
        f"Test {D.fmt(test['macro_f1'])}  ·  CI 95% {D.fmt_ci(low, high)}",
        xy=((low + high) / 2, 0),
        xytext=(0, 26),
        textcoords="offset points",
        ha="center",
        fontsize=8.8,
        color=INK,
    )
    ax.set_xlim(0.845, 0.915)
    ax.set_ylim(-0.5, 0.5)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    _xlabel(ax, "Macro-F1 trên 3.176 ảnh test", size=7.8)
    _xgrid(ax)
    _comma_axis(ax, 3)
    _caption(fig, "Nguồn: results/final_test/final_test_report.json · trục giá trị bắt đầu từ 0,845")
    return _save(fig, "fig_test_gap.png")


BUILDERS = {
    "fig_rq1_ci.png": fig_rq1_ci,
    "fig_rq1_delta.png": fig_rq1_delta,
    "fig_rq2_ci.png": fig_rq2_ci,
    "fig_rq3_scenarios.png": fig_rq3_scenarios,
    "fig_rq3_perm.png": fig_rq3_perm,
    "fig_brightness.png": fig_brightness,
    "fig_test_confusion.png": fig_test_confusion,
    "fig_test_gap.png": fig_test_gap,
}


def build_all() -> list[Path]:
    return [builder() for builder in BUILDERS.values()]


if __name__ == "__main__":
    for path in build_all():
        print(path)
