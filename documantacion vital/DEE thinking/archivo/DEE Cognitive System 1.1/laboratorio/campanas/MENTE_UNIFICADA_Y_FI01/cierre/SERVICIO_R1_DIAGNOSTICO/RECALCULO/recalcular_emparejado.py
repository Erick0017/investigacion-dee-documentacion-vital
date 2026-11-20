"""Standard-library archived verification of the paired native service test."""
import argparse,gzip,hashlib,json
from collections import Counter
from pathlib import Path


def fields(n):
    n=int(n)
    if not 0<=n<2**64:raise ValueError('RAW uint64 required')
    def signed(x):return x-16 if x>=8 else x
    return {'state':n&0xffffffff,'s_reg':(n>>32)&65535,'semantic':(n>>60)&15,'direction':[signed((n>>s)&15)for s in(48,52,56)]}


def calculate(primary):
    data=primary.read_bytes();j=json.loads(gzip.decompress(data));r=j['records'];checks={};issues=[];requests=Counter();native=[];observations=0
    def check(label,condition):
        checks[label]=bool(condition)
        if not condition:issues.append(label)
    results={k:json.loads(v['result'])for k,v in r.items()if isinstance(v,dict)and isinstance(v.get('result'),str)}
    gates={(37,33,32),(37,33,34),(33,37,32),(33,37,34),(37,37,32),(37,37,34),(29,37,32),(29,37,34),(37,29,32),(37,29,34)}
    for key in('pair_r02_pending','pair_r02_gamma'):
        record=r[key];payload=json.loads(record['payload']);encoded=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
        check(key+'_literal_payload_hash',hashlib.sha256(encoded).hexdigest()==record['payload_sha'])
        row=results[key]['result']['rows'][0];panel=row['reader']['panel'];found=[]
        check(key+'_all_ten_gates',len(panel)==10 and set(tuple(x['site'])for x in panel)==gates)
        for item in panel:
            decoded=fields(item['raw']);observations+=1
            check(key+'_fields_'+str(item['site']),all(item[k]==v for k,v in decoded.items()))
            d=decoded['direction']
            if decoded['state']>0 and decoded['semantic']==1 and d[:2]==[0,0]and d[2]in(-1,1):found.append(d[2])
        sign=found[0]if len(found)==1 else None;check(key+'_native_reader_exact',sign==row['reader']['formed_native_command'])
        native.append({'request_id':key,'decoded_sign':sign,'before_tick':results[key]['before_tick'],'after_tick':results[key]['after_tick']})
        for event in row['requests']:requests[event['receipt']['status']]+=1
    exported=r['export']['manifest'];imported=r['import'];initial=r['import_initial'];last=r['second_copy_process_final'];previous=r['first_copy_process_final']
    check('imported_complete_physical_fields_equal_export',all(exported['physical'][k]==imported['physical'][k]==initial['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')))
    check('import_mapping_is_explicit_distinct_life',imported['identity']['new_life_id']!=imported['identity']['source_life_id']and imported['life_id']==initial['life_id'])
    check('import_retained_pause',initial['paused']is True)
    check('transport_payload_deduplicated',r['duplicate']['admission']=='existing_same_transport_request')
    error=json.loads(r['pair_r02_unknown']['error']);check('unknown_interface_rejected_without_native_input',r['pair_r02_unknown']['status']=='rejected_invalid'and error['native_tick_unchanged']and error['no_material_input_submitted'])
    check('same_imported_life_next_process',last['life_id']==previous['life_id']==imported['life_id']and last['pid']!=previous['pid'])
    check('next_process_no_material_replay',last['material_calls']==previous['material_calls']and last['tick']>previous['tick'])
    check('protected_bytes_unchanged',j['protected_before']==j['protected_after'])
    for source in j['executed_source']:
        path=primary.parent/'codigo'/source['file'];check('source_'+source['file'],path.stat().st_size==source['bytes']and hashlib.sha256(path.read_bytes()).hexdigest()==source['sha256'])
    check('no_harness_exception',not r.get('harness_error'))
    return {'schema':'DEE.paired_service.archived_recalculation.v1','primary':{'file':primary.name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)},
        'native_reads':native,'raw_observations_checked':observations,'native_receipts':{'requested':sum(requests.values()),**dict(requests)},
        'next_process_idle_ticks':last['tick']-previous['tick'],'export_members_from_receipt':r['export']['verification'],
        'checks':checks,'issues':issues,'scope':'Archived arithmetic, exact RAW and exported executed-source bytes. Export manifest/native hash checks were performed during the operational test. This calculation does not contain/load omitted full native snapshots, replay physics or re-execute external jobs. Neither access is new learning.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--primario',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    result=calculate(a.primario);a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'issues':result['issues'],'native_receipts':result['native_receipts'],'next_process_idle_ticks':result['next_process_idle_ticks']}));return bool(result['issues'])


if __name__=='__main__':raise SystemExit(main())
