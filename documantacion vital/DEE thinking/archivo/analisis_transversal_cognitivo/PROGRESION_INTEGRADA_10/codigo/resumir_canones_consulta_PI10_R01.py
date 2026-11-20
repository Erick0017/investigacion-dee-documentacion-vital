"""Auditor-only metrics over explicit normalized records; stdlib, no DEE.

This is a prepared summarizer, not a Native result and not a replacement for
an independently checked projection of primary RAW/receipts. No actor may
import this module to choose an action, route, return, target or bank.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re

REGIMES=('need','bypass','need_return')
RESERVED=(2,3,4,5,8,9,10,11,14,15,16,17)
MOTOR=lambda c:(-1 if c==0 else c)if type(c)is int and c in(-1,0,1)else None

def need(ok,why):
    if not ok:raise ValueError(why)

def raw_decode(raw):
    need(type(raw)is int and 0<=raw<2**64,'Exact uint64 RAW, not float/bool')
    ds=[(raw>>s)&15 for s in(48,52,56)]
    return {'raw':raw,'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,
            'semantic':raw>>60,'direction':[n-16 if n&8 else n for n in ds]}

def extra_bit(raw):
    r=raw_decode(raw)
    if raw==0:return 0
    if r['state']>0 and r['semantic']==1:
        if r['direction']==[0,0,1]:return 1
        if r['direction']==[1,0,0]:return 0
    return None

def check_row(row):
    need(type(row['ordinal'])is int and 0<=row['ordinal']<24,'Finite new lot only')
    need(row['regime']in REGIMES,'Known evaluator-only environment regime')
    if row['ordinal']<18:need(row['regime']==REGIMES[row['ordinal']//6],'Prospectively fixed regime per ordinal')
    raw=row['preview_RAW'];bit=extra_bit(raw);state=raw_decode(raw)['state']
    q1=row['q1'];q2=row['q2'];gate=row['resource_gate']
    native1=MOTOR(q1['Native_choice']);native2=MOTOR(q2['Native_choice'])
    need(q1['actual_motor']is None or(type(q1['actual_motor'])is int and q1['actual_motor']in(-1,1)),'Exact actual q1 binary motor/NULL')
    need(q2['actual_motor']is None or(type(q2['actual_motor'])is int and q2['actual_motor']in(-1,1)),'Exact actual q2 binary motor/NULL')
    need(type(q1['question_signature'])is bool and type(q1['released'])is bool,'Exact access booleans')
    need(type(row['returned_failed'])is bool,'Exact generic-return class')
    need(type(q1['query_tick'])is int and type(q2['query_tick'])is int,'Actual integer physical times')
    need(q2['actual_motor']==native2,'No hidden replacement of q2 Native command')
    if row['arm']in('real','nonfailure','yoked'):
        need(q1['actual_motor']==native1,'Candidate/control q1 stays Native')
    need(type(q1['question_requested'])is bool and q1['question_requested']==(q1['actual_motor']==1),'Fixed query actuator codec')
    release=bool(q1['question_requested']and q1['question_receipt_status']=='applied'and q1['question_signature'])
    need(q1['released']==release,'Access requires actual admission and physical signature')
    need(not release or bit is not None,'NULL preview cannot be filled with expected bit')
    datum=2*bit if release else 0
    need(q1['second_datum']==datum,'Only fixed0/2 real RAW codec or declaredNoQuery0')
    valid2=native2 is not None and q2['motor_copy_receipt_status']=='applied'
    route=(1 if native2==1 else 0)if valid2 else None
    need(q2['actual_route']==route,'NULL/rejected motor is not a default intelligent route')
    domain=bit is not None and 0<=state<=3
    available=(bit if row['regime']!='bypass'else 0)if domain else None
    need(gate['available_bin']==available,'Fixed environmental availability law, not post-hoc choice')
    need(gate['placement_tick']<=q1['query_tick'],'Environment placement must precede the choice')
    need(type(gate['FI_required'])is bool,'Explicit FI requirement flag')
    fiok=(not gate['FI_required'])or(type(gate['actual_Native_FI_choice'])is int and gate['actual_Native_FI_choice']==1)
    valid1=native1 is not None if row['arm']in('real','nonfailure','yoked')else q1['actual_motor']in(-1,1)
    would_transfer=bool(domain and valid2 and route==available and fiok)
    attributed_useful=bool(would_transfer and valid1)
    # A local I/O error is not a cognitive miss. It must be preserved separately
    # and cannot be silently scored as either success or an abstention.
    need(not gate.get('process_error'),'Preserve process failure separately before functional scoring')
    need(gate['transferred']is would_transfer,'Actual resource transfer disagrees with fixed law')
    if gate['transferred']:
        product=gate['product']
        need(product['bytes']==64 and re.fullmatch('[0-9a-f]{64}',product['sha256'])is not None,'Actual product locator/hash/size required')
    else:need(gate.get('product')is None,'No invented product for failed transfer')
    need(row['actual_failed']is(not attributed_useful),'Whole-task failure includes valid q1, without erasing a physical resource delivered after a NULL')
    req=row['Native_inputs'];ids={}
    for r in req:
        key=r['id'];need(type(key)is int,'Native receipt identity, not an alias')
        if key in ids:need(ids[key]==r['status'],'Conflicting receipt alias')
        ids[key]=r['status']
    terminal={'applied','rejected_conflict','rejected_invalid','rejected_past','rejected_closed','rejected_quota'}
    need(all(v in terminal for v in ids.values()),'Pending/uncertain transport is not completed cognition')
    return {'ordinal':row['ordinal'],'arm':row['arm'],'life_id':row['life_id'],'regime':row['regime'],
      'reserved':row['ordinal']in RESERVED,'useful':attributed_useful,'physical_delivered':would_transfer,'domain_admitted':domain,
      'Native_q1_valid':native1 is not None,'Native_q1_zero':q1['Native_choice']==0 and type(q1['Native_choice'])is int,
      'query_requested':q1['question_requested'],'query_applied':q1['question_receipt_status']=='applied',
      'query_released':release,'NoQuery_selected':native1 is not None and q1['actual_motor']==-1,
      'q1_STATE':state,'preview_bit':bit,'Native_q2_valid':valid2,'route':route,
      'Native_requested_unique':len(ids),'Native_applied':sum(v=='applied'for v in ids.values()),
      'Native_rejected':sum(v!='applied'for v in ids.values()),'Native_id_statuses':ids,'returned_failed':row['returned_failed'],
      'q1_tick':q1['query_tick'],'q2_tick':q2['query_tick'],
      'q1_phase':[q1['query_tick']%n for n in(67,391,782)],'q2_phase':[q2['query_tick']%n for n in(67,391,782)]}

def summarize(v):
    need(v.get('schema')=='DEE.PI10.audit_normalized_rows.R01'and v.get('closed')is True,'Closed normalized evidence required')
    need(v.get('primary_projection_checked')is True and v.get('projection_code_sha256'),'A separate primary projection must be checked, not just this summarizer')
    rows=[check_row(r)for r in v['rows']];groups={}
    for arm in('real','nonfailure','yoked'):
        rr=sorted([r for r in rows if r['arm']==arm],key=lambda r:r['ordinal'])
        need([r['ordinal']for r in rr if r['ordinal']<18]==list(range(18)),'All18 cases, failures included: '+arm)
        ids={r['life_id']for r in rr};need(len(ids)==1,'One continuous lineage per arm')
        unique_native={}
        for r in rr:
            for ident,status in r['Native_id_statuses'].items():
                if ident in unique_native:need(unique_native[ident]==status,'Cross-episode receipt alias disagrees')
                unique_native[ident]=status
        groups[arm]={'life_id':next(iter(ids)),'offered':len(rr),'evaluated18':18,
          'useful18':sum(r['useful']for r in rr if r['ordinal']<18),
          'reserved12':sum(r['reserved']for r in rr),'reserved_useful':sum(r['useful']for r in rr if r['reserved']),
          'query_requested':sum(r['query_requested']for r in rr),'query_applied':sum(r['query_applied']for r in rr),
          'query_released':sum(r['query_released']for r in rr),'NoQuery_selected':sum(r['NoQuery_selected']for r in rr),
          'Native_q1_NULL':sum(not r['Native_q1_valid']for r in rr),'Native_q1_zero':sum(r['Native_q1_zero']for r in rr),
          'out_of_domain':sum(not r['domain_admitted']for r in rr),'Native_requested':len(unique_native),
          'Native_applied':sum(s=='applied'for s in unique_native.values()),'Native_rejected':sum(s!='applied'for s in unique_native.values()),
          'cross_episode_receipt_aliases':sum(r['Native_requested_unique']for r in rr)-len(unique_native),
          'by_regime':{g:{'offered':sum(r['regime']==g for r in rr),'useful':sum(r['regime']==g and r['useful']for r in rr),
              'query':sum(r['regime']==g and r['query_applied']for r in rr)}for g in REGIMES}}
    gain=groups['real']['reserved_useful']-groups['nonfailure']['reserved_useful']
    actual=[r for r in rows if r['arm']=='real']
    return_uses=[r['ordinal']for r in actual if r['ordinal']in(14,15,16,17)and r['query_released']and r['useful']]
    bypass_uses=[r['ordinal']for r in actual if r['regime']=='bypass'and r['reserved']and r['q1_STATE']==1 and r['preview_bit']==1 and r['NoQuery_selected']and r['useful']]
    return {'schema':'DEE.PI10.normalized_consultation_metrics.R01','Native_executed':False,'DEE_imported':False,
      'scope':'Metrics over normalized closed records whose separate primary projection was checked; not Native reproduction, autonomy or adoption.',
      'source_projection_code_sha256':v['projection_code_sha256'],'groups':groups,'rows':rows,
      'reserved_gain_vs_nonfailure':gain,'gate_at_least2_reserved_resource_gain':gain>=2,
      'useful_return_to_query_reserved_ordinals':return_uses,'useful_bypass_NoQuery_matched_STATE1_Z':bypass_uses,
      'bounded_bidirectional_functional_witness':len(return_uses)>=2 and bool(bypass_uses),
      'query_specific_credit_not_established_by_this_summarizer':True,'automatic_adoption':False}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--entrada',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    v=json.loads(a.entrada.read_text('utf-8-sig'));result=summarize(v)
    result['input']={'path':str(a.entrada),'sha256':hashlib.sha256(a.entrada.read_bytes()).hexdigest()};result['at_utc']=datetime.now(timezone.utc).isoformat()
    need(not a.salida.exists(),'Never overwrite a previous evidence result')
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'output':str(a.salida),'sha256':hashlib.sha256(a.salida.read_bytes()).hexdigest(),'Native_executed':False}))
if __name__=='__main__':main()
