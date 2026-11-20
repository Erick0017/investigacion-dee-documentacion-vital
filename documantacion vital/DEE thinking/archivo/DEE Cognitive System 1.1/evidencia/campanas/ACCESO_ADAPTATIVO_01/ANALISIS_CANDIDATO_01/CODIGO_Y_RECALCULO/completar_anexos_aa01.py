"""Finish analysis metadata/indices; no imports of or writes to a world."""
from pathlib import Path
import argparse,json,hashlib,shutil
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);a=p.parse_args();root=a.system.parent;lab=Path(__file__).parent;ev=root/'evidencia/campanas/ACCESO_ADAPTATIVO_01';stage=a.stage
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(p,q):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
index=read(stage/'INDICE_FUENTES_Y_OMISIONES.json')
def copy(source,relative):
    target=stage/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    try:where={'root':'SYSTEM_ROOT','path':source.relative_to(root).as_posix()}
    except ValueError:where={'root':'EXTERNAL_EXPLICIT','path':str(source)}
    item={**where,'bytes':source.stat().st_size,'sha256':sha(source),'disposition':'EXACT_CURRENT_DOCUMENT_OR_ANALYSIS_CODE_INCLUDED_NOT_AUTOMATIC_PRIOR_EXECUTION','included_member':relative,'included_bytes':target.stat().st_size,'included_sha256':sha(target),'container_bytes_preserved':True};index['files'].append(item)
for source in(lab/'documentos').glob('*'):
    if source.is_file():copy(source,source.name)
copy(root/'ADDENDUM_MANUAL_MAESTRO_EF01_PC01_AA01_EDICION_1_2.md','ADDENDUM_MANUAL_MAESTRO_EF01_PC01_AA01_EDICION_1_2.md')
copy(root/'CONTINUIDAD_ACCESO_ADAPTATIVO_01.json','CONTINUIDAD_ACCESO_ADAPTATIVO_01.json')
copy(ev/'CIERRE_OPERATIVO_52.json','EVIDENCIA_ESENCIAL/CIERRE_OPERATIVO_52.json')
for source in(a.system/'contratos/ACCESO_ADAPTATIVO_01.json',a.system/'capacidades/NSM65_ACTUALIZACIONES_ACCESO_ADAPTATIVO_01.json',a.system/'documentacion/GUIA_ACCESO_ADAPTATIVO_01.md'):copy(source,'CODIGO_Y_RECALCULO/CONTRATOS_ACTUALES/'+source.name)
for name in('recalcular_acceso.py','preparar_analisis_aa01.py','registrar_cierre_operativo_52.py','extraer_contextos_adversos_53.py','completar_anexos_aa01.py'):copy(lab/name,'CODIGO_Y_RECALCULO/'+name)
node=Path(r'C:\Users\Erik\.codex\visualizations\2026\09\11\01a0921e-4727-7f93-8ad0-0b605c9afe96\AA01_tablas\tablas_aa01.mjs');copy(node,'CODIGO_Y_RECALCULO/tablas_aa01.mjs')
catalog=a.system/'capacidades/CATALOGO_CAPACIDADES.json';selected={'source':str(catalog),'source_sha256':sha(catalog),'source_bytes':catalog.stat().st_size,'extraction':'JSON values of AA01 entries, not original byte slice','entries':[q for q in read(catalog)['entries']if q['id'].startswith('AA01_')]};write(stage/'CODIGO_Y_RECALCULO/CONTRATOS_ACTUALES/REGISTRO_AA01.json',selected)
index['files'].append({'root':'SYSTEM_ROOT','path':catalog.relative_to(root).as_posix(),'bytes':catalog.stat().st_size,'sha256':sha(catalog),'disposition':'FULL_REGISTRY_LOCAL_ONLY_SELECTED_AA01_JSON_VALUES_INCLUDED','included_member':'CODIGO_Y_RECALCULO/CONTRATOS_ACTUALES/REGISTRO_AA01.json','included_bytes':(stage/'CODIGO_Y_RECALCULO/CONTRATOS_ACTUALES/REGISTRO_AA01.json').stat().st_size,'included_sha256':sha(stage/'CODIGO_Y_RECALCULO/CONTRATOS_ACTUALES/REGISTRO_AA01.json'),'container_bytes_preserved':False})
for name in('DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_0.docx','ADDENDUM_MANUAL_MAESTRO_EF01_PAISAJE01_EDICION_1_1.md','ADDENDUM_MANUAL_ESPANOL_FUNCIONAL_01.md'):
    source=root/name
    if source.exists():index['files'].append({'root':'SYSTEM_ROOT','path':name,'bytes':source.stat().st_size,'sha256':sha(source),'disposition':'PRESERVED_PRIOR_DOCUMENT_LOCAL_ONLY_CONSOLIDATED_NEW_ADDENDUM_INCLUDED'})
extra=read(stage/'EVIDENCIA_ESENCIAL/CONTEXTOS_ADVERSOS_03/PROCEDENCIA.json');index['selected_extra_adverse_contexts']=extra;index['deep_coverage']='Three complete large repetitive streams remain local. Four exact global growth11 lines and two exact last-recorded dense03 lines are included with offsets/hashes and verified sparse fields. They do not cover every unrecorded or intermediate state. All complete operative snapshots remain local.'
write(stage/'INDICE_FUENTES_Y_OMISIONES.json',index)
continuity=read(root/'CONTINUIDAD_ACCESO_ADAPTATIVO_01.json');tables=read(stage/'CODIGO_Y_RECALCULO/TABLAS_DATOS.json');record_path=stage/'EVIDENCIA_ESENCIAL/REGISTROS_ACTUALES_DE_VIDAS.json';records=read(record_path);known={q[0]for q in tables['capabilities']}
for life in('AA01_ACCESO_LISTO_plus','AA01_ACCESO_LISTO_minus','E1_SOCIAL_11'):
    item=continuity['states'][life];rec=read(a.system/'estado/vidas'/life/'VIDA.json');records['records'][life]={k:rec.get(k)for k in('life_id','world_id','profile','branch','parent','physical','snapshot','snapshot_sha256','availability','knowledge')}
    if life in known:continue
    ready=life.startswith('AA01_ACCESO_LISTO_');tables['capabilities'].append([life,item['profile'],item['tick'],'LEARNED_ACCESS_READY_PENDING_GENERIC_QUERY'if ready else'PROTECTED_DEFAULT_PASSIVE_CONTINUITY_ONLY','same-world finite domain'if ready else'historical functions not rerun',item['tick'],'native learned route state and9pending inputs; evaluation49 is a different future'if ready else'complete checkpoint unchanged','NOT_A_NEW_FUNCTIONAL_QUERY_ON_THIS_BRANCH','READY_STATE_NOT_CONSUMED'if ready else'NO_AA01_FUNCTIONAL_REVALIDATION','CONTINUIDAD_OPERATIVA_49'if ready else'CIERRE_OPERATIVO_52','$.states.'+life,rec['snapshot'],rec['snapshot_sha256']])
write(stage/'CODIGO_Y_RECALCULO/TABLAS_DATOS.json',tables);write(record_path,records)
fichas=read(stage/'FICHAS_ENTES_Y_ASISTENCIA.json');fichas['selected_current_operational_states']={k:{z:v[z]for z in('life','profile','branch','parent','N','tick','snapshot','snapshot_sha256','pending_count')}for k,v in continuity['states'].items()};write(stage/'FICHAS_ENTES_Y_ASISTENCIA.json',fichas)
coverage={'not_a_global_cognition_verdict':True,'physical_contracts_tested':['04/12/17 consequence-dependent local strategy/control/reserves','14/21 common receiver history and cadence','33/34 S50 prototype-to-normal-API exact RAW/clocks at8stages','35 bounded-owner/full-native equality','36 MAIN prospective reserve, including failed lateB','40 content-omitted recovery with backup omissions/cuts/shams','46/47 recovered-content immediate native use and preserved six-function panel','49 normal guarded processes, full learned state, exact restore, new object'],'software_checks':['16 interrupted-future load block','41 mocked parent-record/snapshot coherence before/after, no new worlds'],'not_retested':['34historical families','unaffected profiles and CPC genealogy','indefinite stability','all NSM65 semantics'],'no_automatic_semantic_level_promotions':True,'main_not_globally_promoted':True};write(stage/'CODIGO_Y_RECALCULO/COBERTURA_REGRESION_AA01.json',coverage);write(a.system/'documentacion/COBERTURA_REGRESION_AA01.json',coverage)
print(json.dumps({'files':sum(p.is_file()for p in stage.rglob('*')),'stage_bytes':sum(p.stat().st_size for p in stage.rglob('*')if p.is_file()),'capability_rows':len(tables['capabilities']),'manual_word_updated':False},ensure_ascii=False))
