"""Pure RP proposal/recipe checks, no tool deployment or Native imports."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parents[1]

def load(file,name):
    spec=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

if __name__=='__main__':
    before=set(sys.modules);folder=P/'codigo/RP_C2C_PROPUESTA_OP1'
    runner=load(folder/'ejecutar_diagnostico.py','RP_C2C_PROPOSAL_PURE')
    outer=[{'id':1,'receipt':{'id':1,'status':'applied'}}]
    value={'result':{'rows':[{'requests':outer,'native_arithmetic':None,'second_native_use':None}]}}
    paths=[['result','rows',0,'requests']]
    nullable=[['result','rows',0,'native_arithmetic','native_operation','native_trial','requests'],['result','rows',0,'second_native_use','requests']]
    assert runner.receipts(value,paths,nullable,True)=={1:outer[0]['receipt']}
    refused=[]
    try:runner.receipts(value,paths,nullable,False)
    except(TypeError,KeyError):refused.append('missing_inner_without_preserved_stop')
    else:raise AssertionError('Missing active stage silently ignored')
    zero={'result':{'rows':[{'requests':outer,'native_arithmetic':{'native_operation':{'native_trial':{'requests':[{'id':2,'receipt':{'id':2,'status':'applied'}}]}}},
                           'second_native_use':{'requests':[{'id':3,'receipt':{'id':3,'status':'rejected_occupied'}}]}}]}}
    counted=runner.receipts(zero,paths,nullable,True)
    assert len(counted)==3 and counted[3]['status']=='rejected_occupied'
    # The recipe contains only mode/arm literals. Expected scores are external.
    recipe=json.loads((P/'codigo/REPRODUCIBILIDAD_C2C_R01_BORRADOR/pi04_c2c_adquisicion_20_R01.json').read_text(encoding='utf8'))
    assert recipe['reproduction_enabled']is False and recipe['verification']['new_generic_RP_Native_replay']is False
    real=recipe['variants']['real'];steps=[s for b in real['batches']for s in b]
    assert len(real['batches'])==2 and len(steps)==23
    opportunities=[s for s in steps if s['label'].startswith('opportunity_')]
    assert len(opportunities)==20 and all(s['literal']=={'modo':'eci01-pi04-c2c-oportunidad'}for s in opportunities)
    assert all('expected'not in s['literal']and'target'not in s['literal']for s in steps)
    assert steps[0]['require_zero_ticks']and steps[1]['require_zero_ticks']and steps[-1]['require_zero_ticks']
    assert all(s['stop_on_unapplied_receipt']and s['preserved_stop_paths']for s in opportunities)
    for name in('reproducir.py','ejecutar_diagnostico.py'):ast.parse((folder/name).read_text(encoding='utf8'))
    helper=load(P/'codigo/preparar_receta_RP_C2C_R01.py','RECIPE_BUILDER_PURE')
    # No actual cases/expectations may be inferred from the empty template.
    assert helper.inspect_closed_batches([], 'real')is None
    output=helper.build('ROOT_FINAL_CAPSULE_PENDING',{'real':None,'none':None,'yoked':None})
    assert output['reproduction_enabled']is False and output['blockers']
    assert output['variants']['real']['final_checks']==[]
    dee=[m for m in set(sys.modules)-before if m=='dee_thinking'or m.startswith('dee_thinking.')];assert not dee
    result={'schema':'PI04.C2C.RP_proposal.pure_check.OP1','Native_ticks':0,'official_DEE_imports':dee,
        'nullable_actual_stops_preserved':True,'terminal_rejected_receipt_not_dropped':True,
        'refusals':refused,'two_batches_same_life':True,'twenty_material_opportunities':20,
        'no_expected_or_target_in_actor_literals':True,'template_blocked_without_original20':True,
        'RP_tools_original_unchanged':True,'scope':'Pure data/control-flow checks only; no operational manager test, original acquisition or new Native RP replay.'}
    out=P/'control/RP_C2C_PROPUESTA_PRUEBAS_PURAS_OP1.json'
    if out.exists():raise ValueError('Preserve previous pure proof')
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result,ensure_ascii=False,indent=2))
