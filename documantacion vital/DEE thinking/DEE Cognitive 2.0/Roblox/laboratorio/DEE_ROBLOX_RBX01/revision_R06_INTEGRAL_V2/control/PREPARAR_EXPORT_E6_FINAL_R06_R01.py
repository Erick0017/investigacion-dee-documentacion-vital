"""Final science/E6 selection proposal. No freeze/ZIP build; video stays Root-pending."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def main():
    plan=json.loads((ROOT/'control/EXPORT_CORE_R06_R02.json').read_text('utf-8'))
    plan['status']='SCIENCE_E6_CLOSED_ROOT_VIDEO_AND_FINAL_FREEZE_PENDING';plan['finalized']=False
    existing={x['archive'].casefold()for x in plan['files']}
    def add(rel,role='final_evidence'):
        p=ROOT/rel
        if not p.is_file():raise ValueError('EXPLICIT_FINAL_SOURCE_MISSING: '+rel)
        if rel.casefold()in existing:return
        entry={'source':rel,'archive':rel,'role':role}
        if p.stat().st_size>2_000_000:
            if role!='native_primary':raise ValueError('NONPRIMARY_LIMIT: '+rel)
            entry['max_bytes']=8_000_000
        existing.add(rel.casefold());plan['files'].append(entry)
    for name in('E6_CIERRE_COMPROBADO_R06.json','CONTINUIDAD_CIERRE_R06.json','OMISIONES_CIERRE_R06.json','LEER_PRIMERO_CIERRE_R06.txt',
        'CONSOLIDAR_E6_FINAL_R06_R01.py','RECALCULO_E6_CERRADO_R06_R01.py','MATRIZ_CIENTIFICA_F01_F16_FINAL_R02.csv'):
        add('analisis/'+name,'final_transfer')
    for name in('COMPARACION_TRES_BRAZOS.csv','AUDITORIA_SALIDAS_AI_R01.json','FUENTES_Y_LIMITES.json'):
        add('analisis/COMPARACION_CIENTIFICA_FINAL_R01/'+name,'final_scientific_table')
    for rel in('control/LEDGER_R06.json','control/PRUEBA_SALTOS_LINEA_PROTO_R02.json','control/PROTO_ACCION_NO_ADMITIDA_R02.json',
        'video/CAPTURE_SERVICE_PRUEBA_REAL_R06.json','prototipo/NATIVE_LIMPIO_R01/ejecutar_native_limpio_R02.py',
        'prototipo/NATIVE_LIMPIO_R01/continuar_pregunta_conector_R03.py'):
        add(rel,'E6_provenance')
    for folder in('NATIVE_CONECTOR_LIMPIO_R01','NATIVE_CONECTOR_LIMPIO_R02','NATIVE_CONECTOR_CONTINUACION_R03'):
        directory=ROOT/'evidencia'/folder
        for file in sorted(directory.iterdir()):
            if file.is_file()and file.suffix.lower()in('.json','.jsonl')and not file.name.startswith('MCP'):
                add(file.relative_to(ROOT).as_posix(),'connector_actual_evidence')
    for stage,profiles in((1,('LOAD1',)),(2,('LOAD1','LOAD2')),(3,('LOAD1','LOAD2','LOAD3'))):
        base=f'load/evidencia/ETAPA_{stage:02d}'
        for name in('RESULTADO_ETAPA.json','PLAN_EJECUTADO.json'):
            add(base+'/'+name,'load_actual_evidence')
        for name in('GO.json','ABORT.json'):
            if(ROOT/base/'BARRERA'/name).is_file():add(base+'/BARRERA/'+name,'load_actual_barrier')
        for profile in profiles:
            for file in sorted((ROOT/base/profile).iterdir()):
                if file.is_file()and file.suffix.lower()in('.json','.jsonl'):
                    add(file.relative_to(ROOT).as_posix(),'load_actual_evidence')
    resource_base='analisis/RECURSOS_FINALES_R06_R01/'
    resource=json.loads((ROOT/resource_base/'RECURSOS_RECALCULADOS.json').read_text('utf-8'))
    for name in('RECURSOS_RECALCULADOS.json','OWNERS_POR_RUN.csv','IMPORT0_SEPARADO.csv','FASES_POR_PARTICIPANTE.csv','REPETIR_PORTABLE.json'):
        add(resource_base+name,'final_resources')
    for row in resource['portable_primary_selection']:
        add(resource_base+row['archive_relative'],'native_primary'if row['category']=='owner'else'final_resource_primary')
    for name in('E6_HECHOS_RECALCULADOS.json','CARGA_EPISODIOS_R06.csv'):
        add('analisis/E6_FINAL_RECALCULO_R06_R01/'+name,'E6_recalculated')
    recipe=json.loads((ROOT/resource_base/'REPETIR_PORTABLE.json').read_text('utf-8'))
    resource_recipe=next(x for x in plan['recalculations']if x['id']=='resources_core_closed')
    resource_recipe['id']='resources_final_all_closed'
    resource_recipe['args']=[x.replace('{resource_primary_root}','{root}/'+resource_base.rstrip('/')).replace('{new_output}','{out}')for x in recipe['args']]
    plan['recalculations'].append({'id':'E6_actual_closed','script':'analisis/RECALCULO_E6_CERRADO_R06_R01.py',
        'args':['--stage','{root}/load/evidencia/ETAPA_01/RESULTADO_ETAPA.json','--stage','{root}/load/evidencia/ETAPA_02/RESULTADO_ETAPA.json',
            '--stage','{root}/load/evidencia/ETAPA_03/RESULTADO_ETAPA.json','--ctrl-result','{root}/evidencia/NATIVE_CONECTOR_CONTINUACION_R03/RESULTADO_CONTINUACION.json',
            '--ctrl-world','{root}/evidencia/NATIVE_CONECTOR_CONTINUACION_R03/WORLD_MODULE_CHECKPOINT.json','--ledger','{root}/control/LEDGER_R06.json','--output','{out}'],
        'timeout_seconds':120,'expected_outputs':['E6_HECHOS_RECALCULADOS.json','CARGA_EPISODIOS_R06.csv']})
    plan['required_before_finalization']=['Root final video/code/QC/manifest metadata and actual viewing artifact hash','Root final scientific report/reading guide review',
        'All selected bytes frozen after final Root edits','Final protected eleven comparison','ZIP<=15000000 bytes/clean extraction/five passive recalc recipes']
    plan['recalculation_note']='Five passive recipes: exact integral, final resource owners/main+load+CTRL (main latency remains separate), Q1Q2 latency, comparison audit, E6. Final video material still Root pending.'
    target=ROOT/'control/EXPORT_E6_FINAL_R06_R01.json'
    with target.open('x',encoding='utf-8')as f:json.dump(plan,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'files':len(plan['files']),'raw_bytes_now':sum((ROOT/x['source']).stat().st_size for x in plan['files']),
        'recipes':len(plan['recalculations']),'finalized':False,'path':str(target),'Native_MCP_model_SQLite_calls':0},indent=2))
if __name__=='__main__':main()
