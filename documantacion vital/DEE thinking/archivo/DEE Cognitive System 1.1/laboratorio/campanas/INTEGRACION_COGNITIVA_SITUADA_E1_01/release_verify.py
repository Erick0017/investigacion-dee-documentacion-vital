from pathlib import Path
import sys,json,subprocess,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';SYSTEM=ROOT/'sistema';sys.path.insert(0,str(SYSTEM))
from app.lives import Store
from app.native_tools import atomic_json
from app.process_control import protect_current
protect_current();s=Store()
if time.monotonic()>json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']-2400:raise TimeoutError('Reserve closing')
cases=[('NEGATIVE_RECOVERY_CONTINUATION_171','IC01_GENERIC_RECOVERY_R2_MINUS_RECOVER_167',1,0),('ENVIRONMENT_HORIZON_REJECTION_172','IC01_LATE_SOCIAL_SAME_166',2,2)]
for name,life,steps,expected_return in cases:
    out=EV/(name+'.json')
    if out.exists():continue
    before=s.record(life);argv=[sys.executable,'-B',str(SYSTEM/'gestionar.py'),'integrado-externo','--vida',life,'--pasos',str(steps)];r=subprocess.run(argv,cwd=SYSTEM,capture_output=True,text=True,encoding='utf8',timeout=180)
    if r.returncode!=expected_return:raise RuntimeError('Unexpected real command outcome; reached state retained: '+r.stderr)
    result=json.loads(r.stdout)if not r.returncode else{'expected_rejection':json.loads(r.stderr),'before':before['physical'],'after':s.record(life)['physical'],'same_native_fields':before['physical']==s.record(life)['physical'],'argv':argv}
    atomic_json(out,result);print(name+' '+str(s.record(life)['physical']['tick']),flush=True)
active=s.record();atomic_json(EV/'ACTIVE_PROTECTED_RELEASE_172.json',{'life':active['life_id'],'tick':active['physical']['tick'],'snapshot':active['snapshot'],'snapshot_sha256':active['snapshot_sha256'],'expected_initial_sha256':'51e2ec6a41f906607848c003c6a22e3e33690f57d20dcae90c8dbbc7ab9ad396','exact_protected_snapshot_unchanged':active['snapshot_sha256']=='51e2ec6a41f906607848c003c6a22e3e33690f57d20dcae90c8dbbc7ab9ad396','native_ticks_in_this_check':0})
