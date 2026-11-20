"""Common task scoring AFTER native or conventional trajectories are sealed.

This auditor never runs a participant, chooses a physical branch or replaces a
missing output with a class. IDs join a declared query to its result; the full
observable stimulus must also match. No source physics is decoded here.
"""
from __future__ import annotations
import argparse,collections,hashlib,json
from pathlib import Path


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def tally(rows):
    executed=[r for r in rows if r['measured']];valid=[r for r in executed if r['response'] is not None]
    return {'planned_queries':len(rows),'measured_queries':len(executed),'valid_responses':len(valid),
        'correct':sum(r['correct'] is True for r in rows),'absent_or_invalid':sum(r['measured'] and r['response'] is None for r in rows),
        'not_measured':len(rows)-len(executed),'accuracy_all_measured':sum(r['correct'] is True for r in executed)/len(executed) if executed else None,
        'accuracy_valid_only':sum(r['correct'] is True for r in valid)/len(valid) if valid else None,
        'coverage_among_measured':len(valid)/len(executed) if executed else None,
        'status_counts':dict(collections.Counter(r['state'] for r in rows))}


def evaluate_file(measurements_path,stream_path,evaluator_path):
    m=read(measurements_path);visible=read(stream_path);truth=read(evaluator_path)
    stream_hash=sha(stream_path);claimed=m.get('input_sha256',m.get('stream_sha256'))
    if claimed!=stream_hash:raise ValueError('Trajectory did not use this exact public stream')
    planned={e['event_id']:e for e in visible['stream'] if e['operation']=='query'}
    target={q['event_id']:q for q in truth['queries']}
    if set(target)!=set(planned):raise ValueError('Evaluator queries differ from observable stream')
    if m.get('schema')=='CPC7.native_direct.measurements.v1':
        native=True;outputs=m['responses'];model='DEE4_NATIVE_FIXED_CODEC'
    elif m.get('schema')=='CPC7.comparator.trajectory.v1':
        native=False;outputs=[r for r in m['rows'] if r['operation']=='query'];model=m['model']
    else:raise ValueError('Unregistered primary schema; no guessed decoder')
    byid={}
    for row in outputs:
        eid=row['event_id']
        if eid in byid or eid not in planned:raise ValueError('Duplicate or unplanned result query')
        stimulus=row['stimulus'] if native else row['observable_stimulus']
        if stimulus!=planned[eid]['stimulus']:raise ValueError('Result ID matches but observable stimulus differs')
        byid[eid]=row
    scored=[]
    for eid,event in planned.items():
        row=byid.get(eid);response=None;admission=None
        if row is None:state='NOT_MEASURED'
        else:
            raw=row.get('response')
            if native:
                admission=row['receipt']['status']
                if row.get('coverage') is True and type(raw) is int and raw in(-1,1):response=raw;state='RESPONSE'
                elif admission!='applied':state='INPUT_'+admission.upper()
                else:state='NO_VALID_RESPONSE_IN_FIXED_DECODER'
            else:
                admission='admitted' if row.get('admitted') else 'not_admitted';state=row['state']
                if type(raw) is int and raw in(-1,1):response=raw
                elif raw is not None:raise ValueError('Conventional response outside declared classes')
        scored.append({'event_id':eid,'block':event['block'],'stimulus':event['stimulus'],
             'response':response,'state':state,'admission':admission,'measured':row is not None,
             'expected_evaluator_only':target[eid]['expected'],
             'correct':response==target[eid]['expected'] if row is not None else None,
             'relation_index':target[eid].get('relation_index')})
    panels={block:tally([r for r in scored if r['block']==block]) for block in dict.fromkeys(r['block'] for r in scored)}
    r=m['resources'];wall=m.get('elapsed_seconds',r.get('wall_seconds'));cpu=r.get('cpu_seconds')
    if native:rss=r.get('peak_working_set_bytes') if r.get('available') else None
    else:rss=r['final_memory'].get('peak_working_set_bytes') if r['final_memory'].get('measured') else None
    resource={'wall_seconds':wall,'cpu_seconds':cpu,'peak_process_working_set_bytes':rss,
        'wall_limit_seconds':120,'rss_limit_bytes':256*1024**2,
        'exceeds_wall_limit':wall>120 if wall is not None else None,
        'exceeds_rss_limit':rss>256*1024**2 if rss is not None else None,
        'within_both_measured_limits':wall<=120 and rss<=256*1024**2 if wall is not None and rss is not None else None,
        'scope':'Source-reported whole trajectory includes preparation/initialization and checkpoint persistence; excludes final result-file write, post-hoc scoring, process launch and module imports. Native capture/physics and conventional model arithmetic are different workloads; limits are eligibility bounds, not equal computation.'}
    return {'schema':'CPC7.common.evaluation.v1','case_id':visible['case_id'],'task':visible['task'],'mode':visible['mode'],
        'model':model,'primary_sha256':sha(measurements_path),'stream_sha256':stream_hash,'evaluator_sha256':sha(evaluator_path),
        'query_response_classes':[-1,1],'evaluation_after_persisted_trajectory':True,'performance':tally(scored),
        'panels':panels,'retention':{
          'old8_after_new8':tally([r for r in scored if r['block']=='Q1_RETAIN_8_ADD_8' and r['relation_index'] is not None and r['relation_index']<8]),
          'revised_L01':tally([r for r in scored if r['block']=='Q2_REVISED_AND_RETAINED' and r['relation_index']==0]),
          'other15_after_revision':tally([r for r in scored if r['block']=='Q2_REVISED_AND_RETAINED' and r['relation_index'] is not None and r['relation_index']!=0])},
        'resources_common_bounds':resource,'queries':scored,
        'provenance':'External auditor, not a participant response. No physics, mapping or alternative decoder was computed to fill an absence.'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--measurements',type=Path,required=True);p.add_argument('--stream',type=Path,required=True)
    p.add_argument('--evaluator',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    value=evaluate_file(a.measurements,a.stream,a.evaluator)
    if a.out.exists():raise FileExistsError(a.out)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'case_id':value['case_id'],'performance':value['performance']}))


if __name__=='__main__':main()
