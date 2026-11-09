"""HiMCM 2026 Problem B, requirement 2b: cooling efficiency of a semi-open
rail-station waiting area.

The bus-stop model (2a) treats the shelter as a steady, open space whose air
without cooling equals outdoor air. A semi-open station breaks four of its
assumptions, so this model adds four things:

  1. Heat gains: people, sun through glazing, lights and device motors heat
     a partly enclosed zone above outdoor temperature.
  2. Dynamics: passengers accumulate between trains and leave in a block; each
     train arrival flushes air. The zone is solved as a time-dependent heat
     and moisture balance (dt = 10 s).
  3. Recirculation: coolers draw zone air, so evaporative cooling adds moisture
     that only ventilation removes.
  4. Air conditioning: with enough enclosure a vapour-compression unit becomes a
     candidate; its COP depends on outdoor temperature.

The efficiency definition is unchanged from 2a: heat-stress relief delivered to
people (UTCI, banded weights) per kWh of electricity plus embedded water energy.
"""
import os
import sys
from dataclasses import dataclass, replace
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "stage2"))
from psychro import humidity_ratio, rel_humidity, evaporative_outlet, p_ws  # noqa: E402
from model import (Params, devices_for, utci, stress_dose, eps_of, RHO, CP, G,  # noqa: E402
                   sun_factor)
from run_stage2 import CLIMATES  # noqa: E402

OUT = os.path.join(HERE, "outputs")
os.makedirs(OUT, exist_ok=True)

P2A = Params()
DEVS2A = devices_for(P2A)
H_FG = 2450.0
DT = 10.0                 # s
T_START, T_END = 5.0, 22.0   # simulate from 05:00 (one hour warm-up), report 06:00-22:00


# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Station:
    name: str = "Semi-open waiting area"
    L: float = 30.0            # m, length along the platform
    D: float = 8.0             # m, depth
    Hz: float = 2.5            # m, occupied zone height (cool layer)
    H_open: float = 2.5        # m, height of the wall-opening band
    open_track: float = 1.0    # open fraction of the track-side wall band
    open_back: float = 0.2     # entrances on the street side
    open_ends: float = 0.5
    dwell_open: float = 0.0    # extra track-side opening while a train dwells (screen doors)
    kappa_train: float = 0.3   # share of zone air exchanged by each train arrival (gust)
    dwell_s: float = 40.0
    shgc: float = 0.4          # tinted glazing in closed wall areas
    I_vert: float = 400.0      # W/m2 peak irradiance on the glazing (facade average)
    solar_to_zone: float = 0.6 # share of transmitted sun absorbed in the occupied zone
    lights_W_m2: float = 5.0
    mass_factor: float = 3.0   # fast thermal mass relative to the zone air
    C_w: float = 0.3
    Cd: float = 0.6
    dR_shade: float = 4.0
    # switches used for the model-revision ablation
    gains: bool = True
    dynamic: bool = True
    recirculate: bool = True

    @property
    def area(self):
        return self.L * self.D

    @property
    def volume(self):
        return self.area * self.Hz

    def wall_bands(self, dwelling):
        track = min(self.open_track + (self.dwell_open if dwelling else 0.0), 1.0)
        open_w = np.array([track * self.L, self.open_back * self.L, self.open_ends * 2 * self.D])
        total_w = np.array([self.L, self.L, 2 * self.D])
        return open_w, total_w


SCENARIOS = {
    "Open-sided platform": dict(open_track=1.0, open_back=1.0, open_ends=1.0, kappa_train=0.3),
    "Semi-open waiting area": dict(),
    "Platform screen doors": dict(open_track=0.0, dwell_open=0.5, open_back=0.2, open_ends=0.2, kappa_train=0.0),
    "Enclosed waiting room": dict(open_track=0.0, dwell_open=0.15, open_back=0.05, open_ends=0.05, kappa_train=0.0),
}


def station(name, **kw):
    return replace(Station(name=name), **{**SCENARIOS[name], **kw})


def blend(t):
    """Openness sweep: t = 0 enclosed waiting room ... t = 1 open-sided platform."""
    a, b = SCENARIOS["Enclosed waiting room"], SCENARIOS["Open-sided platform"]
    keys = ["open_track", "open_back", "open_ends", "dwell_open", "kappa_train"]
    base = Station()
    vals = {k: (1 - t) * a.get(k, getattr(base, k)) + t * b.get(k, getattr(base, k)) for k in keys}
    return replace(Station(name=f"openness {t:.2f}"), **vals)


@dataclass(frozen=True)
class System:
    """A cooling system sized for 40 waiting passengers."""
    name: str
    kind: str              # none, fan, evap, ac
    power_kw: float = 0.0
    airflow: float = 0.0   # m3/s (evaporative supply)
    eps: float = 0.0
    jet_speed: float = 0.0 # m/s at covered people
    cover: float = 0.0     # people covered by jets / fans
    cap_kw: float = 0.0    # AC total cooling capacity at 35 C
    shr: float = 0.75
    setpoint: float = 26.0
    low_supply: bool = True  # AC supplies the occupied zone directly (vs. mixing the whole hall)


def systems():
    fan, b, c = DEVS2A
    q = P2A.q_per_person
    return [
        System("No cooling", "none"),
        System("A Fans ×10", "fan", 10 * fan.power_kw, jet_speed=fan.jet_speed, cover=10 * fan.airflow / q),
        System("B Evap ×8", "evap", 8 * b.power_kw, 8 * b.airflow, eps_of(b, P2A), b.jet_speed, 8 * b.airflow / q),
        System("C Large evap ×5", "evap", 5 * c.power_kw, 5 * c.airflow, eps_of(c, P2A), c.jet_speed, 5 * c.airflow / q),
        System("D Air conditioner 60 kW", "ac", cap_kw=60.0),
    ]


def ac_cop(T_out):
    """Carnot-fraction COP: evaporator 10 C, condenser 15 K above outdoor air,
    45 % of Carnot. Gives 3.2 at 35 C (AHRI EER ~11)."""
    Te = 283.15
    Tc = T_out + 273.15 + 15.0
    return 0.45 * Te / (Tc - Te)


# ---------------------------------------------------------------------------
# Boundary conditions
# ---------------------------------------------------------------------------
def outdoor(climate, t_h):
    c = CLIMATES[climate]
    T = (c["Tmax"] + c["Tmin"]) / 2 + (c["Tmax"] - c["Tmin"]) / 2 * np.cos(2 * np.pi * (t_h - 15) / 24)
    RH = np.minimum(100 * p_ws(c["Td"]) / p_ws(T), 100)
    return T, RH, c["v"]


def timetable(t_h):
    """Passengers per hour and train headway (min)."""
    peak = ((t_h >= 7) & (t_h < 9)) | ((t_h >= 16) & (t_h < 19))
    lam = np.where(peak, 400.0, np.where(t_h >= 19, 100.0, 150.0))
    head = np.where(peak, 6.0, 10.0)
    return lam, head


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------
def simulate(st, sysm, climate, n_const=None, dt=DT):
    """Time-dependent heat and moisture balance of the occupied zone.

    Each step uses the exact solution of the linear balance with the flows
    frozen over the step, so the update is stable for any dt:
        C dT/dt = rho cp [Q_x (T_o - T) + Q_s (T_s - T)] + G - Q_ac
        M dW/dt = rho    [Q_x (W_o - W) + Q_s (W_s - W)] + m_people - m_ac
    Q_x: exchange with outdoors (wind, buoyancy, train gusts); Q_s: cooler supply.
    """
    t = np.arange(T_START * 3600, T_END * 3600, dt)
    th = t / 3600
    T_o, RH_o, v_o = outdoor(climate, th)
    W_o = humidity_ratio(T_o, RH_o)
    lam, head = timetable(th)

    if st.dynamic and n_const is None:
        # passengers accumulate between trains and board in a block
        phase = np.zeros_like(t)
        since = 0.0
        for i in range(1, len(t)):
            since += dt
            if since >= head[i] * 60:
                since = 0.0
            phase[i] = since
        N = lam / 3600 * phase
        dwelling = phase < st.dwell_s
    else:
        N = lam * head / 60 / 2 if n_const is None else np.full_like(t, n_const)
        dwelling = np.zeros_like(t, dtype=bool)

    C = st.mass_factor * RHO * CP * st.volume            # kJ/K
    M = RHO * st.volume                                  # kg
    lights = st.lights_W_m2 * st.area / 1000 if st.gains else 0.0
    sun = sun_factor(th)
    every = max(1, int(round(60 / dt)))                  # cooler outlet refreshed each minute
    W_coil = float(humidity_ratio(12.0, 100.0))

    T, W = T_o[0], W_o[0]
    out = {k: np.zeros_like(t) for k in ("T", "W", "Q_x", "P", "water", "Q_ac")}
    for i in range(len(t)):
        open_w, total_w = st.wall_bands(dwelling[i])
        Q_wind = st.C_w * (open_w * st.H_open).max() * v_o
        Q_buoy = st.Cd / 3 * open_w.sum() * np.sqrt(G * st.Hz ** 3 * abs(T - T_o[i]) / (T_o[i] + 273.15))
        Q_x = np.hypot(Q_wind, Q_buoy)
        if st.dynamic and dwelling[i]:
            Q_x += st.kappa_train * st.volume / st.dwell_s

        G_kw = 0.0
        if st.gains:
            glass = ((total_w - open_w) * st.H_open).sum()
            G_kw = (N[i] * 0.075 + st.shgc * glass * st.I_vert * sun[i] * st.solar_to_zone / 1000
                    + lights + (sysm.power_kw if sysm.kind in ("fan", "evap") else 0.0))
        m_people = N[i] * 0.045 / H_FG                      # kg/s, 45 W latent each

        Q_s = T_s = W_s = 0.0
        if sysm.kind == "evap":
            if i % every == 0:
                T_in, W_in = (T, W) if st.recirculate else (T_o[i], W_o[i])
                Ts_, Ws_, _ = evaporative_outlet(T_in, rel_humidity(T_in, W_in), sysm.eps)
                Ts_, Ws_ = float(Ts_), float(Ws_)
            Q_s, T_s, W_s = sysm.airflow, Ts_, Ws_
            out["water"][i] = RHO * Q_s * (W_s - W_in) * dt         # kg
            out["P"][i] = sysm.power_kw
        elif sysm.kind == "fan":
            out["P"][i] = sysm.power_kw

        a = RHO * CP * (Q_x + Q_s)                                   # kW/K
        T_eq = (RHO * CP * (Q_x * T_o[i] + Q_s * T_s) + G_kw) / a
        Q_ac = m_ac = 0.0
        if sysm.kind == "ac":
            share = 1.0 if sysm.low_supply else 0.65                 # mixing also cools the upper hall
            # thermostat: remove enough heat to reach the setpoint by the end of the step
            e = np.exp(-dt * a / C)
            T_eq_target = (sysm.setpoint - T * e) / (1 - e)
            Q_ac = float(np.clip(a * (T_eq - T_eq_target), 0.0, sysm.shr * sysm.cap_kw * share))
            T_eq -= Q_ac / a
            if W > W_coil:
                m_ac = Q_ac / share * (1 - sysm.shr) / sysm.shr / H_FG
            out["P"][i] = (Q_ac / share + m_ac * H_FG) / ac_cop(T_o[i])
        T = T_eq + (T - T_eq) * np.exp(-dt * a / C)

        b = RHO * (Q_x + Q_s)
        W_eq = (RHO * (Q_x * W_o[i] + Q_s * W_s) + m_people - m_ac) / b
        W = W_eq + (W - W_eq) * np.exp(-dt * b / M)

        out["T"][i], out["W"][i], out["Q_x"][i], out["Q_ac"][i] = T, W, Q_x, Q_ac

    out.update(t=th, T_o=T_o, RH_o=RH_o, W_o=W_o, N=N, dwelling=dwelling, v_o=v_o, dt=dt)
    out["RH"] = rel_humidity(out["T"], out["W"])
    return out


def comfort(st, sysm, sim, base):
    """UTCI of covered and uncovered people, relief versus the no-cooling run."""
    open_mean = np.mean([st.open_track, st.open_back, st.open_ends])
    v_in = np.maximum(0.3, 0.5 * sim["v_o"] * open_mean)
    Tmrt = sim["T_o"] + st.dR_shade
    U0 = utci(base["T"], Tmrt, v_in, base["RH"])
    U_unc = utci(sim["T"], Tmrt, v_in, sim["RH"])
    N = sim["N"]
    if sysm.kind in ("fan", "evap"):
        if sysm.kind == "evap":
            Ts, Ws, _ = evaporative_outlet(sim["T"], sim["RH"], sysm.eps)
            theta = P2A.theta0 / (1 + v_in / sysm.jet_speed)
            Tp = sim["T"] - theta * (sim["T"] - Ts)
            Wp = sim["W"] + theta * (Ws - sim["W"])
        else:
            Tp, Wp = sim["T"], sim["W"]
        U_cov = utci(Tp, Tmrt, np.hypot(v_in, sysm.jet_speed), rel_humidity(Tp, Wp))
        n_cov = np.minimum(N, sysm.cover)
    else:
        U_cov = U_unc
        n_cov = np.zeros_like(N)
    D0 = stress_dose(U0, P2A.weights)
    benefit = n_cov * (D0 - stress_dose(U_cov, P2A.weights)) + (N - n_cov) * (D0 - stress_dose(U_unc, P2A.weights))
    hot0 = N * (U0 >= 38)
    hot1 = n_cov * (U_cov >= 38) + (N - n_cov) * (U_unc >= 38)
    return dict(U0=U0, U_unc=U_unc, U_cov=U_cov, benefit=benefit, hot0=hot0, hot1=hot1)


def run(st, sysm, climate, base=None):
    sim = simulate(st, sysm, climate)
    if base is None:
        base = sim if sysm.kind == "none" else simulate(st, systems()[0], climate)
    cf = comfort(st, sysm, sim, base)
    rep = sim["t"] >= 6.0
    h = sim["dt"] / 3600
    elec = sim["P"][rep].sum() * h
    water = sim["water"][rep].sum()
    resource = elec + P2A.e_water * water / 1000
    relief = cf["benefit"][rep].sum() * h
    pm = rep & (sim["t"] >= 14.5) & (sim["t"] < 15.5)
    return dict(
        scenario=st.name, system=sysm.name, climate=climate,
        electricity_kWh=round(elec, 1), water_L=round(water, 0), resource_kWh=round(resource, 1),
        relief_person_degC_h=round(relief, 1),
        eta=round(relief / resource, 1) if resource > 0 else np.nan,
        person_h_UTCI38_before=round(cf["hot0"][rep].sum() * h, 1),
        person_h_UTCI38_after=round(cf["hot1"][rep].sum() * h, 1),
        T_zone_15h=round(float(sim["T"][pm].mean()), 1),
        T_out_15h=round(float(sim["T_o"][pm].mean()), 1),
        RH_zone_15h=round(float(sim["RH"][pm].mean()), 0),
        UTCI_15h=round(float(cf["U_unc"][pm][sim["N"][pm] > 0].mean()), 1),
        RH_zone_max=round(float(sim["RH"][rep].max()), 0),
        hours_RH_over_65=round(float((sim["RH"][rep] > 65).sum() * h), 1),
        passenger_h=round(float(sim["N"][rep].sum() * h), 1),
    ), sim, cf
