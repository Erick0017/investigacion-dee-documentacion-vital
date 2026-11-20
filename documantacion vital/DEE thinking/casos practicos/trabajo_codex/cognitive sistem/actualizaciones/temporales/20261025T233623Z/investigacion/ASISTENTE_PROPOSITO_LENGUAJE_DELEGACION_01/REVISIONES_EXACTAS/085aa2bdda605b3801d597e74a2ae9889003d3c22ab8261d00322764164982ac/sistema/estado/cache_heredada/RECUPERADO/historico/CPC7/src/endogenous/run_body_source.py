"""Two matched source-load cohorts, common online experience and queries."""
from pathlib import Path
import argparse,json,shutil,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,identity,put,sha,digest,record,operational,local_context
from integrated import Session
import order_memory,body_source
from run_regulation_v3 import sparse_z


def run(case,out):
    import dee_thinking as d
    out=Path(out);out.mkdir(parents=True,exist_ok=False);start=time.monotonic();engine=identity()
    prep=body_source.prepare_geometry(center=tuple(case.get('center',[33,25,42])),source_load=case['source_load'])
    recipe=d.OrganizationRecipe.research(67,prep['placements'],0);recipe.interfaces=prep['interfaces'];recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    s=Session(d.OrganizationalWorld.create(recipe),{'body':prep['geometry']});w=s.world
    s.stimulate(order_memory.experience('AB'))
    s.stimulate([{'port':'order.read','payload':7,'tick':t,'kind':'probe','origin':'COMMON_PHYSICAL_READER'} for t in (2,69)])
    put(out/'CONFIG.json',{'case':case,'geometry':s.geometry,'source_sha256':sha(__file__),
        'criterion':'Exact original emission at5 and common later physical query admission/response; raw/clocks conserved except one initial source s_reg; current nonzeroZ traffic sampled without guessed genealogy',
        'horizon':100,'codecs_fixed_between_histories':True})
    for name in ('body_source.py','run_body_source.py'):shutil.copyfile(Path(__file__).parent/name,out/name)
    rows=[];traffic=[];snaps=[];windows=[]
    for tick in range(101):
        s.advance_to(tick);rows.append({'tick':tick,'body':order_memory.observations(w,s.geometry['body'])})
        if tick in (35,50,67,70,72,91,100):traffic.append({'tick':tick,'panel':sparse_z(w)})
        if tick in (1,2,3,4,5,68,69,70,71,72):windows.append({'tick':tick,'context':local_context(w,s.geometry['body']['center'])})
        if tick in (0,5,35,100):
            path=out/f'T{tick}.deetsnap';v=s.save(path);v['path']=path.name;snaps.append(v)
        if tick in (5,35,72,100):put(out/'INCREMENTAL.json',{'last_complete_tick':tick,'rows':rows,'traffic':traffic})
    result={'schema':'CPC7.initial_body_source.measurements.v1','case':case,'engine':engine,'geometry':s.geometry,'rows':rows,
        'traffic':traffic,'local_windows':windows,'snapshots':snaps,'requests':s.receipts(),
        'emission5':rows[5]['body']['emission'],'common_query72':rows[72]['body']['emission'],
        'final_physical':digest(w),'final_operative':operational(w),'preparations':1,
        'host_RAW_clock_edits_after_T0':[],'elapsed_seconds':time.monotonic()-start,
        'scope':'A fresh matched preparation differs in one source s_reg before any experience. It does not remove residuals from an old individual or demonstrate experience-dependent regulation.'}
    put(out/'MEASUREMENTS.json',result);print(json.dumps({'id':case['id'],'emission5':result['emission5'],
        'query72':result['common_query72'],'traffic':[{'tick':x['tick'],'active_Z_low':x['panel']['active_nonzero_Z_in_lexical_planes_1_to31']} for x in traffic]}),flush=True);return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);index=[]
    for case in json.loads(a.config.read_text(encoding='utf-8-sig'))['cases']:
        out=a.out/case['id'];r=json.loads((out/'MEASUREMENTS.json').read_text(encoding='utf-8')) if (out/'MEASUREMENTS.json').exists() else run(case,out)
        index.append({'id':case['id'],'emission5':r['emission5'],'query72':r['common_query72'],'evidence':(out/'MEASUREMENTS.json').resolve().relative_to(ROOT).as_posix(),'sha256':sha(out/'MEASUREMENTS.json')})
        put(a.out/'INDEX.json',{'cases':index})

if __name__=='__main__':main()
