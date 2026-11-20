"""Pure documentary tests against existing CLOSED C1 literals; no D execution.

Actual C1 rows validate the shared unchanged stage2 decoder/return adapter.
Synthetic control mutations are rejection tests, not material D outcomes.
"""
from pathlib import Path
import argparse,ast,copy,hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent;P=H.parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
d=load('_D_portable_pure_test',H/'RECALCULAR_D_PI09_R02.py');shared,old,m,adapter=d.parsers();checks=[]
def check(name,ok):
    assert ok,name
    checks.append(name)
def reject(name,fn):
    try:fn()
    except ValueError:checks.append(name);return
    raise AssertionError(name)
root=P/'control/NATIVE12_PORTABLE_R03';index=json.loads((root/'INDICE_PI09_CONSULTA_R01.json').read_text('utf8'));protocol=json.loads(shared.checked(root,index['protocol']));products={v['sha256']:shared.checked(root,v)for v in index['products']};count=0
for item in index['primaries']:
    primary=json.loads(shared.checked(root,item))
    for row in shared.rows(primary):
        if'first_stage'not in row:continue
        old.VERSION=row['version'];bit=row['extra_bit_entered_second_TC'];second,direct=old.stage2(row['second_stage'],bit,protocol,row['ordinal'],m,products,row['actual_failed']);count+=1
        check('Existing closed C1 ordinal%d unchanged Native decode'%row['ordinal'],second['actual_failed']is row['actual_failed']and second['returned_failed']is row['returned_failed'])
        reject('Wrong expected control valence rejected at%d'%row['ordinal'],lambda row=row,bit=bit:old.stage2(row['second_stage'],bit,protocol,row['ordinal'],m,products,not row['returned_failed']))
check('All twelve actual closed C1 second stages checked; no new D result',count==12)
check('Exactly3 return-only AST adaptations',len(adapter['adapted_expressions'])==3 and adapter['actual_function_actions_decoder_unchanged'])
exporter=load('_D_exporter_pure_test',H/'EXPORTAR_D_PI09_R02.py');dest=P/'control/NEVER_CREATED_D_PORTABLE_TEST_R02'
args=argparse.Namespace(cierre=['real='+str(P/'control/DOES_NOT_EXIST_D_CLOSURE.json')],sistema=['real='+str(P/'estados/NEVER_OPENED/sistema')],destino=str(dest))
result=exporter.export(args);check('Missing closure WAIT before opening world/home or writing output',result['status']=='WAIT'and not dest.exists())
ev=load('_D_eval_pure_test',P/'fuentes/EVALUAR_D_PI09_R02.py');wait=ev.evaluate({'schema':'DEE.PI09.D.recalculated_persistent_environment.R02','integrity_passed':True,'Native_executed':False,'groups':[]})
check('Incomplete D evaluation WAIT, no successful results invented',wait['status']=='WAIT'and wait['output_written']is False)
check('No DEE imported',not any(x=='dee_thinking'or x.startswith('dee_thinking.')for x in sys.modules))
files=[H/'EXPORTAR_D_PI09_R02.py',H/'RECALCULAR_D_PI09_R02.py',P/'fuentes/EVALUAR_D_PI09_R02.py']
for file in files:ast.parse(file.read_text('utf8'))
proof={'schema':'DEE.PI09.D.documentary_portable.pure_tests.R02','passed':True,'checks':checks,'count':len(checks),'existing_C1_second_stages_reused':count,'D_Native_executed':False,'DEE_imported':False,'D_world_or_card_or_home_read':False,'D_outputs_created':False,'actual_D_outcomes_inferred':False,'source_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in files},'adapter':adapter}
out=P/'control/PRUEBAS_PORTABLE_D_PI09_R02_FINAL.json'
with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':True,'checks':len(checks),'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
