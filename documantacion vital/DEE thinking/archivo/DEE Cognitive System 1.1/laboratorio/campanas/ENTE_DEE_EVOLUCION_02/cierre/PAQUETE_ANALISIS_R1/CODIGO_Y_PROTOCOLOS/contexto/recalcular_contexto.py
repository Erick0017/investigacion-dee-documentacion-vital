"""Portable, standard-library recalculation of the finite EO02 context pilots.
No DEE import, ticks, targets for an agent or native state mutation.
"""
from pathlib import Path
import argparse,gzip,hashlib,json

def load(p):
    with gzip.open(p,'rt',encoding='utf8')as f:return json.load(f)
def values(w,k):return [q['s_reg']for q in w[k]]
def code(q):
    return q['direction'][0]if q['state']>0 and q['semantic']==1 and q['direction'][1:]==[-1,-1]else None
def main():
    p=argparse.ArgumentParser();p.add_argument('--primarios',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);args=p.parse_args()
    cases=[];discrepancies=[]
    for f in sorted(args.primarios.glob('AUX_EO02_CTX_*.json.gz')):
        raw=load(f);r=raw['result']['result'];b=r['before'];end=r['after'];requests=r['requests'];statuses={}
        for q in requests:
            s=q['receipt']['status'];statuses[s]=statuses.get(s,0)+1
        kind='R01_context_incoming'if 'R01_'in f.name else'R02_B_direct'if 'R02_'in f.name else'R03_B_peripheral'
        row={'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'code_sha256':raw['source_sha256'],
            'kind':kind,'life':raw['result']['INSTRUMENTO']['life_id'],'parent_life':raw['parent']['parent']['life_id'],
            'parent_tick':raw['parent']['parent']['tick'],'end_tick':end['tick'],'context_before':values(b,'context_A'),
            'context_after':values(end,'context_A'),'own_before':values(b,'own'),'own_after':values(end,'own'),
            'private_B_before':values(b,'private_B'),'private_B_after':values(end,'private_B'),
            'new_requests':len(requests),'new_request_statuses':statuses}
        if kind=='R01_context_incoming':
            row.update(arm=r['arm'],A_command=r['common']['formed_native_command'],after_teaching_context=values(r['after_teaching'],'context_A'))
            row['context_load_changed']=row['context_before']!=row['after_teaching_context']
            row['transient_context_direction_changes']=[{'tick':f['witness']['tick'],'directions':[q['direction']for q in f['witness']['context_A']]}for f in r['frames']if [q['direction']for q in f['witness']['context_A']]!=[q['direction']for q in b['context_A']]]
        else:
            B_events=[{'tick':f['tick'],'native_class':code(f['witness']['B']),'B':f['witness']['B'],'data':f['data']}for f in r['frames']if code(f['witness']['B'])is not None]
            row.update(pair=r['pair'],A_command=r['common_A']['formed_native_command'],B_events=B_events,
                B_classes=sorted(set(x['native_class']for x in B_events)))
            bus_events=[]
            for frame in r['frames']:
                for name,dx in [('minus',-1),('plus',1)]:
                    q=frame['buses'][name]
                    if q['state']>0 and q['semantic']==1 and q['s_reg']==5 and q['direction']==[dx,0,0]:
                        bus_events.append({'tick':frame['tick'],'name':name,'command':dx})
            row['postformed_bus_events']=bus_events
            row['B_reference_changed']=row['private_B_before']!=row['private_B_after']
        cases.append(row)
    byname={x['file']:x for x in cases}
    r1=[x for x in cases if x['kind']=='R01_context_incoming']
    r3=[x for x in cases if x['kind']=='R03_B_peripheral']
    low=next((x for x in r3 if x['pair']==[0,50]),None);high=next((x for x in r3 if x['pair']==[64,50]),None)
    claims={'R01_different_context_loads_acquired':any(x['context_load_changed']for x in r1),
        'R01_common_later_actions':sorted(set(x['A_command']for x in r1 if x['A_command']is not None)),
        'R03_B_sensitive_to_left_at_fixed_right50':None if low is None or high is None else low['B_classes']!=high['B_classes'],
        'R03_A_sensitive_to_left_at_fixed_right50':None if low is None or high is None else low['A_command']!=high['A_command'],
        'two_contexts_acquired_and_retained_in_MAIN_demonstrated':False,
        'native_ticks_added_to_MAIN_or_EO01':0,'P2_or_autonomous_selector_demonstrated':False,
        'statistical_unit':'Seven deterministic diagnostic branches of one exact inherited prefix; not independent organisms or learned histories.'}
    if len(cases)!=7:discrepancies.append({'expected_cases':7,'actual':len(cases)})
    if len(r1)!=3:discrepancies.append({'expected_R01':3,'actual':len(r1)})
    out={'schema':'EO02.context.recalc.v1','cases':cases,'claims':claims,'discrepancies':discrepancies,
        'reproduction':'Archived arithmetic/field inspection only, no DEE engine or physical replay.'}
    args.salida.parent.mkdir(parents=True,exist_ok=True)
    args.salida.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'cases':len(cases),'claims':claims,'discrepancies':discrepancies,'output':str(args.salida)},ensure_ascii=False))
    return bool(discrepancies)
if __name__=='__main__':raise SystemExit(main())
