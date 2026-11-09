"""Stage 2 (requirement 2a) main run: validation checks, point comparison,
design-day integration, figures 1-4 and CSV tables in ./outputs."""
import os
import numpy as np
import pandas as pd

from plotstyle import plt, DEVICE_COLORS, BASELINE, INK2
from psychro import (wet_bulb, evaporative_outlet, humidity_ratio, dew_point,
                     p_ws, H_FG)
from model import (Params, devices_for, evaluate, mean_waiting, eps_of,
                   RHO, CP)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUT, exist_ok=True)

P = Params()
DEVS = devices_for(P)
N_REF = mean_waiting(40, 10)          # 40 passengers/h, bus every 10 min -> ~4.2 waiting
V_REF = 1.5                           # m/s wind at 1.1 m outside the shelter

# Representative hot days. PLACEHOLDERS: replace with measured hourly data
# (e.g. NOAA ISD / Meteostat) for the cities finally chosen.
CLIMATES = {
    "Hot-dry (Phoenix-like)": dict(Tmax=43.0, Tmin=31.0, Td=12.0, v=1.5),
    "Hot-humid (Houston-like)": dict(Tmax=36.0, Tmin=26.0, Td=23.0, v=1.5),
}


def lines(label, ok):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}")


# ---------------------------------------------------------------------------
# 0. Validation checks
# ---------------------------------------------------------------------------
def validation():
    print("Validation checks")
    rows = []
    # (a) wet bulb vs. the independent Stull (2011) empirical formula
    import math
    def stull(T, RH):
        return (T * math.atan(0.151977 * (RH + 8.313659) ** 0.5) + math.atan(T + RH)
                - math.atan(RH - 1.676331) + 0.00391838 * RH ** 1.5 * math.atan(0.023101 * RH)
                - 4.686035)
    for T, RH in [(42, 15), (35, 55), (32, 75), (30, 50)]:
        a, b = float(wet_bulb(T, RH)), stull(T, RH)
        rows.append(("wet bulb vs Stull", f"{T}C/{RH}%", round(a, 2), round(b, 2), abs(a - b) < 1.0))
    # (b) energy closure: sensible cooling = latent heat of the evaporated water
    for T, RH in [(42, 15), (35, 55)]:
        Ts, Ws, _ = evaporative_outlet(T, RH, 0.8)
        dW = float(Ws - humidity_ratio(T, RH))
        sens = 1.006 * (T - float(Ts))
        lat = dW * H_FG
        rows.append(("energy closure (kJ/kg air)", f"{T}C/{RH}%", round(sens, 2), round(lat, 2),
                     abs(sens - lat) / sens < 0.05))
    # (c) the fan reproduces its rated 3 C at the reference condition
    d = DEVS[0]
    r = evaluate(d, P.fan_ref_T, P.fan_ref_RH, 0.6, 4, P)
    rows.append(("fan rated effect at reference", "30C/50%", round(float(r["dU"]), 2), 3.0,
                 abs(float(r["dU"]) - 3.0) < 0.05))
    # (d) the fan stops helping above skin temperature in dry heat
    r = evaluate(d, 46, 10, 1.0, 4, P)
    rows.append(("fan dU at 46C/10% (expect <= 0)", "46C/10%", round(float(r["dU"]), 2), 0.0,
                 float(r["dU"]) <= 0))
    # (e) fan break-even temperature in dry air vs physiological evidence:
    # at RH 20% fans stay beneficial up to ~45 C for young adults, ~42 C for the elderly
    Tg = np.linspace(36, 48, 241)
    r = evaluate(d, Tg, 20, 1.0, 4, P)
    T_cross = float(Tg[np.argmax(r["dU"] <= 0)])
    rows.append(("fan break-even T at RH 20% (evidence: elderly ~42, young ~45 C)", "RH 20%", round(T_cross, 1), "42-45",
                 41 <= T_cross <= 45))
    # (f) water use: catalog 15-20 L/h for an 18,000 m3/h unit implies only ~2 C of cooling
    dT_cat = 17.5 / 3600 * H_FG / (RHO * 5.0 * CP)
    rows.append(("air-temp drop implied by catalog 17.5 L/h at 5 m3/s", "catalog", round(dT_cat, 2), "~2",
                 dT_cat < 3))
    # (g) limiting cases of the volume (mixing) model
    from model import volume_mode_zone
    Tz, _, phi, _ = volume_mode_zone(40.0, 0.01, 30.0, 0.014, 1e6, 1.0, 0, P)
    rows.append(("huge supply -> zone = supply temp", "Qs->inf", round(float(Tz), 2), 30.0,
                 abs(float(Tz) - 30.0) < 0.05))
    Tz, _, phi, _ = volume_mode_zone(40.0, 0.01, 30.0, 0.014, 1e-6, 1.0, 0, P)
    rows.append(("no supply -> zone = ambient", "Qs->0", round(float(Tz), 2), 40.0,
                 abs(float(Tz) - 40.0) < 0.05))
    df = pd.DataFrame(rows, columns=["check", "case", "model", "reference", "pass"])
    for _, x in df.iterrows():
        lines(f"{x.check} {x.case}: model {x.model} vs {x.reference}", x["pass"])
    df.to_csv(os.path.join(OUT, "table0_validation.csv"), index=False)
    return df


# ---------------------------------------------------------------------------
# 1. Point comparison table (the direct answer to 2a)
# ---------------------------------------------------------------------------
POINTS = [
    ("Hot-dry afternoon", 42, 15),
    ("Hot-humid afternoon", 35, 55),
    ("Warm, moderate humidity", 30, 50),
    ("Very humid", 32, 75),
]


def point_table():
    rows = []
    for label, T, RH in POINTS:
        for d in DEVS:
            for mode in (["spot", "volume"] if d.kind == "evap" else ["spot"]):
                r = evaluate(d, T, RH, V_REF, N_REF, P, mode)
                rows.append(dict(
                    condition=label, T=T, RH=RH, wet_bulb=round(float(wet_bulb(T, RH)), 1),
                    device=d.name, mode="jet at people" if d.kind == "fan" else
                    ("spot (aim at people)" if mode == "spot" else "volume (cool the shelter)"),
                    power_kW=d.power_kw,
                    T_at_person=round(float(r["T_person"]), 1),
                    RH_at_person=round(float(r["RH_person"]), 0),
                    UTCI_before=round(float(r["U0"]), 1), UTCI_after=round(float(r["U1"]), 1),
                    UTCI_drop=round(float(r["dU"]), 2),
                    relief_weighted=round(float(r["relief"]), 2),
                    people_benefiting=round(float(r["n_ben"]), 2),
                    eta=round(float(r["eta"]), 1),
                    gross_cooling_kW=round(float(r["gross_kw"]), 1),
                    delivered_share=round(float(r["share"]), 2),
                    water_L_per_h=round(float(r["water_lph"]), 1),
                    naive_degC_per_kW=round(d.rated_drop / d.power_kw, 1),
                ))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table1_point_comparison.csv"), index=False)
    return df


# ---------------------------------------------------------------------------
# 2. Design-day integration with two control rules
# ---------------------------------------------------------------------------
HOURS = np.arange(6, 22) + 0.5     # service 06:00-22:00, evaluated mid-hour


def ridership(h):
    lam = np.where((h >= 7) & (h < 9) | (h >= 16) & (h < 19), 60.0, 25.0)
    lam = np.where(h >= 19, 20.0, lam)
    headway = np.where(lam >= 60, 10.0, 15.0)
    return lam, headway


def day_profile(c):
    T = (c["Tmax"] + c["Tmin"]) / 2 + (c["Tmax"] - c["Tmin"]) / 2 * np.cos(2 * np.pi * (HOURS - 15) / 24)
    RH = np.minimum(100 * p_ws(c["Td"]) / p_ws(T), 100)
    lam, hw = ridership(HOURS)
    n = mean_waiting(lam, hw)
    return T, RH, np.full_like(T, c["v"]), n


def design_days():
    rows, hourly = [], {}
    for cname, c in CLIMATES.items():
        T, RH, v, n = day_profile(c)
        hourly[cname] = dict(T=T, RH=RH, n=n, U={})
        for d in DEVS:
            r = evaluate(d, T, RH, v, n, P, "spot")
            hourly[cname]["U"][d.name] = r["U1"]
            hourly[cname]["U0"] = r["U0"]
            p_occ = 1 - np.exp(-n)                   # Poisson: chance someone is waiting
            for rule in ("always on", "smart"):
                if rule == "always on":
                    on = np.ones_like(T)
                    energy = d.power_kw * on
                else:   # on only when it helps, heat stress is at least strong, and someone is there
                    on = ((r["U0"] >= 32) & (r["relief"] > 0)).astype(float)
                    energy = d.power_kw * on * p_occ
                benefit = on * r["n_ben"] * r["relief"]
                hot_before = (n * (r["U0"] >= 38)).sum()
                hot_after = ((n - on * r["n_ben"]) * (r["U0"] >= 38) + on * r["n_ben"] * (r["U1"] >= 38)).sum()
                rows.append(dict(
                    climate=cname, device=d.name, control=rule,
                    hours_on=round(float(on.sum()), 1),
                    energy_kWh=round(float(energy.sum()), 2),
                    water_L=round(float((on * r["water_lph"] * (p_occ if rule == "smart" else 1)).sum()), 0),
                    relief_person_degC_h=round(float(benefit.sum()), 1),
                    eta_day=round(float(benefit.sum() / energy.sum()) if energy.sum() > 0 else np.nan, 1),
                    person_h_very_strong_before=round(float(hot_before), 1),
                    person_h_very_strong_after=round(float(hot_after), 1),
                ))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table2_design_days.csv"), index=False)
    return df, hourly


# ---------------------------------------------------------------------------
# 3. Decision rules distilled from the model
# ---------------------------------------------------------------------------
def decision_rules():
    rows = []
    for T in [36, 38, 40, 42, 44, 46]:
        RH = np.linspace(5, 85, 321)
        ok = dew_point(T, RH) <= 28
        e = [evaluate(d, T, RH, V_REF, N_REF, P, "spot")["eta"] for d in DEVS]
        evap_wins = (np.maximum(e[1], e[2]) > e[0]) & ok
        rh_max = float(RH[evap_wins].max())
        rows.append(dict(rule="fan vs evaporative boundary", T=T, value=round(rh_max, 1),
                         unit="max RH (%) where evaporative beats the fan",
                         wet_bulb_depression=round(float(T - wet_bulb(T, rh_max)), 1)))
    T = CLIMATES["Hot-dry (Phoenix-like)"]["Tmax"]
    RH = float(100 * p_ws(CLIMATES["Hot-dry (Phoenix-like)"]["Td"]) / p_ws(T))
    for n in [1, 2, 4, 6, 8, 10, 12]:
        rB = evaluate(DEVS[1], T, RH, V_REF, n, P)
        rC = evaluate(DEVS[2], T, RH, V_REF, n, P)
        rows.append(dict(rule="B vs C by crowd size at hot-dry peak", T=T, value=n, unit="people waiting",
                         eta_B=round(float(rB["eta"]), 1), eta_C=round(float(rC["eta"]), 1),
                         UTCI_after_B=round(float(rB["U1"]), 1), UTCI_after_C=round(float(rC["U1"]), 1)))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table5_decision_rules.csv"), index=False)
    return df


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
def fig1_climate_dependence():
    T = np.linspace(28, 46, 73)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
    for ax, RH, title in zip(axes, (15, 55), ("Dry air (RH 15%)", "Humid air (RH 55%)")):
        ok = dew_point(T, RH) <= 28
        for d in DEVS:
            r = evaluate(d, T, RH, V_REF, N_REF, P, "spot")
            y = np.where(ok, r["dU"], np.nan)
            ax.plot(T, y, color=DEVICE_COLORS[d.name], label=d.name)
        ax.axhline(0, color=INK2, lw=0.8)
        ax.axvline(35, color=BASELINE, lw=0.8, ls=":")
        ax.text(35.2, 9.3, "skin temp. ~35 °C", color=INK2, fontsize=7)
        ax.set_title(title)
        ax.set_xlabel("Air temperature (°C)")
    axes[0].set_ylabel("UTCI reduction for a covered person (°C)")
    axes[0].set_ylim(-3, 10)
    axes[1].legend(loc="upper left")
    fig.suptitle("Fig. 1  The 'up to' ratings are not constants: benefit depends on climate", x=0.01, ha="left", fontsize=10)
    fig.subplots_adjust(top=0.80, wspace=0.08)
    fig.savefig(os.path.join(OUT, "fig1_climate_dependence.png"))
    plt.close(fig)


def fig2_dilution():
    from model import volume_mode_zone, spot_mode_person
    T, RH = 42.0, 15.0
    d = DEVS[2]
    v = np.linspace(0.0, 4.0, 41)
    Ts, Ws, _ = evaporative_outlet(T, RH, eps_of(d, P))
    W = humidity_ratio(T, RH)
    Tz, _, phi, _ = volume_mode_zone(np.full_like(v, T), W, Ts, Ws, d.airflow, v, 4, P)
    Tp, _, th = spot_mode_person(T, W, Ts, Ws, np.maximum(P.shelter_factor * v, 0.3), d.jet_speed, P)
    fig, ax = plt.subplots(figsize=(4.6, 3.0))
    ax.axhline(T - float(Ts), color=BASELINE, ls="--", lw=1.0)
    ax.text(0.05, T - float(Ts) + 0.3, f"at the outlet: {T - float(Ts):.1f} °C", color=INK2, fontsize=7)
    ax.plot(v, T - Tz, color="#2a78d6", label="Volume mode (cool the whole shelter)")
    ax.plot(v, T - Tp, color="#eb6834", label="Spot mode (aim the jet at people)")
    ax.set_xlabel("Wind speed outside the shelter (m/s)")
    ax.set_ylabel("Air-temperature drop where people stand (°C)")
    ax.set_ylim(0, 18)
    ax.legend(loc="lower left")
    ax.set_title("Fig. 2  Open sides waste cooling: device C at 42 °C / 15%", loc="left")
    fig.savefig(os.path.join(OUT, "fig2_dilution_vs_wind.png"))
    plt.close(fig)


def fig3_winner_map():
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    T, RH = np.meshgrid(np.linspace(28, 46, 145), np.linspace(5, 85, 161))
    valid = dew_point(T, RH) <= 28
    etas, U1s, rel = [], {}, {}
    for d in DEVS:
        r = evaluate(d, T, RH, V_REF, N_REF, P, "spot")
        etas.append(np.where(r["relief"] > 0, r["eta"], -np.inf))
        U1s[d.name] = r["U1"]
        rel[d.name] = r["relief"]
    etas = np.array(etas)
    best = np.argmax(etas, axis=0).astype(float)
    best[~np.isfinite(etas.max(axis=0))] = 3
    best[~valid] = np.nan
    cmap = ListedColormap([DEVICE_COLORS[d.name] for d in DEVS] + ["#d9d8d4"])
    fig, ax = plt.subplots(figsize=(5.4, 3.8))
    ax.pcolormesh(T, RH, best, cmap=cmap, vmin=-0.5, vmax=3.5, shading="auto", alpha=0.85)
    cs = ax.contour(T, RH, np.where(valid, rel["A Fan"], np.nan), levels=[0], colors=INK2, linewidths=1.0, linestyles="--")
    ax.clabel(cs, fmt={0: "fan stops helping"}, fontsize=7)
    cs2 = ax.contour(T, RH, np.where(valid, U1s["C Large evap cooler"], np.nan), levels=[38], colors="#0b0b0b", linewidths=1.2)
    ax.clabel(cs2, fmt={38: "even C leaves UTCI ≥ 38"}, fontsize=7)
    ax.set_xlabel("Air temperature (°C)")
    ax.set_ylabel("Relative humidity (%)")
    ax.grid(False)
    present = set(np.unique(best[np.isfinite(best)]).astype(int))
    handles = [Patch(color=DEVICE_COLORS[d.name], label=f"{d.name} most efficient")
               for i, d in enumerate(DEVS) if i in present]
    ax.legend(handles=handles, loc="upper right", fontsize=7, frameon=True, facecolor="white", edgecolor="none")
    ax.set_title("Fig. 3  Which device gives the most relief per kWh?", loc="left")
    ax.text(28.3, 6.5, "white = dew point > 28 °C (not a real climate)", fontsize=6.5, color=INK2)
    fig.savefig(os.path.join(OUT, "fig3_winner_map.png"))
    plt.close(fig)


def fig4_design_days(hourly):
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0), sharey=True)
    for ax, (cname, h) in zip(axes, hourly.items()):
        for lo, hi, c in [(32, 38, "#fbeee6"), (38, 46, "#f6d9c9"), (46, 60, "#efc2ab")]:
            ax.axhspan(lo, hi, color=c, lw=0, zorder=0)
        ax.plot(HOURS, h["U0"], color=BASELINE, ls="--", label="No cooling (shade only)")
        for d in DEVS:
            ax.plot(HOURS, h["U"][d.name], color=DEVICE_COLORS[d.name], label=d.name)
        ax.set_title(cname)
        ax.set_xlabel("Hour of day")
        ax.set_xticks([6, 9, 12, 15, 18, 21])
    for y, lab in [(35, "strong"), (42, "very strong"), (47.5, "extreme")]:
        axes[0].text(6.1, y, lab, fontsize=6.5, color=INK2, va="center")
    axes[0].set_ylabel("UTCI of a covered person (°C)")
    axes[0].set_ylim(26, 50)
    axes[1].legend(loc="upper left", fontsize=7)
    fig.suptitle("Fig. 4  Design-day heat stress at the bus stop, spot mode", x=0.01, ha="left", fontsize=10)
    fig.subplots_adjust(top=0.80, wspace=0.08)
    fig.savefig(os.path.join(OUT, "fig4_design_days.png"))
    plt.close(fig)


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)
    print(f"Calibrated fan air speed at the person: {DEVS[0].jet_speed:.2f} m/s")
    print(f"Evaporative effectiveness: B {eps_of(DEVS[1], P):.2f}, C {eps_of(DEVS[2], P):.2f}")
    print(f"Mean people waiting (40 pax/h, 10-min headway, CV 0.5): {N_REF:.2f}\n")
    validation()
    t1 = point_table()
    print("\nTable 1 (point comparison)")
    print(t1[["condition", "device", "mode", "T_at_person", "RH_at_person", "UTCI_before", "UTCI_after",
              "relief_weighted", "people_benefiting", "eta", "delivered_share", "water_L_per_h",
              "naive_degC_per_kW"]].to_string(index=False))
    t2, hourly = design_days()
    print("\nTable 2 (design days)")
    print(t2.to_string(index=False))
    print("\nTable 5 (decision rules)")
    print(decision_rules().to_string(index=False))
    fig1_climate_dependence()
    fig2_dilution()
    fig3_winner_map()
    fig4_design_days(hourly)
    print("\nFigures written to", OUT)
