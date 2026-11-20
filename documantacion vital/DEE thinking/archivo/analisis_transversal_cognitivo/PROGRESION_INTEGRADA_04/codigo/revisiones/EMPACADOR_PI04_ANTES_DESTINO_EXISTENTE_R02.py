"""Seal one PI04 ANALYSIS ZIP only after actual scientific/documentary closure.

Default is a read-only prerequisite/selection plan. Root alone invokes
--crear-y-verificar: refresh the directed selection, include literal current
Manual1.31, write Deflate ZIP, verify every byte from a short clean extraction,
and execute ONLY the preserved stdlib documentary verifier. Never Native.
"""
from pathlib import Path, PurePosixPath
import argparse
import csv
import datetime
import hashlib
import io
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
W = P.parents[4]
C = R / 'DEE Cognitive 2.0'
S = C / 'sistema'
RP = C / 'reproducibilidad'
D = P / 'documentos'
LIMIT = 15_000_000
NAME = 'DEE_PROGRESION_INTEGRADA_04_2026_11_09_ANALISIS.zip'
MANIFEST = '05_CONTROL/MANIFIESTO_SHA256.json'
PUBLICATION = D / 'DOCUMENTOS_PUBLICADOS_PI04_1_31.json'


def need(value, message):
    if not value: raise ValueError(message)
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def digest(data): return hashlib.sha256(data).hexdigest()
def sha(p): return digest(Path(p).read_bytes())
def encoded(value): return (json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def safe_name(name):
    need(isinstance(name,str)and'\\'not in name and'\x00'not in name and':'not in name,'Unsafe ZIP member')
    p=PurePosixPath(name);need(not p.is_absolute()and'..'not in p.parts and all(x not in('','.')for x in p.parts),'Unsafe ZIP member')
    return p.as_posix()
def regular(p):
    p=Path(p).absolute();need(p.resolve(strict=True).is_relative_to(R.resolve()),'Source outside directed DEE scope')
    for node in(p,*p.parents):
        need(not node.is_symlink()and not(getattr(node.lstat(),'st_file_attributes',0)&0x400),'Linked/reparse source refused')
        if node==R:break
    need(p.is_file(),'Regular source required');return p
def exclusive(path,data):
    with Path(path).open('xb')as f:f.write(data)


def validate_docx(data, *, manual=False):
    with zipfile.ZipFile(io.BytesIO(data))as z:
        need(z.testzip()is None,'DOCX CRC failure')
        for name in z.namelist():
            if name.endswith(('.xml','.rels')):ET.fromstring(z.read(name))
        if manual:
            core=ET.fromstring(z.read('docProps/core.xml'))
            need('1.31'in[n.text for n in core if n.tag.endswith('}version')],'Actual full Manual must have internal edition1.31')
            body=z.read('word/document.xml').decode('utf8')
            need('[[CIERRE_REAL_PENDIENTE]]'not in body and'[[PENDIENTE'not in body,'Manual contains unresolved authoring markers')


def prerequisites():
    files=[P/'entrega/00_LEER_PRIMERO.txt',P/'INFORME_CIENTIFICO_PI04.md',PUBLICATION,
        P/'control/CIERRE_CIENTIFICO_PI04.json',P/'control/DECISION_NO_ADOPCION_PI04.json',
        P/'control/CONSERVACION_REGRESION_PI04_VERIFICADA.json',P/'control/C2C_COLD20_NATIVE_VERIFICADA_R01.json',
        P/'control/REGRESION_FIPLUS_REPLICA_CERRADA_R01.json',P/'control/TICKS_NATIVE_CERRADOS_FINAL_PI04.json']
    need(all(p.is_file()for p in files),'Final facts/README/Manual publication/negative replay still missing: '+', '.join(str(p)for p in files if not p.is_file()))
    facts=read(P/'control/CIERRE_CIENTIFICO_PI04.json')
    need(facts.get('closed_for_authoring')is True and facts['principal']['adoption_performed']is False and facts['principal']['life_id']=='ECI02_PI03_MAIN'and facts['principal']['tick']==775355,'Actual closed no-adoption facts required')
    published=read(PUBLICATION)
    need(published.get('status')=='PUBLISHED_LITERAL_STRUCTURALLY_VERIFIED'and published.get('protected_operational_equal')is True and published.get('principal_selectors_modified_by_publisher')is False,'Actual literal1.31 publication proof required')
    for label in('Manual','Compendium'):
        item=published['documents'][label];f=regular(item['published']['path']);b=f.read_bytes()
        need(item['literal_staging_equal']is True and len(b)==item['published']['bytes']and digest(b)==item['published']['sha256'],'Published original document differs: '+label)
        validate_docx(b,manual=label=='Manual')
    need(read(S/'estado/ACTIVO.json')['life_id']=='ECI02_PI03_MAIN','Do not package a guessed principal')
    replica=read(P/'control/REGRESION_FIPLUS_REPLICA_CERRADA_R01.json')
    need(replica.get('Native_execution_by_Root')is True and replica.get('actual_total_Native_ticks')==2055 and all(v is True for v in replica['matches'].values()),'The actual negative technical replay is incomplete or discrepant')
    return facts,published


def build_selection(selection_path,published):
    selection=read(selection_path);items={};dedup=[];missing=[]
    def add(source,member,reason,required=True):
        source=Path(source);member=safe_name(member)
        if not source.is_file():
            if required:raise ValueError('Missing selected source: '+str(source))
            missing.append({'source':str(source),'member':member,'reason':'Not present; not presented as executed'});return
        source=regular(source);b=source.read_bytes()
        need(not source.name.endswith(('.deetsnap.gz','.deetsnap','.sqlite3','.sqlite3-wal','.sqlite3-shm','.whl','.pyd','.exe','.dll','.zip')),'Forbidden full state/engine/archive in analysis selection')
        if member in items:
            need(items[member]['source']==str(source)and items[member]['data']==b,'Duplicate ZIP member collision');return
        need(member.casefold()not in{n.casefold()for n in items},'Case-insensitive extraction collision')
        items[member]={'source':str(source),'data':b,'reason':reason}
    def tree(source,member,reason):
        source=Path(source);need(source.is_dir(),'Required selected directory missing: '+str(source))
        for f in sorted(source.rglob('*')):
            if f.is_file()and'__pycache__'not in f.parts:add(f,member+'/'+f.relative_to(source).as_posix(),reason)
    for row in selection['content']:add(row['source'],row['file'],row['reason'])
    for row in selection.get('pending_required',[]):add(row['source'],row['target'],row['reason'])
    for label in('Manual','Compendium'):
        f=Path(published['documents'][label]['published']['path']);add(f,'02_MANUAL/'+f.name,'Complete literal currently published document')
    add(PUBLICATION,'04_EVIDENCIAS/CONTROL/'+PUBLICATION.name,'Actual publication and protected-state verification')
    for name in('VALIDACION_ESTRUCTURAL_PI04_1_31.json','ACTUALIZACION_DOCUMENTAL_PI04_1_31.json'):
        add(D/name,'04_EVIDENCIAS/CONTROL/'+name,'Document structure/history validation')
    for name in('RENDER_PI04_1_31.json','Manual_RENDER_stdout.txt','Manual_RENDER_stderr.txt',
        'Compendium_RENDER_stdout.txt','Compendium_RENDER_stderr.txt'):
        add(D/name,'04_EVIDENCIAS/CONTROL/RENDER/'+name,'Actual rendering attempts and limitations, not visual approval')
    for name in('REGRESION_FIPLUS_REPLICA_CERRADA_R01.json','REGRESION_FIPLUS_PROTOCOLO_PRE_REPLICA_R01.json',
        'PI04_REGRESION_RET2_R01.json','TICKS_NATIVE_CERRADOS_FINAL_PI04.json',
        'INCORPORACION_MECANISMOS_PRODUCTO_PI04_JSON_R02.json','INCORPORACION_MECANISMOS_PI04_VERIFICACION_ESTATICA_Y_GUIA.json',
        'PUERTA_GESTOR_SYSTEMROOT_OP3.json','INCIDENCIA_CAS_PUERTA_GESTOR_OP1.json'):
        add(P/'control'/name,'04_EVIDENCIAS/CONTROL/'+name,'Actual positive/adverse/technical/incorporation proof')
    for pattern in('PI04_REGRESION_RET2_R01_OP_*.json','PI04_REGRESION_PANEL12_R01_*.json','REGRESION_FIPLUS_R01_CHILD*.txt'):
        for f in sorted((P/'ensayos').glob(pattern)):add(f,'04_EVIDENCIAS/PRIMARIOS/'+f.name,'Actual known-negative Native replay, including expected child exit1')
    need(any(n.endswith('PI04_REGRESION_PANEL12_R01_FIplus.json')for n in items),'Negative reproduced FIplus primary absent')
    need(any(n.endswith('PI04_MAIN_PANEL12_OP2_FIplus.json')for n in items),'Original negative FIplus primary absent')
    # One complete frozen source capsule, no motor or physical states.
    resources=read(RP/'RECURSOS.json');cap=resources['code_capsules']['PI04_C2C_FINAL_OP2'];home=C/cap['product_relative'];manifest=home/cap.get('manifest','SISTEMA_CODIGO.json')
    need(sha(manifest)==cap['manifest_sha256'],'Frozen OP2 capsule manifest changed')
    cm=read(manifest);need(len(cm['files'])==195,'Frozen code capsule expected195 members')
    cap_hashes={}
    for row in cm['files']:
        f=regular(home/row['file']);need(f.stat().st_size==row['bytes']and sha(f)==row['sha256'],'Capsule source member changed')
        target='06_CODIGO/CAPSULA_OP2/'+row['file'];add(f,target,'One exact shared Cognitive capsule, not another life or kernel');cap_hashes[row['sha256']]=target
    add(manifest,'06_CODIGO/CAPSULA_OP2/SISTEMA_CODIGO.json','Exact capsule manifest and local provenance')
    # Deduplicate non-executed loose code copies only. All relative self-contained
    # evidence folders and the whole capsule remain intact for pure verification.
    for name in list(items):
        if name.startswith('06_CODIGO/')and not name.startswith('06_CODIGO/CAPSULA_OP2/'):
            equal=cap_hashes.get(digest(items[name]['data']))
            if equal:
                dedup.append({'omitted_member':name,'source':items[name]['source'],'identical_included_member':equal,'sha256':digest(items[name]['data'])});del items[name]
    for name in('reproducir.py','importar_diagnostico.py','ejecutar_diagnostico.py','propietario_diagnostico.py','observador_pasivo.py',
        'registrar_verificacion.py','comprobar_fisica_final.py','RECURSOS.json','LEER_PRIMERO.md'):
        add(RP/name,'06_CODIGO/RP/'+name,'Actual operative reproduction interface; actor code is not executed by clean verifier')
    for name in('pi04_c2c_adquisicion_20_R01.json','pi04_e3_contingencia_R02.json','panel_12.json'):
        add(RP/'recetas'/name,'06_CODIGO/RP/recetas/'+name,'Exact recipe and fixed evaluation/assistance contract')
    v=RP/'verificaciones/pi04_c2c_adquisicion_20_R01/ECI02_PI03_REPRO_PI04_RP_COLD20_OP2.json'
    add(v,'04_EVIDENCIAS/CONTROL/RP_C2C_REGISTRO_REAL.json','Actual completed cold Native reproduction record')
    add(P/'control/RP_C2C_LISTAR_VERIFICAR_POSTREPLAY_R01/COMPROBACION.json','04_EVIDENCIAS/CONTROL/RP_C2C_GESTOR_LISTAR_VERIFICAR_REAL.json','Actual public read-only operation after registration')
    add(P/'control/F1_GESTOR_INCORPORADO_Y_VERIFICADO.json','04_EVIDENCIAS/CONTROL/F1_GESTOR_INCORPORADO_Y_VERIFICADO.json','Actual public F1 tool use')
    for rel,target in [('sistema/capacidades/CATALOGO_CAPACIDADES.json','03_MAPAS/CATALOGO_PRODUCTO_VIGENTE.json'),
        ('CONTINUIDAD_DEE_COGNITIVE_2_0.json','03_MAPAS/CONTINUIDAD_OPERATIVA_ACTUAL.json'),('PROYECTO.json','03_MAPAS/PROYECTO_ACTUAL.json'),
        ('sistema/estado/ACTIVO.json','03_MAPAS/ACTIVO_ACTUAL.json'),('sistema/estado/vidas/ECI02_PI03_MAIN/VIDA.json','03_MAPAS/VIDA_PRINCIPAL_ACTUAL.json')]:
        add(C/rel,target,'Actual protected-main/documentary pointer, not an executable backup')
    aliases=('PI03_FINAL_T775355','PI03_PI04_C2B_STOP_T800379','PI03_PI04_C2C_POST_DEV_T809763','PI03_PI04_C2C_POST_RES_T816019','PI03_PI04_C2C_CONSERVACION_FALLIDA_T818074')
    pairlocators=[]
    for alias in aliases:
        entry=resources['pairs'][alias];f=C/entry['product_relative']/'EXPORTACION_SERVICIO.json'
        need(sha(f)==entry['manifest_sha256'],'Preserved pair manifest changed: '+alias)
        add(f,'03_MAPAS/PARES/'+alias+'/EXPORTACION_SERVICIO.json','Full-pair file manifest; large payload stays local')
        pairlocators.append({'alias':alias,**entry,'manifest_bytes':f.stat().st_size,'payload_not_in_analysis_ZIP':True})
    for name in('empaquetar_PI04_final.py','preparar_seleccion_PI04.py','verificar_C2C_cold20_cerrado_PI04_R01.py',
        'incorporar_mecanismos_producto_PI04_JSON_R02.py','verificar_incorporacion_y_guia_RP_PI04_R01.py',
        'pi04_verificacion_cli_publica_R01.py','continuar_LINK_por_gestor_PI04_OP3.py','corregir_puerta_system_root_PI04_OP3.py'):
        add(P/'codigo'/name,'06_CODIGO/HERRAMIENTAS/'+name,'Exact localized instrument/packing/incorporation source; not run on extraction')
    # Source names remain locators. No part of the unified verifier opens them.
    omissions={'schema':'DEE.PI04.analysis_coverage_and_omissions.v1','scope':'Analysis and documentary recalculation, not a full executable backup',
        'historical_selection_omissions':selection.get('omissions',[]),'code_duplicates_replaced_by_identical_capsule_member':dedup,
        'full_operational_pair_locators':pairlocators,'missing_optional':missing,
        'not_included':['Universe/Thinking binaries and two official large Thinking manuals','Complete snapshots, SQLite/WAL/SHM, transport outboxes and environment payload trees','Deep repetitive telemetry, old ZIP corpus, staged DOCX backups and videos'],
        'native_reproduction_vs_recalculation':'Native cold replay and adverse technical replay were performed by Root and are evidenced here. Clean verification only recalculates recorded files; it does not execute DEE.'}
    items['05_CONTROL/COBERTURA_Y_OMISIONES.json']={'source':'generated:explicit_selection_and_verified_local_locators','data':encoded(omissions),'reason':'Compact coverage, omissions and stable full-state locators'}
    return items


def validate_content(name,data):
    ext=Path(name).suffix.lower()
    if ext=='.json':json.loads(data.decode('utf-8-sig'))
    elif ext in('.csv','.tsv'):list(csv.reader(io.StringIO(data.decode('utf-8-sig')),delimiter='\t'if ext=='.tsv'else','))
    elif ext=='.jsonl':
        for line in data.decode('utf-8-sig').splitlines():
            if line.strip():json.loads(line)
    elif ext in('.md','.txt','.py','.srt','.jsonl'):data.decode('utf-8-sig')
    elif ext=='.docx':validate_docx(data,manual='DCS11_MM_001'in name)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--crear-y-verificar',action='store_true')
    ap.add_argument('--seleccion',type=Path,help='Existing directed final selection; omitted means run the preserved stdlib selection builder after closure')
    a=ap.parse_args();facts,published=prerequisites()
    if not a.crear_y_verificar:
        print(json.dumps({'mode':'READ_ONLY_READY_TO_PACK','Native_ticks':0,'closed_for_authoring':facts['closed_for_authoring'],
            'manual_internal_edition':'1.31','final_path':str(C/'entregas'/NAME),'action':'Root explicitly invokes --crear-y-verificar after reviewing selection; no ZIP written by this mode.'},ensure_ascii=False));return
    stamp=datetime.datetime.now().astimezone().strftime('%Y%m%d_%H%M%S')
    final=C/'entregas'/NAME;partial=final.with_name(final.name+'.writing');proof=P/'control/VERIFICACION_ZIP_FINAL_PI04.json'
    need(not final.exists()and not partial.exists()and not proof.exists(),'Prior delivery/attempt/proof exists; preserve it instead of overwriting')
    need(final.parent.is_dir(),'Reuse the existing deliveries folder; do not invent a parallel root')
    selected=a.seleccion
    if selected is None:
        selected=P/'entrega'/('SELECCION_FINAL_PI04_'+stamp+'.json')
        process=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(P/'codigo/preparar_seleccion_PI04.py'),'--out',str(selected)],capture_output=True,text=True,encoding='utf8',errors='strict',timeout=180)
        need(process.returncode==0,'Directed selection failed: '+process.stderr[-2000:])
    selected=regular(selected);items=build_selection(selected,published)
    need(all(n in items for n in('00_LEER_PRIMERO.txt','01_INFORME_CIENTIFICO.md','05_RECALCULO/RECALCULAR_EXPEDIENTE_PI04.py')),'Core package missing')
    for n,v in items.items():validate_content(n,v['data'])
    manifest={'schema':'DEE.PI04.analysis_content_manifest.v1','created_local':datetime.datetime.now().astimezone().isoformat(),
        'content':[{'file':n,'bytes':len(v['data']),'sha256':digest(v['data']),'source':v['source']}for n,v in sorted(items.items())],
        'scope':'Sources are provenance locators, never opened by the portable recalculator. Manifest excludes itself and the ZIP; no self-referential hashes.'}
    manifest_bytes=encoded(manifest)
    # All writes below are new output/extraction/verification artifacts only.
    with zipfile.ZipFile(partial,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=False)as z:
        for n,v in sorted(items.items()):z.writestr(n,v['data'])
        z.writestr(MANIFEST,manifest_bytes)
    need(partial.stat().st_size<=LIMIT,'Actual ZIP exceeds15,000,000 bytes; preserve the candidate, do not truncate evidence')
    short=W/('pi04_z'+datetime.datetime.now().strftime('%H%M%S'));need(not short.exists(),'Clean-extraction short directory already exists')
    extraction=short/'x';recalc=short/'r';extraction.mkdir(parents=True)
    with zipfile.ZipFile(partial)as z:
        need(z.testzip()is None,'ZIP member CRC failure');names=z.namelist()
        need(len(names)==len(set(n.casefold()for n in names))and set(names)==set(items)|{MANIFEST},'ZIP member set differs')
        for n in names:
            safe_name(n);data=z.read(n);dest=extraction/Path(*PurePosixPath(n).parts)
            need(dest.resolve().is_relative_to(extraction.resolve()),'Extraction escape')
            need(len(str(dest))<255,'Extraction path exceeds the short Windows budget: '+n)
            dest.parent.mkdir(parents=True,exist_ok=True);exclusive(dest,data)
            if n!=MANIFEST:need(data==items[n]['data'],'Archive member differs from selected bytes');validate_content(n,data)
    current_manual=Path(published['documents']['Manual']['published']['path'])
    copied=extraction/'02_MANUAL'/current_manual.name
    need(copied.read_bytes()==current_manual.read_bytes(),'Complete current Manual bytes differ after extraction')
    command=[sys.executable,'-I','-B','-X','utf8',str(extraction/'05_RECALCULO/RECALCULAR_EXPEDIENTE_PI04.py'),'--raiz',str(extraction),'--destino',str(recalc)]
    process=subprocess.run(command,cwd=extraction,capture_output=True,text=True,encoding='utf8',errors='strict',timeout=480,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    exclusive(short/'verificador.stdout.txt',process.stdout.encode('utf8'));exclusive(short/'verificador.stderr.txt',process.stderr.encode('utf8'))
    need(process.returncode==0,'Clean stdlib verifier failed; ZIP candidate/extraction preserved: '+process.stderr[-2000:])
    verified=read(recalc/'VERIFICACION_EXPEDIENTE_PI04.json')
    need(verified['status']=='DOCUMENTARY_RECALCULATION_VERIFIED'and verified['Native_ticks_executed']==0 and verified['recorded_absolute_source_paths_opened']is False,'Portable verifier scope/result mismatch')
    audits=sorted(recalc.glob('*.AUDIT.json'));need(len(audits)==3,'All3 recalculation children must have actual access-fence witnesses')
    audit_summary=[]
    for f in audits:
        audit=read(f)
        need(not audit['denied']and audit['DEE_or_app_imports']==0 and audit['external_source_locator_opened']is False,'A child attempted undeclared source/import access')
        audit_summary.append({'path':str(f),'sha256':sha(f),'opens_inside_extraction':audit['opens_inside_extraction'],
            'opens_inside_destination':audit['opens_inside_destination'],'opens_inside_stdlib':audit['opens_inside_stdlib'],
            'denied':audit['denied'],'DEE_or_app_imports':audit['DEE_or_app_imports'],'external_source_locator_opened':audit['external_source_locator_opened']})
    # Recheck source hashes rather than claiming whole-project immutability.
    for n,v in items.items():
        if not v['source'].startswith('generated:'):need(sha(Path(v['source']))==digest(v['data']),'Source changed during packaging: '+v['source'])
    prerequisites();need(not final.exists(),'A concurrent final delivery appeared; preserve candidate')
    partial.replace(final)
    result={'schema':'DEE.PI04.final_analysis_ZIP.verified.v1','status':'SEALED_AND_CLEAN_EXTRACTION_VERIFIED',
        'created_local':datetime.datetime.now().astimezone().isoformat(),'zip':{'path':str(final),'bytes':final.stat().st_size,'sha256':sha(final)},
        'strict_limit_bytes':LIMIT,'content_members':len(items),'ZIP_members':len(items)+1,'uncompressed_content_bytes':sum(len(v['data'])for v in items.values()),
        'global_manifest_sha256':digest(manifest_bytes),'selection':{'path':str(selected),'sha256':sha(selected)},
        'clean_extraction':str(extraction),'pure_verification_output':str(recalc),'pure_verifier_command':command,
        'pure_verifier_returncode':process.returncode,'pure_verifier_result':verified,
        'actual_child_access_fences':audit_summary,
        'actual_full_Manual_sha256':sha(current_manual),'copy_byte_identical':True,
        'source_files_hashed_after_packaging':len([v for v in items.values()if not v['source'].startswith('generated:')]),
        'new_Native_ticks':0,'no_originals_modified_by_packager':True,'no_cleanup_performed':True,
        'visual_limit':'DOCX CRC/XML parsing is not visual QA; actual publication/render witness is included separately.',
        'not_an_executable_full_state_backup':True}
    exclusive(proof,encoded(result))
    print(json.dumps({'zip':result['zip'],'verification':{'path':str(proof),'sha256':sha(proof)},'members':len(items)+1,'Native_ticks':0},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
