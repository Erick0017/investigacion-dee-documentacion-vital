"""Pure archived-curve recalculation; exact integers, no Native imports."""
import argparse
import hashlib
import json
from pathlib import Path


def sign(result):
    return result['reader']['formed_native_command']


def _requests(value,found):
    if isinstance(value,list):
        for item in value:_requests(item,found)
    elif isinstance(value,dict):
        if 'receipt'in value and 'id'in value and 'channel'in value:
            key=(int(value['id']),value['channel'])
            previous=found.get(key)
            if previous is not None and previous!=value:
                raise ValueError('A Native request identity has contradictory archived receipts')
            found[key]=value
        for key,item in value.items():
            if key!='receipt':_requests(item,found)


def recalculate(row):
    target=row['B_sign_auditor_only']
    if type(target)is not int or target not in(-1,1):raise ValueError('Exact signed auditor target required')
    consecutive=0;criterion=None;learning=[]
    for lesson in row['B_learning_curve']:
        number=lesson['B_lesson_number'];correct_count=0
        for use_number,use in enumerate(lesson['uses'],1):
            emitted=sign(use['result']);correct=emitted==target
            if use['audit_correct_after_emission']!=correct:
                raise ValueError('Stored curve correctness does not match the primary emitted sign')
            consecutive=consecutive+1 if correct else 0;correct_count+=int(correct)
            if consecutive>=2 and criterion is None:
                criterion={'B_lessons':number,'B_postlesson_queries':(number-1)*2+use_number,
                    'tick':use['result']['end_tick']}
        learning.append({'B_lessons':number,'queries':len(lesson['uses']),
            'correct_emissions':correct_count,
            'emissions':[sign(use['result']) for use in lesson['uses']]})
    if row['first_criterion']!=criterion:
        raise ValueError('Stored criterion does not follow2consecutive primary emissions')
    before={r['form']:sign(r['result']) for r in row['old_panel_before']['rows']}
    after={r['form']:sign(r['result']) for r in row['old_panel_after']['rows']}
    if set(before)!=set(after):raise ValueError('Retention panels have different codecs')
    requests={};_requests(row,requests)
    statuses={}
    for request in requests.values():
        status=request['receipt']['status'];statuses[status]=statuses.get(status,0)+1
    initial_transfer=sign(row['B_before_teaching'])==target
    if initial_transfer!=row['B_initial_transfer_audit']:
        raise ValueError('Initial transfer verdict differs from the emitted primary sign')
    functional=row['B_functional_use']
    return {'schema':'DEE.APD03.lexical_curve_recalculation.R01','life_identity':row['life_identity'],
        'history':row['history'],'B_sign_auditor_only':target,'start_tick':row['start_tick'],'end_tick':row['end_tick'],
        'initial_B_emission_before_B_teaching':sign(row['B_before_teaching']),
        'initial_transfer_not_meta_learning':initial_transfer,'learning_curve':learning,
        'first_criterion':criterion,'A_before_B':[sign(r) for r in row['A_uses']],
        'A_after_B':sign(row['A_after_B_course']),
        'old_panel_before':before,'old_panel_after':after,
        'old_valid_before':sum(s in(-1,1) for s in before.values()),
        'old_valid_after':sum(s in(-1,1) for s in after.values()),
        'old_same_valid_sign':sum(before[k]in(-1,1)and after[k]==before[k] for k in before),
        'old_changed_or_no_response':[{'form':k,'before':before[k],'after':after[k]}for k in before
            if before[k]not in(-1,1)or after[k]!=before[k]],
        'functional_native_choice':functional['native_function_choice'],
        'functional_choice_matches_taught_sign':functional['native_function_choice']==target,
        'native_requests_unique':len(requests),'receipt_status_counts':statuses,
        'actual_physical_function_outcome_must_be_read_in_primary':True,
        'new_native_ticks':0,
        'limits':'Query-level observations are not independent learners. A valid sign selecting a prepared interaction is not proof of its downstream correctness or general meta-learning.'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--primary',required=True)
    parser.add_argument('--output');args=parser.parse_args()
    data=Path(args.primary).read_bytes();result=recalculate(json.loads(data))
    result['primary_sha256']=hashlib.sha256(data).hexdigest()
    encoded=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    if args.output:
        with Path(args.output).open('xb')as stream:stream.write(encoded)
    print(encoded.decode('utf8'),end='')


if __name__=='__main__':main()
