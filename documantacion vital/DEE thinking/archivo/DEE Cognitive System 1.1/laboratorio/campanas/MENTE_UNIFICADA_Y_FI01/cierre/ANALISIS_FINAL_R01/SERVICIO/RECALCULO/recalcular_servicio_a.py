"""Portable archived service calculation: RAW, admissions and real worker bytes.

No DEE import, world restoration or task execution. R04/R07 harness errors remain
in the primaries and are explained from exact boundary receipts, not rewritten.
"""
import argparse,gzip,hashlib,json,zlib
from collections import Counter
from pathlib import Path


def fields(n):
    n=int(n)
    if not 0<=n<2**64:raise ValueError('Exact uint64 RAW required')
    def signed(v):return v-16 if v>=8 else v
    return {'state':n&0xffffffff,'s_reg':(n>>32)&65535,'semantic':(n>>60)&15,'direction':[signed((n>>p)&15)for p in(48,52,56)]}


def calculate(root):
    paths={'main':'MAIN_SERVICIO_R04/MAIN_SERVICIO.json.gz','close':'CIERRE_MAIN_R05/CIERRE_MAIN.json.gz','later':'USO_POSTCOMPACTACION_R07/USO_POSTCOMPACTACION.json.gz'}
    sources=[];data={};checks={};issues=[];counts=Counter();raw_total=0;choices=[];memories=[];workers=[]
    def check(label,condition):
        checks[label]=bool(condition)
        if not condition:issues.append(label)
    for key,name in paths.items():
        b=(root/name).read_bytes();data[key]=json.loads(gzip.decompress(b));sources.append({'file':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
    main=data['main']['records'];close=data['close']['records'];later=data['later']['records']
    def decode_observation(o,label):
        nonlocal raw_total
        p=fields(o['raw']);raw_total+=1;check(label,all(o[k]==v for k,v in p.items()));return p
    def admissions(rows):
        for r in rows:counts[r['receipt']['status']]+=1
    def native_selector(row,label):
        observed=row['reader']['observations'];sites={(13,17,15):-1,(15,17,15):0,(17,17,15):1};found=[]
        check(label+'_three_fixed_actuators',len(observed)==3 and {tuple(o['site'])for o in observed}==set(sites))
        for o in observed:
            f=decode_observation(o,label+'_RAW_'+str(o['site']));sign=sites[tuple(o['site'])]
            if f['state']>0 and f['semantic']==1 and f['direction']==[sign,1,0]:found.append(sign)
        answer=found[0]if len(found)==1 else None;check(label+'_reader_matches_RAW',row['reader']['choice']==answer)
        choices.append({'request_id':label,'native_choice':answer,'read_tick':row['read_tick']});admissions(row['requests']);return answer
    def memory(row,label):
        for query in row['result']['rows']:
            panel=query['reader']['panel'];gates={(37,33,32),(37,33,34),(33,37,32),(33,37,34),(37,37,32),(37,37,34),(29,37,32),(29,37,34),(37,29,32),(37,29,34),(29,29,32),(29,29,34)}
            check(label+'_twelve_fixed_gates',len(panel)==12 and{tuple(o['site'])for o in panel}==gates);found=[]
            for o in panel:
                f=decode_observation(o,label+'_RAW_'+str(o['site']));v=f['direction']
                if f['state']>0 and f['semantic']==1 and v[:2]==[0,0]and v[2]in(-1,1):found.append(v[2])
            answer=found[0]if len(found)==1 else None;check(label+'_reader_exact',query['reader']['formed_native_command']==answer)
            memories.append({'request_id':label,'context_address_P0':query['context_signal'],'native_content':answer,'read_tick':query['read_tick']});admissions(query['requests'])
    for key in('mu_a50_work1','mu_a50_zeta','mu_a50_work2','mu_a50_old_memory'):
        transport=main[key];result=json.loads(transport['result']);payload=json.loads(transport['payload']);canonical=json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')
        check(key+'_literal_input_identity',hashlib.sha256(canonical).hexdigest()==transport['payload_sha'])
        check(key+'_no_fence_denials',not result['result']['INSTRUMENTO_FENCE']['denied'])
        for index,row in enumerate(result['result']['rows']):
            if row['kind']=='explicit_operator_memory_access':memory(row,key+'_'+str(index));continue
            native=native_selector(row,key);external=row['external'];receipt=external['worker_receipt'];public=receipt['raw_observations'];left=sum(public[::2]);right=sum(public[1::2]);content=bytes(public)*max(1,32+left)
            produced=zlib.compress(content,9)if receipt['worker']==1 else hashlib.sha256(content).digest()
            actual=(root/'MAIN_SERVICIO_R04/artefactos'/receipt['output_name']).read_bytes()
            check(key+'_worker_is_native_choice',external['executed_worker']==receipt['worker']==native)
            check(key+'_actual_tool_bytes',actual==produced and len(actual)==receipt['output_bytes']and hashlib.sha256(actual).hexdigest()==receipt['output_sha256'])
            check(key+'_worker_law_and_payload',receipt['accepted']==(receipt['worker']==(1 if left+receipt['modelled_capacity_credit_not_actor_input']>=right else-1))and receipt['input_bytes']==len(content)and receipt['input_sha256']==hashlib.sha256(content).hexdigest())
            check(key+'_exact_one_declared_worker',len(result['result']['INSTRUMENTO_FENCE']['exact_environment_processes'])==1)
            workers.append({'request_id':key,'native_choice':native,'actual_output_bytes':len(actual),'accepted':receipt['accepted'],'public_values':public,'no_result_reexecution':True})
    query=later['native_use_result']['result']['rows'][0];native_selector(query,'mu_a52_use')
    first=json.loads(main['mu_a50_work1']['result']);last=json.loads(main['mu_a50_old_memory']['result']);pause=json.loads(close['mu_a50_pause']['result'])
    check('late_pause_resumed_at_same_actual_cut_without_repeating_actions',pause['before_tick']==pause['after_tick']==last['after_tick']==later['before']['physical']['tick'])
    check('original_timeout_is_preserved',main['harness_error']=={'type':'TimeoutError','detail':'mu_a50_pause'})
    check('first_epoch_no_uncertain_or_lost_action',close['stopped']['material_calls']==4 and close['stopped']['running']is False and not close['stopped']['uncertain_external_result'])
    check('first_epoch_closure_no_native_change',close['explicit_epoch_close']['result']['physical_before']==close['explicit_epoch_close']['result']['physical_after'])
    owner=json.loads(data['later']['commands'][0]['stdout'])
    check('next_epoch_one_new_material_call_from_exact_final_receipt',owner['material_calls']==later['new_epoch']['material_calls']+1==5)
    check('one_life_and_parent_across_windows',later['before']['life_id']==later['final']['life_id']==data['main']['protocol']['pre']['life_id']=='MU_MAIN'and later['before']['parent']==later['final']['parent']==data['main']['protocol']['pre']['parent'])
    check('next_epoch_closed_without_native_rollback',later['closed_epoch']['result']['physical_before']==later['closed_epoch']['result']['physical_after']and later['final']['physical']['tick']>later['before']['physical']['tick'])
    cached_false=[q for q in data['later']['checks']if not q['observed']];check('cached_counter_error_preserved',len(cached_false)==1 and cached_false[0]['check']=='exactly one new generic use and no task replay')
    for item in data['main']['source']:
        p=root/'MAIN_SERVICIO_R04/codigo'/item['file'];check('source_'+item['file'],len(p.read_bytes())==item['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'])
    return {'schema':'DEE.unified.service.archived_calculation_A.v1','sources':sources,'checks':checks,'issues':issues,'exact_RAW_observations':raw_total,
        'native_selections':choices,'assisted_old_memory_accesses':memories,'actual_workers':workers,
        'native_receipt_denominators':{'requested':sum(counts.values()),**dict(counts)},'first_epoch_idle_ticks':close['stopped']['idle_ticks'],
        'final_cut':later['final'],'preserved_harness_errors':{'R04':main['harness_error'],'R07':cached_false},
        'scope_and_limits':'Archived RAW/input/receipt/source and actual tool-byte verification; no DEE import, native reproduction, new worker execution or policy training. Host initiates all requests and the three memory addresses. Two useful workers use an already acquired selector; these cases alone do not establish acquisition of that selector, performance on arbitrary public values, R2 or the final sixty-minute regime.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();result=calculate(a.evidencia)
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'issues':result['issues'],'RAW':result['exact_RAW_observations'],'receipts':result['native_receipt_denominators'],'workers':result['actual_workers']}));return bool(result['issues'])


if __name__=='__main__':raise SystemExit(main())
