"""Build measured July design-day profiles from ASOS airport observations.

Source: Iowa Environmental Mesonet ASOS archive (routine hourly METARs),
stations PHX (Phoenix Sky Harbor) and IAH (Houston Bush Intercontinental),
July 2020-2024.

"Hot day" profile: hour-by-hour mean over the July days whose daily maximum
is at or above the 90th percentile of July daily maxima (the hottest ~10 %
of July days). Wind is converted from 10 m to pedestrian height (1.1 m) with
the same log profile used in the model (factor 1/1.47).
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
STATIONS = {"PHX": ("Hot-dry (Phoenix-like)", "Etc/GMT+7"),      # MST all year
            "IAH": ("Hot-humid (Houston-like)", "America/Chicago")}
KT = 0.514444
V10_TO_PED = np.log(1.1 / 0.01) / np.log(10 / 0.01)


def load(st, tz):
    df = pd.read_csv(os.path.join(HERE, f"{st}_raw.csv"), na_values="M")
    df["t"] = pd.to_datetime(df.valid, utc=True).dt.tz_convert(tz)
    df = df.dropna(subset=["tmpf", "dwpf"])
    df["T"] = (df.tmpf - 32) / 1.8
    df["Td"] = (df.dwpf - 32) / 1.8
    df["v10"] = df.sknt * KT
    df["date"] = df.t.dt.date
    df["hour"] = df.t.dt.hour
    return df[df.t.dt.month == 7]


def profiles():
    rows, summ = [], []
    for st, (label, tz) in STATIONS.items():
        d = load(st, tz)
        dmax = d.groupby("date")["T"].max()
        thr = dmax.quantile(0.9)
        hot = dmax[dmax >= thr].index
        for name, sel in (("July mean", d), ("July hot days (top 10%)", d[d.date.isin(hot)])):
            h = sel.groupby("hour").agg(T=("T", "mean"), Td=("Td", "mean"), v10=("v10", "mean"))
            h["v_ped"] = h.v10 * V10_TO_PED
            for hr, r in h.iterrows():
                rows.append(dict(station=st, climate=label, profile=name, hour=hr, T=round(r["T"], 2),
                                 Td=round(r.Td, 2), v10=round(r.v10, 2), v_ped=round(r.v_ped, 2)))
            summ.append(dict(station=st, climate=label, profile=name, days=sel.date.nunique(),
                             Tmax=round(h["T"].max(), 1), Tmin=round(h["T"].min(), 1),
                             hour_of_max=int(h["T"].idxmax()),
                             Td_mean=round(h.Td.mean(), 1), Td_at_max=round(h.Td.loc[h["T"].idxmax()], 1),
                             v10_mean_06_22=round(h.v10.loc[6:21].mean(), 2),
                             v_ped_mean_06_22=round(h.v_ped.loc[6:21].mean(), 2),
                             hot_threshold=round(thr, 1)))
    prof = pd.DataFrame(rows)
    prof.to_csv(os.path.join(HERE, "july_profiles.csv"), index=False)
    s = pd.DataFrame(summ)
    s.to_csv(os.path.join(HERE, "july_summary.csv"), index=False)
    return prof, s


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    prof, s = profiles()
    print(s.to_string(index=False))
