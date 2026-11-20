"""Brief constructor-route verification, not another scientific replicate."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
cmds=[['mi02-crear','--vida','MI02_CONSTRUCTOR_R9_49','--variante','unificada-r9'],['mi02-adquirir','--vida','MI02_CONSTRUCTOR_R9_49','--propias','13,13','--privadas','91,29'],['mi02-vivir','--vida','MI02_CONSTRUCTOR_R9_49','--condiciones=-1,-1,-1'],['guardar','--vida','MI02_CONSTRUCTOR_R9_49'],['mi02-estado','--vida','MI02_CONSTRUCTOR_R9_49']]
atomic_json(E/'CONSTRUCTOR49_FIJADO.json',{'commands':cmds,'scope':'Technical check of the newly admitted normal constructor, explicit training and process continuation. Same raw contents as reserve246, NOT an independent scientific sample.','sources':archive()})
rows=[]
for i,args in enumerate(cmds):
    budget();cp=subprocess.run([sys.executable,'-I','-B',str(S/'gestionar.py'),*args],cwd=S,capture_output=True,text=True,encoding='utf8',timeout=180)
    try:r=json.loads(cp.stdout)
    except Exception:r={'stdout':cp.stdout}
    atomic_json(E/('CONSTRUCTOR49_%02d.json'%i),{'index':i,'command':args,'returncode':cp.returncode,'result':r,'stderr':cp.stderr});rows.append({'index':i,'returncode':cp.returncode});print(i,args[0],cp.returncode,flush=True)
    if cp.returncode:raise RuntimeError('Constructor-route failure preserved')
from capacidades.observador_causal_retrospectivo_01 import Snapshot,compare
a=Store().record('MI02_CONSTRUCTOR_R9_49');z=Store().record('MI02_RESERVA_REUSABLE_246')
atomic_json(E/'CONSTRUCTOR49_VERIFICACION.json',{'processes':rows,'actual':a,'technical_reference':z,'comparison':compare(Snapshot(S/a['snapshot']),Snapshot(S/z['snapshot']),sample_limit=8),'not_independent_sample':True})
