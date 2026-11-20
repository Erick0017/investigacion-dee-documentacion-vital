"""Use the ordinary guarded manager in separate processes, not a lab shortcut."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
life='MI02_OPERATIVO_RETORNO_15';fork('MI02_CONTROLADOR_90',life)
rows=[]
for args in[['mi02-estado','--vida',life],['mi02-vivir','--vida',life,'--condiciones=-1,1,1'],['guardar','--vida',life],['mi02-estado','--vida',life],['mi02-vivir','--vida',life,'--condiciones=1']]:
    sources=archive();before=Store().record(life);r=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(S/'gestionar.py'),*args],capture_output=True,text=True,encoding='utf8',timeout=240);path=E/('OPERATIVO15_'+str(len(rows))+'.json')
    out={'command':args,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'before':before,'after':Store().record(life),'sources':sources};atomic_json(path,out);rows.append({'file':path.name,'code':r.returncode})
    if r.returncode:raise RuntimeError('Operational integration failed; preserve native future and diagnose '+str(path))
atomic_json(E/'INCORPORACION_OPERATIVA_15.json',{'operations':rows,'life':life,'active_unchanged':Store().record()['life_id'],'no_lab_evidence_reads':'ordinary manager audit fence active','continued_acquired_state_not_recipe':True})
