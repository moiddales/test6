"""HiMCM 2026 Problem B, requirement 1: what a cooling-efficiency measure for an
open freezer case must contain.

Reference case: a 12-ft (3.66 m) low-temperature open vertical multideck
freezer with an air curtain, remote condensing, in a store at ISO 23953
climate class 3 (25 degC, 60 % RH).

Refrigeration load = infiltration (sensible + latent) + radiation through the
opening + wall conduction + internal heat (fans, lights, heaters).
Electricity = load / COP + fans + lights + heaters + defrost.

Infiltration is calibrated once to the literature share (75 % of the load;
SCE tests put it at 70-80 % for open vertical cases, ACEEE 2004); the door retrofit, the DOE energy limit and the
energy closure are then independent checks.
"""
import os
import sys
from dataclasses import dataclass, replace
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stage2"))
from psychro import humidity_ratio  # noqa: E402
from plotstyle import plt, INK2  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUT, exist_ok=True)

SIGMA = 5.67e-8
R_AIR = 287.0
L_FUSION = 334.0       # kJ/kg
# ASHRAE 72 / DOE test: doors opened ~6 times per hour for 8 of 24 hours
TEST_PROTOCOL = dict(openings_per_door_h=6.0, opening_hours=8.0)
TRADING_HOURS = 16.0


@dataclass(frozen=True)
class Case:
    length: float = 3.66        # m (12 ft)
    open_height: float = 1.6    # m
    wall_area: float = 16.4     # m2 insulated envelope
    U_wall: float = 0.45        # W/m2K
    T_air: float = -25.0        # degC discharge / case air
    T_product: float = -20.0    # degC product surface
    eps_view: float = 0.56      # effective emissivity x view factor of the opening
    fans_kw: float = 0.20
    lights_kw: float = 0.15
    rail_heaters_kw: float = 0.10
    heater_share_in: float = 0.5    # share of heater power that ends up as case load
    infil_share: float = 0.75       # calibration target (SCE tests: 0.70-0.80)
    cop: float = 1.6                # low-temperature remote system
    defrost_eff: float = 0.30       # share of defrost heat that melts frost
    # night covers
    cover_hours: float = 8.0
    cover_cut: float = 0.8          # fraction of opening loads stopped by a cover
    # glass doors
    n_doors: int = 5
    U_glass: float = 1.5            # W/m2K, triple-glazed low-e door
    door_heaters_kw: float = 0.30   # anti-sweat heaters, 5 doors
    openings_per_door_h: float = 20.0   # store traffic
    opening_hours: float = 16.0         # hours per day with door traffic
    exchanged_volume: float = 0.35      # m3 of cabinet air replaced per opening

    @property
    def opening_area(self):
        return self.length * self.open_height

    @property
    def tda_ft2(self):
        return self.opening_area * 10.764


def rho(T):
    return 101325.0 / (R_AIR * (np.asarray(T) + 273.15))


def opening_loads(c, T_store, RH_store):
    """Per kg of infiltrated air: sensible and latent enthalpy difference;
    radiation through the opening in kW."""
    W_s = humidity_ratio(T_store, RH_store)
    W_c = humidity_ratio(c.T_air, 100.0)
    dh_sens = 1.006 * (T_store - c.T_air) + W_c * 1.86 * (T_store - c.T_air)
    dh_lat = (W_s - W_c) * (2501.0 + 1.86 * T_store + L_FUSION)   # vapour ends up as frost
    q_rad = c.eps_view * SIGMA * c.opening_area * ((T_store + 273.15) ** 4 - (c.T_product + 273.15) ** 4) / 1000
    return dh_sens, dh_lat, W_s - W_c, q_rad


def fixed_loads(c, T_store):
    q_cond = c.U_wall * c.wall_area * (T_store - c.T_air) / 1000
    q_int = c.fans_kw + c.lights_kw + c.heater_share_in * c.rail_heaters_kw
    return q_cond, q_int


def calibrate_infiltration(c):
    """Mass flow of store air through the air curtain [kg/s] that makes
    infiltration the literature share of the load at class 3."""
    dh_s, dh_l, _, q_rad = opening_loads(c, 25.0, 60.0)
    q_cond, q_int = fixed_loads(c, 25.0)
    q_other = q_rad + q_cond + q_int
    q_inf = c.infil_share / (1 - c.infil_share) * q_other
    return q_inf / (dh_s + dh_l)


def daily(c, variant, T_store=25.0, RH_store=60.0, m_inf=None):
    """Daily refrigeration load components [kWh_th] and electricity [kWh_e]."""
    m_inf = calibrate_infiltration(c) if m_inf is None else m_inf
    dh_s, dh_l, dW, q_rad = opening_loads(c, T_store, RH_store)
    q_cond, q_int = fixed_loads(c, T_store)
    heaters_kw = c.rail_heaters_kw
    if variant == "open":
        hours_exposed = 24.0
    elif variant == "night covers":
        hours_exposed = 24.0 - c.cover_hours * c.cover_cut
    else:
        hours_exposed = 0.0
    m_day = m_inf * 3600 * hours_exposed                    # kg air / day
    rad = q_rad * hours_exposed
    if variant == "glass doors":
        openings = c.n_doors * c.openings_per_door_h * c.opening_hours
        m_day = openings * c.exchanged_volume * rho(c.T_air)
        rad = 0.0
        q_cond += c.U_glass * c.opening_area * (T_store - c.T_air) / 1000
        heaters_kw = c.door_heaters_kw
        q_int = c.fans_kw + c.lights_kw + c.heater_share_in * heaters_kw
    comp = dict(
        infiltration_sensible=m_day * dh_s / 3600,
        infiltration_latent=m_day * dh_l / 3600,
        radiation=rad,
        conduction=q_cond * 24,
        internal=q_int * 24,
    )
    load = sum(comp.values())
    frost = m_day * dW                                       # kg/day
    defrost = frost * (L_FUSION + 2.1 * 25 + 4.19 * 5) / c.defrost_eff / 3600   # kWh_e
    elec = load / c.cop + (c.fans_kw + c.lights_kw + heaters_kw) * 24 + defrost
    return dict(variant=variant, T_store=T_store, RH_store=RH_store, **comp, load_kwh=load,
                frost_kg=frost, defrost_kwh=defrost, electricity_kwh=elec,
                opening_share=(comp["infiltration_sensible"] + comp["infiltration_latent"] + comp["radiation"]) / load)


def doe_limit(c, horizontal=False):
    """DOE maximum daily energy for equipment made on or after 27 March 2017,
    remote-condensing low-temperature classes (10 CFR 431.66(e), 2025 edition):
    VOP.RC.L = 2.2 TDA + 6.85, HZO.RC.L = 0.55 TDA + 6.88 (TDA in ft2)."""
    return (0.55 * c.tda_ft2 + 6.88) if horizontal else (2.2 * c.tda_ft2 + 6.85)


def store_hvac_credit(r, cool_fraction, cop_ac=3.0, cop_heat=2.5):
    """Net store HVAC electricity [kWh/day] caused by the case taking heat and
    moisture out of the store air: negative = saving (cooling season)."""
    q_store = r["infiltration_sensible"] + r["infiltration_latent"] + r["radiation"] + r["conduction"]
    return -cool_fraction * q_store / cop_ac + (1 - cool_fraction) * (q_store - r["infiltration_latent"]) / cop_heat


# ---------------------------------------------------------------------------
def main():
    c = Case()
    m_inf = calibrate_infiltration(c)
    v_eq = m_inf / (rho(25.0) * c.opening_area)
    print(f"Calibrated infiltration: {m_inf:.3f} kg/s = {v_eq * 100:.1f} cm/s of store air across "
          f"{c.opening_area:.2f} m2 opening ({c.tda_ft2:.0f} ft2 TDA)")

    variants = ["open", "night covers", "glass doors"]
    t1 = pd.DataFrame([daily(c, v) for v in variants]).round(2)
    t1["kwh_per_m2_display"] = (t1.electricity_kwh / c.opening_area).round(1)
    # service delivered: display area accessible to shoppers during trading hours, product at <= -18 C
    t1["service_m2h_per_kwh"] = (c.opening_area * TRADING_HOURS / t1.electricity_kwh).round(2)
    t1.to_csv(os.path.join(OUT, "tableS1_variants.csv"), index=False)
    print("\nTable S1: daily loads by design (store 25 C / 60 %)")
    print(t1.to_string(index=False))

    # --- checks (door retrofit under the laboratory door-opening protocol) ---
    base, doors = t1.iloc[0], t1.iloc[2]
    lab = daily(replace(c, **TEST_PROTOCOL), "glass doors")
    load_cut = 1 - lab["load_kwh"] / base.load_kwh
    elec_cut = 1 - lab["electricity_kwh"] / base.electricity_kwh
    limit = doe_limit(c)
    rows = [
        ("door retrofit, test protocol: refrigeration-load reduction (%)", round(load_cut * 100, 1), "68 % (SCE lab test) to 80 % (Hillphoenix, ASHRAE 72)", 0.68 <= load_cut <= 0.80),
        ("door retrofit, test protocol: electricity reduction (%)", round(elec_cut * 100, 1), "71 % (Hillphoenix, ASHRAE 72)", 0.55 <= elec_cut <= 0.75),
        ("open case electricity vs DOE VOP.RC.L limit (kWh/day)", round(base.electricity_kwh, 1), f"limit {limit:.1f}", base.electricity_kwh <= limit),
    ]
    # energy closure on frost: latent infiltration load equals vapour removed x (condensation + fusion)
    lat = base.infiltration_latent
    frost_energy = base.frost_kg * (2501.0 + 1.86 * 25 + L_FUSION) / 3600
    rows.append(("latent load = frost x (condensation + fusion) (kWh)", round(lat, 2), round(float(frost_energy), 2),
                 abs(lat - frost_energy) / lat < 0.01))
    t0 = pd.DataFrame(rows, columns=["check", "model", "reference", "pass"])
    t0.to_csv(os.path.join(OUT, "tableS0_checks.csv"), index=False)
    print("\nChecks")
    for _, x in t0.iterrows():
        print(f"  [{'PASS' if x['pass'] else 'FAIL'}] {x.check}: {x.model} vs {x.reference}")

    # --- store climate: same case, same service, different energy ---
    rows = []
    for T in (21.0, 24.0, 27.0):
        for RH in np.arange(30, 75, 5):
            r = daily(c, "open", T, RH, m_inf)
            rows.append(dict(T_store=T, RH_store=RH, electricity_kwh=r["electricity_kwh"],
                             load_kwh=r["load_kwh"], frost_kg=r["frost_kg"]))
    t2 = pd.DataFrame(rows).round(2)
    t2.to_csv(os.path.join(OUT, "tableS2_store_climate.csv"), index=False)
    lo = t2[(t2.T_store == 21) & (t2.RH_store == 40)].electricity_kwh.item()
    hi = t2[(t2.T_store == 27) & (t2.RH_store == 70)].electricity_kwh.item()
    print(f"\nStore climate: 21 C/40 % -> {lo:.1f} kWh/day; 27 C/70 % -> {hi:.1f} kWh/day (x{hi / lo:.2f})")

    # --- system boundary: the store HVAC sees the case as a cooler/dehumidifier ---
    rows = []
    for climate, fcool in (("Cooling-dominated store (Houston-like)", 0.85), ("Heating-dominated store (Minneapolis-like)", 0.35)):
        for _, r in t1.iterrows():
            credit = store_hvac_credit(r, fcool)
            rows.append(dict(store=climate, variant=r.variant, case_kwh=r.electricity_kwh,
                             store_hvac_kwh=round(credit, 1), system_kwh=round(r.electricity_kwh + credit, 1)))
    t3 = pd.DataFrame(rows)
    t3.to_csv(os.path.join(OUT, "tableS3_system_boundary.csv"), index=False)
    print("\nTable S3: case energy vs whole-store energy")
    print(t3.to_string(index=False))

    # --- the value of access: break-even sales effect of doors ---
    price = 0.13          # $/kWh, US commercial average order
    saving = (base.electricity_kwh - doors.electricity_kwh) * 365 * price
    print(f"\nDoors save {base.electricity_kwh - doors.electricity_kwh:.0f} kWh/day = ${saving:,.0f}/year per case "
          f"at ${price}/kWh; they pay off unless they cost more than ${saving / 365:.2f}/day of gross margin "
          f"(~{saving / 365:.0f} fewer items/day at $1 margin each).")

    # --- sensitivity of the calibrated infiltration share ---
    rows = []
    for share in (0.70, 0.75, 0.80):
        cc = replace(c, infil_share=share)
        o, d = daily(cc, "open"), daily(cc, "glass doors")
        rows.append(dict(infil_share=share, open_kwh=round(o["electricity_kwh"], 1),
                         doors_kwh=round(d["electricity_kwh"], 1),
                         load_cut_pct=round((1 - d["load_kwh"] / o["load_kwh"]) * 100, 1)))
    for n_open in (6, 20, 40):
        cc = replace(c, openings_per_door_h=n_open)
        o, d = daily(cc, "open"), daily(cc, "glass doors")
        rows.append(dict(openings_per_door_h=n_open, open_kwh=round(o["electricity_kwh"], 1),
                         doors_kwh=round(d["electricity_kwh"], 1),
                         load_cut_pct=round((1 - d["load_kwh"] / o["load_kwh"]) * 100, 1)))
    t4 = pd.DataFrame(rows)
    t4.to_csv(os.path.join(OUT, "tableS4_sensitivity.csv"), index=False)
    print("\nTable S4: sensitivity")
    print(t4.to_string(index=False))

    print(f"\nDOE allowance per ft2 display: vertical open {2.2:.2f} vs horizontal open {0.55:.2f} kWh/day "
          f"(x{2.2 / 0.55:.1f}); for this case's TDA: {doe_limit(c):.0f} vs {doe_limit(c, True):.0f} kWh/day")

    figS1(t1)
    figS2(t2, limit)


COMPONENT_COLORS = {
    "infiltration_sensible": "#2a78d6",
    "infiltration_latent": "#eb6834",
    "radiation": "#1baf7a",
    "conduction": "#eda100",
    "internal": "#e87ba4",
}
COMPONENT_LABELS = {
    "infiltration_sensible": "Infiltration, sensible",
    "infiltration_latent": "Infiltration, latent (becomes frost)",
    "radiation": "Radiation through opening",
    "conduction": "Conduction (walls, glass)",
    "internal": "Fans, lights, heaters",
}


def figS1(t1):
    fig, ax = plt.subplots(figsize=(6.8, 2.6))
    y = np.arange(len(t1))
    left = np.zeros(len(t1))
    for k, col in COMPONENT_COLORS.items():
        ax.barh(y, t1[k], left=left, color=col, height=0.55, label=COMPONENT_LABELS[k],
                edgecolor="white", linewidth=1.0)
        left += t1[k].values
    for yi, tot, share in zip(y, left, t1.opening_share):
        ax.text(tot + 3, yi, f"{tot:.0f} kWh/day  ({share:.0%} through the opening)", va="center",
                fontsize=7.5, color=INK2)
    ax.set_yticks(y)
    ax.set_yticklabels(["Open, air curtain", "Open + night covers", "Glass doors"])
    ax.invert_yaxis()
    ax.set_xlim(0, left.max() * 1.55)
    ax.set_xlabel("Refrigeration load (kWh of heat removed per day)")
    ax.legend(loc="lower right", fontsize=7, ncol=1)
    ax.grid(axis="y", visible=False)
    ax.set_title("Fig. S1  Where an open freezer case's cooling goes (12-ft low-temp case, store 25 °C / 60 %)",
                 loc="left", fontsize=9)
    fig.savefig(os.path.join(OUT, "figS1_load_breakdown.png"))
    plt.close(fig)


def figS2(t2, limit):
    fig, ax = plt.subplots(figsize=(4.8, 3.0))
    for T, col in zip((21.0, 24.0, 27.0), ("#2a78d6", "#eb6834", "#1baf7a")):
        s = t2[t2.T_store == T]
        ax.plot(s.RH_store, s.electricity_kwh, color=col, label=f"Store at {T:.0f} °C")
    ax.axhline(limit, color=INK2, ls="--", lw=0.9)
    ax.text(30.5, limit + 2, "DOE limit for this case (VOP.RC.L)", fontsize=7, color=INK2)
    ax.set_xlabel("Store relative humidity (%)")
    ax.set_ylabel("Case electricity (kWh/day)")
    ax.legend(loc="lower right", fontsize=7)
    ax.set_title("Fig. S2  Same case, same products: energy follows store air", loc="left", fontsize=9)
    fig.savefig(os.path.join(OUT, "figS2_store_climate.png"))
    plt.close(fig)


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)
    main()
