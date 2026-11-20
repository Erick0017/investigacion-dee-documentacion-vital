"""Finite event-order trajectory, exact source freeze and primary observations."""
import argparse,hashlib,json,os,shutil,sys,time,traceback
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_name(p.name+'.pending');temp.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(temp,p)
def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True,type=Path);p.add_argument('--case',required=True);p.add_argument('--out',required=True,type=Path);p.add_argument('--restore',type=Path);a=p.parse_args()
    c=json.loads(a.config.read_text(encoding='utf-8'));case=next(x for x in c['cases'] if x['id']==a.case)
    a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source';src=bundle/'src/relaciones';src.mkdir(parents=True)
    files={}
    for name in('temporal_roles.py',):
        old=ROOT/'src/relaciones'/name;shutil.copyfile(old,src/name);files[name]=sha(src/name)
    shutil.copyfile(__file__,bundle/'ejecutar_temporal.py');files['ejecutar_temporal.py']=sha(__file__)
    sys.path.insert(0,str(bundle/'src'));started=time.monotonic();cpu=time.process_time()
    m={'schema':'CPC8.temporal_roles.measurements.v1','case':case,'configuration_sha256':sha(a.config),'source_sha256':files,'started_utc':datetime.now(timezone.utc).isoformat(),'status':'RUNNING','preparations':0 if a.restore else 1,'continuations':int(bool(a.restore)),'snapshots':[],'frames':[],'host_RAW_clock_edits_on_MAIN':[]}
    put(a.out/'CONFIG.json',c)
    try:
        import dee_thinking as dee
        from dee_thinking import _native as d
        from relaciones.temporal_roles import TemporalSession,physical
        assert dee.__version__=='4.5.0' and Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
        assert sha(d.__file__)=='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
        m['engine']={'version':dee.__version__,'module':dee.__file__,'PYD_sha256':sha(d.__file__),'WHL_sha256':'09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'}
        if a.restore:
            s=TemporalSession.load(a.restore);m['parent']={'snapshot':str(a.restore),'sha256':sha(a.restore),'physical':physical(s.world),'modality':'CONTINUATION_IN_NEW_PROCESS'}
        else:
            s=TemporalSession.create(gap=case['gap'],event_state_offset=case['event_state_offset'],query_delay=case['query_delay'],identifier=case['id'])
            s.events(case['history'],event_load=case.get('event_load',3));s.teach(case['name_mode']);s.query(payload=case.get('query_payload',7),role_inverse=case.get('role_inverse',True))
            if case.get('new_experience'):s.acquire_new(case.get('new_value',1))
            path=a.out/'INITIAL_T0.deetsnap.gz';m['snapshots'].append({'path':path.name,'physical':physical(s.world),'storage':s.save(path)})
        m['geometry']=s.geometry;t=s.geometry['ticks']
        frontiers={t['emission'],t['teach']-1,t['teach'],t['query'],99,100,t['role_first'],t['role_second'],234}
        for b in sorted(v for v in frontiers if s.tick<v<=case['horizon']):
            s.run_until(b);record={'tick':s.tick,'body':{k:s.observe(v) for k,v in s.geometry['body'].items()}}
            if b in(t['teach']-1,t['teach'],t['query'],t['role_first'],t['role_second']):
                field='teaching_hub' if b in(t['teach']-1,t['teach']) else'role_normalizer_site' if b==t['role_second'] else'query_site'
                record['encounter_neighborhoods']={k:[s.observe([(q[field][i]+offset[i])%131 for i in range(3)]) for offset in((x,y,z) for x in(-1,0,1) for y in(-1,0,1) for z in(-1,0,1))] for k,q in s.geometry['lanes'].items()}
            m['frames'].append(record)
            if b in(t['emission'],t['teach'],t['query'],100,t['role_second']):
                path=a.out/('T'+str(b)+'.deetsnap.gz');m['snapshots'].append({'path':path.name,'physical':physical(s.world),'storage':s.save(path)})
            put(a.out/'INCREMENTAL.json',{'tick':s.tick,'captures':s.state['captures'],'requests':s.receipts()})
        s.run_until(case['horizon']);m['captures']=s.state['captures'];m['requests']=s.receipts();m['physical']=physical(s.world);m['final_tick']=s.tick
        path=a.out/('FINAL_T'+str(s.tick)+'.deetsnap.gz');m['snapshots'].append({'path':path.name,'physical':physical(s.world),'storage':s.save(path)})
        m['observed']=[{'tick':x['tick'],'decoder':x['decoder'],'n':len(x['decoded']),'values':[y['value'] for y in x['decoded']]} for x in m['captures'] if x['decoder']!='none']
        m['status']='EXECUTED'
    except BaseException as e:m.update(status='TECHNICAL_ERROR',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());raise
    finally:
        m['elapsed_seconds']=time.monotonic()-started;m['cpu_seconds']=time.process_time()-cpu;put(a.out/'MEASUREMENTS.json',m)
    print(json.dumps({'id':case['id'],'status':m['status'],'observed':m['observed']}))
if __name__=='__main__':main()
