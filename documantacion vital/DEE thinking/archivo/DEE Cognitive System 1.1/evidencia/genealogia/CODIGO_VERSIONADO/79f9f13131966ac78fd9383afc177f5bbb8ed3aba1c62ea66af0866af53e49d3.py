from pathlib import Path
from collections import Counter
import argparse,json,sys,time,traceback
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(ROOT/'sistema/capacidades'))
from app.lives import Store
from app.native_tools import physical,observe,moore27,atomic_json,digest_file,exact_receipt
from app.process_control import protect_current,current_resources
import puente_adquirible as bridge
PLAN=Path(__file__).with_name('CONTINUIDAD_FUNCIONAL_PLAN_R1.json')
def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--plan',type=Path,default=PLAN);a=p.parse_args();protect_current();plan=json.loads(a.plan.read_bytes());case=next(x for x in plan['cases']if x['id']==a.case);a.out.mkdir(parents=True,exist_ok=False);started=time.perf_counter();store=Store()
    source=ROOT/'sistema'/plan['source_snapshot']
    if digest_file(source)!=plan['source_sha256']:raise ValueError('Frozen common parent changed')
    rec=store.fork(plan['source_life'],'DCS11_'+a.case,kind='CANDIDATE'if case['mode']=='CANDIDATE_EXACT_CONTINUATION'else'DIAGNOSTIC_COPY',checkpoint=plan['source_snapshot']);rec,s=store.load(rec['life_id'])
    w=s.world;initial=physical(w,occupation=True);g=bridge.declare(w,count=plan['count'],translation=plan.get('translation',[0,0,0]))
    if physical(w,occupation=True)!=initial:raise AssertionError('Empty interface declaration changed physical state')
    bridge.teach(w,case.get('actual_new_form_events',plan['actual_new_form_events']),plan['new_form_teaching_tick'],omit_event=case['events']=='omitted',cue=case.get('cue',plan.get('new_cue_load',5)),teacher=case.get('teacher',plan.get('new_teacher_load',11)));bridge.roundtrip(w,plan['first_source_read_tick'],omit_B_cue=not case['B_cue'],omit_C_cue=not case['C_cue']);g=bridge.geometry(w);times=g['roundtrip'];end=plan['end_tick'];old_two=set();old_count=set();old_joint=set();quantity_outputs=set();captures={1948,1968,1971,2037,2038,2042,2043,2109,2110,2115,2116,2182,2183,2188,2189,2211,2214,2280,2281,2482,end};captures.update([v for v in times.values()if type(v)is int]);captures.update([v-1 for v in times.values()if type(v)is int]);captures.update((plan['new_form_teaching_tick'],plan['new_form_teaching_tick']+3))
    late_reads=set(plan.get('late_source_reads',[]))
    for tick in sorted(late_reads):
        for form in g['forms']:s.input(form['ports']['read'],7,tick-3,'probe','LATE_ACQUIRED_SOURCE_ACCESS')
        captures.update((tick-1,tick))
    for index,value in plan['object_rounds']:
        s.quantity.present_object(value,round_index=index);s.quantity.input('quantity.reader',7,69+67*index,True);quantity_outputs.add(70+67*index);captures.update((69+67*index,70+67*index))
    prefix='quantity.reference.'if case['update']=='onpath'else'quantity.other.'
    s.quantity.input(prefix+'cue',0,plan['reference_update_input_tick']);s.quantity.input(prefix+('resource'if case['update']=='onpath'else'event'),plan['reference_addition'],plan['reference_update_input_tick'])
    for tick in range(2014,end,67):s.two_memory.input('quantity.reader',7,tick,True);old_two.add(tick+1);captures.update((tick,tick+1))
    for tick in range(1957,end+1,67):
        k=(tick-1957)//67
        for name in sorted({r['plus_port']if k%2==0 else r['minus_port']for r in s.geometry['cpc9_life']['count_repeated_readers']}):s.input(name,7,tick-3,'probe','CONTINUATION_OLD_COUNT_NO_RETEACHING')
        old_count.add(tick);captures.add(tick)
    for tick in range(1956,end+1,67):
        for row in s.geometry['joint_names'].values():s.input(row['query_port'],17,tick-3,'probe','CONTINUATION_OLD_JOINT_NO_RETEACHING')
        old_joint.add(tick);captures.add(tick)
    result={'schema':'DCS1.1.functional_continuation.r1','case':case,'life_id':rec['life_id'],'parent_sha256':plan['source_sha256'],'plan_sha256':digest_file(a.plan),'runner_sha256':digest_file(Path(__file__)),'bridge_source_sha256':digest_file(Path(bridge.__file__)),'initial':initial,'bridge_geometry':g,'status':'SCHEDULED','frames':[],'snapshots':[],'external_interventions':'Only explicit current/future inputs and empty interface declarations; noRAW/clockedits','memberships':[{'id':'E1','sites':'Original body plusA/C/use bridge regions'},{'id':'B','sites':'DeclaredB_hub regions only; learned by native received packets'}]}
    def save():result['elapsed_seconds']=time.perf_counter()-started;result['resources']=current_resources();atomic_json(a.out/'MEDICIONES.json',result)
    save()
    try:
        for tick in sorted(t for t in captures if 1948<=t<=end):
            s.run_until(tick);frame={'tick':tick,'physical':physical(w,occupation=True)}
            if tick in old_two:frame['old_two_memory']=observe(w,s.two_memory.geometry['center'])
            if tick in old_count:frame['old_count']=[{'heading':r['heading'],'route':r['route'],'physical':observe(w,r['site'])}for r in s.geometry['cpc9_life']['count_repeated_readers']]
            if tick in old_joint:frame['old_joint']={k:observe(w,r['delivery_site'])for k,r in s.geometry['joint_names'].items()}
            if tick in quantity_outputs:frame['quantity']={k:observe(w,s.geometry['quantity'][k])for k in('center','reference_site','reference_hub','object_site','object_hub')}
            if plan['new_form_teaching_tick']<=tick<=times['use']or tick in late_reads:
                frame['social']=[{'id':f['id'],'A':observe(w,f['A_hub']),'branches':[{'id':b['id'],**{k:observe(w,b[k])for k in('B_hub','C_hub','use_site')}}for b in f['branches']]}for f in g['forms']]
            if tick in(1971,2037,2038,2042,2043,2109,2110,2115,2116,2182,2183,2188,2189,2280,2281)or tick in[v for v in times.values()if type(v)is int]:
                frame['micro']={'quantity':moore27(w,s.geometry['quantity']['center']),'new_A0':moore27(w,g['forms'][0]['A_hub']),'new_B0_plus':moore27(w,g['forms'][0]['branches'][1]['B_hub'])}
            result['frames'].append(frame)
            if tick in(2037,2042,2109,2115,2182,2189,2281,end)or tick in[v-1 for v in times.values()if type(v)is int]:
                f=a.out/('T'+str(tick)+'.deetsnap.gz');storage=s.save(f);result['snapshots'].append({'file':f.name,'storage':storage,'sha256':digest_file(f),'physical':frame['physical']})
            if len(result['frames'])%10==0:save();print(a.case,tick,frame['physical']['occupied'],flush=True)
        result['requests']=[exact_receipt(q)for q in w.runtime.receipts];result['receipt_statuses']=dict(Counter(q['status']for q in result['requests']));result['final']=physical(w,occupation=True);rec['memberships']=result['memberships'];rec=store.commit(rec,s,{'kind':'FUNCTIONAL_CONTINUATION_R1','plan_sha256':digest_file(a.plan),'case':case,'evidence':str(a.out.relative_to(ROOT))});result['operative_snapshot']=rec['snapshot'];result['operative_snapshot_sha256']=rec['snapshot_sha256'];result['status']='MEASURED';save();print(json.dumps({'case':a.case,'life':rec['life_id'],'status':'MEASURED','final':result['final']}),flush=True)
    except BaseException as e:result.update(status='TECHNICAL_ERROR',error=repr(e),traceback=traceback.format_exc());save();raise
if __name__=='__main__':main()
