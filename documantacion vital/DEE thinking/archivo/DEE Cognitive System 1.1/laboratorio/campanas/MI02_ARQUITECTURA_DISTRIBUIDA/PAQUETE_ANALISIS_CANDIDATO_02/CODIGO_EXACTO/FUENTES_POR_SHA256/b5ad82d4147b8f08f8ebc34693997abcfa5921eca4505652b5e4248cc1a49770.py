"""New R9 operative branch, same gestor, same learned state across native/external."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
cmds=[['mi02-estado','--vida','MI02_SOCIAL_REUSABLE_240'],['bifurcar','MI02_SOCIAL_REUSABLE_240','MI02_R9_OPERATIVA47'],['mi02-vivir','--vida','MI02_R9_OPERATIVA47','--condiciones=1,-1'],['guardar','--vida','MI02_R9_OPERATIVA47'],['mi02-estado','--vida','MI02_R9_OPERATIVA47'],['mi02-externo','--vida','MI02_R9_OPERATIVA47','--pasos','8','--semilla','82347','--reiniciar-entorno'],['guardar','--vida','MI02_R9_OPERATIVA47'],['mi02-externo','--vida','MI02_R9_OPERATIVA47','--pasos','8'],['mi02-vivir','--vida','MI02_R9_OPERATIVA47','--condiciones=1,1,-1,-1'],['guardar','--vida','MI02_R9_OPERATIVA47'],['mi02-estado','--vida','MI02_R9_OPERATIVA47']]
atomic_json(E/'OPERATIVO47_FIJADO.json',{'parent':Store().record('MI02_SOCIAL_REUSABLE_240'),'commands':cmds,'same_life_continues':True,'scope':'Bounded operational integration and process continuation, not a new MAIN or competent Pendulum-policy claim. The external environment is new and declared; learned DEE fields are never reset.','sources':archive()})
rows=[]
for i,args in enumerate(cmds):
    budget();cp=subprocess.run([sys.executable,'-I','-B',str(S/'gestionar.py'),*args],cwd=S,capture_output=True,text=True,encoding='utf8',timeout=240)
    try:r=json.loads(cp.stdout)
    except Exception:r={'stdout':cp.stdout}
    atomic_json(E/('OPERATIVO47_%02d.json'%i),{'index':i,'command':args,'returncode':cp.returncode,'result':r,'stderr':cp.stderr});rows.append({'command':args,'returncode':cp.returncode,'evidence':'OPERATIVO47_%02d.json'%i});print(i,args[0],cp.returncode,flush=True)
    if cp.returncode:raise RuntimeError('Preserved actual integration failure')
atomic_json(E/'OPERATIVO47_CIERRE.json',{'rows':rows,'current':Store().record('MI02_R9_OPERATIVA47'),'parent_preserved':Store().record('MI02_SOCIAL_REUSABLE_240'),'default_protected':json.loads((S/'estado/ACTIVO.json').read_bytes())})
