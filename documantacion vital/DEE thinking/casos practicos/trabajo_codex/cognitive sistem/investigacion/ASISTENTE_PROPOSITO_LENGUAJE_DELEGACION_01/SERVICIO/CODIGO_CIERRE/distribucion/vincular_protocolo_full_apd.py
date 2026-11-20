"""Bind an unchanged prospective FullZIP task list to the actual closed history.

Only offline history/identity metadata is populated. No actor input, task,
decoder, teaching sign, route or response is changed from the approved protocol.
"""
import argparse,copy,hashlib,json
from pathlib import Path

def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in('prospectivo','corte','funciones','calculo','salida'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();original=read(a.prospectivo);cut=read(a.corte);functions=read(a.funciones);calc=read(a.calculo)
    if original['status']!='MATERIAL_SEQUENCE_FIXED_SOURCE_CUT_PENDING'or original['service_protocol']['auditor_form_signs_from_closed_results']:raise ValueError('Unmodified prospectively approved task list required')
    if cut['issues']or calc['issues']or cut['persistent_service']['pending_or_uncertain']or not cut['persistent_service']['owner_stopped']:raise ValueError('A complete stopped real cut with no integrity discrepancy is required; functional negatives are not repaired')
    forms=('suma','diferencia','agrega','resta','total','quita');history={k:v for k,v in calc['baseline_history']['last_physically_decoded_signs'].items()if k in forms};lessons=[]
    for row in sorted(functions['explicit_teaching_for_history_including_prior_windows'],key=lambda x:x['after_tick']):
        admissions=row['admissions'];applied=admissions['requested_unique']>0 and admissions['by_status'].get('applied',0)==admissions['requested_unique']
        if applied and row['context']in forms and row['signal']in(-1,1):history[row['context']]=row['signal'];lessons.append(row)
    bound=copy.deepcopy(original);bound['service_protocol']['auditor_form_signs_from_closed_results']=history;bound['status']='READY_EXACT_CLOSED_CUT_AND_FIXED_MATERIAL_PROTOCOL';bound['source_cut']=cut['main'];bound['offline_history_witness']={'cut':{'file':str(a.corte),'sha256':sha(a.corte)},'functional_table':{'file':str(a.funciones),'sha256':sha(a.funciones)},'baseline_calculation':{'file':str(a.calculo),'sha256':sha(a.calculo)},'admitted_form_lessons':lessons,'expected_taught_history':history,'source_last_memory_observations':functions['last_memory_observations'],'last_observed_form_uses':{form:next((row for row in reversed(functions['APD_primitive_uses_including_composition_stages'])if row['form']==form),None)for form in forms},'scope':'Expected taught history: baseline actual P26 observations plus APPLIED explicit lessons. APPLIED alone does not demonstrate acquisition, successful access or retention; independently preserved postpanel emissions provide that separate evidence. The legacy auditor_form_signs_from_closed_results field is only this expected-history comparator, never an actor input.'};bound['approved_material_protocol_sha256']=sha(a.prospectivo)
    reduced=copy.deepcopy(bound);reduced['service_protocol']['auditor_form_signs_from_closed_results']={}
    if reduced['service_protocol']!=original['service_protocol']:raise ValueError('Physical protocol unexpectedly changed; no target-conditioned repair')
    with a.salida.open('x',encoding='utf8')as f:json.dump(bound,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'protocol':str(a.salida),'sha256':sha(a.salida),'prospective_physical_payloads_unchanged':True,'auditor_history':history,'new_ticks':0}))
if __name__=='__main__':main()
