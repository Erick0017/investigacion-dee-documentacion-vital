"""Two native-contact viability conditions, then finite causal/reserved cohorts."""
import argparse,hashlib,json,os,shutil,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
    temp=p.with_name(p.name+'.pending');temp.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(temp,p)
def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf-8'));case=next(x for x in cfg['cases'] if x['id']==a.case)
    a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source';src=bundle/'src/relaciones';src.mkdir(parents=True);shutil.copyfile(ROOT/'src/relaciones/contact_consequence.py',src/'contact_consequence.py');shutil.copyfile(__file__,bundle/'ejecutar_contacto.py');sys.path.insert(0,str(bundle/'src'))
    start=time.monotonic();cpu=time.process_time();m={'schema':'CPC8.contact_consequence.measurements.v1','case':case,'source_sha256':{'module':sha(src/'contact_consequence.py'),'runner':sha(bundle/'ejecutar_contacto.py')},'config_sha256':sha(a.config),'preparations':1,'continuations':0,'diagnostic_forks':0,'status':'RUNNING','snapshots':[],'frames':[],'host_RAW_clock_edits_on_MAIN':[]};put(a.out/'CONFIG.json',cfg)
    try:
        import dee_thinking as dee
        from dee_thinking import _native as d
        from relaciones.contact_consequence import ContactSession,physical,move
        assert dee.__version__=='4.5.0' and Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
        assert sha(d.__file__)=='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
        m['engine']={'version':dee.__version__,'module':dee.__file__,'PYD_sha256':sha(d.__file__),'WHL_sha256':'09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'}
        s=ContactSession.create(**{k:case[k] for k in('mode','medium_direction','medium_load','contact_tick','actor_direction','actor_state','query_offset')},association_mode=case.get('association_mode','instrumental'),use_gap=case.get('use_gap',4))
        s.teach(case['name_mode']);s.query(payload=case['query_payload'],use_payload=case['use_payload'],repeat=case.get('repeat',False))
        if case.get('other_acquisition'):s.acquire_other(case.get('other_value',1))
        m['geometry']=s.geometry
        path=a.out/'INITIAL_T0.deetsnap.gz';m['snapshots'].append({'path':path.name,'storage':s.save(path),'physical':physical(s.world)})
        t=s.geometry['ticks'];frontiers={t['before_contact'],t['contact'],t['teaching']-1,t['teaching'],t['query']-1,t['query'],t['effect']-1,t['effect'],t['delivery']}
        if case.get('repeat'):frontiers.update((90,t['renewed_query'],t['renewed_effect'],t['renewed_delivery'],160))
        for b in sorted(v for v in frontiers if 0<v<=case['horizon']):
            s.run_until(b);frame={'tick':b,'contact':s.observe(s.geometry['contact']),'actor_opportunity_join':s.observe(s.geometry['actor_opportunity_join'])}
            if b in(t['before_contact'],t['contact']):frame['contact_Moore27']=[s.observe(move(s.geometry['contact'],(x,y,z))) for x in(-1,0,1) for y in(-1,0,1) for z in(-1,0,1)]
            if b in(t['teaching']-1,t['teaching']):frame['teaching_Moore27']={k:[s.observe(move(q['hub'],(x,y,z))) for x in(-1,0,1) for y in(-1,0,1) for z in(-1,0,1)] for k,q in s.geometry['parts'].items()}
            if b==160:frame['additional_relation']=s.observe(s.geometry['auxiliary_hub'])
            m['frames'].append(frame)
            if b in(t['contact'],t['teaching'],t['query'],t['delivery'],t.get('renewed_delivery')):
                path=a.out/('T'+str(b)+'.deetsnap.gz');m['snapshots'].append({'path':path.name,'physical':physical(s.world),'storage':s.save(path)})
            put(a.out/'INCREMENTAL.json',{'tick':s.tick,'requests':s.receipts(),'captures':s.state['captures']})
        s.run_until(case['horizon']);m.update(requests=s.receipts(),captures=s.state['captures'],physical=physical(s.world),final_tick=s.tick)
        path=a.out/('FINAL_T'+str(s.tick)+'.deetsnap.gz');m['snapshots'].append({'path':path.name,'physical':physical(s.world),'storage':s.save(path)})
        m['observed']=[{'tick':x['tick'],'stage':x['stage'],'n':len(x['decoded']),'components':[q['consequence_component'] for q in x['decoded']]} for x in m['captures']];m['status']='EXECUTED'
    except BaseException as e:m.update(status='TECHNICAL_ERROR',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());raise
    finally:m.update(elapsed_seconds=time.monotonic()-start,cpu_seconds=time.process_time()-cpu);put(a.out/'MEASUREMENTS.json',m)
    print(json.dumps({'id':case['id'],'observed':m['observed']}))
if __name__=='__main__':main()
