"""Finite geometry debug only; never creates/advances a Runtime."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.conductos_acceso_aa01 import turning_inputs,path_variants
start=[40,43,55];endpoint=[40,40,55];enddir=[1,0,0];incoming=[-1,1,0]
rows=[]
for path in path_variants(start,endpoint,enddir):
    base=sum(k for v,k in path);extra=330-8-base;triangle=[]
    if extra%2:triangle=[([0,0,1],5),([1,0,0],5),([-1,0,-1],5)];extra-=15
    h=extra//4;w=extra//2-h;prefix=[([0,0,1],h),([1,0,0],w),([0,0,-1],h),([-1,0,0],w)]
    prior=incoming;fail=[]
    for v,k in triangle+prefix+path:
        try:turning_inputs(prior,v)
        except ValueError:fail.append([prior,v])
        prior=v
    rows.append({'path':path,'base':base,'extra':extra,'h':h,'w':w,'fail':fail})
atomic_json(E/'GEOMETRIA_RUTA_DIAGNOSTICO_0TICKS.json',{'rows':rows,'native_ticks':0});print(json.dumps(rows),flush=True)
