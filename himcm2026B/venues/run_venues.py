"""Q3: explicitly hypothetical interventions at two documented real venues."""
import json
import sys
from dataclasses import replace
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"stage2"),str(ROOT/"stage2b")]
from station import Station, System, simulate, run, comfort, P2A, DT, T_START, T_END
from model import devices_for, eps_of, stress_dose
from plotstyle import plt

OUT=ROOT/"venues/outputs"


def candidates():
    result=[(System("No added equipment","none"), 0, 0.0)]
    for d,qty in zip(devices_for(P2A),(6,4,3)):
        for ctrl in ("always","demand"):
            s=System(f"{d.name} ×{qty} / {ctrl}",d.kind,d.power_kw*qty,d.airflow*qty,
                     eps_of(d,P2A),d.jet_speed,d.airflow*qty/P2A.q_per_person,
                     rated_drop=d.rated_drop,control=ctrl)
            result.append((s,qty,0.0))
    result.append((System("AC 15 kW / thermostat","ac",cap_kw=15.,supply_share=.65),1,0.0))
    result.append((System("Improved shade only","none"),0,1.0))
    # Combined passive + active option shares the original shade-only baseline.
    a=next(x for x in result if x[0].name.startswith("A Fan") and x[0].control=="demand")
    result.append((replace(a[0],name="Improved shade + A / demand"),a[1],1.0))
    return result


def evaluate_case(case, people_scale=1.0, area_scale=1.0):
    th=np.arange(T_START*3600,T_END*3600,DT)/3600
    hours=(case["start_hour"],case["end_hour"])
    active=(th>=hours[0])&(th<hours[1])
    N=np.where(active,case["people"]*people_scale,0.)
    kw={k:case[k] for k in ("L","D","Hz","H_open","open_track","open_back","open_ends")}
    kw["L"]*=area_scale
    st=Station(name=case["name"],**kw,dynamic=False,kappa_train=0.,lights_W_m2=0.,shgc=0.,U_roof=.5)
    no=System("No added equipment","none")
    base=simulate(st,no,case["climate"],n_const=N)
    ref=comfort(st,no,base,base)["U0"]
    rows=[]
    for system,qty,shade in candidates():
        st_now=replace(st,dR_shade=6.) if shade else st
        r,sim,cf=run(st_now,system,case["climate"],base=base,n_const=N,report_hours=hours,enable=active)
        adjustment=N*(stress_dose(ref,P2A.weights)-stress_dose(cf["U0"],P2A.weights))
        valid=np.isfinite(ref[active]).all() and r["full_day_supported"]
        total=float((cf["benefit"]+adjustment)[active].sum()*DT/3600) if valid else np.nan
        r.update(venue_id=case["id"],system_kind=system.kind,units=qty,shade_upgrade=bool(shade),
                 area_m2=st.area,people=case["people"]*people_scale,study_hours=hours[1]-hours[0],
                 relief_person_degC_h=total,
                 person_h_UTCI38_before=float((N[active]*(ref[active]>=38)).sum()*DT/3600) if valid else np.nan,
                 eta=total/r["resource_kWh"] if valid and r["resource_kWh"]>0 else np.nan,
                 full_day_supported=bool(valid),people_scale=people_scale,area_scale=area_scale)
        rows.append(r)
    return rows


def main():
    cases=json.loads((ROOT/"venues/cases.json").read_text())
    rows=[]
    for case in cases:
        rows.extend(evaluate_case(case))
    df=pd.DataFrame(rows)
    df.to_csv(OUT/"venue_results.csv",index=False)
    # Scale people and area together, keeping equipment fixed: explicitly
    # demonstrates capacity saturation instead of assuming linear scaling.
    scaled=[]
    for case in cases:
        for scale in (.5,2.):
            scaled.extend(evaluate_case(case,people_scale=scale,area_scale=scale))
    pd.DataFrame(scaled).to_csv(OUT/"venue_scaling.csv",index=False)
    draw(df,cases)
    print(df[["venue_id","system","electricity_kWh","water_L","relief_person_degC_h","eta","person_h_UTCI38_after"]].round(2).to_string(index=False))


def draw(df,cases):
    fig,axes=plt.subplots(1,2,figsize=(10,4.1))
    for ax,case in zip(axes,cases):
        d=df[(df.venue_id==case["id"]) & ~df.system.str.endswith("/ always")]
        ax.scatter(d.electricity_kWh,d.relief_person_degC_h,c=d.water_L,cmap="viridis",s=45)
        for _,r in d.iterrows():
            if r.system in ("No added equipment","Improved shade only") or "/ demand" in r.system:
                label = ("S+A" if r.shade_upgrade and r.system_kind=="fan" else "Shade" if r.shade_upgrade else
                         "None" if r.system_kind=="none" else r.system[0])
                offset = (5, -12) if label=="Shade" else (5, 5)
                ax.annotate(label,(r.electricity_kWh,r.relief_person_degC_h),fontsize=8,xytext=offset,textcoords="offset points")
        ax.set_title(case["id"].replace("_"," ").title())
        ax.margins(x=.15, y=.15)
        ax.set_xlabel("Electricity during study window (kWh)")
        ax.set_ylabel("Weighted relief (person·°C·h)")
    fig.suptitle("Named-venue study patches: demand control; S+A = improved shade + fan")
    fig.tight_layout()
    fig.savefig(OUT/"venue_relief.png",dpi=180)
    plt.close(fig)


if __name__=="__main__":
    main()
