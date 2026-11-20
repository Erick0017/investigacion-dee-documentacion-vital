"""Pure WSLS rule/AST tests; no world/Native/DEE or source edits."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent;P=H.parent;file=H/'pi09_referencia_contextual_D_WSLS_R01.py'
s=importlib.util.spec_from_file_location('material_reference_pure_tests',file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);checks=[]
def check(name,ok):
    assert ok,name
    checks.append(name)
def reject(name,fn):
    try:fn()
    except ValueError:checks.append(name);return
    raise AssertionError(name)
meta={'ordinal':0,'sample_register':{'released_bit':1},'material_WSLS_reference':m.initial_policy()}
check('Bit1 initial reference Pulse',m.reference_action(meta)=='pulso')
reject('Pending action cannot be silently replayed',lambda:m.reference_action(meta))
u=m.update_policy(meta,True,0);check('Actual failure flips only used bit1; bit0 retained',u['next_motor_for_same_bit']==-1 and meta['material_WSLS_reference']['motor_by_bit']=={'0':-1,'1':-1})
meta['ordinal']=1;meta['sample_register']['released_bit']=0;check('NoQuery material0 initial neutral',m.reference_action(meta)=='nada');m.update_policy(meta,False,1)
check('Actual success keeps context0 neutral',meta['material_WSLS_reference']['motor_by_bit']['0']==-1)
meta['ordinal']=2;meta['sample_register']['released_bit']=1;check('Previous actual failure changes next context1 to neutral',m.reference_action(meta)=='nada');m.update_policy(meta,False,2)
check('Successful revised context1 stays neutral',meta['material_WSLS_reference']['motor_by_bit']['1']==-1)
reject('Nonboolean evaluator success cannot update rule',lambda:m.update_policy(meta,1,3))
bad=copy.deepcopy(meta);bad['sample_register']['released_bit']=None
reject('Unknown information cannot become context0',lambda:m.reference_action(bad))
for row in ({'modo':m.EPISODE,'forzar':'pulso'},{'modo':m.PREPARE,'brazo':'real'},{'modo':'eci01-pi09-d-episodio'}):reject('No public target/force/oldD mode '+str(row),lambda row=row:m.validate_literal(row))
for mode in m.MODES:m.validate_literal({'modo':mode})
check('Three fixed modes admitted',len(m.MODES)==3)
second=P.parents[2]/'DEE Cognitive 2.0/sistema/capacidades/pi08_consulta_condicional_C_segunda_R02.py';text=second.read_text('utf-8-sig');check('Literal second source pinned',hashlib.sha256(second.read_bytes()).hexdigest()==m.SECOND_SHA)
adapted=m.transformed_second(text);ast.parse(adapted)
original=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='episode');changed=ast.parse(adapted).body[0]
# Undo the single existing forced assignment and prove every other AST node is
# literal, including observed Native reader, efference, FI/message and return.
orig_assign=next(n for n in ast.walk(original)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='forced'for t in n.targets))
changes=0
for n in ast.walk(changed):
    if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='forced'for t in n.targets):n.value=copy.deepcopy(orig_assign.value);changes+=1
check('Exactly one existing forced assignment; all other second AST literal',changes==1 and ast.dump(original,include_attributes=False)==ast.dump(changed,include_attributes=False))
check('No Native or DEE imported',not any(v=='dee_thinking'or v.startswith('dee_thinking.')for v in sys.modules))
proof={'schema':'DEE.PI09.D.material_WSLS.pure_rule_and_AST_tests.R01','passed':True,'checks':checks,'count':len(checks),'Native_executed':False,'DEE_imported':False,'world_or_source_code_written':False,'actual_material_WSLS_outcomes_claimed':False,'module_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'protocol_sha256':hashlib.sha256((H/'PROTOCOLO_PI09_D_WSLS_R01.json').read_bytes()).hexdigest(),'literal_second_sha256':m.SECOND_SHA,'single_existing_forced_assignment_only':True}
out=P/'control/PRUEBAS_REFERENCIA_D_WSLS_PI09_R01.json'
with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':True,'checks':len(checks),'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
