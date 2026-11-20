"""Small real manager smoke test, distinct evaluation lives, exact process logs."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *

commands=[
 ['mi02-estado','--vida','MI02_EFIMERO_210'],
 ['bifurcar','MI02_EFIMERO_210','MI02_OPERATIVO_EFIMERO36'],
 ['mi02-comparar-efimero','--vida','MI02_OPERATIVO_EFIMERO36','--objetos','1,24,27'],
 ['guardar','--vida','MI02_OPERATIVO_EFIMERO36'],
 ['mi02-estado','--vida','MI02_OPERATIVO_EFIMERO36'],
 ['mi02-comparar-efimero','--vida','MI02_OPERATIVO_EFIMERO36','--objetos','30,22'],
 ['mi02-crear','--vida','MI02_CONSTRUCTOR_EFIMERO36','--variante','comparador-efimero'],
 ['mi02-adquirir','--vida','MI02_CONSTRUCTOR_EFIMERO36','--propias','33,9'],
 ['mi02-comparar-efimero','--vida','MI02_CONSTRUCTOR_EFIMERO36','--objetos','25,26,27,None'],
 ['mi02-estado','--vida','MI02_UNIFICADA_180'],
 ['bifurcar','MI02_UNIFICADA_180','MI02_OPERATIVO_SOCIAL36'],
 ['mi02-social-continuar','--vida','MI02_OPERATIVO_SOCIAL36','--ticks','47'],
 ['guardar','--vida','MI02_OPERATIVO_SOCIAL36'],
 ['mi02-estado','--vida','MI02_OPERATIVO_SOCIAL36'],
]
atomic_json(E/'OPERATIVO36_PLAN.json',{'commands':commands,'sources':archive(),'not_reproduction_of_archived_biography':'New process continuation tests on identified copies, no knowledge import intoMAIN'})
records=[]
for i,args in enumerate(commands):
    budget();cp=subprocess.run([sys.executable,'-I','-B',str(S/'gestionar.py'),*args],cwd=S,capture_output=True,text=True,encoding='utf-8',timeout=180)
    try:result=json.loads(cp.stdout)
    except Exception:result={'stdout':cp.stdout}
    rec={'index':i,'command':args,'returncode':cp.returncode,'result':result,'stderr':cp.stderr};atomic_json(E/('OPERATIVO36_%02d.json'%i),rec)
    records.append({'index':i,'command':args,'returncode':cp.returncode,'result_file':'OPERATIVO36_%02d.json'%i,'audit_fence':result.get('INSTRUMENTO_FENCE')})
    print(i,args[0],cp.returncode,flush=True)
    if cp.returncode:raise RuntimeError('Preserved actual manager failure')
atomic_json(E/'OPERATIVO36_RESUMEN.json',{'records':records,'active_unchanged':Store().active_id()if hasattr(Store(),'active_id')else json.loads((S/'estado/ACTIVO.json').read_bytes())})
