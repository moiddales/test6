"""Stage 2 robustness: one-at-a-time tornado (Fig. 5) and Monte Carlo ranking
by crowd size (Fig. 6) of the efficiency eta for the three bus-stop devices,
at the hottest hour of the two design days."""
import os
from dataclasses import replace
import numpy as np
import pandas as pd

from plotstyle import plt, DEVICE_COLORS, INK2
from model import Params, devices_for, evaluate, mean_waiting, E_WATER
from run_stage2 import CLIMATES, OUT, HOURS, peak, peak_wind, ridership

BASE = Params()
N_BASE = mean_waiting(40, 10)
V_PEAK = {name: peak_wind(name) for name in CLIMATES}   # measured wind at the hottest hour
WEIGHT_SCHEMES = {"linear 1-1-1-1": (1, 1, 1, 1), "base 1-2-3-4": (1, 2, 3, 4), "steep 1-3-9-27": (1, 3, 9, 27)}


CONDS = {name: peak(name) for name in CLIMATES}
WEIGHT_ROW = "Heat-stress weights (1-1-1-1 to 1-3-9-27)"
# Crowd size is a property of the stop, known to the planner, so the Monte
# Carlo reports the ranking at each crowd size instead of drawing it at random.
N_FINE = np.arange(1.0, 16.01, 0.25)      # mean people waiting
N_GRID = (2.0, 4.0, 6.0, 8.0, 10.0, 12.0)
N_DAY = mean_waiting(*ridership(HOURS))   # crowd sizes met on the design day

# name: (low, high, how to apply). Ranges are the plausible spans argued in the plan.
RANGES = {
    "Rating depression D_ref (°C)": (8.5, 13.0, "param", "D_ref"),
    "Fan rating reference T (°C)": (28.0, 33.0, "param", "fan_ref_T"),
    "Airflow per covered person (m³/s)": (0.5, 1.2, "param", "q_per_person"),
    "Jet share at person θ0": (0.5, 0.85, "param", "theta0"),
    "Radiant excess under the roof (°C)": (8.0, 16.0, "param", "dR_shade"),
    "Wind sheltering factor": (0.3, 0.8, "param", "shelter_factor"),
    "Outside wind speed (m/s)": (0.5, 4.5, "wind", None),
    "People waiting": (2.0, 12.0, "people", None),
    "Evap jet speed (× base)": (0.7, 1.3, "jet", None),
    "Water energy intensity (kWh/m³)": (0.0, 2.64, "param", "e_water"),
}


def eta_all(p, v=None, n=N_BASE, jet_scale=1.0):
    """eta at each climate's peak hour (an array when n is an array). Wind
    defaults to the measured peak-hour wind and water energy to the city value
    unless the draw sets them."""
    devs = devices_for(p)
    out = {}
    for cname, (T, RH) in CONDS.items():
        pc = replace(p, e_water=E_WATER[cname]) if p.e_water == BASE.e_water else p
        vc = V_PEAK[cname] if v is None else v
        for d in devs:
            if d.kind == "evap":
                d = replace(d, jet_speed=d.jet_speed * jet_scale)
            out[(cname, d.name)] = evaluate(d, T, RH, vc, n, pc, "spot")["eta"]
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
                             eta_base=round(float(base[key]), 2), eta_at_low=round(float(r_lo[key]), 2),
                             eta_at_high=round(float(r_hi[key]), 2)))
    r_lin = eta_all(replace(BASE, weights=WEIGHT_SCHEMES["linear 1-1-1-1"]))
    r_steep = eta_all(replace(BASE, weights=WEIGHT_SCHEMES["steep 1-3-9-27"]))
    for key in base:
        rows.append(dict(climate=key[0], device=key[1], parameter=WEIGHT_ROW, low="1-1-1-1", high="1-3-9-27",
                         eta_base=round(float(base[key]), 2), eta_at_low=round(float(r_lin[key]), 2),
                         eta_at_high=round(float(r_steep[key]), 2)))
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
    """Draw every uncertain parameter except crowd size; for each draw compute
    eta over the whole crowd-size grid. Returns the share of draws in which each
    device is the most efficient, by climate and crowd size."""
    rng = np.random.default_rng(seed)
    schemes = list(WEIGHT_SCHEMES.values())
    clim, devs = list(CONDS), list(DEVICE_COLORS)
    eta = np.zeros((n_draws, len(clim), len(devs), len(N_FINE)))
    for k in range(n_draws):
        p = BASE
        kw = {}
        for name, (lo, hi, how, field) in RANGES.items():
            if how == "people":
                continue
            x = rng.uniform(lo, hi)
            if how == "param":
                p = replace(p, **{field: x})
            elif how == "wind":
                kw["v"] = x
            else:
                kw["jet_scale"] = x
        p = replace(p, weights=schemes[rng.integers(len(schemes))])
        r = eta_all(p, n=N_FINE, **kw)
        for i, c in enumerate(clim):
            for j, d in enumerate(devs):
                eta[k, i, j] = r[(c, d)]
    valid_sets = np.isfinite(eta).all(axis=2)
    best = np.where(np.isfinite(eta), eta, -np.inf).argmax(axis=2)                                           # draws x climates x crowd sizes
    p_best = np.stack([np.divide(((best == j) & valid_sets).sum(axis=0), valid_sets.sum(axis=0),
                                 out=np.full(valid_sets.shape[1:], np.nan), where=valid_sets.sum(axis=0)>0)
                       for j in range(len(devs))], axis=1)   # climates x devices x crowd sizes
    p_neg = (eta < 0).mean(axis=0)
    rows = []
    for i, c in enumerate(clim):
        for n in N_GRID:
            m = int(np.argmin(abs(N_FINE - n)))
            for j, d in enumerate(devs):
                rows.append(dict(climate=c, people_waiting=n, device=d, share_rank1_given_supported=round(float(p_best[i, j, m]), 3),
                                 supported_draw_fraction=round(float(valid_sets[:,i,m].mean()),3),
                                 share_negative_all_draws=round(float(p_neg[i, j, m]), 3)))
    summary = pd.DataFrame(rows)
    summary.to_csv(os.path.join(OUT, "table4_monte_carlo.csv"), index=False)

    # crowd size from which C is more efficient than B
    rows = []
    iB, iC = devs.index("B Evap cooler"), devs.index("C Large evap cooler")
    for i, c in enumerate(clim):
        ahead = eta[:, i, iC, :] > eta[:, i, iB, :]
        n_star = np.where(ahead.any(axis=1), N_FINE[ahead.argmax(axis=1)], np.inf)
        q = np.quantile(n_star, [0.05, 0.5, 0.95], method="lower")
        rows.append(dict(climate=c, n_star_p05=q[0], n_star_median=q[1], n_star_p95=q[2],
                         share_C_ahead_at_every_crowd=round(float(ahead.all(axis=1).mean()), 3),
                         share_C_never_ahead_up_to_16=round(float((~ahead.any(axis=1)).mean()), 3)))
    cross = pd.DataFrame(rows)
    cross.to_csv(os.path.join(OUT, "table4b_break_even_crowd.csv"), index=False)
    return p_best, summary, cross


def fig6(p_best):
    clim, devs = list(CONDS), list(DEVICE_COLORS)
    fig, axes = plt.subplots(1, len(clim), figsize=(7.6, 3.0), sharey=True)
    for i, (ax, c) in enumerate(zip(axes, clim)):
        ax.axvspan(N_DAY.min(), N_DAY.max(), color="#f0efeb", lw=0, zorder=0)
        ax.text(0.5 * (N_DAY.min() + N_DAY.max()), 103, "design-day\ncrowds", ha="center", va="bottom",
                fontsize=6.5, color=INK2)
        for j, d in enumerate(devs):
            ax.plot(N_FINE, 100 * p_best[i, j], color=DEVICE_COLORS[d], label=d)
        ax.set_title(c, fontsize=9, pad=18)
        ax.set_xlabel("Mean number of people waiting")
        ax.set_xlim(1, 16)
        ax.set_ylim(-2, 102)
    axes[0].set_ylabel("Share of parameter sets in which\nthe device is most efficient (%)")
    axes[1].legend(loc="center right", fontsize=7)
    fig.suptitle("Fig. 6  Monte Carlo: the most efficient device by crowd size (3,000 parameter sets, hottest hour)",
                 x=0.01, ha="left", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(os.path.join(OUT, "fig6_monte_carlo.png"))
    plt.close(fig)


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print("Peak conditions (T, RH, wind):", {k: (round(T, 1), round(RH, 1), V_PEAK[k]) for k, (T, RH) in CONDS.items()})
    t = tornado()
    fig5(t)
    swing = t.assign(swing=(t.eta_at_high - t.eta_at_low).abs()).sort_values("swing", ascending=False)
    print("\nLargest one-at-a-time swings")
    print(swing.groupby(["climate", "device"]).head(3)[["climate", "device", "parameter", "eta_base",
                                                          "eta_at_low", "eta_at_high"]].to_string(index=False))
    p_best, summary, cross = monte_carlo()
    fig6(p_best)
    print(f"\nDesign-day mean crowd: {N_DAY.min():.1f}-{N_DAY.max():.1f} people waiting")
    print("\nMonte Carlo: share of draws in which each device is most efficient, by crowd size")
    print(summary.pivot_table(index=["climate", "people_waiting"], columns="device", values="P_rank1").to_string())
    print("\nFan eta negative (share of draws):")
    print(summary[summary.device == "A Fan"].pivot_table(index="climate", columns="people_waiting", values="P_eta_negative").to_string())
    print("\nCrowd size from which C is more efficient than B")
    print(cross.to_string(index=False))
