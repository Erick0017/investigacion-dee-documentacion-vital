"""Explicit closed-core package proposal; no final freeze/build or live state scan."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def main():
    plan=json.loads((ROOT/'control/EXPORT_SEMILLA_R06.json').read_text('utf-8'))
    plan['status']='CLOSED_CORE_SELECTED_E6_FINAL_SELECTION_PENDING'
    plan['source_roots']=['../revision_R05_C02']
    existing={x['archive'].casefold():x for x in plan['files']}
    def add(source,archive=None,role='core_evidence'):
        path=ROOT/source
        if not path.is_file():raise ValueError('EXPLICIT_SOURCE_MISSING: '+source)
        archive=archive or source
        if archive.casefold()in existing:return
        row={'source':source,'archive':archive,'role':role}
        if path.stat().st_size>2_000_000:
            if role not in('native_primary','native_control_primary'):raise ValueError('NONPRIMARY_OVER2MB: '+source)
            row['max_bytes']=8_000_000
        existing[archive.casefold()]=row;plan['files'].append(row)
    facts=json.loads((ROOT/'analisis/FINAL_TRES_BRAZOS_RECALCULO_R03/HECHOS_RECALCULADOS.json').read_text('utf-8'))
    for record in facts['sources']:
        path=Path(record['path']);relative=path.relative_to(ROOT).as_posix()
        role='native_primary'if '/functions/'in relative or '/RBX06_NATIVE_INTEGRAL_V2/'in relative else'core_recalculation_input'
        add(relative,role=role)
    for name in('CONTINUIDAD_CORE_R06.json','OMISIONES_CORE_R06.json','MAPA_CORE_CERRADO_R06.json','LEER_PRIMERO_CORE_R06.txt',
                'PREPARAR_CONTINUIDAD_CORE_R06_R01.py','LEER_RECURSOS_RECALCULO_R06.txt','LATENCIAS_Q1_Q2_VIDEO_R06_R01.py'):
        add('analisis/'+name,role='core_transfer')
    for name in('HECHOS_RECALCULADOS.json','CRITERIOS_E1_E6.json','MANIFIESTO_FUENTES.json','MATRIZ_F01_F16.csv','OPORTUNIDADES.csv'):
        add('analisis/FINAL_TRES_BRAZOS_RECALCULO_R03/'+name,role='core_recalculated')
    for name in('LATENCIAS_Q1_Q2.json','PRIMARIOS_Q1_Q2.jsonl'):
        add('analisis/LATENCIAS_VIDEO_Q1_Q2_R06_R01/'+name,role='latency_evidence')
    resource_root='analisis/RECURSOS_CORE_CERRADO_R06_R01/'
    resource=json.loads((ROOT/resource_root/'RECURSOS_RECALCULADOS.json').read_text('utf-8'))
    for name in('RECURSOS_RECALCULADOS.json','OWNERS_POR_RUN.csv','IMPORT0_SEPARADO.csv','FASES_POR_PARTICIPANTE.csv','REPETIR_PORTABLE.json'):
        add(resource_root+name,role='resources_evidence')
    for row in resource['portable_primary_selection']:
        add(resource_root+row['archive_relative'],role='native_primary'if row['category']=='owner'else'resources_primary')
    add('evidencia/PAR28/CIERRE_CONCILIADO.json',role='closed_pair_proof')
    add('evidencia/PAR28/LEDGER_R06_AL_CORTE.json',role='historical_ledger_at_MAIN_close')
    # Historical environmental intervention, not a new Native experiment or a policy.
    for condition in('INTACT_R02','CUT_B_R02'):
        folder='evidencia/CONTROL_ENLACE_NUMERICO_'+condition
        for name in('RESULTADO_AMBIENTAL_REPLAY_C02.json','RESUMEN_REPLAY_C02.json'):
            add('../revision_R05_C02/'+folder+'/'+name,'historico_C02/'+folder+'/'+name,'native_control_primary')
    for name in('PAYLOAD_REPLAY_ENLACE_C02.json','PROTOCOLO_REPLAY_ENLACE_C02.json'):
        rel='evidencia/CONTROL_ENLACE_NUMERICO_PREPARADO_R02/'+name
        add('../revision_R05_C02/'+rel,'historico_C02/'+rel,'historical_control_contract')
    for rel in('control/replay_enlace_numerico_C02_R02.py','mundo/Control_Enlace_Numerico_REPLAY_C02_R02.luau'):
        add('../revision_R05_C02/'+rel,'historico_C02/'+rel,'historical_control_code')
    add('../revision_R05_C02/control/studio_mailbox_relay_C02_R07.py','dependencias_operador/studio_mailbox_relay_C02_R07.py','historical_operator_wrapper')
    # The exact resource-primary recipe is portable; no original source strings opened.
    recipe=json.loads((ROOT/resource_root/'REPETIR_PORTABLE.json').read_text('utf-8'))
    plan['recalculations']=[{'id':'resources_core_closed','script':'analisis/RECURSOS_RECALCULO_R06.py',
        'args':[x.replace('{resource_primary_root}','{root}/'+resource_root.rstrip('/')).replace('{new_output}','{out}')for x in recipe['args']],
        'timeout_seconds':120,'expected_outputs':['RECURSOS_RECALCULADOS.json','OWNERS_POR_RUN.csv']}]
    plan['recalculation_note']='Resource recipe exact. Root must add the actual verified full integral recalc argv and any final E6 recalc before finalizing.'
    path=ROOT/'control/EXPORT_CORE_R06_R01.json'
    with path.open('x',encoding='utf-8')as f:json.dump(plan,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'output':str(path),'files':len(plan['files']),'raw_bytes_now':sum((ROOT/x['source']).stat().st_size for x in plan['files']),
        'finalized':False,'scope':'Explicit closed-core proposal; no Native full-root/hash scans or ZIP build.'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
