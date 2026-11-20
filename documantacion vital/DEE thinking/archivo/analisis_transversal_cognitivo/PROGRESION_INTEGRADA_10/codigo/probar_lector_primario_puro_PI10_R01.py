"""Synthetic file-contract tests only. No DEE simulation, import or trajectory."""
from pathlib import Path
import copy,importlib.util,json,hashlib,argparse

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('audit',HERE/'recalcular_primarios_PI10_R01.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

def raw(state=0,sem=0,ds=(0,0,0),reg=0):
    return state+(reg<<32)+sum((v%16)<<s for v,s in zip(ds,(48,52,56)))+(sem<<60)

def obs(value,site,tick,clock=None):
    ds=[(value>>s)&15 for s in(48,52,56)]
    return {'raw':str(value),'state':value&0xffffffff,'s_reg':(value>>32)&65535,'semantic':value>>60,
      'direction':[n-16 if n>=8 else n for n in ds],'tick':tick,'site':site,'clock':str(tick if clock is None else clock),
      'active':(value&0xffffffff)>0 and value>>60!=5}

def fixture(regime='need',q1=1,q2=1,fi=1,bit=1):
    q=1000;s=q+22
    p={'query_origin':[24,12,12],'old_origin':[8,40,50],'query_prefix':'PI10.Q1.TC.R01','old_prefix':'PI07.TC.R01',
      'max_ticks_per_episode':2016,'fi_required':True,'schedule':[{'regime':regime,'cue':'threat','role':'adaptation','left':18,'right':5}],
      'calibration_schedule':[]}
    def cal(q,laps):
        seed=q+7;collision=seed+laps*67
        return {'query_tick':q,'query_read_tick':q+4,'seed_tick':seed,'delay_laps':laps,'collision_tick':collision,
          'outcome_injection_tick':collision-1,'contact_tick':collision+1,'settled_after_tick':collision+3}
    one=cal(q,18);two=cal(s,6);req=[]
    def request(channel,tick,payload=0):
        ident=len(req)+1;r={'id':ident,'channel':channel,'payload':payload,'requested_tick':tick,'receipt':{'id':ident,'status':'applied'}};req.append(r);return r
    for prefix,t in((p['query_prefix'],q),(p['old_prefix'],s)):
        for suffix in('query','support.plus','support.minus'):request(prefix+'.'+suffix,t)
    m1=a.motor(q1);m2=a.motor(q2);released=m1==1;sample=obs(raw(1,1,(0,0,1)if bit else(1,0,0)),[30,40,30],q-1)
    request(p['query_prefix']+'.datum',q+3,1);request(p['old_prefix']+'.datum',s+3,2*(bit if released else 0))
    question=request('PI10.question',q+7)if released else None
    copied=request(p['old_prefix']+'.copy.'+('plus'if m2==1 else'minus'),s+7)if m2 is not None else None
    route=(1 if m2==1 else 0)if m2 is not None else None;available=0 if regime=='bypass'else bit
    delivered=route==available and fi==1;useful=delivered and m1 is not None;failed=not useful
    request(p['query_prefix']+'.outcome.'+('failure'if failed else'nonfailure'),one['outcome_injection_tick'])
    request(p['old_prefix']+'.outcome.nonfailure',two['outcome_injection_tick'])
    def reader(c,site,t):
        val=raw(1,1,(c,1,0))if c is not None else 0
        return {'tick':t+4,'site':site,'observation':obs(val,site,t+4),'choice':c}
    def refs(origin,t):
        A=obs(raw(1,2,reg=0),[origin[0]-1,origin[1]-1,origin[2]],t)
        B=obs(raw(1,2,reg=1),[origin[0]+1,origin[1]-1,origin[2]],t)
        return {'A':A,'B':B,'A_minus_B':-1,'reference_clocks':[t,t]}
    fiq=s+150;fio=[]
    for x in(-1,0,1):
        for z in(0,-1):
            value=raw(1,1,(x,1,z))if fi is not None and x==fi and z==0 else 0
            fio.append(obs(value,[15+2*x,17,15+2*z],fiq+6))
    legacy={'old_q6_choice':fi,'original_result':{'native_trial':{'query_tick':fiq,'reader':{'observations':fio,'choice':fi}}}}
    fir={'old_q6_choice':fi,'legacy_result':legacy}
    data=int(sample['raw']).to_bytes(8,'little')*8;digest=hashlib.sha256(data).hexdigest()
    resource={'physical_delivered':delivered,'attributed_useful':useful,'actual_failed':failed,'FI_required':True,
      'actual_Native_FI_choice':fi,'available_bin':available,'actual_route':route,'process_error':None,
      'product':{'bytes':64,'sha256':digest}if delivered else None}
    v={'version':'DEE.PI10.adaptive_query.two_native_traces.R01','ordinal':0,'operator_calibration':False,'environment_spec':p['schedule'][0],
      'life_id':'SYNTHETIC_NO_NATIVE','calendar':{'first':one,'second':two},'before_tick':900,'after_tick':one['settled_after_tick'],
      'new_native_ticks':one['settled_after_tick']-900,
      'first_stage':{'query_tick':q,'reader':reader(q1,p['query_origin'],q),'native_motor':m1,'actual_query_motor':m1,'operator_forced_query':None,
        'sample_register':{'actual_preview_observation':sample,'first_submitted_STATE':1,'question_scheduled':released,'question_applied':released,
          'question_signature':released,'question_applied_and_signature':released,'access_valid':True,'released_bit':bit if released else 0},
        'question_observation':obs(raw(1,1,(1,0,0))if released else 0,[34,40,30],q+8),'question_request':question},
      'second_stage':{'query_tick':s,'reader':reader(q2,p['old_origin'],s),'native_motor':m2,'actual_motor':m2,
        'command_valid':m2 is not None,'actual_route':route,'copy_request':copied,'copy_receipt':copied['receipt']if copied else None,'FI':fir},
      'offer':{'prepared_tick':q-1,'query1_tick':q,'sample':sample,'available_bin':available,'resource':{'bytes':64,'sha256':digest}},
      'resource':resource,'actual_failed':failed,'returned_failed':failed,'feedback_arm':'real','trace_control':'none','requests':req,
      'Q1_references_before':refs(p['query_origin'],900),'Q2_references_before':refs(p['old_origin'],900),
      'references_after':{'q1':refs(p['query_origin'],one['settled_after_tick']),'q2':refs(p['old_origin'],one['settled_after_tick'])},
      'Q2_reference_difference_stable':True,'Native_inputs':{'unique_requested':len(req),'applied':len(req)}}
    return v,p

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--salida',type=Path,required=True);arg=parser.parse_args();checks=[]
    def check(name,fn):
        fn();checks.append({'name':name,'ok':True})
    def rejects(name,mutation):
        v,p=fixture();mutation(v,p)
        try:a.project_episode(v,p)
        except(ValueError,KeyError):checks.append({'name':name,'ok':True});return
        raise AssertionError('Expected rejection: '+name)
    check('RAW genuine Native positive selects query then route1',lambda: a.need(a.project_episode(*fixture())['attributed_useful'],'positive useful'))
    check('Native zero is valid minus, useful NoQuery bypass',lambda:a.need(a.project_episode(*fixture('bypass',0,-1))['attributed_useful'],'zero not NULL'))
    check('NULLq1 preserves physical delivery but no attributed useful',lambda:a.need((lambda r:r['physical_delivered']and not r['attributed_useful'])(a.project_episode(*fixture('bypass',None,-1))),'NULL attribution'))
    check('NULLq2 never defaults to useful bin0',lambda:a.need(not a.project_episode(*fixture('bypass',0,None))['physical_delivered'],'NULL motor'))
    check('Native FI zero is not FI plus; gate remains closed',lambda:a.need(not a.project_episode(*fixture(fi=0))['physical_delivered'],'FI exact output'))
    rejects('Reject actor choice contradicting RAW',lambda v,p:v['first_stage']['reader'].update(choice=-1))
    rejects('Reject early q+4 used as old FI q+6',lambda v,p:v['second_stage']['FI']['legacy_result']['original_result']['native_trial']['reader']['observations'][0].update(tick=1176))
    rejects('Reject preview acquired after choice',lambda v,p:v['first_stage']['sample_register']['actual_preview_observation'].update(tick=1004))
    rejects('Reject supplied expected bit as q2 datum',lambda v,p:next(r for r in v['requests']if r['channel']==p['old_prefix']+'.datum').update(payload=0))
    rejects('Reject Native silent replaced by direct route',lambda v,p:v['second_stage'].update(actual_route=0))
    rejects('Reject nonterminal receipt',lambda v,p:v['requests'][0]['receipt'].update(status='pending'))
    rejects('Reject duplicate receipt with contradictory status',lambda v,p:v['requests'].append({**v['requests'][0],'receipt':{'id':v['requests'][0]['id'],'status':'rejected_conflict'}}))
    rejects('Reject wrong pre-choice availability bin',lambda v,p:v['offer'].update(available_bin=0))
    rejects('Reject resource substituted with expected response bytes',lambda v,p:v['offer']['resource'].update(sha256='0'*64))
    rejects('Reject claimed useful after physical delivery false',lambda v,p:v['resource'].update(physical_delivered=False))
    rejects('Reject Native bank summary inconsistent with RAW',lambda v,p:v['Q1_references_before'].update(A_minus_B=123))
    rejects('Reject new phase/delay after seeing answers',lambda v,p:v['calendar']['first'].update(delay_laps=6))
    rejects('Reject hidden forced query in evaluation',lambda v,p:v['first_stage'].update(operator_forced_query=True))
    rejects('Reject actual contingency misreported as nonfailure',lambda v,p:v.update(returned_failed=True))
    need=arg.salida; a.need(not need.exists(),'Do not overwrite prior pure test evidence')
    data={'schema':'DEE.PI10.pure_primary_reader_contract_tests.R01','synthetic':True,'Native_imported':False,'Native_executed':False,
      'scope':'Exact artificial integer/file records; not a simulated DEE trajectory or Native validation. Real recorded episodes still required.',
      'checks':checks,'passed':len(checks),'total':19,'reader_sha256':hashlib.sha256((HERE/'recalcular_primarios_PI10_R01.py').read_bytes()).hexdigest()}
    with need.open('x',encoding='utf8')as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'checks':len(checks),'file':str(need),'Native_executed':False}))
if __name__=='__main__':main()
