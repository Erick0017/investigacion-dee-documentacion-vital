"""Prueba sin Native; prepara recursos propios, ejecuta y evalúa recibos."""
from pathlib import Path
import json,subprocess,sys,shutil
HERE=Path(__file__).resolve().parent;BUILD=HERE.parents[1];WRAPPER=BUILD/'package/codigo_comun/entorno_seguro.py';P313=BUILD/'entorno313/Scripts/python.exe';P312=Path(r'C:\Users\Erik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe')
package=HERE/'paquete';out=HERE/'salida_r02';package.mkdir(exist_ok=True);out.mkdir(exist_ok=True);common=package/'codigo_comun';common.mkdir(exist_ok=True);shutil.copy2(WRAPPER,common/WRAPPER.name)
forbidden=HERE/'archivo_historico_fuera_del_paquete.txt';forbidden.write_text('test-only historical sentinel',encoding='utf8')
allowed=package/'dato.txt';allowed.write_text('allowed',encoding='utf8')
child=r'''
import sys,json,subprocess
from pathlib import Path
forbidden,out,p313=sys.argv[1:4]
blocked=False
try:Path(forbidden).read_text()
except PermissionError:blocked=True
grandcode="import sys,json;from pathlib import Path;ok=False\ntry:Path(sys.argv[1]).read_text()\nexcept PermissionError:ok=True\nprint(json.dumps({'grandchild_blocked':ok,'isolated':sys.flags.isolated,'bytecode':sys.dont_write_bytecode}))"
grand=subprocess.run([p313,'-I','-B','-c',grandcode,forbidden],capture_output=True,text=True,check=True)
Path(out,'child.txt').write_text('permitted child write')
print(json.dumps({'child_blocked':blocked,'isolated':sys.flags.isolated,'bytecode':sys.dont_write_bytecode,'grandchild':json.loads(grand.stdout)}))
'''
parent=r'''
import sys,json,subprocess
from pathlib import Path
forbidden,out,p312,p313,child=sys.argv[1:6]
ok=False
try:Path(forbidden).read_text()
except PermissionError:ok=True
writing=False
try:Path(forbidden).write_text('must not overwrite')
except PermissionError:writing=True
assert Path(__file__).with_name('dato.txt').read_text()=='allowed'
r=subprocess.run([p312,'-I','-B','-c',child,forbidden,out,p313],capture_output=True,text=True,check=True,creationflags=0)
f=Path(out,'json.json');f.write_text('{"ok":true}')
m=subprocess.run([p312,'-I','-B','-m','json.tool',str(f)],capture_output=True,text=True,check=True)
print(json.dumps({'parent_blocked':ok,'outside_write_blocked':writing,'child':json.loads(r.stdout),'module':json.loads(m.stdout)}))
'''
script=package/'parent.py';script.write_text(parent,encoding='utf8')
command=[str(P313),'-I','-B',str(common/'entorno_seguro.py'),'--script',str(script),'--out',str(out),'--',str(forbidden),str(out),str(P312),str(P313),child]
result=subprocess.run(command,capture_output=True,text=True,encoding='utf8',timeout=90)
(HERE/'stdout.txt').write_text(result.stdout,encoding='utf8');(HERE/'stderr.txt').write_text(result.stderr,encoding='utf8')
reports=[json.loads(p.read_text(encoding='utf8'))for p in(out/'_aislamiento').glob('proceso_*.json')]
summary={'native_ticks':0,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'processes':len(reports),'python_versions':[p['version'].split()[0]for p in reports],'blocks':sum(len(p['blocked'])for p in reports),'all_isolated':all(p['isolated']and p['dont_write_bytecode']for p in reports),'all_reports':[p['pid']for p in reports],'sentinel_unchanged':forbidden.read_text()=='test-only historical sentinel'}
(HERE/'RESULTADO.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(summary,ensure_ascii=False))
if result.returncode:raise SystemExit(result.returncode)
d=json.loads(result.stdout);assert d['parent_blocked']and d['outside_write_blocked']and d['child']['child_blocked']and d['child']['grandchild']['grandchild_blocked']and d['module']['ok']and summary['all_isolated']and summary['sentinel_unchanged'];assert len(reports)==4
