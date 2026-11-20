"""Archived pilot calculation, standard library only; zero new DEE ticks."""
import argparse,gzip,hashlib,json
from collections import Counter
from pathlib import Path


def raw(n):
    n=int(n)
    if not 0<=n<2**64:raise ValueError('RAW outside uint64')
    def signed(x):return x-16 if x>=8 else x
    return {'state':n&0xffffffff,'s_reg':(n>>32)&65535,'semantic':(n>>60)&15,
        'direction':[signed((n>>s)&15)for s in(48,52,56)]}


def calculate(primary):
    data=primary.read_bytes();j=json.loads(gzip.decompress(data));r=j['records'];issues=[];checks={};counts=Counter();answers=[];raw_count=0
    gates={(37,33,32),(37,33,34),(33,37,32),(33,37,34),(37,37,32),(37,37,34),(29,37,32),(29,37,34),(37,29,32),(37,29,34)}
    def verify(label,condition):
        checks[label]=bool(condition)
        if not condition:issues.append(label)
    values={name:json.loads(r[name]['result'])for name in('first','pause','resume','second','save','stop')}
    for name in('first','second'):
        v=values[name];row=v['result']['rows'][0];panel=row['reader']['panel'];candidates=[]
        verify(name+'_all_ten_fixed_gates',set(tuple(o['site'])for o in panel)==gates and len(panel)==10)
        for o in panel:
            fields=raw(o['raw']);raw_count+=1
            for key,val in fields.items():verify(name+'_'+str(o['site'])+'_'+key,o[key]==val)
            d=fields['direction']
            if fields['state']>0 and fields['semantic']==1 and d[:2]==[0,0] and d[2]in(-1,1):candidates.append(d[2])
        sign=candidates[0]if len(candidates)==1 else None
        verify(name+'_reader_matches_exact_RAW',row['reader']['formed_native_command']==sign)
        for request in row['requests']:counts[request['receipt']['status']]+=1
        answers.append({'id':name,'decoded_sign':sign,'before_tick':v['before_tick'],'after_tick':v['after_tick'],
            'scope':'Decoder has no token or expected-answer input; familiar context use, not new acquisition.'})
    first,second=values['first'],values['second'];pause=values['pause']
    idle_exact=pause['before_tick']-first['after_tick']
    continued=r['second_process_final']['tick']-r['first_process_final']['tick']
    verify('real_idle_ticks_after_first_query',idle_exact>0)
    verify('pause_has_no_native_advance',pause['before_tick']==pause['after_tick']==r['paused_status']['tick'])
    verify('queued_material_waited_through_pause',second['before_tick']==pause['after_tick'])
    verify('same_life_in_second_process',r['first_process_final']['life_id']==r['second_process_final']['life_id']==j['life'])
    verify('different_owner_process',r['first_process_final']['pid']!=r['second_process_final']['pid'])
    verify('later_process_continued_not_rewound',continued>0)
    verify('material_calls_stayed_two',r['second_process_final']['material_calls']==r['first_process_final']['material_calls']==2)
    verify('duplicate_transport_not_reexecuted',r['duplicate_transport_receipt']['admission']=='existing_same_transport_request')
    verify('protected_sources_bytes_unchanged',j['protected_before']==j['protected_after'])
    code=[]
    for item in j['code']:
        p=primary.parent/'codigo'/item['file'];actual=hashlib.sha256(p.read_bytes()).hexdigest()
        verify('executed_source_'+item['file'],actual==item['sha256']);code.append({'file':item['file'],'sha256':actual})
    historical_false=[q for q in j['checks']if not q['observed']]
    verify('one_preserved_harness_error_not_hidden',len(historical_false)==1 and historical_false[0]['check']=='world ticks advanced between material requests')
    return {'schema':'DEE.persistent_pilot.archived_recalculation.v1','primary':{'file':primary.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()},
        'answers':answers,'receipt_denominators':{'requested':sum(counts.values()),**dict(counts)},'raw_fields_decoded':raw_count,
        'idle_ticks_between_exact_boundaries':idle_exact,'ticks_in_next_process':continued,'source_bytes_verified':code,
        'checks':checks,'issues':issues,'preserved_harness_false_checks':historical_false,
        'observer_correction':'The R01 harness compared an asynchronous cached heartbeat with a later receipt. It returned false. The exact pause boundary independently shows idle evolution; the primary and original code remain unchanged.',
        'scope_and_limits':'Archived arithmetic/RAW/source-byte verification only. No DEE import, restoration, native reproduction, additional life or 60-minute trial. Two inherited context accesses do not show new semantic learning or P2.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--primario',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    result=calculate(a.primario);a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'issues':result['issues'],'idle_ticks':result['idle_ticks_between_exact_boundaries'],'next_process_ticks':result['ticks_in_next_process'],'receipts':result['receipt_denominators']}))
    return bool(result['issues'])


if __name__=='__main__':raise SystemExit(main())
