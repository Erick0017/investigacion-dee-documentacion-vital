"""Re-evaluate archived synthetic effects; never call either action provider."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('archived_quality_only',HERE/'evaluador_calidad_apd02.py');quality=importlib.util.module_from_spec(spec);spec.loader.exec_module(quality)
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def deterministic(x):return{k:v for k,v in x.items()if k!='evaluation_resources'}
def calculate(root):
    summary=read(root/'RESULTADOS_CALIDAD.json');cases=[];issues=[];references=0
    for row in summary['cases']:
        relative=Path(row['file'])
        if relative.is_absolute()or'..'in relative.parts:raise ValueError('Unsafe archived fixture path')
        casefile=root/relative;case=read(casefile);actual=None;error=None
        try:actual=(quality.evaluate_literal_committed if case.get('entry')=='literal'else quality.evaluate_committed)(case['request'],case['committed'],sandbox_root=casefile.parent,policy=case['policy']);references+=1
        except quality.UncommittedActionError as exc:error={'class':type(exc).__name__,'detail':str(exc)}
        except ValueError as exc:error={'class':type(exc).__name__,'detail':str(exc)}
        category=actual['feedback']['category']if actual else('UNCOMMITTED_REJECTED'if error['class']=='UncommittedActionError'else'EVALUATOR_DOMAIN_REJECTED')
        checks={'report_byte_content_except_new_measurement_equal':(deterministic(actual)==deterministic(case['report']))if actual and case['report']else actual==case['report'],'same_uncommitted_or_domain_rejection':error==case['error'],'single_class_no_answer_in_actor_projection':actual is None or set(quality.actor_feedback(actual))=={'category'},'frozen_expected_category':category==case['expected_category']}
        issues.extend(case['label']+':'+k for k,v in checks.items()if not v);cases.append({'label':case['label'],'category':category,'checks':checks,'source':{'file':relative.as_posix(),'sha256':sha(casefile)}})
    return{'schema':'DEE.APD02.archived_quality_recalculation.v1','cases':cases,'issues':issues,'external_reference_evaluations':references,'provider_callbacks_executed':0,'new_native_ticks':0,'source_code_sha256':sha(HERE/'evaluador_calidad_apd02.py'),'scope':'Recomputed post-commit categories/axes from actual archived synthetic JSON files and original private requests. Fresh external timing measurements are deliberately not compared to old CPU/wall measurements. No tool, native Runtime, repair, alternative route or hidden answer return is executed.'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();x=calculate(a.evidencia)
    with a.salida.open('x',encoding='utf8')as f:json.dump(x,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'cases':len(x['cases']),'issues':x['issues'],'new_ticks':0,'provider_callbacks':0}));raise SystemExit(bool(x['issues']))
