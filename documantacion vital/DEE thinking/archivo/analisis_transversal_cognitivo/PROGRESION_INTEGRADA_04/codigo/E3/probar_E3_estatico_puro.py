"""Pure source/contract tests; mocks are explicit and do not load Native."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,types
P=Path(__file__).resolve().parents[2];C=P.parents[2]/'DEE Cognitive 2.0';HERE=Path(__file__).resolve().parent
out=P/'control/E3_FUENTES_Y_PRUEBA_PURA_R01.json'
if out.exists():raise FileExistsError('Preserve prior static proof')
def imp(name,file):
    spec=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
pure=imp('E3_PURE_SIGNAL_ONLY',HERE/'e3_retorno_desacoplado_R01.py');module=imp('E3_MOCK_OWNER_ONLY',HERE/'pi04_e3_contingencia.py')
source=C/'sistema/capacidades/pi03_tarea_diferida_R02.py';assert hashlib.sha256(source.read_bytes()).hexdigest()==module.SOURCE_TASK_SHA
source_text=source.read_text(encoding='utf-8');old=next(n for n in ast.parse(source_text).body if isinstance(n,ast.FunctionDef)and n.name=='opportunity')
new_text=(HERE/'pi04_e3_contingencia.py').read_text(encoding='utf-8');new=next(n for n in ast.parse(new_text).body if isinstance(n,ast.FunctionDef)and n.name=='_op_body')
new_body=ast.get_source_segment(new_text,new)
reverse={
 'def _op_body(a, directory):':'def opportunity(a, directory):',
 '    _e3_prequery(a, calendar, before_banks, start)\n':'',
 'returned_failed = _e3_feedback(a, effect["failed"], calendar, before_banks, start)':'returned_failed = False if m["control"] == "return_nonfailure" else effect["failed"]',
 '"control": "PI04_E3_" + _e3_get(a)["arm"], "before_tick": start':'"control": m["control"], "before_tick": start'}
for a,b in reverse.items():assert new_body.count(a)==1,a;new_body=new_body.replace(a,b)
assert ast.dump(ast.parse(new_body),include_attributes=False)==ast.dump(ast.parse(ast.get_source_segment(source_text,old)),include_attributes=False)
checks=['exact_PI03_source_hash','physical_body_AST_equal_after_four_declared_changes','module_imports_no_DEE_or_Native','no_kernel_or_PI03_source_edits']
state={'life':module.PREFIX+'MAIN_01','task':{'control':'real','serie':'continuous','ready':True,'opportunity':24,'schedule':[{}]*26,'pending':None,'uncertain':False,'halted_reason':None,'supply_pending':None}}
runtime=types.SimpleNamespace(snapshot_metadata_entries=[],dimension=67)
owner=types.SimpleNamespace(tick=775355,world=types.SimpleNamespace(runtime=runtime))
task=types.SimpleNamespace(__file__=str(source),_guard=lambda a,d=None,material=True:({},'MOCK_HASH',{'origin':[19,54,5]}, {'life_id':state['life']}),_get=lambda a:state['task'])
module._task=lambda:task;module._pure=lambda:pure
fake_package=types.ModuleType('capacidades');fake_package.pi03_proteccion_cola_OP3=types.SimpleNamespace(get=lambda a:{'ready':True,'uncertain':False})
prior=sys.modules.get('capacidades');sys.modules['capacidades']=fake_package
try:
    real={'modo':module.ADMIT,'brazo':'real'};module.validate(owner,real);checks.append('strict_source_admission_mock')
    assert module.operational_dependencies(owner,'IGNORED_NO_KEY')is False and module.uncertain(owner)is False;checks.append('absence_is_readonly_false')
    records=[]
    for i,s in enumerate(module.SPECS):
        k=s['delay_laps'];read=900000+782*i;contact=read+67*k+2
        records.append({'ordinal':i,'failed':i in(2,6,10,14),'calendar':{'query_tick':read-6,'query_read_tick':read,'outcome_injection_tick':contact-2,'contact_tick':contact,'delay_laps':k,'reference_contact_phase':391}})
    plan=pure.build_permuted_plan(records,source_identity={'mock_source':'SYNTHETIC_NOT_NATIVE','source_tick':775355})
    control={'modo':module.ADMIT,'brazo':'desacoplado','plan':pure.pack_plan(plan)};module.validate(owner,control);checks.append('eighteen_slot_control_literal')
    transport={'uncompressed_plan_bytes':len(pure.canonical(plan)),'encoded_plan_bytes':len(control['plan'].encode('utf-8')),'literal_canonical_bytes':len(pure.canonical(control)),'literal_default_JSON_UTF8_bytes':len(json.dumps(control,ensure_ascii=False).encode('utf-8'))}
    assert transport['literal_default_JSON_UTF8_bytes']<8192 and pure.unpack_plan(control['plan'])==plan;checks.append('bounded18plan_transport_below8192_roundtrip')
    assert len(module.SPECS)==18 and sum(r['cantidad']for r in module.SUPPLIES)==16;checks.append('two_preserved_plus_sixteen_explicit_offers')
    replay=[pure.replay_signal(plan,i,r['calendar'])for i,r in enumerate(records)]
    assert sum(replay)==sum(r['failed']for r in records);checks.append('same_failure_nonfailure_dose_by_phase_delay')
    assert plan['plan']['source_signal_changes']>0;checks.append('nontrivial_fixed_permutation')
    assert pure.summarize_manipulation(plan,[r['failed']for r in records])['manipulation_effective'];checks.append('posthoc_manipulation_measurement_not_action')
    refusals=[]
    def bad(label,fn):
        try:fn()
        except(ValueError,KeyError,TypeError):refusals.append(label)
        else:raise AssertionError('Expected refusal '+label)
    for life in('ECI02_PI03_MAIN','ECI02_PI02_MAIN','ECI02_PI03_REPRO_OTHER_01'):
        state['life']=life;bad('life_'+life,lambda:module.validate(owner,real))
    state['life']=module.PREFIX+'MAIN_01'
    owner.tick=775356;bad('source_tick',lambda:module.validate(owner,real));owner.tick=775355
    state['task']['pending']={'MOCK':True};bad('pending_task',lambda:module.validate(owner,real));state['task']['pending']=None
    state['task']['opportunity']=0;bad('reset_counter',lambda:module.validate(owner,real));state['task']['opportunity']=24
    bad('arbitrary_plan_file',lambda:module.validate_literal(dict(control,file='C:/private.json')))
    bad('desired_action',lambda:module.validate_literal(dict(real,action=1)))
    bad('calendar_shift',lambda:pure.replay_signal(plan,0,dict(records[0]['calendar'],query_tick=899995)))
    tampered=copy.deepcopy(plan);tampered['plan']['slots'][0]['returned_failed']=not tampered['plan']['slots'][0]['returned_failed'];tampered['sha256']=pure.digest(tampered['plan'])
    bad('edited_plan_rehashed',lambda:pure.validate_plan(tampered))
    bad('bool_coercion',lambda:pure.summarize_manipulation(plan,[1]*18))
    bad('oversized_plan',lambda:pure.unpack_plan('E3Z1:'+'A'*6144))
    bad('arbitrary_path_as_plan',lambda:pure.unpack_plan('D:/plan.json'))
    bad('raw_dictionary_as_transport_plan',lambda:module.validate_literal(dict(control,plan=plan)))
    bad('trailing_compressed_stream',lambda:pure.unpack_plan(control['plan']+'AAAA'))
    proof={'schema':'PI04.E3.static_and_pure_contract.v1','new_native_ticks':0,'actual_DEE_or_Native_imports':0,'checks':checks,'refusals':refusals,
           'synthetic_only':True,'no_CS_or_product_edit':True,'literal_modes':sorted(module.MODES),'count':18,'typical_ticks_per_arm':14076,'hard_max_per_arm':27000,
           'signal_self_test':pure.self_test(),'transport_plan_measurement':transport,'source_PI03_task_sha256':module.SOURCE_TASK_SHA,
           'files':{f.name:{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}for f in(HERE/'pi04_e3_contingencia.py',HERE/'e3_retorno_desacoplado_R01.py')}}
finally:
    if prior is None:sys.modules.pop('capacidades',None)
    else:sys.modules['capacidades']=prior
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(proof,ensure_ascii=False,indent=2))
