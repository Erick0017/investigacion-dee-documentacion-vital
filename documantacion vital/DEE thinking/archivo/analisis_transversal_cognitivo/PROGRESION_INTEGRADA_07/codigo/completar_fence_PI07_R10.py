"""Run all frozen recalculators; accept only successful CLI SystemExit0."""
from pathlib import Path
import runpy,subprocess,sys,json
P=Path(__file__).resolve().parents[1];W=P.parents[4];root=W/'p7v131721'
m=runpy.run_path(str(P/'codigo/empaquetar_PI07_final_R07.py'),run_name='static_fence_source')
source=m['FENCE'];needle=" sys.argv=[str(script),*args];runpy.run_path(str(script),run_name='__main__')"
replacement=" sys.argv=[str(script),*args]\n try:runpy.run_path(str(script),run_name='__main__')\n except SystemExit as e:\n  if e.code not in (None,0):raise"
if source.count(needle)!=1:raise ValueError('Exact composition point required')
f=root/'fence_all_R10.py';f.open('x',encoding='utf8').write(source.replace(needle,replacement))
command=[sys.executable,'-I','-B','-X','utf8',str(f),str(root/'x'),str(root/'r2'),str(root/'AUDIT_R10.json')]
r=subprocess.run(command,cwd=root/'x',capture_output=True,text=True,encoding='utf8',timeout=240)
(root/'fence_R10_stdout.txt').write_text(r.stdout,encoding='utf8');(root/'fence_R10_stderr.txt').write_text(r.stderr,encoding='utf8')
print(json.dumps({'returncode':r.returncode,'Native_executed':False,'stderr':r.stderr[-3000:],'directory':str(root/'r2')}))
raise SystemExit(r.returncode)
