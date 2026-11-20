"""Synthetic effect providers for causal quality tests, not a native solver.

Exactly one selected callback is invoked. Native values must come from a
supplied physical-result callback in real use; fixtures here are labeled pure
test data. There is no cheapest-route choice, dual execution or fallback.
"""
from pathlib import Path
import hashlib,json,os,re

SCHEMA='DEE.APD02.calculation_artifact.v1'
def execute_selected(public_request,action,*,sandbox_root,native_value_reader,external_calculator,law,fault=None,synthetic_fixture=True):
    if set(public_request)!={'task_id','text','operands'}:raise ValueError('Provider must not receive evaluator-private requested operation/reference')
    if set(action)!={'operation','procedure'}or action['operation']not in('add','sub')or action['procedure']not in('native','external'):raise ValueError('Only an already selected bounded action is accepted')
    if not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]{0,95}',public_request['task_id']):raise ValueError('Bounded synthetic task identifier required')
    if type(synthetic_fixture)is not bool:raise ValueError('The caller must declare factual fixture/real-callback scope')
    if not isinstance(public_request['operands'],list)or len(public_request['operands'])!=2 or any(type(v)is not int or not 0<=v<=32 for v in public_request['operands']):raise ValueError('Only two public exact integer operands0..32')
    if set(law)!={'price','delay_ticks','available'}or type(law['available'])is not bool:raise ValueError('A fixed chosen-route law is required, not alternatives or an optimal action')
    fault=dict(fault or{});allowed={'wrong_value_delta','fail_before_write','fail_after_write','corrupt_json'}
    if set(fault)-allowed:raise ValueError('Unknown declared synthetic fault')
    if type(fault.get('wrong_value_delta',0))is not int or not -64<=fault.get('wrong_value_delta',0)<=64 or any(type(fault[k])is not bool for k in('fail_before_write','fail_after_write','corrupt_json')if k in fault):raise ValueError('Exact bounded perturbation integer and explicit failure flags required')
    root=Path(sandbox_root).resolve(strict=True);name=public_request['task_id']+'.json';receipt={'task_id':public_request['task_id'],'state':'failed','selected_operation':action['operation'],'selected_procedure':action['procedure'],'artifact':None,'price':law['price'],'delay_ticks':law['delay_ticks'],'provider_calls':{'native':0,'external':0},'raw_provider_response':None,'used_value':None,'synthetic_fault':fault,'no_dual_execution_or_fallback':True,'fixture_does_not_advance_DEE':synthetic_fixture,'effect_phase':'planned','effect_phases':['planned'],'requires_explicit_reconciliation':False}
    def phase(value):receipt['effect_phase']=value;receipt['effect_phases'].append(value)
    if not law['available']:receipt['failure_class']='selected_provider_unavailable';return receipt
    callback=native_value_reader if action['procedure']=='native'else external_calculator
    receipt['provider_calls'][action['procedure']]+=1
    try:
        phase('before_compute')
        value=callback(action['operation'],tuple(public_request['operands']));receipt['raw_provider_response']={'value':value,'procedure':action['procedure']}
        if type(value)is not int:raise ValueError('Selected provider did not return an exact integer')
        used=value+fault.get('wrong_value_delta',0)
        if type(used)is not int:raise ValueError('Invalid explicit test perturbation')
        receipt['reported_value']=used;receipt['used_value']=used;phase('computed')
        if fault.get('fail_before_write'):raise PermissionError('Declared synthetic filesystem denial; no real permissions changed')
        body={'schema':SCHEMA,'task_id':public_request['task_id'],'operation':action['operation'],'operands':list(public_request['operands']),'value':used,'procedure':action['procedure']}
        data=(json.dumps(body,sort_keys=True,separators=(',',':'))+'\n').encode('utf8')
        if fault.get('corrupt_json'):data=b'{invalid synthetic artifact\n'
        path=root/name
        with path.open('xb')as stream:
            phase('opened');stream.write(data);stream.flush();phase('written')
            if fault.get('fail_after_write'):raise OSError('Declared synthetic failure after possible real file effect; no retry or committed receipt')
            os.fsync(stream.fileno());phase('fsynced')
        actual=path.read_bytes();phase('readback');receipt['artifact']={'relative_path':name,'bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest()};receipt['state']='committed'
    except Exception as exc:
        receipt['failure_class']=type(exc).__name__;receipt['provider_error']=str(exc)
        if receipt['effect_phase']in('opened','written','fsynced','readback'):
            receipt['state']='uncertain';receipt['requires_explicit_reconciliation']=True;receipt['possible_artifact']={'relative_path':name,'effect_may_exist':True,'no_confirmed_bytes_or_hash':True}
    return receipt
