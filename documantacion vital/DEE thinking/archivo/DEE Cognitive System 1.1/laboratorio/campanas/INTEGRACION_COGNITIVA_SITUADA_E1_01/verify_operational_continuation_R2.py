"""Use only installed system sources/state; audit reads cannot feed decisions."""
from pathlib import Path
import sys,json,subprocess,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';SYSTEM=ROOT/'sistema'
sys.path.insert(0,str(SYSTEM))
from app.lives import Store
from app.native_tools import atomic_json,digest_file
from app.process_control import protect_current
protect_current();s=Store();life='E1_INTEGRADO_CONTINUABLE_01'
if time.monotonic()>json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']:raise TimeoutError('Original deadline')
before=s.record('IC01_STRESS_MATCHED_144')
if not s.life_dir(life).exists():s.fork('IC01_STRESS_MATCHED_144',life,kind='CANDIDATE')
fixed={'selection':'Complementary finite usable life from an actual no-noise trajectory T7440, not a rewind, repair or replacement of either failed MAIN. Explicitly retain and document losses of the short route selector. Not promoted to active.','source_snapshot':before['snapshot_sha256'],'system_commands':[['integrado-externo','--vida',life,'--pasos','2'],['integrado-panel','--vida',life],['integrado-externo','--vida',life,'--pasos','1']],'scope':'Three separate processes, same life, exact saved Pendulum/RNG/delay/native queues. A material old-function panel is consecutive actual use, not inserted favorable clone knowledge. Pendulum remains paused during the declared native-only panel.'}
atomic_json(EV/'CONTINUATION_SPEC_161.json',fixed)
for i,argv in enumerate(fixed['system_commands']):
    output=EV/('SYSTEM_CONTINUATION_'+str(i+1)+'_161.json')
    if output.exists():continue
    rec_before=s.record(life);r=subprocess.run([sys.executable,'-B',str(SYSTEM/'gestionar.py'),*argv],cwd=SYSTEM,text=True,encoding='utf8',capture_output=True,timeout=180)
    if r.returncode:atomic_json(EV/('SYSTEM_CONTINUATION_FAILURE_R2_'+str(i+1)+'_161.json'),{'returncode':r.returncode,'stderr':r.stderr,'stdout':r.stdout,'before':rec_before['snapshot_sha256']});raise RuntimeError('Real system command failed; reached state retained, no fallback')
    d=json.loads(r.stdout);atomic_json(output,d);atomic_json(EV/('SYSTEM_PROCESS_'+str(i+1)+'_161.json'),{'argv':[sys.executable,'-B',str(SYSTEM/'gestionar.py'),*argv],'returncode':r.returncode,'before_snapshot':rec_before['snapshot_sha256'],'after_snapshot':s.record(life)['snapshot_sha256'],'same_life':life,'new_process_each_operation':True,'stderr':r.stderr})
    print('SYSTEM_PROCESS '+str(i+1)+' '+str(s.record(life)['physical']['tick']),flush=True)
atomic_json(EV/'SYSTEM_CONTINUATION_FINAL_161.json',{'selection':fixed,'final_record':s.record(life),'active_unchanged':s.record()['life_id']=='E1_SOCIAL_11'})
