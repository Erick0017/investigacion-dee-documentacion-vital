from pathlib import Path
import sys,json,subprocess,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';SYSTEM=ROOT/'sistema';sys.path.insert(0,str(SYSTEM))
from app.lives import Store
from app.native_tools import atomic_json
from app.process_control import protect_current
protect_current();s=Store();life='E1_INTEGRADO_CONTINUABLE_01'
if time.monotonic()>json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']-2400:raise TimeoutError('Closing reserve')
for i,args in enumerate([['integrado-panel','--vida',life],['integrado-externo','--vida',life,'--pasos','2']]):
    out=EV/('FINAL_OPERATIONAL_'+str(i+1)+'_165.json')
    if out.exists():continue
    before=s.record(life);r=subprocess.run([sys.executable,'-B',str(SYSTEM/'gestionar.py'),*args],cwd=SYSTEM,capture_output=True,text=True,encoding='utf8',timeout=240)
    if r.returncode:atomic_json(EV/('FINAL_OPERATIONAL_ERROR_'+str(i+1)+'_165.json'),{'stderr':r.stderr,'stdout':r.stdout,'returncode':r.returncode,'before':before['snapshot_sha256']});raise RuntimeError('No fallback')
    atomic_json(out,json.loads(r.stdout));print('FINAL_OPERATIONAL '+str(i+1)+' '+str(s.record(life)['physical']['tick']),flush=True)
atomic_json(EV/'FINAL_OPERATIONAL_RECORD_165.json',{'final_record':s.record(life),'active':s.record()['life_id'],'scope':'Reached state after a real old-function panel and two new external interactions; no selection of a favorable snapshot per function.'})
