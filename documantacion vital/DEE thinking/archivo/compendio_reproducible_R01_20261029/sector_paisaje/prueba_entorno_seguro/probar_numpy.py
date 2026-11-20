"""Comprueba elección de terceros por versión sin importar Native."""
from pathlib import Path
import json,subprocess
HERE=Path(__file__).resolve().parent;BUILD=HERE.parents[1];PACKAGE=BUILD/'package';WRAPPER=PACKAGE/'codigo_comun/entorno_seguro.py';P313=BUILD/'entorno313/Scripts/python.exe';P312=Path(r'C:\Users\Erik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe')
OUT=HERE/'salida_numpy';OUT.mkdir(exist_ok=True)
SCRIPT=OUT/'sonda_numpy.py'
SCRIPT.write_text(r'''
import sys,json,subprocess,tempfile
from pathlib import Path
import numpy as np
package,p312,p313=sys.argv[1:4]
expected=Path(package,'codigo_comun','terceros','numpy').resolve()
assert np.__version__=='2.2.6'and Path(np.__file__).resolve().is_relative_to(expected)
code="import sys,json,numpy as np,tempfile; print(json.dumps({'version':np.__version__,'file':np.__file__,'python':sys.version,'temp':tempfile.gettempdir()}))"
children=[]
for exe,version,folder in [(p312,'2.3.5','terceros312'),(p313,'2.2.6','terceros')]:
 result=subprocess.run([exe,'-I','-B','-c',code],capture_output=True,text=True,check=True)
 data=json.loads(result.stdout)
 assert data['version']==version and Path(data['file']).resolve().is_relative_to(Path(package,'codigo_comun',folder,'numpy').resolve())
 children.append(data)
temp=tempfile.gettempdir();temp.encode('ascii');assert len(temp)<120
print(json.dumps({'numpy_parent':{'version':np.__version__,'file':np.__file__},'children':children,'temp':temp,'native_ticks':0}))
''',encoding='utf8')
command=[str(P313),'-I','-B',str(WRAPPER),'--script',str(SCRIPT),'--package',str(PACKAGE),'--out',str(OUT),'--',str(PACKAGE),str(P312),str(P313)]
result=subprocess.run(command,capture_output=True,text=True,encoding='utf8',timeout=90)
reports=[json.loads(p.read_text(encoding='utf8'))for p in(OUT/'_aislamiento').glob('proceso_*.json')]
data={'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'processes':len(reports),'blocked':[b for r in reports for b in r['blocked']],'temporary_roots':[r['temporary_directory']for r in reports],'native_ticks':0}
(HERE/'RESULTADO_NUMPY.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(data,ensure_ascii=False))
assert result.returncode==0 and len(reports)==3 and not data['blocked']
