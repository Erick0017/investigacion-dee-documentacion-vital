"""Pure Python cases: real synthetic files, no DEE, no route policy or fallback."""
import argparse,copy,hashlib,importlib.util,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
def module(name):
    s=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
q=module('evaluador_calidad_apd02');providers=module('proveedores_prueba_apd02')
POLICY={'max_operand':32,'max_artifact_bytes':4096,'max_price':2,'max_delay_ticks':3,'resource_limits_required_for_success':True}
def dump(p,value):
    with p.open('x',encoding='utf8')as f:json.dump(value,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def deterministic(report):return {k:v for k,v in report.items()if k!='evaluation_resources'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False);cases=[];issues=[]
    def run(label,expected,*,operation='add',required='add',operands=None,procedure='native',native_value=11,price=1,delay=0,available=True,fault=None,mutate=None,state=None,policy=None,literal=None):
        folder=out/'CASOS'/label;folder.mkdir(parents=True);operands=list(operands or[7,4]);request={'task_id':label,'text':literal or'literal_fixture_no_semantic_lookup','operands':operands};public=copy.deepcopy(request);calls=[]
        if literal is None:request['required_operation']=required
        def native(op,args):calls.append({'procedure':'native','operation':op,'operands':list(args)});return native_value
        def external(op,args):calls.append({'procedure':'external','operation':op,'operands':list(args)});return args[0]+args[1]if op=='add'else args[0]-args[1]
        if state in('abstained','no_output','processing'):
            receipt={'task_id':label,'state':state,'selected_operation':None,'selected_procedure':None,'artifact':None,'price':0,'delay_ticks':0,'provider_calls':{'native':0,'external':0},'fixture_does_not_advance_DEE':True}
        else:
            receipt=providers.execute_selected(public,{'operation':operation,'procedure':procedure},sandbox_root=folder,native_value_reader=native,external_calculator=external,law={'price':price,'delay_ticks':delay,'available':available},fault=fault)
        if mutate:mutate(receipt,folder)
        actual_policy=copy.deepcopy(policy or POLICY);before=copy.deepcopy((request,receipt,actual_policy));report=None;error=None
        try:report=(q.evaluate_literal_committed if literal is not None else q.evaluate_committed)(request,receipt,sandbox_root=folder,policy=actual_policy)
        except q.UncommittedActionError as exc:error={'class':type(exc).__name__,'detail':str(exc)}
        except ValueError as exc:error={'class':type(exc).__name__,'detail':str(exc)}
        category=report['feedback']['category']if report else('UNCOMMITTED_REJECTED'if error['class']=='UncommittedActionError'else'EVALUATOR_DOMAIN_REJECTED');checks={'expected_category':category==expected,'only_selected_provider_once_or_unavailable':len(calls)==(0 if not available or state in('abstained','no_output','processing')else 1)and all(x['procedure']==procedure for x in calls),'no_request_or_receipt_mutation':before==(request,receipt,actual_policy),'literal_transport_has_no_requested_operator':literal is None or set(request)=={'task_id','text','operands'}}
        if report:
            checks['feedback_exact_category_only']=set(q.actor_feedback(report))=={'category'}and q.actor_feedback(report)['category']in q.CATEGORIES
            checks['binary_feedback_has_no_answer']=q.actor_feedback(report,binary=True)=={'category':'SUCCESS'if category=='SUCCESS'else'FAILURE'}
            checks['abstention_is_not_completion']=category!='ABSTENTION'or report['completed_task']is False
            checks['external_evaluation_accounted']=report['evaluation_resources']['external_reference_operations']==1and report['evaluation_resources']['not_DEE_computation']is True
        failures=[k for k,v in checks.items()if not v];issues.extend(label+':'+k for k in failures);row={'label':label,'entry':'literal'if literal is not None else'explicit_private_reference','expected_category':expected,'request':request,'committed':receipt,'policy':actual_policy,'provider_calls':calls,'report':report,'error':error,'checks':checks,'artifact_directory':'.','scope':'Synthetic purePython fixture; selected native callback is test data, not a claim of native DEE calculation.'};dump(folder/'CASO.json',row);cases.append({'label':label,'file':folder.relative_to(out).as_posix()+'/CASO.json','category':category,'checks':checks,'valid_solution':report['valid_solution_before_resource_ranking']if report else None,'completed_task':report['completed_task']if report else False});return row
    def rewrite(receipt,folder,transform):
        path=folder/receipt['artifact']['relative_path'];body=json.loads(path.read_bytes());body=transform(body);data=(json.dumps(body,sort_keys=True)+'\n').encode();path.write_bytes(data);receipt['artifact'].update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    run('native_correct','SUCCESS')
    run('file_exists_wrong_value','NUMERIC_ERROR',fault={'wrong_value_delta':1})
    run('cheap_wrong_operator','SEMANTIC_ERROR',operation='sub',native_value=3,price=0)
    run('correct_operation_filesystem_failed','FILESYSTEM_ERROR',fault={'fail_before_write':True})
    run('external_correct','SUCCESS',procedure='external')
    run('correct_but_expensive','RESOURCE_LIMIT',price=7)
    run('correct_but_late','RESOURCE_LIMIT',delay=8)
    run('external_unavailable_no_fallback','EXECUTION_ERROR',procedure='external',available=False)
    run('invalid_json_file_exists','ARTIFACT_ERROR',fault={'corrupt_json':True})
    run('receipt_SHA_disagrees','ARTIFACT_ERROR',mutate=lambda r,f:r['artifact'].update(sha256='0'*64))
    run('relative_escape_not_read','SAFETY_ERROR',mutate=lambda r,f:r['artifact'].update(relative_path='../outside.json'))
    run('absolute_path_not_read','SAFETY_ERROR',mutate=lambda r,f:r['artifact'].update(relative_path=str(f/'native_correct.json')))
    run('ADS_path_not_read','SAFETY_ERROR',mutate=lambda r,f:r['artifact'].update(relative_path='file.json:secret'))
    run('reserved_device_not_read','SAFETY_ERROR',mutate=lambda r,f:r['artifact'].update(relative_path='CON.json'))
    run('accidental_numeric_match_wrong_operation','SEMANTIC_ERROR',operation='sub',operands=[7,0],native_value=7)
    run('pending_not_evaluated','UNCOMMITTED_REJECTED',state='processing')
    run('explicit_abstention_not_completed','ABSTENTION',state='abstained')
    run('silence_not_abstention','NO_RESPONSE',state='no_output')
    run('bool_is_not_integer','ARTIFACT_ERROR',mutate=lambda r,f:rewrite(r,f,lambda b:{**b,'value':True}))
    run('foreign_task_artifact','ARTIFACT_ERROR',mutate=lambda r,f:rewrite(r,f,lambda b:{**b,'task_id':'another_task'}))
    run('wrong_operands_same_number','ARTIFACT_ERROR',mutate=lambda r,f:rewrite(r,f,lambda b:{**b,'operands':[8,3]}))
    run('invalid_resource_bool','RESOURCE_LIMIT',price=True)
    def duplicate(r,f):
        path=f/r['artifact']['relative_path'];data=path.read_bytes().rstrip();data=data[:-1]+b',"value":99}\n';path.write_bytes(data);r['artifact'].update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    run('duplicate_JSON_key','ARTIFACT_ERROR',mutate=duplicate)
    limited={**POLICY,'max_artifact_bytes':16};run('artifact_size_limit','ARTIFACT_ERROR',policy=limited)
    later=run('another_wrong_value_same_feedback','NUMERIC_ERROR',operands=[8,5],native_value=13,fault={'wrong_value_delta':1})
    for word in('suma','agrega','total'):run('literal_'+word,'SUCCESS',literal=word)
    for word in('diferencia','resta','quita'):run('literal_'+word,'SUCCESS',literal=word,operation='sub',native_value=3)
    run('literal_suma_wrong_operator','SEMANTIC_ERROR',literal='suma',operation='sub',native_value=3,price=0)
    run('literal_unknown_after_effect','EVALUATOR_DOMAIN_REJECTED',literal='desconocida')
    run('literal_unknown_pending_before_lookup','UNCOMMITTED_REJECTED',literal='desconocida',state='processing')
    first=json.loads((out/'CASOS/file_exists_wrong_value/CASO.json').read_bytes());feedback_equal=q.actor_feedback(first['report'])==q.actor_feedback(later['report'])
    if not feedback_equal:issues.append('different_numeric_targets_leaked_through_feedback')
    summary={'schema':'DEE.APD02.pure_quality_cases.v1','cases':cases,'issues':issues,'native_Runtime_imported':False,'new_DEE_ticks':0,'actual_selected_callback_invocations':sum(len(json.loads((out/c['file']).read_bytes())['provider_calls'])for c in cases),'numeric_error_feedback_equal_across_distinct_targets':feedback_equal,'scope':'Actual synthetic JSON effects and post-commit evaluation. Pure fixtures do not certify any DEE learning. No unselected route is executed, no correction is returned to a participant.'};dump(out/'RESULTADOS_CALIDAD.json',summary);print(json.dumps({'cases':len(cases),'issues':issues,'new_ticks':0}));return bool(issues)
if __name__=='__main__':raise SystemExit(main())
