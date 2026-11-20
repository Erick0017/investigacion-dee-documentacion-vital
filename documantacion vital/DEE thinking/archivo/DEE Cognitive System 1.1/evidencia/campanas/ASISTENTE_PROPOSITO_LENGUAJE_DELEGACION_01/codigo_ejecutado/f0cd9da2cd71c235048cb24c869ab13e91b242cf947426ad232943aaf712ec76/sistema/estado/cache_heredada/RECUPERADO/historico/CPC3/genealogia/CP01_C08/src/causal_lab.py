"""Reusable external causal panel: deep diagnostic forks, passive signatures."""
import argparse
import json
from pathlib import Path
import dee_thinking as d
from laboratorio import physical,reading,receipt,edit_fork


def compare_panel(snapshot,intervention_site,panel):
    main=d.OrganizationalWorld.load_snapshot(str(snapshot));initial=physical(main)
    cut=edit_fork(main,d.Coordinate(*intervention_site),0,'specified late causal cut');rows=[]
    for test in panel:
        responses={}
        for arm,base in [('intact',main),('cut',cut)]:
            w=base.fork();r=w.probe(test['channel'],test['value'],test['at']);w.run_until(test['read']);o=w.observe(test['view'],test['port']);responses[arm]={'response':reading(o),'receipt':receipt(w.runtime.receipt(r.id)),'future':physical(w)}
        a=responses['intact']['response'];b=responses['cut']['response'];rows.append({'protocol':test,'responses':responses,'load_effect':a['s_reg']-b['s_reg'] if a['active'] and b['active'] else None})
    assert physical(main)==initial,'Diagnostic panel changed MAIN'
    return {'main_state_before_and_after_identical':True,'initial':initial,'intervention':{'site':intervention_site,'field':'RAW','replacement':0,'clock_preserved':True,'modality':'DIAGNOSTIC_FORK'},'panel':rows}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);p.add_argument('--spec',required=True);p.add_argument('--output',required=True);a=p.parse_args();s=json.loads(Path(a.spec).read_text());r=compare_panel(a.snapshot,s['cut_site'],s['panel']);Path(a.output).write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r,indent=2))
