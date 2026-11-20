"""Fixed-codec native associative stream. Evaluator is never read here.

The experiment transports opaque symbols and the current observed physical
consequence. It does not select an answer, edit memory or inspect a target.
"""
import argparse,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,identity,put,sha,record,receipt,digest,operational,until,local_context

def run(stream_path,out,revision_method=None):
    from repertoire_reference import CapacitySession,memory,normalized_op
    stream_path=Path(stream_path);data=json.loads(stream_path.read_text(encoding='utf-8'))
    out=Path(out);out.mkdir(parents=True,exist_ok=False);start=time.monotonic();engine=identity()
    if data['task']!='DIRECT':raise ValueError('Only frozen direct association codec in this native comparator')
    case={'N':67,'K':len(data['interface']['forms']),'plane_gap':2,'translation':[0,0,0]}
    if revision_method:
        from update_methods import UpdateSession
        if revision_method not in ('double_teacher','symmetric_counterflow'):raise ValueError('Unknown revision protocol')
        session=UpdateSession.create(case)
    else:session=CapacitySession.create(case)
    w=session.world
    byname={f['name']:f for f in session.spec['forms']}
    rows=[];lessons=[];contexts=[];snapshots=[];costs=[]
    put(out/'CONFIG.json',{'schema':'CPC7.native_direct.config.v1','input_sha256':sha(stream_path),
        'engine':engine,'preparation':session.spec,'source_sha256':sha(__file__),
        'decoder':'Applied query, active semantic1, s_reg>input, exact(-1,±1,0); no expected class read',
        'updates':revision_method or 'Identical cue+currently observed event codec at every experience; no memory reset or compensating policy',
        'scope':'Fixed-interface selective access by explicit requested form. Routing is not learned context selection.'})
    def save(name):snapshots.append(session.save(out/(name+'.deetsnap')))
    save('INITIAL_T0')
    revisions=[e for e in data['stream'] if e['operation']=='experience' and e['block'].startswith('B2_')]
    if revision_method and any(e['stimulus']['form_id']!='L01' for e in revisions):raise ValueError('This revision candidate supports only explicit L01 teaching interface')
    auxiliary_times={e['tick']-4 for e in revisions} if revision_method=='symmetric_counterflow' else set()
    times=sorted({int(e['tick']) for e in data['stream']}|auxiliary_times)
    for tick in times:
        t=time.perf_counter();until(w,tick)
        events=[e for e in data['stream'] if e['tick']==tick];pending=[]
        if tick in auxiliary_times:
            for name in ('plus','minus'):session.submit_named('revision.counter.'+name,0,tick)
        for e in events:
            f=e['stimulus']['form_id']
            if e['stimulus']['context_id']!=0:raise ValueError('Context planes require separately validated codec')
            if e['operation']=='experience':
                ids=[]
                if e['teacher_present']:
                    sign=e['observed_consequence']
                    if sign not in(-1,1):raise ValueError('Current sensor outside fixed directional codec')
                    ids.append(session.submit(f,'event.'+('plus' if sign==1 else 'minus'),e['teacher_payload'],e['teacher_tick']))
                ids.append(session.submit(f,'signal',e['signal_payload'],tick))
                if revision_method=='double_teacher' and e in revisions:
                    if e['teacher_present']:ids.append(session.submit_named('revision.teacher2.'+('plus' if e['observed_consequence']==1 else 'minus'),e['teacher_payload'],e['teacher_tick']))
                pending.append((e,ids))
            elif e['operation']=='query':
                identifier=session.submit(f,'signal',e['query_payload'],tick,True);pending.append((e,[identifier]))
            else:raise ValueError('Unknown observable operation')
        until(w,tick+2)
        for e,ids in pending[:2]:contexts.append({'event_id':e['event_id'],'tick':tick+2,'neighborhood':local_context(w,byname[e['stimulus']['form_id']]['hub'])})
        until(w,tick+max(3,max((e.get('teacher_tick',tick)-tick+3 for e in events),default=3)))
        for e,ids in pending:
            f=byname[e['stimulus']['form_id']];p=record(w,f['hub'])
            if e['operation']=='query':
                r=receipt(w,ids[0]);valid=(r['status']=='applied' and p['active'] and p['semantic']==1 and p['s_reg']>e['query_payload'] and p['direction'] in ([-1,1,0],[-1,-1,0]))
                rows.append({'event_id':e['event_id'],'block':e['block'],'stimulus':e['stimulus'],'input_tick':tick,'tick':int(w.runtime.current_tick),
                    'physical':p,'receipt':r,'response':p['direction'][1] if valid else None,'coverage':valid,'provenance':'ENTE'})
            else:lessons.append({'event_id':e['event_id'],'block':e['block'],'tick':int(w.runtime.current_tick),'stimulus':e['stimulus'],
                                 'physical_after':p,'receipts':[receipt(w,i) for i in ids]})
        costs.append({'input_tick':tick,'events':len(events),'wall_seconds':time.perf_counter()-t})
        save('T'+str(w.runtime.current_tick))
        put(out/'PROGRESS.json',{'last_complete_tick':int(w.runtime.current_tick),'responses':rows,'lessons':lessons,'checkpoints':snapshots})
    result={'schema':'CPC7.native_direct.measurements.v1','case_id':data['case_id'],'engine':engine,'input_sha256':sha(stream_path),
       'code_sha256':sha(__file__),'preparations':1,'diagnostic_forks':0,'continuations':0,'same_RUNTIME':True,'N':67,'backend':'LAZY',
       'geometry':session.spec,'revision_method':revision_method,'responses':rows,'lessons':lessons,'calls':session.state['calls'],
       'receipts':[receipt(w,c['id']) for c in session.state['calls']],'local_windows':contexts,'costs':costs,
       'final_physical':digest(w),'final_operational':normalized_op(w),'checkpoints':snapshots,
       'resources':{'basic_buffers_bytes':32*67**3,'initial_material_sites':0,'interfaces':len(w.runtime.channel_names),**memory()},
       'elapsed_seconds':time.monotonic()-start,'host_RAW_clock_writes_after_T0':[],'evaluation_reads_targets':False}
    put(out/'MEASUREMENTS.json',result)
    print(json.dumps({'case_id':data['case_id'],'queries':len(rows),'valid':sum(r['coverage'] for r in rows),'seconds':result['elapsed_seconds']}),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stream',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--revision-method',choices=['double_teacher','symmetric_counterflow']);a=p.parse_args();run(a.stream,a.out,a.revision_method)
