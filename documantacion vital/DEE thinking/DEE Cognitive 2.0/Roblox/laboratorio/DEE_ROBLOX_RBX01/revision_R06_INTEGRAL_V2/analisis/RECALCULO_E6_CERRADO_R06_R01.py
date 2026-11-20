"""Portable passive E6: closed load-stage results, same CTRL1 episode and ledger.
No Native/SQLite/Studio/model. Reads only explicit files, not their original paths.
"""
from pathlib import Path
import argparse,csv,hashlib,json,datetime
def read(path,sources):
    p=Path(path).resolve(strict=True);before=p.stat();raw=p.read_bytes();after=p.stat()
    if len(raw)>2_000_000 or(before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise ValueError('BOUNDED_FROZEN_INPUT_REQUIRED')
    for q in(p,*p.parents):
        if q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024:raise ValueError('LINK_REFUSED')
    sources.append({'path':str(p),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()});return json.loads(raw.decode('utf-8-sig'))
def classify(tool):
    numeric=tool.get('kind')=='CALCULATE';actual=tool.get('numeric_result');formed=numeric and type(actual)is int and tool.get('formed')is not False
    return {'numeric_opportunity':numeric,'integer_formed':formed,'valid_zero':formed and actual==0,'numeric_NULL_or_absent':numeric and type(actual)is not int,
        'memory_value':tool.get('memory_value'),'actual_operation':tool.get('operation'),'numeric_result':actual,
        'capability_execution_admitted':tool.get('capability_execution_admitted'),'reason':tool.get('reason'),
        'partial_lesson':tool.get('kind')=='LESSON'and(tool.get('capability_execution_admitted')is False or tool.get('reason')=='NATIVE_PARTIAL_ADMISSION')}
def main(a):
    output=Path(a.output)
    if output.exists()or not output.parent.is_dir():raise ValueError('NEW_OUTPUT_REQUIRED')
    sources=[];stages=[];rows=[]
    for path in a.stage:
        value=read(path,sources);stage=value['stage'];n=0
        for owner in value['owners']:
            result=owner['result']
            if not result or result['closed']is not True or result['pending_global_intent']is not None:raise ValueError('CLOSED_LOAD_OWNER_REQUIRED')
            for row in result['results']:
                tool=row.get('public_tool_result')or{};request=row.get('tool')or{}
                rows.append({'stage':stage,'profile':owner['profile'],'life':result['life'],'index':row['index'],
                    'q1_action':row['q1']['name'],'q1_NULL':row['q1']['null'],'route_observed':row['actual_final_action']['name'],
                    'route_executed_in_Roblox':False,'request_kind':request.get('kind'),'request_slot':request.get('slot'),'request_form':request.get('form'),
                    'left':request.get('left'),'right':request.get('right'),'native_tick_after':row['native_tick'],**classify(tool)})
                n+=1
        stages.append({'stage':stage,'status':value['status'],'abort_reason':value.get('abort_reason'),'owners':len(value['owners']),
            'completed_episodes':n,'owner_lifetime_overlap_seconds':value['owner_lifetime_common_overlap_seconds'],
            'material_concurrent_task_execution_supported':len(value['owners'])if value['status']=='ALL_DECLARED_LIVES_CLOSED_AND_COMPLETE'and n else 0})
    control=read(a.ctrl_result,sources);world=read(a.ctrl_world,sources);ledger=read(a.ledger,sources)
    if control['owner_closed']is not True or control['status']!='ONE_ORIGINAL_EPISODE_CLOSED' or control['failure']is not None:raise ValueError('CLOSED_CTRL_EPISODE_REQUIRED')
    if ledger['intents']or ledger['consumed']!=sum(x['consumed']for x in ledger['worlds'].values()):raise ValueError('RECONCILED_LEDGER_REQUIRED')
    if world['state']['phase']!='BOUNDARY'or world['state']['completedOpportunities']!=1:raise ValueError('MODULE_CLOSED_BOUNDARY_REQUIRED')
    report={'schema':'DEE.INTEGRAL.V2.E6_passive_recalc.R01','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'stages':sorted(stages,key=lambda x:x['stage']),'load_episode_rows':rows,
        'load_numeric_opportunities':sum(x['numeric_opportunity']for x in rows),'load_integers_formed':sum(x['integer_formed']for x in rows),
        'load_numeric_NULL_or_absent':sum(x['numeric_NULL_or_absent']for x in rows),'load_partial_lessons':sum(x['partial_lesson']for x in rows),
        'CTRL1':{'life':control['life'],'source_tick':control['parent_episode_tick'],'final_tick':control['last_confirmed_tick'],
            'new_ticks_whole_original_episode':control['full_episode_ticks'],'new_ticks_resume_only':control['new_ticks_this_continuation'],
            'Q1_original':control['original_q1'],'Q2_feedback_new':control['new_native_outputs'],'body_ACKs':control['body_acks'],
            'Q1_reexecuted':False,'module_cursor':world['state']['actionCursor'],'module_completed':world['state']['completedOpportunities']},
        'global_ticks_actual':ledger['consumed'],'global_intents':ledger['intents'],'per_life_ledger':ledger['worlds'],
        'Native_SQLite_Studio_model_calls':0,'sources':sources,
        'limits':['Load routes are Native selectors observed in a focal process test, not executed Roblox movement.',
            'Prepared arithmetic is not a learned arithmetic algorithm. Partial lesson admission is not full acquisition.',
            'Stage3 owner runtime overlap withoutGO/episodes is not three simultaneously processing task lives.',
            'CTRL1 is one continuation of DEV4, not MAIN memory integration or a new independent replicate.',
            'Same originalQ1 was delivered after known unadmitted World message; no recomputedQ1 or automatic ambiguous retry.',
            'Snapshot/moduleWorld alone is not a complete Native backup. No generic-agency or learned-control claim is inferred.']}
    output.mkdir()
    (output/'E6_HECHOS_RECALCULADOS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with(output/'CARGA_EPISODIOS_R06.csv').open('w',encoding='utf-8-sig',newline='')as f:
        fields=list(dict.fromkeys(k for r in rows for k in r));w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',action='append',type=Path,required=True);p.add_argument('--ctrl-result',type=Path,required=True)
    p.add_argument('--ctrl-world',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=main(a);print(json.dumps({k:r[k]for k in('stages','load_numeric_opportunities','load_integers_formed','load_numeric_NULL_or_absent','load_partial_lessons','global_ticks_actual')},ensure_ascii=False,indent=2))
