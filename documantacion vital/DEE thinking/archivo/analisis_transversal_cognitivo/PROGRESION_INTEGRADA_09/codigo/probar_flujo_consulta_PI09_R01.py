"""Execute the adapted host flow with Fakes only; no Native/DEE imports."""
from pathlib import Path
from types import SimpleNamespace
import importlib.util, json, sys
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('pi09_fake_subject',H/'pi09_consulta_selectiva_R01.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.SOURCE=H.parents[1]/'PROGRESION_INTEGRADA_08/codigo/pi08_consulta_condicional_C_R03.py'
c=m._C();P=m._protocol()[0];D=H.parent/'control/PRUEBA_FLUJO_FAKE_PI09_R02';D.mkdir(exist_ok=False)
checks=[]
def require(ok,name):
    if not ok:raise AssertionError(name)
    checks.append(name)
def run(policy,native_choice):
    home=D/(policy+'_'+str(native_choice));home.mkdir();a=SimpleNamespace(tick=900,world=object());counter=[0];calls=[]
    meta={'ordinal':0,'control':{'query_policy':policy,'information_policy':'real'},'sample_register':None,'first_stage_rows':[],'pending':None,'uncertain':False}
    def req():
        counter[0]+=1;return {'id':counter[0],'receipt':{'id':counter[0],'status':'applied'}}
    def until(t):require(t>=a.tick,'Fake_monotonic_'+policy);a.tick=t;calls.append(t)
    def observe(adapter,site):
        direction=[1,0,0]if tuple(site)==c.QUESTION_READER else [0,0,1]
        return {'raw':str((1<<60)|1),'state':1,'s_reg':0,'semantic':1,'direction':direction,'site':list(site),'tick':a.tick,'clock':str(a.tick),'active':True}
    calendars=[]
    def schedule(*args):
        q=1000 if not calendars else 1782;cal={'query_tick':q,'contact_tick':q+410};calendars.append(cal);return cal
    def submit(adapter,channel,payload,tick,requests,**kw):
        value=req();requests.append(value);return value
    def summary(requests,start,end):return {'unique_requested':len({r['id']for r in requests}),'applied':len({r['id']for r in requests}),'all_terminal':True}
    def second(adapter,row,directory):
        value=meta['sample_register']['released_bit'];require(m._second_datum(meta)==value,'second_gets_actual_released_'+policy)
        until(2194);meta['ordinal']+=1
        return {'requests':[],'actual_failed':False,'returned_failed':False,'extra_submitted':value}
    core=SimpleNamespace(PREFIX='FAKE.TC',at=lambda v:tuple(v),_observe=observe,_helper=lambda:SimpleNamespace(schedule_trial=schedule,submit_query=lambda *args,**kw:[req()for _ in range(6)],submit_motor_copy=lambda *args,**kw:req()),_record=lambda *args,**kw:None,_submit=submit,_read=lambda *args:{'choice':native_choice,'tick':1004},_motor=lambda x:None if x is None else 1 if x==1 else -1,_receipts=lambda adapter,values:values,_summary=summary,_home=lambda *args:home,episode=second,body=SimpleNamespace(SafeAdapter=lambda adapter:SimpleNamespace(run_until=until)),_save=lambda *args:None)
    c._component=lambda:core;c.validate=lambda *args:None;c._get=lambda adapter:meta;c.protocol=lambda *args,**kwargs:(P,'a'*64);c._old_literals=lambda *args:{};c.LIFE='FAKE_ONLY'
    row=c.episode(a,home)
    expected=native_choice==1 if policy=='native' else policy=='always'
    require(row['first_stage']['native_motor']==(None if native_choice is None else 1 if native_choice==1 else -1),'exact_Native_motor_'+policy)
    require(row['first_stage']['actual_query_motor']==(1 if expected else None if policy=='native'and native_choice is None else -1),'reference_motor_separate_'+policy)
    require(row['first_stage']['sample_register']['question_scheduled']==expected,'material_request_only_policy_'+policy)
    require(row['extra_bit_entered_second_TC']==(1 if expected else 0),'gated_actual_bit_'+policy)
    require(row['first_stage']['no_generic_return_scheduled_for_first_trace']is True,'no_invented_first_credit_'+policy)
    w=home/row['external_immediate_first_stage_witness']['file'];require(w.is_file()and m._sha(w.read_bytes())==row['external_immediate_first_stage_witness']['sha256'],'immediate_witness_hash_'+policy)
    require(meta['ordinal']==1 and meta['sample_register']is None,'closed_progress_and_register_'+policy)
    return {'query_policy':policy,'Native_choice':native_choice,'question':expected,'requests':row['Native_inputs']['unique_requested'],'first_query':1000,'second_query':1782,'fixture_MOCK_ONLY_NOT_NATIVE':True}
rows=[run('native',1),run('native',0),run('native',None),run('always',0),run('never',1)]
require(not any(k=='dee_thinking'or k.startswith('dee_thinking.')for k in sys.modules),'no_DEE_module_imported')
out=H.parent/'control/PRUEBAS_FLUJO_FAKE_CONSULTA_PI09_R01.json'
value={'schema':'DEE.PI09.selective_consultation.fake_flow_tests.R01','passed':True,'count':len(checks),'checks':checks,'rows':rows,'Native_executed':False,'DEE_imported':False,'material_passivity_tested':False,'fixture_MOCK_ONLY_NOT_NATIVE':True,'module_sha256':m._sha((H/'pi09_consulta_selectiva_R01.py').read_bytes())}
with out.open('x',encoding='utf8')as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'checks':len(checks),'sha256':m._sha(out.read_bytes())}))
