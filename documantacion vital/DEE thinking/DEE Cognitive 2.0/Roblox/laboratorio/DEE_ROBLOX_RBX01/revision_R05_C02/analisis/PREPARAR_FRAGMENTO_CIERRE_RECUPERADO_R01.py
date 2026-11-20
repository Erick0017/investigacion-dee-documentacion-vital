"""Passive Native/PROGRAMMED closure fragment; no scientific/engine execution."""
from __future__ import annotations
import ast
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analisis/CIERRE_RECUPERADO_R01'
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'


def read(path):
    raw=Path(path).read_bytes();value=json.loads(raw)
    if Path(path).read_bytes()!=raw:raise RuntimeError('Frozen source changed')
    return value,{'path_relative_R05':str(Path(path).relative_to(ROOT)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}


def main():
    metrics,ms=read(OUT/'METRICAS_NATIVE_PROGRAMMED_AI_PENDIENTE/RESUMEN_COMPARATIVO.json')
    native,ns=read(ROOT/'analisis/MAIN_R02_FINAL_RECALCULO_R01/HECHOS_Y_ATRIBUCION_MAIN_R02_FINAL.json')
    pw,ps=read(ROOT/'evidencia/PROGRAMMED_PERIODO_02/WORLD_CHECKPOINT.json')
    pr,prs=read(ROOT/'evidencia/PROGRAMMED_PERIODO_02/RESULTADO.json')
    pc,pcs=read(ROOT/'evidencia/PROGRAMMED_PERIODO_02/COMPARATOR_CLOSED.json')
    dev,ds=read(ROOT/'analisis/DEV_FINAL_RECALCULO_R02/HECHOS_Y_ATRIBUCION_DEV_R02.json')
    paired,pas=read(ROOT/'analisis/CONTROL_MEMPAIR_RECALCULO_R01/HECHOS_Y_ATRIBUCION.json')
    if pr['status']!='COMPARATOR_HORIZON_CLOSED'or pr['process_returncode']!=0 or pw['S']['completedCycles']!=18:
        raise ValueError('Closed18 PROGRAMMED required')
    if pc['nativeOwnerOpened']is not False or pc['nativeTicks']!=0 or pc['writerDrained']is not True:
        raise ValueError('Comparator must remain external/closed')
    if metrics['issues']:raise ValueError('Inspect recalc issues before closure fragment')
    policy=ROOT/'comparadores/adaptadores_C02.py';raw_policy=policy.read_bytes();tree=ast.parse(raw_policy.decode('utf8'))
    rules=next(ast.literal_eval(node.value)for node in tree.body if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PUBLIC_RULES'for t in node.targets))
    policy_source={'path_relative_R05':str(policy.relative_to(ROOT)),'bytes':len(raw_policy),'sha256':hashlib.sha256(raw_policy).hexdigest(),
                   'PUBLIC_RULES_literal':rules,'read_as_text_AST_not_imported':True}
    totals={r['arm']:r for r in metrics['summary_rows']if r['scope']=='ALL_ACTUALLY_OBSERVED'}
    program_rows=[r for r in metrics['opportunity_rows']if r['arm']=='PROGRAMMED']
    fragment={
      'schema':'DEE.RBX01.C02.recovered_closure.scientific_fragment.R01',
      'inspection_utc':datetime.now(timezone.utc).isoformat(),
      'scope':'Native18 and PROGRAMMED18 closed historical records only. AI later closure remains prospective/pending; no new Native permitted here.',
      'execution_in_this_synthesis':{'Native':0,'model_calls':0,'MCP':0,'HTTP':0,'simulations':0},
      'Native_closed':{'life':native['life_id'],'N':67,'parent_T':947395,'final_T':975547,'new_ticks':28152,
                       'metrics':totals['LIVE_NATIVE'],'main_findings':[
                         'All36 actual World actions/ticks matched Native phase outputs.7/7 numeric calculations were correct for the actual opcode; two real12 intermediates fed B and produced8.',
                         'No resource/delivery. The sole lock check at12 had no current B/code; it was not an observed rejection of numeric8.',
                         'Two concordant-sign lessons were4/6 admitted; no lesson was encountered during the reversed-sign interval8..13. Later compatible signs do not isolate pure retention from refresh/readquisition.',
                         'One key/round kept FAMILIAR9,3,4; six reserved-time opportunities were completed but reserved operand tuples were not presented.',
                         'Same life/session was reopened at6 and closed at18; no post18 reopen or final complete inherited12/12 panel. No principal adoption.']},
      'PROGRAMMED_closed':{'wire_id':pw['native_life_id'],'DEE_life':False,'Native_ticks':0,'environment_completed':18,
                          'metrics':totals['PROGRAMMED'],'final_S':pw['S'],
                          'actual_actions':dict(__import__('collections').Counter(action for row in program_rows for action in row['actions'])),
                          'lesson_cycles':[r['cycle']for r in program_rows if r['lessons']],
                          'calculation_rows':[{'cycle':r['cycle'],'calculations':r['calculations']}for r in program_rows if r['calculations']],
                          'lock_rows':[{'cycle':r['cycle'],'locks':r['lock_checks']}for r in program_rows if r['lock_checks']],
                          'main_findings':[
                            'Prepared program obtained one resource and delivered one, with8/8 correct arithmetic outputs; Python dictionary/arithmetic/planning are disclosed reference mechanisms, not DEE.',
                            'Observed18 ASK and18 EXIT_0. Its code contains goal hierarchy and BFS on learned edges, but necessity of BFS was not ablated and is not established by this constant route-action sequence.',
                            'Learned visible reverse signs at11 via direct dictionary update, used9-3=6 then6+4=10; lock at14 rejected10 because the current world law had returned to expected8. Earlier lock9 rejected old8 while expected10.',
                            'Second key was acquired at6. Its retained FAMILIAR tuple means no reserved operand tuple was experienced here either.',
                            'The closure coherence.completed_cycles=6 names the retained bridge boundary row from the first suspension; full World boundary/events show18 and completed_operations66. Do not substitute the stale summary for the final primary.']},
      'comparison_scope':{
        'Native_PROGRAMMED_common_observed_prefix':min(metrics['arms']['LIVE_NATIVE']['completed_contiguous_prefix'],metrics['arms']['PROGRAMMED']['completed_contiguous_prefix']),
        'three_arm_common_prefix_at_this_cut':0,'AI_result':'No AI game evidence supplied at this cut; not scored as failure. Root has separately authorized a prospective AI-only closure window.',
        'one_history_per_arm':True,'independent_population_inference':False,
        'conclusion':'The programmed complete configuration obtained greater task utility in these18 opportunities; this does not identify an isolated cognitive superiority because priors, goal encoding and memory/admission mechanisms were not matched.',
        'information_matched':'Same scenario, actuator/body contract and legal dynamic observation fields; no edge graph, future schedule, private target/code or other agent history intentionally supplied.',
        'information_not_matched':'PUBLIC_RULES supplies symbolic codec semantics, zone roles and Archive1->A2->B4->Gate5->Base0 decomposition to references. Program also implements that goal hierarchy and BFS. Native receives physical scalar/sign inputs and inherited/prepared mechanisms, without demonstrated equivalent goal instruction.',
        'admission_not_matched':'Native teaching can be physically rejected at occupied RAW ports; programmed lesson storage directly updates a Python dictionary. Equal visible lesson content is not equal admission reliability or learned representation.',
        'return_objective_limit':'Native generic False covers both harmless movement and useful collection; no separately demonstrated resource/delivery-specific objective transduction. The references receive that objective symbolically.',
        'frozen_policy_preserved':'No policy change after PROGRAMMED6; this fragment changes no rule or criterion.'},
      'positive_controls_kept_separate':{
        'DEV4':{'life':dev['life_id'],'N':67,'T':953651,'observation':'Native luma-6-2->4, same-life reopen, nara+actual4+1->5, one resource contact/inventory unit; no delivery in four-opportunity horizon.'},
        'MEMPAIR6':{'life':paired['life_id'],'N':67,'T':956779,'observation':'Before lesson8/7; after inverted lesson4/5; later7-3->4;5/5 numeric results. No Roblox and no desynchronized control executed.'},
        'ENV_B_cut':'Recorded actual5 versus B absent changed resource1->0 with same recorded actions/costs,0 new Native ticks. Not a new Native learning/control trajectory.'},
      'continuation':'Original protected REAL2 remains the principal reference; C02 descendant/control experiences are not merged. Final C02 Native/World states are preserved but the historical scope/horizon is closed.',
      'sources':[ms,ns,ps,prs,pcs,ds,pas,policy_source],
      'not_changed':['INFORME_C02.md','principal','kernel/WHL','Manual Maestro','frozen PUBLIC_RULES/policies']}
    target=OUT/'FRAGMENTO_RESULTADOS_Y_LIMITES_R01.json'
    with target.open('x',encoding='utf8')as stream:stream.write(json.dumps(fragment,ensure_ascii=False,indent=2)+'\n')
    with(ROOT/'fuentes/MATRIZ_REPERTORIO_BASE.csv').open(encoding='utf-8-sig',newline='')as stream:base=list(csv.DictReader(stream))
    with(ROOT/'fuentes/MATRIZ_REPERTORIO_C02_FINAL_NATIVE.csv').open(encoding='utf8',newline='')as stream:main_rows={r['id']:r for r in csv.DictReader(stream)}
    cohorts=[('PRINCIPAL_REFERENCIA',PREFIX+'REAL2_01',67,947395,None,'Historico:panel relevante anterior943970;sin nueva consulta al principal'),
             ('DEV',dev['life_id'],67,953651,4,'Desarrollo;no principal ni réplica independiente'),
             ('MEMPAIR',paired['life_id'],67,956779,6,'Control focal;no Roblox ni principal'),
             ('MAIN_R02',native['life_id'],67,975547,18,'Descendiente experimental;no adoptado'),
             ('PROGRAMMED',pw['native_life_id'],None,None,18,'Referencia externa Python;no vida DEE'),
             ('AI_PENDIENTE','CONVENTIONAL_AI',None,None,0,'Sin resultado aportado a este corte;no fracaso puntuado')]
    statuses={
      'DEV':{'01':'Leccion luma-/nara+ admitida6/6 y uso posterior;sin baseline contemporaneo propio',
             '02':'nara+ y enteroA4 usados tras reapertura;no panel contextual completo',
             '04':'2/2 numeros Native formados:4 y5; algoritmo preparado',
             '05':'A4->B5->recurso1;entrega0 por horizonte4',
             '06':'8 acciones reales/4 oportunidades;424 entradas aplicadas',
             '07':'Retornos presentes;sin control de contingencia exclusivo',
             '12':'N67 T953651;misma sesion tras reapertura en frontera2 y cierre4;sin adopcion'},
      'MEMPAIR':{'01':'Revisión antes8/7 despues4/5; variante posterior4;control desync no ejecutado',
                 '02':'Uso sucesivo en una vida tras enseñanza;no reabrir demostrado aquí',
                 '04':'5/5 cálculos Native correctos;987 entradas aplicadas',
                 '05':'Transportes reales8->7 y4->5;secuencia focal preparada',
                 '06':'6 oportunidades focales;no actuación Roblox',
                 '07':'Cambio con historia;emparejamiento exclusivo no aislado',
                 '12':'N67T956779;cerrado/guardado;rama de control separada'},
      'PROGRAMMED':{'01':'Diccionario Python actualizado por lecciones en1/6/11/16;no adquisición Native',
                    '02':'Historia/estado propio persistido tras frontera6;memoria de referencia externa',
                    '04':'8/8 resultados por aritmética Python;no DEE',
                    '05':'8 salidas aritméticas y transporteA->B;recurso1/entrega1',
                    '06':'18ASK y18EXIT_0 observados;plantilla de metas/BFS preparados',
                    '07':'Refresh tras rechazo es regla escrita;no aprendizaje del algoritmo',
                    '08':'Jerarquia de metas yBFS preparados;su necesidad no ablatida',
                    '09':'Coste20 permisos;sin termodinámica ni regulación Native',
                    '12':'18 oportunidades;NativeTicks0;identidad COMPARATOR y estado propio reabierto'},
    }
    table=OUT/'MATRIZ_12_FAMILIAS_POR_VIDA_Y_CORTE_R01.csv'
    fields=('familia_id','familia','sujeto','identidad','N_DEE','T_DEE','oportunidades_esta_prueba','estado_en_este_corte','atribucion_y_limites','fuente')
    with table.open('x',encoding='utf8',newline='')as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for role,life,N,T,opps,limit in cohorts:
            for row in base:
                if role=='PRINCIPAL_REFERENCIA':
                    prefix='MECANISMO_HISTORICO_EN_OTRAS_VIDAS_NO_CONFIRMADO_EN_PRINCIPAL: 'if row['id']in('10','11')else'BASE_DOCUMENTADA_NO_NUEVA_VALIDACION_DEL_CORTE: '
                    status=prefix+row['base_documentada'];source=row['localizadores']
                elif role=='MAIN_R02':status=main_rows[row['id']]['estado_MAIN_R02'];source=main_rows[row['id']]['fuente_final_MAIN']
                elif role=='AI_PENDIENTE':status='NO_EJECUTADO_EN_DATOS_APORTADOS;sin inferencia de incapacidad';source='Corte recuperado antes de nueva AI'
                else:status=statuses.get(role,{}).get(row['id'],'NO_ENSAYADO_NUEVAMENTE_EN_ESTA_RAMA; no heredar éxitos de otra vida');source=str(target.relative_to(ROOT))
                writer.writerow(dict(zip(fields,(row['id'],row['familia'],role,life,N,T,opps,status,limit,source))))
    print(json.dumps({'fragment':str(target.relative_to(ROOT)),'fragment_bytes':target.stat().st_size,'fragment_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                      'matrix':str(table.relative_to(ROOT)),'rows':len(base)*len(cohorts),'matrix_bytes':table.stat().st_size,'matrix_sha256':hashlib.sha256(table.read_bytes()).hexdigest()},ensure_ascii=False))


if __name__=='__main__':main()
