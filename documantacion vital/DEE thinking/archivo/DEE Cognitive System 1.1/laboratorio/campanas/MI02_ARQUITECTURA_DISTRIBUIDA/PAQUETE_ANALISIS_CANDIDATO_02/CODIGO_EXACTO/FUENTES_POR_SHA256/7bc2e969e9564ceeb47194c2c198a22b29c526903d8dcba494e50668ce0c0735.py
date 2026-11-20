"""Exact current cuts, real manager processes, bridge state persists across calls."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
cmds=[
 ['mi02-estado','--vida','D1_MI02_MAIN'],
 ['mi02-estado','--vida','E1_MI02_HEREDADA_R8'],
 ['bifurcar','D1_MI02_MAIN','D1_MI02_OPERATIVA39'],
 ['mi02-externo','--vida','D1_MI02_OPERATIVA39','--pasos','4'],
 ['guardar','--vida','D1_MI02_OPERATIVA39'],
 ['mi02-estado','--vida','D1_MI02_OPERATIVA39'],
 ['mi02-externo','--vida','D1_MI02_OPERATIVA39','--pasos','3'],
 ['mi02-orden','--vida','D1_MI02_OPERATIVA39','izquierda','derecha'],
 ['guardar','--vida','D1_MI02_OPERATIVA39'],
 ['mi02-estado','--vida','D1_MI02_OPERATIVA39'],
]
atomic_json(E/'OPERATIVA39_FIJADA.json',{'commands':cmds,'actual_parent':Store().record('D1_MI02_MAIN'),'scope':'Identified evaluation copy; no outcome is copied back into MAIN, no environment reset, no learner recreation. The stored external episode continues after the intervening native history.','sources':archive()})
rows=[]
for i,args in enumerate(cmds):
    budget();cp=subprocess.run([sys.executable,'-I','-B',str(S/'gestionar.py'),*args],cwd=S,capture_output=True,text=True,encoding='utf-8',timeout=240)
    try:r=json.loads(cp.stdout)
    except Exception:r={'stdout':cp.stdout}
    atomic_json(E/('OPERATIVA39_%02d.json'%i),{'index':i,'command':args,'returncode':cp.returncode,'result':r,'stderr':cp.stderr})
    rows.append({'index':i,'command':args,'returncode':cp.returncode,'evidence':'OPERATIVA39_%02d.json'%i})
    print(i,args[0],cp.returncode,flush=True)
    if cp.returncode:raise RuntimeError('Actual manager error preserved')
atomic_json(E/'OPERATIVA39_CIERRE.json',{'rows':rows,'current':Store().record('D1_MI02_OPERATIVA39'),'MAIN_unchanged':Store().record('D1_MI02_MAIN'),'active':json.loads((S/'estado/ACTIVO.json').read_bytes())})
