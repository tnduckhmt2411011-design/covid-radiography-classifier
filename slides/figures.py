"""Sinh 8 biểu đồ của bộ slide bảo vệ từ CSV/JSON gốc.

Mỗi hàm ghi rõ tệp nguồn trong docstring. Không hàm nào nhận tham số số: giá trị
đọc qua ``slides.data`` tại thời điểm dựng. Hình xuất PNG 200 DPI, nền trùng nền
slide để ghép không thấy khung.

Cỡ chữ: hình ghép vào slide theo tỷ lệ 1:1 (1 px PNG = 1 px khung slide), nên cỡ
matplotlib quy ra pt slide bằng hệ số 2,085. Sàn 18 pt slide ứng với 8,63 pt
matplotlib; mọi hằng cỡ chữ bên dưới đều ≥ 9,5 pt (≥ 19,8 pt slide).

Nguồn của mỗi biểu đồ đã ghi ở dòng chân trang của cùng slide, nên dòng chú thích
trong hình chỉ giữ phần giải thích cách đọc (sai số, mốc nền, màu).
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
TICK = 9.5    # nhãn trục
LABEL = 9.5   # tên trục
VALUE = 10.0  # số ghi trên thanh / trong ô
NOTE = 9.5    # chú thích trong vùng vẽ
CAPTION = 9.5  # dòng chú thích dưới cùng


def _comma(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def _frame(width_px: int, height_px: int, *, left: float, bottom: float = 0.40,
           top: float = 0.97, right: float = 0.12):
    """Khung hình: kích thước tính bằng px của khung slide (ghép 1:1)."""
    fig = plt.figure(figsize=(width_px / DPI, height_px / DPI), dpi=DPI, facecolor=PAPER)
    ax = fig.add_axes((left, bottom, 1 - left - right, top - bottom))
    ax.set_facecolor(PAPER)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(LINE)
        ax.spines[side].set_linewidth(1.0)
    ax.tick_params(colors=INK_SOFT, labelsize=TICK, length=0, pad=6)
    return fig, ax


def _save(fig, name: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    fig.savefig(path, dpi=DPI, facecolor=PAPER)
    plt.close(fig)
    return path


def _caption(fig, text: str) -> None:
    """Dòng chú thích cuối hình: chỉ giải thích cách đọc, không lặp lại nguồn."""
    fig.text(0.012, 0.022, text, ha="left", va="bottom", fontsize=CAPTION, color=INK_SOFT)


def _xlabel(ax, text: str, *, size: float = LABEL) -> None:
    ax.set_xlabel(text, fontsize=size, color=INK_SOFT, labelpad=7)


def _xgrid(ax) -> None:
    ax.xaxis.grid(True, color=LINE, linewidth=0.7, alpha=0.7)
    ax.set_axisbelow(True)


def _comma_axis(ax, digits: int = 2) -> None:
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: _comma(value, digits)))


def _label_after(ax, y, x, text, *, ha: str = "left", dy: float = 0) -> None:
    ax.annotate(
        text,
        xy=(x, y),
        xytext=(8 if ha == "left" else -8, dy),
        textcoords="offset points",
        ha=ha,
        va="center",
        fontsize=VALUE,
        color=INK,
        fontweight="bold",
        annotation_clip=False,
        path_effects=[path_effects.withStroke(linewidth=3.5, foreground=PAPER)],
    )


def _base_lines(ax, baselines, labels) -> None:
    """Vạch mốc nền: giá trị ghi ở dòng chú thích dưới hình."""
    for key in labels:
        ax.axvline(baselines[key], color=AMBER, linestyle=(0, (4, 3)), linewidth=1.6, zorder=2)


def _rows(ax, labels, values, errors, colors, height=0.46):
    return ax.barh(
        labels,
        values,
        height=height,
        color=colors,
        xerr=errors,
        error_kw={"ecolor": INK, "elinewidth": 1.5, "capsize": 5.0, "capthick": 1.5},
        zorder=3,
    )


def _ci_errors(rows):
    return [
        [row["macro_f1"] - row["ci"][0] for row in rows],
        [row["ci"][1] - row["macro_f1"] for row in rows],
    ]


def fig_rq1_ci() -> Path:
    """Nguồn: results/report_rq1/r1_summary.csv, results/b0_majority, results/a0_shortcut."""
    rows = sorted(D.D["rq1"], key=lambda item: item["macro_f1"])
    labels = {
        "hist": "Histogram 64",
        "glcmlbp": "GLCM + LBP 88",
        "hog": "HOG 10.404",
        "ghep": "Ghép 152",
    }
    fig, ax = _frame(736, 270, left=0.30)
    bars = _rows(
        ax,
        [labels[row["key"]] for row in rows],
        [row["macro_f1"] for row in rows],
        _ci_errors(rows),
        [TEAL if row["key"] == "ghep" else TEAL_LIGHT for row in rows],
    )
    for bar, row in zip(bars, rows):
        _label_after(ax, bar.get_y() + bar.get_height() / 2, row["ci"][1], D.fmt(row["macro_f1"]))
    _base_lines(ax, D.D["baselines"], ("b0", "a0"))
    ax.set_xlim(0, 1.05)
    ax.set_ylim(-0.6, 3.6)
    _xlabel(ax, "Macro-F1 validation (3.174 ảnh, 3 seed)")
    _xgrid(ax)
    _comma_axis(ax)
    _caption(fig, "Sai số: CI 95% bootstrap 2.000 lần · vạch cam: B0, A0")
    return _save(fig, "fig_rq1_ci.png")


def fig_rq1_delta() -> Path:
    """Nguồn: results/report_rq1/r1_bootstrap_vs_reference.csv."""
    rows = [row for row in D.D["rq1"] if row["delta"]]
    rows.sort(key=lambda item: item["delta"]["diff"])
    labels = {"glcmlbp": "GLCM + LBP", "hog": "HOG", "ghep": "Ghép"}
    fig, ax = _frame(736, 260, left=0.245)
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
        height=0.42,
    )
    for bar, row in zip(bars, rows):
        delta = row["delta"]["diff"]
        anchor = row["delta"]["ci"][1] if delta >= 0 else row["delta"]["ci"][0]
        _label_after(ax, bar.get_y() + bar.get_height() / 2, anchor, D.fmt_delta(delta),
                     ha="left" if delta >= 0 else "right",
                     dy=0)
    ax.axvline(0, color=INK, linewidth=1.2, zorder=4)
    ax.axvline(0.005, color=INK_SOFT, linestyle=(0, (2, 3)), linewidth=1.2, zorder=2)
    ax.annotate(
        "ngưỡng Δ ≥ 0,005",
        xy=(0.005, 0.015),
        xycoords=("data", "axes fraction"),
        xytext=(2, 0),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=NOTE,
        color=INK_SOFT,
        annotation_clip=False,
    )
    ax.set_xlim(-0.14, 0.135)
    ax.set_ylim(-0.6, 2.6)
    _xlabel(ax, "Chênh macro-F1 so với histogram (CI 95%)")
    _xgrid(ax)
    _comma_axis(ax, 3)
    _caption(fig, "Cam: khoảng tin cậy của hiệu chứa 0")
    return _save(fig, "fig_rq1_delta.png")


def fig_rq2_ci() -> Path:
    """Nguồn: results/report_rq2/r1_summary.csv."""
    rows = sorted(D.D["rq2"], key=lambda item: item["macro_f1"])
    names = {
        "lr": "Logistic Regr.",
        "knn": "k-NN",
        "dt": "Decision Tree",
        "rf": "Random Forest",
        "gb": "Gradient Boost.",
        "svm": "SVM RBF",
    }
    fig, ax = _frame(736, 272, left=0.30)
    bars = _rows(
        ax,
        [names[row["key"]] for row in rows],
        [row["macro_f1"] for row in rows],
        _ci_errors(rows),
        [TEAL if row["key"] == "svm" else TEAL_LIGHT for row in rows],
        height=0.55,
    )
    for bar, row in zip(bars, rows):
        _label_after(ax, bar.get_y() + bar.get_height() / 2, row["ci"][1], D.fmt(row["macro_f1"]))
    rf = next(row for row in D.D["rq2"] if row["key"] == "rf")
    ax.axvline(rf["macro_f1"], color=INK_SOFT, linestyle=(0, (3, 3)), linewidth=1.4, zorder=2)
    ax.set_xlim(0, 1.07)
    ax.set_ylim(-0.6, 5.6)
    _xlabel(ax, "Macro-F1 validation (nhóm ghép, 152 chiều)")
    _xgrid(ax)
    _comma_axis(ax)
    _caption(fig, "SVM tất định, chạy một lần · vạch mờ: Random Forest")
    return _save(fig, "fig_rq2_ci.png")


def fig_rq3_scenarios() -> Path:
    """Nguồn: results/report_rq3/r1_summary.csv."""
    order = ["orig_to_orig", "lung_to_lung", "out_to_out", "orig_to_lung", "orig_to_out"]
    names = {
        "orig_to_orig": "Gốc → gốc",
        "lung_to_lung": "Phổi → phổi",
        "out_to_out": "Ngoài → ngoài",
        "orig_to_lung": "Gốc → phổi",
        "orig_to_out": "Gốc → ngoài",
    }
    scenarios = D.D["rq3"]["scenarios"]
    fig, ax = _frame(736, 270, left=0.28)
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
        height=0.52,
    )
    for bar, key in zip(bars, order):
        _label_after(ax, bar.get_y() + bar.get_height() / 2, scenarios[key]["ci"][1],
                     D.fmt(values[order.index(key)]))
    _base_lines(ax, D.D["baselines"], ("b0", "a0"))
    ax.set_xlim(0, 1.07)
    ax.set_ylim(-0.6, 4.6)
    _xlabel(ax, "Macro-F1 validation (3.174 ảnh)")
    _xgrid(ax)
    _comma_axis(ax)
    _caption(fig, "A → B: huấn luyện A, đánh giá B · vạch cam: B0, A0")
    return _save(fig, "fig_rq3_scenarios.png")


def fig_rq3_perm() -> Path:
    """Nguồn: results/rq3_permutation_importance.csv."""
    modes = D.D["permutation"]
    blocks = ["hist_64", "glcm_60", "lbp_28"]
    labels = {"hist_64": "Histogram 64", "glcm_60": "GLCM 60", "lbp_28": "LBP 28"}
    series = {"lung_only": ("Chỉ phổi", TEAL), "outside_only": ("Ngoài phổi", AMBER)}
    fig, ax = _frame(736, 270, left=0.27, top=0.87)
    height = 0.34
    for offset, (mode, (label, color)) in zip((-height / 2, height / 2), series.items()):
        lookup = {block["block"]: block["importance"] for block in modes[mode]}
        positions = [index + offset for index in range(len(blocks))]
        bars = ax.barh(positions, [lookup[block] for block in blocks], height=height, color=color,
                       label=label, zorder=3)
        for bar, block in zip(bars, blocks):
            value = lookup[block]
            _label_after(ax, bar.get_y() + bar.get_height() / 2, value, D.fmt(value))
    ax.set_yticks(range(len(blocks)), [labels[block] for block in blocks])
    ax.legend(frameon=False, fontsize=NOTE, loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=2,
              handlelength=1.1, columnspacing=1.4)
    ax.set_xlim(0, 0.68)
    ax.set_ylim(-0.55, 2.55)
    _xlabel(ax, "Mức giảm macro-F1 khi xáo trộn khối đặc trưng")
    _xgrid(ax)
    _comma_axis(ax)
    _caption(fig, "10 lần xáo trộn mỗi khối đặc trưng")
    return _save(fig, "fig_rq3_perm.png")


def fig_brightness() -> Path:
    """Nguồn: results/eda/brightness_by_class.csv."""
    order = ["COVID", "Lung_Opacity", "Normal", "Viral Pneumonia"]
    rows = sorted(D.D["brightness"], key=lambda row: order.index(row["label"]))
    fig, ax = _frame(720, 316, left=0.32, right=0.13)
    for index, row in enumerate(rows):
        ax.plot([row["q1"], row["q3"]], [index, index], color=TEAL_LIGHT, linewidth=15,
                solid_capstyle="butt", zorder=2)
        ax.plot([row["mean"], row["mean"]], [index - 0.24, index + 0.24], color=TEAL,
                linewidth=3.0, zorder=3)
        _label_after(ax, index, row["q3"] + 3, D.fmt(row["mean"], 1))
    ax.set_yticks(range(len(rows)), [D.CLASS_VI[row["label"]] for row in rows])
    ax.set_xlim(100, 195)
    ax.set_ylim(-0.6, 3.6)
    _xlabel(ax, "Độ sáng trung bình (0–255)")
    _xgrid(ax)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f}"))
    covid = next(row for row in rows if row["label"] == "COVID")
    _caption(fig, f"Thanh: tứ phân vị · gạch: trung bình · AUC {D.fmt(covid['auc_vs_rest'])}")
    return _save(fig, "fig_brightness.png")


def fig_test_confusion() -> Path:
    """Nguồn: results/final_test/metrics.json."""
    matrix = D.D["test"]["matrix"]
    short = ["COVID", "Lung Op.", "Normal", "Viral Pn."]
    fig = plt.figure(figsize=(608 / DPI, 380 / DPI), dpi=DPI, facecolor=PAPER)
    ax = fig.add_axes((0.24, 0.36, 0.72, 0.58))
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
                fontsize=VALUE,
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
                linewidth=2.6,
            )
        )
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_xticks([i + 0.5 for i in range(4)], short, fontsize=TICK)
    ax.set_yticks([4 - i - 0.5 for i in range(4)], short, fontsize=TICK)
    ax.set_xlabel("Cột: dự đoán · Hàng: nhãn thật", fontsize=LABEL, color=INK_SOFT, labelpad=8)
    ax.tick_params(length=0, colors=INK_SOFT, pad=6)
    for spine in ax.spines.values():
        spine.set_visible(False)
    _caption(fig, "Cam: cặp Normal ↔ Lung Opacity")
    return _save(fig, "fig_test_confusion.png")


def fig_test_gap() -> Path:
    """Nguồn: results/final_test/final_test_report.json (ci95, macro_f1)."""
    test = D.D["test"]
    low, high = D.D["test_ci"]
    fig, ax = _frame(656, 250, left=0.055, bottom=0.40, top=0.74, right=0.02)
    ax.plot([low, high], [0, 0], color=INK, linewidth=2.0, solid_capstyle="round", zorder=3)
    ax.plot([low, low], [-0.13, 0.13], color=INK, linewidth=2.0, zorder=3)
    ax.plot([high, high], [-0.13, 0.13], color=INK, linewidth=2.0, zorder=3)
    ax.scatter([test["macro_f1"]], [0], s=130, color=TEAL, zorder=5)
    ax.annotate(
        f"Test {D.fmt(test['macro_f1'])}\nCI 95% {D.fmt_ci(low, high)}",
        xy=(0.5, 0.0),
        xycoords=("axes fraction", "data"),
        xytext=(0, 10),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=VALUE,
        color=INK,
        linespacing=1.35,
    )
    ax.set_xlim(0.845, 0.915)
    ax.set_ylim(-0.5, 0.5)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    _xlabel(ax, "Macro-F1 trên 3.176 ảnh test")
    _xgrid(ax)
    _comma_axis(ax, 3)
    _caption(fig, "Trục giá trị bắt đầu từ 0,845")
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
