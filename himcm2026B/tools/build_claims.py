"""Render the registered numerical results; selectors are deliberate, never fuzzy."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def build():
    claims, schema, lines = [], {}, ["# Registered numerical results", "", "Each number below is tied to one CSV row, column, unit and baseline.", ""]
    def add(id_, csv, where, column, unit, baseline, label, decimals=1):
        t = pd.read_csv(ROOT / csv)
        for k, v in where.items():
            t = t[t[k] == v]
        if len(t) != 1:
            raise ValueError((id_, len(t)))
        v = float(t.iloc[0][column])
        value = f"{v:.{decimals}f}" if pd.notna(v) else "unsupported"
        claims.append(dict(id=id_, csv=csv, where=where, column=column, unit=unit, baseline=baseline,
                           decimals=decimals, document="paper/key_results.md"))
        schema[csv + ":" + column] = dict(unit=unit, baseline=baseline)
        lines.append(f"- {label}: <!-- claim:{id_} -->{value}<!-- /claim --> {unit}.")
    c = "stage2b/outputs/table2b_9_controls.csv"
    for ctrl in ("always", "demand"):
        w = dict(scenario="Platform screen doors", climate="Hot-humid (Houston-like)", system="B Evap ×8", control=ctrl)
        for col, unit, name in [("hours_on", "h", "runtime"), ("electricity_kWh", "kWh", "electricity"),
                                 ("water_L", "L", "water"), ("eta", "person·°C·h/kWh", "weighted relief efficiency"),
                                 ("powered_hours_RH_over_65", "h", "powered RH exceedance")]:
            add(f"humid_b_{ctrl}_{col}", c, w, col, unit, "same uncooled screen-door station; 06–22; weights 1,2,3,4",
                f"Houston-like B / {ctrl}: {name}", 3 if col.endswith("hours_on") else 1)
    c = "stage2/outputs/table2_design_days.csv"
    for clim, prefix in [("Hot-dry (Phoenix-like)", "dry"), ("Hot-humid (Houston-like)", "humid")]:
        for dev in ("A Fan", "B Evap cooler", "C Large evap cooler"):
            add(f"bus_{prefix}_{dev[0]}", c, dict(climate=clim, device=dev, control="smart"), "eta_day",
                "person·°C·h/kWh", "same uncooled shaded bus shelter; 06–22; weights 1,2,3,4", f"{clim} bus {dev} smart efficiency")
    (ROOT / "paper/claims.json").write_text(json.dumps(claims, ensure_ascii=False, indent=2) + "\n")
    (ROOT / "paper/metric_schema.json").write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n")
    (ROOT / "paper/key_results.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    build()
