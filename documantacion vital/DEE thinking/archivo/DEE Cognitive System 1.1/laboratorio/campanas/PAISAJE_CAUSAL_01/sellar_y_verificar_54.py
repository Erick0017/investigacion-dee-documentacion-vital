"""Seal and verify the exact PC01 analysis ZIP; no native physics is executed."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse, ast, csv, hashlib, io, json, shutil, struct, subprocess, sys, time, zipfile, zlib

def sha(path):
    h=hashlib.sha256()
    with path.open('rb')as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def read(path):return json.loads(path.read_bytes())
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def png_crc(data):
    if data[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('Not PNG')
    pos=8;chunks=0
    while pos<len(data):
        n=struct.unpack_from('>I',data,pos)[0];tag=data[pos+4:pos+8];end=pos+8+n
        if end+4>len(data)or zlib.crc32(data[pos+4:end])&0xffffffff!=struct.unpack_from('>I',data,end)[0]:raise ValueError('PNG chunk CRC mismatch')
        chunks+=1;pos=end+4
        if tag==b'IEND':break
    if pos!=len(data)or tag!=b'IEND':raise ValueError('Incomplete PNG')
    return chunks

def main():
    p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--verification-root',type=Path,required=True);p.add_argument('--kernel-source',type=Path,required=True);a=p.parse_args()
    start=time.perf_counter();root=a.system.resolve();stage=a.stage.resolve();lab=root/'laboratorio/campanas/PAISAJE_CAUSAL_01';ev=root/'evidencia/campanas/PAISAJE_CAUSAL_01';deliver=root/'entregas';name='DEE_COGNITIVE_1_1_PAISAJE_CAUSAL_01_ANALISIS.zip';final=deliver/name
    if final.exists():raise FileExistsError('Preserve an existing canonical delivery; do not overwrite blindly')
    if a.verification_root.exists():raise FileExistsError('Use a fresh independent verification folder')
    code=stage/'CODIGO_Y_RECALCULO';ledger=[]
    for src in (Path(__file__).resolve(),lab/'ejecutar_recalculo_aislado.py',lab/'cerrar_candidato_53.py'):
        dest=code/src.name;shutil.copyfile(src,dest);h=sha(src);obj=code/'objetos'/(h+'.py')
        if not obj.exists():shutil.copyfile(src,obj)
        ledger.append({'source':str(src),'copy':dest.relative_to(stage).as_posix(),'sha256':h,'bytes':src.stat().st_size,'role':'Data-only closing/verification source; not native scientific execution'})
    for src in (lab/'INFORME_COMPACTACION.md',lab/'INCIDENTE_CIERRE_53.md'):
        dest=stage/src.name if src.name=='INFORME_COMPACTACION.md'else code/'incidentes'/src.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
    write(code/'CAPTURA_CIERRE_FINAL.json',{'sources':ledger,'no_primary_records_or_native_states_modified':True})
    members=[]
    for path in sorted(stage.rglob('*')):
        if not path.is_file()or path.name in('MANIFIESTO_HASHES.json','HASHES.sha256'):continue
        if '__pycache__'in path.parts or path.suffix.lower()in('.pyd','.whl','.dll'):raise ValueError('Unexpected binary/cache in analysis stage')
        members.append({'path':path.relative_to(stage).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)})
    manifest={'schema':'PC01.analysis_manifest.v1','generated_utc':datetime.now(timezone.utc).isoformat(),'members':members,'payload_member_count':len(members),'payload_expanded_outer_bytes':sum(q['bytes']for q in members),'exclusions':['MANIFIESTO_HASHES.json excludes itself and HASHES.sha256','No hash of the containing ZIP is stored inside it'],'scope':'Private analysis only; not a full operational backup or complete historical archive'}
    write(stage/'MANIFIESTO_HASHES.json',manifest)
    lines=[q['sha256']+'  '+q['path']for q in members]+[sha(stage/'MANIFIESTO_HASHES.json')+'  MANIFIESTO_HASHES.json']
    (stage/'HASHES.sha256').write_text('\n'.join(lines)+'\n',encoding='utf8')
    candidate_folder=deliver/'PAISAJE_CAUSAL_01_SELLADO_54';candidate_folder.mkdir(exist_ok=False);candidate=candidate_folder/name
    with zipfile.ZipFile(candidate,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=False)as z:
        for path in sorted(stage.rglob('*')):
            if path.is_file():z.write(path,path.relative_to(stage).as_posix())
    if candidate.stat().st_size>16000000:raise ValueError('Absolute 16,000,000-byte analysis limit exceeded')
    archive_sha=sha(candidate);verify=a.verification_root.resolve();verify.mkdir(parents=True,exist_ok=False);extracted=verify/'analisis';extracted.mkdir();reports=verify/'comprobantes';reports.mkdir()
    with zipfile.ZipFile(candidate)as z:
        if z.testzip()is not None:raise ValueError('ZIP CRC failure')
        infos=z.infolist();names=[q.filename for q in infos]
        if len(names)!=len(set(names)):raise ValueError('Duplicate ZIP members')
        if sum(q.file_size for q in infos)>256*1024**2:raise ValueError('Unexpected outer expansion')
        for item in infos:
            rel=PurePosixPath(item.filename)
            if item.is_dir()or rel.is_absolute()or'..'in rel.parts or'\\'in item.filename or':'in item.filename or (item.external_attr>>16)&0o170000==0o120000:raise ValueError('Unsafe or unexpected ZIP member')
            dest=extracted.joinpath(*rel.parts);dest.parent.mkdir(parents=True,exist_ok=True)
            with dest.open('xb')as f:f.write(z.read(item))
    actual=read(extracted/'MANIFIESTO_HASHES.json');expected={q['path']:q for q in actual['members']}
    if set(names)!=set(expected)|{'MANIFIESTO_HASHES.json','HASHES.sha256'}:raise ValueError('Manifest coverage mismatch')
    readability={'json':0,'csv':0,'utf8_text':0,'png':0,'current_direct_python_syntax':0}
    for rel,row in expected.items():
        path=extracted/rel
        if path.stat().st_size!=row['bytes']or sha(path)!=row['sha256']:raise ValueError('Extracted member mismatch '+rel)
        if path.suffix=='.json':read(path);readability['json']+=1
        elif path.suffix=='.csv':list(csv.reader(io.StringIO(path.read_text(encoding='utf-8-sig'))));readability['csv']+=1
        elif path.suffix in('.md','.py','.txt','.sha256'):path.read_text(encoding='utf-8-sig');readability['utf8_text']+=1
        elif path.suffix=='.png':png_crc(path.read_bytes());readability['png']+=1
        if path.suffix=='.py'and'/objetos/'not in'/'+rel and'/revisiones_fallidas_preservadas/'not in'/'+rel:
            ast.parse(path.read_text(encoding='utf-8-sig'),filename=rel);readability['current_direct_python_syntax']+=1
    for line in (extracted/'HASHES.sha256').read_text(encoding='utf8').splitlines():
        digest,rel=line.split('  ',1)
        if sha(extracted/rel)!=digest:raise ValueError('Hash-list mismatch')
    commands=[]
    for operation in('data','recalculate'):
        argv=[sys.executable,'-I','-B','-X','utf8',str(extracted/'CODIGO_Y_RECALCULO/ejecutar_recalculo_aislado.py'),'--root',str(extracted),'--output',str(reports),'--operation',operation];t=time.perf_counter();r=subprocess.run(argv,cwd=extracted,capture_output=True,text=True,encoding='utf8',timeout=180)
        (reports/(operation+'.stdout.txt')).write_text(r.stdout,encoding='utf8');(reports/(operation+'.stderr.txt')).write_text(r.stderr,encoding='utf8');commands.append({'argv':argv,'cwd':str(extracted),'returncode':r.returncode,'seconds':time.perf_counter()-t,'stdout':r.stdout,'stderr':r.stderr})
        if r.returncode:write(reports/'INCIDENTE_VERIFICACION.json',commands);raise RuntimeError('Extracted data verification failed: '+operation+' '+r.stderr)
    recomputed=read(reports/'RECALCULO_REHECHO.json');baseline=read(extracted/'ATLAS_CAUSAL/RECALCULO_DATOS.json')
    if recomputed!=baseline:raise ValueError('Fresh extracted ordinary recalculation differs from the preserved independent result')
    deep=read(extracted/'ATLAS_CAUSAL/VERIFICACION_CAMPOS_PROFUNDOS.json');data_index=read(extracted/'EVIDENCIA_ESENCIAL/INDICE_REGISTROS.json')
    if deep['data_archive_sha256']!=sha(extracted/'EVIDENCIA_ESENCIAL/REGISTROS_COMPLETOS.tar.xz')or deep['recalculation_script_sha256']!=sha(extracted/'CODIGO_Y_RECALCULO/recalcular_analisis.py'):raise ValueError('Deep-check binding mismatch')
    local_deep=Path(deep['full_local_result'])
    if sha(local_deep)!=deep['full_local_result_sha256']:raise ValueError('Changed local deep verification receipt')
    # Deep checks already ran on these exact archive and script bytes. Do not
    # mislabel the selected fresh recalculation as a second deep run.
    active=read(root/'sistema/estado/ACTIVO.json')
    if active['life_id']!='E1_SOCIAL_11'or active['tick']!=3154 or active['snapshot_sha256']!='51e2ec6a41f906607848c003c6a22e3e33690f57d20dcae90c8dbbc7ab9ad396':raise ValueError('Protected default changed')
    manual=root/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_0.docx'
    if sha(manual)!='f0d1a71f8dc4aa8d9d72aa1428b9ed62df320897ce4987353122539285f2e6e5':raise ValueError('Received manual edition changed')
    identity=read(ev/'ARRANQUE_01/ESTADO_INICIAL.json')['identity']
    if sha(Path(identity['native']))!='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'or sha(a.kernel_source)!='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31':raise ValueError('Frozen engine/source identity changed')
    states=read(extracted/'CONTINUIDAD_PAISAJE_CAUSAL_01.json')['lives'];state_checks=[]
    for name2,record in states.items():
        path=Path(record['snapshot'])
        if sha(path)!=record['snapshot_sha256']:raise ValueError('Changed complete selected snapshot '+name2)
        state_checks.append({'life':name2,'tick':record['physical']['tick'],'snapshot':str(path),'sha256':record['snapshot_sha256'],'bytes':path.stat().st_size,'verification':'File integrity only at closure; functional continuation is evidenced by earlier native trials, not a new simulation here'})
    # Publish the same verified bytes, never regenerate or edit the tested ZIP.
    with candidate.open('rb')as src,final.open('xb')as dst:shutil.copyfileobj(src,dst)
    if sha(final)!=archive_sha:raise ValueError('Published canonical bytes differ from the tested candidate')
    budget=read(ev/'ARRANQUE_01/PRESUPUESTO.json');mono=time.perf_counter();elapsed=budget['elapsed_conservative_at_capture']+mono-budget['monotonic_capture']
    if mono>=budget['monotonic_deadline']:raise TimeoutError('Final closure exceeded the fixed budget')
    proof={'schema':'PC01.exact_final_zip_external_verification.v1','verified_utc':datetime.now(timezone.utc).isoformat(),'canonical_zip':str(final),'zip_sha256':archive_sha,'compressed_bytes':final.stat().st_size,'absolute_limit_bytes':16000000,'outer_member_count':len(names),'outer_expanded_bytes':sum(q.file_size for q in infos),'inner_scientific_payload_bytes':data_index['payload_expanded_bytes'],'inner_members':len(data_index['members']),'inner_archive_sha256':data_index['archive_sha256'],'primary_cases':data_index['primary_cases'],'zip_CRC_manifest_and_member_hashes':True,'readability':readability,'extraction':str(extracted),'commands':commands,'data_verification':read(reports/'DATOS_VERIFICADOS.json'),'recalculation_summary':recomputed['summary'],'ordinary_result_equals_preserved_result':True,'ordinary_result_exact_bytes_equal':sha(reports/'RECALCULO_REHECHO.json')==sha(extracted/'ATLAS_CAUSAL/RECALCULO_DATOS.json'),'python_read_audits':{name:read(reports/('LECTURAS_'+name+'.json'))for name in('data','recalculate')},'deep_verification':{'global_frames':deep['global_frames_reconstructed'],'route_records':deep['non_global_route_records_separately_counted'],'exact_archive_and_script_binding_verified':True,'not_rerun_during_final_zip_check':True,'source_result_sha256':deep['full_local_result_sha256']},'selected_operational_snapshots_retained_local':state_checks,'official_native_identity_unchanged':True,'kernel_source_identity_unchanged':True,'received_Word_identity_unchanged':True,'manual_update':'Consolidated root addendum; Word editorial merge pending authorized render validation','protected_default':active,'budget':{'reference_start_utc':budget['reference_start_utc'],'first_command_clock_gap':budget['first_command_record_gap'],'deadline_utc':budget['deadline_utc'],'monotonic_sample':mono,'elapsed_conservative_seconds':elapsed,'remaining_seconds':budget['monotonic_deadline']-mono,'not_restarted':True},'closing_verification_seconds':time.perf_counter()-start,'limits':['Analysis ZIP, not an operational snapshot backup','Python read audit is not an OS sandbox','No new native experiment in final packaging','Deep field reconstruction previously performed on exactly the included data/script bytes; selected ordinary recalculation repeated from this exact ZIP','Preserved failed revisions are readable genealogy, not all syntactically valid programs','No P2, general Spanish, AGI or NSM65 mastery verdict'],'no_container_self_hash_inside_zip':True,'private':True}
    write(deliver/'VERIFICACION_FINAL_EXTERNA_PAISAJE_CAUSAL_01.json',proof);write(ev/'VERIFICACION_FINAL_EXTERNA.json',proof)
    write(ev/'CIERRE_FINAL_54.json',{'canonical_zip':str(final),'sha256':archive_sha,'elapsed_conservative_seconds':elapsed,'deadline_utc':budget['deadline_utc'],'native_processes_finished':True,'next_action':'Human review or explicit continuation of an identified complete life; no automatic experiment restart.'})
    print(json.dumps({'zip':str(final),'sha256':archive_sha,'bytes':final.stat().st_size,'files':len(names),'expanded_outer_bytes':sum(q.file_size for q in infos),'inner_payload_bytes':data_index['payload_expanded_bytes'],'recalculation':recomputed['summary'],'elapsed_conservative_seconds':elapsed,'verification_seconds':time.perf_counter()-start},ensure_ascii=False))

if __name__=='__main__':main()
