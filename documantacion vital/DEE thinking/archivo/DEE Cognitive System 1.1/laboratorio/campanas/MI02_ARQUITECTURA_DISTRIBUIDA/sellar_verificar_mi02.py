"""Seal one <=16,000,000byte analysis ZIP and verify its exact extracted bytes.

No native simulation, no life restoration, no engine import, no historical
corpus replay. Delta checks use an explicitly synthetic file-only fixture.
"""
import gzip,hashlib,io,json,os,shutil,subprocess,sys,tempfile,time,tokenize,zipfile
from pathlib import Path
from datetime import datetime,timezone
from xml.etree import ElementTree as ET
sys.stdout.reconfigure(encoding='utf8')
L=Path(__file__).resolve().parent;R=L.parents[2];S=R/'sistema';stage=L/'PAQUETE_ANALISIS_CANDIDATO_02';deliver=R/'entregas';deliver.mkdir(exist_ok=True)
name='DEE_COGNITIVE_1_1_MI02_ARQUITECTURA_DISTRIBUIDA_ANALISIS.zip';destination=deliver/name
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
def run(command,cwd):
    cp=subprocess.run(command,cwd=cwd,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=300)
    result={'command':command,'returncode':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr}
    if cp.returncode:raise RuntimeError(json.dumps(result,ensure_ascii=False))
    return result

budget=json.loads((L/'PRESUPUESTO.json').read_bytes());assert time.monotonic()<budget['monotonic_deadline'];assert not destination.exists(),'Never overwrite a prior sealed delivery'
for p in L.glob('*.py'):shutil.copy2(p,stage/'CODIGO_EXACTO/CAMPANA'/p.name)
for p in L.glob('*.mjs'):shutil.copy2(p,stage/'CODIGO_EXACTO/CAMPANA'/p.name)
shutil.copy2(L/'recalcular_mi02.py',stage/'RECALCULO/recalcular_mi02.py');shutil.copy2(L/'RECALCULO_FINAL_MI02.json',stage/'RECALCULO/RESULTADO_REFERENCIA.json');shutil.copy2(L/'verificar_tablas.py',stage/'RECALCULO/verificar_tablas.py');shutil.copy2(L/'LEER_ANALISIS_MI02.md',stage/'LEER_PRIMERO.md');shutil.copy2(L/'aplicar_delta_mi02.py',stage/'DELTA_APLICACION/aplicar_delta_mi02.py')
reference=json.loads((stage/'RECALCULO/RESULTADO_REFERENCIA.json').read_bytes());assert reference['historical_parent_validation']['nonzero_RAW_before_added_frame']==0
old_registry=json.loads((L/'CATALOGO_ANTES_CIERRE_MI02.json').read_bytes());new_registry=json.loads((S/'capacidades/CATALOGO_CAPACIDADES.json').read_bytes());old_entries={x['id']:x for x in old_registry['entries']if not x['id'].startswith('MI02_')};new_entries={x['id']:x for x in new_registry['entries']};assert all(new_entries.get(k)==v for k,v in old_entries.items())
write(stage/'DOCUMENTACION/CATALOGO_HEREDADO_PRESERVADO.json',{'historical_entries_unchanged':len(old_entries),'baseline_catalogue_sha256':sha(L/'CATALOGO_ANTES_CIERRE_MI02.json'),'current_catalogue_sha256':sha(S/'capacidades/CATALOGO_CAPACIDADES.json'),'scope':'Structural catalogue preservation, NOT a repeated physical validation of all historical capabilities. No old entry is promoted into a new life by this check.','native_ticks':0})
files=sorted(p for p in stage.rglob('*')if p.is_file()and p.name!='MANIFIESTO.json')
manifest={'scope':'Private MI02 essential scientific analysis and code delta. Not an intact historical archive or standalone operative system.','assembled_utc':datetime.now(timezone.utc).isoformat(),'members':[{'path':p.relative_to(stage).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in files],'self_excluded':True,'zip_hash_outside_container':True,'member_timestamp_policy':'Fixed2026-10-22packaging timestamp for reproducibility; experiment times are inside the primary records','native_ticks_during_sealing':0}
write(stage/'MANIFIESTO.json',manifest)
candidate=L/'MI02_CANDIDATO_SELLADO_01.zip';assert not candidate.exists(),'Preserve any prior sealed candidate'
with zipfile.ZipFile(candidate,'w',zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True)as z:
    for p in sorted(p for p in stage.rglob('*')if p.is_file()):
        arc=p.relative_to(stage).as_posix();info=zipfile.ZipInfo(arc,date_time=(2026,10,22,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,p.read_bytes(),compresslevel=9)
if candidate.stat().st_size>16000000:raise RuntimeError('Candidate exceeds absolute transfer limit; preserve it and compact without removing indispensable evidence')
encoded_hash=sha(candidate);temp_root=Path(tempfile.gettempdir()).resolve();extracted=Path(tempfile.mkdtemp(prefix='mi02_extraccion_')).resolve();assert extracted.is_relative_to(temp_root)
with zipfile.ZipFile(candidate)as z:
    assert z.testzip()is None;names=z.namelist();assert len(names)==len(set(names));assert len(names)==len(manifest['members'])+1
    for member in names:
        p=Path(member)
        if p.is_absolute()or'..'in p.parts or not(extracted/p).resolve().is_relative_to(extracted):raise ValueError('Unsafe archive path')
    z.extractall(extracted)
text_encodings={}
for member in manifest['members']:
    p=extracted/member['path'];assert p.stat().st_size==member['bytes']and sha(p)==member['sha256']
    if p.suffix in('.md','.json','.csv','.mjs','.py','.txt'):
        payload=p.read_bytes();encoding=tokenize.detect_encoding(io.BytesIO(payload).readline)[0]if p.suffix=='.py'else'utf-8-sig';payload.decode(encoding);text_encodings[encoding]=text_encodings.get(encoding,0)+1
        if p.suffix=='.json':json.loads(payload)
    if p.suffix=='.docx':
        with zipfile.ZipFile(p)as doc:
            assert doc.testzip()is None
            for item in doc.namelist():
                if item.endswith('.xml'):ET.fromstring(doc.read(item))
            body=doc.read('word/document.xml').decode('utf8');assert'25 Arquitectura distribuida MI02 y alcance operativo'in body and'T81207'in body and'T20021'in body
portable=run([sys.executable,'-I','-B',str(extracted/'RECALCULO/recalcular_mi02.py'),'--raiz',str(extracted),'--comparar',str(extracted/'RECALCULO/RESULTADO_REFERENCIA.json')],extracted)
tables=run([sys.executable,'-I','-B',str(extracted/'RECALCULO/verificar_tablas.py')],extracted)
delta_manifest=json.loads((extracted/'DELTA_APLICACION/MANIFIESTO_DELTA.json').read_bytes());fixture=Path(tempfile.mkdtemp(prefix='mi02_delta_fixture_')).resolve();assert fixture.is_relative_to(temp_root)
(fixture/'app').mkdir();(fixture/'contratos').mkdir();(fixture/'capacidades').mkdir()
(fixture/'app/lives.py').write_bytes(b'# Synthetic file-presence fixture only. No participant or engine.\n');(fixture/'contratos/PERFILES.json').write_text('{"fixture_only":true}',encoding='utf8')
manager=next(x for x in delta_manifest['files']if x['path']=='gestionar.py');old=None
for h in manager['known_previous_sha256']:
    p=extracted/'CODIGO_EXACTO/FUENTES_POR_SHA256'/(h+'.py')
    if p.exists()and h!=manager['sha256']and b'mi02-'not in p.read_bytes():old=p;break
if old is None:old=extracted/'DELTA_SISTEMA/gestionar.py'
shutil.copy2(old,fixture/'gestionar.py')
registry=json.loads((extracted/'DELTA_SISTEMA/capacidades/CATALOGO_CAPACIDADES.json').read_bytes());registry['entries']=[x for x in registry['entries']if not x['id'].startswith('MI02_')];unrelated=json.loads(json.dumps(registry['entries']));registry['fixture_only_non_cognitive_marker']='Preserve this unrecognized root metadata';write(fixture/'capacidades/CATALOGO_CAPACIDADES.json',registry)
installer=extracted/'DELTA_APLICACION/aplicar_delta_mi02.py';delta_first=run([sys.executable,'-I','-B',str(installer),'--sistema',str(fixture),'--aplicar'],extracted);delta_second=run([sys.executable,'-I','-B',str(installer),'--sistema',str(fixture),'--aplicar'],extracted)
one=json.loads(delta_first['stdout']);two=json.loads(delta_second['stdout']);assert all(x['action']=='SKIP'for x in two['files']);assert two['backup']is None
reg_after=json.loads((fixture/'capacidades/CATALOGO_CAPACIDADES.json').read_bytes());assert[x for x in reg_after['entries']if not x['id'].startswith('MI02_')]==unrelated;assert reg_after['fixture_only_non_cognitive_marker']=='Preserve this unrecognized root metadata';assert not(fixture/'estado/ACTIVO.json').exists()
for row in delta_manifest['files']:
    if row['path']!='capacidades/CATALOGO_CAPACIDADES.json':assert sha(fixture/row['path'])==row['sha256']
assert not any((S/'estado/locks').glob('*MI02*.lock'))
active=json.loads((S/'estado/ACTIVO.json').read_bytes());assert active['life_id']=='E1_SOCIAL_11'and active['tick']==3154;assert sha(S/active['snapshot'])=='51e2ec6a41f906607848c003c6a22e3e33690f57d20dcae90c8dbbc7ab9ad396'
assert sha(R/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_7_MI01_SIN_VALIDACION_VISUAL.docx')=='8a73d88bcdc3fbefb9537bc2026480c7d9762021e058d2a8d27954b6216984d9'
shutil.copy2(candidate,destination);assert sha(destination)==encoded_hash
with zipfile.ZipFile(destination)as z:assert z.testzip()is None
verification={'zip':str(destination),'zip_sha256':encoded_hash,'compressed_bytes':destination.stat().st_size,'absolute_limit_bytes':16000000,'file_members':len(manifest['members'])+1,'member_hashes_verified':len(manifest['members']),'ZIP_CRC_valid':True,'clean_extraction':str(extracted),'portable_recalculation':portable,'CSV_verification':tables,'text_encodings_verified':text_encodings,'delta_file_fixture':{'path':str(fixture),'scope':'Synthetic file transaction only. Does NOT reconstruct a cognitive life or validate native physics.','first_apply':one,'second_apply_all_skip':True,'unrelated_registry_entries_preserved':True,'ACTIVO_not_created':True},'active_protected':active,'prior_manual_unchanged':True,'native_replay_from_analysis_zip':False,'native_execution_evidence':'Recorded normal gestor operations and full local snapshots, archived in the analysis; no new native ticks in this verification.','manual_visual_validation':False,'manual_render_blocker':'LibreOffice soffice.exe not found on PATH','other_life_locks_not_removed':[str(p)for p in(S/'estado/locks').glob('*.lock')],'native_ticks_during_verification':0,'verified_utc':datetime.now(timezone.utc).isoformat(),'elapsed_campaign_seconds':time.monotonic()-(budget['monotonic_deadline']-budget['maximum_seconds']),'deadline_utc':budget['deadline_utc'],'not_a_cognitive_PASS':True}
write(deliver/'VERIFICACION_FINAL_EXTERNA_MI02.json',verification)
print(json.dumps({k:verification[k]for k in['zip','zip_sha256','compressed_bytes','file_members','member_hashes_verified','ZIP_CRC_valid','manual_visual_validation','verified_utc','elapsed_campaign_seconds']},ensure_ascii=False,indent=2),flush=True)
