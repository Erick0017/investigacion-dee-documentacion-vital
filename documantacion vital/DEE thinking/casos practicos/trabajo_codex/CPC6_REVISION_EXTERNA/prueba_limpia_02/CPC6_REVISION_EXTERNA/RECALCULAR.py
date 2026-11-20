"""Recalculate external CPC6 accounting only. No simulator or scientific state."""
import argparse,collections,json
from pathlib import Path

def rows(root,name):
    with (root/'datos'/name).open(encoding='utf-8') as f:return [json.loads(s) for s in f if s.strip()]

def calculate(root):
    trials=rows(root,'ENSAYOS.jsonl');inputs=rows(root,'ENTRADAS.jsonl');responses=rows(root,'RESPUESTAS.jsonl')
    predictions=rows(root,'PREDICCIONES_TEMPORALES.jsonl');errors=rows(root,'INCIDENCIAS_Y_REPRODUCCIONES.jsonl')
    assert len({r['ensayo'] for r in trials})==len(trials)
    ids={r['ensayo'] for r in trials};assert all(r['ensayo'] in ids for r in inputs+responses+predictions)
    count=collections.Counter(r['tipo'] for r in trials)
    admission=collections.Counter();new_admission=collections.Counter();by_trial={}
    for t in trials:
        q=[r for r in inputs if r['ensayo']==t['ensayo']]
        allc=collections.Counter();newc=collections.Counter();latencies=[]
        for r in q:
            allc[r['estado_admision']]+=r['cantidad'];admission[r['estado_admision']]+=r['cantidad']
            if not r['heredada_del_padre']:newc[r['estado_admision']]+=r['cantidad'];new_admission[r['estado_admision']]+=r['cantidad']
            if r['estado_admision']=='applied' and r['t_solicitado_rel'] is not None and r['t_aplicado_rel'] is not None:
                latencies.extend([r['t_aplicado_rel']-r['t_solicitado_rel']]*r['cantidad'])
        denominator=sum(v for k,v in newc.items() if k!='scheduled')
        by_trial[t['ensayo']]={'solicitudes_registradas':sum(allc.values()),'estados':dict(sorted(allc.items())),
            'entradas_nuevas_no_heredadas':sum(newc.values()),'estados_nuevos':dict(sorted(newc.items())),
            'fraccion_aplicada_entre_finalizadas_nuevas':newc['applied']/denominator if denominator else None,
            'denominador_fraccion':denominator,'latencia_admision_con_tiempos':{'n':len(latencies),'media':sum(latencies)/len(latencies) if latencies else None,
            'min':min(latencies) if latencies else None,'max':max(latencies) if latencies else None}}
    by_var={}
    for variable in sorted({r['variable'] for r in responses}):
        rr=[r for r in responses if r['variable']==variable]
        eligible={r['ensayo'] for r in rr if r['numero_respuestas'] is not None}
        active={r['ensayo'] for r in rr if r['estado']=='respuesta_publicada' and (r['numero_respuestas'] or 0)>0}
        by_var[variable]={'filas_observadas':len(rr),'ensayos_con_medida_numerable':len(eligible),
            'ensayos_con_respuesta_decodificada_no_vacia':len(active),'estados_de_fila':dict(sorted(collections.Counter(r['estado'] for r in rr).items())),
            'advertencia':'Las filas temporales no son replicas independientes; presencia de salida no equivale a acierto o significado.'}
    protocol=[]
    contrast_file=json.loads((root/'CONTROLES_Y_RESERVAS.json').read_text(encoding='utf-8'))
    reserve_ids={x['referencia'] for x in contrast_file['contrastes_reservados_completos']}|{x['comparador'] for x in contrast_file['contrastes_reservados_completos']}
    def readout(cid,variable,t):
        rr=[r for r in responses if r['ensayo']==cid and r['variable']==variable and r['t_rel']==t]
        if not rr:return {'cobertura':'NO_PUBLICADA','clases':None,'n':None}
        vals=sorted({str(x) for r in rr for x in (r['respuestas'] or [])})
        return {'cobertura':'PUBLICADA','clases':vals,'n':sum(r['numero_respuestas'] or 0 for r in rr)}
    for cid in sorted(reserve_ids):
        first=readout(cid,'FORMA_01',53);second=readout(cid,'FORMA_02',90);last=readout(cid,'FORMA_01_REMOTA',162)
        same=bool(first['clases']) and bool(last['clases']) and first['clases']==last['clases'] if first['clases'] is not None and last['clases'] is not None else None
        protocol.append({'ensayo':cid,'primera_consulta':first,'segunda_forma':second,'consulta_posterior':last,
            'misma_clase_primera_y_posterior':same,'secuencia_con_ambas_formas_y_reexpresion':bool(same and second['clases']) if same is not None else None})
    comparisons=[]
    for c in contrast_file['contrastes_reservados_completos']:
        a=readout(c['referencia'],c['variable_de_lectura'],c['t_rel']);b=readout(c['comparador'],c['variable_de_lectura'],c['t_rel'])
        comparisons.append({'contraste':c['contraste'],'referencia':c['referencia'],'comparador':c['comparador'],
            'factor_declarado':c['factor_declarado'],'variable':c['variable_de_lectura'],'t_rel':c['t_rel'],
            'lectura_referencia':a,'lectura_comparador':b,
            'clases_iguales':a['clases']==b['clases'] if a['clases'] is not None and b['clases'] is not None else None})
    result={'tipo':'CALCULOS_OBSERVACIONALES_REPRODUCIBLES','n_ensayos':len(trials),'n_familias':len({t['familia'] for t in trials}),
        'tipos':dict(sorted(count.items())),'preparaciones':sum(t['preparaciones'] for t in trials),
        'forks_diagnosticos':sum(t['forks_diagnosticos'] for t in trials),'continuaciones':sum(t['continuaciones'] for t in trials),
        'filas_entradas_agrupadas':len(inputs),'solicitudes_contadas':sum(admission.values()),'admision':dict(sorted(admission.items())),
        'admision_no_heredada':dict(sorted(new_admission.items())),'por_ensayo':by_trial,'por_variable':by_var,
        'precedencia_temporal':{'registros':len(predictions),'emision_estrictamente_anterior':sum(r['emision_rel']<r['objetivo_rel'] for r in predictions),
            'horizontes_coherentes':all(r['horizonte']==r['objetivo_rel']-r['emision_rel'] for r in predictions),'acierto_predictivo':'NO_CALCULABLE_SIN_VALOR_PREDICHO_PUBLICADO'},
        'secuencia_reservada':protocol,'testigos_de_secuencia_completa':sum(x['secuencia_con_ambas_formas_y_reexpresion'] is True for x in protocol),
        'denominador_testigos_reservados_y_controles':len(protocol),'incidencias_y_reproducciones_tecnicas':len(errors),
        'recuentos_no_son_muestras_independientes':True,'veredicto_global_de_inteligencia':None}
    assert (len(trials),result['preparaciones'],result['forks_diagnosticos'],result['continuaciones'])==(129,94,29,6)
    return result,{'comparaciones':comparisons,'alcance':'Contrastes de salidas publicadas; no verifican selectividad interna, transporte o equivalencia fisica de recursos.'}

def encoded(x):return json.dumps(x,ensure_ascii=False,indent=2)+'\n'
def main():
    p=argparse.ArgumentParser();p.add_argument('--raiz',type=Path,default=Path(__file__).resolve().parent);p.add_argument('--verificar',action='store_true');a=p.parse_args()
    values=calculate(a.raiz)
    for name,value in zip(('CALCULOS.json','COMPARACIONES.json'),values):
        path=a.raiz/name;content=encoded(value)
        if a.verificar:assert path.read_text(encoding='utf-8')==content,name+' differs'
        else:path.write_text(content,encoding='utf-8',newline='\n')
    print(json.dumps({'estado':'RECALCULADO_Y_COINCIDENTE' if a.verificar else 'RECALCULADO','ensayos':values[0]['n_ensayos'],'testigos_secuencia':values[0]['testigos_de_secuencia_completa']}))
if __name__=='__main__':main()
