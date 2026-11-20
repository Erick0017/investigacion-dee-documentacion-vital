"""Finite guarded-adapter cases plus exact selective replay of unused rays."""
from pathlib import Path
import argparse,json,shutil,sys,types
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,record,digest,local_context
from integrated import Session
import run_need,comparison_need_v2,need_regulation


def builder(mode):
    def prepare_geometry(**kw):
        prep=comparison_need_v2.prepare_geometry(**kw)
        extra=need_regulation.prepare_geometry(prep['geometry'],mode=mode)
        sites={(p.site.x,p.site.y,p.site.z) for p in prep['placements']}
        if any((p.site.x,p.site.y,p.site.z) in sites for p in extra['placements']):raise ValueError('Guard/adapter preparation overlap')
        prep['placements']+=extra['placements'];prep['geometry']['regulation']=extra['geometry']
        return prep
    return types.SimpleNamespace(prepare_geometry=prepare_geometry,actual_protocol=comparison_need_v2.actual_protocol,
        source_protocol=comparison_need_v2.source_protocol,use_protocol=comparison_need_v2.use_protocol,capture=comparison_need_v2.capture)


def reconstruct(out):
    s=Session.load(out/'T19.deetsnap');g=s.geometry['need'];rows=[];windows=[]
    for tick in range(19,36):
        s.advance_to(tick);r={'tick':tick,'normalizers':{},'guards':{}}
        for key,b in g['regulation']['guards'].items():
            q=comparison_need_v2.moved(b['question_site'],tuple(b['normalizer_direction']),tick-g['ticks']['question'])
            r['normalizers'][key]=record(s.world,q)
            site=b['nominal_interception_site'];r['guards'][key]=record(s.world,site)
            if tick in (21,22,23,24):windows.append({'tick':tick,'branch':key,'interception_context':local_context(s.world,site)})
        rows.append(r)
    original=json.loads((out/'MEASUREMENTS.json').read_text(encoding='utf-8'))
    same=digest(s.world)==original['final_physical']
    value={'schema':'CPC7.regulation.replay.v1','replay_from':'T19.deetsnap','physical_equal_at35':same,
        'rows':rows,'local_interception_windows':windows,
        'retained_negative_Z_nominal_records_24_to35':sum(o['active'] and o['direction']==[0,1,-1] for r in rows if r['tick']>=24 for o in r['normalizers'].values()),
        'scope':'Exact sampled records along nominal mediator routes. A changed ray is not given a guessed continuation; snapshots retain full state for reconstruction.'}
    put(out/'REGULATION_TRACE.json',value)
    if not same:raise AssertionError('Selective replay changed future physics')
    return value


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);index=[]
    for case in json.loads(a.config.read_text(encoding='utf-8-sig'))['cases']:
        out=a.out/case['id'];run_need.apparatus=builder(case['guard_mode'])
        r=json.loads((out/'MEASUREMENTS.json').read_text(encoding='utf-8')) if (out/'MEASUREMENTS.json').exists() else run_need.run(case,out)
        for name in ('comparison_need_v2.py','need_regulation.py','run_regulation.py'):shutil.copyfile(Path(__file__).parent/name,out/name)
        trace=json.loads((out/'REGULATION_TRACE.json').read_text(encoding='utf-8')) if (out/'REGULATION_TRACE.json').exists() else reconstruct(out)
        row={'id':case['id'],'guard_mode':case['guard_mode'],'questions':len(r['native_questions']),'information':len(r['received_information']),
            'use':len(r['later_physical_use']),'negative_Z_on_nominal_route_after24':trace['retained_negative_Z_nominal_records_24_to35'],
            'primary':(out/'MEASUREMENTS.json').resolve().relative_to(ROOT).as_posix(),'sha256':sha(out/'MEASUREMENTS.json'),
            'trace':(out/'REGULATION_TRACE.json').resolve().relative_to(ROOT).as_posix()}
        index.append(row);put(a.out/'INDEX.json',{'cases':index});print(json.dumps({'guard_case':row}),flush=True)

if __name__=='__main__':main()
