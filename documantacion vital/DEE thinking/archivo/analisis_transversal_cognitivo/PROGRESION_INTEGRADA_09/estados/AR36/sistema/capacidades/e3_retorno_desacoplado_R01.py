"""Pure E3 controlled-signal planner. No Native, state opening or action policy.

The root alone may connect the frozen output bit to its declared experimental
return transducer. This file never imports DEE or chooses an actuator/bank.
"""
from collections import Counter,defaultdict
import argparse,hashlib,json,base64,zlib

VERSION='PI04.E3.stratified_fixed_rotation.R01'
CALENDAR_KEYS=('query_tick','query_read_tick','outcome_injection_tick','contact_tick','delay_laps','reference_contact_phase')
def require(ok,message):
    if not ok:raise ValueError(message)
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
def digest(value):return hashlib.sha256(canonical(value)).hexdigest()
def checked_calendar(value):
    require(type(value)is dict and set(value)==set(CALENDAR_KEYS),'Exact frozen E3 calendar fields required')
    require(all(type(value[k])is int for k in CALENDAR_KEYS),'Integer calendar boundaries required')
    require(1<=value['delay_laps']<=4,'Prepared delay domain1..4 laps only')
    require(value['reference_contact_phase']==391,'Original prepared391mod782 contact required')
    require(value['query_read_tick']==value['query_tick']+6,'Original q+6 reader required')
    require(value['outcome_injection_tick']==value['contact_tick']-2,'Original generic-return boundary required')
    require(value['contact_tick']-value['query_read_tick']==67*value['delay_laps']+2,'Original one-tick efference/Native contact timing required')
    return dict(value)
def build_permuted_plan(source_records,*,source_identity,frozen_rule='rotate_plus_one_within_delay_phase'):
    require(frozen_rule=='rotate_plus_one_within_delay_phase','No fitted or post-hoc permutation rule')
    require(type(source_identity)is dict and source_identity,'Exact source identity/provenance required')
    require(type(source_records)is list and 2<=len(source_records)<=32,'Finite2..32 source episodes required')
    records=[];groups=defaultdict(list)
    for i,record in enumerate(source_records):
        require(type(record)is dict and set(record)=={'ordinal','calendar','failed'},'No actions, targets or chosen-bank fields in signal source')
        require(record['ordinal']==i and type(record['ordinal'])is int,'Consecutive source opportunity order required')
        require(type(record['failed'])is bool,'Actual generic consequence bool required')
        cal=checked_calendar(record['calendar']);records.append({'ordinal':i,'calendar':cal,'failed':record['failed']})
        groups[(cal['delay_laps'],cal['reference_contact_phase'])].append(i)
    mapping=list(range(len(records)))
    for indices in groups.values():
        for position,index in enumerate(indices):mapping[index]=indices[(position+1)%len(indices)]
    slots=[]
    for i,record in enumerate(records):
        j=mapping[i];slots.append({'ordinal':i,'calendar':record['calendar'],'source_ordinal':j,'returned_failed':records[j]['failed']})
    strata=[]
    for key,indices in sorted(groups.items()):
        original=Counter(records[i]['failed']for i in indices);permuted=Counter(slots[i]['returned_failed']for i in indices)
        require(original==permuted,'Return-type dose changed')
        strata.append({'delay_laps':key[0],'reference_contact_phase':key[1],'slots':indices,
                       'failure':original[True],'nonfailure':original[False],
                       'changed_signal_slots':sum(records[i]['failed']!=slots[i]['returned_failed']for i in indices)})
    body={'schema':'DEE.PI04.E3.frozen_signal_plan.v1','version':VERSION,'frozen_rule':frozen_rule,
          'source_identity':source_identity,'source_records':records,'source_records_sha256':digest(records),'slots':slots,'strata':strata,
          'source_signal_changes':sum(records[i]['failed']!=slots[i]['returned_failed']for i in range(len(records))),
          'attribution':'Experimental control schedule only. Not cognitive memory, a learned policy or Native agency.'}
    return {'plan':body,'sha256':digest(body)}
def validate_plan(envelope):
    require(type(envelope)is dict and set(envelope)=={'plan','sha256'},'Frozen plan envelope required')
    body=envelope['plan'];require(digest(body)==envelope['sha256'],'Frozen E3 plan hash mismatch')
    require(body['schema']=='DEE.PI04.E3.frozen_signal_plan.v1'and body['version']==VERSION,'Exact E3 version required')
    require(body['frozen_rule']=='rotate_plus_one_within_delay_phase','Frozen rotation differs')
    # Verify the permutation and counts rather than trusting an edited table.
    expected=build_permuted_plan(body['source_records'],source_identity=body['source_identity'],frozen_rule=body['frozen_rule'])
    require(expected==envelope,'Plan is not the exact fixed rotation of its preserved source signals')
    return body
def pack_plan(envelope):
    """Bounded UTF8 JSON -> zlib -> URL-base64 transport, never code/path."""
    validate_plan(envelope);raw=canonical(envelope)
    require(len(raw)<=32768,'Expanded E3 plan exceeds32KB')
    packed='E3Z1:'+base64.urlsafe_b64encode(zlib.compress(raw,9)).decode('ascii')
    require(len(packed)<=6144,'Encoded plan exceeds bounded transport budget')
    return packed
def unpack_plan(packed):
    require(type(packed)is str and packed.startswith('E3Z1:')and len(packed)<=6144,'Only bounded E3Z1 encoded plan, never a path')
    try:data=base64.b64decode(packed[5:].encode('ascii'),altchars=b'-_',validate=True)
    except(ValueError,UnicodeError)as exc:raise ValueError('Invalid E3Z1 base64')from exc
    decoder=zlib.decompressobj()
    try:raw=decoder.decompress(data,32769)
    except zlib.error as exc:raise ValueError('Invalid E3Z1 compressed JSON')from exc
    require(len(raw)<=32768 and decoder.eof and not decoder.unconsumed_tail and not decoder.unused_data,'Incomplete/trailing/oversized E3Z1 plan')
    try:envelope=json.loads(raw.decode('utf-8'))
    except(UnicodeError,ValueError)as exc:raise ValueError('E3Z1 must be UTF8 JSON')from exc
    validate_plan(envelope)
    require(pack_plan(envelope)==packed,'Noncanonical E3Z1 encoding')
    return envelope
def replay_signal(envelope,ordinal,calendar):
    """No live effect, motor, history lookup, target or bank is accepted here."""
    body=validate_plan(envelope)
    require(type(ordinal)is int and 0<=ordinal<len(body['slots']),'One predeclared signal per included ordinal')
    slot=body['slots'][ordinal]
    require(slot['ordinal']==ordinal and slot['calendar']==checked_calendar(calendar),'Calendar diverged: preserve, do not reposition/readjust')
    require(type(slot['returned_failed'])is bool,'Stored generic signal must be bool')
    return slot['returned_failed']
def summarize_manipulation(envelope,actual_control_failures):
    """Evaluation after execution only; must never feed the participant."""
    body=validate_plan(envelope);slots=body['slots']
    require(type(actual_control_failures)is list and len(actual_control_failures)==len(slots),'Complete evaluated history required')
    require(all(type(x)is bool for x in actual_control_failures),'Real control effects must remain bool, not NULL/zero coercions')
    mismatches=sum(x!=s['returned_failed']for x,s in zip(actual_control_failures,slots))
    return {'included':len(slots),'source_signal_changes':body['source_signal_changes'],'actual_effect_return_mismatches':mismatches,
            'false_failure_signals':sum(not x and s['returned_failed']for x,s in zip(actual_control_failures,slots)),
            'real_failures_without_failure_signal':sum(x and not s['returned_failed']for x,s in zip(actual_control_failures,slots)),
            'manipulation_effective':body['source_signal_changes']>0 and mismatches>0,
            'scope':'Finite observed decoupling; no claim of statistical independence or learned agency.'}
def self_test():
    bits=[True,False,False,True,False,False,True,False];records=[]
    for i,failed in enumerate(bits):
        laps=1 if i%2==0 else 2;read=1000+782*i;contact=read+67*laps+2
        records.append({'ordinal':i,'failed':failed,'calendar':{'query_tick':read-6,'query_read_tick':read,'outcome_injection_tick':contact-2,'contact_tick':contact,'delay_laps':laps,'reference_contact_phase':391}})
    plan=build_permuted_plan(records,source_identity={'kind':'SYNTHETIC_PURE_TEST_NOT_NATIVE'})
    returned=[replay_signal(plan,i,r['calendar'])for i,r in enumerate(records)]
    assert Counter(returned)==Counter(bits)and returned!=bits
    report=summarize_manipulation(plan,bits);assert report['manipulation_effective']
    rejected=[]
    for label,fn in [('extra_action',lambda:build_permuted_plan([dict(records[0],action=1),*records[1:]],source_identity={'mock':True})),
                     ('calendar_shift',lambda:replay_signal(plan,0,dict(records[0]['calendar'],query_tick=995))),
                     ('wrong_hash',lambda:replay_signal(dict(plan,sha256='0'*64),0,records[0]['calendar'])),
                     ('bool_coercion',lambda:summarize_manipulation(plan,[1]*8))]:
        try:fn()
        except ValueError:rejected.append(label)
        else:raise AssertionError(label)
    return {'version':VERSION,'mode':'PURE_SYNTHETIC_TEST_NO_NATIVE','new_native_ticks':0,'returned_bits':returned,'manipulation':report,'refusals':rejected}
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--self-test',action='store_true',required=True);parser.parse_args()
    print(json.dumps(self_test(),ensure_ascii=False,indent=2))
