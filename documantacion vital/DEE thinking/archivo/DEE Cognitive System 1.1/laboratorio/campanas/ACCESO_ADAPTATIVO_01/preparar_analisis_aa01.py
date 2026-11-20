"""Engine-free extraction/packaging. Never supplies data to a participant.

Primary JSON bytes are not rewritten. Gzip wrappers are identified separately
from the exact uncompressed included bytes. Large omitted streams stay local.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import argparse,json,gzip,hashlib,tarfile,lzma,io,shutil,zipfile,time

def sha(b):return hashlib.sha256(b).hexdigest()
def file_sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def read(p):return json.loads(p.read_bytes())
def primaries(ev):
    for p in sorted(ev.glob('*/*/PRIMARIOS.json*')):
        b=p.read_bytes();plain=gzip.decompress(b)if p.suffix=='.gz'else b
        yield p,plain,json.loads(plain)
def add(tf,name,b):
    entry=tarfile.TarInfo(name);entry.size=len(b);entry.mtime=0;entry.mode=0o644;tf.addfile(entry,io.BytesIO(b))
def origin(p,system,ev):
    try:return {'root':'SYSTEM_ROOT','path':p.relative_to(system.parent).as_posix()}
    except ValueError:return {'root':'EXTERNAL_EXPLICIT','path':str(p)}
def source_entry(p,system,ev,mode,member=None,plain=None):
    v={**origin(p,system,ev),'bytes':p.stat().st_size,'sha256':file_sha(p),'disposition':mode}
    if member is not None:v.update(included_member=member,included_bytes=len(plain),included_sha256=sha(plain),container_bytes_preserved=len(plain)==v['bytes']and sha(plain)==v['sha256'])
    return v
def eligible_source(path,system,lab):
    if path.is_relative_to(lab):return 'versiones_codigo'not in path.parts and path.suffix=='.py'
    if path in(system/'gestionar.py',system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01/instrumentos_pc01.py',system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01/agenda_binaria_pc01.py'):return True
    if path.is_relative_to(system/'app'):return True
    if path.parent==system/'capacidades':return True
    return path.is_relative_to(system/'organizaciones/cpc9')
def parent_ref(v):
    if not isinstance(v,dict):return v
    if v.get('schema')=='DCS1.1.life.v1':return {k:v.get(k)for k in('life_id','profile','branch','snapshot','snapshot_sha256','physical','parent')}
    return v

def collect(system,ev,lab,stage,calc):
    stage.mkdir(parents=True,exist_ok=True);(stage/'EVIDENCIA_ESENCIAL').mkdir(exist_ok=True);(stage/'CODIGO_Y_RECALCULO').mkdir(exist_ok=True)
    r=read(calc)
    if r['errors']:raise ValueError('Unresolved recalculation errors: '+str(len(r['errors'])))
    bycase={q['id']:q for q in r['cases']};execution={}
    for p in ev.glob('*/EJECUCION.json'):
        for row in read(p)['cases']:execution[p.parent.name+'/'+row['case']]=row
    rows=[];fichas=[];index=[];tables={'capabilities':[],'recovery':[],'trials':[]};latest={};life_records={}
    for p,b,data in primaries(ev):
        key=p.parent.parent.name+'/'+p.parent.name;row=bycase.get(key)
        if row is None:raise ValueError('Primary not in frozen recalculation: '+key)
        row={**row,'execution':execution.get(key),'original_primary':origin(p,system,ev),'original_sha256':file_sha(p),'exact_uncompressed_json_sha256':sha(b)};rows.append(row);life=row.get('life')
        if life and(system/'estado/vidas'/life/'VIDA.json').exists()and life not in life_records:
            rp=system/'estado/vidas'/life/'VIDA.json';record=read(rp);record['original_record_file']=str(rp);record['original_record_sha256']=file_sha(rp)
            if(rp.parent/'FUTURO_INTERRUMPIDO.json').exists():record['availability']='INTERRUPTED_UNRECORDED_FUTURE_NORMAL_LOAD_BLOCKED'
            life_records[life]=record
        rec=life_records.get(life,{})
        N=data.get('pre',{}).get('N',rec.get('physical',{}).get('N',data.get('N')))
        fichas.append({'experiment':key,'life':life,'parent':parent_ref(data.get('historical_full_parent',{}).get('parent',data.get('parent',rec.get('parent')))),'profile':rec.get('profile'),'Runtime':'One complete world per actual life; internal B views share this matter'if life else'Diagnostic or auxiliary; see primary','N':N,'initial_tick':row['initial_tick'],'classification':'COMPOSITE_FUNCTIONAL_WITH_SIMPLE_RECEIVER'if rec.get('profile')=='cpc9_integral_n67'else'AUXILIARY_OR_DIAGNOSTIC_NOT_AUTOMATICALLY_MAIN','basis':'Native geometry, channel encounters and demonstrated functions; not number of connected voxels','components':'Inherited quantity/spatial/contact regions; declared access source, alternatives, selected route and recipient when present. Original primary fixes exact subset.','prepared':'Geometry, clocks, supply opportunities, calibration/consequence transformations, finite fixed decoder and scheduling','acquired':'Only content/route transformations actually executed in this case; no trained-field transplant','host_selects':'Curriculum, current environmental utility, query time and prepared participant; never a posteriori target-specific route in local selector','native_selects':'Route from acquired directional policy where the recorded query and control demonstrate it; not all cases','boundaries':'External environment supplies declared inputs. Auditor witnesses do not feed decisions. No bridge between runtimes.','original_primary':origin(p,system,ev),'sha256':file_sha(p)})
        fichas[-1]['parent']=parent_ref(rec.get('parent')or data.get('historical_full_parent')or data.get('parent'))
        if rec.get('profile')!='cpc9_integral_n67':
            fichas[-1]['components']='Auxiliary preparation/copy defined in this primary and its exact source. No inherited E1 functions are inferred.'
            if N==17:fichas[-1]['classification']='SIMPLE_ACQUISITION_AND_ABSORBER_AUXILIARY'
        evals=row['logical_evaluations'];mc=row['material_submissions'];asked=len(evals);responded=sum(q['response_qualified']for q in evals);correct=sum(q.get('task_correct')is True for q in evals);incorrect=sum(q.get('task_correct')is False for q in evals);not_scored=sum(q.get('task_correct')is None for q in evals)
        requested=[q for q in evals if q.get('asked')];qualified_requested=sum(q['response_qualified']for q in requested)
        row['denominators']={'logical_evaluations':asked,'logical_queries_requested':len(requested),'logical_evaluations_without_query':asked-len(requested),'requested_with_qualified_signature':qualified_requested,'requested_without_qualified_signature':len(requested)-qualified_requested,'correct_with_explicit_task_truth_contract':correct,'incorrect_with_explicit_task_truth_contract':incorrect,'not_scored_as_semantic_truth':not_scored,'logical_admission':'NOT_INFERRED_FROM_MULTI_INPUT_RECIPE; exact material admission/application/rejection in recorded receipt statuses','material_submission_IDs':mc,'out_of_domain':'explicit error retained if present; not inferred from silence'}
        tables['trials'].append([key,life or'',row['execution_scope'],row['initial_tick'],row['final_tick'],asked,responded,asked-responded,correct,incorrect,not_scored,mc['explicit_submission_IDs_in_primary'],mc['applied'],mc['rejected_at_application'],mc['pending'],mc['statuses'].get('final_receipt_not_in_primary',0),row['instrument_failure']is not None,str((execution.get(key)or{}).get('exit_code','')),p.relative_to(ev).as_posix(),file_sha(p),len(requested),qualified_requested,len(requested)-qualified_requested])
        for q in evals:
            sub=(q.get('actual_parameter'),q.get('frame'),q['kind'])
            if life:
                token=(life,str(sub));old=latest.get(token)
                if old is None or(q.get('tick')or-1)>=(old[1].get('tick')or-1):latest[token]=(row,q)
            if any(t in q['kind']for t in('RECOVERY','LOCAL','NATIVE_SELECTED_ACCESS')):
                arm='RETAINED_CONTENT_NEW_ACCESS_TEACHING'if'40'in key or'46'in key or'47'in key else'PREPARED_RECOVERY_OR_ACCESS'
                tables['recovery'].append([key,life or'',arm,q['kind'],q.get('tick'),';'.join(q['words']),';'.join(q.get('expected_task_words')or[]),str(q.get('task_correct'))if q.get('task_correct')is not None else'NOT_SCORED_AS_SEMANTIC_TRUTH',q['response_qualified'],q.get('conflicting_codes'),q['locator'],row['source_file'],row['source_sha256']])
        if'loss_assay_code'in row:
            tables['recovery'].append([key,life or'','EXPLICIT_RELEARNING_AFTER_IDENTICAL_CAUSAL_STATE','N17_LOSS_AND_RETEACH',row['final_tick'],str(row.get('loss_assay_code')),str(row.get('explicit_relearned_code')),'RETEACH_NOT_RETENTION',bool(row.get('explicit_relearned_code')),False,'$.decoded / $.relearned_decoded',row['source_file'],row['source_sha256']])
    for (life,token),(row,q)in sorted(latest.items()):
        rec=life_records[life];tables['capabilities'].append([life,rec.get('profile'),rec.get('physical',{}).get('tick'),q['kind'],q.get('actual_parameter',q.get('frame','')),q.get('tick'),';'.join(q['words']),str(q.get('task_correct'))if q.get('task_correct')is not None else'NOT_SCORED_AS_SEMANTIC_TRUTH','LAST_RECORDED_USE_NOT_AN_INDEFINITE_CURRENT_GUARANTEE',row['id'],q['locator'],rec.get('snapshot'),rec.get('snapshot_sha256')])
    write(stage/'ENSAYOS_Y_CONTROLES.json',{'schema':'AA01.experiments.v1','cases':rows,'totals':r['totals'],'denominators':'Logical evaluations, explicit material submission IDs and independent lives are different. Pending/rejection/nonresponse are retained. A code without a task truth contract is not scored as semantic correctness.','do_not_sum_admin_parent_history':True,'recalculation_file':'CODIGO_Y_RECALCULO/RECALCULO.json'})
    write(stage/'FICHAS_ENTES_Y_ASISTENCIA.json',{'schema':'AA01.entity_and_assistance.v1','fichas':fichas,'classification_limits':'Internal regions are not automatically autonomous bodies. A receiver is not a full mind. No acquired capability is inferred solely from an interface.'})
    write(stage/'CODIGO_Y_RECALCULO/RECALCULO.json',r);write(stage/'CODIGO_Y_RECALCULO/TABLAS_DATOS.json',tables)
    compact={life:{**{k:v.get(k)for k in('life_id','world_id','profile','branch','parent','physical','snapshot','snapshot_sha256','availability','knowledge','original_record_file','original_record_sha256')},'operations_count_not_a_capability_count':len(v.get('operations',[]))}for life,v in life_records.items()}
    write(stage/'EVIDENCIA_ESENCIAL/REGISTROS_ACTUALES_DE_VIDAS.json',{'captured_utc':datetime.now(timezone.utc).isoformat(),'records':compact,'operational_snapshots_not_in_this_zip':True,'counts_do_not_establish_functional_access':True,'full_administrative_records_local_original_hashes_identified':True})
    shutil.copyfile(lab/'recalcular_acceso.py',stage/'CODIGO_Y_RECALCULO/recalcular_acceso.py')
    for p in(lab/'documentos').glob('*'):
        if p.is_file():shutil.copyfile(p,stage/p.name)
    print(json.dumps({'primary_cases':len(rows),'lives':len(life_records),'tables':{k:len(v)for k,v in tables.items()}},ensure_ascii=False))

def archive(system,ev,lab,stage):
    index=[];source_map={};objects={};target=stage/'EVIDENCIA_ESENCIAL/PRIMARIOS_Y_TESTIGOS.tar.xz'
    if target.exists():raise FileExistsError('Immutable evidence archive already exists; use a new candidate')
    with lzma.open(target,'wb',format=lzma.FORMAT_XZ,filters=[{'id':lzma.FILTER_LZMA2,'preset':6,'dict_size':64*1024*1024}])as compressed:
        with tarfile.open(fileobj=compressed,mode='w|')as tf:
            for p,b,data in primaries(ev):
                member='primarios/'+p.relative_to(ev).as_posix().removesuffix('.gz');add(tf,member,b);index.append(source_entry(p,system,ev,'EXACT_PRIMARY_JSON_BYTES_INCLUDED',member,b))
            for p in sorted(ev.glob('*/*/*.jsonl.gz')):
                if p.stat().st_size>=1_000_000:index.append(source_entry(p,system,ev,'DEEP_REPETITIVE_STREAM_LOCAL_ONLY_SELECTED_PRIMARY_WITNESSES_INCLUDED'));continue
                b=gzip.decompress(p.read_bytes());member='registros/'+p.relative_to(ev).as_posix().removesuffix('.gz');add(tf,member,b);index.append(source_entry(p,system,ev,'EXACT_UNCOMPRESSED_JSONL_INCLUDED',member,b))
            for p in sorted(ev.glob('*/EJECUCION.json')):
                b=p.read_bytes();member='supervision/'+p.relative_to(ev).as_posix();add(tf,member,b);index.append(source_entry(p,system,ev,'EXACT_JOB_RECORD_INCLUDED',member,b))
            for p in sorted(ev.glob('*/*.log')):
                if p.stat().st_size>150000:continue
                b=p.read_bytes();member='supervision/'+p.relative_to(ev).as_posix();add(tf,member,b);index.append(source_entry(p,system,ev,'EXACT_CONSOLE_BYTES_INCLUDED',member,b))
            for pattern in('PRESUPUESTO.json','ESTADO_INICIAL.json','VERIFICACIONES_TECNICAS_37.json','INTERRUPCION_Y_CARGA_SEGURA_16.json'):
                p=ev/pattern
                if p.exists():b=p.read_bytes();member='identidad_y_tecnica/'+p.name;add(tf,member,b);index.append(source_entry(p,system,ev,'EXACT_EXISTING_RECORD_INCLUDED',member,b))
    # Immutable executed Python bytes: deduplicate by content, never ship runtime
    # binaries, the kernel source or optional numpy/toolchain trees.
    for p in sorted(ev.glob('*/FUENTES_EJECUTADAS.json')):
        index.append(source_entry(p,system,ev,'ORIGINAL_FULL_CAPTURE_MAP_LOCAL_FILTERED_EXECUTED_SOURCE_IDENTITIES_INCLUDED'))
        for raw,item in read(p)['sources'].items():
            path=Path(raw)
            if not eligible_source(path,system,lab):continue
            h=item['sha256'];obj=Path(item['object'])
            if not obj.exists()or file_sha(obj)!=h:raise ValueError('Executed source bytes missing: '+str(obj))
            objects[h]=obj;source_map.setdefault(h,{'bytes':item['bytes'],'original_paths':set(),'capture_maps':set()});source_map[h]['original_paths'].add(str(path));source_map[h]['capture_maps'].add(p.parent.name)
    for path in sorted({*lab.glob('*.py'),system/'gestionar.py',*system.joinpath('app').glob('*.py'),*system.joinpath('capacidades').glob('*.py')}):
        if not eligible_source(path,system,lab):continue
        h=file_sha(path);objects[h]=path;source_map.setdefault(h,{'bytes':path.stat().st_size,'original_paths':set(),'capture_maps':set()});source_map[h]['original_paths'].add(str(path));source_map[h]['capture_maps'].add('CURRENT_AT_PACKAGING_NOT_A_CLAIM_OF_PRIOR_EXECUTION')
    with tarfile.open(stage/'CODIGO_Y_RECALCULO/FUENTES_POR_HASH.tar.xz','w:xz',preset=6)as tf:
        for h,p in sorted(objects.items()):add(tf,'objetos/'+h+'.py',p.read_bytes())
    write(stage/'CODIGO_Y_RECALCULO/MAPA_FUENTES_EJECUTADAS.json',{h:{**q,'original_paths':sorted(q['original_paths']),'capture_maps':sorted(q['capture_maps'])}for h,q in source_map.items()})
    # Complete operational states stay local, including rejected/failed futures.
    snapshot_paths=set(ev.glob('*/*/*.deetsnap.gz'))
    for rec in read(stage/'EVIDENCIA_ESENCIAL/REGISTROS_ACTUALES_DE_VIDAS.json')['records'].values():snapshot_paths.add(system/rec['snapshot'])
    for p in sorted(snapshot_paths):
        if p.exists():index.append(source_entry(p,system,ev,'FULL_OPERATIONAL_SNAPSHOT_LOCAL_ONLY_REQUIRED_FOR_CONTINUITY'))
    for p in sorted(ev.glob('EXTRACCION_FALLO_26/*/*.xz')):
        dest=stage/'EVIDENCIA_ESENCIAL/CRECIMIENTO_ADVERSO_11'/p.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(p,dest);index.append(source_entry(p,system,ev,'EXACT_SELECTED_ORIGINAL_LINE_XZ_INCLUDED',dest.relative_to(stage).as_posix(),p.read_bytes()))
    for p in sorted(ev.glob('TRAZA_RETENCION_B_39/baseline/*.native.gz')):
        dest=stage/'EVIDENCIA_ESENCIAL/CONTRAFACTUAL_42'/p.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(p,dest);index.append(source_entry(p,system,ev,'NATIVE_MICROSTATE_DIAGNOSTIC_NOT_COMPLETE_OWNER_CONTINUITY',dest.relative_to(stage).as_posix(),p.read_bytes()))
    for p in(lab/'DISENO_CONFIRMATORIO_36.json',lab/'INCIDENTE_PRESENTACION_36.md'):
        if p.exists():dest=stage/'CODIGO_Y_RECALCULO'/p.name;shutil.copyfile(p,dest);index.append(source_entry(p,system,ev,'EXACT_DESIGN_OR_INCIDENT_NOTE_INCLUDED',dest.relative_to(stage).as_posix(),p.read_bytes()))
    write(stage/'INDICE_FUENTES_Y_OMISIONES.json',{'schema':'AA01.sources_and_omissions.v1','files':index,'archives_are_private_not_historical_integral_or_restore_backups':True,'gzip_identity':'For decompressed included JSON/JSONL, original gzip hash and exact included byte hash are separate. No claim of original gzip wrapper identity.','deep_coverage':'Three large repetitive streams remain local. Their primary outcomes/control witnesses and the interrupted-growth selected full fields are included. All full owner snapshots remain local. A native tick microstate is not a complete protocol snapshot.','external_runtime_dependency':'Official installed CPython3.13 x64 plus frozen thinking4.5 and the local system; not included in this analysis ZIP.'})
    print(json.dumps({'evidence_archive_bytes':target.stat().st_size,'source_objects':len(objects),'indexed_sources':len(index),'stage_bytes':sum(p.stat().st_size for p in stage.rglob('*')if p.is_file())}))

def seal(system,ev,lab,stage):
    required=['INFORME_RESULTADOS.md','FICHAS_ENTES_Y_ASISTENCIA.json','ENSAYOS_Y_CONTROLES.json','CAPACIDADES_POR_VIDA.csv','RECUPERACION_RETENCION_REAPRENDIZAJE.csv','DECISIONES_E_INCORPORACIONES.md','CONTINUIDAD_ACCESO_ADAPTATIVO_01.json','INDICE_FUENTES_Y_OMISIONES.json']
    for name in required:
        if not(stage/name).is_file()or not(stage/name).stat().st_size:raise ValueError('Missing effective member '+name)
    members=[{'path':p.relative_to(stage).as_posix(),'bytes':p.stat().st_size,'sha256':file_sha(p)}for p in sorted(stage.rglob('*'))if p.is_file()and p.name!='MANIFIESTO_HASHES.json'];write(stage/'MANIFIESTO_HASHES.json',{'schema':'AA01.member_manifest.v1','members':members,'self_and_zip_hash_excluded':True})
    dest=stage.parent/'CANDIDATO_ACCESO_ADAPTATIVO_01_ANALISIS.zip'
    if dest.exists():raise FileExistsError('Canonical existing delivery protected; identify before replacement')
    with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True)as z:
        for p in sorted(stage.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(stage).as_posix())
    if dest.stat().st_size>=16_000_000:raise ValueError('Analysis ZIP exceeds strict limit; no split authorized')
    print(json.dumps({'zip':str(dest),'bytes':dest.stat().st_size,'sha256':file_sha(dest),'files':len(members)+1},ensure_ascii=False))

def main():
    p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--mode',choices=['collect','archive','seal'],required=True);p.add_argument('--calc',type=Path);a=p.parse_args();lab=Path(__file__).parent;ev=a.system.parent/'evidencia/campanas/ACCESO_ADAPTATIVO_01'
    if a.mode=='collect':collect(a.system,ev,lab,a.stage,a.calc)
    elif a.mode=='archive':archive(a.system,ev,lab,a.stage)
    else:seal(a.system,ev,lab,a.stage)
if __name__=='__main__':main()
