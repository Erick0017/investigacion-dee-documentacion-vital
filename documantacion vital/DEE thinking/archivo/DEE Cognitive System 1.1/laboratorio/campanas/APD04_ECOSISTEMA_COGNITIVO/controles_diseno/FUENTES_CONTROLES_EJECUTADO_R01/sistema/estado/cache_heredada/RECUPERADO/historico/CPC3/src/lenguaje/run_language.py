"""Finite CPC3 association/composition tests, no historical runner imports."""
import argparse
import json
import hashlib
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from lenguaje.association import AssociationSession,composition_world,experience_composition,query_composition,physical


def save_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')


def run_case(case,out):
    ident=case['id'];folder=out/ident;folder.mkdir(parents=True,exist_ok=True);started=time.monotonic()
    if case['family']=='association':
        s=AssociationSession.create(case.get('forms'),tuple(case.get('translation',[0,0,0])))
        before=physical(s.world);s.save(folder/'T0.deetsnap')
        history=s.train(tuple(case['teachers']),case.get('cue',5),case.get('mode','paired'))
        s.save(folder/'ACQUIRED.deetsnap')
        if case.get('sequential'):
            response=s.start_sequence(case['queries'])
        else:response=s.query_simultaneous(case['query'])
        s.save(folder/'FINAL.deetsnap')
        result={'id':ident,'case':case,'before':before,'acquisition':history,'response':response,'log':s.log}
    else:
        w=composition_world(case.get('depth',2),tuple(case.get('translation',[0,0,0])))
        before=physical(w);w.save_snapshot(str(folder/'T0.deetsnap'))
        history=experience_composition(w,case['pairs'],case.get('omit'));w.save_snapshot(str(folder/'ACQUIRED.deetsnap'))
        response=query_composition(w,case['query']);w.save_snapshot(str(folder/'FINAL.deetsnap'))
        result={'id':ident,'case':case,'before':before,'acquisition_receipts':history,'response':response}
    result['duration_seconds']=time.monotonic()-started
    save_json(folder/'MEASUREMENTS.json',result)
    return {'id':ident,'duration_seconds':result['duration_seconds'],'result':str((folder/'MEASUREMENTS.json').relative_to(out)),
            'configuration_sha256':hashlib.sha256(json.dumps(case,sort_keys=True).encode()).hexdigest()}


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--stage',choices=['discovery','reserved'],required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();config=json.loads(a.config.read_text(encoding='utf-8'))
    summary=[]
    for case in config['cases']:
        if case['stage']!=a.stage:continue
        file=a.output/case['id']/'MEASUREMENTS.json'
        if file.exists():summary.append({'id':case['id'],'skipped_completed':True});continue
        try:summary.append(run_case(case,a.output))
        except Exception as exc:
            error={'id':case['id'],'status':'TECHNICAL_ERROR','error':repr(exc)};save_json(file,error);summary.append(error)
    save_json(a.output/(a.stage.upper()+'_SUMMARY.json'),summary)
    print(json.dumps(summary,ensure_ascii=True),flush=True)
    if any(x.get('status')=='TECHNICAL_ERROR' for x in summary):raise SystemExit(1)


if __name__=='__main__':main()
