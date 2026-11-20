"""Pure stdlib contracts; no DEE imports, owner or Native execution."""
from pathlib import Path
import ast, hashlib, importlib.util, json, sys
H = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('pi09_test_subject',H/'pi09_consulta_selectiva_R01.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
P8 = H.parents[1]/'PROGRESION_INTEGRADA_08'
m.SOURCE = P8/'codigo/pi08_consulta_condicional_C_R03.py'
checks = []
def check(name,ok):
    if not ok: raise AssertionError(name)
    checks.append(name)
def rejects(name,fn):
    try: fn()
    except (ValueError,KeyError,TypeError): checks.append(name); return
    raise AssertionError(name)
p,ph = m._protocol()
check('18_lot_split6_and6_plus6future',len(p['schedule']) == 18 and [r['stage'] for r in p['schedule']] == ['development']*6+['reserved']*6+['operational_prepared']*6)
check('first12_4_of_each_environment',all(sum(r['cue']==c for r in p['schedule'][:12])==4 for c in ('threat','falsecue','none')))
check('prefixed_plus5_derangement',p['yoke_permutation']==[(i+5)%12 for i in range(12)] and all(i!=j for i,j in enumerate(p['yoke_permutation'])))
source = m.SOURCE.read_bytes(); check('literal_C_source_pin',m._sha(source)==m.SOURCE_SHA)
transformed,n = m._transformed_episode(source.decode('utf-8-sig')); ast.parse(transformed)
check('8_local_source_adapter_anchors',n==8)
check('no_second_episode_change',m._sha((P8/'codigo/pi08_consulta_condicional_C_segunda_R02.py').read_bytes())=='500db3042c14bd23bb839de5e2dbf8bb715040dec2c1d740db270ad8026b5f9f')
rejects('anchor_fail_closed',lambda:m._transformed_episode(source.decode('utf-8-sig').replace("motor1 = c._motor(reader1['choice'])","motor1 = unexpected()")))
for a in ('native_real','always_real','never'):
    m.validate_literal({'modo':m.PREPARE,'brazo':a}); checks.append('literal_'+a)
for mode in (m.EPISODE,m.STATE):
    m.validate_literal({'modo':mode}); checks.append('literal_'+mode)
    rejects('no_actor_expected_'+mode,lambda mode=mode:m.validate_literal({'modo':mode,'expected':1}))
for native in (-1,1,None):
    check('native_motor_preserved_'+str(native),m._question_motor({'control':{'query_policy':'native'}},native)==native)
    check('always_material_reference_'+str(native),m._question_motor({'control':{'query_policy':'always'}},native)==1)
    check('never_material_reference_'+str(native),m._question_motor({'control':{'query_policy':'never'}},native)==-1)
# Loading the literal C module only imports stdlib; no _core/_native call.
c = m._C(); check('no_DEE_module_imported',not any(k=='dee_thinking' or k.startswith('dee_thinking.') for k in sys.modules))
def obs(bit,tick):
    raw = 0 if bit is None else ((1<<60)|1|((1<<56) if bit else (1<<48)))
    return {'raw':str(raw),'state':0 if bit is None else 1,'s_reg':0,'semantic':0 if bit is None else 1,'direction':[0,0,0] if bit is None else [0,0,1] if bit else [1,0,0],'site':[30,40,30],'tick':tick,'clock':str(tick),'active':bit is not None}
samples=[]
for i in range(12):
    o=obs(i%2,900000+i); samples.append({'ordinal':i,'observation':o,'observation_sha256':m._sha(m._canon(o)),'primary_sha256':'a'*64})
plan={'schema':'DEE.PI09.actual_RAW_sample_yoke.v1','permutation':p['yoke_permutation'],'source_arm':'always_real','source_evidence_sha256':'b'*64,'samples':samples}
encoded=m._canon(plan).decode('utf8'); loaded=m.validate_plan(encoded,p)
check('compact12_payload_below_8192',len(m._canon({'operacion':'sesion','actuador':'closed','retorno':'real','situaciones':[{'modo':m.PREPARE,'brazo':'always_desacoplado','plan':encoded}]}))<8192)
m.validate_literal({'modo':m.PREPARE,'brazo':'always_desacoplado','plan':encoded}); checks.append('bounded_yoke_admission')
for i in range(12):
    meta={'ordinal':i,'control':{'information_policy':'desynchronized','sample_plan':loaded}}
    decoded=m._released_decode(meta,obs(0,3),True,'noaccess')
    check('actual_permuted_source_'+str(i),decoded['bit']==((i+5)%12)%2 and decoded['source']['source_ordinal']==(i+5)%12)
    no=m._released_decode(meta,obs(1,4),False,'NoQuery')
    check('no_request_no_hidden_direction_'+str(i),no['bit']==0 and no['source'] is None)
    check('second_TC_receives_released_bit_'+str(i),m._second_datum({'ordinal':i,'sample_register':{'ordinal':i,'question_applied_and_signature':True,'released_bit':decoded['bit'],'release_source':decoded['source']}})==decoded['bit'])
rejects('no_arbitrary_path_plan',lambda:m.validate_plan('/tmp/plan.json',p))
bad=json.loads(encoded); bad['permutation']=list(range(12)); rejects('no_retuned_permutation',lambda:m.validate_plan(m._canon(bad).decode(),p))
bad=json.loads(encoded); bad['samples'][0]['observation']['direction']=[-1,0,0]; rejects('changed_source_hash_rejected',lambda:m.validate_plan(m._canon(bad).decode(),p))
bad=json.loads(encoded); bad['samples'][0]['observation']['direction']=[-1,0,0]; bad['samples'][0]['observation_sha256']=m._sha(m._canon(bad['samples'][0]['observation'])); rejects('NULL_source_no_expected_fallback',lambda:m.validate_plan(m._canon(bad).decode(),p))
class Runtime: snapshot_metadata_entries=[]
class World: runtime=Runtime()
class Adapter: world=World()
check('no_KEY_dependencies_absent_without_native',m.operational_dependencies(Adapter(),None)['present'] is False)
check('no_KEY_uncertainty_false_without_native',m.uncertain(Adapter()) is False)
check('no_DEE_after_all_pures',not any(k=='dee_thinking' or k.startswith('dee_thinking.') for k in sys.modules))
result={'schema':'DEE.PI09.selective_consultation.pure_contract_tests.R01','passed':True,'checks':checks,'count':len(checks),'Native_executed':False,'DEE_imported':False,'fixture_MOCK_ONLY_NOT_NATIVE':True,'material_passivity_tested':False,'compact_plan_bytes':len(encoded.encode()),'transport_envelope_bytes':len(m._canon({'operacion':'sesion','actuador':'closed','retorno':'real','situaciones':[{'modo':m.PREPARE,'brazo':'always_desacoplado','plan':encoded}]})),'module_sha256':m._sha((H/'pi09_consulta_selectiva_R01.py').read_bytes()),'protocol_sha256':ph,'literal_C_sha256':m.SOURCE_SHA,'source_adapter_anchor_count':n}
out=H.parent/'control/PRUEBAS_PURAS_CONSULTA_PI09_R03.json'
with out.open('x',encoding='utf8') as f: json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':True,'checks':len(checks),'output':str(out),'sha256':m._sha(out.read_bytes())}))
