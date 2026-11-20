"""Verify an exact analysis ZIP by independent extraction; no native simulation.

Hashes, lossless byte extractions, fixed-decoder recalculation and flat CSV
contents are checked separately. This is not a cognitive PASS criterion.
"""
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import argparse,hashlib,json,zipfile,tarfile,csv,subprocess,sys,time,gzip,lzma,importlib.util
p=argparse.ArgumentParser();p.add_argument('--zip',type=Path,required=True);p.add_argument('--system',type=Path,required=True);p.add_argument('--extract',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();began=time.perf_counter();a.extract.mkdir(parents=True,exist_ok=False)
def sha(b):return hashlib.sha256(b).hexdigest()
def sha_file(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(p.read_bytes())
result={'schema':'AA01.exact_final_zip_verification.v1','started_utc':datetime.now(timezone.utc).isoformat(),'tested_zip':str(a.zip),'zip_bytes':a.zip.stat().st_size,'zip_sha256':sha_file(a.zip),'extraction':str(a.extract),'no_simulation_or_new_material_probe':True,'claims':'Technical integrity and recalc, not a scientific global verdict.'}
try:
    if a.zip.stat().st_size>=16_000_000:raise ValueError('Strict16,000,000byte limit')
    with zipfile.ZipFile(a.zip)as z:
        names=z.namelist()
        if len(names)!=len(set(names)):raise ValueError('Duplicate ZIP member')
        for info in z.infolist():
            path=PurePosixPath(info.filename)
            if path.is_absolute()or'..'in path.parts or'\\'in info.filename or':'in info.filename:raise ValueError('Unsafe member')
            if info.file_size>512*1024*1024:raise ValueError('Unexpected huge individual member')
        if z.testzip()is not None:raise ValueError('ZIP CRC failure')
        z.extractall(a.extract)
    manifest=read(a.extract/'MANIFIESTO_HASHES.json');expected_names={q['path']for q in manifest['members']}|{'MANIFIESTO_HASHES.json'}
    if set(names)!=expected_names:raise ValueError('Manifest membership mismatch')
    for item in manifest['members']:
        target=a.extract/item['path']
        if target.stat().st_size!=item['bytes']or sha_file(target)!=item['sha256']:raise ValueError('Member hash mismatch '+item['path'])
        if target.suffix in('.md','.csv','.py','.mjs','.json'):
            target.read_text(encoding='utf-8-sig')
            if target.suffix=='.json':read(target)
    result['zip_members']=len(names);result['all_member_hashes_and_text_readability']=True
    index=read(a.extract/'INDICE_FUENTES_Y_OMISIONES.json');included={q['included_member']:q for q in index['files']if'included_member'in q};verified=set()
    for name,item in included.items():
        target=a.extract/name
        if target.is_file():
            if target.stat().st_size!=item['included_bytes']or sha_file(target)!=item['included_sha256']:raise ValueError('Indexed extracted member mismatch '+name)
            verified.add(name)
    with tarfile.open(a.extract/'EVIDENCIA_ESENCIAL/PRIMARIOS_Y_TESTIGOS.tar.xz','r|xz')as tf:
        for m in tf:
            if not m.isfile():continue
            b=tf.extractfile(m).read()
            if m.name not in included:raise ValueError('Unindexed primary archive member '+m.name)
            q=included[m.name]
            if len(b)!=q['included_bytes']or sha(b)!=q['included_sha256']:raise ValueError('Inner exact bytes mismatch '+m.name)
            b.decode('utf8')
            if m.name.endswith('.json'):json.loads(b)
            verified.add(m.name)
    if set(included)!=verified:raise ValueError('Indexed included data absent '+str(sorted(set(included)-verified)[:3]))
    source_map=read(a.extract/'CODIGO_Y_RECALCULO/MAPA_FUENTES_EJECUTADAS.json');source_count=0
    with tarfile.open(a.extract/'CODIGO_Y_RECALCULO/FUENTES_POR_HASH.tar.xz','r|xz')as tf:
        for m in tf:
            if not m.isfile():continue
            h=PurePosixPath(m.name).stem;b=tf.extractfile(m).read()
            if h not in source_map or sha(b)!=h or len(b)!=source_map[h]['bytes']:raise ValueError('Executed source object mismatch')
            b.decode('utf8');source_count+=1
    result['exact_indexed_included_members']=len(verified);result['source_objects_verified']=source_count
    originals=0
    for q in index['files']:
        target=a.system.parent/q['path']if q['root']=='SYSTEM_ROOT'else Path(q['path'])
        if not target.exists():raise FileNotFoundError('Original indexed source missing '+str(target))
        if target.stat().st_size!=q['bytes']or sha_file(target)!=q['sha256']:raise ValueError('Original source hash mismatch '+str(target))
        originals+=1
    result['local_original_sources_hashed']=originals
    spec=importlib.util.spec_from_file_location('aa01_engine_free_recalc',a.extract/'CODIGO_Y_RECALCULO/recalcular_acceso.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    selected=read(a.extract/'EVIDENCIA_ESENCIAL/CONTEXTOS_ADVERSOS_03/PROCEDENCIA.json');selected_count=0
    for q in selected['records']:
        b=lzma.decompress((a.extract/q['included_member']).read_bytes())
        if sha(b)!=q['selected_exact_sha256']or len(b)!=q['selected_exact_bytes']:raise ValueError('Selected adverse field hash')
        with gzip.open(q['source'],'rb')as f:f.seek(q['selected_decompressed_byte_offset']);original=f.read(q['selected_exact_bytes'])
        if b!=original:raise ValueError('Selected adverse line not original bytes')
        for loc,v in module.walk(json.loads(b)):
            if{'rows','clock_default','clock_exceptions','N','RAW_sha256','clocks_sha256'}<=v.keys()and v['clock_exceptions']is not None:
                check=module.frame_check(v)
                if not all(check['matches'].values())or not check['row_clock_match']:raise ValueError('Selected global field reconstruction')
                selected_count+=1
    result['extra_dense_adverse_original_fields_verified']=selected_count
    argv=[sys.executable,'-I','-B','-X','utf8',str(a.extract/'CODIGO_Y_RECALCULO/recalcular_acceso.py'),'--root',str(a.extract),'--out',str(a.extract.parent/(a.extract.name+'_RECALCULO.json')),'--deep'];t=time.perf_counter();r=subprocess.run(argv,cwd=a.extract,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=420)
    result['recalculation']={'argv':argv,'exit_code':r.returncode,'seconds':time.perf_counter()-t,'stdout':r.stdout.decode('utf8','replace'),'stderr':r.stderr.decode('utf8','replace')}
    if r.returncode:raise ValueError('Extracted portable recalculation failed')
    fresh=read(Path(argv[-2]));expected=read(a.extract/'CODIGO_Y_RECALCULO/RECALCULO.json')
    if fresh!=expected:raise ValueError('Recalculation differs from sealed expected data')
    result['recalculation']['exact_expected_object_equality']=True;result['recalculation']['totals']=fresh['totals'];result['recalculation']['field_checks']=fresh['field_checks'];result['recalculation']['frame_checks']=fresh['frame_checks']
    tables=read(a.extract/'CODIGO_Y_RECALCULO/TABLAS_DATOS.json');counts={}
    def text(v):return''if v is None else str(v).lower()if type(v)is bool else str(v)
    for key,name in(('trials','TABLA_TODOS_LOS_ENSAYOS.csv'),('capabilities','CAPACIDADES_POR_VIDA.csv'),('recovery','RECUPERACION_RETENCION_REAPRENDIZAJE.csv')):
        with(a.extract/name).open(encoding='utf-8-sig',newline='')as f:rows=list(csv.reader(f))
        if rows[1:]!=[[text(v)for v in row]for row in tables[key]]:raise ValueError('CSV changed source values '+name)
        counts[name]=len(rows)-1
    result['tables_exact_source_values']=counts
    closure=read(a.extract/'EVIDENCIA_ESENCIAL/CIERRE_OPERATIVO_52.json');result['operative_continuation']={'evidence':'CONTINUIDAD_OPERATIVA_49 plus local complete checkpoints','new_native_execution_by_this_zip_verifier':False,'learned_ready_states':{k:{'tick':closure['states'][k]['tick'],'snapshot_sha256':closure['states'][k]['snapshot_sha256'],'pending_count':closure['states'][k]['pending_count']}for k in closure['learned_ready_states']},'protected_default_exact':closure['states']['E1_SOCIAL_11']['snapshot_sha256']=='51e2ec6a41f906607848c003c6a22e3e33690f57d20dcae90c8dbbc7ab9ad396','analysis_does_not_include_full_restore_states':True}
    result['technical_result']='INTEGRITY_AND_RECALCULATION_VERIFIED_WITH_STATED_SCIENTIFIC_LIMITATIONS'
except Exception as error:
    result['technical_result']='NOT_VERIFIED';result['error']={'type':type(error).__name__,'detail':str(error)};raise
finally:
    result['ended_utc']=datetime.now(timezone.utc).isoformat();result['verification_seconds']=time.perf_counter()-began;budget=read(a.system.parent/'evidencia/campanas/ACCESO_ADAPTATIVO_01/PRESUPUESTO.json');result['total_elapsed_from_first_command_seconds']=time.perf_counter()-budget['start_monotonic'];result['budget_seconds']=budget['budget_seconds'];a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:result[k]for k in('zip_bytes','zip_sha256','zip_members','technical_result','verification_seconds','total_elapsed_from_first_command_seconds')},ensure_ascii=False))
