"""Close the analysis candidate from existing measurements only; no engine import."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, csv, hashlib, json, shutil, time

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''):h.update(b)
    return h.hexdigest()

def read(path):return json.loads(path.read_bytes())
def write(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')

def main():
    p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);a=p.parse_args()
    root=a.system;stage=a.stage;lab=root/'laboratorio/campanas/PAISAJE_CAUSAL_01';ev=root/'evidencia/campanas/PAISAJE_CAUSAL_01'
    code=stage/'CODIGO_Y_RECALCULO';objects=code/'objetos';objects.mkdir(exist_ok=True)
    revision=read(code/'REVISIONES.json');captured=[]
    current=[lab/'dibujar_atlas_51.py',Path(__file__).resolve(),root/'sistema/gestionar.py',root/'sistema/capacidades/paisaje_causal_01.py']
    for src in current:
        h=sha(src);obj=objects/(h+'.py')
        if not obj.exists():shutil.copyfile(src,obj)
        row={'source':str(src),'sha256':h,'bytes':src.stat().st_size,'object':'objetos/'+h+'.py','role':'POST_ASSEMBLY_EXACT_SOURCE; not a new native scientific execution'}
        captured.append(row)
        previous=revision['current_sources'].get(str(src))
        if previous and previous['sha256']!=h:row['superseded_candidate_source']=previous
        revision['current_sources'][str(src)]={k:v for k,v in row.items()if k!='source'}
    revision['post_assembly_capture']=captured;revision['objects_count']=len(list(objects.glob('*.py')));write(code/'REVISIONES.json',revision)
    shutil.copyfile(lab/'dibujar_atlas_51.py',code/'dibujar_atlas_51.py')
    shutil.copyfile(Path(__file__).resolve(),code/Path(__file__).name)
    for relative in ('gestionar.py','capacidades/paisaje_causal_01.py','contratos/PAISAJE_CAUSAL_01.json','capacidades/NSM65_ACTUALIZACIONES_PAISAJE_01.json'):
        dest=code/'SISTEMA_AFECTADO'/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/'sistema'/relative,dest)
    for h in ('5ba112361f014135e7f53ff0d707d03eaf228474a9d85ce79faf922fbd5a41cb','794417ff80a4fb5c8b1d02be6698c86b20da59fbdbcf583ed6472a2b7684429e'):
        src=lab/'versiones_codigo/objetos'/(h+'.py')
        if not src.exists()or sha(src)!=h:raise ValueError('Missing preserved failed packaging revision '+h)
        dest=code/'revisiones_fallidas_preservadas'/(h+'.py');shutil.copyfile(src,dest)
    deep_path=ev/'RECALCULO_DESDE_DATOS_EMPAQUETADOS_52.json';deep=read(deep_path);baseline=read(stage/'ATLAS_CAUSAL/RECALCULO_DATOS.json');data=read(stage/'EVIDENCIA_ESENCIAL/INDICE_REGISTROS.json')
    compare=dict(deep)
    if 'deep_field_hash_checks' in baseline:compare['deep_field_hash_checks']=baseline['deep_field_hash_checks']
    else:compare.pop('deep_field_hash_checks',None)
    if compare!=baseline:raise ValueError('Deep and ordinary results differ outside the additional field checks')
    deep_proof={'schema':'PC01.deep_data_verification.binding.v1','data_archive_sha256':data['archive_sha256'],'recalculation_script_sha256':sha(code/'recalcular_analisis.py'),'full_local_result':str(deep_path),'full_local_result_sha256':sha(deep_path),'summary':deep['summary'],'global_frames_reconstructed':sum(q['checked_global_frames']for q in deep['deep_field_hash_checks']),'non_global_route_records_separately_counted':sum(q['non_global_route_records']for q in deep['deep_field_hash_checks']),'files':deep['deep_field_hash_checks'],'non_deep_result_exactly_equal':True,'not_a_new_simulation_or_cognitive_verdict':True}
    write(stage/'ATLAS_CAUSAL/VERIFICACION_CAMPOS_PROFUNDOS.json',deep_proof)
    trials=read(stage/'ENSAYOS_Y_CONTROLES.json')['execution_records_including_instrumental_failures']
    columns=['batch','case','exit_code','seconds','primary_exists','scientific_result_not_inferred_from_exit_code','resources_json']
    with (stage/'TABLA_ENSAYOS_Y_CONTROLES.csv').open('w',encoding='utf-8-sig',newline='')as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader()
        for row in trials:w.writerow({**{k:row.get(k,'')for k in columns[:-1]},'resources_json':json.dumps(row.get('resources',{}),ensure_ascii=False,sort_keys=True)})
    budget=read(ev/'ARRANQUE_01/PRESUPUESTO.json');clock=time.perf_counter();elapsed=budget['elapsed_conservative_at_capture']+clock-budget['monotonic_capture']
    if clock>=budget['monotonic_deadline']:raise TimeoutError('Campaign closing exceeded the fixed budget')
    resources=read(stage/'RECURSOS_Y_COMPRESION.json');resources['candidate_closed_utc']=datetime.now(timezone.utc).isoformat();resources['candidate_elapsed_conservative_seconds']=elapsed;resources['remaining_budget_seconds']=budget['monotonic_deadline']-clock;resources['monotonic_sample']=clock;resources['no_native_simulation_during_candidate_closure']=True;write(stage/'RECURSOS_Y_COMPRESION.json',resources)
    preparation=read(stage/'PREPARACION_PAQUETE.json');preparation['final_zip_not_yet_sealed']=True;preparation['scope_of_flag']='Historical assembly event, not final release status. Exact final ZIP is verified by the external receipt.';preparation['post_assembly_complete_utc']=datetime.now(timezone.utc).isoformat();write(stage/'PREPARACION_PAQUETE.json',preparation)
    documents=[root/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_0.docx',root/'ADDENDUM_MANUAL_MAESTRO_EF01_PAISAJE01_EDICION_1_1.md',root/'CONTINUIDAD_PAISAJE_CAUSAL_01.json',root/'sistema/estado/ACTIVO.json']
    continued=read(stage/'CONTINUIDAD_PAISAJE_CAUSAL_01.json');proof={'schema':'PC01.local_evidence_index.v1','primary_cases':len(read(stage/'ENSAYOS_Y_CONTROLES.json')['cases_with_primary']),'indexed_data_members':len(data['members']),'data_archive':str(stage/'EVIDENCIA_ESENCIAL/REGISTROS_COMPLETOS.tar.xz'),'data_archive_sha256':data['archive_sha256'],'data_index':str(stage/'EVIDENCIA_ESENCIAL/INDICE_REGISTROS.json'),'native_recalculation':str(ev/'RECALCULO_FINAL_DATOS_49.json'),'deep_data_result':str(deep_path),'full_states':continued['lives'],'documents_and_protected_default':[{'path':str(q),'bytes':q.stat().st_size,'sha256':sha(q)}for q in documents],'source_bytes':'Laboratory versiones_codigo/objetos and delivered CODIGO_Y_RECALCULO/REVISIONES.json','final_zip_proof':'entregas/VERIFICACION_FINAL_EXTERNA_PAISAJE_CAUSAL_01.json; written only after verifying that exact ZIP','scope':'This campaign only. No CPC1-CPC9 re-consolidation; no implied whole-history coverage.'};write(ev/'INDICE_EVIDENCIA.json',proof)
    handoff={'schema':'PC01.resume.final_candidate.v1','status':'Scientific runs complete; candidate ready for exact-ZIP verification','life_alternatives':continued['recommended_by_task'],'full_continuity':str(root/'CONTINUIDAD_PAISAJE_CAUSAL_01.json'),'failed_main_preserved':continued['failed_main_future_preserved'],'protected_default':continued['protected_default'],'deadline_utc':budget['deadline_utc'],'candidate_elapsed_conservative_seconds':elapsed,'automatic_resume_or_more_native_experiments':False,'own_native_jobs_finished':True,'next_action':'Verify sealed ZIP data and calculations without importing the engine. Do not restart the budget.'};write(lab/'REANUDACION.json',handoff);write(ev/'CIERRE_CANDIDATO_53.json',handoff)
    write(stage/'CODIGO_Y_RECALCULO/CAPTURA_POST_ENSAMBLAJE.json',{'sources':captured,'new_data':deep_proof['summary'],'no_scientific_record_changed':True})
    print(json.dumps({'stage':str(stage),'deep_global_frames':deep_proof['global_frames_reconstructed'],'deep_route_records':deep_proof['non_global_route_records_separately_counted'],'elapsed_conservative_seconds':elapsed,'execution_rows':len(trials),'source_objects':revision['objects_count']}))

if __name__=='__main__':main()
