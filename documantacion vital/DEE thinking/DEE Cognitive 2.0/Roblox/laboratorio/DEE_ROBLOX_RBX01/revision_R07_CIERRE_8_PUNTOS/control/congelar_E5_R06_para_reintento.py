"""Seal prepared reference infra only. Does not run any server/World/policy."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
prepared=ROOT/'control/E5_LEASE_R06_PREPARADO.json'
meta=json.loads(prepared.read_text('utf-8'))
for row in meta['records']:
    for field,hash_field in(('source','original_sha256'),('new','new_sha256')):
        raw=(ROOT/row[field]).read_bytes();assert hashlib.sha256(raw).hexdigest()==row[hash_field]
        ast.parse(raw.decode('utf-8-sig'));compile(raw.decode('utf-8-sig'),row[field],'exec')
extra=['control/world_comprimido_v3_R06.py','control/test_E5_lease_R06_sin_material.py']
members=[]
for name in extra:
    raw=(ROOT/name).read_bytes();members.append({'file':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
record={'schema':'DEE.R07.E5.InfrastructureFreeze.R06','status':'PREPARED_NOT_STARTED',
    'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'prepared':{'file':str(prepared),'sha256':hashlib.sha256(prepared.read_bytes()).hexdigest()},
    'new_files':meta['records'],'extra_source_pins':members,
    'verification':{'AST_and_compile_without_execution':'4new+4preserved sources',
        'client_and_backend_policy_function_AST_identical':True,'synthetic_new_tests':3,'passed':3,'observed_seconds':1.474,
        'cases':['Finite120s wait, no World/policy until sufficient RAM','Wait expiry preserves rejection without opening World/policy',
            'Dates/minStart/floor/source/strategy invariance'],
        'old_RAM5fixtures_previously_passed_not_rerun':True},
    'unchanged':['model llama3.2:latest and manifest a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72',
        'temperature0/context8192/seed404271','global CUOTA_LLM_V3.json160 no reset',
        'minimum physical start3758096384/floor1073741824/daemonJob6442450944',
        'public inputs/strategy/phase grammar/arithmetic output handling/NULL decoding'],
    'server_argv':['python','-I','-B','-X','utf8','comparadores/servidor_modelo_v3_R06.py',
        '--run-local-server','--deadline-utc-epoch','1794906420'],
    'runner_argv':['python','-I','-B','-X','utf8','control/runner_comparador_v3_R07_RAM.py',
        '--execute-root-only','--participant','CONVENTIONAL_AI','--destination','comparadores/CONVENTIONAL_AI_R06',
        '--world','native/MAIN/WORLD_PADRE_PAR28.json','--output','evidencia/CONVENTIONAL_AI_R06_BLOQUE_02',
        '--studio-id','522e9816-883b-4c8b-88cd-04de5607b901','--expected-place','DEE_RBX01_R07_NATIVE.rbxlx',
        '--session','R07_CONVENTIONAL_AI_R06_02','--stop-cycle','46','--min-start-free-bytes','3758096384'],
    'new_episode_cutoff_utc':'2026-11-17T08:00:00Z','hard_finish_utc':'2026-11-17T09:07:00Z',
    'own_new_daemon_stop_file':'comparadores/ollama_V3_R06.stop',
    'safety':'No start until Root confirms Native0tick lease operation closed. Same Studio fresh Play, unused output/policy directory, no pending operation, host guard unchanged.',
    'previous_R05_sources_lifecycle_and_RAM_rejection_preserved':True,
    'Native_MCP_model_OS_measurement_calls':0}
target=ROOT/'control/E5_LEASE_R06_CONGELADO.json'
with target.open('x',encoding='utf-8')as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'freeze':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
    'new_files':meta['records'],'status':'PREPARED_NOT_STARTED'},ensure_ascii=False))
