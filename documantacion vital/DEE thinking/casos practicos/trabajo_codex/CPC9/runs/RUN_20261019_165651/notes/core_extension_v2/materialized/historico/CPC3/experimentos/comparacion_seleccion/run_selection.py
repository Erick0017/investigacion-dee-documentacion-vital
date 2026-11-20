from pathlib import Path
import argparse,json,sys,time


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);a=ap.parse_args()
    root=Path(a.root);sys.path.insert(0,str(root/'src'))
    from habitat.selection import run_case
    out=root/'experimentos/comparacion_seleccion/seleccion';out.mkdir(parents=True,exist_ok=True)
    cases=[('positive_contextQ',dict(expected=1,consequence=-1,context=1)),
           ('negative_contextP',dict(expected=-1,consequence=1,context=0)),
           ('roles_swapped_positive',dict(expected=1,consequence=-1,context=0)),
           ('roles_swapped_negative',dict(expected=-1,consequence=1,context=1)),
           ('equal_positive',dict(expected=1,consequence=1,context=0)),
           ('equal_negative',dict(expected=-1,consequence=-1,context=1)),
           ('expectation_omitted',dict(expected=1,consequence=-1,context=1,omit='expectation')),
           ('consequence_omitted',dict(expected=1,consequence=-1,context=1,omit='consequence')),
           ('common_query_cut',dict(expected=1,consequence=-1,context=1,query_cut=True)),
           ('selected_Q_cut',dict(expected=1,consequence=-1,context=1,source_cut='Q')),
           ('unselected_P_cut',dict(expected=1,consequence=-1,context=1,source_cut='P')),
           ('reserved_Q',dict(expected=1,consequence=-1,context=1,report=41,hub=(14,17,20))),
           ('reserved_P',dict(expected=-1,consequence=1,context=0,report=31,hub=(29,18,11))) ]
    config={'cases':[{'id':k,'spec':v} for k,v in cases],'reservations':['reserved_Q','reserved_P'],
            'source_report':'Native source payload acquired at a physical encounter; uninformative source carries constant5',
            'scope':'Native context-dependent access component, not yet a renewable learned information policy',
            'freeze_before_cases':True}
    (out/'EXPERIMENT_CONFIG.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
    results=[];start=time.monotonic()
    for cid,spec in cases:
        x=run_case(spec,out/cid);results.append({'id':cid,'source_products':x['source_products'],
                                               'context':x['metadata']['context'],'receipts':x['receipts']})
        print(json.dumps(results[-1]),flush=True)
    summary={'cases':results,'elapsed_seconds':time.monotonic()-start,
             'scope':'Comparison state physically controls later access. Reversing utility does not retrain the installed mapping.',
             'all_cases_completed':True}
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')


if __name__=='__main__':main()
