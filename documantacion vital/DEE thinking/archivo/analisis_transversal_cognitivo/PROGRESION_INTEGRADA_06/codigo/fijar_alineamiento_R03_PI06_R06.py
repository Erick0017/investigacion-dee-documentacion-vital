"""Final pre-Native R03 calendar fix: expose a normal and aligned threat window."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    old_protocol=P/'codigo/PROTOCOLO_PI06_AMBIENTE_R03_R05.json';p=read(old_protocol)
    changed=False
    for row in p['functional_followup']:
        if row.get('mode')=='unforced_evolution':
            if row['ticks']!=271:raise ValueError('Exact previous271tick design required')
            row['ticks']=274;changed=True
    if not changed:raise ValueError('No previous horizon')
    p['registered_final_calendar_utc']=stamp
    p['prior_calendar_protocol_preserved']={'file':old_protocol.name,'sha256':sha(old_protocol)}
    p['age_budget_max_per_arm']=1758;p['expected_age_if_original_FI198']=938
    p['admission']=p['admission'].replace('common271tickhorizon','common274tickhorizon')
    p['prospective_calendar_reason']={
        'formed_adverse_query':826307,'initial_characterization_ticks':268,
        'predicted_first_query':826773,'predicted_first_query_minus_adverse':466,
        'old_second_wait':271,'old_predicted_second_query':827242,'old_second_query_minus_adverse':935,
        'new_second_wait':274,'new_predicted_second_query':827245,'new_second_query_minus_adverse':938,
        'N':67,'new_second_query_minus_adverse_in_N':14,
        'actual_native_calendar_may_normalize_and_must_be_reported':True,
        'reason':'The earlier calendar placed bothquestions3ticks away from the established adversephase. Add3unforcedticks only beforeFI2 to offer one informationallyuseful threat-alignedchallenge, before anyR03Native result. No seed, site, inputload, reader, expectedanswer or materialintervention is adjusted.'}
    current_protocol=P/'codigo/PROTOCOLO_PI06_AMBIENTE_R03_R06.json';write(current_protocol,p)
    plans=[]
    for condition in('NUBE','CONTROL'):
        prior=P/'control'/('PLAN_AMBIENTE_'+condition+'_PI06_R05.json');plan=read(prior)
        steps=plan['steps'];original=read(prior)['steps']
        if steps[2]['literal']!={'modo':'eci01-pi06-ambiente-evolucion','ticks':271,'captura':'global'}:
            raise ValueError('Only the precise prospective free-wait change')
        steps[2]['label']='EVOLUCION_SEGURA274'
        steps[2]['literal']['ticks']=274;steps[2]['max_native_ticks']=274;steps[2]['expected_new_ticks']=274
        if steps[:2]!=original[:2]or steps[3:]!=original[3:]:raise RuntimeError('Other scientificsteps must remain exact')
        plan['max_native_ticks']=1758;plan['registration_utc']=stamp
        plan['source_proof']['prior_R05_plan_preserved']={'file':prior.name,'sha256':sha(prior)}
        plan['source_proof']['protocol']=str(current_protocol);plan['source_proof']['protocol_sha256']=sha(current_protocol)
        plan['description']=plan['description'].replace('evolve271','evolve274').replace('q2−q1=469=7N','q2−q1=472')
        plan['description']+=' Finalcalendarcorrection beforeanyR03Native: secondfreewait274, not271. PredictedFI1q826773is3ticks off the knownadversephase; FI2q827245is938=14Nticks afteradverseq826307. These are prospective timingpredictions, not suppliedanswers. Record actual originalnormalizer timing. The R05plans were prepared but neverexecuted. No furtherdesignchanges follow observedR03results.'
        current=P/'control'/('PLAN_AMBIENTE_'+condition+'_PI06_R06.json');write(current,plan)
        plans.append({'file':current.name,'sha256':sha(current),'prior_R05_file':prior.name,
            'prior_R05_sha256':sha(prior),'only_literal_change':'ambient-evolution ticks271→274; same cloud, FI questions and finalC2Cord28'})
    output=P/'control/ALINEAMIENTO_FINAL_AMBIENTE_PI06_R06.json'
    proof={'schema':'DEE.PI06.R03.final_pre_Native_calendar.R06','registered_utc':stamp,
        'status':'SEALED_BEFORE_ANY_R03_NATIVE_FINAL','protocol':{'file':current_protocol.name,'sha256':sha(current_protocol)},
        'fixture_literal_unchanged':p['fixture'],'plans':plans,'reason':p['prospective_calendar_reason'],
        'prior_R05_status':'PREPARADO_NO_EJECUTADO: both functionalquestions missed the knownadversephase.',
        'maximum_Native_ticks_per_arm':1758,'maximum_Native_ticks_pair':3516,
        'global_capture_budget_unchanged':{'pair_deltas':54,'pair_anchors':8},
        'no_data_from_R03_material_execution_used_for_revision':True,
        'Native_executed_by_this_tool':False,'new_Native_ticks':0}
    write(output,proof)
    print(json.dumps({'protocol':current_protocol.name,'protocol_sha256':sha(current_protocol),
        'proof':output.name,'proof_sha256':sha(output),'plans':plans,'Native_executed':False}))
if __name__=='__main__':main()
