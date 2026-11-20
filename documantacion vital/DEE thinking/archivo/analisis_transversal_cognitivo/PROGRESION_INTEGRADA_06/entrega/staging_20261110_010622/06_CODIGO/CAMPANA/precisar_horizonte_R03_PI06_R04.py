"""Final prospective R03 horizon policy; original geometry and steps unchanged."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    old=P/'codigo/PROTOCOLO_PI06_AMBIENTE_R03_R03.json';p=read(old)
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    p['registered_final_horizon_policy_utc']=stamp
    p['prior_horizon_protocol_preserved']={'file':old.name,'sha256':sha(old)}
    p['interfaces_in_both_arms']='Both nube and control declare the same61fixed InterfaceSpec/ChannelSpec sources. Only nube submits61births; control submits0. No existing source or RAW is replaced.'
    p['admission']='All61cloudrequests are individuallegalNativeexperiences; actualApplied/RejectedOccupied receipts are retained. Expected58/3 is a prediction from the frozenpreflight, not forcedcounts. In the two fixedR03plans only, resolvedRejectedOccupied in cloudinputs OR originalFI176inputs is reported and does not select a repair or abort the common271tickhorizon. Pending, unknown, anyotherunexpectedrejection, uncertaintransport or HostSafetyStop preserves and stops. R01/R02scientific bodies and allother runners keep their previousstrictadmissionrule.'
    p['Native_admission_contract'].update({
        'same61interfaces_declared_in_both_arms':True,
        'resolved_occupied_rejections_allowed_only_in':'The two fixed pairedR03plans: environmental61inputs and their commonFI176inputs.',
        'common_FI_requested_inputs':176,
        'report_FI_applied_and_RejectedOccupied_counts_separately':True,
        'any_FI_input_rejected_blocks_historical_176_input_retention_certification':True,
        'any_material_regression_blocks_promotion_until_resolved':True})
    p['Native_admission_contract'].pop('resolved_occupied_rejections_allowed_only_for_mode',None)
    p['common_FI_interpretation']='An observedvaliddirection, NULL or incorrectanswer is recorded. If not all176FIinputs were applied, the result is a functionattempt under degradedadmission, never a verifiedretention test of the intact historicalcontract.'
    output=P/'codigo/PROTOCOLO_PI06_AMBIENTE_R03_R04.json';write(output,p)
    plans=[]
    for condition in('NUBE','CONTROL'):
        prior=P/'control'/('PLAN_AMBIENTE_'+condition+'_PI06_R03.json');plan=read(prior)
        plan['source_proof']['prior_plan_preserved']={'file':prior.name,'sha256':sha(prior)}
        plan['source_proof']['protocol']=str(output);plan['source_proof']['protocol_sha256']=sha(output)
        plan['registration_utc']=stamp
        plan['description']+=' Finalpre-Nativepolicy: botharmsdeclare61identicalinterfaces. ResolvedRejectedOccupied inenvironmentalorFIinputs is retained and commonfixedstepscontinue; otherunexpected/nonterminalreceipt, transportuncertainty orhostSafetyStop stopswithoutrepair. An incompletelyadmittedFI attempt doesnot certify historical176-inputretention. This overrides only the earlier genericadmissionstop prose in these2R03plans; literals and order are unchanged.'
        current=P/'control'/('PLAN_AMBIENTE_'+condition+'_PI06_R04.json');write(current,plan)
        if plan['steps']!=read(prior)['steps']:raise RuntimeError('Scientific literalsteps must remain exact')
        plans.append({'file':current.name,'sha256':sha(current),'prior_file':prior.name,'prior_sha256':sha(prior),'literal_steps_exact_equal':True})
    witness={'schema':'DEE.PI06.R03.final_pre_Native_horizon_policy.R04','registered_utc':stamp,
        'protocol':{'file':output.name,'sha256':sha(output)},'prior_protocol':{'file':old.name,'sha256':sha(old)},
        'fixture_unchanged':p['fixture'],'plans':plans,
        'scope':'Matched-interface generalenvironment experiment, including failureandlateravailability. No per-failureguard, decoderchange, contentreplacement or automaticrepair.',
        'only_resolved_occupied_terminal_rejections_allowed':True,
        'not_universal_relaxation_of_input_integrity':True,'historical_retention_contract_protected':True,
        'no_R03_Native_executed_yet':True,'Native_executed_by_this_tool':False,'new_Native_ticks':0}
    proof=P/'control/POLITICA_HORIZONTE_AMBIENTE_PI06_R04.json';write(proof,witness)
    print(json.dumps({'protocol':output.name,'protocol_sha256':sha(output),'proof':proof.name,'proof_sha256':sha(proof),'plans':plans,'Native_executed':False}))
if __name__=='__main__':main()
