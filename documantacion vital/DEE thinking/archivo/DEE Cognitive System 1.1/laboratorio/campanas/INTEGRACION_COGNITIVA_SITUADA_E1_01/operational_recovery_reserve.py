"""New reserve cases through the installed manager, no laboratory imports."""
from pathlib import Path
import sys,json,subprocess,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';SYSTEM=ROOT/'sistema';sys.path.insert(0,str(SYSTEM))
from app.lives import Store
from app.native_tools import atomic_json,digest_file
from app.process_control import protect_current
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
cases=[('AGED','E1_INTEGRADO_RECUPERACION_01','E1_INTEGRADO_CONTINUABLE_01',False),('AGED_SHAM','IC01_RECOVERY_AGED_SHAM_170','E1_INTEGRADO_CONTINUABLE_01',True),('NO_OLD_CONTENT','IC01_RECOVERY_NO_CONTENT_170','IC01_INTEGRATED_NO_B_134',False)]
spec={'frozen_before_reserves':True,'cases':cases,'no_old_content_is_a_real_different_history':True,'fixed_resources_and_reader':'Same generic zero-load Z+ both signs, alternative zminus3 wires and original wires; no answer-dependent port choice.','aged_source_tick':16485,'aged_external_index':193,'scope':'Late reserve + no-old-content specificity using ordinary admitted commands; protected defaults and failed futures unchanged.'}
if not(EV/'OPERATIONAL_RECOVERY_SPEC_170.json').exists():atomic_json(EV/'OPERATIONAL_RECOVERY_SPEC_170.json',spec)
for tag,life,parent,sham in cases:
    if time.monotonic()>deadline-2400:raise TimeoutError('Closing reserve')
    if not s.life_dir(life).exists():s.fork(parent,life,kind='CANDIDATE'if tag=='AGED'else'DIAGNOSTIC_COPY')
    commands=[['integrado-experiencia','--vida',life,'--tipo','social','--parametros',json.dumps({'name':'RESERVE_'+tag+'_170','mode':'no_partner'})],['integrado-externo','--vida',life,'--pasos','2'],['integrado-recuperar-social','--vida',life]+(['--sham']if sham else[]),['integrado-externo','--vida',life,'--pasos','4']]
    if tag=='AGED':commands.extend([['integrado-externo','--vida',life,'--reiniciar-entorno','--semilla','81031','--pasos','2'],['integrado-panel','--vida',life],['integrado-externo','--vida',life,'--pasos','1']])
    for i,command in enumerate(commands):
        out=EV/('OPERATIONAL_RECOVERY_'+tag+'_'+str(i+1)+'_170.json')
        if out.exists():continue
        before=s.record(life);r=subprocess.run([sys.executable,'-B',str(SYSTEM/'gestionar.py'),*command],cwd=SYSTEM,capture_output=True,text=True,encoding='utf8',timeout=240)
        if r.returncode:atomic_json(EV/('OPERATIONAL_RECOVERY_ERROR_'+tag+'_'+str(i+1)+'_170.json'),{'stderr':r.stderr,'stdout':r.stdout,'returncode':r.returncode,'before':before['snapshot_sha256']});raise RuntimeError('Reached state retained; no fallback')
        atomic_json(out,json.loads(r.stdout));print('RECOVERY_RESERVE '+tag+' '+str(i+1)+' '+str(s.record(life)['physical']['tick']),flush=True)
    atomic_json(EV/('OPERATIONAL_RECOVERY_FINAL_'+tag+'_170.json'),{'final_record':s.record(life),'spec':spec})
