"""Attempt real skill renderer, bounded; never touches Word or DEE."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
P=Path(__file__).resolve().parents[1];D=P/'documentos';O=D/'INTENTO_RENDER_EDICION_1_37_PI09.json'
PY=Path(r'C:\Users\Erik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe')
SCRIPT=Path(r'C:\Users\Erik\.cache\codex-runtimes\codex-primary-runtime\plugins\openai-primary-runtime\plugins\documents\skills\documents\render_docx.py')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not O.exists();files=sorted((D/'edicion_1_37').glob('*.docx'));manual=next(p for p in files if 'Manual_Maestro_DCS11' in p.name)
cmd=[str(PY),str(SCRIPT),str(manual),'--output_dir',str(D/'render_1_37'),'--emit_pdf']
out=D/'RENDER_1_37.stdout.txt';err=D/'RENDER_1_37.stderr.txt';failure=None
with out.open('x',encoding='utf8')as so,err.open('x',encoding='utf8')as se:
 try:r=subprocess.run(cmd,cwd=P,stdout=so,stderr=se,timeout=60);code=r.returncode
 except subprocess.TimeoutExpired as ex:code=None;failure={'type':type(ex).__name__,'message':str(ex),'scope':'Only this owned renderer, no Word/DEE process'}
images=list((D/'render_1_37').glob('page-*.png'))if(D/'render_1_37').exists()else[]
v={'schema':'DEE.PI09.actual_DOCX_render_attempt.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),'command':cmd,'renderer_sha256':sha(SCRIPT),'document':{'path':str(manual),'sha256':sha(manual)},'exit_code':code,'timeout':failure,'stdout':{'path':str(out),'sha256':sha(out)},'stderr':{'path':str(err),'sha256':sha(err),'text':err.read_text('utf8')},'rendered_pages':len(images),'visual_review_completed':False,'other_document_visual_status':'Not visually validated. Same unavailable conversion dependency if the first real attempt fails. Structural validation is separate.','original_or_foreign_Word_process_touched':False,'Native_executed':False}
O.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'proof':str(O),'exit_code':code,'rendered_pages':len(images),'stderr_tail':v['stderr']['text'][-1000:]}))
