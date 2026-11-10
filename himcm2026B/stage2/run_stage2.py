"""Stage 2 (requirement 2a) main run: validation checks, point comparison,
design-day integration, figures 1-4 and CSV tables in ./outputs."""
import os
from dataclasses import replace
import numpy as np
import pandas as pd

from plotstyle import plt, DEVICE_COLORS, BASELINE, INK2
from psychro import (wet_bulb, evaporative_outlet, humidity_ratio, dew_point,
                     p_ws, H_FG)
from model import (Params, devices_for, evaluate, mean_waiting, eps_of, shade_relief,
                   utci, stress_dose, E_WATER, RHO, CP)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUT, exist_ok=True)

P = Params()
DEVS = devices_for(P)
N_REF = mean_waiting(40, 10)          # 40 passengers/h, bus every 10 min -> ~4.2 waiting
V_REF = 1.5                           # m/s wind at 1.1 m outside the shelter

# Measured design days: hour-by-hour means of the hottest 10 % of July days,
# 2020-2024, ASOS airport observations (data/weather/hot_days.py).
WEATHER_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "weather", "july_profiles.csv")
_prof = pd.read_csv(WEATHER_CSV)
_prof = _prof[_prof.profile == "July hot days (top 10%)"]
CLIMATES = {name: g.sort_values("hour") for name, g in _prof.groupby("climate", sort=False)}
OBS_MINUTE = 52 / 60      # routine METARs are taken at about hh:51-hh:53


def weather(climate, hour):
    """Outdoor air temperature, RH and pedestrian-height wind at local clock
    time `hour` (periodic linear interpolation of the measured profile)."""
    g = CLIMATES[climate]
    x = np.r_[g.hour.values + OBS_MINUTE, g.hour.values[0] + OBS_MINUTE + 24]
    h = np.mod(np.asarray(hour, float) - x[0], 24) + x[0]
    T = np.interp(h, x, np.r_[g["T"].values, g["T"].values[0]])
    Td = np.interp(h, x, np.r_[g.Td.values, g.Td.values[0]])
    v = np.interp(h, x, np.r_[g.v_ped.values, g.v_ped.values[0]])
    return T, np.minimum(100 * p_ws(Td) / p_ws(T), 100), v


def peak(climate):
    """Air temperature and RH at the hottest measured hour of the design day."""
    g = CLIMATES[climate]
    k = g["T"].idxmax()
    return float(g["T"][k]), float(100 * p_ws(g.Td[k]) / p_ws(g["T"][k]))


def peak_wind(climate):
    """Measured pedestrian-height wind at the hottest hour of the design day."""
    g = CLIMATES[climate]
    return float(g.v_ped[g["T"].idxmax()])


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
    # (e) fan effect vs resting-subject trials: Morris et al. 2019 (fans helped at
    # 40 C / 50 % RH, harmed at 47 C / 10 % RH); Ravanelli et al. 2015 (fans helped
    # up to 50 % RH at 42 C)
    for T, RH, helps, src in ((40, 50, True, "Morris 2019"), (47, 10, False, "Morris 2019"),
                              (42, 50, True, "Ravanelli 2015")):
        dU = float(evaluate(d, T, RH, 1.0, 4, P)["dU"])
        rows.append((f"fan {'helps' if helps else 'harms'} at {T} C / {RH} % ({src})", f"{T}C/{RH}%",
                     round(dU, 2), "> 0" if helps else "< 0", (dU > 0) == helps))
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
                    resource_kW=round(float(r["resource_kw"]), 3),
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


def day_profile(climate):
    T, RH, v = weather(climate, HOURS)
    lam, hw = ridership(HOURS)
    n = mean_waiting(lam, hw)
    return T, RH, v, n


def design_days(p=P, tag="table2_design_days"):
    devs = devices_for(p)
    rows, hourly = [], {}
    for cname in CLIMATES:
        T, RH, v, n = day_profile(cname)
        pc = replace(p, e_water=E_WATER[cname])
        hourly[cname] = dict(T=T, RH=RH, n=n, U={})
        for d in devs:
            r = evaluate(d, T, RH, v, n, pc, "spot")
            hourly[cname]["U"][d.name] = r["U1"]
            hourly[cname]["U0"] = r["U0"]
            p_occ = 1 - np.exp(-n)                   # Poisson: chance someone is waiting
            for rule in ("always on", "smart"):
                if rule == "always on":
                    on = np.ones_like(T)
                    run = on
                else:   # on only when it helps, heat stress is at least strong, and someone is there
                    on = ((r["U0"] >= 32) & (r["relief"] > 0)).astype(float)
                    run = on * p_occ
                energy = d.power_kw * run
                resource = r["resource_kw"] * run
                benefit = on * r["n_ben"] * r["relief"]
                made = (r["gross_kw"] * run).sum()
                hot_before = (n * (r["U0"] >= 38)).sum()
                hot_after = ((n - on * r["n_ben"]) * (r["U0"] >= 38) + on * r["n_ben"] * (r["U1"] >= 38)).sum()
                rows.append(dict(
                    climate=cname, device=d.name, control=rule,
                    hours_on=round(float(on.sum()), 1),
                    energy_kWh=round(float(energy.sum()), 2),
                    water_L=round(float((r["water_lph"] * run).sum()), 0),
                    resource_kWh=round(float(resource.sum()), 2),
                    relief_person_degC_h=round(float(benefit.sum()), 1),
                    eta_day=round(float(benefit.sum() / resource.sum()), 1),
                    cooling_made_kWh=round(float(made), 1),
                    share_delivered=round(float((r["gross_kw"] * run * r["fate_delivered"]).sum() / made), 3) if made > 0 else np.nan,
                    share_diluted=round(float((r["gross_kw"] * run * r["fate_diluted"]).sum() / made), 3) if made > 0 else np.nan,
                    share_unused=round(float((r["gross_kw"] * run * r["fate_unused"]).sum() / made), 3) if made > 0 else np.nan,
                    person_h_very_strong_before=round(float(hot_before), 1),
                    person_h_very_strong_after=round(float(hot_after), 1),
                ))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, f"{tag}.csv"), index=False)
    return df, hourly


# ---------------------------------------------------------------------------
# 2b. Zero-energy design levers (the bus stop's "doors and night covers")
# ---------------------------------------------------------------------------
def design_levers(t2):
    """Zero-energy levers. Every relief figure is measured against the same
    baseline: open shelter (no screens), no device. Screens change the
    felt temperature of everybody waiting, so their own effect is counted."""
    rows = []
    ps = replace(P, shelter_factor=0.25)
    screens, _ = design_days(ps, "table6b_wind_screens")
    for cname in CLIMATES:
        T, RH, v, n = day_profile(cname)
        _, _, rel = shade_relief(T, RH, v, HOURS, P)
        rows.append(dict(climate=cname, lever="Shelter roof (shade vs full sun)", device="none",
                         energy_kWh=0.0, relief_person_degC_h=round(float((n * rel).sum()), 1)))
        U_open = utci(T, T + P.dR_shade, np.maximum(P.shelter_factor * v, 0.3), RH)
        U_scr = utci(T, T + P.dR_shade, np.maximum(ps.shelter_factor * v, 0.3), RH)
        alone = float((n * (stress_dose(U_open, P.weights) - stress_dose(U_scr, P.weights))).sum())
        rows.append(dict(climate=cname, lever="Side wind screens alone (inside wind halved)", device="none",
                         energy_kWh=0.0, relief_person_degC_h=round(alone, 1)))
        for _, b in t2[(t2.climate == cname) & (t2.control == "smart")].iterrows():
            sc = screens[(screens.climate == cname) & (screens.device == b.device)
                         & (screens.control == "smart")].iloc[0]
            total = alone + sc.relief_person_degC_h
            rows.append(dict(climate=cname, lever="Side wind screens + device", device=b.device,
                             energy_kWh=sc.energy_kWh, relief_person_degC_h=round(total, 1),
                             relief_device_alone=b.relief_person_degC_h,
                             net_gain_from_screens=round(total - b.relief_person_degC_h, 1),
                             eta_day_without=b.eta_day,
                             eta_day_with=round(total / sc.resource_kWh, 1)))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table6_design_levers.csv"), index=False)
    return df


# ---------------------------------------------------------------------------
# 2c. Fans above skin temperature: model vs the physiological literature
# ---------------------------------------------------------------------------
def fan_evidence(t2):
    """Compare the fan's help/harm boundary with three studies, and show what
    the design-day result becomes under the most pessimistic reading (no fan
    benefit above 35 C air, Meade et al. 2024)."""
    d = DEVS[0]
    rows = []
    RH = np.linspace(2, 95, 931)
    for T in (38.0, 40.0, 42.0, 44.0):
        dU = evaluate(d, T, RH, 1.0, 4, P)["dU"]
        rh0 = float(RH[dU > 0].min()) if (dU > 0).any() else np.nan
        rows.append(dict(item="fan break-even", T=T, model_RH_pct=round(rh0, 1),
                         model_vapour_kPa=round(rh0 / 100 * float(p_ws(T)) / 1000, 2)))
    Ts = np.arange(35.0, 48.01, 0.1)
    harm = Ts[evaluate(d, Ts, 5.0, 1.0, 4, P)["dU"] < 0]
    rows.append(dict(item="lowest air temperature at which the fan harms (RH 5 %)",
                     T=round(float(harm.min()), 1) if len(harm) else np.nan,
                     reference="Morris et al. 2021: never harmful below 39 C (young), 38 C (older), 37 C (older on anticholinergics)"))
    rows.append(dict(item="vapour pressure above which wind helps at 40 C", T=40.0,
                     model_vapour_kPa=rows[1]["model_vapour_kPa"],
                     reference="Broede & Kampmann 2023, moderate exercise: 2 kPa (heart rate, core T), 3 kPa (skin T, sweat)"))
    # design-day consequence under the Meade et al. 2024 reading
    for cname in CLIMATES:
        T, RH_, v, n = day_profile(cname)
        r = evaluate(d, T, RH_, v, n, P, "spot")
        base = t2[(t2.climate == cname) & (t2.device == d.name) & (t2.control == "smart")].iloc[0]
        rel = np.where(T > 35, np.minimum(r["relief"], 0), r["relief"])
        on = ((r["U0"] >= 32) & (rel > 0)).astype(float)
        run = on * (1 - np.exp(-n))
        hot_after = ((n - on * r["n_ben"]) * (r["U0"] >= 38) + on * r["n_ben"] * (r["U1"] >= 38)).sum()
        rows.append(dict(item="design day, smart fan: model", climate=cname, hours_on=base.hours_on,
                         relief_person_degC_h=base.relief_person_degC_h, eta_day=base.eta_day,
                         person_h_very_strong_after=base.person_h_very_strong_after))
        rows.append(dict(item="design day, smart fan: no benefit above 35 C (Meade et al. 2024)", climate=cname,
                         hours_on=float(on.sum()), relief_person_degC_h=round(float((on * r["n_ben"] * rel).sum()), 1),
                         eta_day=round(float((on * r["n_ben"] * rel).sum() / max((r["resource_kw"] * run).sum(), 1e-9)), 1),
                         person_h_very_strong_after=round(float(hot_after), 1)))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table7_fan_evidence.csv"), index=False)
    return df


def rating_reading():
    """Second reading of the problem's ratings ("Effect on Shelter"): the
    air-temperature drop delivered to a covered person at the hottest dry hour.
    Returns the saturation effectiveness that reading implies, and the drop the
    model delivers with its own effectiveness."""
    hd = "Hot-dry (Phoenix-like)"
    T, RH = peak(hd)
    v = peak_wind(hd)
    dep = T - float(wet_bulb(T, RH))
    rows = []
    for d in DEVS[1:]:
        r = evaluate(d, T, RH, v, N_REF, P)
        theta = float(r["share"])
        theta_rating = P.theta0 / (1 + max(P.shelter_factor * V_REF, 0.3) / d.jet_speed)
        rows.append(dict(device=d.name, wet_bulb_depression=round(dep, 1),
                         eps_model=round(eps_of(d, P), 2),
                         eps_implied_by_shelter_reading=round(d.rated_drop / (theta_rating * dep), 2),
                         theta_at_peak_wind=round(theta, 2),
                         air_drop_at_person_peak=round(T - float(r["T_person"]), 1)))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table8_rating_reading.csv"), index=False)
    return df


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
    hd = "Hot-dry (Phoenix-like)"
    T, RH = peak(hd)
    v, pc = peak_wind(hd), replace(P, e_water=E_WATER[hd])
    for n in [1, 2, 4, 6, 8, 10, 12]:
        rB = evaluate(DEVS[1], T, RH, v, n, pc)
        rC = evaluate(DEVS[2], T, RH, v, n, pc)
        rows.append(dict(rule="B vs C by crowd size at hot-dry peak", T=T, value=n, unit="people waiting",
                         eta_B=round(float(rB["eta"]), 1), eta_C=round(float(rC["eta"]), 1),
                         UTCI_after_B=round(float(rB["U1"]), 1), UTCI_after_C=round(float(rC["U1"]), 1)))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table5_decision_rules.csv"), index=False)
    return df


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
def fig7_cooling_fate(t2):
    sub = t2[(t2.control == "smart") & (t2.device != "A Fan")]
    labels = [f"{r.device.split()[0]}  {r.climate.split(' (')[0]}" for r in sub.itertuples()]
    parts = [("share_delivered", "Reaches people", "#2a78d6"),
             ("share_diluted", "Diluted by hot air on the way", "#eb6834"),
             ("share_unused", "Aimed where nobody stands", "#b8b7b2")]
    fig, ax = plt.subplots(figsize=(6.8, 2.4))
    y = np.arange(len(sub))
    left = np.zeros(len(sub))
    for col, lab, colr in parts:
        vals = sub[col].values * 100
        ax.barh(y, vals, left=left, color=colr, height=0.55, label=lab, edgecolor="white", linewidth=1.0)
        left += vals
    for yi, v in zip(y, sub.share_delivered.values):
        ax.text(1.5, yi, f"{v:.0%}", va="center", fontsize=7.5, color="white", fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of the sensible cooling the cooler makes over the design day (%)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=3, fontsize=7)
    ax.grid(axis="y", visible=False)
    ax.set_title("Fig. 7  Where an evaporative cooler's cooling goes at the bus stop", loc="left", fontsize=9)
    fig.savefig(os.path.join(OUT, "fig7_cooling_fate.png"))
    plt.close(fig)


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
    t6 = design_levers(t2)
    print("\nTable 6 (design levers, common baseline: open shelter, no device)")
    print(t6.to_string(index=False))
    print("\nTable 7 (fans above skin temperature)")
    print(fan_evidence(t2).to_string(index=False))
    print("\nTable 8 (second reading of the device ratings)")
    print(rating_reading().to_string(index=False))
    fig7_cooling_fate(t2)
    print("\nFigures written to", OUT)
