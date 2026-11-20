"""Native replay of archived inputs, not a new external closed-loop trial."""
from pathlib import Path
import sys,json,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
from capacidades.observador_causal_retrospectivo_01 import Snapshot
import ic_body as body
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
def read(name):return json.loads((EV/(name+'.json')).read_text(encoding='utf8'))
expected=read('MAIN_COMMITTED_BODY_38')['INSTRUMENTO']['snapshot_sha256']
parent=next(p for p in(s.root/'estado/checkpoints').glob('E1_INTEGRADO_MAIN.T3312.*')if digest_file(p)==expected)
social=read('MAIN_NATIVE_SOCIAL_39')['result']['social']['requests']
external=[]
for name in('MAIN_EXTERNAL_CONSEQUENCES_40','MAIN_EXTERNAL_CONTINUATION_42'):
    for row in read(name)['result']['data']['rows']:external.extend(row['requests'])
panel=read('MAIN_OLD_FUNCTIONS_INTERLEAVED_41')['result']['data'];panel_events=[]
for r in panel['requests']:panel_events.append({'port':r['channels'][0],'payload':7,'tick':r['requested_tick'],'kind':r['kind']})
q=next(f for f in panel['frames']if f['kind']=='quantity')
panel_events.extend([{'port':'quantity.object.cue','payload':5,'tick':q['tick']-5,'kind':'experience'},{'port':'quantity.object.resource','payload':q['object'],'tick':q['tick']-5,'kind':'experience'}])
cases=[('FACTOR_NATIVE_ONLY_67',False,False,False),('FACTOR_SOCIAL_ONLY_68',True,False,False),('FACTOR_EXTERNAL_INPUTS_69',False,True,False),('FACTOR_SOCIAL_EXTERNAL_70',True,True,False),('FACTOR_PANEL_ONLY_71',False,False,True),('FACTOR_REPLAY_MAIN_72',True,True,True)]
for name,b,x,p in cases:
    if time.monotonic()>deadline:raise TimeoutError('Original deadline')
    out=EV/(name+'.json');life='IC01_'+name
    if out.exists():continue
    s.fork('E1_INTEGRADO_MAIN',life,kind='DIAGNOSTIC_COPY',checkpoint=str(parent.relative_to(s.root)))
    def run(a):
        before=physical(a.world,occupation=True);events=[];seen=set()
        if b:events.extend(social)
        if x:events.extend(external)
        if p:events.extend(panel_events)
        rr=[]
        for e in sorted(events,key=lambda e:(e.get('tick',e.get('requested_tick',0)),e.get('id',0))):
            if e.get('id')is not None:
                if e['id']in seen:continue
                seen.add(e['id'])
            port=e.get('port',e.get('channels',[None])[0]);tick=e.get('tick',e.get('requested_tick'));kind=e.get('kind',e.get('receipt',{}).get('kind','experience'))
            rec=(a.world.probe if kind=='probe'else a.world.submit)(port,e['payload'],tick);rr.append({'port':port,'payload':e['payload'],'tick':tick,'id':int(rec.id),'kind':kind})
        h=body.attach(a);samples=[];snapshots=[]
        try:
            for t in sorted(set([3312,3400,3483,3550,3600,3639,3660,3691,3710,3743,3795,3847,3899])):
                a.run_until(t);samples.append(physical(a.world,occupation=True))
                if len(snapshots)==0 and samples[-1]['occupied']>10000:
                    path=EV/(name+'_FIRST_DENSE_T'+str(t)+'.deetsnap.gz');a.save(path);snapshots.append({'path':str(path),'sha256':digest_file(path),'not_exact_birth_tick':True})
        finally:h['detach']()
        return{'initial':before,'factors':{'social_B_and_back':b,'archived_external_sensor_cost':x,'material_old_panel':p},'samples':samples,'native_frames':h['frames'],'requests':body.ic.receipts(a,rr),'first_dense_snapshots':snapshots,'final':physical(a.world,occupation=True),'attribution':'Archived-input native replay. No Pendulum environment runs here. These cases isolate native input families; not new external learning, independent biological samples or full Python-log byte identity.'}
    r=s.mutate(life,'IC01_GROWTH_INPUT_FAMILY_CONTRAST',run,{'source_sha256':digest_file(__file__),'archived_sources':['MAIN_NATIVE_SOCIAL_39','MAIN_EXTERNAL_CONSEQUENCES_40','MAIN_EXTERNAL_CONTINUATION_42','MAIN_OLD_FUNCTIONS_INTERLEAVED_41'],'predefined_cases':cases});atomic_json(out,r);print(name+' '+str(r['INSTRUMENTO']['tick']),flush=True)
