"""Bounded CPC3 comparator discovery, controls and frozen reserved variations."""
from pathlib import Path
import argparse,json,sys,time


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);args=ap.parse_args()
    root=Path(args.root).resolve();sys.path.insert(0,str(root/'src'))
    from core.comparison import run_comparison
    out=root/'experimentos/comparacion_seleccion/resultados';out.mkdir(parents=True,exist_ok=True)
    cases=[
        ('equal_positive',dict(expected=1,consequence=1)),
        ('equal_negative',dict(expected=-1,consequence=-1)),
        ('positive_discrepancy',dict(expected=1,consequence=-1)),
        ('negative_discrepancy',dict(expected=-1,consequence=1)),
        ('same_sum_equal',dict(expected=1,consequence=1,loads=(65,65))),
        ('same_sum_unequal',dict(expected=1,consequence=-1,loads=(30,100))),
        ('expectation_omitted',dict(expected=1,consequence=1,omit='expectation')),
        ('consequence_omitted',dict(expected=1,consequence=1,omit='consequence')),
        ('one_tick_miss',dict(expected=1,consequence=-1,phase_miss=1)),
        ('branch_equal',dict(expected=1,consequence=1,context_payloads={'equal':7,'higher':11,'lower':13})),
        ('branch_discrepancy',dict(expected=1,consequence=-1,context_payloads={'equal':7,'higher':11,'lower':13})),
        ('reserved_translation',dict(expected=-1,consequence=1,hub=(12,14,17),loads=(9,21))),
        ('reserved_timing',dict(expected=1,consequence=1,hub=(31,19,29),arrival_tick=13,
                                 expectation_tick=2,consequence_tick=7,loads=(17,43))),
    ]
    freeze={'method':'directional_complement_v1','cases':[{'id':k,'spec':v} for k,v in cases],
            'reserved':['reserved_translation','reserved_timing'],
            'decoder':'Native product direction x=0 same; +/- mismatch; only when dy=dz=1',
            'invalidity':'Missing participants/timing misses are not automatically assigned an error value',
            'maximum_cases':13,'postT0':'Only declared experience submissions; no RAW/clock edits'}
    (out.parent/'EXPERIMENT_CONFIG.json').write_text(json.dumps(freeze,indent=2),encoding='utf-8')
    start=time.monotonic();results=[]
    for name,spec in cases:
        result=run_comparison(spec,out/name);results.append({'id':name,'meeting':result['meeting'],
             'decoded_relation':result['decoded_relation'],'receipts':result['receipts']})
        print(json.dumps(results[-1]),flush=True)
    summary={'cases':results,'elapsed_seconds':time.monotonic()-start,
             'scope':'Two independently supplied event roles; not yet an integrated native forecast-return loop',
             'cases_count':len(results),'all_cases_completed':True}
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')


if __name__=='__main__':main()
