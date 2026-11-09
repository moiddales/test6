"""Stage 2 robustness: one-at-a-time tornado (Fig. 5) and Monte Carlo ranking
(Fig. 6) of the efficiency eta for the three bus-stop devices, at the 15:00
peak of the two design days."""
import os
from dataclasses import replace
import numpy as np
import pandas as pd

from plotstyle import plt, DEVICE_COLORS, INK2
from model import Params, devices_for, evaluate, mean_waiting
from run_stage2 import CLIMATES, OUT, peak

BASE = Params()
N_BASE = mean_waiting(40, 10)
V_BASE = 1.5
WEIGHT_SCHEMES = {"linear 1-1-1-1": (1, 1, 1, 1), "base 1-2-3-4": (1, 2, 3, 4), "steep 1-3-9-27": (1, 3, 9, 27)}


CONDS = {name: peak(name) for name in CLIMATES}
WEIGHT_ROW = "Heat-stress weights (1-1-1-1 to 1-3-9-27)"

# name: (low, high, how to apply). Ranges are the plausible spans argued in the plan.
RANGES = {
    "Rating depression D_ref (°C)": (8.5, 13.0, "param", "D_ref"),
    "Fan rating reference T (°C)": (28.0, 33.0, "param", "fan_ref_T"),
    "Airflow per covered person (m³/s)": (0.5, 1.2, "param", "q_per_person"),
    "Jet share at person θ0": (0.5, 0.85, "param", "theta0"),
    "Radiant excess in shade (°C)": (0.0, 10.0, "param", "dR_shade"),
    "Wind sheltering factor": (0.3, 0.8, "param", "shelter_factor"),
    "Outside wind speed (m/s)": (0.5, 3.0, "wind", None),
    "People waiting": (2.0, 12.0, "people", None),
    "Evap jet speed (× base)": (0.7, 1.3, "jet", None),
    "Water energy intensity (kWh/m³)": (0.0, 2.64, "param", "e_water"),
}


def eta_all(p, v=V_BASE, n=N_BASE, jet_scale=1.0):
    devs = devices_for(p)
    out = {}
    for cname, (T, RH) in CONDS.items():
        for d in devs:
            if d.kind == "evap":
                d = replace(d, jet_speed=d.jet_speed * jet_scale)
            out[(cname, d.name)] = float(evaluate(d, T, RH, v, n, p, "spot")["eta"])
    return out


def apply(name, value):
    lo, hi, how, field = RANGES[name]
    kw = dict(p=BASE)
    if how == "param":
        kw["p"] = replace(BASE, **{field: value})
    elif how == "wind":
        kw["v"] = value
    elif how == "people":
        kw["n"] = value
    else:
        kw["jet_scale"] = value
    return eta_all(**kw)


def tornado():
    base = eta_all(BASE)
    rows = []
    for name, (lo, hi, _, _) in RANGES.items():
        r_lo, r_hi = apply(name, lo), apply(name, hi)
        for key in base:
            rows.append(dict(climate=key[0], device=key[1], parameter=name, low=lo, high=hi,
                             eta_base=round(base[key], 2), eta_at_low=round(r_lo[key], 2),
                             eta_at_high=round(r_hi[key], 2)))
    r_lin = eta_all(replace(BASE, weights=WEIGHT_SCHEMES["linear 1-1-1-1"]))
    r_steep = eta_all(replace(BASE, weights=WEIGHT_SCHEMES["steep 1-3-9-27"]))
    for key in base:
        rows.append(dict(climate=key[0], device=key[1], parameter=WEIGHT_ROW, low="1-1-1-1", high="1-3-9-27",
                         eta_base=round(base[key], 2), eta_at_low=round(r_lin[key], 2),
                         eta_at_high=round(r_steep[key], 2)))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table3_sensitivity_oat.csv"), index=False)
    return df


def fig5(df):
    cl = list(CONDS)
    devs = list(DEVICE_COLORS)
    fig, axes = plt.subplots(len(cl), len(devs), figsize=(10.5, 6.2), sharey=True)
    params = list(RANGES) + [WEIGHT_ROW]
    for i, c in enumerate(cl):
        for j, d in enumerate(devs):
            ax = axes[i, j]
            sub = df[(df.climate == c) & (df.device == d) & df.parameter.isin(params)].set_index("parameter").loc[params]
            lo = sub[["eta_at_low", "eta_at_high"]].min(axis=1)
            hi = sub[["eta_at_low", "eta_at_high"]].max(axis=1)
            base = sub.eta_base.iloc[0]
            y = np.arange(len(params))
            ax.barh(y, hi - lo, left=lo, height=0.55, color=DEVICE_COLORS[d])
            ax.axvline(base, color=INK2, lw=0.9)
            ax.axvline(0, color="#b8b7b2", lw=0.7)
            ax.set_yticks(y)
            ax.set_yticklabels(params, fontsize=7)
            ax.invert_yaxis()
            ax.set_title(f"{d}\n{c}", fontsize=8)
            if i == len(cl) - 1:
                ax.set_xlabel("η (person·°C·h per kWh)")
    fig.suptitle("Fig. 5  One-at-a-time sensitivity of η at the 15:00 peak (vertical line = base case)",
                 x=0.01, ha="left", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(OUT, "fig5_tornado.png"))
    plt.close(fig)


def monte_carlo(n_draws=3000, seed=1):
    rng = np.random.default_rng(seed)
    schemes = list(WEIGHT_SCHEMES.values())
    rows = []
    for k in range(n_draws):
        p = BASE
        kw = {}
        for name, (lo, hi, how, field) in RANGES.items():
            x = rng.uniform(lo, hi)
            if how == "param":
                p = replace(p, **{field: x})
            elif how == "wind":
                kw["v"] = x
            elif how == "people":
                kw["n"] = x
            else:
                kw["jet_scale"] = x
        p = replace(p, weights=schemes[rng.integers(len(schemes))])
        r = eta_all(p, **kw)
        for (c, d), e in r.items():
            rows.append(dict(draw=k, climate=c, device=d, eta=e))
    df = pd.DataFrame(rows)
    df["rank"] = df.groupby(["draw", "climate"])["eta"].rank(ascending=False, method="first")
    summary = (df.groupby(["climate", "device"])
                 .agg(P_rank1=("rank", lambda s: (s == 1).mean()),
                      eta_p05=("eta", lambda s: s.quantile(0.05)),
                      eta_median=("eta", "median"),
                      eta_p95=("eta", lambda s: s.quantile(0.95)),
                      P_eta_negative=("eta", lambda s: (s < 0).mean()))
                 .round(3).reset_index())
    summary.to_csv(os.path.join(OUT, "table4_monte_carlo.csv"), index=False)
    return df, summary


def fig6(df):
    cl = list(CONDS)
    devs = list(DEVICE_COLORS)
    fig, axes = plt.subplots(1, len(cl), figsize=(8.2, 3.0))
    for ax, c in zip(axes, cl):
        data = [df[(df.climate == c) & (df.device == d)].eta.values for d in devs]
        bp = ax.boxplot(data, orientation="horizontal", widths=0.5, patch_artist=True, showfliers=False,
                        medianprops=dict(color="#0b0b0b", lw=1.2))
        for patch, d in zip(bp["boxes"], devs):
            patch.set_facecolor(DEVICE_COLORS[d])
            patch.set_edgecolor(DEVICE_COLORS[d])
        p1 = df[df.climate == c].groupby("device")["rank"].apply(lambda s: (s == 1).mean())
        ax.set_yticks(range(1, len(devs) + 1))
        ax.set_yticklabels([f"{d}\nP(most efficient) = {p1[d]:.0%}" for d in devs], fontsize=7)
        ax.axvline(0, color="#b8b7b2", lw=0.7)
        ax.set_title(c, fontsize=9)
        ax.set_xlabel("η (person·°C·h per kWh)")
        ax.invert_yaxis()
    fig.suptitle("Fig. 6  Monte Carlo: η across 3,000 random parameter sets (box = 25–75%, whiskers = 1.5 IQR)",
                 x=0.01, ha="left", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(os.path.join(OUT, "fig6_monte_carlo.png"))
    plt.close(fig)


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print("Peak conditions:", {k: (round(T, 1), round(RH, 1)) for k, (T, RH) in CONDS.items()})
    t = tornado()
    fig5(t)
    swing = t.assign(swing=(t.eta_at_high - t.eta_at_low).abs()).sort_values("swing", ascending=False)
    print("\nLargest one-at-a-time swings")
    print(swing.groupby(["climate", "device"]).head(3)[["climate", "device", "parameter", "eta_base",
                                                          "eta_at_low", "eta_at_high"]].to_string(index=False))
    mc, summary = monte_carlo()
    fig6(mc)
    print("\nMonte Carlo summary")
    print(summary.to_string(index=False))
