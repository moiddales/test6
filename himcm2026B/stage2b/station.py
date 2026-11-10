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
  3. Moisture: the zone keeps the moisture that evaporative coolers add until
     ventilation removes it. Coolers draw outdoor air (ducted, the default) or
     zone air (free-standing units that recirculate).
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
from psychro import humidity_ratio, rel_humidity, evaporative_outlet, enthalpy  # noqa: E402
from model import (Params, devices_for, utci, stress_dose, eps_of, RHO, CP, G,  # noqa: E402
                   sun_factor, E_WATER, rated_fan)
from run_stage2 import weather  # noqa: E402

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
    # roof: sol-air method (ASHRAE Fundamentals): T_sa = T_o + a I_hor / h_o - 3.9 K
    U_roof: float = 1.0        # W/m2K, lightly insulated metal deck
    roof_absorptance: float = 0.6
    I_hor: float = 950.0       # W/m2 peak global irradiance on the roof
    h_out: float = 17.0        # W/m2K outside surface coefficient
    mass_factor: float = 3.0   # fast thermal mass relative to the zone air
    C_w: float = 0.3
    Cd: float = 0.6
    dR_shade: float = 12.0     # degC radiant excess of the outdoor view (same as the bus shelter, 2a)
    dR_inside: float = 4.0     # degC radiant excess of enclosed walls and roof over zone air
    # switches used for the model-revision ablation
    gains: bool = True
    dynamic: bool = True

    @property
    def area(self):
        return self.L * self.D

    @property
    def volume(self):
        return self.area * self.Hz

    @property
    def openness(self):
        """Open share of the wall band with doors closed."""
        open_w, total_w = self.wall_bands(False)
        return float(open_w.sum() / total_w.sum())

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
    recirculate: bool = False  # evaporative cooler draws zone air instead of outdoor air
    cap_kw: float = 0.0    # AC total cooling capacity at 35 C
    shr: float = 0.75
    setpoint: float = 26.0
    low_supply: bool = True  # AC supplies the occupied zone directly (vs. mixing the whole hall)
    rated_drop: float = np.inf
    rating_policy: str = "occupied"
    control: str = "always"   # always or demand (heat demand + occupancy; evap RH hysteresis)
    rh_stop: float = 65.0
    rh_resume: float = 60.0


def systems():
    fan, b, c = DEVS2A
    q = P2A.q_per_person
    return [
        System("No cooling", "none"),
        System("A Fans ×10", "fan", 10 * fan.power_kw, jet_speed=fan.jet_speed, cover=10 * fan.airflow / q, rated_drop=fan.rated_drop),
        System("B Evap ×8", "evap", 8 * b.power_kw, 8 * b.airflow, eps_of(b, P2A), b.jet_speed, 8 * b.airflow / q, rated_drop=b.rated_drop),
        System("C Large evap ×5", "evap", 5 * c.power_kw, 5 * c.airflow, eps_of(c, P2A), c.jet_speed, 5 * c.airflow / q, rated_drop=c.rated_drop),
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
    return weather(climate, t_h)


def timetable(t_h):
    """Passengers per hour and train headway (min)."""
    peak = ((t_h >= 7) & (t_h < 9)) | ((t_h >= 16) & (t_h < 19))
    lam = np.where(peak, 400.0, np.where(t_h >= 19, 100.0, 150.0))
    head = np.where(peak, 6.0, 10.0)
    return lam, head


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------
def simulate(st, sysm, climate, n_const=None, dt=DT, on=None, base=None):
    """Time-dependent heat and moisture balance of the occupied zone.

    Each step uses the exact solution of the linear balance with the flows
    frozen over the step, so the update is stable for any dt:
        C dT/dt = rho cp [Q_x (T_o - T) + Q_s (T_s - T)] + G - Q_ac
        M dW/dt = rho    [Q_x (W_o - W) + Q_s (W_s - W)] + m_people - m_ac
    Q_x: exchange with outdoors (wind, buoyancy, train gusts); Q_s: cooler supply.
    `on` is an external enable mask for every device. Demand control uses
    local heat-stress/occupancy sensors; evap additionally uses 60/65% RH
    hysteresis and a one-step moisture prediction. Thermal states continue
    evolving when a device is off.
    """
    t = np.arange(T_START * 3600, T_END * 3600, dt)
    th = t / 3600
    T_o, RH_o, v_o = outdoor(climate, th)
    W_o = humidity_ratio(T_o, RH_o)
    if sysm.rating_policy not in ("occupied", "outlet", "uncapped"):
        raise ValueError("Unknown rating_policy")
    if sysm.kind == "evap" and sysm.rating_policy == "occupied" and base is None:
        base = simulate(st, systems()[0], climate, n_const=n_const, dt=dt)
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

    T_solair = T_o + st.roof_absorptance * st.I_hor * sun / st.h_out - 3.9
    requested_on = np.ones_like(t, dtype=bool) if on is None else np.asarray(on, dtype=bool)
    if requested_on.shape != t.shape:
        raise ValueError("on must match the simulation time grid")
    if sysm.control not in ("always", "demand"):
        raise ValueError("Unknown control")
    on = np.zeros_like(t, dtype=bool)
    wet_enabled, useful = True, True
    if sysm.kind == "evap" and not sysm.recirculate:
        nominal_ts, nominal_ws, _ = evaporative_outlet(T_o, RH_o, sysm.eps)

    T, W = T_o[0], W_o[0]
    out = {k: np.zeros_like(t) for k in ("T", "W", "Q_x", "P", "water", "Q_ac", "T_s", "W_s")}
    for i in range(len(t)):
        open_w, total_w = st.wall_bands(dwelling[i])
        Q_wind = st.C_w * (open_w * st.H_open).max() * v_o[i]
        Q_buoy = st.Cd / 3 * open_w.sum() * np.sqrt(G * st.Hz ** 3 * abs(T - T_o[i]) / (T_o[i] + 273.15))
        Q_x = np.hypot(Q_wind, Q_buoy)
        if st.dynamic and dwelling[i]:
            Q_x += st.kappa_train * st.volume / st.dwell_s

        T_in, W_in = (T, W) if sysm.recirculate else (T_o[i], W_o[i])
        if sysm.kind == "evap":
            if not sysm.recirculate:
                Ts_, Ws_ = float(nominal_ts[i]), float(nominal_ws[i])
            elif i % every == 0:
                Ts_, Ws_, _ = evaporative_outlet(T_in, rel_humidity(T_in, W_in), sysm.eps)
                Ts_, Ws_ = float(Ts_), float(Ws_)
        if sysm.control == "demand" and sysm.kind in ("fan", "evap"):
            rh_now = float(rel_humidity(T, W))
            if rh_now >= sysm.rh_stop:
                wet_enabled = False
            elif rh_now <= sysm.rh_resume:
                wet_enabled = True
            if i % every == 0:
                vin = max(0.3, 0.5 * v_o[i] * np.mean([st.open_track, st.open_back, st.open_ends]))
                mrt_now = st.openness * (T_o[i] + st.dR_shade) + (1 - st.openness) * (T + st.dR_inside)
                theta_now = P2A.theta0 / (1 + vin / sysm.jet_speed)
                tp = T + theta_now * (Ts_ - T) if sysm.kind == "evap" else T
                wp = W + theta_now * (Ws_ - W) if sysm.kind == "evap" else W
                u0 = float(utci(T, mrt_now, vin, rh_now))
                u1 = float(utci(tp, mrt_now, np.hypot(vin, sysm.jet_speed), rel_humidity(tp, wp)))
                useful = np.isfinite(u0 + u1) and u0 >= 32 and u1 < u0
            enabled = useful and N[i] > 0 and (wet_enabled or sysm.kind == "fan")
        else:
            enabled = True
        running = bool(requested_on[i] and enabled and sysm.kind != "none")
        on[i] = running
        G_kw = 0.0
        if st.gains:
            glass = ((total_w - open_w) * st.H_open).sum()
            G_kw = (N[i] * 0.075 + st.shgc * glass * st.I_vert * sun[i] * st.solar_to_zone / 1000
                    + st.U_roof * st.area * (T_solair[i] - T) / 1000
                    + lights + (sysm.power_kw if running else 0.0))
        m_people = N[i] * 0.045 / H_FG                      # kg/s, 45 W latent each

        Q_s = T_s = W_s = 0.0
        if sysm.kind == "evap" and running:
            Q_s, T_s, W_s = sysm.airflow, Ts_, Ws_
            out["T_s"][i], out["W_s"][i] = T_s, W_s
            out["water"][i] = RHO * Q_s * (W_s - W_in) * dt         # kg
            out["P"][i] = sysm.power_kw
        elif sysm.kind == "fan" and running:
            out["P"][i] = sysm.power_kw

        a = RHO * CP * (Q_x + Q_s)                                   # kW/K
        if Q_s > 0 and sysm.rating_policy != "uncapped":
            if sysm.rating_policy == "outlet":
                minimum_supply = T_in - sysm.rated_drop
            else:
                # Solve the frozen-flow balance for a bypass supply that
                # bounds both covered and uncovered occupied temperatures.
                v_in = max(0.3, 0.5 * v_o[i] * np.mean([st.open_track, st.open_back, st.open_ends]))
                theta = P2A.theta0 / (1 + v_in / sysm.jet_speed)
                e = np.exp(-dt * a / C)
                coef = (1 - e) * Q_s / (Q_x + Q_s)
                intercept = e * T + (1 - e) * (RHO * CP * Q_x * T_o[i] + G_kw) / a
                target = base["T"][i] - sysm.rated_drop
                minimum_supply = max((target - (1 - theta) * intercept) / (theta + (1 - theta) * coef),
                                     (target - intercept) / coef)
            T_s = min(T_in, max(T_s, minimum_supply))
            W_s = float((enthalpy(T_in, W_in) - CP * T_s) / (2501 + 1.86 * T_s))
            out["T_s"][i], out["W_s"][i] = T_s, W_s
            out["water"][i] = RHO * Q_s * max(W_s - W_in, 0) * dt
        T_eq = (RHO * CP * (Q_x * T_o[i] + Q_s * T_s) + G_kw) / a
        if sysm.kind == "evap" and running and sysm.control == "demand":
            t_next = T_eq + (T - T_eq) * np.exp(-dt * a / C)
            b_test = RHO * (Q_x + Q_s)
            w_eq = (RHO * (Q_x * W_o[i] + Q_s * W_s) + m_people) / b_test
            w_next = w_eq + (W - w_eq) * np.exp(-dt * b_test / M)
            if rel_humidity(t_next, w_next) > sysm.rh_stop:
                # Reject this wet operation before charging water/electricity;
                # re-solve the off-state balance, retaining stored heat/moisture.
                wet_enabled = running = on[i] = False
                Q_s = T_s = W_s = 0.0
                out["P"][i] = out["water"][i] = 0.0
                if st.gains:
                    G_kw -= sysm.power_kw
                a = RHO * CP * Q_x
                T_eq = T_o[i] + G_kw / a
        Q_ac = m_ac = 0.0
        if sysm.kind == "ac" and running:
            share = 1.0 if sysm.low_supply else 0.65                 # mixing also cools the upper hall
            shr = sysm.shr if W > W_coil else 1.0                    # dry air: the coil removes no moisture
            # thermostat: remove enough heat to reach the setpoint by the end of the step
            e = np.exp(-dt * a / C)
            T_eq_target = (sysm.setpoint - T * e) / (1 - e)
            Q_ac = float(np.clip(a * (T_eq - T_eq_target), 0.0, shr * sysm.cap_kw * share))
            T_eq -= Q_ac / a
            if W > W_coil:
                m_ac = Q_ac / share * (1 - shr) / shr / H_FG
            out["P"][i] = (Q_ac / share + m_ac * H_FG) / ac_cop(T_o[i])
        T = T_eq + (T - T_eq) * np.exp(-dt * a / C)

        b = RHO * (Q_x + Q_s)
        W_eq = (RHO * (Q_x * W_o[i] + Q_s * W_s) + m_people - m_ac) / b
        W = W_eq + (W - W_eq) * np.exp(-dt * b / M)

        out["T"][i], out["W"][i], out["Q_x"][i], out["Q_ac"][i] = T, W, Q_x, Q_ac

    out.update(t=th, T_o=T_o, RH_o=RH_o, W_o=W_o, N=N, dwelling=dwelling, v_o=v_o, dt=dt, on=on)
    out["RH"] = rel_humidity(out["T"], out["W"])
    return out


def comfort(st, sysm, sim, base):
    """UTCI of covered and uncovered people, relief versus the no-cooling run.
    Radiant field: the open share of the view sees the outdoors (air + dR_shade),
    the enclosed share sees walls and roof that follow the zone air (+ dR_inside)."""
    open_mean = np.mean([st.open_track, st.open_back, st.open_ends])
    v_in = np.maximum(0.3, 0.5 * sim["v_o"] * open_mean)
    f = st.openness
    mrt = lambda T_zone: f * (sim["T_o"] + st.dR_shade) + (1 - f) * (T_zone + st.dR_inside)  # noqa: E731
    U0 = utci(base["T"], mrt(base["T"]), v_in, base["RH"])
    Tmrt = mrt(sim["T"])
    U_unc = utci(sim["T"], Tmrt, v_in, sim["RH"])
    N = sim["N"]
    if sysm.kind in ("fan", "evap"):
        if sysm.kind == "evap":
            # the jet carries the cooler's outlet air (as simulated) and entrains zone air
            theta = P2A.theta0 / (1 + v_in / sysm.jet_speed)
            Tp = sim["T"] - theta * (sim["T"] - sim["T_s"])
            Wp = sim["W"] + theta * (sim["W_s"] - sim["W"])
        else:
            Tp, Wp = sim["T"], sim["W"]
        vp = np.hypot(v_in, sysm.jet_speed)
        U_cov = utci(Tp, Tmrt, vp, rel_humidity(Tp, Wp))
        if sysm.kind == "fan" and sysm.rating_policy != "uncapped":
            U_cov, vp = rated_fan(Tp, Tmrt, v_in, rel_humidity(Tp, Wp), sysm.jet_speed, U0, sysm.rated_drop)
        U_cov = np.where(sim["on"], U_cov, U_unc)
        Tp = np.where(sim["on"], Tp, sim["T"])
        Wp = np.where(sim["on"], Wp, sim["W"])
        n_cov = np.minimum(N, sysm.cover)
    else:
        U_cov = U_unc
        n_cov = np.zeros_like(N)
        Tp, Wp, vp = sim["T"], sim["W"], v_in
    D0 = stress_dose(U0, P2A.weights)
    benefit = (np.where(n_cov > 0, n_cov * (D0 - stress_dose(U_cov, P2A.weights)), 0)
               + np.where(N > n_cov, (N - n_cov) * (D0 - stress_dose(U_unc, P2A.weights)), 0))
    valid0 = np.isfinite(U0)
    valid1 = ((n_cov == 0) | np.isfinite(U_cov)) & ((N == n_cov) | np.isfinite(U_unc))
    valid = valid0 & valid1
    # A missing UTCI must never be counted as a safe person-hour. Nor may an
    # incomplete day be silently rescaled to a full-day efficiency.
    benefit = np.where(N == 0, 0.0, np.where(valid, benefit, np.nan))
    hot0 = np.where(N == 0, 0.0, np.where(valid0, N * (U0 >= 38), np.nan))
    hot1 = np.where(N == 0, 0.0, np.where(valid1,
                    n_cov * (U_cov >= 38) + (N - n_cov) * (U_unc >= 38), np.nan))
    return dict(U0=U0, U_unc=U_unc, U_cov=U_cov, benefit=benefit, hot0=hot0, hot1=hot1,
                valid=valid, T_person=Tp, RH_person=rel_humidity(Tp, Wp), v_person=vp)


def fan_schedule(st, sysm, climate, base):
    """Smart fan control as in 2a: run an hour only if, averaged over that hour,
    heat stress is at least strong and the fan lowers covered people's stress."""
    sim = simulate(st, sysm, climate)
    cf = comfort(st, sysm, sim, base)
    gain = stress_dose(cf["U0"], P2A.weights) - stress_dose(cf["U_cov"], P2A.weights)
    hour = np.floor(sim["t"]).astype(int)
    on = np.zeros_like(sim["t"], dtype=bool)
    for h in np.unique(hour):
        k = hour == h
        on[k] = (cf["U0"][k].mean() >= 32) and (gain[k].mean() > 0)
    return on


def run(st, sysm, climate, base=None):
    if base is None and sysm.kind != "none":
        base = simulate(st, systems()[0], climate)
    sim = simulate(st, sysm, climate, base=base)
    if base is None:
        base = sim
    cf = comfort(st, sysm, sim, base)
    rep = sim["t"] >= 6.0
    h = sim["dt"] / 3600
    elec = sim["P"][rep].sum() * h
    water = sim["water"][rep].sum()
    resource = elec + E_WATER[climate] * water / 1000
    relief = cf["benefit"][rep].sum() * h
    invalid = rep & ~cf["valid"] & (sim["N"] > 0)
    pm = rep & (sim["t"] >= 14.5) & (sim["t"] < 15.5)
    rating_drop = cf["U0"] - cf["U_cov"] if sysm.kind == "fan" else base["T"] - cf["T_person"]
    return dict(
        scenario=st.name, system=sysm.name, climate=climate,
        control=sysm.control,
        rating_policy=sysm.rating_policy,
        rating_exceed_hours=round(float((rep & (rating_drop > sysm.rated_drop + 1e-5)).sum() * h), 3),
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
        hours_on=round(float(sim["on"][rep].sum() * h), 3),
        powered_hours_RH_over_65=round(float((rep & sim["on"] & (sim["RH"] > 65 + 1e-6)).sum() * h), 3),
        passenger_h=round(float(sim["N"][rep].sum() * h), 1),
        utci_invalid_hours=round(float(invalid.sum() * h), 3),
        utci_invalid_person_h=round(float(sim["N"][invalid].sum() * h), 3),
        full_day_supported=bool(not invalid.any()),
    ), sim, cf
