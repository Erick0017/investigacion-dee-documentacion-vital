from pathlib import Path
import sys,json,subprocess,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from app.native_tools import atomic_json,digest_file
from app.process_control import protect_current
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds'];life='E1_INTEGRADO_CONTINUABLE_01'
spec={'life':life,'start_tick_required':7708,'start_external_index':63,'chunks':8,'steps_per_chunk':16,'max_external_index':191,'stop':'3 consecutive out-of-domain magnitude readings or environmental episode bound; retain actual failed future','purpose':'Test prolonged use of retained native magnitude and received positive relation after actual old-function panel, no new B teaching or hand repair. Constant torque is not competent control. This is one life, not128 independent trials.','future_queries':'Fixed67ticks per0.05s. No performance-dependent wait, reader swap or codec change.'}
if not(EV/'LONG_CONTINUATION_SPEC_162.json').exists():atomic_json(EV/'LONG_CONTINUATION_SPEC_162.json',spec)
for i in range(8):
    output=EV/('LONG_SYSTEM_CONTINUATION_'+str(i+1)+'_162.json')
    if output.exists():continue
    if time.monotonic()>deadline-2400:break
    rec=s.record(life);argv=[sys.executable,'-B',str(ROOT/'sistema/gestionar.py'),'integrado-externo','--vida',life,'--pasos','16'];r=subprocess.run(argv,cwd=ROOT/'sistema',capture_output=True,text=True,encoding='utf8',timeout=300)
    if r.returncode:atomic_json(EV/('LONG_SYSTEM_FAILURE_'+str(i+1)+'_162.json'),{'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'before':rec['snapshot_sha256']});raise RuntimeError('Continuation failed, no rewind')
    d=json.loads(r.stdout);atomic_json(output,d);atomic_json(EV/('LONG_SYSTEM_PROCESS_'+str(i+1)+'_162.json'),{'argv':argv,'returncode':r.returncode,'before_snapshot':rec['snapshot_sha256'],'after_snapshot':s.record(life)['snapshot_sha256'],'new_process':True})
    print('LONG '+str(i+1)+' '+str(d['INSTRUMENTO']['tick']),flush=True)
    if d['result']['final_environment'].get('stop_reason'):break
atomic_json(EV/'LONG_SYSTEM_FINAL_162.json',{'spec':spec,'final_record':s.record(life),'active_unchanged':s.record()['life_id']=='E1_SOCIAL_11'})
