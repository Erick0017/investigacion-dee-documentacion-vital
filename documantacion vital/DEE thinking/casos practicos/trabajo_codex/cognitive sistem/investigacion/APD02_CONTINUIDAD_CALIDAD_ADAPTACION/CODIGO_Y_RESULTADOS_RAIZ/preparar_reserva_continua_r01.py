"""Fixed prospective60minute MAIN protocol; no Runtime, solver or route lookup.

All opportunity times, raw inputs, explicit lessons and environmental changes
are fixed here before seeing any reserve response. Only the stopped input
snapshot hash is provided later. Event names remain transport/auditor labels.
"""
import argparse,json
from pathlib import Path

def protocol(snapshot):
    events=[]
    def add(t,name,rows,feedback='real'):
        events.append({'at_seconds':t,'id':name,'payload':{'operacion':'sesion','retorno':feedback,'situaciones':rows}})
    def environment(t,name,prices=(1,1),faults=('none','none'),available=(True,True),delay=(0,0)):
        add(t,name,[{'modo':'apd02-ambiente','configuracion':{'precios':list(prices),'demora':list(delay),'disponibilidad':list(available),'fallos':list(faults),'presupuesto':2,'demora_maxima':8}}])
    def task(t,name,word,a,b,feedback='real'):add(t,name,[{'modo':'apd02','texto':word,'operandos':[a,b]}],feedback)
    def memories(t,name):add(t,name,[{'modo':'memoria','contexto':c}for c in('alfa','beta','gamma','delta','epsilon','zeta')],'omit')
    def function(t,name,word,value,context):add(t,name,[{'modo':'apd02-lenguaje','texto':word,'valor':value,'contexto':context}],'omit')
    environment(0,'law_A',prices=(1,5));memories(10,'old6_initial_no_feedback')
    task(90,'a1','suma',12,9);task(180,'a2','diferencia',30,11)
    add(300,'new_opposite_lexical_lesson',[{'modo':'apd02-docencia','texto':'compara','senal':-1,'revision':True}])
    function(315,'revised_compara_uses_gamma','compara',9,'gamma');task(420,'a3','agrega',11,8)
    environment(600,'law_B',prices=(5,1));task(615,'b1','resta',29,12);task(720,'b2','total',10,13)
    add(900,'hidden_goal',[{'modo':'apd02-meta','texto':'suma','operandos':[13,7],'segundo_visible':False}])
    memories(1020,'old6_middle_no_feedback')
    environment(1200,'law_A_again',prices=(1,5));task(1215,'a4','suma',14,8);task(1320,'a5','quita',31,9)
    add(1450,'explicit_lexical_restore',[{'modo':'apd02-docencia','texto':'compara','senal':1,'revision':True}])
    function(1470,'restored_compara_not_retention','compara',57,'beta')
    add(1560,'new_beta_reference',[{'modo':'memoria','operacion_memoria':'revisar','contexto':'beta','senal':1}])
    function(1590,'old_learned_request_new_content','recuerda',7,'beta')
    add(1650,'renewed_accumulator',[{'modo':'apd02-acumular','valor':1,'demora_periodos':4}],'omit')
    add(1750,'new_assisted_combination',[{'modo':'apd02-componer','formas':['total','diferencia'],'datos':[6,7,4]}])
    environment(1860,'law_B_again',prices=(5,1));task(1875,'b3','resta',28,10);task(1980,'b4','agrega',15,9)
    raw=[0]*128;raw[0]=2;raw[1]=1
    add(2100,'joint128_literal_frame',[{'modo':'crudos','componentes':raw}],'omit');memories(2220,'old5_plus_revised_beta_no_feedback')
    environment(2300,'equal_cost_numeric_quality',faults=('wrong_value','none'))
    task(2315,'numeric_quality1','suma',13,10);task(2400,'numeric_quality2','resta',26,8)
    environment(2490,'external_unavailable',available=(True,False))
    task(2505,'availability1','total',11,12);task(2580,'availability2','quita',30,13)
    environment(2700,'native_delay64',delay=(64,0));task(2715,'delay1','suma',15,7);task(2820,'delay2','diferencia',31,10)
    environment(2940,'healthy_both')
    add(2955,'hidden_goal_after_other_work',[{'modo':'apd02-meta','texto':'diferencia','operandos':[29,8],'segundo_visible':False}])
    add(3150,'old_math6_no_feedback',[{'modo':'apd02','texto':f,'operandos':values}for f,values in zip(('suma','diferencia','agrega','resta','total','quita'),([4,13],[25,8],[6,12],[28,7],[8,15],[30,11]))],'omit')
    function(3350,'current_new_request_no_feedback','compara',7,'gamma');function(3370,'historical_new_request_no_feedback','recuerda',7,'beta')
    add(3480,'accumulator_delayed_retention',[{'modo':'apd02-acumular','valor':0,'demora_periodos':8}],'omit')
    memories(3550,'final_current_memory_no_feedback')
    return {'schema':'APD02.prospective_single_owner_integrated_reserve.R01','life':'APD02_MAIN','prefix':'apd02hr_',
      'snapshot_sha256':snapshot,'enabled_seconds':3600,'events':events,
      'fixed_before_reserve':True,'one_owner_required':True,'idle_quantum_ticks':1,'idle_interval_seconds':0.1,
      'attribution':'Explicit teacher revisions of compara and beta are NEW declared teaching, not retention. Beta changes from inherited minus to plus; the other five contexts receive no teacher. Comparison/history addressing, arithmetic, ACT/QUERY transduction and opportunity timing remain prepared. All actual raw128 values are transported separately, not summed by host. The local route continues changing under physical consequences; no hidden block or future target is sent to it.',
      'evaluation':'Every request stays in the denominator, including rejection/no-response/wrong artifact/cost/delay. Old-memory and final mathematical panels have feedback OMIT, separate from adaptation/teaching windows. Task success, valid numeric file and resource acceptability remain separate. Any uncertain effect stops normal work without retry. No robustness or24/7 claim follows from this finite horizon.',
      'prospective_duration_rule':'3600 monotonic enabled seconds under ONE owner; busy Native operations do not reset the clock, pause or replace the world. A late event starts late and its lateness is recorded; no adaptive simulator pause rescues an answer.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if len(a.snapshot)!=64 or any(c not in'0123456789abcdef'for c in a.snapshot):raise ValueError('Exact stopped cut SHA required')
    v=protocol(a.snapshot)
    with a.output.open('x',encoding='utf8')as f:f.write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'events':len(v['events']),'enabled_seconds':v['enabled_seconds'],'output':str(a.output)}))
if __name__=='__main__':main()
