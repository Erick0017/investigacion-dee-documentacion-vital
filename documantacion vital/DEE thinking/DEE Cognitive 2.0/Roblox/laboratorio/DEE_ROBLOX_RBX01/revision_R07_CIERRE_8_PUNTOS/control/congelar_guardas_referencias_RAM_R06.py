"""Write the prospective host-only reference guard/freeze; no experiment."""
from pathlib import Path
import datetime
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
files=['control/runner_comparador_v3_R06_RAM.py','control/test_runner_RAM_R06_sintetico.py',
    'control/runner_comparador_v3_R05.py','control/world_comprimido_v3_R05.py',
    'comparadores/backends_v3_R05.py','comparadores/cliente_modelo_v3_R05.py',
    'comparadores/servidor_modelo_v3_R05.py']
members=[]
for name in files:
    data=(ROOT/name).read_bytes()
    members.append({'file':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
old=next(x for x in members if x['file']=='control/runner_comparador_v3_R05.py')
assert old['sha256']=='76bdd69a2768c42a3f2758b414408362672568d54f1f5f40da341962e75aa72d'
doc={'schema':'DEE.R07.E5.ProspectiveHostSafety.R06','status':'PREPARED_NOT_MATERIAL_EXECUTED',
    'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'approved_physical_start_minimum_bytes':3758096384,'applies_to':['PROGRAMMED','CONVENTIONAL_AI'],
    'boundary_stop_available_physical_below_bytes':1073741824,
    'deadline_new_episodes_utc':'2026-11-17T02:00:00Z','hard_finish_utc':'2026-11-17T03:07:00Z',
    'administrative_start_unchanged':'2026-11-16T15:07:00Z','budget_reset':False,
    'host_measurements':{'physical':'Win32.GlobalMemoryStatusEx ullAvailPhys/ullTotalPhys',
        'reported_process_commit_fields':'ullAvailPageFile/ullTotalPageFile raw; may be process-limited, not physical RAM',
        'system_commit':'Win32.GetPerformanceInfo CommitTotal/CommitLimit times PageSize, available=(limit-total)*PageSize',
        'sampling':['INITIAL_PRECHECK before World/policy opening','BEFORE_BEGIN for every prospective episode'],
        'measurement_failure':'Fail closed; no invented available-memory number'},
    'stop_contract':{'initial_below_minimum':'PREFLIGHT_RAM_REJECTED.json and samples; no World/policy opened',
        'boundary_below_1GiB':'Break before BEGIN; normal policy checkpoint, World export and closure; actual completed cursor and denominator only',
        'reason':'HOST_FREE_RAM_BELOW_1GiB','daemon_stop_written':False,'automatic_retry':False,
        'zero_episode_block':'Valid administrative closed baseline, not an experimental failure or successful new opportunity'},
    'unchanged':{'policy':'comparadores/backends_v3_R05.py','client':'comparadores/cliente_modelo_v3_R05.py',
        'daemon':'comparadores/servidor_modelo_v3_R05.py','model':'llama3.2:latest',
        'model_manifest_sha256':'a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72',
        'temperature':0,'seed':404271,'context':8192,'num_predict':128,'threads':4,
        'global_quota':'comparadores/CUOTA_LLM_V3.json','global_call_limit':160,
        'daemon_job_limit_bytes':6442450944,'Native_policy_decoder_or_criteria_changed':False},
    'memory_interpretation':'R06 model peak_job_committed_bytes3619258368 was Job commitment, not RSS. It does not establish physical RAM minimum. Fixed3.5GiB start margin is prospective host administration, not a scientific claim.',
    'synthetic_verification':{'tests':5,'passed':5,'observed_seconds':2.857,
        'cases':['No implicit/lowered margin','Normal requested horizon','Prestart rejection without opening World/policy',
                 'Clean stop after one without beginning second','Clean zero-episode stop without BEGIN'],
        'Native_calls':0,'MCP_calls':0,'model_calls':0},
    'members':members}
target=ROOT/'protocolo/CONGELADO_REFERENCIAS_RAM_R06.json'
assert not target.exists()
target.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'protocol':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
    'runner':members[0],'Native_calls':0,'model_calls':0},ensure_ascii=False))
