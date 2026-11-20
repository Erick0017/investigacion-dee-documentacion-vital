"""Read-only launcher check, no policy bypass, native tick or life commit."""
from pathlib import Path
import hashlib,json,subprocess,sys
L=Path(__file__).resolve().parent;R=L.parents[2];S=R/'sistema';E=R/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
cont=json.loads((R/'CONTINUIDAD_CICLO02.json').read_bytes());life=next(r for r in cont['lives']if r['life_id']=='E1_CICLO02_SEPARACION_TRIPLE_01');source=S/life['snapshot']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
before=sha(source);cmd="& '"+str(S/'iniciar_sistema.ps1')+"' -PythonExecutable '"+sys.executable+"' -Comandos @('integrado-estado','--vida','E1_CICLO02_SEPARACION_TRIPLE_01')"
argv=[r'C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe','-NoProfile','-NonInteractive','-Command',cmd]
r=subprocess.run(argv,cwd=R,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=60)
try:parsed=json.loads(r.stdout)
except Exception:parsed=None
out={'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'parsed_json':parsed,'native_ticks':0,
     'snapshot_sha256_before':before,'snapshot_sha256_after':sha(source),'source_unchanged':before==sha(source),'execution_policy_not_bypassed':True,
     'fallback_if_blocked':'Use the already verified explicit CPython3.13 executable with sistema/gestionar.py; no new environment or permission bypass.'}
(E/'COMPROBACION_LANZADOR_365.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
assert out['source_unchanged']
print(json.dumps({'returncode':r.returncode,'parsed':parsed is not None,'source_unchanged':out['source_unchanged'],'error':r.stderr[-800:]},ensure_ascii=False))
