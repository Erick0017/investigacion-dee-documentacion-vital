"""Passive campaign-budget tally from canonical MATERIAL_REQUEST and own run receipts.

No DEE imports, ticks or process signals. OWNER startup/closure only checks missing
intervals; inherited idle_ticks and snapshots' starting ages are never new work.
"""
from pathlib import Path,PureWindowsPath
import argparse,collections,datetime,hashlib,json,sys
def sha(b):return hashlib.sha256(b).hexdigest()
def run(campaign,planned=0,limit=100000,reserved_batch_total=0):
    root=Path(campaign).resolve();ledger=root/'ENSAYOS.jsonl';data=ledger.read_bytes()
    # A concurrently appended incomplete last line is not interpreted as an event.
    end=data.rfind(b'\n')+1;prefix=data[:end];lines=prefix.decode('utf-8-sig').splitlines();events=[json.loads(x)for x in lines if x.strip()]
    seen={};duplicates=[];errors=[];requests=[];runs={};last_by_run={};perlife=collections.defaultdict(int)
    for line,event in enumerate(events,1):
        kind=event.get('kind');run_id=event.get('run')
        if kind=='OWNER_STARTED':
            initial=event['initial_status']['physical']['tick']
            runs[run_id]={'run':run_id,'life':event['life'],'initial_tick':initial,'material_tick_sum':0,'start_line':line,'closed':False}
            last_by_run[run_id]=initial
        elif kind=='MATERIAL_REQUEST':
            key=(event['life'],event['id'])
            if key in seen:
                duplicates.append({'life':key[0],'id':key[1],'line':line,'first_line':seen[key]})
                continue
            seen[key]=line
            parts=PureWindowsPath(event['record'])
            if parts.is_absolute()or parts.drive or'..'in parts.parts:raise ValueError('Unsafe primary path')
            p=root.joinpath(*parts.parts)
            if p.is_symlink()or getattr(p.stat(),'st_file_attributes',0)&1024:raise ValueError('Primary reparse/link')
            b=p.read_bytes();h=sha(b)
            if h!=event['sha256']:errors.append('Primary identity:'+event['id'])
            primary=json.loads(b.decode('utf-8-sig'))
            if primary['id']!=event['id']:errors.append('Primary ID:'+event['id'])
            before=after=None;source='primary result'
            if primary.get('result')is not None:
                result=json.loads(primary['result'])if isinstance(primary['result'],str)else primary['result']
                before=result.get('before_tick');after=result.get('after_tick')
            elif primary.get('error')is not None:
                failure=json.loads(primary['error'])if isinstance(primary['error'],str)else primary['error']
                after=failure.get('native_tick_after_attempt')
                before=last_by_run.get(run_id)
                source='preserved failure after_tick plus preceding own-run primary/startup boundary'
                preserved=failure.get('failed_native_future_preserved',{}).get('physical',{})
                if preserved.get('tick')!=after:errors.append('Failed future boundary:'+event['id'])
            if not isinstance(before,int)or not isinstance(after,int)or after<before:
                errors.append('Unresolved/nonmonotonic Native interval:'+event['id']);delta=None
            else:
                delta=after-before;perlife[event['life']]+=delta
                if run_id in runs:runs[run_id]['material_tick_sum']+=delta
                if run_id in last_by_run and before!=last_by_run[run_id]:errors.append('Gap/overlap in own run:'+event['id'])
                last_by_run[run_id]=after
                for k,v in [('before_tick',before),('after_tick',after)]:
                    if event.get(k)is not None and event[k]!=v:errors.append('Ledger/primary '+k+':'+event['id'])
            requests.append({'line':line,'life':event['life'],'id':event['id'],'run':run_id,'status':primary['status'],'record':event['record'],'record_bytes':len(b),'record_sha256':h,'before_tick':before,'after_tick':after,'new_ticks':delta,'boundary_source':source,'failed_preserved':primary['status']=='failed_preserved'})
        elif kind=='OWNER_CLOSED'and run_id in runs:
            close=event['final_status']['physical']['tick'];r=runs[run_id]
            r.update(closed=True,final_tick=close,total_owner_interval=close-r['initial_tick'],close_line=line)
            r['unrepresented_owner_ticks']=r['total_owner_interval']-r['material_tick_sum']
            if r['unrepresented_owner_ticks']!=0:errors.append('Unrepresented or double-counted owner interval:'+run_id)
    total=sum(perlife.values());unclosed=[x for x in runs.values()if not x['closed']]
    reserved_done=sum(x['new_ticks']or 0 for x in requests if x['id'].startswith('PI02_R04_RES_')and x['id'].endswith('_TIME'))
    reserved_remaining=max(0,reserved_batch_total-reserved_done)if reserved_batch_total else 0
    effective_planned=planned+reserved_remaining
    if reserved_batch_total and reserved_done>reserved_batch_total:errors.append('Recorded reserved batch already exceeds its planned total')
    result={'schema':'PI02.canonical_native_tick_budget.v1','calculated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ledger':str(ledger),'ledger_prefix_bytes':len(prefix),'ledger_prefix_sha256':sha(prefix),'complete_prefix_lines':len(lines),'incomplete_trailing_bytes_ignored':len(data)-len(prefix),'new_ticks_by_this_recalculation':0,'DEE_imports':0,
            'counting_rule':'Sum nonnegative primary after-before exactly once per life/request ID. Related clones count actual separate Native executions, never inherited ages, aliases, wall CPU seconds, deterministic record recalculations or inherited idle_ticks.',
            'canonical_material_requests':len(requests),'duplicate_material_aliases_excluded':duplicates,'by_life':[{'life':k,'new_native_ticks':v,'requests':sum(x['life']==k for x in requests),'failed_preserved_requests':sum(x['life']==k and x['failed_preserved']for x in requests)}for k,v in sorted(perlife.items())],
            'material_requests':requests,'own_runs':list(runs.values()),'observed_request_native_ticks_total':total,
            'failed_preserved_native_ticks':sum(x['new_ticks']or 0 for x in requests if x['failed_preserved']),
            'limit':limit,'remaining_after_observed':limit-total,'planned_extra_outside_reserved_batch':planned,'reserved_batch_total_planned':reserved_batch_total,'reserved_batch_ticks_already_in_observed_total':reserved_done,'reserved_batch_ticks_remaining_to_plan':reserved_remaining,'planned_additional_ticks':effective_planned,'after_observed_and_planned':total+effective_planned,'remaining_after_observed_and_planned':limit-total-effective_planned,
            'unclosed_runs':unclosed,'inconsistencies':errors,
            'budget_guard_all_recorded_runs_closed_and_within_limit':not errors and not unclosed and total+effective_planned<=limit,
            'limits':['Snapshot of completed ledger prefix, not an instantaneous observation of a live owner','An unclosed run may already have advanced before its final material receipt is logged; do not certify an exact remaining budget while it runs','Any subsequent Native development/panel/continuation must be added before the reserved batch; rerun this passive tally only, not the experiments']}
    return result
def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--campaign',type=Path,required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--planned',type=int,default=0);a.add_argument('--reserved-batch-total',type=int,default=0);a.add_argument('--limit',type=int,default=100000);a.add_argument('--strict',action='store_true');args=a.parse_args();r=run(args.campaign,args.planned,args.limit,args.reserved_batch_total);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:r[k]for k in('canonical_material_requests','observed_request_native_ticks_total','failed_preserved_native_ticks','remaining_after_observed','reserved_batch_ticks_already_in_observed_total','reserved_batch_ticks_remaining_to_plan','planned_additional_ticks','remaining_after_observed_and_planned','budget_guard_all_recorded_runs_closed_and_within_limit','unclosed_runs','inconsistencies')},ensure_ascii=False,indent=2));return 2 if args.strict and r['inconsistencies']else 0
if __name__=='__main__':sys.exit(main())
