"""Bounded packaged-renderer attempts, without opening Word or altering staged DOCX."""
from pathlib import Path
import datetime,hashlib,json,subprocess
P=Path(__file__).resolve().parents[1];D=P/'documentos'
PY=Path(r'C:\Users\Erik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe')
SCRIPT=Path(r'C:\Users\Erik\.codex\plugins\cache\openai-primary-runtime\documents\26.1104.22356\skills\documents\render_docx.py')
def main():
 out=D/'RENDER_PI04_1_31.json';assert not out.exists();rows=[]
 for file in sorted((D/'staging_1_31_R01').glob('*.docx')):
  label='Manual'if'DCS11_MM_001'in file.name else'Compendium';folder=D/('render_'+label+'_1_31')
  args=[str(PY),str(SCRIPT),str(file),'--output_dir',str(folder),'--emit_pdf']
  before=file.read_bytes()
  try:
   r=subprocess.run(args,capture_output=True,encoding='utf8',timeout=45);status='COMPLETED'if r.returncode==0 else'FAILED'
   stdout,stderr,exitcode=r.stdout,r.stderr,r.returncode
  except subprocess.TimeoutExpired as e:status='TIMEOUT';stdout=str(e.stdout or'');stderr=str(e.stderr or'');exitcode=None
  (D/(label+'_RENDER_stdout.txt')).write_text(stdout,encoding='utf8');(D/(label+'_RENDER_stderr.txt')).write_text(stderr,encoding='utf8')
  assert file.read_bytes()==before
  rows.append({'document':str(file),'sha256':hashlib.sha256(before).hexdigest(),'command':args,'result':status,'exit_code':exitcode,'stderr':stderr,'rendered_pages':[str(x)for x in folder.glob('page-*.png')],'DOCX_unchanged':True})
 result={'schema':'DEE.PI04.actual_packaged_renderer_attempts.v1','status':'NOT_VALIDATED','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'attempts':rows,'manual_sha256':next(x['sha256']for x in rows if'DCS11_MM_001'in x['document']),'rendered_pdf':None,'reviewed_images':[],'scope':'Actual bounded render attempts; structural validation is separate. No visual approval, page-image inspection or rendering success is invented. No Word COM process or protected application was opened.','new_Native_ticks':0}
 with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps({'proof':str(out),'status':'NOT_VALIDATED','attempts':[(x['document'],x['result'],x['exit_code'])for x in rows]}))
if __name__=='__main__':main()
