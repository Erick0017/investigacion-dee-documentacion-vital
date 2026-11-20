"""One finite social trajectory, frozen source bundle and exact observations."""
from array import array
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[2]


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def put(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.pending.'+str(os.getpid()))
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(temp,path)


def freeze(target):
    bundle=target/'executed_source';files={}
    for name in('comunicacion/__init__.py','comunicacion/social_channel.py','integracion/__init__.py','integracion/shared_world.py','integracion/alias_lower.py','integracion/relocated_lower.py','integracion/revision_lower.py'):
        src=ROOT/'src'/name;dst=bundle/'src'/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
        files[name]=sha(dst)
    shutil.copyfile(__file__,bundle/'ejecutar_social.py')
    files['ejecutar_social.py']=sha(__file__)
    sys.path.insert(0,str(bundle/'src'))
    return files


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case',required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--parent',type=Path)
    p.add_argument('--diagnostic',choices=['cut','sham']);a=p.parse_args()
    config=json.loads(a.config.read_text(encoding='utf-8'));case=next(x for x in config['cases'] if x['id']==a.case)
    a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();cpu=time.process_time()
    source=freeze(a.out)
    result={'schema':'CPC8.social.measurements.v1','case':case,'configuration_sha256':sha(a.config),
        'executed_source':source,'started_utc':datetime.now(timezone.utc).isoformat(),'frames':[],'snapshots':[],
        'parent':None,'preparations':0 if a.parent else 1,'diagnostic_forks':int(bool(a.diagnostic)),
        'continuations':0,'host_RAW_clock_edits_on_MAIN':[],'status':'RUNNING'}
    put(a.out/'CONFIG.json',config)
    try:
        import dee_thinking as dee
        from dee_thinking import _native as d
        from dee_thinking.consolidated import exact_observation
        from integracion.shared_world import physical
        from comunicacion.social_channel import SocialSession
        assert dee.__version__=='4.5.0' and Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
        assert sha(d.__file__)=='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
        result['engine']={'version':dee.__version__,'module':dee.__file__,'native_sha256':sha(d.__file__),
                          'wheel_sha256':'09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c','python':sys.executable}
        if a.parent:
            if not a.diagnostic:raise ValueError('Parent loading here is only the explicit fork control')
            parent=SocialSession.load(a.parent);before=physical(parent.world)
            s=parent.diagnostic_message(sham=a.diagnostic=='sham')
            result['parent']={'checkpoint':str(a.parent),'sha256':sha(a.parent),'physical':before,
                              'parent_unchanged':physical(parent.world)==before,'intervention':a.diagnostic}
            result['preparations']=0
        else:
            s=SocialSession.create(delay=case['delay'],renewed_access=case.get('renewed_access','none'),base_family=case.get('base_family','extra_own'),identifier=case['id'])
            s.experience_order(case['history'])
            if not case.get('base_family','').startswith('relocated_L17'):
                s.experience_own({'left':case['source_value'],'right':case['source_value']},mode=case['source_mode'])
            s.action_resources();s.teach_receiver(case['receiver_mode'])
            s.query_receiver(payload=case['query_payload'],context=case['context'],context_payload=case['context_payload'])
            if case.get('lower_curriculum'):
                values=[1 if i%3 else -1 for i in range(s.geometry['K'])]
                if case.get('base_family','').startswith('relocated_L17'):
                    values[16]=case['source_value']
                    s.experience_lower(values,[k for k in range(32) if k!=16],0)
                    if case['source_mode']!='omitted':
                        s.stimulate([{'port':'L17.signal','payload':5,'tick':int(case['source_mode']=='unpaired'),'origin':'ACTUAL_LOWER_L17_CUE'},
                            {'port':'L17.event.'+('plus' if values[16]>0 else'minus'),'payload':11,'tick':0,'origin':'ACTUAL_LOWER_L17_EVENT'}])
                else:s.experience_lower(values,range(32),0)
                s.experience_lower(values,range(32,s.geometry['K']),262)
                if case.get('lower_panels'):
                    s.query_lower([k for k in range(32) if not case.get('base_family','').startswith('relocated_L17') or k!=16],131)
                    s.query_lower(range(s.geometry['K']),393)
            if case.get('repeat_query'):
                t=s.geometry['social']['ticks']['query_input']+131
                method=s.query_receiver_renewed if case.get('renewed_access','none')!='none' else s.query_receiver
                method(at_tick=t,payload=case['query_payload'],context=-case['context'],context_payload=case['context_payload'])
            if case.get('revision_mode'):
                s.revise_l01(case['revision_sign'],mode=case['revision_mode'],tick=524)
                s.query_lower(range(s.geometry['K']),655)
            if case.get('post_revision_social_query'):
                s.query_receiver(at_tick=678,payload=11,context=case['context'],context_payload=7)
            path=a.out/'INITIAL_T0.deetsnap.gz';proof=s.save(path)
            result['snapshots'].append({'path':path.name,'physical':physical(s.world),'storage':proof})
            s.run_until(5);s.actual(case['actual'])
        result['geometry']=s.geometry
        result['preparation_resources_actual']={'N':int(s.world.runtime.dimension),'interfaces':len(s.world.interfaces),
            'initial_material_sites':len(s.world.recipe.placements),'organizations':list(s.world.organization_ids),
            'scope':'A is U0 plus selected acquired lower source and support banks; B is a new directional mobile receiver, not a second independently validated full compound.'}
        ticks=s.geometry['social']['ticks'];frontiers={136,138,139,140,ticks['query']-1,ticks['query'],ticks['effect']-1,ticks['effect'],ticks['delivery']}
        if case.get('revision_mode'):frontiers.update((523,524,526,527,658))
        for q in s.state.get('social_queries',[]):frontiers.update((q['read_tick']-1,q['read_tick'],q['effect_tick']-1,q['effect_tick'],q['delivery_tick']))
        def neighborhood(q):
            n=s.geometry['N'];out=[]
            for x in(-1,0,1):
                for y in(-1,0,1):
                    for z in(-1,0,1):out.append(exact_observation(s.world.runtime.observe(d.Coordinate((q[0]+x)%n,(q[1]+y)%n,(q[2]+z)%n))))
            return out
        for boundary in sorted(t for t in frontiers if s.tick<=t<=case['horizon']):
            s.run_until(boundary);frame=s.observe()
            if boundary in(139,140,ticks['query']-1,ticks['query'],ticks['effect']-1,ticks['effect']):
                field='hub' if boundary in(139,140) else 'query_site' if boundary in(ticks['query']-1,ticks['query']) else 'effect_site'
                frame['local_Moore26_plus_center']={k:neighborhood(v[field]) for k,v in s.geometry['social']['parts'].items()}
            result['frames'].append(frame);put(a.out/'INCREMENTAL.json',{'last_tick':s.tick,'requests':s.receipts(),'frames':result['frames']})
            if boundary in(138,140) or any(boundary==q['delivery_tick'] for q in s.state.get('social_queries',[])):
                path=a.out/('T'+str(boundary)+'.deetsnap.gz');proof=s.save(path)
                result['snapshots'].append({'path':path.name,'physical':physical(s.world),'storage':proof})
        s.run_until(case['horizon']);result['final_physical']=physical(s.world)
        path=a.out/('FINAL_T'+str(s.tick)+'.deetsnap.gz');proof=s.save(path)
        result['snapshots'].append({'path':path.name,'physical':physical(s.world),'storage':proof})
        result['requests']=s.receipts();result['social_captures']=s.state.get('social_captures',[])
        result['native_readouts']=s.state['reads'];result['final_tick']=s.tick
        result['observed_counts']=[{'tick':r['tick'],'stage':r['stage'],'pattern_count':len(r['decoded']),
            'decoded_pairs':[{'content_class':x['content_class'],'context_class':x['context_class'],'context_role':x['context_role']} for x in r['decoded']]}
            for r in result['social_captures']]
        result['coverage']='Pre/post local neighborhoods at fixed encounters plus complete causal-frontier snapshots. Uncovered segments are not assigned unique genealogy.'
        result['status']='EXECUTED';result['elapsed_seconds']=time.monotonic()-start;result['cpu_seconds']=time.process_time()-cpu
    except BaseException as error:
        result.update(status='TECHNICAL_ERROR',error_type=type(error).__name__,error=str(error),traceback=traceback.format_exc())
        raise
    finally:put(a.out/'MEASUREMENTS.json',result)
    print(json.dumps({'case_id':case['id'],'status':result['status'],'observed_counts':result['observed_counts'],'seconds':result['elapsed_seconds']}))


if __name__=='__main__':main()
