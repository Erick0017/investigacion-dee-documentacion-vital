"""Explicit finite host/file/loopback preflight only; no game/model decision."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import socket
import sys
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'control/runner_comparador_v3_R06_RAM.py'
assert hashlib.sha256(path.read_bytes()).hexdigest()=='2ae529519d7a41fbfcf76710eef4be3c985d6408a4a864855b72800578c2af03'
spec=importlib.util.spec_from_file_location('_E5_RAM_PREFLIGHT',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
memory=module.host_memory()
parent=ROOT/'native/MAIN/WORLD_PADRE_PAR28.json';raw=parent.read_bytes();world=json.loads(raw)
assert world['native_tick']==991187 and world['S']['completedCycles']==28
assert world['S']['permissionStock']==164 and world['S']['delivered']==3 and world['S']['resourceCount']==3
assert hashlib.sha256(raw).hexdigest()=='48544f655382bdf97b4930200158e35371d878c29d17c1ce918077aa27cf6930'
fresh=['comparadores/PROGRAMMED_R06','comparadores/CONVENTIONAL_AI_R06',
    'evidencia/PROGRAMMED_R06_BLOQUE_01','evidencia/CONVENTIONAL_AI_R06_BLOQUE_01',
    'comparadores/SERVIDOR_MODELO_V3_R05.jsonl','comparadores/ollama_V3_R05.stop',
    'comparadores/ollama_isolated_V3_R05_stdout.log','comparadores/ollama_isolated_V3_R05_stderr.log',
    'comparadores/CUOTA_LLM_V3.lock','comparadores/CUOTA_LLM_V3.json.writing']
presence={name:(ROOT/name).exists()for name in fresh}
assert not any(presence.values()),'Existing history, lifecycle or unresolved lock; preserve before new experiment'
quota=ROOT/'comparadores/CUOTA_LLM_V3.json'
q=json.loads(quota.read_text('utf-8'))if quota.exists()else None
if q is not None:assert q['limit']==160 and q['model_manifest_sha256']=='a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72'
port=None
try:
    with socket.create_connection(('127.0.0.1',11435),timeout=3):port='EXISTING_LISTENER'
except ConnectionRefusedError:port='NO_LISTENER_CONNECTION_REFUSED'
assert port=='NO_LISTENER_CONNECTION_REFUSED','Endpoint not proved free; no server restart or request replay'
exe=Path('C:/Users/Erik/AppData/Local/Programs/Ollama/ollama.exe')
blob=ROOT.parent/'revision_R05_C02/comparadores/modelos/blobs/sha256-dde5aa3fc5ffc17176b5e8bdc82f587b24b2678c6c66101bf7da77af9f7ccdff'
assert exe.is_file()and blob.is_file()and blob.stat().st_size==2019377376
result={'schema':'DEE.R07.E5.MaterialPreflight.R06','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'host_memory':memory,'minimum_start_available_physical_bytes':3758096384,
    'host_margin_met':memory['available_physical_bytes']>=3758096384,
    'fresh_path_presence':presence,'quota_existing':q is not None,'quota_used_before':q['used']if q else None,
    'quota_reset':False,'endpoint':port,'model_executable_present':True,'model_blob_bytes':blob.stat().st_size,
    'download_calls':0,'parent_world_sha256':hashlib.sha256(raw).hexdigest(),'parent_world_bytes':len(raw),
    'Native_calls':0,'Studio_calls':0,'model_calls':0}
target=ROOT/'control/E5_PREFLIGHT_R06/03_HOST_FILES_LOOPBACK.json'
with target.open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(result,ensure_ascii=False))
