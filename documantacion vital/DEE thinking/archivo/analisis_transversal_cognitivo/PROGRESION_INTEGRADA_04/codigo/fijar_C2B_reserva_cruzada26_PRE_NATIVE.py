"""Root-approved DRAFT-only fixture amendment; no Native, CS or state writes."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parents[1]

if __name__=="__main__":
    file=P/'codigo/PROTOCOLO_PI04_C2B_R01.json';old=file.read_bytes();p=json.loads(old)
    if p['status']!='DRAFT'or len(p['schedule'])!=24:raise ValueError('Exact unexecuted24-offer B draft required')
    before=P/'codigo/revisiones/C2B_DRAFT24_ANTES_RESERVA_CRUZADA26'
    if before.exists():raise ValueError('Preserve prior draft revision')
    before.mkdir(parents=True);(before/file.name).write_bytes(old)
    first22=json.dumps(p['schedule'][:22],sort_keys=True,separators=(',',':'))
    p['schedule'][22]={'stage':'retention','context':2,'left':29,'right':4}
    p['schedule'][23]={'stage':'retention','context':6,'left':6,'right':5}
    p['schedule'] += [{'stage':'retention','context':3,'left':26,'right':4},
                      {'stage':'retention','context':7,'left':7,'right':6}]
    if json.dumps(p['schedule'][:22],sort_keys=True,separators=(',',':'))!=first22:raise AssertionError('First22 changed')
    p['attribution']='UNEXECUTED C2B draft: same continuous physical descendant after old C2 firstNULL, symmetric two identical scalar inputs/query0/unchanged q6six-reader.26explicit resources:12development/8reserved/2retention/4crossed opportunities. Before any B Native, crossed fixtures22/23 and future24/25 fix different second routes for the SAME arithmetic operation. Old C2/PI03 devices and counters remain preserved, not reset. Proposed MAIN22 after reopening,23on diagnostic clone,24/25remain explicit future stock; actual execution/adoption not claimed.'
    file.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    proof={'schema':'PI04.C2B.crossed26.DRAFT_amendment.PRE_NATIVE.R01','local_cut':datetime.datetime.now().astimezone().isoformat(),
        'literal_previous_draft':str(before/file.name),'before_sha256':hashlib.sha256(old).hexdigest(),
        'protocol':str(file),'after_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
        'first22_schedule_unchanged':True,'total_explicit_opportunities':26,'amended':p['schedule'][22:],
        'Native_executed_by_this_tool':0,'CS_modified':False,'model_or_decoder_changed':False,
        'status':'DRAFT_ROOT_MUST_COPY_AND_SEAL','targets_remain_evaluator_only':True}
    target=P/'control/C2B_DRAFT26_RESERVA_CRUZADA_PRE_NATIVE.json'
    if target.exists():raise ValueError('Preserve prior fixture amendment proof')
    target.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(proof,ensure_ascii=False,indent=2))
