"""Freeze-before-import fresh E1+SPX; passive union of component boundaries."""
import argparse,hashlib,json,os,shutil,sys,time,traceback
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCES=['src/integracion/'+n+'.py'for n in('longitudinal_e1','complete_e1','quantity_core','relational_guarded_v2','relational_social','relational_ensemble','relational_pair_v2','relational_pair')]+['src/relaciones/'+n+'.py'for n in('mode_reference','spatial_gradient','spatial_reference','full_spatial_e1','run_full_spatial_e1')]+['src/comunicacion/'+n+'.py'for n in('mode_communication','spatial_communication','spatial_context')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
    for attempt in range(3):
        try:os.replace(t,p);return
        except PermissionError:
            if attempt==2:raise
            time.sleep(.05*(attempt+1))
def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--inspect-only',action='store_true');a=p.parse_args()
    cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in cfg['cases']if c['id']==a.case);a.out.mkdir(parents=True,exist_ok=False)
    sources={};bundle=a.out/'executed_source'
    for f in SOURCES:
        target=bundle/f;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,target);sources[f]=sha(target)
    sys.path.insert(0,str(bundle/'src'))
    import dee_thinking as dee
    from dee_thinking import _native as d
    from relaciones.full_spatial_e1 import prepare_full_spatial,FullSpatialE1Session
    from integracion.relational_pair import physical,move
    if dee.__version__!='4.5.0'or not Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):raise RuntimeError('Official isolated4.5 required')
    start=time.monotonic();m={'schema':'CPC8R.full_spatialE1.measurements.v1','case':case,'status':'RUNNING','preparations':0,'diagnostic_forks':0,'continuations':0,'configuration_sha256':sha(a.config),'source_sha256':sources,'engine':{'version':dee.__version__,'module':dee.__file__,'native_sha256':sha(d.__file__),'python':sys.executable},'frames':[],'windows':[],'snapshots':[],'host_RAW_clock_edits_on_MAIN':[]};put(a.out/'CONFIG.json',cfg)
    prepkeys=('spatial_origin','reference_state','object_states','context_state','guard_mode','actor_mode','include_order','include_contact','event_state_offset','medium_load','actor_state','quantity_guards')
    def checkpoint():
        m['elapsed_seconds']=time.monotonic()-start;put(a.out/'MEASUREMENTS.json',m)
    try:
        recipe,g=prepare_full_spatial(**{k:v for k,v in case.items()if k in prepkeys});m['geometry']=g
        if a.inspect_only:m.update(status='PRET0_GEOMETRY_ONLY',resources=g['resources'],merge=g['spatial_merge']);checkpoint();print(json.dumps({'status':m['status'],'resources':m['resources'],'merge':m['merge']}));return
        s=FullSpatialE1Session(d.OrganizationalWorld.create(recipe),g,identifier=case['id']);m['preparations']=1
        s.curriculum(**{k:v for k,v in case.items()if k not in(*prepkeys,'id')});m['initial_physical']=physical(s.world)
        windows={31:[x['query_site']for x in g['order'].values()],76:[x['query_site']for x in g['contact'].values()],143:[x['renewed_site']for x in g['contact'].values()],165:[x['query_site']for x in g['order'].values()],206:[g['common_join']]}
        for t in(281,348,415,549):windows[t]=[x['delivery_site']for x in g['joint_names'].values()]
        for t in(70,137,204,338,405,472,539):windows.setdefault(t,[]).append(g['quantity']['center'])
        for t in(235,240,243):
            for r in g['spatial']['communication']['receivers']:
                targets=[r['memory_site']]if t==235 else [r['context_site']]if t==240 else [x['site']for x in r['deliveries'].values()]
                windows.setdefault(t,[]).extend(targets)
        boundaries={0,5,11,78,100,110,155,157,160,168,170,180,200,210,214,227,229,231,232,243,268,271,549}
        for t in windows:boundaries.update((t-1,t))
        boundaries.update(s.spatial.critical_ticks())
        for t in sorted(boundaries):
            s.run_until(t);v=s.view();v['mode'].pop('captures',None);v['mode'].pop('social_captures',None);v['spatial'].pop('social_captures',None);m['frames'].append(v)
            if t in windows:
                for q in windows[t]:m['windows'].append({'tick':t,'center':q,'Moore27':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
            if t in(0,110,168,200,243,281,348,549):
                path=a.out/('T'+str(t)+'.deetsnap.gz');storage=s.save(path);m['snapshots'].append({'path':path.name,'tick':t,'sha256':sha(path),'physical':physical(s.world),'storage':storage})
            m.update(last_complete_tick=t,requests=s.receipts());checkpoint()
        m.update(status='MEASURED',final_physical=physical(s.world),requests=s.receipts(),receipt_statuses=dict(Counter(r['receipt']['status']for r in s.receipts())),mode_captures=s.mode.state['captures'],social_captures=s.mode.state.get('social_captures',[]),quantity_observations=s.quantity.state['observations'],spatial_captures={k:v.state['captures']for k,v in s.spatial.modes.items()},spatial_social_captures=s.spatial.state.get('social_captures',[]),spatial_captured_ticks=s.state['spatial_captured_ticks'])
    except BaseException as e:m.update(status='TECHNICAL_ERROR',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());raise
    finally:checkpoint()
    print(json.dumps({'case':case['id'],'status':m['status'],'requests':m.get('receipt_statuses'),'spatial_query':[(x['receiver'],x['relation'])for x in m['spatial_social_captures']if x['phase']=='FORM_QUERY'and x['covered']],'seconds':m['elapsed_seconds']}))
if __name__=='__main__':main()
