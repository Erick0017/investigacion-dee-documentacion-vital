"""Supervised finite mode-reference trajectory; no targets available to entity."""
import argparse,hashlib,json,os,shutil,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(t,p)
def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf-8'));case=next(x for x in cfg['cases'] if x['id']==a.case)
    a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source';src=bundle/'src/relaciones';src.mkdir(parents=True);shutil.copyfile(ROOT/'src/relaciones/mode_reference.py',src/'mode_reference.py');shutil.copyfile(__file__,bundle/'run_mode_reference.py');sys.path.insert(0,str(bundle/'src'))
    start=time.monotonic();cpu=time.process_time();m={'schema':'CPC8R.mode_reference.measurements.v1','case':case,'source_sha256':{'module':sha(src/'mode_reference.py'),'runner':sha(bundle/'run_mode_reference.py')},'configuration_sha256':sha(a.config),'preparations':1,'diagnostic_forks':0,'continuations':0,'status':'RUNNING','snapshots':[],'frames':[],'host_RAW_clock_edits_on_MAIN':[]};put(a.out/'CONFIG.json',cfg)
    try:
        import dee_thinking as dee
        from dee_thinking import _native as d
        from relaciones.mode_reference import ModeReferenceSession,physical,move
        assert dee.__version__=='4.5.0' and Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
        assert sha(d.__file__)=='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
        m['engine']={'version':dee.__version__,'module':dee.__file__,'PYD_sha256':sha(d.__file__),'WHL_sha256':'09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'}
        s=ModeReferenceSession.create(object_states=tuple(case['object_states']),reference_state=case['reference_state'])
        s.acquire_reference(case['reference_direction'],case['reference_mode'],case['reference_load']);s.prepare_normalizers()
        s.query_object(1,case['objects'][0],case['query_loads'][0]);s.query_object(2,case['objects'][1],case['query_loads'][1]);s.acquire_other(case['other_value']);m['geometry']=s.geometry
        path=a.out/'INITIAL_T0.deetsnap.gz';m['snapshots'].append({'path':path.name,'physical':physical(s.world),'storage':s.save(path)})
        boundaries={3,69,70,110,180};boundaries.update(q['parent']['query_tick']+offset for q in s.geometry['queries'] for offset in(-1,0));boundaries.update(b[k]+off for b in s.geometry['branches'] for k in('first_tick','second_tick') for off in(-1,0))
        for t in sorted(v for v in boundaries if s.tick<v<=case['horizon']):
            s.run_until(t);frame={'tick':s.tick,'reference_origin':s.observe(s.geometry['reference_hub'])}
            if t==180:frame['other_relation']=s.observe(s.geometry['other_hub'])
            frames=[b for b in s.geometry['branches'] if t in(b['first_tick']-1,b['first_tick'],b['second_tick']-1,b['second_tick'])]
            if frames:
                frame['normalizers']={b['id']:{'first':s.observe(b['first_site']),'second':s.observe(b['second_site'])} for b in frames}
            if any(t in(q['parent']['query_tick']-1,q['parent']['query_tick']) for q in s.geometry['queries']):
                frame['query_Moore27']={q['parent']['id']:[s.observe(move(q['parent']['hub'],(x,y,z))) for x in(-1,0,1) for y in(-1,0,1) for z in(-1,0,1)] for q in s.geometry['queries'] if t in(q['parent']['query_tick']-1,q['parent']['query_tick'])}
            m['frames'].append(frame);put(a.out/'INCREMENTAL.json',{'last_tick':s.tick,'captures':s.state['captures'],'requests':s.receipts()})
            if t in(3,70,110,157,165):
                path=a.out/('T'+str(t)+'.deetsnap.gz');m['snapshots'].append({'path':path.name,'physical':physical(s.world),'storage':s.save(path)})
        s.run_until(case['horizon']);path=a.out/('FINAL_T'+str(s.tick)+'.deetsnap.gz');m['snapshots'].append({'path':path.name,'physical':physical(s.world),'storage':s.save(path)})
        m.update(captures=s.state['captures'],requests=s.receipts(),aliases=s.state['aliases'],final_physical=physical(s.world),status='EXECUTED')
        m['observed']=[{'tick':c['tick'],'stage':c['stage'],'parent_route':c['parent_route'],'covered':c['covered'],'relation':c['relation'],'direction':c['physical']['direction']} for c in m['captures']]
    except BaseException as e:m.update(status='TECHNICAL_ERROR',error=str(e),error_type=type(e).__name__,traceback=traceback.format_exc());raise
    finally:m.update(elapsed_seconds=time.monotonic()-start,cpu_seconds=time.process_time()-cpu);put(a.out/'MEASUREMENTS.json',m)
    print(json.dumps({'id':case['id'],'status':m['status'],'observed':m['observed']}))
if __name__=='__main__':main()
