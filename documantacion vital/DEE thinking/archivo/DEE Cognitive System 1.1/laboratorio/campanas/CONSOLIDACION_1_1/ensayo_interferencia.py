"""Matched full-state continuations and a distinct new organization.

All physical changes occur through official admitted channels and v27. Current
events are environmental inputs; expected directions are auditor-only outputs.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,json,sys,time,traceback
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store,legacy_class
from app.native_tools import physical,observe,moore27,atomic_json,digest_file,exact_receipt
from app.process_control import protect_current,current_resources
from dee_thinking import _native as d
sys.path.insert(0,str(ROOT/'sistema/organizaciones/cpc9/src'))
from repertorio_n67 import N67RepertoireSession
PLAN=Path(__file__).with_name('INTERFERENCIA_PLAN_R1.json')

def add_guards(world,forms,mode,tick):
    records=[];n=int(world.runtime.dimension)
    if mode=='none':return records
    for bank in forms:
        for k,v in enumerate(((-1,0,0),(1,1,0),(1,-1,0))):
            site=[(bank['hub'][i]+v[i]+(17 if mode=='offpath'and i==2 else 0))%n for i in range(3)]
            name='DCS11.guard.'+bank['id']+'.'+str(k);c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(0,0,0);c.state=1;c.semantic=4;c.allow_experience=True;c.allow_probe=False
            spec=d.InterfaceSpec();spec.name=name;spec.channel=c;world.declare_interface(spec);receipt=world.submit(name,0,tick)
            records.append({'role':'PREPARED_R0_GUARD','port':name,'site':site,'requested_tick':tick,'payload':0,'semantic':4,'state':1,'receipt_id':int(receipt.id)})
    return records

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--end',type=int);p.add_argument('--plan',type=Path,default=PLAN);a=p.parse_args();protect_current();plan=json.loads(a.plan.read_bytes());case=next(x for x in plan['cases']if x['id']==a.case);out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);began=time.perf_counter();store=Store();pure=case.get('architecture')is not None;end=a.end or plan['end_tick'];life_id='DCS11_'+a.case
    if pure:
        s=N67RepertoireSession.create(65);s.run_until(1907);rec=None;rep=s;world=s.world;continuity='NEW_ARCHITECTURE_T0_EMPTY_WITH1907_NATIVE_WAIT_TICKS'
    else:
        rec=store.fork(plan['parent_life'],life_id,kind='CANDIDATE'if case['guards']=='onpath'else'DIAGNOSTIC_COPY');rec,s=store.load(life_id);world=s.world;continuity='EXACT_FORK_FROM_COMPLETE_CPC9_1907';before=physical(world);s.attach_instruments(65)
        if physical(world)!=before:raise AssertionError('Interface registration changed physical state')
        rep=s.repertoire
    maintenance=case.get('maintenance',not pure);old_s=s
    if pure and maintenance:
        _,old_s=store.load(plan['parent_life'])
        for interface in old_s.world.interfaces:world.declare_interface(interface)
    report={'schema':'DCS1.1.K65.study.r1','case':case,'case_id':a.case,'life_id':life_id,'status':'SCHEDULED','continuity_type':continuity,'plan_sha256':digest_file(a.plan),'runner_sha256':digest_file(Path(__file__)),'start_physical':physical(world,occupation=True),'parent':rec.get('parent')if rec else None,'requests':[],'frames':[],'snapshots':[],'queries':[],'old_operand_queries':[],'new_preparation':pure,'MAIN_RAW_clock_edits':[],'cause_not_prejudged':True}
    def save():report['elapsed_seconds']=time.perf_counter()-began;report['actual_worker_resources']=current_resources();atomic_json(out/'MEDICIONES.json',report)
    guards=add_guards(world,rep.geometry['forms'],case['guards'],1908);report['guard_requests']=guards;events=defaultdict(list);captures={1907,1908,1912,2152,2219,2286,2291,2292,2293,2353,2493,end};off=plan['training_start']
    for begin,finish,t0 in plan['training_blocks']:
        for index in range(begin,finish):
            bank=rep.geometry['forms'][index];sign=1 if index%2==0 else-1;at=off+t0
            rep.input(bank['ports']['cue'],5,at+int(case['events']=='unpaired'))
            if case['events']!='omitted':rep.input(bank['ports']['event.plus'if sign==1 else'event.minus'],11,at)
            if case['queries']=='none':continue
            count=0;t=at+70
            while t<=end:
                rep.input(bank['ports']['read.plus'if count%2==0 else'read.minus'],7,t-3,True)
                q={'tick':t,'form':bank['id'],'hub':bank['hub'],'query_index':count,'expected_auditor_direction':[0,sign,1 if count%2==0 else 0]};report['queries'].append(q);events[t].append(q);captures.update((t-1,t));t+=67;count+=1
    old_ticks=[];old_count_ticks=set();old_joint_ticks=set()
    if maintenance:
        for t in range(1947,end,67):world.probe('TM.quantity.reader',7,t);old_ticks.append(t+1);captures.update((t,t+1))
        for t in range(1957,end+1,67):
            k=(t-1957)//67
            for name in sorted({x['plus_port']if k%2==0 else x['minus_port']for x in old_s.geometry['cpc9_life']['count_repeated_readers']}):world.probe(name,7,t-3)
            captures.add(t)
            old_count_ticks.add(t)
        for t in range(1956,end+1,67):
            for bank in old_s.geometry['joint_names'].values():world.probe(bank['query_port'],17,t-3)
            captures.add(t)
            old_joint_ticks.add(t)
    report['requested_inputs_before_first_evolution']=[exact_receipt(x)for x in world.runtime.receipts];save()
    try:
        for tick in sorted(t for t in captures if 1907<=t<=end):
            s.run_until(tick);qs=[]
            for q in events.get(tick,[]):
                ob=observe(world,q['hub']);qualified=ob['active']and ob['semantic']==1 and ob['direction']==q['expected_auditor_direction'];item={**q,'physical':ob,'qualified':qualified};qs.append(item)
            frame={'tick':tick,'physical':physical(world,occupation=True),'queries':qs}
            if tick in(1912,2219,2291,2292,2353,2493,end):
                frame['local_samples']=[{'form':rep.geometry['forms'][i]['id'],'Moore27':moore27(world,rep.geometry['forms'][i]['hub'])}for i in(0,15,64)]
            if tick in old_ticks:
                ob=observe(world,old_s.two_memory.geometry['center']);entry={'tick':tick,'physical':ob};report['old_operand_queries'].append(entry);frame['old_two_memory']=entry
            if tick in old_count_ticks:frame['old_count_readers']=[{'heading':v['heading'],'route':v['route'],'physical':observe(world,v['site'])}for v in old_s.geometry['cpc9_life']['count_repeated_readers']]
            if tick in old_joint_ticks:frame['old_joint_readers']={k:observe(world,v['delivery_site'])for k,v in old_s.geometry['joint_names'].items()}
            if not pure and tick in(2152,2353,2493,end):frame['old_views']=s.view()
            report['frames'].append(frame)
            if tick in(1912,2353,end):
                file=out/('T'+str(tick)+'.deetsnap.gz');storage=s.save(file);report['snapshots'].append({'file':file.name,'sha256':digest_file(file),'storage':storage,'physical':frame['physical']})
            if len(report['frames'])%15==0:save();print(a.case,tick,frame['physical']['occupied'],flush=True)
        report['requests']=[exact_receipt(x)for x in world.runtime.receipts];report['receipt_statuses']=dict(Counter(x['status']for x in report['requests']));report['final_physical']=physical(world,occupation=True)
        allq=[q for f in report['frames']for q in f['queries']];report['all_qualified']=sum(x['qualified']for x in allq);report['all_queries']=len(allq)
        windows=[]
        for begin in range(2180,end+1,67):
            rows=[q for q in allq if begin<=q['tick']<=begin+39]
            if len(rows)==65 and len({q['form']for q in rows})==65:windows.append({'begin_tick':begin,'end_tick':begin+39,'qualified':sum(q['qualified']for q in rows),'denominator':65,'ticks':sorted({q['tick']for q in rows})})
        report['staggered_sweeps']=windows
        if not pure:
            rec=store.commit(rec,s,{'kind':'K65_CONTROLLED_STUDY_R1','plan_sha256':digest_file(a.plan),'case':case,'end_tick':end,'evidence':str(out.relative_to(ROOT))});report['operational_final_snapshot']=rec['snapshot'];report['operational_final_sha256']=rec['snapshot_sha256']
        report['status']='MEASURED';save();print(json.dumps({'case':a.case,'status':'MEASURED','sweeps':windows,'final':report['final_physical'],'old_positive_X':sum(q['physical']['active']and q['physical']['direction']==[1,0,0]for q in report['old_operand_queries']),'old_queries':len(report['old_operand_queries']),'seconds':report['elapsed_seconds']}),flush=True)
    except BaseException as e:report.update(status='TECHNICAL_ERROR',error=repr(e),traceback=traceback.format_exc());save();raise
if __name__=='__main__':main()
