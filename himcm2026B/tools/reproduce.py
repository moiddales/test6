"""Reproduce model outputs and key claims from committed inputs.

Default runs all 3,000 parameter sets. --verify-only checks existing artifacts;
it does not claim to recompute them. Failure of any step stops the pipeline.
"""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def execute(args,log=None):
    print('Running: '+' '.join(args),flush=True)
    if log:
        with (ROOT/log).open('w') as stream:
            subprocess.run([sys.executable,*args],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
        output = ROOT/log
        output.write_text('\n'.join(line.rstrip() for line in output.read_text().splitlines())+'\n')
    else:subprocess.run([sys.executable,*args],cwd=ROOT,check=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--verify-only',action='store_true');a=ap.parse_args()
    if not a.verify_only:
        for args,log in [(['data/weather/hot_days.py'],'analysis/outputs/weather_profile_log.txt'),
             (['stage1/freezer.py'],'stage1/outputs/freezer_log.txt'),
             (['stage2/run_stage2.py'],'stage2/outputs/run_stage2_log.txt'),
             (['stage2/sensitivity.py'],'stage2/outputs/sensitivity_log.txt'),
             (['stage2b/run_2b.py'],'stage2b/outputs/run_2b_log.txt'),
             (['tools/robustness.py'],'analysis/outputs/robustness_log.txt'),
             (['venues/run_venues.py'],'venues/outputs/venue_log.txt'),
             (['venues/tradeoffs.py'],'venues/outputs/tradeoff_log.txt')]:execute(args,log)
    execute(['-m','unittest','discover','-s','tests','-v'])
    execute(['tools/validate_outputs.py'])
    if not a.verify_only:execute(['tools/build_claims.py'])
    execute(['tools/check_numbers.py'])
    files=[p for p in ROOT.rglob('*') if p.is_file() and ('__pycache__' not in p.parts) and
           (p.suffix=='.py' or p.name.endswith('_raw.csv') or p.name in ('cases.json','cost_assumptions.json','requirements.txt'))]
    provenance={'python':platform.python_version(),'packages':{n:importlib.metadata.version(n) for n in
                ['numpy','pandas','matplotlib','pythermalcomfort','numba','scipy','reportlab','pypdf']},
                'inputs_and_sources_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)},
                'verification_mode':'existing outputs' if a.verify_only else 'full regeneration'}
    (ROOT/'analysis/outputs/reproducibility.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print('Completed. Report publication is pending explicit user approval; this entry point reproduces models and key claims.')


if __name__=='__main__':main()
