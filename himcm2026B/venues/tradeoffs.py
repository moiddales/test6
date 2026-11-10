"""Q4: life-cycle planning cost and explicit multiobjective comparisons."""
import itertools
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"stage2"))
from plotstyle import plt
OUT=ROOT/"venues/outputs"


def nondominated(objectives):
    """All columns are minimized. Rows with missing values are unranked."""
    a=np.asarray(objectives,float)
    valid=np.isfinite(a).all(axis=1)
    return np.array([bool(valid[i] and not any(valid[j] and np.all(a[j]<=a[i]+1e-9)
                     and np.any(a[j]<a[i]-1e-9) for j in range(len(a)) if j!=i))
                     for i in range(len(a))])


def cost_table(df,p,capital_multiplier=1.,electricity=None,water=None):
    e=p["electricity_per_kWh"] if electricity is None else electricity
    w=p["water_per_m3"] if water is None else water
    r,n=p["discount_rate"],p["life_years"]
    crf=r*(1+r)**n/((1+r)**n-1) if r else 1/n
    result=df.copy()
    cap=[]
    for _,x in result.iterrows():
        key="ac" if x.system_kind=="ac" else "none" if x.system_kind=="none" else "A" if x.system_kind=="fan" else x.system[0]
        c=x.units*p["installed_unit_cost"][key]+int(x.shade_upgrade)*p["shade_upgrade_cost"]
        if x.control=="demand": c+=p["demand_control_cost"]
        cap.append(c*capital_multiplier)
    result["capital_USD"]=cap
    result["annualized_capital_USD"]=result.capital_USD*crf
    result["annual_maintenance_USD"]=result.capital_USD*p["maintenance_fraction_per_year"]
    result["annual_operating_USD"]=p["study_days_per_year"]*(e*result.electricity_kWh+w*result.water_L/1000)
    result["annual_cost_USD"]=result.annualized_capital_USD+result.annual_maintenance_USD+result.annual_operating_USD
    result["residual_exposure_fraction"]=result.person_h_UTCI38_after/result.person_h_UTCI38_before
    result["meets_illustrative_target"]=(result.full_day_supported &
        (result.residual_exposure_fraction<=p["illustrative_residual_exposure_fraction_target"]) &
        ((result.system_kind!="evap")|(result.powered_hours_RH_over_65==0)))
    result["pareto"]=False
    for _,ix in result.groupby("venue_id").groups.items():
        g=result.loc[ix]
        obj=np.column_stack([g.annual_cost_USD,g.resource_kWh,g.water_L,g.person_h_UTCI38_after,-g.relief_person_degC_h])
        result.loc[ix,"pareto"]=nondominated(obj)
    return result


def main():
    p=json.loads((ROOT/"venues/cost_assumptions.json").read_text())
    df=pd.read_csv(OUT/"venue_results.csv")
    base=cost_table(df,p)
    base.to_csv(OUT/"venue_tradeoffs.csv",index=False)
    scenarios=[]
    for e,w,c in itertools.product(p["sensitivity_electricity"],p["sensitivity_water"],p["sensitivity_capital_multiplier"]):
        t=cost_table(df,p,c,e,w)
        for venue,g in t.groupby("venue_id"):
            ok=g[g.meets_illustrative_target]
            best=ok.sort_values("annual_cost_USD").iloc[0] if len(ok) else None
            scenarios.append(dict(venue_id=venue,electricity_USD_kWh=e,water_USD_m3=w,capital_multiplier=c,
                                  least_cost_meeting_target=best.system if best is not None else "No tested option meets target",
                                  annual_cost_USD=float(best.annual_cost_USD) if best is not None else np.nan))
    pd.DataFrame(scenarios).to_csv(OUT/"cost_sensitivity.csv",index=False)
    fig,axes=plt.subplots(1,2,figsize=(10,4.2))
    for ax,(venue,g) in zip(axes,base.groupby("venue_id",sort=False)):
        for _,x in g.iterrows():
            color="#167d8d" if x.pareto else "#c4c7ca"
            ax.scatter(x.annual_cost_USD,x.person_h_UTCI38_after,color=color,s=35+x.water_L/35,alpha=.8,edgecolors="white")
            if x.pareto and (x.control=="demand" or x.system_kind=="none"):
                label="S+A" if x.shade_upgrade and x.system_kind=="fan" else "Shade" if x.shade_upgrade else "None" if x.system_kind=="none" else x.system[0]
                offset=(4,8) if label in ("A","Shade") else (4,-10)
                ax.annotate(label,(x.annual_cost_USD,x.person_h_UTCI38_after),xytext=offset,textcoords="offset points",fontsize=7)
        ax.axhline(g.person_h_UTCI38_before.iloc[0]*p["illustrative_residual_exposure_fraction_target"],ls="--",color="#b56b41",lw=1)
        ax.set_title(venue.replace("_"," ").title());ax.set_xlabel("Illustrative annualized cost (USD)")
        ax.set_ylabel("Residual UTCI ≥38°C exposure (person-hours)");ax.margins(x=.13,y=.2)
    fig.suptitle("Trade-offs: teal = nondominated; bubble area increases with water use")
    fig.tight_layout();fig.savefig(OUT/"venue_tradeoffs.png",dpi=180);plt.close(fig)
    print(base[["venue_id","system","annual_cost_USD","pareto","meets_illustrative_target"]].round(2).to_string(index=False))


if __name__=="__main__":main()
