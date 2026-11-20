from pathlib import Path
import sys,time,json
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB),str(ROOT/'laboratorio/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01')]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
import ic_body as body,social_habitat as social
protect_current();s=Store();name='MAIN_NATIVE_SOCIAL_39';out=EV/(name+'.json')
if out.exists():raise FileExistsError('No overwrite')
if time.monotonic()>json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']:raise TimeoutError('Deadline')
def run(a):
    initial=physical(a.world,occupation=True);plan=social.make_plan(a,name,mode='full',values=(45,));h=body.attach(a)
    try:result=social.run(a,plan)
    finally:h['detach']()
    return{'initial':initial,'social':result,'native_frames':h['frames'],'native_action_after_social':body.report(a),'final':physical(a.world,occupation=True),'not_claimed':'Existing communication shares this trajectory; a functional coupling from received content to the new selector is not established by sharing Runtime.'}
r=s.mutate('E1_INTEGRADO_MAIN','IC01_MAIN_SOCIAL_WITH_NATIVE_BODY',run,{'source_sha256':digest_file(__file__),'reused_social_sha256':digest_file(Path(social.__file__))});atomic_json(out,r);print(r['INSTRUMENTO'],flush=True)
