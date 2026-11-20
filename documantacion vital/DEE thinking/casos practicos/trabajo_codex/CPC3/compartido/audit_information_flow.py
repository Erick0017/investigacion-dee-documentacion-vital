"""Directed executable information-flow contrasts; no observer assertion substitutes evidence."""
import argparse,hashlib,json,sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();root=Path(a.root).resolve();sys.path.insert(0,str(root/'src'))
    from core.entity import Entity
    from core.comparison_entity import CentralComparisonEntity
    calls=[];profile_calls=[]
    def audit(frame,event,arg):
        if event=='c_call':
            name=getattr(arg,'__qualname__',getattr(arg,'__name__',''))
            owner=getattr(arg,'__self__',None)
            module=getattr(type(owner),'__module__','')
            if 'dee_thinking' in module and any(x in name.lower() for x in ('fork','raw','clock','research','submit','probe','advance','run_until','snapshot','experience')):
                profile_calls.append({'name':name,'owner':type(owner).__name__,'source_line':frame.f_lineno,'source':Path(frame.f_code.co_filename).name})
    class BoundarySpy:
        # pybind vectorcall may not generate c_call events. Explicitly record
        # the Python-facing calls we forward to the unchanged native instance.
        def __init__(self,value,role):self._value=value;self._role=role
        def __getattr__(self,name):
            value=getattr(self._value,name)
            if name=='runtime':return BoundarySpy(value,'Runtime')
            if not callable(value):return value
            def invoke(*args,**kwargs):
                calls.append({'name':name,'owner':self._role,'method':'explicit forwarding boundary, native instance unchanged'})
                if name in ('fork','diagnostic_fork','import_research_state','set_raw','set_clock','set_raw_at','set_clock_at'):
                    raise RuntimeError('Operational intervention entrypoint attempted: '+name)
                result=value(*args,**kwargs)
                return BoundarySpy(result,'OrganizationView') if name=='view' else result
            return invoke
    tests=[];states=[]
    left=Entity.create(initial_open=False,change_tick=80);right=Entity.create(initial_open=False,change_tick=None)
    left.sense();right.sense();left.world=BoundarySpy(left.world,'OrganizationalWorld');right.world=BoundarySpy(right.world,'OrganizationalWorld')
    # These functions must not be consulted by the predictor. Current time is
    # still evolved; only an actually requested sensory sample may read it.
    def forbidden(*args,**kwargs):raise RuntimeError('Forbidden future/result access during prediction')
    lr,rr=left.habitat.resolve,right.habitat.resolve
    ls,rs=left.habitat.sample,right.habitat.sample
    left.habitat.resolve=right.habitat.resolve=forbidden;left.habitat.sample=right.habitat.sample=forbidden
    sys.setprofile(audit)
    try:le=left.predict(30);re=right.predict(30)
    finally:sys.setprofile(None);left.habitat.resolve=lr;right.habitat.resolve=rr;left.habitat.sample=ls;right.habitat.sample=rs
    assert le['prediction_set']==re['prediction_set']==[False]
    assert left.physical_digest()==right.physical_digest()
    tests.append({'name':'predictor_no_future_or_result_or_sample_access','equal_physical_and_prediction':True,'different_hidden_future_laws':True,'forbidden_functions_raise_if_called':True})
    # Auditor log corruption is deliberately outside the native state. The
    # comparison evaluates false records, but it must not update the body.
    right.predictions[0]['prediction_set']=[True]
    left.advance(100);right.advance(100)
    assert left.physical_digest()==right.physical_digest()
    tests.append({'name':'auditor_prediction_log_not_feedback','native_identical_after_different_evaluations':True,'intervention':'one external prediction entry changed only; no RAW/clock edit','different_outcomes_after80':True})
    states.append({'left':left.physical_digest(),'right':right.physical_digest(),'actual_operations_left':left.operation_calls,'actual_operations_right':right.operation_calls})
    e=CentralComparisonEntity.create(initial_open=False,change_tick=80);e.sense();e.world=BoundarySpy(e.world,'OrganizationalWorld');em=e.predict();before=e.physical_digest()
    # Tamper only the audit's declared output. Its pending physical expectation
    # still verifies the actual live representation; this metadata is NOT an
    # input to the consequence codec or the native comparison.
    e.predictions[0]['prediction_set']=[True]
    sys.setprofile(audit)
    try:co=e.compare()
    finally:sys.setprofile(None)
    assert co['after_native']['physical_output']['direction']==[-1,0,-1]
    assert co['comparison_decoder']['presentation']=='discrepancia_direccional'
    assert co['input_receipt']['status']=='applied'
    tests.append({'name':'actual_report_not_computed_from_auditor_error','initial_native_expectation':em['physical_output']['direction'],'tampered_external_forecast':[True],'current_native_comparison':co['after_native']['physical_output'],'actual_report':co['source_actual'],'receipt':co['input_receipt']})
    assert not [c for c in calls if any(k in c['name'].lower() for k in ('fork','import_research','set_raw','set_clock'))]
    assert any(c['name']=='probe' for c in calls) and any(c['name']=='submit' for c in calls) and any(c['name']=='run_until' for c in calls)
    tests.append({'name':'explicit_forwarded_native_calls','forbidden_python_native_entrypoints_observed':[],'calls':calls,'c_call_profile_count':len(profile_calls),'instrumental_revision':'The first sys.setprofile attempt captured no pybind calls; retained as INFORMATION_FLOW_PROFILE_ATTEMPT.json, not accepted as absence proof. Explicit forwarding now records actual probe/submit/run_until calls.','coverage':'Python-facing world/runtime/view calls forwarded unchanged; source review covers native internal evolution, not a generic whole-binary noninterference proof'})
    report={'checks':tests,'native_states':states,'central_before':before,'central_after':e.physical_digest(),'methods':'Runtime evolution and counterfactual auditor metadata; no hidden oracle supplied to DEE','source_sha256':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (root/'src/core/entity.py',root/'src/core/central_comparison.py',root/'src/core/comparison_entity.py')},'all_assertions':True}
    out=root/'resultados/INFORMATION_FLOW_CHECK.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'checks':len(tests),'all_assertions':True,'output':str(out)}))

if __name__=='__main__':main()
