"""Sensitivity to explicit AC supply fraction and actual hot-day weather.

All selected days are retained when complete. Missing-weather days are listed,
not filled using a typical day. This is a weather robustness check, not a new
calibration or a probability forecast.
"""
import sys
from dataclasses import replace
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / x) for x in ("stage2", "stage2b", "data/weather")]
from hot_days import load, STATIONS, V10_TO_PED
from model import Params, devices_for, evaluate, mean_waiting, E_WATER
from psychro import p_ws
from run_stage2 import ridership, HOURS, CLIMATES
from station import run, station, systems


def actual_days():
    profiles, qc, rows, station_rows = [], [], [], []
    p = Params()
    devs = devices_for(p)
    for code, (climate, tz) in STATIONS.items():
        raw = load(code, tz)
        max_t = raw.groupby("date")["T"].max()
        threshold = max_t.quantile(.9)
        selected = max_t[max_t >= threshold].index
        complete = []
        for date in selected:
            g = raw[raw.date == date].groupby("hour").agg(T=("T", "mean"), Td=("Td", "mean"), v10=("v10", "mean")).reindex(range(24))
            ok = bool(g.notna().all().all())
            qc.append(dict(station=code, date=str(date), threshold_C=threshold, complete_24h=ok))
            if not ok:
                continue
            g["v_ped"] = g.v10 * V10_TO_PED
            g["hour"] = g.index
            key = f"{code} {date}"
            CLIMATES[key] = g
            E_WATER[key] = E_WATER[climate]
            profiles.extend(dict(station=code, date=str(date), **r) for r in g.to_dict("records"))
            complete.append((key, float(g["T"].max())))
            x = np.r_[g.hour.values + 52/60, 24 + 52/60]
            hh = np.mod(HOURS-x[0],24)+x[0]
            interp = lambda col: np.interp(hh, x, np.r_[g[col].values,g[col].iloc[0]])
            T, Td, v = interp("T"), interp("Td"), interp("v_ped")
            rh = np.minimum(100*p_ws(Td)/p_ws(T),100)
            n = mean_waiting(*ridership(HOURS))
            for d in devs:
                r = evaluate(d,T,rh,v,n,replace(p,e_water=E_WATER[climate]),hour=HOURS)
                valid = np.isfinite(r["U0"]) & np.isfinite(r["U1"])
                enabled = (r["U0"]>=32)&(r["relief"]>0)&valid
                resource = np.sum(r["resource_kw"]*enabled*(1-np.exp(-n)))
                relief = np.sum(np.where(enabled,r["n_ben"]*r["relief"],0))
                rows.append(dict(station=code,date=str(date),device=d.name,weather="observed individual hot day",
                                 full_day_supported=bool(valid.all()),invalid_hours=int((~valid).sum()),
                                 eta=relief/resource if valid.all() and resource>0 else np.nan,
                                 relief=relief if valid.all() else np.nan,resource_kWh=resource))
        # A declared deterministic stress subset of five actual days, ordered
        # by daily maximum temperature; choose evenly across that ordering.
        complete.sort(key=lambda x:x[1])
        take = sorted(set(np.linspace(0,len(complete)-1,min(5,len(complete)),dtype=int)))
        for j in take:
            key, _ = complete[j]
            for dev in systems()[1:4]:
                result = run(station("Platform screen doors"),replace(dev,control="demand"),key)[0]
                station_rows.append(dict(result, weather_station=code, date=key.split()[1]))
        for key,_ in complete:
            del CLIMATES[key]
            del E_WATER[key]
    out = ROOT / "analysis/outputs"
    out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(profiles).to_csv(ROOT / "data/weather/actual_hot_days.csv",index=False)
    pd.DataFrame(qc).to_csv(out / "weather_quality.csv",index=False)
    df = pd.DataFrame(rows)
    df.to_csv(out / "actual_day_bus_results.csv",index=False)
    pd.DataFrame(station_rows).to_csv(out / "actual_day_station_results.csv",index=False)
    summaries=[]
    for (code,device),g in df.groupby(["station","device"]):
        good=g[g.full_day_supported]
        ranked=df[df.station==code].pivot(index="date",columns="device",values="eta").dropna()
        winners=ranked.idxmax(axis=1)
        summaries.append(dict(station=code,device=device,days_total=len(g),days_supported=len(good),
                              eta_p10=good.eta.quantile(.1),eta_median=good.eta.median(),eta_p90=good.eta.quantile(.9),
                              supported_comparable_days=len(ranked),rank1_days=int((winners==device).sum())))
    summary=pd.DataFrame(summaries)
    summary.to_csv(out / "actual_day_summary.csv",index=False)
    print(summary.round(2).to_string(index=False))
    print(f"Weather QA: {sum(x['complete_24h'] for x in qc)}/{len(qc)} selected days complete")


if __name__ == "__main__":
    actual_days()
