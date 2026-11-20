from pathlib import Path
import sys,json,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import atomic_json,digest_file,physical,observe
from app.process_control import protect_current
import ic_body as body,ic_external as ext,delayed_social as social
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
source='E1_INTEGRADO_COSTO_SOCIAL_01';parent=json.loads((EV/'INTEGRATED_COST_SOCIAL_132.json').read_text())['final_record']
cases=[('INTERLEAVE_NATIVE_EXTERNAL_141',source,'paired','intact'),('INTERLEAVE_NO_NATIVE_RETURN_142','IC01_INTERLEAVE_NO_RETURN_142','paired','omit_return'),('INTERLEAVE_NO_NATIVE_TEACH_143','IC01_INTERLEAVE_NO_TEACH_143','omit','intact')]
spec={'frozen_before_all_cases':True,'parent':parent['snapshot_sha256'],'retained_external_environment_and_social_carrier':True,'new_native_contexts':[-1,1],'native_availability':[1,1,-1,-1,1,1],'external_steps':6,'old_social_content_not_taught_again':True,'motor_wiring_unchanged':'quantity1+social1','native_context_learning_rule':'Prepared physical win-stay/lose-switch mechanism, acquired directional state, not a general strategy learner','pause':'During the scheduled native training block Pendulum is paused, with exact prior state retained; no adaptive waiting for a desired response. Six subsequent motor steps resume the fixed67tick phase. Closing3native ticks do not step Pendulum.'}
if not(EV/'INTERLEAVE_SPEC_141.json').exists():atomic_json(EV/'INTERLEAVE_SPEC_141.json',spec)
for name,life,teaching,returns in cases[1:]:
    if not s.life_dir(life).exists():s.fork(source,life,kind='DIAGNOSTIC_COPY',checkpoint=parent['snapshot'])
for name,life,teaching,returns in cases:
    if time.monotonic()>deadline:raise TimeoutError('Fixed campaign deadline')
    out=EV/(name+'.json')
    if out.exists():continue
    def run(a):
        initial=physical(a.world,occupation=True);pre={'selector':body.ic.obs(a,body.ic.CENTER),'reference':observe(a.world,a.quantity.geometry['reference_hub'])}
        train=body.ic.train(a,episode=name,contexts=(-1,1),feedback=teaching)
        armed=body.arm(a,name=name,contexts=tuple(spec['native_availability']),mode=returns,shunt='a_only')
        h=body.attach(a)
        try:external=ext.run(a,steps=6,mode='closed',readout='magnitude',feedback='cost',codec=2,reader='omit',stop_invalid=3,social_ports=social.get(a)['plan']['banks'])
        finally:h['detach']()
        finish=body.finish(a)
        return{'spec':spec,'initial':initial,'initial_native_fields':pre,'training':train,'armed':armed,'native_frames':h['frames'],'external':external,'native_finish':finish,'reference_after':observe(a.world,a.quantity.geometry['reference_hub']),'social_current':[observe(a.world,b['target'])for b in social.get(a)['plan']['banks']],'final':physical(a.world,occupation=True),'scope':'Sequential same-world use of new native training, native consequence returns, retained received information and actual external feedback. The prepared native return law and fixed mixed actuator remain external design; no native compositional rule or optimal Pendulum learning is assumed.'}
    r=s.mutate(life,'IC01_NATIVE_SOCIAL_EXTERNAL_CONSECUTIVE_USE',run,{'spec':spec,'sources':{p.name:digest_file(p)for p in[LAB/'ic_native_core.py',LAB/'ic_body.py',LAB/'ic_external.py',LAB/'delayed_social.py',Path(__file__)]}});atomic_json(out,r);print(name+' '+str(r['INSTRUMENTO']['tick']),flush=True)
