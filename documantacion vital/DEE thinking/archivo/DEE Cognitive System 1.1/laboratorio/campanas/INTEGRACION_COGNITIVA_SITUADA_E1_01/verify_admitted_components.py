from pathlib import Path
import sys,json,subprocess,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';SYSTEM=ROOT/'sistema'
sys.path.insert(0,str(SYSTEM))
from app.lives import Store
from app.native_tools import atomic_json,digest_file
from app.process_control import protect_current
protect_current();s=Store();life='IC01_SISTEMA_NATIVO_163'
if time.monotonic()>json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']-2400:raise TimeoutError('Close reserve')
expected=json.loads((EV/'MAIN_OWN_ACQUISITION_37.json').read_text())['INSTRUMENTO']['snapshot_sha256'];parent=next(p for p in(SYSTEM/'estado/checkpoints').glob('E1_INTEGRADO_MAIN.T3312.*')if digest_file(p)==expected)
if not s.life_dir(life).exists():s.fork('E1_INTEGRADO_MAIN',life,kind='DIAGNOSTIC_COPY',checkpoint=str(parent.relative_to(SYSTEM)))
commands=[['integrado-experiencia','--vida',life,'--tipo','programar','--parametros',json.dumps({'name':'SYSTEM_NATIVE_163','contexts':[1,1,-1,-1,1,1],'shunt':'none'})],['integrado-continuar','--vida',life,'--hasta','3691']]
for i,command in enumerate(commands):
    path=EV/('ADMITTED_NATIVE_COMPONENT_'+str(i+1)+'_163.json')
    if path.exists():continue
    r=subprocess.run([sys.executable,'-B',str(SYSTEM/'gestionar.py'),*command],cwd=SYSTEM,capture_output=True,text=True,encoding='utf8',timeout=180)
    if r.returncode:atomic_json(EV/('ADMITTED_COMPONENT_FAILURE_'+str(i+1)+'_163.json'),{'stdout':r.stdout,'stderr':r.stderr,'returncode':r.returncode});raise RuntimeError('Admitted component test failed; reached life retained')
    atomic_json(path,json.loads(r.stdout));print('ADMITTED_NATIVE '+str(i+1),flush=True)
from capacidades import conductos_acceso_aa01 as old
before=old.turning_inputs
from capacidades.integracion_situada_01 import ic_native_core as core
directions=[(x,y,z)for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)if(x,y,z)!=(0,0,0)]
checks=[]
for incoming in directions:
    for outgoing in directions:
        try:a=before(incoming,outgoing)
        except Exception as e:
            try:core._same_turn(incoming,outgoing)
            except Exception as b:checks.append(type(e).__name__==type(b).__name__);continue
            checks.append(False);continue
        checks.append(a==core._same_turn(incoming,outgoing))
atomic_json(EV/'PURE_TRANSPORT_EQUIVALENCE_163.json',{'native_ticks':0,'pairs':len(checks),'exact_pulse_list_equal':sum(checks),'shared_function_not_replaced':old.turning_inputs is before,'sources':{p.name:digest_file(p)for p in[SYSTEM/'capacidades/integracion_situada_01/ic_native_core.py',SYSTEM/'capacidades/conductos_acceso_aa01.py']},'scope':'Exact pure finite-geometry equivalence, not a new learning sample or general native regression.'})
