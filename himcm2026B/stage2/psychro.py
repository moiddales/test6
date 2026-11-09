"""Moist-air (psychrometric) functions at sea-level pressure.

All temperatures in degC, humidity ratio W in kg water / kg dry air,
enthalpy h in kJ / kg dry air. Formulas follow ASHRAE Handbook -
Fundamentals, Ch. 1 (saturation pressure uses the Magnus form, accurate to
well under 1% in the 0-50 degC range used here).
"""
import numpy as np

P_ATM = 101325.0  # Pa
H_FG = 2450.0     # kJ/kg, latent heat of vaporisation near 25-30 degC


def p_ws(T):
    """Saturation vapour pressure over water [Pa]."""
    T = np.asarray(T, dtype=float)
    return 611.2 * np.exp(17.62 * T / (243.12 + T))


def humidity_ratio(T, RH):
    """W from dry-bulb T and relative humidity RH [%]."""
    pw = np.asarray(RH, dtype=float) / 100.0 * p_ws(T)
    return 0.621945 * pw / (P_ATM - pw)


def rel_humidity(T, W):
    """RH [%] from T and W (capped at 100)."""
    W = np.asarray(W, dtype=float)
    pw = W * P_ATM / (0.621945 + W)
    return np.minimum(100.0 * pw / p_ws(T), 100.0)


def enthalpy(T, W):
    return 1.006 * np.asarray(T) + np.asarray(W) * (2501.0 + 1.86 * np.asarray(T))


def dew_point(T, RH):
    """Dew point [degC] by inverting the Magnus formula."""
    g = np.log(np.asarray(RH, dtype=float) / 100.0) + 17.62 * np.asarray(T) / (243.12 + np.asarray(T))
    return 243.12 * g / (17.62 - g)


def wet_bulb(T, RH, iters=60):
    """Thermodynamic wet-bulb temperature by bisection on the ASHRAE
    adiabatic-saturation equation. Vectorised."""
    T = np.asarray(T, dtype=float)
    W = humidity_ratio(T, RH)
    lo = np.full_like(T, -20.0)
    hi = T.copy()
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        Ws = humidity_ratio(mid, 100.0)
        W_mid = ((2501.0 - 2.326 * mid) * Ws - 1.006 * (T - mid)) / (2501.0 + 1.86 * T - 4.186 * mid)
        too_hot = W_mid > W          # guess wet bulb too high
        hi = np.where(too_hot, mid, hi)
        lo = np.where(too_hot, lo, mid)
    return 0.5 * (lo + hi)


def evaporative_outlet(T, RH, eps):
    """Direct evaporative cooler: outlet temperature and humidity ratio.

    T_out = T - eps (T - T_wb); the process is adiabatic, so enthalpy is
    conserved and the outlet humidity ratio follows from h_in = h_out.
    """
    Twb = wet_bulb(T, RH)
    W_in = humidity_ratio(T, RH)
    T_out = T - eps * (T - Twb)
    h = enthalpy(T, W_in)
    W_out = (h - 1.006 * T_out) / (2501.0 + 1.86 * T_out)
    return T_out, W_out, Twb
