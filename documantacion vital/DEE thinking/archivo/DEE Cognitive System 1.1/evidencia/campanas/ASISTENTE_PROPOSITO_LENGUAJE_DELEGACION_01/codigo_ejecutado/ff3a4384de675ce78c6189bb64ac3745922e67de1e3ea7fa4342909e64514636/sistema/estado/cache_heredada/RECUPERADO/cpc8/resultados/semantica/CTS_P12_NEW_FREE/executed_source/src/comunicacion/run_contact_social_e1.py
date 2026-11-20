"""Freeze exact InitiativeUseE1 dependencies before the new candidate is imported."""
import argparse,hashlib,json,os,shutil,sys,time,traceback
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCES=['src/integracion/'+x+'.py'for x in('longitudinal_e1','complete_e1','quantity_core','relational_guarded_v2','relational_social','relational_ensemble','relational_pair_v2','relational_pair','contact_renewal_e1','initiative_e1','initiative_use_e1')]+['src/comunicacion/'+x+'.py'for x in('mode_communication','contact_social_e1','run_contact_social_e1')]+['src/relaciones/mode_reference.py','src/iniciativa_accion/solicitud.py','src/iniciativa_accion/return_use.py']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
    for i in range(3):
        try:os.replace(t,p);return
        except PermissionError:
            if i==2:raise
            time.sleep(.05*(i+1))
def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in cfg['cases']if c['id']==a.case);a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source';sources={}
    for f in SOURCES:
        dst=bundle/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,dst);sources[f]=sha(dst)
    sys.path.insert(0,str(bundle/'src'))
    import dee_thinking as dee
    from dee_thinking import _native as d
    from integracion.relational_pair import physical,move
    from comunicacion.contact_social_e1 import ContactSocialE1Session
    if dee.__version__!='4.5.0'or not Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):raise RuntimeError('Official isolated4.5 required')
    start=time.monotonic();m={'schema':'CPC8R.contact_socialE1.measurements.v1','case':case,'status':'RUNNING','preparations':0,'diagnostic_forks':0,'continuations':0,'source_sha256':sources,'configuration_sha256':sha(a.config),'engine':{'version':dee.__version__,'module':dee.__file__,'native_sha256':sha(d.__file__),'python':sys.executable},'frames':[],'windows':[],'snapshots':[],'host_RAW_clock_edits_on_MAIN':[]};put(a.out/'CONFIG.json',cfg)
    prepkeys=('guard_mode','actor_mode','include_order','include_contact','event_state_offset','medium_load','actor_state','quantity_guards')
    def checkpoint():m['elapsed_seconds']=time.monotonic()-start;put(a.out/'MEASUREMENTS.json',m)
    try:
        s=ContactSocialE1Session.create(identifier=case['id'],**{k:v for k,v in case.items()if k in prepkeys});m['preparations']=1;m['geometry']=s.geometry
        s.curriculum(**{k:v for k,v in case.items()if k not in('id',*prepkeys)})
        windows={31:[x['query_site']for x in s.geometry['order'].values()],76:[x['query_site']for x in s.geometry['contact'].values()],143:[x['renewed_site']for x in s.geometry['contact'].values()],165:[x['query_site']for x in s.geometry['order'].values()],206:[s.geometry['common_join']]}
        for t in(281,348,415,549,616):windows[t]=[x['delivery_site']for x in s.geometry['joint_names'].values()]
        for t in(70,137,204,338,405,472,539):windows.setdefault(t,[]).append(s.geometry['quantity']['center'])
        boundaries={0,5,11,89,110,170,200,210,214,268,271,340,344,411,417,428,433,436,478,484,486,487,549,553,554,558,559,563,616}
        for t in windows:boundaries.update((t-1,t))
        for t in sorted(boundaries):
            s.run_until(t);v=s.view();v['mode'].pop('captures',None);v['mode'].pop('social_captures',None);m['frames'].append(v)
            if t in windows:
                for q in windows[t]:m['windows'].append({'tick':t,'center':q,'Moore27':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
            if t in(0,484,487,549,554,563,616):
                path=a.out/('T'+str(t)+'.deetsnap.gz');storage=s.save(path);m['snapshots'].append({'path':path.name,'tick':t,'sha256':sha(path),'physical':physical(s.world),'storage':storage})
            m.update(last_complete_tick=t,requests=s.receipts());checkpoint()
        m.update(status='MEASURED',final_physical=physical(s.world),requests=s.receipts(),receipt_statuses=dict(Counter(r['receipt']['status']for r in s.receipts())),mode_captures=s.mode.state['captures'],social_captures=s.mode.state.get('social_captures',[]),quantity_observations=s.quantity.state['observations'],renewal_observations=s.state['renewal_observations'],initiative_captures=s.initiative.state['captures'],return_use_observations=s.state['return_use_observations'],contact_social_observations=s.state['contact_social_observations'])
    except BaseException as e:m.update(status='TECHNICAL_ERROR',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());raise
    finally:checkpoint()
    print(json.dumps({'case':case['id'],'status':m['status'],'queries':[(x['receiver'],x['covered'],x['content'])for x in m['contact_social_observations']if x['phase']=='QUERY'],'seconds':m['elapsed_seconds']}))
if __name__=='__main__':main()
