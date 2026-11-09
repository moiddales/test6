"""Shared figure style: light paper figures, thin marks, recessive grid.
Categorical slots follow the validated reference palette order (blue, orange,
aqua), so each device keeps its colour in every figure."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DEVICE_COLORS = {
    "A Fan": "#2a78d6",
    "B Evap cooler": "#eb6834",
    "C Large evap cooler": "#1baf7a",
}
BASELINE = "#8a8984"   # neutral gray for "no cooling"
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e4e3df"

plt.rcParams.update({
    "figure.dpi": 110,
    "savefig.dpi": 220,
    "savefig.bbox": "tight",
    "font.size": 9,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK2,
    "axes.titlesize": 10,
    "axes.titlecolor": INK,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "lines.linewidth": 1.6,
    "legend.frameon": False,
    "legend.fontsize": 8,
})
