"""HiMCM 2026 Problem B, requirement 2a: cooling efficiency of an open-sided
bus-stop shelter.

Chain of sub-models (each maps to one subsection of the paper):
  M1 climate + moist air   -> psychro.py
  M2 device physics        -> what the device does to the air it handles
  M3 delivery / dilution   -> how much of that reaches the people (open sides!)
  M4 occupancy             -> how many people are there to benefit (Little's law)
  M5 thermal comfort       -> UTCI, one common "felt temperature" for fans and coolers
  M6 useful relief and efficiency
       eta = (people benefiting x heat-stress relief) / electric power
       unit: person * degC * h per kWh

Every number in PARAMS is an assumption or an estimate; the plan document
lists its reason and the range used in the sensitivity analysis.
"""
from dataclasses import dataclass, replace
import warnings
import numpy as np
from pythermalcomfort.models import utci as _utci

from psychro import humidity_ratio, rel_humidity, evaporative_outlet, wet_bulb

RHO = 1.16    # kg/m3, air density near 30-40 degC
CP = 1.006    # kJ/(kg K)
G = 9.81


# --------------------------------------------------------------------------
# Parameters
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Device:
    name: str
    kind: str          # "fan" or "evap"
    power_kw: float    # electric power while running
    rated_drop: float  # degC, the "up to" value in the problem table
    airflow: float     # m3/s handled by the device
    jet_speed: float   # m/s air speed the device produces at a covered person


@dataclass(frozen=True)
class Params:
    # --- M2 device rating interpretation ---
    D_ref: float = 10.0        # degC, wet-bulb depression at which "up to" values hold
    rating_policy: str = "occupied"  # occupied (main), outlet (alternative), uncapped (diagnostic)
    fan_ref_T: float = 30.0    # degC, condition at which the fan "feels 3 degC cooler"
    fan_ref_RH: float = 50.0
    q_per_person: float = 0.8  # m3/s of device airflow needed per covered person
    # --- M3 shelter and delivery ---
    L: float = 6.0             # m, shelter length
    D: float = 1.8             # m, depth
    H: float = 2.5             # m, height of open sides
    Hz: float = 2.0            # m, occupied-zone height
    C_w: float = 0.3           # wind-driven exchange coefficient
    Cd: float = 0.6            # discharge coefficient (buoyant spill of cool air)
    shelter_factor: float = 0.5  # wind speed inside / outside
    theta0: float = 0.7        # share of jet air (vs entrained ambient air) at a person, calm
    dR_shade: float = 12.0     # degC, mean radiant temp. above air temp. under the shelter roof:
                               # sun ~+28 C (Middel & Krayenhoff 2019) minus ~15 C shelter cooling (Tucson MaRTy)
    # --- M4 occupancy ---
    q_person_W: float = 75.0   # W sensible heat per standing person
    capacity: int = 16         # people who fit under the roof
    # --- M6 heat-stress weights for UTCI bands >=26, >=32, >=38, >=46 ---
    weights: tuple = (1.0, 2.0, 3.0, 4.0)
    # --- resources (Requirement 1: count every input) ---
    e_water: float = 0.53      # kWh/m3: US water supply ~2,000 kWh per million gallons (ACEEE 2009);
                               # city-specific values in E_WATER
    # --- zero-energy design levers ---
    dR_sun: float = 30.0       # degC, mean radiant temp. above air temp. in full sun


# Airflow per kW from commercial evaporative-cooler data sheets:
# 18,000 m3/h at 1.1 kW, 25,000 m3/h at 2.2 kW, 30,000 m3/h at 3.0 kW.
DEVICES = (
    Device("A Fan", "fan", 0.25, 3.0, 3.2, 2.0),          # jet_speed is calibrated in devices_for()
    Device("B Evap cooler", "evap", 1.2, 5.0, 5.0, 1.5),
    Device("C Large evap cooler", "evap", 2.5, 8.0, 7.5, 2.0),
)

UTCI_BANDS = (26.0, 32.0, 38.0, 46.0)   # Broede et al. 2012 heat-stress categories

# Embedded energy of water by design-day city [kWh/m3]. Phoenix: Central Arizona
# Project conveyance 5.5 kWh/kgal (1.45 kWh/m3) plus city tap-water supply
# ~1.8 kWh/kgal (0.48 kWh/m3), Arroyo 2010. Houston: US average (ACEEE 2009).
E_WATER = {"Hot-dry (Phoenix-like)": 1.93, "Hot-humid (Houston-like)": 0.53}


# --------------------------------------------------------------------------
# M5 comfort: UTCI wrapper
# --------------------------------------------------------------------------
Z0 = 0.01
V10_FACTOR = np.log(10 / Z0) / np.log(1.1 / Z0)   # ~1.47: 1.1 m speed -> 10 m equivalent


def utci(T, Tmrt, v_ped, RH):
    """UTCI [degC]. v_ped is air speed at the person (1.1 m); UTCI expects the
    10 m reference speed, so it is scaled up by the log wind profile."""
    # The 0.5 m/s floor is the UTCI reference convention, not permission to
    # extrapolate at high wind or temperature. Unsupported inputs stay NaN.
    v10 = np.maximum(np.asarray(v_ped, dtype=float) * V10_FACTOR, 0.5)
    # The library enumerates every invalid timestep in its warning. Preserve
    # the NaNs; callers report aggregate invalid hours instead of thousands
    # of duplicate input values. Other warnings and exceptions remain visible.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*outside the applicability limits.*", category=UserWarning)
        out = _utci(tdb=T, tr=Tmrt, v=v10, rh=RH, limit_inputs=True, round_output=False)
    return np.asarray(out.utci, dtype=float)


def stress_dose(U, weights):
    """Weighted heat-stress dose D(U) = integral_26^U w(u) du."""
    U = np.asarray(U, dtype=float)
    edges = list(UTCI_BANDS) + [np.inf]
    d = np.zeros_like(U)
    for k, w in enumerate(weights):
        d += w * np.clip(U - edges[k], 0, edges[k + 1] - edges[k])
    return d


def stress_band(U):
    return np.digitize(U, UTCI_BANDS)   # 0 none, 1 moderate, 2 strong, 3 very strong, 4 extreme


# --------------------------------------------------------------------------
# M2 device calibration
# --------------------------------------------------------------------------
def eps_of(dev, p):
    """Evaporative saturation effectiveness implied by the 'up to' rating."""
    return dev.rated_drop / p.D_ref


def calibrate_fan_speed(p, v_in=0.3):
    """Air speed at the person such that the fan lowers UTCI by its rated 3 degC
    at the reference condition (shaded, light wind)."""
    T, RH = p.fan_ref_T, p.fan_ref_RH
    Tmrt = T + p.dR_shade
    U0 = utci(T, Tmrt, v_in, RH)
    lo, hi = v_in, 6.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if U0 - utci(T, Tmrt, np.hypot(v_in, mid), RH) < DEVICES[0].rated_drop:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def devices_for(p):
    fan_u = calibrate_fan_speed(p)
    return tuple(replace(d, jet_speed=fan_u) if d.kind == "fan" else d for d in DEVICES)


def rated_fan(T, mrt, v_in, RH, jet, baseline, rating):
    """Ideal speed modulation to the occupied-location UTCI rating.

    Full rated electric power is charged even when speed is reduced; no
    unmeasured fan power curve is invented. Harmful fan effects are retained.
    This is a performance-envelope assumption, not physiological calibration.
    """
    raw_v = np.hypot(v_in, jet)
    raw = utci(T, mrt, raw_v, RH)
    active = np.isfinite(raw) & (baseline - raw > rating)
    if not np.any(active):
        return raw, raw_v
    lo = np.zeros_like(raw)
    hi = np.broadcast_to(jet, raw.shape).copy()
    for _ in range(24):
        mid = (lo + hi) / 2
        u = utci(T, mrt, np.hypot(v_in, mid), RH)
        hit = baseline - u > rating
        hi = np.where(hit, mid, hi)
        lo = np.where(hit, lo, mid)
    v = np.where(active, np.hypot(v_in, lo), raw_v)
    return utci(T, mrt, v, RH), v


# --------------------------------------------------------------------------
# M3 delivery: volume mode (cool the whole shelter) vs spot mode (aim at people)
# --------------------------------------------------------------------------
def volume_mode_zone(T, W, T_s, W_s, Qs, v_w, n_people, p, iters=40):
    """Well-mixed occupied zone. Ambient air enters by wind (Q_wind) and by the
    buoyant spill of cool air out of the open sides (Q_buoy, the 'open freezer'
    effect); the two are combined in quadrature as in ASHRAE infiltration
    models. Solved by fixed-point iteration because Q_buoy depends on the
    temperature difference it produces."""
    T = np.asarray(T, float)
    Q_wind = p.C_w * (p.L * p.H) * np.asarray(v_w, float)
    W_open = p.L + 2 * p.D
    Tz = T - 0.5 * (T - T_s)
    for _ in range(iters):
        dT = np.maximum(T - Tz, 0.0)
        Q_buoy = p.Cd / 3 * W_open * np.sqrt(G * p.Hz ** 3 * dT / (T + 273.15))
        Q_inf = np.hypot(Q_wind, Q_buoy)
        phi = Qs / (Qs + Q_inf)
        gain = n_people * p.q_person_W / 1000 / (RHO * CP * (Qs + Q_inf))
        Tz_new = phi * T_s + (1 - phi) * T + gain
        Tz = 0.5 * Tz + 0.5 * Tz_new
    Wz = phi * W_s + (1 - phi) * W
    return Tz, Wz, phi, Q_inf


def spot_mode_person(T, W, T_s, W_s, v_in, jet_speed, p):
    """Jet aimed at the waiting area. Air reaching a covered person is a mix of
    cooled jet air (share theta) and entrained ambient air; cross-wind bends
    and dilutes the jet, reducing theta."""
    theta = p.theta0 / (1 + np.asarray(v_in, float) / jet_speed)
    return T - theta * (T - T_s), W + theta * (W_s - W), theta


# --------------------------------------------------------------------------
# M4 occupancy
# --------------------------------------------------------------------------
def expected_min(n_mean, cap, kmax=80):
    """E[min(N, cap)] for a Poisson number of waiting people N with mean
    n_mean. Using min(E[N], cap) instead overstates the people a small device
    covers, because crowds above its capacity are cut off."""
    n = np.asarray(n_mean, float)
    pmf = np.exp(-n)
    out = np.zeros_like(n)
    for k in range(kmax):
        out += pmf * np.minimum(k, cap)
        pmf = pmf * n / (k + 1)
    return out


def mean_waiting(arrivals_per_h, headway_min, headway_cv=0.5):
    """Little's law: N = lambda * W_q. With random passenger arrivals the mean
    wait is (h/2)(1 + CV^2) (the 'inspection paradox' for irregular buses)."""
    wait_h = headway_min / 60 / 2 * (1 + headway_cv ** 2)
    return arrivals_per_h * wait_h


# --------------------------------------------------------------------------
# M6 evaluation for one device in one condition
# --------------------------------------------------------------------------
def evaluate(dev, T, RH, v_w, n_mean, p, mode="spot"):
    """Return a dict of arrays (broadcast over T, RH, v_w, n_mean)."""
    T, RH, v_w, n_mean = np.broadcast_arrays(*(np.asarray(x, float) for x in (T, RH, v_w, n_mean)))
    W = humidity_ratio(T, RH)
    Tmrt = T + p.dR_shade
    v_in = np.maximum(p.shelter_factor * v_w, 0.3)
    U0 = utci(T, Tmrt, v_in, RH)
    n_in = expected_min(n_mean, p.capacity)          # people under the roof
    cap = dev.airflow / p.q_per_person
    n_cov = expected_min(n_mean, min(cap, p.capacity))   # people a jet can cover

    if dev.kind == "fan":
        Tp, Wp = T, W
        vp = np.hypot(v_in, dev.jet_speed)
        n_ben = n_cov
        gross_kw = np.zeros_like(T)
        water_lph = np.zeros_like(T)
        share = np.ones_like(T)
    else:
        eps = eps_of(dev, p)
        if p.rating_policy not in ("occupied", "outlet", "uncapped"):
            raise ValueError("Unknown rating_policy")
        if p.rating_policy == "outlet":
            eps = np.minimum(eps, dev.rated_drop / np.maximum(T - wet_bulb(T, RH), 1e-9))
        elif p.rating_policy == "occupied" and mode == "spot":
            theta = p.theta0 / (1 + v_in / dev.jet_speed)
            eps = np.minimum(eps, dev.rated_drop / np.maximum(theta * (T - wet_bulb(T, RH)), 1e-9))
        T_s, W_s, _ = evaporative_outlet(T, RH, eps)
        if p.rating_policy == "occupied" and mode != "spot":
            # Bypass modulation is solved through the zone balance, so water
            # and sensible cooling use the same supply condition as comfort.
            test_T = volume_mode_zone(T, W, T_s, W_s, dev.airflow, v_w, n_in, p)[0]
            if np.any(T - test_T > dev.rated_drop):
                lo, hi = np.zeros_like(T), np.broadcast_to(eps, T.shape).copy()
                for _ in range(24):
                    mid = (lo + hi) / 2
                    ts, ws, _ = evaporative_outlet(T, RH, mid)
                    tz = volume_mode_zone(T, W, ts, ws, dev.airflow, v_w, n_in, p)[0]
                    hit = T - tz > dev.rated_drop
                    hi, lo = np.where(hit, mid, hi), np.where(hit, lo, mid)
                T_s, W_s, _ = evaporative_outlet(T, RH, lo)
        gross_kw = RHO * dev.airflow * CP * (T - T_s)                     # sensible cooling made
        water_lph = RHO * dev.airflow * (W_s - W) * 3600                   # kg/h ~ L/h
        if mode == "spot":
            Tp, Wp, share = spot_mode_person(T, W, T_s, W_s, v_in, dev.jet_speed, p)
            vp = np.hypot(v_in, dev.jet_speed)
            n_ben = n_cov
        else:
            Tp, Wp, share, _ = volume_mode_zone(T, W, T_s, W_s, dev.airflow, v_w, n_in, p)
            vp = v_in
            n_ben = n_in
    RHp = rel_humidity(Tp, Wp)
    U1 = utci(Tp, Tmrt, vp, RHp)   # radiant field is not changed by the device
    if dev.kind == "fan" and p.rating_policy != "uncapped":
        U1, vp = rated_fan(Tp, Tmrt, v_in, RHp, dev.jet_speed, U0, dev.rated_drop)
    relief = stress_dose(U0, p.weights) - stress_dose(U1, p.weights)
    eff_drop = np.maximum(U0, 26) - np.maximum(U1, 26)
    resource_kw = dev.power_kw + p.e_water * water_lph / 1000
    eta = n_ben * relief / resource_kw
    # where the cooling goes (spot mode): aimed at people and received, diluted
    # by entrained air on the way, or aimed at places where nobody stands
    aimed = np.minimum(n_ben / cap, 1.0)
    return dict(U0=U0, U1=U1, dU=U0 - U1, eff_drop=eff_drop, relief=relief,
                n_ben=n_ben, eta=eta, resource_kw=resource_kw, T_person=Tp, RH_person=RHp,
                v_person=vp, share=share, gross_kw=gross_kw, gross_cop=gross_kw / dev.power_kw,
                water_lph=water_lph, capture_index=aimed * share,
                mixing_index=aimed * (1 - share), unused_index=1 - aimed)


def sun_factor(hour):
    """Relative solar exposure over a summer day: 0 before 05:30 and after
    20:00, 1 at solar noon (~12:45)."""
    return np.clip(np.sin(np.pi * (np.asarray(hour, float) - 5.5) / 14.5), 0, None)


def shade_relief(T, RH, v_w, hour, p):
    """Heat-stress relief per person from standing under the shelter roof
    instead of in the sun (zero energy)."""
    T, RH, v_w = np.broadcast_arrays(*(np.asarray(x, float) for x in (T, RH, v_w)))
    U_sun = utci(T, T + p.dR_shade + (p.dR_sun - p.dR_shade) * sun_factor(hour), v_w, RH)
    U_shade = utci(T, T + p.dR_shade, np.maximum(p.shelter_factor * v_w, 0.3), RH)
    return U_sun, U_shade, stress_dose(U_sun, p.weights) - stress_dose(U_shade, p.weights)
