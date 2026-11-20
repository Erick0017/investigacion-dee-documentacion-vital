from pathlib import Path
from collections import Counter
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(ROOT/'sistema/capacidades'))
from app.lives import Store
from app.native_tools import physical,observe,moore27,atomic_json,digest_file,exact_receipt
from app.process_control import protect_current,current_resources
from dee_thinking import _native as d
import puente_adquirible as bridge
def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();protect_current();a.out.mkdir(parents=True,exist_ok=False);planfile=Path(__file__).with_name('MOVIL_SOCIAL_PLAN_R1.json');plan=json.loads(planfile.read_bytes());case=next(x for x in plan['cases']if x['id']==a.case);store=Store();src=ROOT/plan['source_file'];parent=plan['source_import_life']
    if not store.life_dir(parent).exists():store.import_state(src,parent,'cpc9_integral_n67',plan['source_sha256'])
    rec=store.fork(parent,'DCS11_'+a.case,kind='CANDIDATE'if case['query']else'DIAGNOSTIC_COPY');rec,s=store.load(rec['life_id']);w=s.world;g=bridge.geometry(w);end=plan['end_tick'];oldtwo=set();oldjoint=set();oldcount=set();capture={2189,end,2482,2281,2618};lookup={t:i for i,t in enumerate(plan['query_ticks'])};receipts=[]
    for f in g['forms']:
        for b in f['branches']:
            name='DCS11.mobile.'+f['id']+'.'+b['id']+'.readminus';v=(-1,0,0);c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*bridge.move(b['use_site'],v,-3));c.direction=d.Direction(*v);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True;i=d.InterfaceSpec();i.name=name;i.channel=c;w.declare_interface(i);b['mobile_minus']=name
    for tick,index in lookup.items():
        if case['query']:
            for f in g['forms']:
                for b in f['branches']:receipts.append(s.input(b['mobile_minus']if index%2==0 else b['ports']['use'],7,tick-3,'probe','EXPLICIT_TRANSFORMED_CARRIER_ACCESS'))
        capture.update((tick-1,tick))
    for tick in range(2684,end,67):s.two_memory.input('quantity.reader',7,tick,True);oldtwo.add(tick+1);capture.add(tick+1)
    for tick in range(2627,end+1,67):
        k=(tick-1957)//67
        for name in sorted({x['plus_port']if k%2==0 else x['minus_port']for x in s.geometry['cpc9_life']['count_repeated_readers']}):s.input(name,7,tick-3,'probe','OLD_COUNT_CONTINUED')
        oldcount.add(tick);capture.add(tick)
    for tick in range(2626,end+1,67):
        for bank in s.geometry['joint_names'].values():s.input(bank['query_port'],17,tick-3,'probe','OLD_JOINT_CONTINUED')
        oldjoint.add(tick);capture.add(tick)
    result={'schema':'DCS1.1.mobile_social_access.r1','case':case,'life_id':rec['life_id'],'parent':rec['parent'],'source_sha256':digest_file(src),'plan_sha256':digest_file(planfile),'initial':physical(w,occupation=True),'geometry':g,'frames':[],'status':'SCHEDULED','RAW_clock_edits':[]}
    for tick in sorted(x for x in capture if 2189<=x<=end):
        s.run_until(tick);f={'tick':tick,'physical':physical(w,occupation=True)}
        if tick in lookup:f['read_index']=lookup[tick];f['forms']=[{'id':f['id'],'branches':[{'id':b['id'],'physical':observe(w,b['use_site'])}for b in f['branches']]}for f in g['forms']]
        if tick in oldtwo:f['old_two_memory']=observe(w,s.two_memory.geometry['center'])
        if tick in oldjoint:f['old_joint']={k:observe(w,x['delivery_site'])for k,x in s.geometry['joint_names'].items()}
        if tick in oldcount:f['old_count']=[{'heading':x['heading'],'route':x['route'],'physical':observe(w,x['site'])}for x in s.geometry['cpc9_life']['count_repeated_readers']]
        if tick in(2256,2591,2993):f['micro']=moore27(w,g['forms'][1]['branches'][0]['use_site'])
        result['frames'].append(f)
    result['receipts']=[exact_receipt(x)for x in w.runtime.receipts];result['receipt_statuses']=dict(Counter(x['status']for x in result['receipts']));result['final']=physical(w,occupation=True);rec=store.commit(rec,s,{'kind':'MOBILE_SOCIAL_ACCESS','plan_sha256':digest_file(planfile),'case':case});result['snapshot']=rec['snapshot'];result['status']='MEASURED';result['resources']=current_resources();atomic_json(a.out/'MEDICIONES.json',result);print(json.dumps({'case':a.case,'tick':s.tick,'occupation':result['final']['occupied']}))
if __name__=='__main__':main()
