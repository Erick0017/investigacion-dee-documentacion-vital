"""Load-only counter cuts preserve supports; explicit auditor diagnostic forks."""
import argparse,hashlib,json,sys,time
from copy import deepcopy
from pathlib import Path
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE));sys.path.insert(0,str(BASE/'src'))
from content_reflection import ContentReflectionSession
from integracion.quantity_core import move
from dee_thinking import _native as d
from run_action_trace import digest

def main():
    p=argparse.ArgumentParser();p.add_argument('--parents',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    parents=Path(a.parents);out=Path(a.out);out.mkdir(parents=True,exist_ok=False);ids=[]
    for cid in ('RR_P01_PLUS','RR_P02_MINUS'):
        refpath=parents/(cid+'.json');reference=json.loads(refpath.read_text(encoding='utf-8'));snapshot=parents/(cid+'_72.snapshot.gz')
        for mode in ('cut_counterload','sham','restore'):
            started=time.monotonic();parent=ContentReflectionSession.load(snapshot);parent.run_until(81);before=digest(parent);interventions=[]
            if mode=='restore':s=parent
            else:
                edits=[]
                for point in parent.geometry['reflection_sites']:
                    q=point['actual_reflector'];o=parent.observe(q);e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q)
                    e.raw=d.pack_record(o['state'],0,*o['direction'],o['semantic']) if mode=='cut_counterload' else int(o['raw'])
                    e.label='AUDITOR_'+mode.upper();edits.append(e);interventions.append({'site':q,'before':o,'after_requested_RAW':str(e.raw),'clock_edit':None})
                s=ContentReflectionSession(parent.world.diagnostic_fork(edits,True),parent.geometry,deepcopy(parent.state))
            frames=[];predictions=[]
            for point in s.geometry['reflection_sites']:
                q=point['site'];pre=s.observe(q);hood=[s.observe(move(q,(x,y,z))) for x in (-1,0,1) for y in (-1,0,1) for z in (-1,0,1) if (x,y,z)!=(0,0,0)]
                gradient=[0,0,0]
                for o in hood:
                    if o['state']:
                        offsets=[(o['site'][i]-q[i]+33)%67-33 for i in range(3)]
                        for i in range(3):gradient[i]-=offsets[i]*o['s_reg']
                direction=[(v>0)-(v<0) for v in gradient]
                # This explicit physical prediction is recorded before advance.
                # It is tested only for an observed active normal c7 input and
                # seven zero-direction live neighbors (no tetrahedral pattern).
                active=[o for o in hood if o['state'] and o['semantic']!=5]
                branch_qualified=pre['active'] and pre['semantic']==1 and pre['s_reg']==7 and len(active)==7 and all(o['direction']==[0,0,0] for o in active)
                predictions.append({'site':q,'pre':pre,'Moore26':hood,'gradient':gradient,'n_active':len(active),
                                    'branch_qualified':branch_qualified,'predicted_RAW_before_step':str(d.pack_record(1,7,*direction,1)) if branch_qualified else None})
            for tick in (81,82,83,84,110,113,138,139,140,147,148,149,177,180,205,206,207):s.run_until(tick);frames.append(s.capture())
            post82=next(f for f in frames if f['tick']==82)
            for prediction in predictions:
                post=next(p['material'] for p in post82['reflection'] if p['material']['site']==prediction['site'])
                prediction['post']=post;prediction['raw_exact_match']=prediction['branch_qualified'] and prediction['predicted_RAW_before_step']==post['raw']
                prediction['clock_exact_match']=int(prediction['pre']['clock'])+1==int(post['clock'])
            row={'id':cid+'_'+mode,'mode':mode,'parent_case':cid,'modality':'CROSS_PROCESS_CONTINUATION' if mode=='restore' else'DIAGNOSTIC_FORK',
                 'geometry':s.geometry,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 'parent_primary_sha256':hashlib.sha256(refpath.read_bytes()).hexdigest(),'parent_snapshot_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),
                 'frames':frames,'predictions_before_82':predictions,'interventions':interventions,'new_inputs':[],
                 'receipts':s.receipts(),'terminal_state':digest(s),'parent_unchanged':mode=='restore' or digest(parent)==before,
                 'full_state_equal_reference':digest(s)==reference['terminal_state'],'receipts_equal_reference':s.receipts()==reference['receipts'],
                 'elapsed_seconds':time.monotonic()-started}
            (out/(row['id']+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8');ids.append(row['id']);print(row['id'],flush=True)
            if mode in ('sham','restore') and not(row['full_state_equal_reference'] and row['receipts_equal_reference']):raise AssertionError('Exact sham/restore mismatch')
    (out/'BATCH.json').write_text(json.dumps({'cases':ids,'preparations':0,'forks':4,'continuations':2},ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
