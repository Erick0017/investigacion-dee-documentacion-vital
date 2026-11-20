"""Archived recalculation only: stdlib, zero DEE ticks, no external environment.

All metrics are recomputed from primary fields; no PASS or scenario label is
used to decide a physical output. Separate archived replay from native replay.
"""
from pathlib import Path
from collections import Counter
import argparse,json,hashlib,math

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def qx(r):return isinstance(r,dict)and r.get('state')==1 and r.get('semantic')==1 and r.get('direction')in([1,0,0],[-1,0,0])
def qa(r):return isinstance(r,dict)and r.get('state')==1 and r.get('semantic')==1 and r.get('s_reg',0)>0 and r.get('direction')in([1,1,0],[1,-1,0])
def qs(r,bank):return isinstance(r,dict)and r.get('state')==1 and r.get('semantic')==1 and r.get('s_reg',0)>0 and r.get('direction')==[0,-1 if bank=='minus'else 1,1]
def result(d):
    r=d.get('result',{})if isinstance(d,dict)else{}
    return r if isinstance(r,dict)else{'original_result_type_not_coerced_to_success':type(r).__name__}
def extrows(d):
    r=result(d)
    if isinstance(r.get('data'),dict):r=r['data']
    prefix=r.get('first2',{}).get('rows',[])if isinstance(r.get('first2'),dict)else[]
    if isinstance(r.get('external'),dict):r=r['external']
    rows=r.get('rows',[])
    return prefix+rows if rows and isinstance(rows[0],dict)and'response'in rows[0]else prefix
def native_rows(d):
    r=result(d)
    if isinstance(r.get('data'),dict):r=r['data']
    rows=r.get('native',[])
    if isinstance(rows,list)and rows and'action'in rows[0]:return[{'tick':x['query_tick'],'action':x['action'],'availability':x.get('availability')}for x in rows]
    frames=r.get('native_frames',r.get('body_frames',[]));out=[];seen=set()
    for f in frames:
        roles=[q for q in f.get('roles',[])if q.get('role')=='action']
        if roles and f['tick']not in seen:
            out.append({'tick':f['tick'],'action':f['selector'],'availability':roles[0].get('context')});seen.add(f['tick'])
    return out
def requests(d):
    found={}
    def walk(v):
        if isinstance(v,dict):
            receipt=v.get('receipt')
            if isinstance(receipt,dict)and'id'in receipt and'status'in receipt:
                key=int(receipt['id']);old=found.get(key)
                if old is None or old['status']=='scheduled':found[key]=receipt
            elif'id'in v and'status'in v and'channels'in v:
                key=int(v['id']);old=found.get(key)
                if old is None or old['status']=='scheduled':found[key]=v
            for k,u in v.items():
                if k not in('operations','parent','prefix_record','final_record','spec','frozen','prediction','operational_protocol','initial_environment','final_environment'):walk(u)
        elif isinstance(v,list):
            for u in v:walk(u)
    walk(d.get('result',{})if isinstance(d,dict)else{});return found
def nums(rows):
    rewards=[float(x['response']['reward'])for x in rows]
    native=[x.get('native',x.get('native_body',{}))for x in rows]
    magnitude=[r.get('state')==1 and r.get('semantic')==1 and r.get('direction')in([1,0,0],[-1,0,0],[0,0,0])for r in native]
    valid=[x.get('qualified_in_declared_domain',qa(x.get('native_body',{}))if'native_body'in x else magnitude[i])for i,x in enumerate(rows)]
    social=[any(s.get('qualified',False)for s in x.get('social_reads',[]))for x in rows]
    return{'opportunities':len(rows),'qualified_native_actuator_readings':sum(valid),'native_readings_outside_declared_codec':len(rows)-sum(valid),'body_opportunities':sum(bool(x.get('is_body_opportunity'))for x in rows),'qualified_body_opportunities':sum(bool(x.get('is_body_opportunity'))and qa(x.get('native_body',{}))for x in rows),'nonzero_executed_actions':sum(x.get('executed_torque',0)!=0 for x in rows),'received_relation_used_at_motor':sum(social),'reward_sum':math.fsum(rewards),'simulated_seconds':len(rows)*0.05,'first_tick':rows[0]['tick']if rows else None,'last_tick':rows[-1]['tick']if rows else None,'actions':[x.get('executed_torque',0)for x in rows]}
def metric(d,name):
    nr=native_rows(d);er=extrows(d);rr=requests(d);statuses=Counter(x['status']for x in rr.values());ins=d.get('INSTRUMENTO',{})
    m={'file':name,'life':ins.get('life_id',d.get('life')),'operation':ins.get('operation'),'tick':ins.get('tick'),'native_actions_requested':len(nr),'native_actions_with_payload':sum(qa(x['action'])for x in nr),'native_actions_useful_in_current_prepared_context':sum(qa(x['action'])and x['action']['direction'][1]==x.get('availability')for x in nr),'native_action_sequence':[x['action']['direction'][1]if qa(x['action'])else None for x in nr],'receipt_scope':'Distinct IDs visible in this primary record, not an assertion of all world inputs or independent learners','requests_visible_distinct':len(rr),'applied':statuses['applied'],'pending':statuses['scheduled'],'rejected':sum(v for k,v in statuses.items()if k.startswith('rejected')),'statuses':dict(statuses)}
    if er:m['external']=nums(er)
    r=result(d)
    if isinstance(r.get('data'),dict):r=r['data']
    if'received_outputs'in r:m['delayed_received_relation']=[{'bank':x['bank'],'qualified':qx(x['read'])and x['read']['s_reg']==7,'direction':x['read']['direction'],'s_reg':x['read']['s_reg']}for x in r['received_outputs']]
    if'frames'in r and any(x.get('kind')=='social'for x in r['frames']):
        forms=next(x for x in r['frames']if x.get('kind')=='social')['forms'];m['old_social_panel']=[{'id':f['id'],'qualified_banks':[b['id']for b in f['branches']if qs(b['read'],b['id'])]}for f in forms]
        m['old_social_forms_with_response']=sum(bool(f['qualified_banks'])for f in m['old_social_panel'])
        m['old_social_residual_directional_traces']=[{'id':f['id'],'banks':[b['id']for b in f['branches']if b['read']['state']==1 and b['read']['semantic']==1 and b['read'].get('s_reg',0)>7 and b['read']['direction'][1]==(-1 if b['id']=='minus'else 1)and b['read']['direction'][2]==1]}for f in forms]
        m['old_social_forms_with_residual_trace_not_automatically_functional']=sum(bool(f['banks'])for f in m['old_social_residual_directional_traces'])
        m['old_panel_quantity']=[f for f in r['frames']if f.get('kind')in('quantity','two_memory')]
    return m
def getfile(data,pattern):
    return next((d for n,d in data.items()if n==pattern),None)
def finalphys(d):
    r=result(d)
    if isinstance(r.get('data'),dict):r=r['data']
    for k in('final','physical','final_native'):
        if k in r and isinstance(r[k],dict)and'RAW_sha256'in r[k]:return r[k]
    return d.get('physical',{})
def samephys(a,b):
    x,y=finalphys(a or{}),finalphys(b or{});return{'RAW_equal':x.get('RAW_sha256')==y.get('RAW_sha256')and bool(x.get('RAW_sha256')),'clocks_equal':x.get('clocks_sha256')==y.get('clocks_sha256')and bool(x.get('clocks_sha256')),'a':x,'b':y}
def compute(ev):
    data={p.name:read(p)for p in sorted(ev.glob('*.json'))if not p.name.startswith(('CALCULOS','LECTURA_CIENTIFICA','TABLAS','INDICE_','MANIFIESTO','VERIFICACION'))}
    allmetrics=[metric(d,n)for n,d in data.items()if isinstance(d,dict)and'INSTRUMENTO'in d]
    checks={}
    for title,a,b in[('passive_delayed_record','SOCIAL_DELAY_LOW_125.json','SOCIAL_DELAY_PASSIVE_131.json'),('factorial_exact_main','FACTOR_REPLAY_MAIN_72.json','MAIN_BODY_REACHED_FAILURE_52.json'),('stress_observation_passive','STRESS_REPLAY_ALL_148.json','STRESS_REPLAY_PASSIVITY_153.json')]:
        if a in data and b in data:checks[title]=samephys(data[a],data[b])
    common=[]
    for name,d in data.items():
        if not name.startswith(('COMMON_INTEGRATED_','COMMON_ACTION_')):continue
        r=result(d);o=r['quantity'];ref=r['reference_hub'];common.append({'file':name,'life':d['INSTRUMENTO']['life_id'],'tick':d['INSTRUMENTO']['tick'],'public_object':r.get('common_raw_object',r.get('common_actual_object')),'reference_s_reg':ref['s_reg'],'qualified':qx(o)or(o['state']==1 and o['semantic']==1 and o['direction']==[0,0,0]),'direction':o['direction'],'raw':o['raw'],'whole_period_delay':r.get('whole_period_delay',0)})
    collision=[];d=data.get('AUTOPSY_MAIN_FIRST_LOSS_51.json')
    if d:
        for f in result(d)['frames']:
            collision.append({'tick':f['tick'],'s_reg140_sites':[x['site']for x in f['all_nonzero_RAW']if x['s_reg']==140],'occupied':f['global']['occupied']})
    key={n:{'physical':finalphys(d),'external':nums(extrows(d))if extrows(d)else None}for n,d in data.items()if isinstance(d,dict)and'INSTRUMENTO'in d and any(z in n for z in('FACTOR_','RECORD_ONLY_','STRESS_','COMMON_','INTERLEAVE_'))}
    return{'schema':'IC01.archived.recalculation.v1','native_ticks_executed':0,'external_environment_steps_executed':0,'independent_replica_count_not_inferred_from_branches':True,'primary_record_count':len(data),'trial_metrics':allmetrics,'physical_checks':checks,'common_history_opportunities':common,'main140_collision_window':collision,'selected_physical_results':key}
def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path);p.add_argument('--out',type=Path);p.add_argument('--compare',type=Path);a=p.parse_args();here=Path(__file__).resolve().parent
    ev=a.evidence or(here.parent/'EVIDENCIA_ESENCIAL'if(here.parent/'EVIDENCIA_ESENCIAL').exists()else here.parents[2]/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01');out=a.out or ev/'CALCULOS.json';r=compute(ev)
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
    if a.compare:
        expected=read(a.compare)
        if r!=expected:raise AssertionError('Archived recalculation differs from sealed reference')
    print(json.dumps({'calculation_file':str(out),'records':r['primary_record_count'],'trials_with_primary_operation':len(r['trial_metrics']),'common_history_cases':len(r['common_history_opportunities']),'physical_checks':{k:{s:v[s]for s in('RAW_equal','clocks_equal')}for k,v in r['physical_checks'].items()},'native_ticks':0},ensure_ascii=False))
if __name__=='__main__':main()
