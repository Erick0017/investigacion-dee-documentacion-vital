"""Pure R02 quota bound and exact scientific-body AST comparison.
Uses closed C6 metadata as documentary input; no Native/DEE/SQLite imports.
"""
from pathlib import Path
import ast,copy,importlib.util,json,sys
H=Path(__file__).resolve().parent;P=H.parent;P8=P.parent/'PROGRESION_INTEGRADA_08';P7=P.parent/'PROGRESION_INTEGRADA_07'
def load(name,file):
    s=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
r1=load('pi09_frozen_R01_quota',H/'pi09_consulta_selectiva_R01.py');r2=load('pi09_R02_quota',H/'pi09_consulta_selectiva_R02.py')
checks=[]
def require(ok,name):
    if not ok:raise AssertionError(name)
    checks.append(name)
require(r1._sha((H/'pi09_consulta_selectiva_R01.py').read_bytes())=='59d7cc5740ae5d9ca99ad30a86fc793a08f9fc89b23e03cb62377e2c844b2ecd','R01_literal_unchanged')
require(r1._sha(r1.PROTOCOL.read_bytes())=='cb6973e6f1bd747de8da73ecda37497579370330f828ea43d559a61c86e45ad5','18_environment_protocol_literal_unchanged')
source=(P8/'codigo/pi08_consulta_condicional_C_R03.py').read_text('utf-8-sig');a,n1=r1._transformed_episode(source);b,n2=r2._transformed_episode(source)
class ReferenceOnly(ast.NodeTransformer):
    def __init__(self):self.n=0
    def visit_Call(self,node):
        self.generic_visit(node)
        if isinstance(node.func,ast.Attribute)and node.func.attr=='append'and isinstance(node.func.value,ast.Subscript)and isinstance(node.func.value.value,ast.Name)and node.func.value.value.id=='m'and isinstance(node.func.value.slice,ast.Constant)and node.func.value.slice.value=='first_stage_rows':
            require(len(node.args)==1 and isinstance(node.args[0],ast.Name)and node.args[0].id=='first','exact_first_append_anchor');node.args=[ast.Call(func=ast.Name(id='_first_reference',ctx=ast.Load()),args=[ast.Name(id='first',ctx=ast.Load())],keywords=[])];self.n+=1
        return node
t=ReferenceOnly();expected=t.visit(ast.parse(a));actual=ast.parse(b)
require(t.n==1 and n1==8 and n2==9 and ast.dump(expected,include_attributes=False)==ast.dump(actual,include_attributes=False),'scientific_episode_AST_only_first_storage_reference_change')
for name in('_question_motor','_checked_RAW','validate_plan','_released_decode','_second_datum'):
    def function(file):return next(n for n in ast.parse(file.read_text('utf-8-sig')).body if isinstance(n,ast.FunctionDef)and n.name==name)
    require(ast.dump(function(H/'pi09_consulta_selectiva_R01.py'),include_attributes=False)==ast.dump(function(H/'pi09_consulta_selectiva_R02.py'),include_attributes=False),'decision_codec_and_data_function_unchanged_'+name)
primaryfile=P8/'ensayos/PI08_C_EVALUAR_R04_estado_post.json';primary=json.loads(primaryfile.read_bytes());v=primary['result'];v=json.loads(v)if isinstance(v,str)else v;m=v.get('result',v)['rows'][0]['progress']
require(len(m['first_stage_rows'])==len(m['rows'])==m['ordinal']==6,'actual_C6_documentary_source')
old_size=len(json.dumps(m,ensure_ascii=False,separators=(',',':')).encode());old_first_size=len(json.dumps(m['first_stage_rows'],ensure_ascii=False,separators=(',',':')).encode())
base=copy.deepcopy(m);base.update(version=r2.VERSION,life_id='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01',ordinal=0,rows=[],first_stage_rows=[],sample_register=None,log_count=10000,log_chain_sha256='a'*64)
base['control']={'arm':'always_desacoplado','query_policy':'always','information_policy':'desynchronized','max_ordinal':18,'evaluation_horizon':12,'conservative_max_plan_UTF8_bytes_buffer':'X'*6500}
base['environmental_supply']={'new_opportunities':18,'evaluation_horizon':12,'operational_future':6,'old_C_ordinal_preserved':6,'physical_bank_reset':False,'new_Native_ticks':0,'new_Native_inputs':0}
base['administrative_first_stage_storage']='R02_compact_witness_references_full_external_evidence_preserved'
full=copy.deepcopy(base);compact=copy.deepcopy(base);full_external=[];sizes=[]
# Execute the actual frozen65,536B guard with stdlib-only encode/native stubs.
bodyfile=P7/'codigo/pi07_regulacion_R01.py';tree=ast.parse(bodyfile.read_text('utf-8-sig'));nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in('_safe','_encoded')]
namespace={'json':json,'_native':lambda:(None,None,None,None,lambda x:json.dumps(x,ensure_ascii=False,separators=(',',':')))};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(bodyfile)+':pure_two_functions','exec'),namespace)
for i in range(18):
    first=copy.deepcopy(m['first_stage_rows'][i%6]);first['ordinal']=i;first['query_tick']+=1564*(i//6);first['external_immediate_witness']['file']='primera_C_%02d_q%d.json'%(i,first['query_tick'])
    row=copy.deepcopy(m['rows'][i%6]);row['ordinal']=i
    full['first_stage_rows'].append(first);full['rows'].append(row);full['ordinal']=i+1
    compact['first_stage_rows'].append(r2._first_reference(first));compact['rows'].append(row);compact['ordinal']=i+1
    # Worst pending current register remains full; it is never compacted.
    compact['sample_register']=copy.deepcopy(first['sample_register'])
    encoded=namespace['_encoded'](compact);require(len(encoded.encode())<=65536,'actual_frozen_encoder_accepts_compact_prefix_'+str(i+1));sizes.append({'opportunities':i+1,'compact_with6500Bbuffer':len(encoded.encode()),'uncompacted':len(json.dumps(full,ensure_ascii=False,separators=(',',':')).encode())});full_external.append({'first_stage':first})
require(len(full_external)==18 and all('requests'in x['first_stage']and'sample_register'in x['first_stage']for x in full_external),'all18_full_first_stage_records_retained_external_fixture')
try:namespace['_encoded'](full)
except ValueError:checks.append('frozen_encoder_rejects_uncompacted18_as_predicted')
else:raise AssertionError('quota risk not reproduced')
require(not any(k=='dee_thinking'or k.startswith('dee_thinking.')for k in sys.modules),'no_DEE_imported')
result={'schema':'DEE.PI09.consultation.R02.administrative_compaction.pure_proof.v1','passed':True,'Native_executed':False,'DEE_imported':False,'fixture_MOCK_ONLY_NOT_NATIVE':True,'no_material_passivity_claim':True,'checks':checks,'count':len(checks),'source_C6':{'path':str(primaryfile),'sha256':r2._sha(primaryfile.read_bytes()),'metadata_JSON_bytes':old_size,'full_first_stage_rows_JSON_bytes':old_first_size},'quota_guard':{'source':str(bodyfile),'source_sha256':r2._sha(bodyfile.read_bytes()),'literal_limit':65536,'guard_executed_with_stdlib_stubs':True},'sizes':sizes,'maximum_compact_bytes':max(x['compact_with6500Bbuffer']for x in sizes),'uncompacted18_bytes':sizes[-1]['uncompacted'],'module_R01_sha256':r2._sha((H/'pi09_consulta_selectiva_R01.py').read_bytes()),'module_R02_sha256':r2._sha((H/'pi09_consulta_selectiva_R02.py').read_bytes()),'scientific_body_AST_delta':'Exactly one storage append now holds witness reference; all Native calls/arguments/ordering/observations/decoders/actuators/return/timing unchanged'}
out=P/'control/COMPACTACION_METADATA_CONSULTA_PI09_R02_PRUEBA_PURA_FINAL.json'
with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':True,'checks':len(checks),'max_compact':result['maximum_compact_bytes'],'old18':result['uncompacted18_bytes'],'sha256':r2._sha(out.read_bytes())}))
