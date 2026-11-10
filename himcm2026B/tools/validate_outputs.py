"""Artifact-level invariants: fail on unsupported rankings or stale semantics."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def main():
    numerical=[('stage1/outputs/tableS0_checks.csv','passed'),('stage2/outputs/table0_validation.csv','pass'),
               ('stage2b/outputs/table2b_0_validation.csv','pass')]
    count=0
    for path,col in numerical:
        t=pd.read_csv(ROOT/path)
        assert t[col].all(),f'Failed numerical check: {path}'
        count+=len(t)
    for path in ['stage2/outputs/table2_design_days.csv','stage2b/outputs/table2b_2_scenarios.csv',
                 'stage2b/outputs/table2b_9_controls.csv','venues/outputs/venue_results.csv',
                 'venues/outputs/venue_scaling.csv','analysis/outputs/actual_day_station_results.csv']:
        t=pd.read_csv(ROOT/path);eta='eta_day' if 'eta_day' in t else 'eta'
        assert t.loc[~t.full_day_supported,eta].isna().all(),f'Unsupported result ranked: {path}'
        assert t.loc[~t.full_day_supported,'relief_person_degC_h'].isna().all(),path
        if 'rating_supported' in t:
            assert (~t.loc[(t.rating_policy=='occupied')&(t.rating_exceed_hours>0),'rating_supported']).all(),path
        if 'powered_hours_RH_over_65' in t:
            evap=t.system.str.contains('Evap|evap')&(t.control=='demand')
            assert (t.loc[evap,'powered_hours_RH_over_65']==0).all(),path
    b=pd.read_csv(ROOT/'stage2b/outputs/table2b_8_shelter_bridge.csv')
    f=b[b.device=='A Fan'];assert np.all(abs(f.eta_2a_spot-f.eta_2b_zone_and_jet)<.01)
    q=pd.read_csv(ROOT/'analysis/outputs/weather_quality.csv')
    assert len(q)==50 and q.complete_24h.sum()==45
    v=pd.read_csv(ROOT/'venues/outputs/venue_results.csv')
    assert len(v)==20 and v.venue_id.nunique()==2 and v.full_day_supported.all()
    assert (v.loc[v.resource_kWh==0,'eta'].isna()).all()
    cost=pd.read_csv(ROOT/'venues/outputs/venue_tradeoffs.csv')
    assert (cost.annual_cost_USD>=0).all()
    old=['fig7_cooling_fate.png','fig11_2a_model_error.png']
    assert not any(p.name in old for p in ROOT.rglob('*.png')),'Obsolete figure retained'
    result={'numerical_checks_passed':count,'artifact_invariants':'passed','complete_actual_weather_days':45,
            'venue_scenarios':20,'limitations':'Numerical and bookkeeping checks do not establish field accuracy.'}
    (ROOT/'analysis/outputs/validation_summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
