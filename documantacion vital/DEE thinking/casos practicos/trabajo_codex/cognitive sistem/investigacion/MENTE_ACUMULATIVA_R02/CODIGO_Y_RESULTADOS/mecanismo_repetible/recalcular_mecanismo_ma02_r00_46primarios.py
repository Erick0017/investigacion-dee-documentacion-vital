"""Portable exact archive recalculation. Python stdlib only; ZERO DEE ticks.
Recomputes signed emissions from uint64 RAW, checks decoded fields, denominators,
actual service law and finite-use persistence evidence. It does not certify a
general cognitive interpretation or re-run the native engine/environment.
"""
import argparse,gzip,hashlib,json
from collections import Counter
from pathlib import Path
def raw(x):
    q=int(x['raw']);ns=[(q>>shift)&15 for shift in(48,52,56)]
    return {'state':q&0xffffffff,'s_reg':(q>>32)&65535,'semantic':(q>>60)&15,'direction':[v-16 if v>=8 else v for v in ns]}
def signed(panel):
    cs=[]
    for p in panel:
        r=raw(p)
        if r['state']>0 and r['semantic']==1 and r['direction']in([0,0,-1],[0,0,1]):cs.append({'site':p['site'],'sign':r['direction'][2]})
    return cs
def norm(cs):return sorted((tuple(x['site']),x['sign'])for x in cs)
def walk(x,path=''):
    if isinstance(x,dict):
        yield path,x
        for k,v in x.items():yield from walk(v,path+'/'+str(k))
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from walk(v,path+'/'+str(i))
def check_observations(x):
    count=0;issues=[]
    for path,p in walk(x):
        if {'raw','clock','site','state','s_reg','semantic','direction'}<=set(p):
            count+=1;r=raw(p)
            for k,v in r.items():
                if p[k]!=v:issues.append(path+': decoded '+k+' differs from exact RAW')
            if not 0<=int(p['raw'])<2**64 or not 0<=int(p['clock'])<2**64:issues.append(path+': integer outside uint64')
        if {'panel','candidates'}<=set(p)and isinstance(p['panel'],list)and all(isinstance(a,dict)and'raw'in a for a in p['panel']):
            if norm(signed(p['panel']))!=norm(p['candidates']):issues.append(path+': stored gate candidates differ from RAW')
    return count,issues
def statuses(x):
    rs=x.get('receipts',[]);c=Counter()
    for r in rs:
        if not isinstance(r,dict):continue
        q=r.get('receipt',r)
        if isinstance(q,dict)and'status'in q:c[q['status']]+=1
    return dict(sorted(c.items()))
def u0_actions(sites):
    found={}
    for k,p in sites.items():
        if not k.startswith('action.'):continue
        r=raw(p);v=r['direction']
        if r['state']>0 and r['semantic']==1 and r['s_reg']>7 and v[0]in(-1,1)and v[1]in(-1,1)and v[2]==1:found[k]={'site':p['site'],'direction':v,'s_reg':r['s_reg']}
    return found
def result(name,x):
    schema=x['schema'];n,issues=check_observations(x);out={'file':name,'schema':schema,'identifier':x.get('identifier',x.get('label',name)),'exact_observations_checked':n,'receipt_status_counts':statuses(x)}
    if schema.startswith('MA02.native_history_selector.'):
        tick=x['read_tick'];r=next(a for a in x['rows']if a['tick']==tick);cs=signed(r['gates'])
        if norm(cs)!=norm(x['candidates']):issues.append('Recorded candidates differ from fixed RAW gates')
        v=cs[0]['sign']if len(cs)==1 else None
        if v!=x['decoded_sign']:issues.append('Recorded decoded sign differs from RAW')
        out.update(read_tick=tick,candidates=cs,unique_sign=v,selector_trace=[{'tick':r['tick'],'direction':raw(r['selector'])['direction'],'history_semantic':raw(r['history_latch'])['semantic']}for r in x['rows']if r['tick']in(129,130,133,134,197,200,201,205)])
    elif schema=='MA02.P1.actual_consequence_cycle.2':
        pending=None;js=[]
        for j in x['jobs']:
            cs=signed(j['fixed_all_gate_panel']);v=cs[0]['sign']if len(cs)==1 else None
            if norm(cs)!=norm(j['candidates'])or v!=j['native_command']:issues.append('Cycle native command not recomputed from fixed gate RAW')
            w=j['worker_receipt'];expected=None;file_match=None
            if w is not None:
                if w['worker']!=j['executed_command']:issues.append('Worker command differs from native actuator command')
                if w['operation']=='verify_commit':expected=w['worker']!=pending['prepared_by']and bool(w['prepared_artifact_check']['valid'])if pending else False
                else:
                    vals=w['raw_observations'];expected=w['worker']==(1 if sum(vals[::2])+int(w['modelled_capacity_credit_not_actor_input'])>=sum(vals[1::2])else -1)
                if bool(expected)!=bool(w['accepted']):issues.append('Actual worker acceptance not consistent with declared service law')
                pending=w['pending_transaction']
            js.append({'tick':j['tick'],'candidates':cs,'native_command':v,'executed_command':j['executed_command'],'worker_accepted':None if w is None else w['accepted'],'acceptance_recomputed':expected,'operation':None if w is None else w['operation'],'transaction_completed':False if w is None else w['transaction_completed'],'generic_return_requested':j['feedback_touch_request']is not None})
        out.update(requested_windows=len(js),native_emissions=sum(j['native_command']is not None for j in js),abstentions=sum(j['native_command']is None for j in js),actual_actions=sum(j['executed_command']is not None for j in js),accepted_actions=sum(j['worker_accepted']is True for j in js),transactions_completed=sum(j['transaction_completed']for j in js),jobs=js)
    elif schema=='MA02.physical_tap.pilot.1':
        born=[r['tick']for r in x['rows']if raw(r['detector'])['state']>0 and raw(r['detector'])['semantic']==7]
        continued=[{'tick':r['tick'],'raw':r['packet']['raw'],'direction':raw(r['packet'])['direction'],'s_reg':raw(r['packet'])['s_reg']}for r in x['rows']if r['tick']>=1]
        out.update(detector_native_sem7_ticks=born,parent_continuation=continued,parent_payload_preserved=all(p['direction']==[0,0,1]and p['s_reg']==x['payload']for p in continued)if x['packet_supplied']else None)
    elif schema in('MA02.U0.restore.pilot.1','MA02.U0.repeatable.pilot.1'):
        rounds=[]
        for j in range(5):
            t=72+67*j;r=next(a for a in x['rows']if a['tick']==t);sites=r['physical']['sites']if'physical'in r else r['observation']['sites'];acts=u0_actions(sites)
            stored=x['rounds'][j].get('actions',x['rounds'][j].get('native_actions'))
            if set(acts)!=set(stored):issues.append('U0 stored action set differs from fixed RAW panel at'+str(t))
            rounds.append({'tick':t,'native_actions':acts,'unique_action':next(iter(acts))if len(acts)==1 else None,'ambiguous':len(acts)>1})
        out.update(rounds=rounds,requested_windows=5,unique_actions=sum(r['unique_action']is not None for r in rounds),ambiguous_windows=sum(r['ambiguous']for r in rounds),empty_windows=sum(not r['native_actions']for r in rounds))
        if schema=='MA02.U0.repeatable.pilot.1':out['formed_question_ticks']=[r['round']for r in x['rounds']if r['native_questions']]
    elif schema=='MA02.P1.operational_check.1':
        r=x['result'];out.update(phase=x['phase'],before_tick=x['before']['tick'],after_tick=x['after']['tick'],physical_equality=x['before']==x['after'])
        if x['phase']=='usar':out['native_command']=r['reader']['formed_native_command'];out['candidates']=signed(r['reader']['panel'])
        if x['phase']=='recargar':out['second_use_rejected']=r['repeat_attempt']['rejected_by_contract']
        if x['phase']in('admitir','recargar')and x['before']!=x['after']:issues.append('Metadata-only phase changed physical state')
    elif schema=='MA02.P1.system_operational_check.1':
        out['phase']=x['phase'];rr=[]
        for r in x['results']:
            same=r['source_status_before']==r['source_status_after']
            if not same:issues.append('Ready source advanced during evaluation')
            z={'life':r['source_life'],'source_tick':r['source_status_after']['physical']['tick'],'ready_source_unchanged':same}
            if x['phase']=='fork_use':
                read=r['result']['result']['reader'];z['candidates']=signed(read['panel']);z['native_command']=read['formed_native_command'];z['evaluation_end_tick']=r['result']['physical']['tick']
            else:z['evaluation_end_tick']=r['reloaded_record']['physical']['tick'];z['repeat_rejected']=bool(r['repeat_rejected'])
            rr.append(z)
        out['lives']=rr
    elif schema=='MA02.P1.system_import.1':out.update(returncode=x['returncode'],no_ticks=x['no_new_ticks_or_teaching'],life=x.get('result',{}).get('life_id'),tick=x.get('result',{}).get('physical',{}).get('tick'))
    elif schema=='MA02.P1.gestor_path.1':
        out['operations']=[{'life':r['evaluation_life'],'command':r['command'][0],'returncode':r['returncode']}for r in x['rows']]
        if [r['returncode']for r in x['rows']]!=[0,0,0,0,0,2]*2:issues.append('Unexpected gestor finite-use path status')
    else:issues.append('Unsupported schema: '+schema)
    out['issues']=issues;return out
def main():
    p=argparse.ArgumentParser();p.add_argument('--evidencia',required=True);p.add_argument('--salida',required=True);a=p.parse_args();ev=Path(a.evidencia);out=[]
    for f in sorted([*ev.glob('*.json.gz'),*ev.glob('MA02_P1_OPERATION_*.json')],key=lambda z:z.name):
        blob=f.read_bytes();x=json.loads(gzip.decompress(blob)if f.suffix=='.gz'else blob)
        if not str(x.get('schema','')).startswith('MA02.'):continue
        r=result(f.name,x);r['sha256']=hashlib.sha256(blob).hexdigest();out.append(r)
    total={'schema':'MA02.archive_recalculation.mechanism.1','scope':'Exact archived recalculation only; no DEE import, no new ticks and no cognitive interpretation by PASS','primary_files':len(out),'exact_observations_checked':sum(r['exact_observations_checked']for r in out),'issue_count':sum(len(r['issues'])for r in out),'results':out}
    dest=Path(a.salida)
    if dest.exists():raise FileExistsError('Reference protected; choose new output')
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(total,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8');print(json.dumps({'primary_files':len(out),'exact_observations_checked':total['exact_observations_checked'],'issue_count':total['issue_count']}))
    if total['issue_count']:raise SystemExit(2)
if __name__=='__main__':main()
