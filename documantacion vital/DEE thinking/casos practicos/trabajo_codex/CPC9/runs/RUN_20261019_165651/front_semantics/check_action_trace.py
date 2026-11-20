"""Explicit diagnostic trace/feedback cuts after the common consequence.

No fork is returned to MAIN.  Sham and separate-process snapshot continuation
must be exact at full RAW/clocks and neutral receipt level.
"""
import argparse,hashlib,json,sys,time
from copy import deepcopy
from pathlib import Path
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE));sys.path.insert(0,str(BASE/'src'))
from action_trace import ActionTraceSession
from dee_thinking import _native as d
from run_action_trace import digest

def main():
    p=argparse.ArgumentParser();p.add_argument('--parents',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    parents=Path(a.parents);out=Path(a.out);out.mkdir(parents=True,exist_ok=False);records=[]
    for case_id in ('AV2_P01_A','AV2_P02_B'):
        refpath=parents/(case_id+'.json');reference=json.loads(refpath.read_text(encoding='utf-8'));actor=reference['case']['actor']
        snapshot=parents/(case_id+'_11.snapshot.gz')
        for mode in ('cut_own','cut_consequence','sham','restore'):
            started=time.monotonic();parent=ActionTraceSession.load(snapshot);before=digest(parent)
            interventions=[]
            if mode=='restore':s=parent
            else:
                key='C' if mode=='cut_consequence' else actor;q=parent.geometry['sites'][key];observation=parent.observe(q)
                e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=int(observation['raw']) if mode=='sham' else 0
                e.label='AUDITOR_ONLY_'+mode.upper();w=parent.world.diagnostic_fork([e],True)
                s=ActionTraceSession(w,parent.geometry,deepcopy(parent.state))
                interventions=[{'site':q,'before':observation,'requested_RAW':str(e.raw),'clock_edit':None}]
            frames=[]
            for tick in (11,15,16,17,30,31,32):s.run_until(tick);frames.append(s.capture())
            data={'id':case_id+'_'+mode,'parent_case':case_id,'modality':'DIAGNOSTIC_FORK' if mode!='restore' else 'CROSS_PROCESS_CONTINUATION',
                  'mode':mode,'parent_snapshot_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),
                  'parent_primary_sha256':hashlib.sha256(refpath.read_bytes()).hexdigest(),
                  'geometry':s.geometry,'frames':frames,'interventions':interventions,'new_inputs':[],
                  'terminal_state':digest(s),'receipts':s.receipts(),'parent_before':before,
                  'parent_unchanged':mode=='restore' or before==digest(parent),
                  'full_state_equal_parent_reference':digest(s)==reference['terminal_state'],
                  'receipts_equal_parent_reference':s.receipts()==reference['receipts'],
                  'elapsed_seconds':time.monotonic()-started}
            (out/(data['id']+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');records.append(data['id'])
            if mode in ('sham','restore') and not(data['full_state_equal_parent_reference'] and data['receipts_equal_parent_reference']):raise AssertionError('Exact sham/restore mismatch')
            print(data['id'],flush=True)
    (out/'BATCH.json').write_text(json.dumps({'cases':records,'preparations':0,'forks':6,'continuations':2},ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
