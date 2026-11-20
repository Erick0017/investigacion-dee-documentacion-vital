"""Validate the sealed exact ZIP after independent extraction; zero new ticks."""
from pathlib import Path
from datetime import datetime,timezone
from zipfile import ZipFile
import hashlib,importlib.util,json,subprocess,sys,time
L=Path(__file__).resolve().parent;R=L.parents[2];E=R/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
C=json.loads((E/'CANDIDATO_SELLADO_01.json').read_bytes());P=Path(C['zip'])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(P)==C['sha256']and P.stat().st_size==C['bytes']and P.stat().st_size<=16000000
outdir=R/'entregas/CONSOLIDACION_EVOLUCION_E1_CICLO_02';outdir.mkdir(exist_ok=True)
target=Path('D:/GENESIS AI/GENESIS 5.0/simulador de universo ab-initio/dee_libreria/VERSION_27/tests/_c02_verify_20261022_01')
if target.exists():raise FileExistsError('Do not silently reuse an extraction')
target.mkdir()
with ZipFile(P)as z:
    assert z.testzip()is None
    for info in z.infolist():
        member=Path(info.filename)
        assert not member.is_absolute()and '..'not in member.parts and ':'not in info.filename and '\\'not in info.filename
    z.extractall(target)
    members=len(z.infolist())
command=[sys.executable,'-I','-B',str(target/'RECALCULO/verificar_exportacion.py'),'--root',str(target),'--salida',str(outdir/'RECALCULO_EXTRAIDO.json')]
t=time.monotonic();p=subprocess.run(command,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=600)
run={'command':command,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'wall_seconds':time.monotonic()-t,'native_ticks':0}
(outdir/'EJECUCION_VERIFICACION_EXTRAIDA.json').write_text(json.dumps(run,ensure_ascii=False,indent=2),encoding='utf8')
if p.returncode:raise RuntimeError('Exact extraction validation failed; preserve candidate and error, do not announce verified: '+p.stderr[-3000:])
verification=json.loads((outdir/'RECALCULO_EXTRAIDO.json').read_bytes())
readable=0
for f in target.rglob('*'):
    if not f.is_file():continue
    if f.suffix.lower()in('.json','.py','.mjs','.md','.csv','.txt'):
        text=f.read_text(encoding='utf-8-sig')
        if f.suffix.lower()=='.json':json.loads(text)
        readable+=1
# Archival IC01 recovery evidence, using the same fixed decoder as C2.
sp=importlib.util.spec_from_file_location('offline_codec',target/'RECALCULO/recalcular.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
historical=[]
for f in sorted((target/'EVIDENCIA_CAUSAL/IC01_ANTECEDENTE').glob('GENERIC_RECOVERY_R2_*.json')):
    data=json.loads(f.read_bytes())['result'];ex=m.external(data['external']);sign=data['old_sign_for_auditor_only']
    n=sum(any(z['qualified']and z['bank']==sign for z in row['social'])for row in ex['rows'])
    historical.append({'file':f.name,'old_content_auditor_only':sign,'uses':ex['steps'],'content_usable':n,'archival_only_no_new_native_ticks':True})
    assert ex['steps']==4 and n==(4 if data['mode']=='recover'else 0)
continuity=json.loads((target/'CONTINUIDAD_CICLO02.json').read_bytes());active=json.loads((R/'sistema/estado/ACTIVO.json').read_bytes());assert active==continuity['active_pointer']
for v in continuity['lives']:assert sha(R/'sistema'/v['snapshot'])==v['snapshot_sha256'],('Source life changed during packaging',v['life_id'])
budget=json.loads((L/'PRESUPUESTO.json').read_bytes());assert time.monotonic()<budget['monotonic_deadline']
result={'utc':datetime.now(timezone.utc).isoformat(),'zip':str(P),'zip_sha256':sha(P),'zip_bytes':P.stat().st_size,'members':members,
 'CRC_all_members':True,'independent_extraction':str(target),'exact_extracted_validation':run,'checks':verification,'UTF8_text_files_checked':readable,
 'archived_IC01_recovery':historical,'active_protected_unchanged':True,'current_life_snapshot_hashes_unchanged':len(continuity['lives']),
 'actual_operational_continuation_evidence':['C02_SEPOP_350_FORK through364_RECARGA: own experience, three codes, new consequence, previous material comparisons, new external use, save and reload in ordinary separate manager processes.','C02_CAPAS_210 through218: finite two-layer access loaded/used/saved/reloaded/continued.','C02_OP_250 through263: message-diversion variant used in ordinary manager processes.'],
 'scope':'Exact ZIP archival recalculation and integrity. Operational continuation was already executed and recorded; it is not repeated or mislabelled as an extracted standalone-system simulation.',
 'native_ticks_during_final_verification':0,'not_a_complete_operative_backup':True,'engine_and_WHL_modified':False,'visual_Word_validation':'BLOCKED: LibreOffice soffice.exe unavailable, actual updated Word/XML included',
 'budget_fixed':budget,'finished_monotonic':time.monotonic(),'sealed_file_unchanged':sha(P)==C['sha256']}
path=outdir/'VERIFICACION_FINAL_EXTERNA.json';path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'verified_zip':str(P),'bytes':P.stat().st_size,'sha256':sha(P),'members':members,'verification':str(path),'checks':{k:v for k,v in verification.items()if k!='complete_snapshot_witnesses'},'historical_recovery':historical},ensure_ascii=False))
