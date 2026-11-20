"""Instrument-only R3 failed-terminal fixtures and unchanged archived replay."""
import argparse,copy,gzip,hashlib,importlib.util,json,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def load(name,p):
    sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('Preserve old instrumental proof')
    helper=load('helper_r3',HERE/'auditar_evento_objetivo_apd02_r03.py')
    quality=load('frozen_quality',a.stage/'FUENTES/W1/capacidades/evaluador_calidad_apd02.py')
    x=read(a.stage/'EVIDENCIA/W1/REGISTROS_VENTANA.json.gz');base=None
    for k,v in x['records'].items():
        if k.endswith('_parsed'):continue
        parsed=json.loads(v['result'])
        for row in parsed.get('result',{}).get('rows',[]):
            for op in row.get('result',{}).get('opportunities',[]):
                if op['environment_effect']['selected_action']=='ACT'and op['native_numeric']:base=op;break
            if base:break
        if base:break
    if base is None:raise ValueError('Known archived ACT fixture required')
    tests=[]
    with tempfile.TemporaryDirectory(prefix='apd02_audit_r3_')as temp:
        root=Path(temp)
        for name in('used_none','used_absent','response_none'):
            op=copy.deepcopy(base);effect=op['environment_effect'];receipt=effect['committed_effect'];record=op['native_numeric'][0]
            fixed_tick=int(record['native_trial']['datum_tick'])-2
            for frame in record['native_trial']['frames']:
                if int(frame['tick'])==fixed_tick:frame['fields']['C']['raw']='0'
            receipt.update(state='failed',artifact=None,raw_provider_response=None if name=='response_none'else{'value':None,'procedure':'native'},used_value=None,failure_class='ValueError')
            if name=='used_absent':receipt.pop('used_value')
            public={'task_id':receipt['task_id'],'text':effect['public_before']['text'],'operands':[effect['public_before']['left'],effect['public_before']['second']]}
            report=quality.evaluate_literal_committed(public,receipt,sandbox_root=root,policy={'max_operand':32,'max_artifact_bytes':4096,'max_price':2,'max_delay_ticks':8,'resource_limits_required_for_success':True})
            effect['quality']=report;effect['feedback']=quality.actor_feedback(report,binary=True)
            if op['common_return']is not None:op['common_return']['category']='FAILURE'
            result=helper.audit_goal_opportunity(op,artifact_directory=root,quality_module=quality)
            ok=not result['issues']and result['native_number']is None and result['file_goal_success']is False and result['file_quality_category']=='EXECUTION_ERROR'
            tests.append({'fixture':name,'result':result,'pass':ok})
        dest=root/'copied';shutil.copytree(a.stage,dest)
        shutil.copyfile(HERE/'auditar_evento_objetivo_apd02_r03.py',dest/'RECALCULO/auditar_evento_objetivo_apd02_r02.py')
        cp=subprocess.run([sys.executable,'-I','-B','-X','utf8','RECALCULO/recalcular_main_objetivo_r01.py','--evidence','EVIDENCIA','--output','R3_REPLAY.json'],cwd=dest,capture_output=True,text=True,encoding='utf8',timeout=45)
        calculated=dest/'R3_REPLAY.json';reference=a.stage/'REFERENCIA_MAIN_OBJETIVO_R02.json'
        replay={'returncode':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr,'byte_identical':calculated.exists()and calculated.read_bytes()==reference.read_bytes(),'reference_sha256':sha(reference),'calculated_sha256':sha(calculated)if calculated.exists()else None}
    result={'schema':'APD02.goal_auditor_R3.instrumental_N0','helper_sha256':sha(HERE/'auditar_evento_objetivo_apd02_r03.py'),'fixtures':tests,'archived_replay':replay,'issues':[]if all(t['pass']for t in tests)and replay['returncode']==0 and replay['byte_identical']else['instrumental_proof_failed'],'new_native_ticks':0,'synthetic_fixtures_are_not_cognitive_trials':True}
    with a.output.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,sort_keys=True,indent=2)
    print(json.dumps({'issues':result['issues'],'helper_sha256':result['helper_sha256'],'fixtures':len(tests),'replay_byte_identical':replay['byte_identical']},ensure_ascii=False))
    if result['issues']:raise SystemExit(1)
if __name__=='__main__':main()
