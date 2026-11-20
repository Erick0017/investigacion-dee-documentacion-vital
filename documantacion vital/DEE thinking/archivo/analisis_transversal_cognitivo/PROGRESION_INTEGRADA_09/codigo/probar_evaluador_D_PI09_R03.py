"""Pure actual closed Real6 chain view; controls remain WAIT, no guesses."""
from pathlib import Path
import copy,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];file=P/'fuentes/EVALUAR_D_PI09_R03.py';s=importlib.util.spec_from_file_location('D_eval_R03_pure_tests',file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
source=P/'control/D_REAL6_RESULTADO_RECALCULO_R03.json';r=json.loads(source.read_text('utf8'));rows=sorted(r['rows'],key=lambda x:x['ordinal']);checks=[]
def check(name,ok):
    assert ok,name
    checks.append(name)
actual=m.first_chain_descriptors(rows)
check('Actual same STATE1 Native query changes after own shared failure',any(x['later_changed_ordinal']==3 and x['same_observed_preview_direction']and x['later_first_Native_choice']==0 for x in actual))
check('Actual changed-use cases preserve credit limitation',all(x['shared_bank_chain_revision_not_query_specific_credit']for x in actual))
wait=m.evaluate(r);check('No None/Yoke results invented; incomplete4comparison WAIT',wait['status']=='WAIT'and wait['output_written']is False)
no_failure=copy.deepcopy(rows)
for row in no_failure:row['second']['actual_failed']=False;row['second']['returned_failed']=False
check('No prior actual failure => no acquired-revision descriptor',m.first_chain_descriptors(no_failure)==[])
no_return=copy.deepcopy(rows);no_return[0]['second']['returned_failed']=False
check('Failure without returned negative is not own-failed-return evidence',m.first_chain_descriptors(no_return)==[])
null=copy.deepcopy(rows)
for row in null:row['first']['Native_valid']=False
check('NULL selections do not become valid abstention/revision',m.first_chain_descriptors(null)==[])
assert hashlib.sha256((P/'fuentes/EVALUAR_D_PI09_R02.py').read_bytes()).hexdigest()=='8ef28ca0b554d3b936f3bc014bdd89cb1ad93e90fce4ecd2069f7bd265ff608d'
proof={'schema':'DEE.PI09.D.shared_chain_documentary_view.tests.R03','passed':True,'checks':checks,'count':len(checks),'Native_executed':False,'DEE_imported':False,'actual_source_recalculation':{'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()},'R03_evaluator_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'actual_shared_chain_descriptors':actual,'no_control_score_or_adoption_inferred':True,'old_R02_evaluator_unchanged':True}
out=P/'control/PRUEBAS_EVALUADOR_D_PI09_R03.json'
with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':True,'count':len(checks),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'actual_shared_chain_changes':len(actual)}))
