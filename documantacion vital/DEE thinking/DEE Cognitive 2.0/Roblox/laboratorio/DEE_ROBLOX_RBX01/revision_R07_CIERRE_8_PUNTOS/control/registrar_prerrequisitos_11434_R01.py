"""Record two already-completed failed GETs and read host RAM; no new HTTP."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'control/runner_comparador_v3_R06_RAM.py';raw=source.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='2ae529519d7a41fbfcf76710eef4be3c985d6408a4a864855b72800578c2af03'
tree=ast.parse(raw.decode('utf-8'))
function=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='host_memory')
namespace={};exec(compile(ast.Module(body=[function],type_ignores=[]),str(source),'exec'),namespace)
memory=namespace['host_memory']()
daemon=ROOT/'comparadores/SERVIDOR_MODELO_V3_R05.jsonl'
rows=[json.loads(x)for x in daemon.read_text('utf-8').splitlines()if x.strip()]
closed=[x for x in rows if x.get('kind')=='CLOSED'];assert len(closed)==1 and closed[0]['server_exit_code']==0
report={'schema':'DEE.R07.E5.ExistingLoopbackPrerequisites.R01',
    'inspection_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'GETs_already_attempted':[
        {'url':'http://127.0.0.1:11434/api/version','curl_result':'Connection failure, curl7','elapsed_ms_reported':2473},
        {'url':'http://127.0.0.1:11434/api/tags','curl_result':'Connection failure, curl7','elapsed_ms_reported':2460}],
    'HTTP_attempts':2,'HTTP_retries':0,'other_ports_scanned':False,'default_service_accessible':False,
    'current_service_model_verified':False,'current_service_model_manifest_comparison':'NOT_POSSIBLE_NO_RESPONSE',
    'local_reference_manifest_sha256':'a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72',
    'host_memory_after_owned12728_closed':memory,'owned_daemon_close':closed[0],
    'original_IA_prestart_rejection_preserved':True,'original_available_physical_bytes':3333148672,
    'frozen_start_minimum_physical_bytes':3758096384,
    'model_prompts_load_download_or_configuration_calls':0,'Native_MCP_World_calls':0,
    'conclusion':'No reachable existing Ollama service at the two explicitly requested localhost11434 endpoints. No running model identity can be inferred from a historical label or the stored reference manifest.'}
target=ROOT/'analisis/E5_PREREQUISITOS_11434_R01.json'
with target.open('x',encoding='utf-8')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'output':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
    'available_physical_bytes':memory['available_physical_bytes'],
    'system_available_commit_bytes':memory['system_available_commit_bytes'],
    'service_accessible':False,'model_verified':False,'HTTP_attempts':2,'model_calls':0},ensure_ascii=False))
