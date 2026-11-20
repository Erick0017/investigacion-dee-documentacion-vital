"""Prepare compact retrospective deliverable and continuity, without DEE."""
from pathlib import Path
import argparse,json,shutil,tarfile,hashlib,difflib,gzip,time
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--lab',type=Path,required=True);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--tablas-js',type=Path,required=True);a=p.parse_args();root=a.root;lab=a.lab;ev=a.evidencia;pkg=ev/'PAQUETE_CANDIDATO_01';re=pkg/'RECALCULO';re.mkdir(exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def read(f):return json.loads(f.read_text(encoding='utf-8-sig'))
def write(f,v):f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for name in ['leer_estado.py','rutas_retrospectivas.py','recalcular.py','preparar_tablas.py','extraer_retrospectiva.py','anexar_rutas_y_codigo.py','explorar_snapshots.py']:
    shutil.copyfile(lab/name,re/name)
shutil.copyfile(a.tablas_js,re/'tablas_ret01.mjs')
shutil.copyfile(ev/'CALCULOS_R5.json',pkg/'EVIDENCIA_CAUSAL/CALCULOS.json')
shutil.copyfile(ev/'INCORPORACION_VERIFICADA_R3.json',pkg/'EVIDENCIA_CAUSAL/INCORPORACION_VERIFICADA.json')
shutil.copyfile(root/'sistema/contratos/OBSERVADOR_CAUSAL_RETROSPECTIVO_01.json',re/'CONTRATO_OBSERVADOR.json')
shutil.copyfile(root/'sistema/documentacion/GUIA_OBSERVADOR_CAUSAL_RETROSPECTIVO_01.md',re/'USO_DEL_OBSERVADOR.md')
shutil.copyfile(root/'ADDENDUM_MANUAL_MAESTRO_RETROSPECTIVA_EDICION_1_3.md',pkg/'ADDENDUM_MANUAL_MAESTRO_RETROSPECTIVA_EDICION_1_3.md')
before=(lab/'gestionar_antes_ret01.py').read_text(encoding='utf8');after=(root/'sistema/gestionar.py').read_text(encoding='utf8');(re/'CAMBIO_GESTOR.diff').write_text(''.join(difflib.unified_diff(before.splitlines(keepends=True),after.splitlines(keepends=True),fromfile='sistema/gestionar.py anterior',tofile='sistema/gestionar.py con observador')),encoding='utf8')
assert(lab/'leer_estado.py').read_bytes()==(root/'sistema/capacidades/observador_causal_retrospectivo_01.py').read_bytes()

q=read(ev/'CALCULOS_R5.json');protected=read(pkg/'EVIDENCIA_CAUSAL/ESTADOS_PROTEGIDOS.json');states=[]
for d in protected:
    if'life'not in d:continue
    assert sha(Path(d['snapshot']).read_bytes())==d['summary']['encoded_sha256']
    states.append({'life':d['life'],'profile':d['profile'],'parent':d['parent'],'N':d['summary']['N'],'tick':d['summary']['tick'],'snapshot':d['snapshot'],'snapshot_sha256':d['summary']['encoded_sha256'],'pending_count':len(d['pending']),'last_operation_scope':'No new native operation; unchanged since AA01. Field inspection only.'})
for d in protected:
    if'protected_file'in d:assert sha(Path(d['protected_file']).read_bytes())==d['sha256']
continuity={'schema':'DCS1.1.RETROSPECTIVE.continuity.v1','states_unchanged':states,'new_native_ticks':0,'worlds_created_or_restored':0,'preferred_protected':'E1_SOCIAL_11','main_preserved':'E1_ACCESO_ADAPTATIVO_01','promotion':'NONE','incorporated':'External read-only observer; no native skill or NSM level change','learned_ready_use':'AA01 full-snapshot branches remain unconsumed. Use the existing AA01 guide to bifurcate explicitly before advancing; not executed in this audit.','main_loss_scope':'Local incoming contribution coalesces in AA42; whole MAIN content history not proved globally erased','required_local_files':['sistema/gestionar.py and official installed environment','Full selected snapshot plus its VIDA.json and existing profile components','AA01 contract and continuation protocols'],'analysis_not_complete_restore_backup':True,'next_operation_not_executed':'Only if requested later: explicit historical full-state fork of a learned ready branch. No automatic promotion, rewind or synthesis of memories.','manual':'ADDENDUM_MANUAL_MAESTRO_RETROSPECTIVA_EDICION_1_3.md; original DOCX remains unchanged'}
write(root/'CONTINUIDAD_AUDITORIA_RETROSPECTIVA_01.json',continuity);write(pkg/'CONTINUIDAD_AUDITORIA_RETROSPECTIVA_01.json',continuity)

ix=read(pkg/'EVIDENCIA_CAUSAL/INDICE_PRIMARIOS.json');snap_sources={e['original']for e in ix['entries']if e['role']=='snapshot'};omitted=[]
for d in read(ev/'EXPLORACION_X5.json')['snapshots']:
    if d['source']in snap_sources:continue
    if any(x['path']==d['source']for x in omitted):continue
    omitted.append({'path':d['source'],'bytes':Path(d['source']).stat().st_size,'sha256':d['encoded_sha256'],'reason':'Complete local checkpoint not transported; selected exact full-field extract or recorded X5 observation is indexed separately. Not an operational state inferred from arrays.'})
original_guide=lab/'LEER_PRIMERO_antes_ret01.md';paragraph=next(line for line in original_guide.read_text(encoding='utf8').splitlines()if line.startswith('La vida preferente es'))
write(pkg/'EVIDENCIA_CAUSAL/ALCANCE_DOCUMENTAL_DEL_PREDETERMINADO.json',{'scope':'Documentary historical capability statement, not a new physical test','preserved_source':str(original_guide),'source_sha256':sha(original_guide.read_bytes()),'exact_paragraph':paragraph,'current_snapshot_identity':'See ESTADOS_PROTEGIDOS.json; never reinterrogated in this audit'})

# Link protocol sources to the original primary-record hashes where available.
objects={}
for item in [dict(archive=ix['archive']),*ix.get('additional_archives',[])]:
    with tarfile.open(pkg/'EVIDENCIA_CAUSAL'/item['archive'],'r:xz')as t:objects.update({m.name:t.extractfile(m).read()for m in t.getmembers()if m.isfile()})
declared={}
for e in ix['entries']:
    if e['role']!='primary':continue
    b=objects[e['member']];d=json.loads(gzip.decompress(b)if e['member'].endswith('.gz')else b)
    for k in('source_sha256','source_code_sha256','source_sha256_code'):
        if isinstance(d.get(k),str):declared.setdefault(d[k],[]).append({'id':e['id'],'field':k})
code=[]
frozen_path=root/'evidencia/campanas/ACCESO_ADAPTATIVO_01/ANALISIS_CANDIDATO_01/CODIGO_Y_RECALCULO/FUENTES_POR_HASH.tar.xz'
with tarfile.open(frozen_path,'r:xz')as tf:frozen_hashes={Path(m.name).stem for m in tf.getmembers()if m.isfile()}
for e in ix['entries']:
    if e['role'].startswith('historical_protocol_code'):
        code.append({'id':e['id'],'sha256':e['sha256'],'linked_original_records':declared.get(e['sha256'],[]),'present_in_prior_frozen_AA_source_bundle':e['sha256']in frozen_hashes,'scope':'Exact included bytes; direct original-source hash links are distinguished from current helper implementation references'})
write(pkg/'EVIDENCIA_CAUSAL/FUENTES_DE_PROTOCOLO_VERIFICADAS.json',code)
deep=[{'local':str(root/'evidencia/campanas/ACCESO_ADAPTATIVO_01'),'omitted':'Nonselected cases, deep streams and complete checkpoints not explicitly included. Existing original files are untouched.'},{'local':str(root/'evidencia/campanas/PAISAJE_CAUSAL_01'),'omitted':'Other atlas windows, full snapshots and nonselected architecture tests; no general coverage claim.'},{'local':str(root.parent/'CPC9/runs/RUN_20261019_165651'),'omitted':'Whole historical campaign outside the exact targeted primary records. Historical ZIP is not nested.'}]
manual=root/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_0.docx';assert sha(manual.read_bytes())=='f0d1a71f8dc4aa8d9d72aa1428b9ed62df320897ce4987353122539285f2e6e5'
write(pkg/'INDICE_FUENTES_Y_OMISIONES.json',{'scope':'Essential analysis, not integral historical archive or operational system','primary_index':'EVIDENCIA_CAUSAL/INDICE_PRIMARIOS.json','exact_selected_source_bytes':ix['sources_total_bytes'],'exact_selected_objects':len(ix['entries']),'original_primary_files':133,'complete_snapshots_in_evidence':17,'archives':[{'file':x,'bytes':(pkg/'EVIDENCIA_CAUSAL'/x).stat().st_size,'sha256':sha((pkg/'EVIDENCIA_CAUSAL'/x).read_bytes())}for x in [ix['archive'],*[v['archive']for v in ix.get('additional_archives',[])]]],'omitted_complete_checkpoints_on_examined_spine':omitted,'other_deep_material_local':deep,'official_engine':'No motor, WHL or kernel source is redistributed; identity checks reused from AA01. Recalculation uses Python standard library only. Native continuation still needs the existing installed system.','manual_original_local':{'path':str(manual),'sha256':sha(manual.read_bytes()),'word_updated':False,'editorial_status':'Prior recorded render blocker retained; no fresh installation/revalidation audit.'},'historical_conversations':'No new access to conversations or external services claimed. No source uploaded.'})
write(ev/'CIERRE_DE_LECTURA.json',{'start':read(ev/'CORTE.json'),'ended_monotonic':time.perf_counter(),'new_native_ticks':0,'protected_snapshots_and_pointers_unchanged':True,'no_necessary_new_causal_experiment':'Existing controls suffice for the bounded conclusions and external-observer incorporation. Unresolved lineage/functional-access hypotheses are not promoted.','manual_docx_unchanged':True})
print(json.dumps({'package':str(pkg),'members_before_seal':sum(f.is_file()for f in pkg.rglob('*')),'deep_checkpoint_references':len(omitted),'selected_source_bytes':ix['sources_total_bytes'],'new_ticks':0}))
