"""Portable exact archived calculation, stdlib only, zero native ticks.

Verifies RAW decoding, frozen readers, denominators, fixed outcome codec, and
actual bounded worker output bytes. Does not emulate kernel evolution or prove
unrecorded encounters. Original complete worlds remain at indexed local paths.
"""
import argparse,base64,gzip,hashlib,json,zlib,struct
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def raw_fields(raw):
    r=int(raw);dirs=[(r>>k)&15 for k in(48,52,56)]
    return {'state':r&0xffffffff,'s_reg':(r>>32)&65535,'semantic':(r>>60)&15,'direction':[v-16 if v>=8 else v for v in dirs]}
def observations(node):
    if isinstance(node,dict):
        if all(k in node for k in('raw','state','s_reg','semantic','direction','clock','site')):yield node
        for v in node.values():yield from observations(v)
    elif isinstance(node,list):
        for v in node:yield from observations(v)
def decode(o):return raw_fields(o['raw'])
def reader(obs,include_zero=True):
    out=[]
    for o in obs:
        x=decode(o);sx=int(o['site'][0])-33
        if o['site'][1:]!=[35,33]or sx not in(-2,0,2):continue
        sign=sx//2
        if not include_zero and sign==0:continue
        if x['state']>0 and x['semantic']==1 and x['direction']==[sign,1,0]:out.append({'choice':sign,'site':o['site'],'raw':str(o['raw']),'clock':str(o['clock']),'s_reg':x['s_reg']})
    return {'candidates':out,'choice':out[0]['choice']if len(out)==1 else None}
def check_actual(op,mode,errors,label):
    rr=reader(op['native_read']['observations']);decision=rr['choice']
    if decision!=op['physical_decision']:errors.append(label+': physicaldecisionnotrawreader')
    expected_exec=decision in(-1,1)and mode!='nulled'
    if expected_exec!=op['executed']:errors.append(label+': actuatorsubstituted')
    receipt=op['worker_receipt'];expected_success=False
    if expected_exec:
        q=op['worker_request'];v=q['raw_observations'];left=sum(v[::2]);right=sum(v[1::2]);eligible=1 if left+q['capacity_credit']>=right else -1
        expected_success=decision==eligible
        if q['executed_worker']!=decision:errors.append(label+': workerchoiceleaked')
        if q['domain']!='trabajadores':errors.append(label+': unexpectedworkerdomain')
        payload=bytes(v)*max(1,32+left);expected=zlib.compress(payload,9)if decision==1 else hashlib.sha256(payload).digest()
        actual=base64.b64decode(op['actual_output']['base64'])
        if expected!=actual:errors.append(label+': actualworkerbytesnotreproducible')
        if sha(actual)!=op['actual_output']['sha256']or len(actual)!=op['actual_output']['bytes']:errors.append(label+': outputbytesidentity')
        if receipt['accepted']!=expected_success or receipt['worker']!=decision:errors.append(label+': servicelawverdict')
        if receipt['input_sha256']!=sha(payload)or receipt['input_bytes']!=len(payload):errors.append(label+': inputpayload')
        if receipt['output_sha256']!=sha(actual)or receipt['output_bytes']!=len(actual):errors.append(label+': outputreceipt')
    elif receipt is not None:errors.append(label+': unexecutedworkerhasreceipt')
    if op['opportunity_success']!=expected_success or op['deadline_or_worker_failure']==expected_success:errors.append(label+': outcomeclassification')
    return {'choice':decision,'executed':expected_exec,'success':expected_success,'raw_candidates':rr['candidates'],'output_sha256':op['actual_output']['sha256']if expected_exec else None}
def calculate(folder):
    files=sorted([*folder.glob('MUFI_S*.json.gz'),*folder.glob('MUFI_G*.json.gz')]);errors=[];tables=[];all_obs=0;contents={};fileindex=[];array_values=0
    for p in files:
        b=p.read_bytes();x=json.loads(gzip.decompress(b));label=x.get('identifier',p.name);fileindex.append({'name':p.name,'sha256':sha(b),'bytes':len(b)})
        contents[label]=x;count=0
        for o in observations(x):
            fields=decode(o);count+=1
            for k,v in fields.items():
                if o[k]!=v:errors.append(label+': RAW '+k+' mismatchat'+str(o['tick'])+str(o['site']))
            if int(o['clock'])<0:errors.append(label+': negativeclock')
        all_obs+=count
        reqs=x.get('requests',[]);statuses={}
        for r in reqs:
            s=r['receipt']['status'];statuses[s]=statuses.get(s,0)+1
        rec={'identifier':label,'raw_observations_checked':count,'requested_material_inputs':len(reqs),'receipt_statuses':statuses}
        if 'worlds'in x:
            for name,v in x['worlds'].items():
                if v['tick_before']!=v['tick_after']:errors.append(label+': read_onlyadvanced')
                for field in('raw','clock'):
                    vs=v[field];array_values+=len(vs)
                    if len(vs)!=v['N']**3:errors.append(label+': arraywrongsize')
                    if any(not 0<=int(y)<2**64 for y in vs):errors.append(label+': arrayoutofuint64')
                    h=sha(b''.join(struct.pack('<Q',int(y))for y in vs))
                    if h!=v[field+'_le_uint64_sha256']:errors.append(label+': arraydigest')
            summaries=[]
            for pair in x['comparisons']:
                u=x['worlds'][pair['left']];v=x['worlds'][pair['right']]
                ri=[i for i,(a,b)in enumerate(zip(u['raw'],v['raw']))if a!=b];ci=[i for i,(a,b)in enumerate(zip(u['clock'],v['clock']))if a!=b]
                if ri!=[r['index']for r in pair['raw_differences']]or ci!=[r['index']for r in pair['clock_differences']]:errors.append(label+': fullarraydifferencecount')
                for r in pair['raw_differences']:
                    i=r['index'];N=u['N']
                    if r['site']!=[i//(N*N),(i//N)%N,i%N]or r['left_raw']!=u['raw'][i]or r['right_raw']!=v['raw'][i]:errors.append(label+': exactdifferencecoordinate/raw')
                summaries.append({'left':pair['left'],'right':pair['right'],'raw_differences':len(ri),'clock_differences':len(ci),'raw_sites':[r['site']for r in pair['raw_differences']]})
            rec.update({'kind':'complete_physical_arrays_read_only','worlds':len(x['worlds']),'comparisons':summaries,'operational_metadata_not_compared':True})
        elif 'results'in x:
            decoded=[]
            for old in x['results']:
                row=next(r for r in x['rows']if r['tick']==old['read_tick']);r=reader(row['roi'],False);decoded.append(r['choice'])
                if r['choice']!=old['choice']:errors.append(label+': originalfrozenreader')
            rec.update({'kind':'prospective_pilot','frozen_binary_reader':decoded,'native_binary_emissions':sum(c in(-1,1)for c in decoded),'evaluated_windows':len(decoded),'history_for_evaluator_only':x['history_for_evaluator_only'],'original_prediction_not_relabelled':True})
        elif 'readings'in x:
            decoded=[]
            for old in x['readings']:
                r=reader(old['observations']);decoded.append(r['choice'])
                if r['choice']!=old['choice']:errors.append(label+': reservereader')
            rec.update({'kind':'new_timing_payload5_reserve','mode':x['mode'],'choices':decoded,'evaluated_windows':len(decoded),'native_binary_emissions':sum(c in(-1,1)for c in decoded),'neutral_emissions':sum(c==0 for c in decoded),'no_emission':sum(c is None for c in decoded)})
        elif 'operation'in x:
            d=check_actual(x['operation'],x['mode'],errors,label)
            if x['snapshot']['tick']<=x['parent']['tick']:errors.append(label+': continuationnotadvanced')
            rec.update({'kind':'separate_process_operational_continuation','parent_sha256':x['parent']['sha256'],'parent_tick':x['parent']['tick'],'final_tick':x['snapshot']['tick'],'choice':d['choice'],'actual_execution':d['executed'],'actual_service_accepted':d['success'],'snapshot_sha256':x['snapshot']['sha256']})
        elif 'operations'in x:
            decoded=[check_actual(o,x['mode'],errors,label+':'+str(j))for j,o in enumerate(x['operations'])]
            for j,(old,d)in enumerate(zip(x['operations'],decoded)):
                should_return=j<2 and not d['success']and x['mode']!='omitted';rr=old['generic_failure_return']
                if bool(rr)!=should_return:errors.append(label+': outcomecodeccondition')
                if rr:
                    expected=(1173,1955)[j]+(1 if x['mode']=='phase_shift'else 0)
                    if rr['payload']!=0 or rr['port']!='consequence.experience.A'or rr['tick']!=expected-3:errors.append(label+': returnencodeswrongport/solution')
            rec.update({'kind':'consequence_actual_worker','mode':x['mode'],'initial_history_for_evaluator_only':x['initial_history_for_evaluator_only'],'decisions':[d['choice']for d in decoded],'opportunities':len(decoded),'binary_native_responses':sum(d['choice']in(-1,1)for d in decoded),'neutral_responses':sum(d['choice']==0 for d in decoded),'absence':sum(d['choice']is None for d in decoded),'actual_executions':sum(d['executed']for d in decoded),'actual_service_accepted':sum(d['success']for d in decoded),'actual_service_rejected':sum(d['executed']and not d['success']for d in decoded),'abstention_or_nullified':sum(not d['executed']for d in decoded),'first_two_successes':sum(d['success']for d in decoded[:2]),'first_two_denominator':2,'five_reserved_same_law_successes':sum(d['success']for d in decoded[2:7]),'five_reserved_same_law_denominator':5,'last_two_inverted_law_successes':sum(d['success']for d in decoded[7:]),'last_two_denominator':2,'generic_returns':sum(bool(o['generic_failure_return'])for o in x['operations']),'worker_raw_checks':decoded})
        else:errors.append(label+': unsupportedprimaryschema')
        tables.append(rec)
    r8={r['identifier']:r for r in tables if r.get('kind')=='consequence_actual_worker'}
    contrasts={}
    if r8:
        real=r8['MUFI_S08_REAL_MINUS'];omit=r8['MUFI_S08_OMITTED_MINUS'];phase=r8['MUFI_S08_PHASE1_MINUS'];plus=r8['MUFI_S08_REAL_PLUS'];nulled=r8['MUFI_S08_NULLED_PLUS']
        contrasts={'actual_vs_omitted_same_law_reserved_successes':[real['five_reserved_same_law_successes'],omit['five_reserved_same_law_successes']],'actual_vs_dose_matched_phase1_reserved_successes':[real['five_reserved_same_law_successes'],phase['five_reserved_same_law_successes']],'real_plus_vs_actuator_nullified_plus_executions':[plus['actual_executions'],nulled['actual_executions']],'real_plus_vs_actuator_nullified_plus_first_decisions':[plus['decisions'][0],nulled['decisions'][0]],'law_inversion_counterexample_real_vs_omit':[real['last_two_inverted_law_successes'],omit['last_two_inverted_law_successes']],'scope':'One asymmetric prepared failure-to-A codec, acquired native scalar/choice. Phase-specific, not a reversible general policy or proof of own causal credit assignment.'}
    return {'schema':'MUFI01.selection.archived_recalculation.v2','native_ticks_executed':0,'input_files':fileindex,'primary_files':len(files),'exact_raw_observations_verified':all_obs,'exact_full_array_uint64_values_verified':array_values,'errors':errors,'cases':tables,'causal_contrasts':contrasts,'coverage':'RAW and readers fromexported observations; materialreceipt statuses; exactworkerbytes/input/hash/law; fixedfailure0returnprotocol; optional completephysicalRAW/clocks andcontinuations. No nativephysicsreproduction or equalityofunexportedoperationalmetadata.'}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--evidencia',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);args=ap.parse_args()
    r=calculate(args.evidencia);args.salida.parent.mkdir(parents=True,exist_ok=True);args.salida.write_bytes(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2).encode());print(json.dumps({'primary_files':r['primary_files'],'raw':r['exact_raw_observations_verified'],'errors':len(r['errors']),'sha256':sha(args.salida.read_bytes())}));raise SystemExit(bool(r['errors']))
