"""V3 guard extension and native continuation; no targets return to MAIN."""
from pathlib import Path
import argparse,json,shutil,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,digest,record,local_context
from integrated import Session
import order_memory,run_regulation,need_regulation_v3


def sparse_z(world):
    n=world.runtime.dimension;rows=[]
    for i,raw in enumerate(world.runtime.raw_copy()):
        if not raw:continue
        q=(i//(n*n),(i//n)%n,i%n);value=record(world,q)
        if value['direction'][2]!=0:rows.append(value)
    return {'nonzero_Z_records_including_inactive':rows,
        'active_nonzero_Z_in_lexical_planes_1_to31':sum(r['active'] and 1<=r['site'][2]<=31 for r in rows),
        'all_nonzero_Z_in_lexical_planes_1_to31':sum(1<=r['site'][2]<=31 for r in rows),
        'active_positive_Z_in_lexical_planes':sum(r['active'] and r['direction'][2]>0 and 1<=r['site'][2]<=31 for r in rows),
        'active_negative_Z_in_lexical_planes':sum(r['active'] and r['direction'][2]<0 and 1<=r['site'][2]<=31 for r in rows),
        'scope':'Current exact unpacked records, not unique provenance inferred from direction alone.'}


def continue_and_inspect(out):
    session=Session.load(out/'T24.deetsnap');g=session.geometry['need'];windows=[]
    for tick in (26,27,28,35):
        session.advance_to(tick)
        if tick<35:
            windows.append({'tick':tick,'guard_contexts':{k:local_context(session.world,x['nominal_interception_site']) for k,x in g['regulation']['guards'].items()}})
    primary=json.loads((out/'MEASUREMENTS.json').read_text(encoding='utf-8'))
    if digest(session.world)!=primary['final_physical']:raise AssertionError('Replay to35 altered physics')
    rows=[]
    for tick in (35,50,67,70,91,100):
        session.advance_to(tick)
        rows.append({'tick':tick,'body':order_memory.observations(session.world,session.geometry['body']),
                     'Z_record_panel':sparse_z(session.world),'physical':digest(session.world)})
    path=out/'CONTINUED_T100.deetsnap';snapshot=session.save(path);snapshot['path']=path.name
    value={'schema':'CPC7.need_regulation.continuation.v1','replay35_equal':True,
        'guard_pre_post_windows':windows,'continuation_rows':rows,'snapshot100':snapshot,
        'new_inputs_after35':[],'host_RAW_clock_edits':[],
        'scope':'Continuation of the same saved operative state, not a new independent preparation. Traffic in lexical planes is measured even when it belongs to a legitimate later probe product.'}
    put(out/'GLOBAL_TRAFFIC_AND_CONTINUATION.json',value);return value


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);index=[]
    run_regulation.need_regulation=need_regulation_v3
    for case in json.loads(a.config.read_text(encoding='utf-8-sig'))['cases']:
        out=a.out/case['id'];run_regulation.run_need.apparatus=run_regulation.builder(case['guard_mode'])
        r=json.loads((out/'MEASUREMENTS.json').read_text(encoding='utf-8')) if (out/'MEASUREMENTS.json').exists() else run_regulation.run_need.run(case,out)
        for name in ('need_regulation_v2.py','need_regulation_v3.py','run_regulation_v3.py'):shutil.copyfile(Path(__file__).parent/name,out/name)
        trace=run_regulation.reconstruct(out)
        cont=continue_and_inspect(out)
        row={'id':case['id'],'questions':len(r['native_questions']),'information':len(r['received_information']),'use':len(r['later_physical_use']),
             'traffic':[{'tick':x['tick'],'active_Z_in_low_planes':x['Z_record_panel']['active_nonzero_Z_in_lexical_planes_1_to31']} for x in cont['continuation_rows']],
             'primary':(out/'MEASUREMENTS.json').resolve().relative_to(ROOT).as_posix(),'sha256':sha(out/'MEASUREMENTS.json'),
             'guard_source_sha256':sha(Path(__file__).parent/'need_regulation_v3.py')}
        index.append(row);put(a.out/'INDEX.json',{'cases':index});print(json.dumps({'guard_case':row}),flush=True)

if __name__=='__main__':main()
