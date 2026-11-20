"""Release only this owned local model after its terminal failed HTTP request.

No prompts, inference, history modification, quota reset or DEE access.
"""
from pathlib import Path
import subprocess,os,json,datetime
root=Path(__file__).resolve().parents[1]
out=root/'comparadores/LIBERACION_MODELO_CALIENTE_R08.json'
if out.exists():raise RuntimeError('Preserve prior proof; no repeated lifecycle action')
state=json.loads((root/'comparadores/CONVENTIONAL_AI_R07_HISTORIA_01/POLICY_STATE_V3.json').read_text('utf8'))
env=os.environ.copy();env['OLLAMA_HOST']='127.0.0.1:11435';env['OLLAMA_NO_CLOUD']='1'
exe=Path('C:/Users/Erik/AppData/Local/Programs/Ollama/ollama.exe')
reply=subprocess.run([str(exe),'stop','llama3.2:latest'],env=env,cwd=root,
    stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf8',errors='replace',
    timeout=45,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
data={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'action':'UNLOAD_OWN_LOCAL_MODEL_NOT_INFERENCE','endpoint':'127.0.0.1:11435',
    'model':'llama3.2:latest','exit_code':reply.returncode,'stdout':reply.stdout,'stderr':reply.stderr,
    'history_preserved':True,'quota_not_reset':True,'Native_ticks':0,'inference_requests':0,
    'old_failed_request_is_not_resent':True}
with out.open('x',encoding='utf8')as f:json.dump(data,f,ensure_ascii=False,indent=2)
print(json.dumps(data,ensure_ascii=False))
if reply.returncode:raise SystemExit(reply.returncode)
