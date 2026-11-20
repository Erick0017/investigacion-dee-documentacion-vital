"""Pure file preparation of a new owned Ollama host-cache condition; no inference."""
from pathlib import Path
import ast,hashlib,json,datetime
root=Path(__file__).resolve().parents[1]
source=root/'comparadores/servidor_modelo_v3_R08.py'
dest=root/'comparadores/servidor_modelo_v3_R10KV.py'
proof=root/'control/SERVIDOR_KV_R10_PREPARADO.json'
if dest.exists()or proof.exists():raise ValueError('Fresh source/proof required; preserve previous preparation')
raw=source.read_bytes();digest=hashlib.sha256(raw).hexdigest()
freeze=json.loads((root/'video/FUENTES_CONGELADAS_CIERRE_FINITO_R09.json').read_text('utf8'))
def entries(x):
    if isinstance(x,dict):
        if 'sha256'in x and any(str(v).replace('\\','/').endswith('comparadores/servidor_modelo_v3_R08.py')for v in x.values()if isinstance(v,str)):yield x
        for v in x.values():yield from entries(v)
    elif isinstance(x,list):
        for v in x:yield from entries(v)
pins=list(entries(freeze))
if len(pins)!=1 or pins[0]['sha256']!=digest:raise ValueError('Exact frozen R08 server source required')
text=raw.decode('utf8')
needle='    os.environ.update(settings)'
if text.count(needle)!=1:raise ValueError('Unique process-local environment installation required')
text=text.replace('_R08','_R10KV')
text=text.replace(needle,"    settings.update({'OLLAMA_KV_CACHE_TYPE':'q8_0','OLLAMA_FLASH_ATTENTION':'1'})\n"+needle)
needle2='cloud_disabled=True,keys_copied=False,global_environment_changed=False)'
if text.count(needle2)!=1:raise ValueError('Unique startup record required')
text=text.replace(needle2,"requested_KV_cache_type='q8_0',requested_Flash_attention='1',cache_binary_equivalence_claimed=False,"+needle2)
ast.parse(text)
with dest.open('x',encoding='utf8',newline='')as f:f.write(text)
data={'schema':'DEE.R07.LLMHostKVCondition.Prepared.R10','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'source':str(source),'source_sha256':digest,'output':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
    'requested_KV_cache_type':'q8_0','requested_flash_attention':'1','runtime_effectiveness':'NOT_YET_CHECKED',
    'changes':['fresh lifecycle names only','two process-local cache environment settings','startup declarations'],
    'same_weights_context_prompt_policy_seed_thread_quota_guards':True,'same_Native_kernel_Thinking':True,
    'may_change_float_responses':True,'not_learned_policy_adaptation':True,
    'last_new_epoch':1794934800,'hard_close_epoch':1794938400,'Native_calls':0,'model_calls':0}
with proof.open('x',encoding='utf8')as f:json.dump(data,f,ensure_ascii=False,indent=2)
print(json.dumps(data,ensure_ascii=True))
