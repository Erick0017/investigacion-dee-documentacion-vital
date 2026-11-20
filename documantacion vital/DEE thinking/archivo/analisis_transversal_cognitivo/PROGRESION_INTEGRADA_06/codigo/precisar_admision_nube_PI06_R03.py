"""Pre-Native admission clarification after Root checked the frozen Runtime."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    original=P/'codigo/PROTOCOLO_PI06_AMBIENTE_R03_R02.json'
    fixture=P/'codigo/FIXTURE_PI06_AMBIENTE_R03_R02.json'
    p=json.loads(original.read_text(encoding='utf8'));f=json.loads(fixture.read_text(encoding='utf8'))
    if f['birth_count']!=61 or len(f['preflight_selected_nonzero_RAW_sites'])!=3:raise ValueError('Exact fixed61-source fixture only')
    p['registered_admission_clarification_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    p['prior_protocol_preserved']={'file':original.name,'sha256':sha(original)}
    p['admission']='Submit all61fixedsources as individual legalNativeexperiences, including the3preflightoccupiedSEM4sites. The frozenRuntime rejects RAW!=0, includingstate0. No externallyomittedsource, resampling, overwrite, clearing or retry. Preserve eachactualreceipt. ResolvedRejectedOccupied is scientific evidence in thisambientmode only; pending, uncertain or otherunexpectedstatuses stop. Actual admitted/rejected denominators are reported, not forced to expectedcounts.'
    p['Native_admission_contract']={
        'source_review_reported_by_Root':'Frozen runtime.cpp lines377–407: raw_a_[idx]!=0 givesRejectedOccupied; onlyApplied writes and preserves the priorclock.',
        'all_fixed_requests_submitted_individually':61,
        'expected_applied_from_fixed_preflight':58,
        'expected_RejectedOccupied_from_fixed_preflight':3,
        'expected_rejection_sites':[x['site']for x in f['preflight_selected_nonzero_RAW_sites']],
        'counts_are_predictions_not_retrospective_selection':True,
        'resolved_occupied_rejections_allowed_only_for_mode':'eci01-pi06-ambiente',
        'allowed_terminal_receipt_states':['applied','rejected_occupied'],
        'unexpected_or_nonterminal_receipts_stop_without_retry':True,
        'report_fixture_density_and_real_admitted_density_separately':True,
        'no_cognitive_regulation_credit_for_Runtime_admission_guard':True}
    output=P/'codigo/PROTOCOLO_PI06_AMBIENTE_R03_R03.json';write(output,p)
    control={'schema':'DEE.PI06.cloud_native_admission.clarified.R03',
        'recorded_utc':p['registered_admission_clarification_utc'],
        'fixture_literal_unchanged':{'file':fixture.name,'sha256':sha(fixture)},
        'prior_protocol_literal_preserved':p['prior_protocol_preserved'],
        'current_protocol':{'file':output.name,'sha256':sha(output)},
        'Native_admission_contract':p['Native_admission_contract'],
        'external_preflight_omission_suggestion_not_adopted':True,
        'Root_review_resolved_safety_question_before_R03_Native':True,
        'Native_executed_by_this_tool':False,'new_Native_ticks':0}
    proof=P/'control/ADMISION_NUBE_GENERAL_PI06_R03.json';write(proof,control)
    print(json.dumps({'protocol':output.name,'protocol_sha256':sha(output),
                     'proof':proof.name,'proof_sha256':sha(proof),'fixture_sha256':sha(fixture),'Native_executed':False}))
if __name__=='__main__':main()
