"""Finite new controls of integrated U0, not another independent architecture.

Normal histories reuse life.run. Diagnostic edits operate only on complete
forks of a named saved U0 boundary. They never feed information back to MAIN.
"""
from pathlib import Path
import argparse,json,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,identity,digest,record,receipt,operational,local_context
from integrated import Session
import life,action_feedback


def diagnostic(case,out):
    import dee_thinking as d
    out=Path(out);out.mkdir(parents=True,exist_ok=False);start=time.monotonic();engine=identity()
    parent_dir=ROOT/case['parent_case'];source=parent_dir/case['checkpoint'];parent=Session.load(source)
    g=parent.geometry['adapter'];tick=int(parent.world.runtime.current_tick)
    target=case['target'];key=case.get('branch','right.mismatch')
    if target=='forecast':site=parent.geometry['body']['emission_site']
    elif target in ('source_Q','source_P'):
        source_name=target[-1];value='negative' if source_name=='Q' else 'positive'
        part=g['source_codecs'][key+'.'+source_name+'.'+value][0]
        site=action_feedback.moved(part['hub'],part['direction'],tick-3)
    elif target=='information':site=g['branches'][key]['sources']['Q']['information_site']
    else:raise ValueError('Unregistered diagnostic target')
    before=record(parent.world,site);parent_pre=digest(parent.world);operative_pre=operational(parent.world)
    edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.label=case['id']
    operation=case['operation']
    if operation=='raw_cut':edit.raw=0
    elif operation=='reverse_direction':
        dr=before['direction'];edit.raw=d.pack_record(before['state'],before['s_reg'],-dr[0],dr[1],dr[2],before['semantic'])
    elif operation=='reverse_z':
        dr=before['direction'];edit.raw=d.pack_record(before['state'],before['s_reg'],dr[0],dr[1],-dr[2],before['semantic'])
    elif operation=='sham_exact':edit.raw=int(before['raw'])
    else:raise ValueError('Unregistered intervention')
    fork_world=parent.world.diagnostic_fork([edit],True)
    fork=Session(fork_world,parent.geometry,parent.requests,case['id'])
    post=record(fork.world,site);rows=[];windows=[{'tick':tick,'pre_parent':local_context(parent.world,site),'post_fork':local_context(fork.world,site)}]
    put(out/'CONFIG.json',{'case':case,'source_sha256':sha(__file__),'life_sha256':sha(life.__file__),
        'action_feedback_sha256':sha(action_feedback.__file__),'parent_checkpoint_sha256':sha(source),
        'intervention':{'site':site,'before':before,'after':post,'field':'RAW only, clock preserved','mode':'DIAGNOSTIC_FORK'},
        'frozen_criterion':'Native selections20, information23, later physicalquery33 on all fixed candidates. Source/P cut is sham of unused but acquired same-load source; cuts never return to MAIN.'})
    snap_before=fork.save(out/'POST_DIAGNOSTIC_BOUNDARY.deetsnap')
    for t in range(tick,41):
        fork.advance_to(t);rows.append({'tick':t,'adapter':action_feedback.capture(fork.world,g)})
        if t in (14,15,19,20,22,23,32,33):windows.append({'tick':t,'edited_trajectory_context':local_context(fork.world,site)})
        if t in (20,23,33,40):put(out/'INCREMENTAL.json',{'last_tick':t,'rows':rows})
    summary=life.summarize(rows,g)
    snap_after=fork.save(out/'FINAL_T40.deetsnap')
    parent_post=digest(parent.world);operative_post=operational(parent.world)
    assert parent_pre==parent_post and operative_pre==operative_post,'Diagnostic branch mutated loaded parent'
    result={'schema':'CPC6.U0.diagnostic.v1','case':case,'engine':engine,'source_sha256':sha(__file__),
       'parent_checkpoint':str(source.relative_to(ROOT)),'parent_checkpoint_sha256':sha(source),
       'pre_parent':parent_pre,'post_parent':parent_post,'parent_operative_unchanged':operative_pre==operative_post,
       'intervention':{'site':site,'before':before,'after':post,'raw_written':str(edit.raw),'clock_written':None,'mode':'DIAGNOSTIC_FORK'},
       'summary':summary,'rows':rows,'local_windows':windows,'snapshots':[snap_before,snap_after],
       'requests':fork.receipts(),'final_physical':digest(fork.world),'final_operative':operational(fork.world),
       'status':'MEASURED','preparations':0,'diagnostic_forks':1,'continuations':1,
       'coverage':'All fixed candidate fields everytick; pre/post Moore27 around edit. Genealogy not inferred outside captured windows.',
       'elapsed_seconds':time.monotonic()-start}
    put(out/'MEASUREMENTS.json',result);print(json.dumps({'id':case['id'],'before':before,'summary':summary}),flush=True)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    cfg=json.loads(a.config.read_text(encoding='utf-8'));a.out.mkdir(parents=True,exist_ok=True);index=[]
    for case in cfg['cases']:
        target=a.out/case['id']
        if (target/'MEASUREMENTS.json').exists():r=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf-8'))
        elif case.get('mode')=='diagnostic':r=diagnostic(case,target)
        else:r=life.run(case,target)
        index.append({'id':case['id'],'summary':r['summary'],'evidence':str((target/'MEASUREMENTS.json').relative_to(ROOT))})
        put(a.out/'INDEX.json',index)


if __name__=='__main__':main()
