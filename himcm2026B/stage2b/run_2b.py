"""Requirement 2b runs: validation, model-revision ablation, scenario table,
openness sweep and figures 8-11 (outputs/)."""
import os
from dataclasses import replace
import numpy as np
import pandas as pd

from station import (Station, System, SCENARIOS, station, blend, systems, simulate, run, ac_cop, OUT, P2A, DEVS2A,
                     comfort, T_START, T_END, DT)
from model import volume_mode_zone, evaporative_outlet, evaluate, eps_of, mean_waiting, stress_dose, E_WATER
from run_stage2 import CLIMATES, day_profile, ridership
from plotstyle import plt, BASELINE, INK2

SYS = systems()
CLIM = list(CLIMATES)
SYS_COLORS = {"A Fans ×10": "#2a78d6", "B Evap ×8": "#eb6834", "C Large evap ×5": "#1baf7a",
              "D Air conditioner 60 kW": "#6250d6"}


def openness_index(st):
    return st.openness


# ---------------------------------------------------------------------------
def validation():
    rows = []
    # (1) nesting: the station model with the bus shelter's geometry and 2a's
    # assumptions reproduces the 2a volume-mode zone temperature
    shelter = replace(Station(name="bus shelter"), L=6.0, D=1.8, Hz=2.0, H_open=2.5, open_track=1.0, open_back=0.0,
                      open_ends=1.0, kappa_train=0.0, mass_factor=1.0, gains=False, dynamic=False)
    c = SYS[3]
    c1 = replace(c, power_kw=DEVS2A[2].power_kw, airflow=DEVS2A[2].airflow, rating_policy="uncapped")
    sim = simulate(shelter, c1, CLIM[0], n_const=0.0, dt=5.0)
    k = np.argmin(abs(sim["t"] - 15.0))
    T_o, W_o = sim["T_o"][k], sim["W_o"][k]
    from psychro import rel_humidity
    Ts, Ws, _ = evaporative_outlet(T_o, rel_humidity(T_o, W_o), c1.eps)
    Tz_2a, _, _, _ = volume_mode_zone(T_o, W_o, Ts, Ws, c1.airflow, sim["v_o"][k], 0, P2A)
    rows.append(("balance nesting without rating control: bus shelter reproduces 2a volume mode (zone T at 15:00, C)",
                 round(float(sim["T"][k]), 2), round(float(Tz_2a), 2), abs(sim["T"][k] - Tz_2a) < 0.15))
    # (2) time-step convergence: dt = 10 s vs dt = 2 s
    st = station("Platform screen doors")
    r10 = run(st, SYS[3], CLIM[1])[0]
    s2 = simulate(st, SYS[3], CLIM[1], dt=2.0)
    base2 = simulate(st, SYS[0], CLIM[1], dt=2.0)
    cf2 = comfort(st, SYS[3], s2, base2)
    rep = s2["t"] >= 6
    res2 = s2["P"][rep].sum() * 2 / 3600 + E_WATER[CLIM[1]] * s2["water"][rep].sum() / 1000
    eta2 = cf2["benefit"][rep].sum() * 2 / 3600 / res2
    rows.append(("time step: eta with dt = 10 s vs dt = 2 s (C, screen doors, hot-humid)",
                 r10["eta"], round(float(eta2), 1), abs(r10["eta"] - eta2) / eta2 < 0.02))
    # (3) AC efficiency at the AHRI rating point (35 C outdoor)
    rows.append(("AC COP at 35 C outdoor (AHRI EER 10-12.5 = COP 2.9-3.7)", round(ac_cop(35.0), 2), "2.9-3.7",
                 2.9 <= ac_cop(35.0) <= 3.7))
    # (4) sealed limit: a nearly closed room with ample AC capacity holds the setpoint
    sealed = replace(station("Enclosed waiting room"), dwell_open=0.0, open_back=0.002, open_ends=0.002,
                     open_track=0.0)
    big = replace(SYS[4], cap_kw=300.0)
    s = simulate(sealed, big, CLIM[0])
    k = s["t"] >= 6
    rows.append(("sealed room + ample AC holds the 26 C setpoint (max zone T, 06-22 h)",
                 round(float(s["T"][k].max()), 2), 26.0, s["T"][k].max() < 26.05))
    df = pd.DataFrame(rows, columns=["check", "model", "reference", "pass"])
    df.to_csv(os.path.join(OUT, "table2b_0_validation.csv"), index=False)
    return df


# ---------------------------------------------------------------------------
ABLATION = [
    ("R0  2a model applied to the station", dict(gains=False, dynamic=False)),
    ("R1  + heat gains (people, sun, lights, motors)", dict(gains=True, dynamic=False)),
    ("R2  + train-driven dynamics (full model)", dict(gains=True, dynamic=True)),
]


def ablation():
    rows = []
    for scen in ("Semi-open waiting area", "Platform screen doors"):
        for label, sw in ABLATION:
            st = replace(station(scen), **sw)
            for clim in CLIM:
                base = simulate(st, SYS[0], clim)
                for sysm in SYS[1:]:
                    if sysm.kind == "ac" and not label.startswith("R2"):
                        continue
                    r = run(st, sysm, clim, base)[0]
                    rows.append(dict(scenario=scen, revision=label, climate=clim, system=sysm.name,
                                     eta=r["eta"], relief=r["relief_person_degC_h"],
                                     T_zone_15h_no_cooling=round(float(base["T"][np.argmin(abs(base["t"] - 15))]), 1),
                                     T_zone_15h=r["T_zone_15h"], RH_zone_15h=r["RH_zone_15h"],
                                     ph_UTCI38_after=r["person_h_UTCI38_after"]))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table2b_1_ablation.csv"), index=False)
    return df


def scenarios():
    """Each device's relief is measured against the same station without
    cooling. To compare stations with each other, the table also gives the
    effect of the enclosure itself against one common reference, the uncooled
    open-sided platform, and the relief of enclosure plus device on that common
    baseline. The enclosure uses no energy, so no efficiency is formed from it."""
    rows, sims = [], {}
    w = P2A.weights
    ref = {}
    for clim in CLIM:
        st0 = station("Open-sided platform")
        b0 = simulate(st0, SYS[0], clim)
        ref[clim] = comfort(st0, SYS[0], b0, b0)["U0"]
    for scen in SCENARIOS:
        st = station(scen)
        for clim in CLIM:
            base = simulate(st, SYS[0], clim)
            U0 = comfort(st, SYS[0], base, base)["U0"]
            rep = base["t"] >= 6
            encl = float((base["N"] * (stress_dose(ref[clim], w) - stress_dose(U0, w)))[rep].sum() * base["dt"] / 3600)
            for sysm in SYS:
                r, sim, cf = run(st, sysm, clim, base)
                r["openness"] = round(openness_index(st), 2)
                r["enclosure_relief_person_degC_h"] = round(encl, 1)
                r["relief_common_baseline"] = round(r["relief_person_degC_h"] + encl, 1)
                rows.append(r)
                sims[(scen, clim, sysm.name)] = (sim, cf)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table2b_2_scenarios.csv"), index=False)
    return df, sims


def shelter_bridge():
    """The 2a bus shelter run through the station model: one device, always on,
    2a's hourly mean crowd. 2a's spot mode counts the jet on covered people
    against outdoor air. The station model differs in three ways: it cools the
    zone air that everyone stands in and that the jet entrains, its inside wind
    follows the open share of the walls, and the closed back panel radiates at
    zone temperature. 'jet only' keeps the last two and leaves the zone air
    uncooled, which separates the first."""
    shelter = replace(Station(name="bus shelter"), L=6.0, D=1.8, Hz=2.0, H_open=2.5, open_track=1.0, open_back=0.0,
                      open_ends=1.0, kappa_train=0.0, mass_factor=1.0, gains=False, dynamic=False)
    th = np.arange(T_START * 3600, T_END * 3600, DT) / 3600
    crowd = mean_waiting(*ridership(th))
    rows = []
    for clim in CLIM:
        T, RH, v, n = day_profile(clim)
        pc = replace(P2A, e_water=E_WATER[clim])
        base = simulate(shelter, SYS[0], clim, n_const=crowd)
        rep = base["t"] >= 6
        h = DT / 3600
        for d in DEVS2A[1:]:
            cap = d.airflow / P2A.q_per_person
            r = evaluate(d, T, RH, v, n, pc, "spot")
            eta_2a = float((np.minimum(n, cap) * r["relief"]).sum() / r["resource_kw"].sum())
            one = System(d.name, "evap", d.power_kw, d.airflow, eps_of(d, P2A), d.jet_speed, cap)
            sim = simulate(shelter, one, clim, n_const=crowd)
            res = sim["P"][rep].sum() * h + E_WATER[clim] * sim["water"][rep].sum() / 1000
            full = comfort(shelter, one, sim, base)["benefit"][rep].sum() * h / res
            jet = comfort(shelter, one, dict(base, T_s=sim["T_s"], W_s=sim["W_s"]), base)["benefit"][rep].sum() * h / res
            rows.append(dict(climate=clim, device=d.name, eta_2a_spot=round(eta_2a, 1),
                             eta_station_jet_only=round(float(jet), 1), eta_station=round(float(full), 1),
                             station_over_2a=round(float(full) / eta_2a, 2)))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table2b_8_shelter_bridge.csv"), index=False)
    return df


def door_jump(sims, scen="Platform screen doors", name="C Large evap ×5"):
    """Rise of zone air temperature within two minutes of each train arrival, 14:00-16:00."""
    out = {}
    for clim in CLIM:
        s, _ = sims[(scen, clim, name)]
        arrivals = np.flatnonzero((s["t"] >= 14) & (s["t"] < 16) & s["dwelling"] & ~np.r_[False, s["dwelling"][:-1]])
        n = int(120 / s["dt"])
        rise = [s["T"][i:i + n].max() - s["T"][i - 1] for i in arrivals]
        out[clim] = (round(float(min(rise)), 1), round(float(max(rise)), 1))
    return out


def sweep():
    rows = []
    for t in (0.0, 0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0):
        st = blend(t)
        st0 = replace(st, **ABLATION[0][1])
        for clim in CLIM:
            base = simulate(st, SYS[0], clim)
            base0 = simulate(st0, SYS[0], clim)
            for sysm in SYS[1:]:
                r = run(st, sysm, clim, base)[0]
                eta_2a = run(st0, sysm, clim, base0)[0]["eta"] if sysm.kind != "ac" else np.nan
                rows.append(dict(t=t, openness=round(openness_index(st), 3), climate=clim, system=sysm.name,
                                 eta=r["eta"], eta_2a_model=eta_2a, RH_zone_max=r["RH_zone_max"],
                                 ph_UTCI38_after=r["person_h_UTCI38_after"],
                                 ph_UTCI38_before=r["person_h_UTCI38_before"],
                                 T_zone_15h_no_cooling=round(float(base["T"][np.argmin(abs(base["t"] - 15))]), 1)))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table2b_3_openness_sweep.csv"), index=False)
    return df


def control_comparison():
    """Identical station/weather/occupancy baseline for both control policies."""
    rows = []
    for scen in ("Platform screen doors", "Enclosed waiting room"):
        st = station(scen)
        for clim in CLIM:
            base = simulate(st, SYS[0], clim)
            for sysm in SYS[1:4]:
                for control in ("always", "demand"):
                    rows.append(run(st, replace(sysm, control=control), clim, base)[0])
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table2b_9_controls.csv"), index=False)
    return df


def ac_capacity():
    rows = []
    for scen in ("Platform screen doors", "Enclosed waiting room"):
        st = station(scen)
        for clim in CLIM:
            base = simulate(st, SYS[0], clim)
            for cap in (30.0, 60.0, 120.0):
                r = run(st, replace(SYS[4], cap_kw=cap), clim, base)[0]
                rows.append(dict(scenario=scen, climate=clim, capacity_kW=cap, electricity_kWh=r["electricity_kWh"],
                                 eta=r["eta"], T_zone_15h=r["T_zone_15h"], RH_zone_15h=r["RH_zone_15h"],
                                 ph_UTCI38_before=r["person_h_UTCI38_before"],
                                 ph_UTCI38_after=r["person_h_UTCI38_after"]))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table2b_5_ac_capacity.csv"), index=False)
    return df


def intake():
    """Where the evaporative coolers take their air: outdoors (ducted, the
    default) or the zone itself (free-standing units that recirculate)."""
    rows = []
    for scen in SCENARIOS:
        st = station(scen)
        for clim in CLIM:
            base = simulate(st, SYS[0], clim)
            for sysm in SYS[2:4]:
                for rec in (False, True):
                    r = run(st, replace(sysm, recirculate=rec), clim, base)[0]
                    rows.append(dict(scenario=scen, climate=clim, system=sysm.name,
                                     intake="zone air (recirculating)" if rec else "outdoor air",
                                     eta=r["eta"], relief=r["relief_person_degC_h"], water_L=r["water_L"],
                                     T_zone_15h=r["T_zone_15h"], RH_zone_15h=r["RH_zone_15h"],
                                     RH_zone_max=r["RH_zone_max"], hours_RH_over_65=r["hours_RH_over_65"],
                                     ph_UTCI38_after=r["person_h_UTCI38_after"]))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table2b_7_intake.csv"), index=False)
    return df


SENS = {
    "Peak irradiance on glazing (W/m²)": ("I_vert", 200.0, 600.0),
    "Glazing SHGC": ("shgc", 0.25, 0.6),
    "Door opening while a train dwells": ("dwell_open", 0.3, 0.8),
    "Wind exchange coefficient C_w": ("C_w", 0.15, 0.5),
    "Thermal mass factor": ("mass_factor", 1.0, 6.0),
    "Entrance openness (street side)": ("open_back", 0.1, 0.4),
    "Roof U-value (W/m²K)": ("U_roof", 0.3, 5.0),
    "Radiant excess of the outdoor view (°C)": ("dR_shade", 8.0, 16.0),
    "Radiant excess of enclosed surfaces (°C)": ("dR_inside", 2.0, 8.0),
}


def sensitivity(scen="Platform screen doors"):
    rows = []
    for label, (field, lo, hi) in [("base", (None, None, None))] + list(SENS.items()):
        for val in ([None] if field is None else [lo, hi]):
            st = station(scen) if field is None else replace(station(scen), **{field: val})
            for clim in CLIM:
                base = simulate(st, SYS[0], clim)
                res = {s.name: run(st, s, clim, base)[0] for s in SYS[1:]}
                etas = {k: r["eta"] for k, r in res.items()}
                finite_etas = {k: v for k, v in etas.items() if np.isfinite(v)}
                best = max(finite_etas, key=finite_etas.get) if finite_etas else "unsupported UTCI inputs"
                rows.append(dict(parameter=label, value=val, climate=clim, best=best,
                                 T_zone_15h_no_cooling=round(float(base["T"][np.argmin(abs(base["t"] - 15))]), 1),
                                 **etas, RH_max_B=res[SYS[2].name]["RH_zone_max"],
                                 RH_max_C=res[SYS[3].name]["RH_zone_max"]))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table2b_6_sensitivity.csv"), index=False)
    return df


def ac_supply():
    rows = []
    for scen in ("Platform screen doors", "Enclosed waiting room"):
        st = station(scen)
        for clim in CLIM:
            base = simulate(st, SYS[0], clim)
            for low in (True, False):
                sysm = replace(SYS[4], low_supply=low)
                r = run(st, sysm, clim, base)[0]
                rows.append(dict(scenario=scen, climate=clim,
                                 supply="low-level supply to occupied zone" if low else "mixing (cools whole hall)",
                                 electricity_kWh=r["electricity_kWh"], eta=r["eta"], T_zone_15h=r["T_zone_15h"],
                                 ph_UTCI38_after=r["person_h_UTCI38_after"]))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "table2b_4_ac_supply.csv"), index=False)
    return df


# ---------------------------------------------------------------------------
def block_mean(x, n):
    m = len(x) // n * n
    return x[:m].reshape(-1, n).mean(axis=1)


def fig8(sims, scen="Platform screen doors"):
    fig, axes = plt.subplots(2, 2, figsize=(7.6, 5.2), sharex=True)
    n = int(900 / 10)   # 15-minute means
    for j, clim in enumerate(CLIM):
        sim0, _ = sims[(scen, clim, "No cooling")]
        k = sim0["t"] >= 6
        t = block_mean(sim0["t"][k], n)
        for i, (key, ylab) in enumerate((("T", "Zone air temperature (°C)"), ("RH", "Zone relative humidity (%)"))):
            ax = axes[i, j]
            ax.plot(t, block_mean((sim0["T_o"] if key == "T" else sim0["RH_o"])[k], n), color=BASELINE,
                    ls="--", lw=1.0, label="Outdoor")
            ax.plot(t, block_mean(sim0[key][k], n), color=BASELINE, lw=1.6, label="No cooling")
            for name, col in SYS_COLORS.items():
                s, _ = sims[(scen, clim, name)]
                ax.plot(t, block_mean(s[key][k], n), color=col, lw=1.4, label=name)
            if i == 0:
                ax.set_title(clim, fontsize=9)
            if j == 0:
                ax.set_ylabel(ylab)
            if i == 1:
                ax.set_xlabel("Hour of day (15-min means)")
                ax.set_xticks([6, 9, 12, 15, 18, 21])
    h, lab = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=6, fontsize=7, frameon=False)
    fig.suptitle(f"Fig. 8  Zone air over the design day: {scen.lower()}", x=0.01, ha="left", fontsize=10)
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    fig.savefig(os.path.join(OUT, "fig8_zone_timeseries.png"))
    plt.close(fig)


def fig9(sw):
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.1), sharey=False)
    for ax, clim in zip(axes, CLIM):
        s = sw[sw.climate == clim]
        for name, col in SYS_COLORS.items():
            d = s[s.system == name].sort_values("openness")
            ax.plot(d.openness * 100, d.eta, color=col, marker="o", ms=3.5, label=name)
        ax.axhline(0, color="#b8b7b2", lw=0.7)
        ax.set_title(clim, fontsize=9)
        ax.set_xlabel("Open share of the waiting-area walls (%)")
    axes[0].set_ylabel("η (person·°C·h per kWh)")
    h, lab = axes[1].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=4, fontsize=7, frameon=False)
    fig.suptitle("Fig. 9  Enclosure decides the technology: η across openness", x=0.01, ha="left", fontsize=10)
    fig.tight_layout(rect=(0, 0.08, 1, 0.92))
    fig.savefig(os.path.join(OUT, "fig9_eta_vs_openness.png"))
    plt.close(fig)


def fig10(sims, scen="Platform screen doors", clim=None, name="C Large evap ×5"):
    clim = clim or CLIM[0]
    s, cf = sims[(scen, clim, name)]
    s0, _ = sims[(scen, clim, "No cooling")]
    k = (s["t"] >= 15.0) & (s["t"] < 15.75)
    m = (s["t"][k] - 15.0) * 60
    fig, axes = plt.subplots(2, 1, figsize=(5.6, 3.6), sharex=True)
    axes[0].plot(m, s["N"][k], color=INK2, lw=1.2)
    axes[0].set_ylabel("People waiting")
    axes[1].plot(m, s0["T"][k], color=BASELINE, lw=1.2, label="No cooling")
    axes[1].plot(m, s["T"][k], color=SYS_COLORS[name], lw=1.2, label=name)
    for x in m[s["dwelling"][k] & ~np.r_[False, s["dwelling"][k][:-1]]]:
        for ax in axes:
            ax.axvline(x, color="#d9d8d4", lw=0.8, zorder=0)
    axes[1].set_ylabel("Zone air (°C)")
    axes[1].set_xlabel("Minutes after 15:00 (grey lines = train arrivals)")
    axes[1].legend(loc="center right", fontsize=7)
    axes[0].set_title(f"Fig. 10  Train-scale dynamics, {scen.lower()}, {clim.split(' (')[0].lower()}",
                      loc="left", fontsize=9)
    fig.savefig(os.path.join(OUT, "fig10_train_dynamics.png"))
    plt.close(fig)


def fig11(sw):
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.2))
    for ax, clim in zip(axes, CLIM):
        s = sw[sw.climate == clim]
        for name in ("A Fans ×10", "B Evap ×8", "C Large evap ×5"):
            d = s[s.system == name].sort_values("openness")
            ax.plot(d.openness * 100, d.eta, color=SYS_COLORS[name], marker="o", ms=3.5, label=f"{name}: revised model")
            ax.plot(d.openness * 100, d.eta_2a_model, color=SYS_COLORS[name], ls="--", lw=1.1,
                    label=f"{name}: 2a model")
        ax.axhline(0, color="#b8b7b2", lw=0.7)
        ax.set_title(clim, fontsize=9)
        ax.set_xlabel("Open share of the waiting-area walls (%)")
    axes[0].set_ylabel("η (person·°C·h per kWh)")
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=3, fontsize=6.5, frameon=False)
    fig.suptitle("Fig. 11  The bus-stop (2a) model versus the revised model across openness",
                 x=0.01, ha="left", fontsize=10)
    fig.tight_layout(rect=(0, 0.13, 1, 0.92))
    fig.savefig(os.path.join(OUT, "fig11_2a_model_error.png"))
    plt.close(fig)


if __name__ == "__main__":
    pd.set_option("display.width", 230)
    pd.set_option("display.max_columns", 30)
    v = validation()
    print("Validation")
    for _, x in v.iterrows():
        print(f"  [{'PASS' if x['pass'] else 'FAIL'}] {x.check}: {x.model} vs {x.reference}")
    ab = ablation()
    print("\nTable 2b-1 ablation")
    print(ab.to_string(index=False))
    sc, sims = scenarios()
    print("\nTable 2b-2 scenarios")
    print(sc.drop(columns=["passenger_h"]).to_string(index=False))
    print("\nDoor openings (screen doors, C): zone air rises by",
          ", ".join(f"{a}-{b} C ({c.split(' (')[0].lower()})" for c, (a, b) in door_jump(sims).items()))
    sw = sweep()
    print("\nTable 2b-3 openness sweep")
    print(sw.pivot_table(index=["climate", "openness"], columns="system", values=["eta", "eta_2a_model"]).round(1).to_string())
    acc = ac_capacity()
    print("\nTable 2b-5 AC capacity")
    print(acc.to_string(index=False))
    se = sensitivity()
    print("\nTable 2b-6 sensitivity (platform screen doors)")
    print(se.to_string(index=False))
    acs = ac_supply()
    print("\nTable 2b-4 AC supply")
    print(acs.to_string(index=False))
    print("\nTable 2b-8 the 2a bus shelter in the station model (always on, same crowd)")
    print(shelter_bridge().to_string(index=False))
    print("\nTable 2b-7 evaporative-cooler intake")
    print(intake().to_string(index=False))
    print("\nTable 2b-9 comparable always-on and demand controls")
    print(control_comparison().to_string(index=False))
    fig8(sims)
    fig9(sw)
    fig10(sims)
    fig11(sw)
    print("\nFigures written to", OUT)
