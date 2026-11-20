"""Portable exact B14 adaptation recalc: stdlib, no DEE, no new ticks."""
import argparse,base64,gzip,hashlib,json,zlib
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def fields(o):
    r=int(o['raw']);v=[(r>>k)&15 for k in(48,52,56)]
    return {'state':r&0xffffffff,'s_reg':(r>>32)&65535,'semantic':(r>>60)&15,'direction':[x-16 if x>=8 else x for x in v]}
def observations(o):
    if isinstance(o,dict):
        if all(k in o for k in('raw','clock','state','s_reg','semantic','direction','site')):yield o
        for v in o.values():yield from observations(v)
    elif isinstance(o,list):
        for v in o:yield from observations(v)
def choice(row,family,errors,label):
    rr=row['reader'];panel=rr['observations']if family=='quantitative'else rr['panel'];cs=[]
    for o in panel:
        x=fields(o);v=x['direction']
        if x['state']<=0 or x['semantic']!=1:continue
        if family=='quantitative'and v[0]in(-1,0,1)and v[1]==1 and v[2]in(0,-1):cs.append(v[0])
        if family=='gamma'and v in([0,0,-1],[0,0,1]):cs.append(v[2])
    actual=cs[0]if len(cs)==1 else None
    reported=rr['choice']if family=='quantitative'else rr['formed_native_command']
    if actual!=reported:errors.append(label+': fixed primary reader differs')
    frames={f['tick']:{tuple(o['site']):o for o in f['sites']}for f in row['frames']}
    tick=row['query_tick']+6 if family=='quantitative'else row['read_tick']
    for o in panel:
        if frames[tick].get(tuple(o['site']))!=o:errors.append(label+': primary frame/reader differs')
    return actual
def output(w,errors,label):
    q=w['request'];r=w['receipt'];v=q['raw_observations'];payload=bytes(v)*max(1,32+sum(v[::2]))
    if q['pending_transaction']is not None:payload=base64.b64decode(q['pending_transaction']['payload_base64'])
    b=zlib.compress(payload,9)if q['executed_worker']==1 else hashlib.sha256(payload).digest()
    actual=bytes.fromhex(w['readback_hex'])
    if b!=actual or sha(actual)!=w['readback_sha256']or sha(actual)!=r['output_sha256']or len(actual)!=r['output_bytes']:errors.append(label+': actual file output not exact')
    if sha(payload)!=r['input_sha256']or len(payload)!=r['input_bytes']:errors.append(label+': file input differs')
    return actual
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidencia',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
    files=[];rows=[];errors=[];obs_count=0;receipts=[]
    for p in sorted(a.evidencia.glob('*_OP_*.json.gz')):
        b=p.read_bytes();o=read(p);r=o['result'];label=p.name;files.append({'file':label,'sha256':sha(b),'bytes':len(b)})
        for ob in observations(r):
            obs_count+=1
            if not 0<=int(ob['clock'])<2**64:errors.append(label+': clock not uint64')
            for key,val in fields(ob).items():
                if ob[key]!=val:errors.append(label+': decoded RAW '+key+' differs')
        fam=r['schedule']['family'];actual=choice(r['native'],fam,errors,label)
        if actual!=r['native_choice']:errors.append(label+': native command substituted')
        fixture=output(r['fixture'],errors,label+':fixture');fq=r['fixture']['request'];fr=r['fixture']['receipt'];pending=fr['pending_transaction']
        if len(fixture)!=12 or fq['executed_worker']!=1 or fq['raw_observations']!=[7,7]or fq['pending_transaction']is not None or not fr['accepted']:errors.append(label+': fixed environmental fixture differs')
        if fam=='quantitative'and r['native']['value']!=len(fixture):errors.append(label+': raw bytecount codec differs')
        accepted=False;action=r['actual_action']
        if actual in(-1,1):
            if action is None:errors.append(label+': signed native command not executed')
            else:
                output(action,errors,label+':action');q=action['request'];receipt=action['receipt']
                if q['executed_worker']!=actual or q['pending_transaction']!=pending:errors.append(label+': wrong native worker or altered pending task')
                embedded=base64.b64decode(pending['prepared_output_base64']);payload=base64.b64decode(pending['payload_base64'])
                intact=(embedded==fixture and sha(embedded)==pending['prepared_output_sha256']and sha(payload)==pending['payload_sha256']and zlib.decompress(embedded)==payload)
                accepted=actual!=pending['prepared_by']and intact
                if receipt['accepted']!=accepted or receipt['transaction_completed']!=accepted:errors.append(label+': actual C2 receipt mismatch')
                if not receipt['prepared_artifact_check']['valid']:errors.append(label+': invalid prepared artifact')
        elif action is not None:errors.append(label+': substituted action for silence/neutral')
        if accepted!=r['actual_accepted']or accepted!=r['actual_transaction_completed']:errors.append(label+': success counter mismatch')
        ret=r['failure_return']
        if (ret is not None)==accepted:errors.append(label+': generic failure return mismatched consequence')
        reqs=list(r['native']['requests'])
        if ret is not None:
            reqs.append(ret['request'])
            if ret['arrival']!=r['schedule']['possible_failure_arrival_tick']:errors.append(label+': return calendar changed')
            if(ret['post'][0]['s_reg']-ret['post'][1]['s_reg'])!=(ret['pre'][0]['s_reg']-ret['pre'][1]['s_reg'])-1:errors.append(label+': admitted failure contact did not have declared local reference effect')
        for req in reqs:receipts.append({'file':label,'id':req['id'],'status':req['receipt']['status']})
        if r['physical_after']['tick']!=r['schedule']['common_end_tick']:errors.append(label+': unmatched age')
        difference=r['references_after'][0]['s_reg']-r['references_after'][1]['s_reg']
        rows.append({'file':label,'arm':r['arm'],'index':r['schedule']['index'],'family':fam,'query_tick':r['native'].get('query_tick',r['native'].get('input_tick')),
          'end_tick':r['physical_after']['tick'],'native_choice_from_primary':actual,'actual_worker_executed':action is not None,'actual_accepted':accepted,'actual_transaction_completed':accepted,
          'failure_contact_requested':ret is not None,'reference_difference_after':difference,'counterlaw_analytic_useful_only':actual==1,
          'snapshot_sha256':o['INSTRUMENTO']['snapshot_sha256'],'artifact_sha256':r['fixture']['readback_sha256']})
    summaries=[]
    for arm in('T','U','H'):
        rr=sorted([r for r in rows if r['arm']==arm],key=lambda r:r['index']);run=0;firstfour=None
        for r in rr:
            run=run+1 if r['actual_accepted']else 0
            if run>=4 and firstfour is None:firstfour=r['index']-3
        summaries.append({'arm':arm,'requested_opportunities':len(rr),'actual_actions':sum(r['actual_worker_executed']for r in rr),'actual_completed':sum(r['actual_accepted']for r in rr),
          'first_pre_feedback_action':rr[0]['native_choice_from_primary']if rr else None,'first_four_consecutive_useful_start':firstfour,
          'new_feedbacks_before_stable_run':0 if firstfour==1 else(firstfour-1 if firstfour is not None else None),'cost_right_censored_beyond8':firstfour is None,
          'family_coverage':{f:sum(r['family']==f for r in rr)for f in('quantitative','gamma')},'counterlaw_analytic_only_useful':sum(r['counterlaw_analytic_useful_only']for r in rr),
          'initial_prior_reference_difference':-20 if arm=='T'else -1 if arm=='U'else 18,'final_reference_difference':rr[-1]['reference_difference_after']if rr else None})
    byage={r['index']:set(x['end_tick']for x in rows if x['index']==r['index'])for r in rows}
    if any(len(x)!=1 for x in byage.values())or len(rows)!=24:errors.append('Missing/mismatched fixed arm opportunities')
    result={'schema':'MUFI01.B14.adaptation.recalculation.v1','native_ticks_executed':0,'files':files,'trials':rows,'summaries':summaries,'exact_uint64_observations_checked':obs_count,
      'native_receipts':receipts,'requested':len(receipts),'admitted':sum(x['status']=='applied'for x in receipts),'rejected':sum(x['status'].startswith('rejected')for x in receipts),'errors':errors,
      'limits':'Counterlaw is analytical scoring of actual actions, not counterlaw C2 acceptance or its adaptation trajectory. Equal opportunity/age budget; failure material is the consequence-dependent variable. Only4uses per family, no new omitted-return branch, no population independence, no general learned policy or abstraction.'}
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'opportunities':len(rows),'summaries':summaries,'errors':errors,'sha256':sha(a.salida.read_bytes())}))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
