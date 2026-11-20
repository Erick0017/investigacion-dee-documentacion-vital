"""C2C fixed-reader/quality pure checks plus passive old B receipt audit."""
from pathlib import Path
from types import SimpleNamespace,ModuleType
import ast,copy,hashlib,importlib.util,json,sys

def load(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

if __name__=='__main__':
    H=Path(__file__).resolve().parent;P=H.parent;before=set(sys.modules)
    c=load(H/'pi04_coordinacion_central_C2C.py','C2C_STATIC')
    sensor=load(H/'pi04_sensor_central_C2C_R01.py','C2C_SENSOR_STATIC')
    p,ph=c.protocol();assert p['status']=='DRAFT'and p['calibration_values']==[0,4,5]and len(p['schedule'])==26
    refusals=[]
    for x in(0,4,5):c.validate_literal({'modo':c.CALIBRATE,'valor':x})
    for x in(1,3,6,True):
        try:c.validate_literal({'modo':c.CALIBRATE,'valor':x})
        except ValueError:refusals.append('cal_value_'+str(x))
        else:raise AssertionError('Unexpected C calibration')
    # Fake physical records test the exact predicate, not Native behaviour.
    record={'state':1,'semantic':1,'direction':[0,1,-1],'raw':'SYNTHETIC','s_reg':0}
    metadata={'OLD_SENSOR':json.dumps({'version':'OLD'}),sensor.KEY:json.dumps({'version':sensor.VERSION})}
    d=SimpleNamespace(Coordinate=lambda *x:tuple(x))
    old=SimpleNamespace(KEY='OLD_SENSOR',VERSION='OLD')
    old._guard=lambda a:(d,lambda x:dict(x),None,json.loads,json.dumps,metadata,'ECI02_PI03_REPRO_PI04_C2CCAL_01')
    sensor._OLD=old
    owner=SimpleNamespace(tick=104,world=SimpleNamespace(runtime=SimpleNamespace(observe=lambda site:record)))
    cases=[]
    for dx in(-1,0,1):
        for z in(-1,0):
            record.update(state=1,semantic=1,direction=[dx,1,z]);r=sensor.read_fixed(owner,100)
            assert r['choice']==dx;cases.append({'direction':list(record['direction']),'choice':r['choice']})
    for label,change in(('state0',{'state':0}),('SEM4',{'semantic':4}),('Y0',{'direction':[0,0,-1]}),('Zplus',{'direction':[0,1,1]})):
        record.update(state=1,semantic=1,direction=[0,1,-1]);record.update(change)
        assert sensor.read_fixed(owner,100)['choice']is None;cases.append({'invalid':label,'choice':None})
    owner.tick=106
    try:sensor.read_fixed(owner,100)
    except ValueError:refusals.append('wrong_q6_window')
    else:raise AssertionError('Reader searched late window')
    def req(i,status='applied',tick=5):return {'id':i,'receipt':{'id':i,'status':status,'requested_tick':tick}}
    quality=c._native_input_summary([req(1),req(1)],{'native_operation':{'native_trial':{'requests':[req(2,'rejected_occupied')]}}},{'requests':[req(3)]},0,10)
    assert quality['unique_requested']==3 and quality['aliases_deduplicated']==1 and quality['rejected']==1 and quality['all_terminal']
    pending=c._native_input_summary([req(1,'scheduled')],None,None,0,10)
    assert not pending['all_terminal']and pending['pending_or_other']==1
    null=c._native_input_summary([req(1)],None,None,0,10)
    assert null['unique_requested']==1 and null['group_raw_counts']=={'outer':1}
    try:c._native_input_summary([req(1,tick=-1)],None,None,0,10)
    except ValueError:refusals.append('inherited_outside_window')
    else:raise AssertionError('Inherited receipt counted')
    passive=[]
    for i in range(3):
        file=P/'ensayos'/('PI04_C2B_REAL_DEV_R01_OP_'+str(i)+'.json')
        root=json.loads(file.read_text(encoding='utf8'));native=json.loads(root['result']);r=native['result']['rows'][0]
        q=c._native_input_summary(r['requests'],r['native_arithmetic'],r['second_native_use'],r['before_tick'],r['after_tick'])
        passive.append({'ordinal':i,'primary':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'dose':q})
    assert sum(v['dose']['unique_requested']for v in passive)==561 and sum(v['dose']['applied']for v in passive)==559 and sum(v['dose']['rejected']for v in passive)==2
    # Both old source histories are mocked, but the full three B receipt
    # groups are independently read from their existing real journal here.
    oldm={'admitted':True,'arm':'real','ordinal':11,'pending':None,'uncertain':False,'halted_reason':'First NULL/actual preserved',
          'rows':[{'first_choice':1}for _ in range(10)]+[{'first_choice':None}]}
    bm={'admitted':True,'arm':'real','ordinal':3,'pending':None,'uncertain':False,'halted_reason':None,'rows':[{'after_tick':798815},{'after_tick':799597},{'after_tick':800379}]}
    deps=lambda *a:{'pending':None,'uncertain':False,'device_pending':None,'device_feedback_pending':None,'device_uncertain':False}
    om=SimpleNamespace(KEY='OLD_C2',_get=lambda a:oldm,operational_dependencies=deps)
    bmod=SimpleNamespace(KEY='OLD_B',FOLDER='PI04_C2B_COORDINACION_R01',_get=lambda a:bm,operational_dependencies=deps)
    c._module=lambda n:om if n=='pi04_coordinacion_adquirida'else bmod if n=='pi04_coordinacion_simetrica_C2B'else (_ for _ in()).throw(ValueError(n))
    source=P/'estados/candidato_R02/sistema/estado/servicios_locales/ECI02_PI03_REPRO_PI04_MAIN_02'
    pred=c._require_closed_predecessors(None,source)
    assert pred['old_C2B_actual_Native_dose']=={'requested':561,'applied':559,'rejected':2,'other':0}
    # Read/hold/efference ordering is fixed in source; this is NOT timing proof.
    code=(H/'pi04_coordinacion_central_C2C.py').read_text(encoding='utf8')
    assert 'a.run_until(q+4); first_reader=_sensor().read_fixed(a,q)\n    a.run_until(cal["query_read_tick"])'in code
    assert code.index('a.run_until(q+4); first_reader')<code.index('copy=_helper().submit_motor_copy')
    dee=[x for x in set(sys.modules)-before if x=='dee_thinking'or x.startswith('dee_thinking.')];assert not dee
    result={'schema':'PI04.C2C.pure_and_passive_check.R01','status':'PURE_READER_AND_PASSIVE_OLD_INPUTS_NOT_NATIVE_C2C',
        'Native_ticks':0,'official_DEE_imports':dee,'reader_synthetic_cases':cases,'refusals':refusals,
        'quality_synthetic':quality,'quality_scheduled_synthetic':pending,'NULL_unexecuted_stage_synthetic':null,
        'real_predecessor_B_passive_dose':passive,'predecessor_guard_mocks_and_real_journal':pred,
        'fixed_q4_to_q6_hold_source_order':True,'controller_sha256':hashlib.sha256((H/'pi04_coordinacion_central_C2C.py').read_bytes()).hexdigest(),
        'sensor_sha256':hashlib.sha256((H/'pi04_sensor_central_C2C_R01.py').read_bytes()).hexdigest(),
        'limits':'The q4 observer change does not repair FI ports or the eligibility hub. No C2C Native response, admission, learning or usefulness has been tested by this agent.'}
    out=P/'control/C2C_PURO_Y_DOSIS_PASIVA_R01.json'
    if out.exists():raise ValueError('Preserve prior proof')
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'report':str(out),'status':result['status'],'Native_ticks':0,'controller_sha256':result['controller_sha256'],'old_B_dose':[561,559,2]},indent=2))
