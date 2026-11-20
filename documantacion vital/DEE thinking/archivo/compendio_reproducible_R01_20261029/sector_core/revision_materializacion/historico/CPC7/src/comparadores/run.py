"""Finite comparator worker; public stream first, evaluation strictly afterward."""
from __future__ import annotations
import argparse, ctypes, hashlib, json, os, platform, sys, time, traceback
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from models import B1,B2,selftest


def put(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise FileExistsError(path)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def process_memory():
    class PMC(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong)]+[(x,ctypes.c_size_t) for x in
            ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage',
             'QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]
    p=PMC();p.cb=ctypes.sizeof(p);kernel=ctypes.WinDLL('kernel32');kernel.GetCurrentProcess.restype=ctypes.c_void_p
    ok=ctypes.WinDLL('psapi').GetProcessMemoryInfo(ctypes.c_void_p(kernel.GetCurrentProcess()),ctypes.byref(p),p.cb)
    return {'peak_working_set_bytes':int(p.PeakWorkingSetSize),'working_set_bytes':int(p.WorkingSetSize),
            'private_bytes':int(p.PrivateUsage),'measured':bool(ok),'scope':'Whole worker process, not parameter storage alone.'}


def participant_step(model,event):
    """No evaluator, case seed, hidden condition or expected answer is passed."""
    stimulus=event['stimulus']
    if event['operation']=='experience':
        paired=event['teacher_present'] and event['teacher_tick']==event['tick']
        if paired:model.observe(stimulus,event['observed_consequence'])
        return {'operation':'experience','admitted':True,'paired_by_fixed_coincidence_contract':paired,
                'consequence_observed':event['observed_consequence'] if event['teacher_present'] else None,
                'model_update':paired}
    if event['operation']=='query':return {'operation':'query','admitted':True,**model.predict(stimulus)}
    raise ValueError('Unknown observable operation')


def trajectory(stream,kind,config,out,resume=None):
    wall=time.perf_counter();cpu=time.process_time();initial=process_memory()
    if resume:
        saved=json.loads(Path(resume).read_text(encoding='utf-8'))
        if saved['stream_sha256']!=sha(stream):raise ValueError('Resume requires exact same observable stream')
        state=saved['model'];model=(B1 if state['kind']==B1.kind else B2).restore(state);start=saved['next_index']
    else:
        visible=json.loads(Path(stream).read_text(encoding='utf-8'));model=B1(visible['interface']) if kind=='B1' else B2(visible['interface'],config);start=0
    visible=json.loads(Path(stream).read_text(encoding='utf-8'));rows=[];block=None;initialization={'wall_seconds':time.perf_counter()-wall,'cpu_seconds':time.process_time()-cpu}
    observed_events=0;query_events=0
    for i,event in enumerate(visible['stream'][start:],start):
        if block is not None and event['block']!=block:
            put(Path(out)/'checkpoints'/f'{i:03d}_AFTER_{block}.json',{'schema':'CPC7.comparator.checkpoint.v1',
                'stream_sha256':sha(stream),'next_index':i,'model':model.state(),'last_event_id':visible['stream'][i-1]['event_id'],
                'scope':'Operational learner state; no evaluator or query targets.'})
        block=event['block'];before=time.perf_counter();c0=time.process_time();observed_events+=event['operation']=='experience';query_events+=event['operation']=='query'
        public={'operation':event['operation'],'stimulus':event['stimulus'],'tick':event['tick']}
        if event['operation']=='experience':public.update(teacher_present=event['teacher_present'],teacher_tick=event['teacher_tick'],observed_consequence=event['observed_consequence'])
        result=participant_step(model,public)
        rows.append({'event_id':event['event_id'],'block':event['block'],'requested_tick':event['tick'],
                     'observable_stimulus':event['stimulus'],**result,'wall_seconds':time.perf_counter()-before,'cpu_seconds':time.process_time()-c0})
    put(Path(out)/'checkpoints'/'FINAL.json',{'schema':'CPC7.comparator.checkpoint.v1','stream_sha256':sha(stream),
        'next_index':len(visible['stream']),'model':model.state(),'scope':'No query targets/evaluator.'})
    summary={'schema':'CPC7.comparator.trajectory.v1','case_id':visible['case_id'],'task':visible['task'],'mode':visible['mode'],
        'model':model.kind,'config':config if kind!='B1' else {'memory_policy':'Last paired observed consequence per observable key'},
        'stream_sha256':sha(stream),'rows':rows,'initialization':initialization,
        'resources':{'wall_seconds':time.perf_counter()-wall,'cpu_seconds':time.process_time()-cpu,'initial_memory':initial,
                     'final_memory':process_memory(),'training_events_seen':observed_events,'queries':query_events,
                     **model.counters,'stored_examples':len(model.buffer) if isinstance(model,B2) else len(model.table),
                     'parameter_scalars':sum(map(len,model.w1))+len(model.b1)+len(model.w2)+1 if isinstance(model,B2) else None},
        'provenance':{'python':platform.python_version(),'implementation':platform.python_implementation(),'architecture':platform.architecture()[0],
             'worker_source_sha256':sha(__file__),'models_source_sha256':sha(Path(__file__).with_name('models.py'))},
        'status':'EXECUTED','resumed_from':str(Path(resume).name) if resume else None,
        'limitations':['Prepared fixed temporal binding for demonstrations.','Pure-Python conventional model, not DEE physics.',
                       'No long-horizon plasticity benchmark; finite retention/adaptation task only.']}
    put(Path(out)/'TRAJECTORY.json',summary);return summary


def evaluate(trajectory_path,evaluator_path,out):
    """Called only after all participant predictions have been persisted."""
    t=json.loads(Path(trajectory_path).read_text(encoding='utf-8'));e=json.loads(Path(evaluator_path).read_text(encoding='utf-8'))
    expected={q['event_id']:q['expected'] for q in e['queries']};rows=[];panels={}
    for row in t['rows']:
        if row['operation']!='query':continue
        truth=expected[row['event_id']];good=row['response']==truth
        item={'event_id':row['event_id'],'block':row['block'],'response':row['response'],'state':row['state'],
              'expected_evaluator_only':truth,'correct':good,'response_present':row['response'] is not None};rows.append(item)
        p=panels.setdefault(row['block'],{'queries':0,'responses':0,'correct':0,'absent':0})
        p['queries']+=1;p['correct']+=good;p['responses']+=row['response'] is not None;p['absent']+=row['response'] is None
    for p in panels.values():p['accuracy']=p['correct']/p['queries'];p['coverage']=p['responses']/p['queries']
    result={'schema':'CPC7.comparator.evaluation.v1','case_id':t['case_id'],'model':t['model'],'task':t['task'],'mode':t['mode'],
        'trajectory_sha256':sha(trajectory_path),'evaluator_sha256':sha(evaluator_path),'panels':panels,'queries':rows,
        'query_targets_were_not_passed_to_participant':True,'score_evaluated_after_trajectory':True}
    put(out,result);return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');p.add_argument('--stream',type=Path);p.add_argument('--evaluator',type=Path)
    p.add_argument('--model',choices=['B1','B2'],default='B1');p.add_argument('--config',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--resume',type=Path)
    a=p.parse_args();started=time.perf_counter();a.out.mkdir(parents=True,exist_ok=False)
    try:
        if a.self_test:result=selftest();put(a.out/'SELFTEST.json',result)
        else:
            cfg=json.loads(a.config.read_text(encoding='utf-8')) if a.config else {}
            trajectory(a.stream,a.model,cfg,a.out,a.resume)
            result=evaluate(a.out/'TRAJECTORY.json',a.evaluator,a.out/'EVALUATION.json') if a.evaluator else {'status':'TRAJECTORY_ONLY'}
        print(json.dumps({'status':'EXECUTED','out':str(a.out),'wall_seconds':time.perf_counter()-started,'panels':result.get('panels',{})}))
    except Exception as exc:
        put(a.out/'ERROR.json',{'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc(),'wall_seconds':time.perf_counter()-started});raise


if __name__=='__main__':main()
