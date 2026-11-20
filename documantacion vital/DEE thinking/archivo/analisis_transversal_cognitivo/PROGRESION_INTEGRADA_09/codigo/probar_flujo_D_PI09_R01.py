"""Pure D first/second-stage flow; Fakes replace every Native adapter."""
from pathlib import Path
from types import SimpleNamespace
import importlib.util,json,sys
H=Path(__file__).resolve().parent;P=H.parent
s=importlib.util.spec_from_file_location('D_fake_flow_subject',H/'pi09_entorno_persistente_D_R01.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
b=d._bridge();b.SOURCE=P.parent/'PROGRESION_INTEGRADA_08/codigo/pi08_consulta_condicional_C_R03.py';c=b._C();p,ph=d.protocol(False)
dest=P/'control/PRUEBA_FLUJO_D_FAKE_R01';dest.mkdir(exist_ok=False);checks=[]
def check(name,ok):
    if not ok:raise AssertionError(name)
    checks.append(name)
records=[]
real_core=d._core
for role in('real','none','yoked'):
    a=SimpleNamespace(tick=900,world=object());home=dest/role;home.mkdir();counter=[0];calendars=[];nativecalls=[]
    parent={'literal':'same acquired R02/C/B history, fixture only'}
    plan={'values':[False,True,False,True,False,True]}
    meta={'ordinal':0,'control':{'arm':role,'query_policy':'native','information_policy':'real','return_plan':plan},'sample_register':None,'first_stage_rows':[],'pending':None,'uncertain':False}
    def request():
        counter[0]+=1;return {'id':counter[0],'receipt':{'id':counter[0],'status':'applied'}}
    def until(t):
        check('monotonic_'+role,t>=a.tick);a.tick=t;nativecalls.append(('until',t))
    def observe(adapter,site):
        direction=[1,0,0]if tuple(site)==c.QUESTION_READER else[0,0,1];raw=(1<<60)|1|(1<<(48 if direction[0] else 56))
        return {'raw':str(raw),'state':1,'semantic':1,'s_reg':0,'direction':direction,'clock':str(a.tick),'tick':a.tick,'site':list(site),'active':True}
    def schedule(*args):
        q=1000 if not calendars else 1782;cal={'query_tick':q,'contact_tick':q+410};calendars.append(cal);return cal
    def submit(adapter,channel,payload,tick,values,**kwargs):
        v=request();values.append(v);nativecalls.append(('submit',channel,payload,tick));return v
    def second(adapter,row,directory):
        check('actual_released_bit_enters_second_'+role,b._second_datum(meta)==1)
        returned=core._return(meta,True);until(2194);meta['ordinal']+=1
        return {'requests':[request()],'actual_failed':True,'returned_failed':returned,'scope':'Fake second function only; no Native execution'}
    core=SimpleNamespace(PREFIX='FAKE.TC',at=lambda v:tuple(v),_observe=observe,_helper=lambda:SimpleNamespace(schedule_trial=schedule,submit_query=lambda *args,**kw:[request()for _ in range(3)],submit_motor_copy=lambda *args,**kw:request()),_record=lambda *args,**kw:None,_submit=submit,_read=lambda *args:{'choice':1,'tick':1004},_motor=lambda v:None if v is None else 1 if v==1 else -1,_receipts=lambda adapter,values:values,_summary=lambda values,start,end:{'unique_requested':len({r['id']for r in values}),'applied':len({r['id']for r in values}),'all_terminal':True},_home=lambda *args:home,episode=second,body=SimpleNamespace(SafeAdapter=lambda adapter:SimpleNamespace(run_until=until)),_save=lambda *args:None,_return=lambda meta,failed:bool(failed))
    b._core=lambda:core;check('D_only_fixed_return_hook_'+role,real_core()._return is d._returned)
    c._component=lambda:core;c.validate=lambda *args:None;c._get=lambda *args:meta;c.protocol=lambda *args,**kw:(p,ph);c._old_literals=lambda *args:parent;c.LIFE=d.LIVES[role]
    d.validate=lambda *args:None;d._old_literals=lambda *args:parent;d._get=lambda *args:meta
    result=d.episode(a,home)
    check('Native_first_choice_never_forced_'+role,result['first_stage']['reader']['choice']==result['first_stage']['native_motor']==result['first_stage']['actual_query_motor']==1)
    check('shared_first_trace_no_credit_'+role,result['first_stage']['no_generic_return_scheduled_for_first_trace']is True)
    check('actual_failure_retained_'+role,result['actual_failed']is True)
    check('role_changes_only_return_'+role,result['returned_failed']is(role=='real'))
    check('compact_first_reference_'+role,'requests'not in meta['first_stage_rows'][0]and'requests'in result['first_stage'])
    check('no_guard_reinjection_during_episode_'+role,not any(v[0]=='submit'and v[1]==d.GUARD_CHANNEL for v in nativecalls))
    check('R02_ordinal12_literal_not_advanced_'+role,result['old_R02_ordinal_preserved']==12)
    check('D_progress1_registered_'+role,meta['ordinal']==1 and meta['sample_register']is None)
    records.append({'role':role,'first_Native_choice':1,'released_bit':1,'actual_failed':result['actual_failed'],'returned_failed':result['returned_failed'],'before_tick':result['before_tick'],'after_tick':result['after_tick'],'fixture_MOCK_ONLY_NOT_NATIVE':True})
check('all_roles_same_fake_Native_age',len({(r['before_tick'],r['after_tick'])for r in records})==1)
check('no_DEE_imported',not any(k=='dee_thinking'or k.startswith('dee_thinking.')for k in sys.modules))
value={'schema':'DEE.PI09.D.prepared_flow.fake_tests.R01','passed':True,'Native_executed':False,'DEE_imported':False,'fixture_MOCK_ONLY_NOT_NATIVE':True,'material_P0_or_passivity_not_tested':True,'checks':checks,'count':len(checks),'rows':records,'module_sha256':d._sha((H/'pi09_entorno_persistente_D_R01.py').read_bytes())}
out=P/'control/PRUEBAS_FLUJO_FAKE_D_PI09_R01.json'
with out.open('x',encoding='utf8')as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'checks':len(checks),'sha256':d._sha(out.read_bytes())}))
