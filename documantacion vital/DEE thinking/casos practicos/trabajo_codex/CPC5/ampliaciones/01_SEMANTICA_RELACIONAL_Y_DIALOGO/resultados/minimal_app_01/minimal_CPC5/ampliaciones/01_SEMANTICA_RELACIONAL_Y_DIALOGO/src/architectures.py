"""Matched physical cluster-spacing screen; finite native messages, not labels.

Twelve acquired mobile components are grouped in 1/2/3/4 spatial clusters.
Actual intercluster gaps, latency, and encounters differ.  Native output travels
across each gap.  Group labels alone confer no integration or renewable body.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import sys,time
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from common import sha,put,identity,record,interface,receipt,digest,operational,until,local_context
from capacity import memory,normalized_op
ROOT=HERE.parent
KEY='cpc5.extension.architectures.v1'


def moved(q,d,t,n):return tuple((q[i]+d[i]*t)%n for i in range(3))


def geometry(case):
    n=case.get('N',127);g=case['groups'];count=case.get('components',12)
    if g not in (1,2,3,4) or count!=12 or n!=127:raise ValueError('Matched domain: twelve components N127,1..4clusters')
    group_size=count//g;tr=case.get('translation',[0,0,0]);stages=[];distance=0;ports=[]
    for i in range(count):
        if i:distance+=case.get('between_gap',11) if i%group_size==0 else 5
        hub=tuple((q+tr[j])%n for j,q in enumerate((110-distance,20,8)))
        t=11+distance;meet=moved(hub,(0,1,0),t-3,n)
        s={'index':i,'compound':i//group_size,'local':i%group_size,'hub':list(hub),'meeting_tick':t,'meeting':list(meet)};stages.append(s)
        for label,dr in (('cue',(-1,0,0)),('report',(1,1,0))):
            ports.append(interface(f'stage{i}.{label}',moved(hub,dr,-3,n),dr))
    ports.append(interface('request',moved(stages[0]['meeting'],(-1,0,0),-5,n),(-1,0,0)))
    final=stages[-1];consequence=moved(final['meeting'],(-1,1,0),3,n)
    ports.append(interface('environment.contact',moved(consequence,(1,0,0),-3,n),(1,0,0)))
    spec={'recipe':'twelve acquired components with true cluster spacing','N':n,'groups':g,'components':count,
          'components_per_compound':group_size,'stages':stages,'initial_material':0,'interfaces':len(ports),'translation':tr,
          'between_gap':case.get('between_gap',11),'within_gap':5,'consequence_site_round1':list(consequence),
          'scope':'Finite composition and transmission among physically spaced learned component clusters. Does not imply independently renewable communicative individuals.'}
    return spec,ports


def run_case(case,out):
    import dee_thinking as d
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);start=time.monotonic();engine=identity();spec,ports=geometry(case)
    recipe=d.OrganizationRecipe.research(spec['N'],[],0);recipe.interfaces=ports;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    w=d.OrganizationalWorld.create(recipe);n=spec['N'];calls=[];snapshots=[];training=[];reads=[];messages=[];edits=[];trace=[]
    loads=case.get('loads',[[3,9+2*i] for i in range(12)]);query=case.get('query',13);rounds=case.get('rounds',2)
    if len(loads)!=12 or any(len(p)!=2 or any(type(x)is not int or not 0<=x<=65535 for x in p) for p in loads):raise ValueError('Twelve actual cue/report pairs')
    if rounds not in (1,2):raise ValueError('Finite1/2rounds')
    def submit(name,value,tick,role):
        r=w.submit(name,value,tick);calls.append({'id':int(r.id),'port':name,'payload':value,'requested_tick':tick,'call_tick':int(w.runtime.current_tick),'origin':role,'modality':'EXPERIENCE_PROTOCOL'});return int(r.id)
    def save(label):
        w.runtime.set_snapshot_metadata(KEY,json.dumps({'schema':1,'geometry':spec,'calls':calls,'tick':int(w.runtime.current_tick)},separators=(',',':')))
        p=out/(label+'.deetsnap');w.save_snapshot(str(p));snapshots.append({'file':p.name,'sha256':sha(p),'physical':digest(w)})
    put(out/'CONFIG.json',{'case':case,'geometry':spec,'engine':engine,'source_sha256':sha(__file__),
        'criterion_frozen':{'common_task':'Native serial transformation of the same query through all twelve acquired mobile relations, then contact with same environmental packet7.',
         'quality':'Exact field preservation and causal dependence; no winner by final-load magnitude.',
         'resources':'Same N127,12components,24traininginputs,2requests,one environmental input; topology changes gaps and latency.',
         'round2':'Tests continued access; does not assume twelve relations remain separate after consumed serial encounters.'}})
    save('INITIAL_T0')
    omit=set(case.get('omit_training',[]));unpair=set(case.get('unpaired_training',[]))
    for s,pair in zip(spec['stages'],loads):
        ids=[]
        if s['index']not in omit:
            ids.append(submit(f'stage{s["index"]}.cue',pair[0],int(s['index']in unpair),'ACTUAL_CUE_EXPERIENCE'))
            ids.append(submit(f'stage{s["index"]}.report',pair[1],0,'ACTUAL_REPORT_EXPERIENCE'))
        training.append({'component':s['index'],'receipt_ids':ids})
    until(w,3+bool(unpair))
    for r,s in zip(training,spec['stages']):r['physical']=record(w,moved(s['hub'],(0,1,0),max(0,int(w.runtime.current_tick)-3),n));r['receipts']=[receipt(w,x) for x in r['receipt_ids']]
    save('ACQUIRED_T'+str(w.runtime.current_tick))
    # All external inputs are fixed before observed outputs; no host feedback.
    for cycle in range(rounds):submit('request',query,6+n*cycle,'COMMON_PHYSICAL_REQUEST')
    final_tick=spec['stages'][-1]['meeting_tick']+n*(rounds-1)
    submit('environment.contact',7,final_tick,'CURRENT_ENVIRONMENTAL_CONTACT')
    # End consequence site moves by period n, therefore same coordinates.
    boundaries={6,final_tick+3,final_tick+6}
    for cycle in range(rounds):
        for s in spec['stages']:boundaries.update((s['meeting_tick']+n*cycle-1,s['meeting_tick']+n*cycle))
    edit_case=case.get('edge_edit');edit_tick=None
    if edit_case:
        edge=edit_case['after_stage'];s=spec['stages'][edge];edit_tick=s['meeting_tick']+2;boundaries.add(edit_tick)
    contact=None
    for tick in sorted(boundaries):
        until(w,tick)
        if tick==6:save('BEFORE_REQUEST_T6')
        if tick==edit_tick:
            s=spec['stages'][edit_case['after_stage']];site=moved(s['meeting'],(-1,1,0),2,n);before=record(w,site)
            edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.label='Explicit CPC5-extension diagnostic native-message '+edit_case['kind']
            if edit_case['kind']=='remove':edit.raw=0
            elif edit_case['kind']=='direction':edit.raw=d.pack_record(before['state'],before['s_reg'],1,1,0,before['semantic'])
            elif edit_case['kind']=='sham':edit.raw=int(before['raw'])
            else:raise ValueError('Unknown edit')
            parent=digest(w);op_before=normalized_op(w);clone=w.diagnostic_fork([edit],True);main_unchanged=digest(w)==parent and normalized_op(w)==op_before
            edits.append({'kind':edit_case['kind'],'site':list(site),'tick':tick,'before':before,'after':record(clone,site),
                          'parent_physical':parent,'MAIN_unchanged':main_unchanged,'only_RAW_field_requested':True,'clock_unchanged_at_site':record(clone,site)['clock']==before['clock']})
            assert main_unchanged;w=clone;save('DIAGNOSTIC_FORK_T'+str(tick))
        for cycle in range(rounds):
            for s in spec['stages']:
                if tick in (s['meeting_tick']+n*cycle-1,s['meeting_tick']+n*cycle):
                    q=s['meeting'];item={'round':cycle+1,'component':s['index'],'compound':s['compound'],'tick':tick,
                                         'relative_to_encounter':tick-(s['meeting_tick']+n*cycle),'physical':record(w,q)}
                    if item['relative_to_encounter']==0:reads.append(item)
                    if s['local']==0 or s['local']==spec['components_per_compound']-1:item['context']=local_context(w,q)
                    trace.append(item)
        if tick==final_tick+3:contact={'physical':record(w,spec['consequence_site_round1']),'context':local_context(w,spec['consequence_site_round1'])}
        put(out/'PROGRESS.json',{'case':case,'reads':reads,'edits':edits,'trace':trace,'snapshots':snapshots,'contact':contact})
    consequence=record(w,moved(spec['consequence_site_round1'],(0,1,0),3,n))
    # Correctly retain the immediate contact result by checkpoint-free exact
    # observation at its declared time; later free-flight site is also recorded.
    save('FINAL_T'+str(w.runtime.current_tick))
    final=digest(w);restored=d.OrganizationalWorld.load_snapshot(str(out/snapshots[-1]['file']))
    technical={'save_load_physical_equal':digest(restored)==final,'save_load_operative_equal':normalized_op(restored)==normalized_op(w)}
    for cycle in range(rounds):
        for a,b in zip(spec['stages'],spec['stages'][1:]):
            if a['compound']!=b['compound']:
                source=next(x for x in reads if x['component']==a['index'] and x['round']==cycle+1)
                dest=next(x for x in reads if x['component']==b['index'] and x['round']==cycle+1)
                messages.append({'emitter_compound':a['compound'],'receiver_compound':b['compound'],'emission':source,
                                 'reception':dest,'route_direction':[-1,1,0],'flight_ticks':b['meeting_tick']-a['meeting_tick'],
                                 'coverage':'Exact endpoint records/context; interior ballistic prediction, not unique genealogy or hidden ablation'})
    metrics=[]
    for cycle in range(rounds):
        rs=[r for r in reads if r['round']==cycle+1]
        metrics.append({'round':cycle+1,'components_read':len(rs),'active_endpoint_records':sum(r['physical']['active'] for r in rs),
                        'final_physical':rs[-1]['physical'],'request_to_final_ticks':rs[-1]['tick']-(6+n*cycle)})
    result={'case':case,'status':'MEASURED','source_sha256':sha(__file__),'engine':engine,'geometry':spec,
       'modality':'DIAGNOSTIC_FORK' if edit_case else 'EXPERIENCE_PROTOCOL followed by native transmission',
       'preparations':1,'forks':int(bool(edit_case)),'same_RUNTIME':not bool(edit_case),'training':training,'calls':calls,
       'receipts':[receipt(w,r['id']) for r in calls],'readouts':reads,'trace':trace,'messages':messages,'interventions':edits,
       'calculations':metrics,'consequence_at_contact':contact,'consequence_after_free_flight':consequence,'final':final,'operative_final':operational(w),'checkpoints':snapshots,
       'technical':technical,'direct_RAW_writes_in_MAIN':0,'direct_clock_writes_in_MAIN':0,
       'resources':{'components':12,'initial_material':0,'training_requests':2*(12-len(omit)),'query_requests':rounds,'environment_requests':1,
                    'basic_buffers_bytes':32*n**3,**memory()},'elapsed_seconds':time.monotonic()-start,
       'scope':spec['scope']+' Cluster symmetry and ports are designed; relations themselves arise from actual admitted experiences. No semantic roles are inferred from a commutative load.'}
    put(out/'MEASUREMENTS.json',result);assert all(technical.values())
    print(json.dumps({'id':case['id'],'metrics':metrics,'seconds':result['elapsed_seconds']}),flush=True);return result


def screen(config,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);rows=[]
    for case in config['cases']:
        target=out/case['id'];m=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf-8')) if (target/'MEASUREMENTS.json').exists() else run_case(case,target)
        rows.append({'case':case,'calculations':m['calculations'],'file':str((target/'MEASUREMENTS.json').relative_to(ROOT)),
                     'sha256':sha(target/'MEASUREMENTS.json'),'elapsed_seconds':m['elapsed_seconds']})
        put(out/'INDEX.json',{'configuration':config,'cases':rows})
    return rows


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['worker','screen']);p.add_argument('--case',type=Path);p.add_argument('--config',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.command=='worker':run_case(json.loads(a.case.read_text(encoding='utf-8')),a.out)
    else:screen(json.loads(a.config.read_text(encoding='utf-8')),a.out)
