from pathlib import Path
from collections import defaultdict,Counter
import argparse,json,sys,time,traceback
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from app.native_tools import physical,observe,moore27,atomic_json,digest_file,exact_receipt
from app.process_control import protect_current,current_resources
from dee_thinking import _native as d
PLAN=Path(__file__).with_name('LECTURA_TARDIA_PLAN_R1.json')
def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--plan',type=Path,default=PLAN);a=p.parse_args();protect_current();plan=json.loads(a.plan.read_bytes());case=next(x for x in plan['cases']if x['id']==a.case);a.out.mkdir(parents=True,exist_ok=False);started=time.perf_counter();store=Store();life='DCS11_'+a.case;rec=store.fork(plan['source'],life,kind='CANDIDATE');rec,s=store.load(life);w=s.world;end=plan['common_end_tick'];events=defaultdict(list);captures={2822,2889,3000,3224,3559,end};old_two=set();old_count=set();old_joint=set()
    if int(s.tick)!=plan['source_tick']:raise ValueError('Frozen delayed-read parent mismatch')
    result={'schema':'DCS1.1.late_access.r1','case':case,'life_id':life,'plan_sha256':digest_file(a.plan),'runner_sha256':digest_file(Path(__file__)),'parent':rec['parent'],'initial':physical(w,occupation=True),'status':'SCHEDULED','queries':[],'frames':[],'snapshots':[],'first_read_is_not_a_reconstruction':True,'RAW_clock_edits':[],'initiator':'EXTERNAL_INSTRUMENT_FIXED_PROTOCOL'}
    for index,bank in enumerate(s.repertoire.geometry['forms']):
        block=0 if index<8 else 1 if index<16 else 2 if index<32 else 3;first=plan['fixed_first_read_by_block'][block];sign=1 if index%2==0 else-1
        for qindex in range(case['rounds']):
            tick=first+case['cadence']*qindex;port=bank['ports']['read.plus'if qindex%2==0 else'read.minus']
            if case['route']!='onpath':
                name='DCS11.sham.'+bank['id']+'.'+str(qindex%2);vector=(0,0,1 if qindex%2==0 else-1)
                if name not in w.runtime.channel_names:
                    channel=d.ChannelSpec();channel.name=name;channel.injection_site=d.Coordinate(bank['hub'][0],(bank['hub'][1]+17)%67,(bank['hub'][2]-3*vector[2])%67);channel.direction=d.Direction(*vector);channel.state=1;channel.semantic=1;channel.allow_experience=True;channel.allow_probe=True;spec=d.InterfaceSpec();spec.name=name;spec.channel=channel;w.declare_interface(spec)
                port=name
            rr=w.probe(port,7,tick-3);row={'form':bank['id'],'hub':bank['hub'],'tick':tick,'qindex':qindex,'port':port,'receipt_id':int(rr.id),'expected_auditor_direction':[0,sign,1 if qindex%2==0 else 0]};result['queries'].append(row);events[tick].append(row);captures.update((tick-1,tick))
    for tick in range(2886,end,67):s.two_memory.input('quantity.reader',7,tick,True);old_two.add(tick+1);captures.update((tick,tick+1))
    for tick in range(2828,end+1,67):
        k=(tick-1957)//67
        for name in sorted({x['plus_port']if k%2==0 else x['minus_port']for x in s.geometry['cpc9_life']['count_repeated_readers']}):s.input(name,7,tick-3,'probe','CONTINUED_OLD_COUNT_NO_RETEACHING')
        old_count.add(tick);captures.add(tick)
    for tick in range(2827,end+1,67):
        for bank in s.geometry['joint_names'].values():s.input(bank['query_port'],17,tick-3,'probe','CONTINUED_OLD_JOINT_NO_RETEACHING')
        old_joint.add(tick);captures.add(tick)
    def save():result['elapsed_seconds']=time.perf_counter()-started;result['resources']=current_resources();atomic_json(a.out/'MEDICIONES.json',result)
    save()
    try:
        for tick in sorted(t for t in captures if 2822<=t<=end):
            s.run_until(tick);frame={'tick':tick,'physical':physical(w,occupation=True),'queries':[]}
            for q in events.get(tick,[]):
                o=observe(w,q['hub']);frame['queries'].append({**q,'physical':o,'qualified':o['active']and o['semantic']==1 and o['direction']==q['expected_auditor_direction']})
            if tick in old_two:frame['old_two_memory']=observe(w,s.two_memory.geometry['center'])
            if tick in old_count:frame['old_count']=[{'heading':r['heading'],'route':r['route'],'physical':observe(w,r['site'])}for r in s.geometry['cpc9_life']['count_repeated_readers']]
            if tick in old_joint:frame['old_joint']={k:observe(w,r['delivery_site'])for k,r in s.geometry['joint_names'].items()}
            if tick in(2850,2889,3224,3559,end):frame['micro_samples']=[{'id':s.repertoire.geometry['forms'][i]['id'],'Moore27':moore27(w,s.repertoire.geometry['forms'][i]['hub'])}for i in(0,15,64)]
            result['frames'].append(frame)
            if tick in(2889,end):
                f=a.out/('T'+str(tick)+'.deetsnap.gz');result['snapshots'].append({'file':f.name,'sha256':digest_file(f)if f.exists()else None,'storage':s.save(f),'physical':frame['physical']});result['snapshots'][-1]['sha256']=digest_file(f)
            if len(result['frames'])%12==0:save();print(a.case,tick,frame['physical']['occupied'],flush=True)
        result['rounds']=[{'query_index':i,'qualified':sum(q['qualified']for f in result['frames']for q in f['queries']if q['qindex']==i),'queries':sum(q['qindex']==i for f in result['frames']for q in f['queries']),'ticks':sorted({q['tick']for q in result['queries']if q['qindex']==i})}for i in range(case['rounds'])]
        result['receipts']=[exact_receipt(rr)for rr in w.runtime.receipts];result['receipt_statuses']=dict(Counter(x['status']for x in result['receipts']));result['final']=physical(w,occupation=True);rec=store.commit(rec,s,{'kind':'DELAYED_QUERY_DOSE_STUDY','plan_sha256':digest_file(a.plan),'case':case});result['operative_snapshot']=rec['snapshot'];result['status']='MEASURED';save();print(json.dumps({'case':a.case,'rounds':result['rounds'],'final':result['final']}),flush=True)
    except BaseException as e:result.update(status='TECHNICAL_ERROR',error=repr(e),traceback=traceback.format_exc());save();raise
if __name__=='__main__':main()
