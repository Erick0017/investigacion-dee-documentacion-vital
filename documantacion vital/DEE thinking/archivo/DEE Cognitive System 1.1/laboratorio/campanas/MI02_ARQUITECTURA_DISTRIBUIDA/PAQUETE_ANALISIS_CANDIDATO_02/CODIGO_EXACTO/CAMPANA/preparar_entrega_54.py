"""Assemble the analysis/delta from completed records; no engine imports/ticks."""
import csv,gzip,hashlib,json,os,shutil,sys,time
from pathlib import Path
from datetime import datetime,timezone
sys.stdout.reconfigure(encoding='utf8')
L=Path(__file__).resolve().parent;R=L.parents[2];S=R/'sistema';E=R/'evidencia/campanas/MI02_ARQUITECTURA_DISTRIBUIDA';out=L/'PAQUETE_ANALISIS_CANDIDATO_02'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
def copy(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)

budget=json.loads((L/'PRESUPUESTO.json').read_bytes());assert time.monotonic()<budget['monotonic_deadline']
index=json.loads((out/'INDICE_EVIDENCIA.json').read_bytes());source_revisions={};original_checks=[]
parent=S/'estado/checkpoints/E1_MI01_MAIN.T24752.bec543681d6d.deetsnap.gz'
assert sha(parent)=='23114e8445f2b651ce9dfd53011b9749b357e1fa9a4191e87982b0fafec081a4'
q=out/'EVIDENCIA_ESENCIAL/SNAPSHOTS_SELECCIONADOS'/parent.name;copy(parent,q)
index['historical_parent_snapshot']={'snapshot':str(q.relative_to(out)).replace('\\','/'),'original':str(parent.relative_to(R)),'sha256':sha(parent),'scope':'Exact MI01T24752 father selected before inherited realizationA; forensic/replay starting state, not knowledge imported into distributed B.'}
omission_path=out/'INDICE_FUENTES_Y_OMISIONES.json';omissions=json.loads(omission_path.read_bytes());included_initials={str((E/Path(v['snapshot']).name).relative_to(R))for v in index.get('diagnostic_initial_snapshots',[])};omissions['omitted']=[v for v in omissions['omitted']if v['original']not in included_initials];omissions['reclassified_as_included_initial_controls']=sorted(included_initials);write(omission_path,omissions)
with gzip.open(out/'EVIDENCIA_ESENCIAL/REGISTROS_PRIMARIOS.jsonl.gz','rb')as f:
    for line in f:
        packet=json.loads(line);x=packet['data']
        if isinstance(x,dict):
            for v in x.get('sources',[]):source_revisions.setdefault(v['path'].replace('\\','/'),set()).add(v['sha256'])
for row in index['index']:
    p=R/row['original'];actual=sha(p)
    if actual!=row['original_sha256']:raise AssertionError('Original changed after export '+str(p))
    original_checks.append({'path':row['original'],'sha256':actual,'projection_line':row['jsonl_line_1based']})
delta=out/'DELTA_SISTEMA';extra=[S/'documentacion/GUIA_MI02.md']
for source in extra:
    rel=str(source.relative_to(S)).replace('\\','/');copy(source,delta/rel)
    if not any(x['path']==rel for x in index['delta_files']):index['delta_files'].append({'path':rel,'sha256':sha(source),'bytes':source.stat().st_size})
for row in index['delta_files']:
    source=S/row['path'];copy(source,delta/row['path']);row.update({'sha256':sha(source),'bytes':source.stat().st_size})
    if source.suffix=='.py':compile(source.read_text(encoding='utf-8-sig'),str(source),'exec')
for source in L.glob('*.py'):copy(source,out/'CODIGO_EXACTO/CAMPANA'/source.name)
for source in L.glob('*.mjs'):copy(source,out/'CODIGO_EXACTO/CAMPANA'/source.name)
copy(L/'TABLAS_DATOS_MI02.json',out/'RECALCULO/TABLAS_DATOS_MI02.json');copy(L/'RECALCULO_FINAL_MI02.json',out/'RECALCULO/RESULTADO_REFERENCIA.json');copy(L/'recalcular_mi02.py',out/'RECALCULO/recalcular_mi02.py');copy(L/'aplicar_delta_mi02.py',out/'DELTA_APLICACION/aplicar_delta_mi02.py')
for name in['INFORME_CIENTIFICO_MI02.md','ARQUITECTURA_Y_FLUJOS_MI02.md','INCORPORACIONES_MI02.md','CAMBIOS_MANUAL_MI02.md']:copy(L/name,out/name)
for name in['FICHAS_ENTES_MI02.json','VERIFICACION_WORD_MI02_ESTRUCTURAL.json','VERIFICACION_WORD_MI02_RENDER.json']:copy(E/name,out/'DOCUMENTACION'/name)
manual=R/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_8_MI02_SIN_VALIDACION_VISUAL.docx';assert sha(manual)=='1f37b20a860b50835b87bbfcf8bc783f23e31c37db7d230bf4bb350e9106504a';copy(manual,out/'MANUAL_MAESTRO_1_8_MI02_SIN_VALIDACION_VISUAL.docx')
registry_versions={}
for p in[L/'CATALOGO_ANTES_CIERRE_MI02.json',S/'capacidades/CATALOGO_CAPACIDADES.json']:
    for row in json.loads(p.read_bytes())['entries']:
        if row['id'].startswith('MI02_'):registry_versions.setdefault(row['id'],set()).add(hashlib.sha256(canonical(row)).hexdigest())
delta_files=[]
for row in index['delta_files']:
    versions=source_revisions.get('sistema/'+row['path'],set());delta_files.append({**row,'known_previous_sha256':sorted(versions|{row['sha256']})})
deps={'base':'Existing DEE Cognitive System1.1 with app/lives.py, native_tools, original base organizations and contracts','interpreter_native':'CPython3.13x64 compatible, existing local environment','engine':'Official DEE thinking4.5.0 frozen','WHL_SHA256':'09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c','PYD_SHA256':'17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d','kernel_source_SHA256':'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31','external':'Installed separate Gymnasium1.4.0 / NumPy2.3.5 / Python3.12.14 worker from the base system; not included here','portable_recalculation':'Python3.10+ standard library; no DEE engine or Artifact Tool required to recalculate the archived evidence'}
write(out/'DELTA_APLICACION/MANIFIESTO_DELTA.json',{'scope':'Code/profile delta, not a standalone system or memory transfer','files':delta_files,'registry_known_entries':{k:sorted(v)for k,v in registry_versions.items()},'external_dependencies':deps,'state_files_never_written':True,'default_never_promoted':True})
legacy=S/'documentacion/NSM65_ESTADO_POR_VIDA.csv';copy(legacy,out/'REFERENCIAS/NSM65_ESTADO_ANTECEDENTE.csv')
write(out/'DOCUMENTACION/NSM65_MI02_ALCANCE.json',{'source':str(legacy.relative_to(R)),'source_sha256':sha(legacy),'source_bytes':legacy.stat().st_size,'source_unchanged':True,'new_meanings_credited_MI02':0,'legacy_scope':'Historical per-life rows, not knowledge transferred to D1MAIN or R9. Original four-profile coverage remains unchanged.','additional_vocabulary':['izquierda','derecha'],'word_specific_acquisition':'Not established; unpaired consequences also distinguish the two physical codes. No NSM levels increased from this result.','new_native_functions':'Useful bounded mechanisms remain credited under their contracts, without being renamed semantic primitives.','all_65_still_research_target':True})
continuity=json.loads((R/'CONTINUIDAD_MI02_ARQUITECTURA_DISTRIBUIDA.json').read_bytes());continuity.update({'release_recorded_utc':datetime.now(timezone.utc).isoformat(),'native_work_complete':True,'closed_native_work':'MAIN remains at the realT81207cut; diagnostic48 and constructor49 are complete. No MI02native writers remain. Divergent results were not imported into selected lives.','diagnostic48_complete':True,'constructor49_operatively_verified':True,'manual_edition':'1.8','manual_sha256':sha(manual),'manual_visual_validation':False,'release_verification_external':'entregas/VERIFICACION_FINAL_EXTERNA_MI02.json','analysis_zip':'entregas/DEE_COGNITIVE_1_1_MI02_ARQUITECTURA_DISTRIBUIDA_ANALISIS.zip','analysis_not_full_operating_backup':True});write(R/'CONTINUIDAD_MI02_ARQUITECTURA_DISTRIBUIDA.json',continuity);copy(R/'CONTINUIDAD_MI02_ARQUITECTURA_DISTRIBUIDA.json',out/'CONTINUIDAD_MI02_ARQUITECTURA_DISTRIBUIDA.json')
write(R/'REANUDACION_MI02.json',{'campaign':'MI02_ARQUITECTURA_DISTRIBUIDA','native_work_complete':True,'main':'D1_MI02_MAIN','tick':81207,'alternative':'MI02_SOCIAL_REUSABLE_240','alternative_tick':15329,'external_continuation':'MI02_R9_OPERATIVA47','external_tick':20021,'protected_active':'E1_SOCIAL_11','active_tick':3154,'continuity_file':'CONTINUIDAD_MI02_ARQUITECTURA_DISTRIBUIDA.json','verification_outside_archive':'entregas/VERIFICACION_FINAL_EXTERNA_MI02.json','do_not_repeat_experiments':True,'remaining_scientific_limit':'Arbitrary social-context updating and independent preservation of signal discrimination during policy change were not established; no generalR2 or learned external control.','deadline_utc':budget['deadline_utc'],'monotonic_deadline':budget['monotonic_deadline'],'budget_not_restarted':True});copy(R/'REANUDACION_MI02.json',out/'REANUDACION_MI02.json')
guide=(S/'documentacion/GUIA_MI02.md').read_text(encoding='utf8').replace('../../CONTINUIDAD_MI02_ARQUITECTURA_DISTRIBUIDA.json','CONTINUIDAD_MI02_ARQUITECTURA_DISTRIBUIDA.json').replace('../../DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_8_MI02_SIN_VALIDACION_VISUAL.docx','MANUAL_MAESTRO_1_8_MI02_SIN_VALIDACION_VISUAL.docx')
(out/'GUIA_MI02.md').write_text(guide,encoding='utf8');write(out/'INDICE_EVIDENCIA.json',index)
write(out/'DOCUMENTACION/VERIFICACION_ORIGINALES_EXPORTADOS.json',{'checked':len(original_checks),'all_current_original_hashes_match_exported_index':True,'files':original_checks,'native_ticks':0})
resources={'budget':budget,'recorded_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-(budget['monotonic_deadline']-budget['maximum_seconds']),'native_runtime_locks_present':[str(p)for p in(S/'estado/locks').glob('*MI02*.lock')],'evidence_deep_files':sum(1 for p in E.rglob('*')if p.is_file()),'evidence_deep_bytes':sum(p.stat().st_size for p in E.rglob('*')if p.is_file()),'operative_MI02_life_files_bytes':sum(p.stat().st_size for f in(S/'estado/vidas').glob('*MI02*')if f.is_dir()for p in f.rglob('*')if p.is_file()),'operative_MI02_checkpoint_bytes':sum(p.stat().st_size for p in(S/'estado/checkpoints').glob('*MI02*')if p.is_file()),'D_free_bytes_now':shutil.disk_usage(R).free,'size_units':'Bytes are filesystem bytes; they are not RAM, cognitive capacity, electricity or native energy.','no_new_native_ticks_during_assembly':True};write(out/'DOCUMENTACION/RECURSOS_Y_TAMANOS.json',resources)
print(json.dumps({'originals_rechecked':len(original_checks),'delta_files':len(delta_files),'native_locks':resources['native_runtime_locks_present'],'elapsed_seconds':resources['elapsed_seconds'],'deep_evidence_bytes':resources['evidence_deep_bytes'],'manual_sha256':sha(manual)},ensure_ascii=False),flush=True)
