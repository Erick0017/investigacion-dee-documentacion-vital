"""Map the recorded, already executed core recalc argv to package-relative inputs."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def main():
    plan=json.loads((ROOT/'control/EXPORT_CORE_R06_R01.json').read_text('utf-8'))
    record=json.loads((ROOT/'analisis/ARGV_REAL_FINAL_TRES_BRAZOS_R03.json').read_text('utf-8'))
    original=record['argv_relative_to_working_directory'];script=original[0];args=[];index=1
    while index<len(original):
        value=original[index]
        if value=='--native-functions':
            args.append(value)
            args.extend('{root}/'+Path(row['path']).relative_to(ROOT).as_posix()for row in record['native_function_files_explicit_from_report'])
            index+=2;continue
        if value=='--output':args.extend((value,'{out}'));index+=2;continue
        if value.startswith('--'):args.append(value)
        elif '='in value:
            label,path=value.split('=',1);args.append(label+'={root}/'+path)
        else:args.append('{root}/'+value)
        index+=1
    existing={x['archive'].casefold()for x in plan['files']}
    def add(rel,role):
        if not(ROOT/rel).is_file():raise ValueError('EXPLICIT_SOURCE_MISSING: '+rel)
        if rel.casefold()not in existing:plan['files'].append({'source':rel,'archive':rel,'role':role});existing.add(rel.casefold())
    for rel in('analisis/ARGV_REAL_FINAL_TRES_BRAZOS_R03.json','analisis/CONSOLIDAR_COMPARACION_R06_R01.py',
               'comparadores/AI_RUN_01/POLICY_EVENTS_R06.jsonl','comparadores/AI_RUN_01/MODEL_HISTORY_R06.jsonl'):
        add(rel,'core_reproducibility')
    plan['recalculations'].insert(0,{'id':'integral_core_closed','script':script,'args':args,'timeout_seconds':180,
        'expected_outputs':['HECHOS_RECALCULADOS.json','CRITERIOS_E1_E6.json','OPORTUNIDADES.csv']})
    plan['recalculations'].append({'id':'actual_Q1_Q2_latency','script':'analisis/LATENCIAS_Q1_Q2_VIDEO_R06_R01.py',
        'args':[x for arm,folders in [('LIVE_NATIVE',['NATIVE_BLOQUE_01','NATIVE_BLOQUE_02_R02','NATIVE_CONTINUACION_C16_R01']),
            ('PROGRAMMED',['PROGRAMMED_BLOQUE_01','PROGRAMMED_BLOQUE_02']),('CONVENTIONAL_AI',['AI_BLOQUE_01','AI_BLOQUE_02'])]
            for folder in folders for x in('--events',arm+'={root}/evidencia/'+folder+'/EVENTS.jsonl')]+['--output','{out}'],
        'timeout_seconds':120,'expected_outputs':['LATENCIAS_Q1_Q2.json','PRIMARIOS_Q1_Q2.jsonl']})
    plan['recalculations'].append({'id':'core_comparison_table','script':'analisis/CONSOLIDAR_COMPARACION_R06_R01.py',
        'args':['--facts','{root}/analisis/FINAL_TRES_BRAZOS_RECALCULO_R03/HECHOS_RECALCULADOS.json',
            '--policy-events','{root}/comparadores/AI_RUN_01/POLICY_EVENTS_R06.jsonl',
            '--model-history','{root}/comparadores/AI_RUN_01/MODEL_HISTORY_R06.jsonl','--output','{out}'],
        'timeout_seconds':120,'expected_outputs':[]})
    plan['recalculation_note']='Four recorded/passive core recipes; original native-functions directory expanded to the twelve actual preserved files. Root still adds only final closed E6/video evidence and reruns clean extracted QA before delivery.'
    path=ROOT/'control/EXPORT_CORE_R06_R02.json'
    with path.open('x',encoding='utf-8')as f:json.dump(plan,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'files':len(plan['files']),'recalculations':len(plan['recalculations']),'raw_bytes_now':sum((ROOT/x['source']).stat().st_size for x in plan['files']),
        'finalized':False,'output':str(path),'Native_MCP_SQLite_model_calls':0},indent=2))
if __name__=='__main__':main()
