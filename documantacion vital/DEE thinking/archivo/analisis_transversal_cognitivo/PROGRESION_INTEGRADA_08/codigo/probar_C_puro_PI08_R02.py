"""Pure C codec/conditional transport/source tests; no Native import/execution."""
from pathlib import Path
import ast, copy, hashlib, importlib.util, json, sys

H=Path(__file__).resolve().parent;P=H.parent

def main():
    spec=importlib.util.spec_from_file_location('PI08_C_pure_only',H/'pi08_consulta_condicional_C_R02.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    checks=[]
    def check(name,value):
        if not value:raise AssertionError(name)
        checks.append({'check':name,'passed':True})
    check('stdlib_import_NO_DEE',not any(n.startswith('dee_thinking')for n in sys.modules))
    p,ph=m.protocol(False);check('draft_not_materially_authorized',p['status']=='DRAFT_PREPARED_NO_MATERIAL_AUTHORIZATION')
    try:m.protocol(True)
    except(FileNotFoundError,ValueError):check('material_requires_actual_Root_source_seal',True)
    else:check('material_requires_actual_Root_source_seal',False)
    check('six_fixed_cases',[row['cue']for row in p['schedule']]==['threat','threat','falsecue','none','threat','falsecue'])
    check('whole_bound_with_preparation',p['preparation_ticks']+6*p['max_ticks_per_C_opportunity']==12597<=p['total_C_ticks_bound']==12600)
    check('no_new_TC_origin',p['origin']==[8,40,50]and p['delay_laps']==6)
    for mode in m.MODES:m.validate_literal({'modo':mode});check('exact_literal_'+mode,True)
    for field,value in [('forzar','pulso'),('cue','threat'),('bit',1),('target',1),('ticks',1),('action',1)]:
        try:m.validate_literal({'modo':m.EPISODE,field:value})
        except ValueError:check('actor_override_refused_'+field,True)
        else:raise AssertionError('Actor override accepted')
    zero={'raw':0,'state':0,'semantic':0,'s_reg':0,'direction':[0,0,0]}
    plusX={'raw':123,'state':1,'semantic':1,'s_reg':0,'direction':[1,0,0]}
    plusZ={'raw':456,'state':1,'semantic':1,'s_reg':0,'direction':[0,0,1]}
    check('same_partial_STATE_hides_direction',plusX['state']==plusZ['state']==1)
    for label,sample,expected in [('exact_RAW0',zero,0),('active_plusX',plusX,0),('active_plusZ',plusZ,1)]:
        value=m.decode_extra(sample);check('actual_codec_'+label,value['valid']and type(value['bit'])is int and value['bit']==expected)
    for label,sample in [('state0_nonzeroRAW',dict(zero,raw=1)),('other_direction',dict(plusZ,direction=[-1,0,1])),('SEM4',dict(plusZ,semantic=4))]:
        value=m.decode_extra(sample);check('NULL_not_filled_'+label,value['valid']is False and value['bit']is None)
    for available in(False,True):
        for label,sample in[('plusX',plusX),('plusZ',plusZ),('exactRAW0',zero)]:
            progress={'ordinal':0,'sample_register':{'ordinal':0,'question_applied_and_signature':available,'actual_preview_observation':sample}}
            before=copy.deepcopy(progress);value=m._second_datum(progress)
            check('fixed_conditional_datum_%s_%s'%(available,label),value==(m.decode_extra(sample)['bit'] if available else 0))
            check('sample_register_immutable_%s_%s'%(available,label),progress==before)
    try:m._second_datum({'ordinal':1,'sample_register':{'ordinal':0,'question_applied_and_signature':True,'actual_preview_observation':plusZ}})
    except ValueError:check('no_stale_sample_reuse',True)
    else:check('no_stale_sample_reuse',False)
    try:m._second_datum({'ordinal':0,'sample_register':{'ordinal':0,'question_applied_and_signature':True,'actual_preview_observation':dict(zero,raw=1)}})
    except ValueError:check('queried_unknown_RAW_stops_not_expected_fallback',True)
    else:check('queried_unknown_RAW_stops_not_expected_fallback',False)
    check('NoQuery_does_not_reveal_hidden_unknown_or_direction',m._second_datum({'ordinal':0,'sample_register':{'ordinal':0,'question_applied_and_signature':False,'actual_preview_observation':dict(zero,raw=1)}})==0)
    original=P.with_name('PROGRESION_INTEGRADA_07')/'codigo/pi07_regulacion_R03.py';source=original.read_text('utf-8-sig');node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)and n.name=='episode')
    actual=''.join(source.splitlines(True)[node.lineno-1:node.end_lineno])+'\n'
    file=H/'pi08_consulta_condicional_C_segunda_R02.py';copied=file.read_text('utf8');n=next(n for n in ast.parse(copied).body if isinstance(n,ast.FunctionDef));copied=''.join(copied.splitlines(True)[n.lineno-1:n.end_lineno])+'\n'
    reversals=[('sent_datum=_c_second_datum(m)','sent_datum=0 if sensor_ablation else datum'),("'C_stage_ordinal':m['ordinal']","'cumulative_PI07_ordinal':28+m['ordinal']"),
       ('Inherited Native selection with one registered actual extra bit after an optional first request. Environment and transport are prepared; first-query credit and value of information are not causally isolated in this single-world partial protocol.','New prepared Native selection plus identity sensor and fixed transducer. Host offers opportunities/environment and evaluates actual function; forced controls are not Native learned decisions. Useful learning requires causal controls and conservation.')]
    for before,after in reversals:check('one_declared_second_stage_change_'+str(len(checks)),copied.count(before)==1);copied=copied.replace(before,after)
    check('second_stage_rest_literal40648f',copied==actual)
    check('second_source_fingerprint',hashlib.sha256(file.read_bytes()).hexdigest()==m.SECOND_SHA)
    own=(H/'pi08_consulta_condicional_C_R02.py').read_text('utf8')
    check('first_datum_is_actual_STATE',"sample = c._observe(a, PREVIEW); datum = int(sample['state'])"in own)
    check('only_Native_plus1_schedules_question',"if motor1 == 1 else None"in own)
    check('applied_request_missing_physical_signature_stops',"if applied and not signature:"in own and'NULL access is not materialzero'in own)
    check('first_trace_has_no_assigned_generic_return',"'no_generic_return_scheduled_for_first_trace':True"in own)
    for name in('pi08_consulta_condicional_C_R02.py','pi08_consulta_condicional_C_segunda_R02.py','preparar_C_PI08_R02.py','importar_C_PI08_R02.py','ejecutar_C_PI08_R02.py'):
        ast.parse((H/name).read_bytes());check('AST_'+name,True)
    output={'schema':'DEE.PI08.C.pure_codec_and_source_tests.R02','passed':True,'checks':checks,'check_count':len(checks),'Native_executed':False,'DEE_imported':False,
            'files':{name:{'bytes':(H/name).stat().st_size,'sha256':hashlib.sha256((H/name).read_bytes()).hexdigest()}for name in('pi08_consulta_condicional_C_R02.py','pi08_consulta_condicional_C_segunda_R02.py','PROTOCOLO_PI08_C_R02.json','preparar_C_PI08_R02.py','importar_C_PI08_R02.py','ejecutar_C_PI08_R02.py')},
            'scope':'Pure validation, conditional actual-sample codec, immutable register and exact copied-source comparison. No Native device admission, functional effect, asking strategy or passivity demonstration.'}
    target=P/'control/PRUEBAS_PURAS_C_PI08_R02.json'
    with target.open('x',encoding='utf8')as out:json.dump(output,out,ensure_ascii=False,indent=2);out.write('\n')
    print(json.dumps({'passed':True,'checks':len(checks),'proof':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()},indent=2))

if __name__=='__main__':main()
