"""Final pre-Native R03 functional-use addition; no further design iteration."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    prior_protocol=P/'codigo/PROTOCOLO_PI06_AMBIENTE_R03_R04.json';p=read(prior_protocol)
    old_C2C=P.parents[2]/'DEE Cognitive 2.0/sistema/capacidades/PROTOCOLO_PI05_C2C_30_R01.json'
    schedule=read(old_C2C)['schedule']
    if len(schedule)!=30 or schedule[28]!={'stage':'retention','context':2,'left':30,'right':7}:
        raise ValueError('Exact preserved environment30 offer28 required')
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    p['registered_final_C2C_followup_utc']=stamp
    p['prior_functional_protocol_preserved']={'file':prior_protocol.name,'sha256':sha(prior_protocol)}
    p['functional_followup'].append({'mode':'eci01-pi04-c2c-oportunidad','ordinal':28,
        'feedback':'real','actuator':'closed','max_Native_ticks':800,
        'preserved_public_offer':schedule[28],'one_remaining_offer_after_attempt':29,
        'environment_resources_or_counters_reset':False,'extra_supplement':False,
        'require_actual_Native_values_not_expected_answers':True,
        'actual_product_if_formed_bytes':64,'score_not_assumed':True})
    p['age_budget_max_per_arm']=1755
    p['C2C_followup_contract']={'protocol':str(old_C2C),'sha256':sha(old_C2C),
        'literal':{'modo':'eci01-pi04-c2c-oportunidad'},'preserved_source_ordinal':28,
        'expected_counter_after_one_attempt':29,'resources_total':30,
        'do_not_consume_final_offer29':True,
        'scientific_scope':'Test a previously available real numerical chain and effect on its device under the evolved condition. Host sequence, fixed codecs and transducers remain prepared; a correct product is not a new learned planner or regulator.',
        'actual_data_to_preserve':['firstNativechoice','actualarithmeticinteger','secondNativechoice',
            'realdeviceproductorabsence','actual64byteproducthash','allNativeinputsandfeedback','counterbeforeafter']}
    current_protocol=P/'codigo/PROTOCOLO_PI06_AMBIENTE_R03_R05.json';write(current_protocol,p)
    plans=[]
    for condition in('NUBE','CONTROL'):
        prior=P/'control'/('PLAN_AMBIENTE_'+condition+'_PI06_R04.json');plan=read(prior)
        oldsteps=plan['steps'][:]
        plan['source_proof']['prior_R04_plan_preserved']={'file':prior.name,'sha256':sha(prior)}
        plan['source_proof']['protocol']=str(current_protocol);plan['source_proof']['protocol_sha256']=sha(current_protocol)
        plan['registration_utc']=stamp;plan['max_native_ticks']=1755
        plan['steps'].append({'label':'C2C_ORD28','literal':{'modo':'eci01-pi04-c2c-oportunidad'},
            'max_native_ticks':800,'feedback':'real','actuator':'closed'})
        plan['description']+=' Finalfunctionaladdition beforeR03Native: consume only existing C2Coffer28 after allprevioussteps, feedbackreal/closedactuator, maximum800ticks; preserveoffer29. The actualNativeinteger, choices and real64byteproductorabsence are measured, no result assumed. The first4literalsteps remain exact. This closesdesign; no response-dependent followup or newlearning claim follows merely from an emittedchain.'
        if plan['steps'][:-1]!=oldsteps:raise RuntimeError('Do not change prior literalsteps')
        current=P/'control'/('PLAN_AMBIENTE_'+condition+'_PI06_R05.json');write(current,plan)
        plans.append({'file':current.name,'sha256':sha(current),'prior_R04_file':prior.name,
                      'prior_R04_sha256':sha(prior),'first4steps_exact_equal':True})
    proof={'schema':'DEE.PI06.R03.final_functional_plan.R05','registered_utc':stamp,
        'status':'SEALED_BEFORE_ANY_R03_NATIVE_FINAL_DESIGN',
        'protocol':{'file':current_protocol.name,'sha256':sha(current_protocol)},
        'fixture_literal_unchanged':p['fixture'],'plans':plans,
        'changes':'Exactlyone commonC2Coffer28 added after the preservedfoursteps of botharms.',
        'max_Native_ticks_per_arm':1755,'max_Native_ticks_pair':3510,
        'global_capture_budget_unchanged':{'pair_deltas':54,'pair_anchors':8},
        'previous_R03_R04_plans':'Preparedonly, notexecuted. Theirliteralbytes andhashes remain local.',
        'Root_remaining_budget_gate_still_required':True,'Native_executed_by_this_tool':False,'new_Native_ticks':0}
    output=P/'control/PLANES_AMBIENTE_FUNCION_FINAL_PI06_R05.json';write(output,proof)
    print(json.dumps({'protocol':current_protocol.name,'protocol_sha256':sha(current_protocol),
        'proof':output.name,'proof_sha256':sha(output),'plans':plans,'Native_executed':False}))
if __name__=='__main__':main()
