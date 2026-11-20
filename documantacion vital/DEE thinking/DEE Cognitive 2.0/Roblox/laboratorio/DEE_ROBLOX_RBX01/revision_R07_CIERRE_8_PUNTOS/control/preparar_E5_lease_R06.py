"""New FS-only E5 infrastructure lease. Preserves every previously used source."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
mapping=[('comparadores/cliente_modelo_v3_R05.py','comparadores/cliente_modelo_v3_R06.py'),
    ('comparadores/servidor_modelo_v3_R05.py','comparadores/servidor_modelo_v3_R06.py'),
    ('comparadores/backends_v3_R05.py','comparadores/backends_v3_R06.py'),
    ('control/runner_comparador_v3_R06_RAM.py','control/runner_comparador_v3_R07_RAM.py')]
changes={
    mapping[0][0]:[('1794880800','1794902400'),('2026-11-17 02:00 UTC','2026-11-17 08:00 UTC')],
    mapping[1][0]:[('1794884820','1794906420'),('1794880800','1794902400'),
        ('2026-11-17 03:07 UTC','2026-11-17 09:07 UTC'),('2026-11-17 02:00 UTC','2026-11-17 08:00 UTC'),
        ('tmp_ollama_V3_R05','tmp_ollama_V3_R06'),('SERVIDOR_MODELO_V3_R05','SERVIDOR_MODELO_V3_R06'),
        ('ollama_V3_R05.stop','ollama_V3_R06.stop'),('ollama_isolated_V3_R05','ollama_isolated_V3_R06'),
        ('R07.CIERRE8.MODEL.V3.R05','R07.CIERRE8.MODEL.V3.R06')],
    mapping[2][0]:[('cliente_modelo_v3_R05','cliente_modelo_v3_R06')],
    mapping[3][0]:[('world_comprimido_v3_R05','world_comprimido_v3_R06'),('backends_v3_R05','backends_v3_R06'),
        ('1794880800','1794902400'),('1794884820','1794906420'),
        ('2026-11-17 02:00 UTC','2026-11-17 08:00 UTC'),("'revision':'R06_RAM'","'revision':'R07_RAM'")]}
records=[];originals={};diffs=[]
for old_name,new_name in mapping:
    old=ROOT/old_name;new=ROOT/new_name;data=old.read_bytes();originals[old_name]=data
    text=data.decode('utf-8-sig');before=text
    for source,target in changes[old_name]:
        assert source in text,(old_name,source)
        text=text.replace(source,target)
    if old_name==mapping[3][0]:
        marker="    initial_memory=memory_sample('INITIAL_PRECHECK',state['boundary']['next_opportunity'])\n"
        assert text.count(marker)==1
        extra="""    # Administrative admission only: wait finitely before opening World/policy.
    wait_started=time.monotonic();wait_deadline=wait_started+120.0
    while (initial_memory['available_physical_bytes']<a.min_start_free_bytes and
           time.monotonic()<wait_deadline and time.time()<CUTOFF):
        remaining=max(0.0,wait_deadline-time.monotonic())
        record('HOST_START_RAM_WAIT',remaining_seconds=remaining,minimum_bytes=a.min_start_free_bytes,
            available_physical_bytes=initial_memory['available_physical_bytes'],no_World_or_policy_opened=True)
        time.sleep(min(5.0,remaining))
        initial_memory=memory_sample('INITIAL_PRECHECK_WAIT',state['boundary']['next_opportunity'])
    need(time.time()<CUTOFF,'Prospective cutoff during finite RAM admission; no World/policy opened')
"""
        text=text.replace(marker,marker+extra)
        record_marker="                   'daemon_stop_written':False})"
        assert text.count(record_marker)==1
        text=text.replace(record_marker,"                   'start_RAM_wait_limit_seconds':120,'daemon_stop_written':False})")
    assert not new.exists(),str(new)
    ast.parse(text);compile(text,str(new),'exec')
    new.write_text(text,encoding='utf-8',newline='\n')
    records.append({'source':old_name,'original_sha256':hashlib.sha256(data).hexdigest(),
        'new':new_name,'new_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'bytes':new.stat().st_size})
    diffs.extend(difflib.unified_diff(before.splitlines(True),text.splitlines(True),fromfile=old_name,tofile=new_name))
    # Exact policy function ASTs are preserved. Only administrative module constants/imports vary.
    if old_name in(mapping[0][0],mapping[2][0]):
        old_tree=ast.parse(before);new_tree=ast.parse(text)
        old_defs=[n for n in old_tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
        new_defs=[n for n in new_tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
        a=ast.dump(ast.Module(body=old_defs,type_ignores=[]),include_attributes=False)
        b=ast.dump(ast.Module(body=new_defs,type_ignores=[]),include_attributes=False)
        if old_name==mapping[2][0]:b=b.replace('cliente_modelo_v3_R06.py','cliente_modelo_v3_R05.py')
        assert a==b,'Policy AST changed'
for name,data in originals.items():assert(ROOT/name).read_bytes()==data,'Original modified'
diff_path=ROOT/'control/E5_LEASE_R06_DIFF.txt';assert not diff_path.exists();diff_path.write_text(''.join(diffs),'utf-8')
meta={'schema':'DEE.R07.E5.NewInfrastructureLease.R06','status':'PREPARED_FS_ONLY_NOT_STARTED',
    'new_episode_cutoff_utc':'2026-11-17T08:00:00Z','hard_finish_utc':'2026-11-17T09:07:00Z',
    'old_rejection_and_lifecycle_preserved':True,'quota_path':'comparadores/CUOTA_LLM_V3.json',
    'quota_limit':160,'quota_reset':False,'model':'llama3.2:latest',
    'model_manifest_sha256':'a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72',
    'temperature':0,'context':8192,'seed':404271,'daemon_Job_limit_bytes':6442450944,
    'minimum_start_free_physical_bytes':3758096384,'stop_boundary_below_physical_bytes':1073741824,
    'administrative_RAM_wait_max_seconds':120,'no_World_or_policy_during_wait':True,
    'policy_and_decoder_semantics_changed':False,
    'allowed_diff':'Prospective dates, imports/source pins, own infra lifecycle names; finite prestart host-RAM admission loop only',
    'shared_model_store_stays_revision_R05_C02':True,'records':records,
    'AST_policy_functions_identical':True,'diff_path':str(diff_path),'Native_MCP_model_calls':0}
target=ROOT/'control/E5_LEASE_R06_PREPARADO.json';assert not target.exists()
target.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'record':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'files':records},ensure_ascii=False))
