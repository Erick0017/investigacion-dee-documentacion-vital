"""Pure exact coordinate/time calculation, no native Runtime constructed."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.mente_integral_mi01.habitat_nativo import exact_route
out=[]
for sign in(-1,1):
    r=exact_route({'site':[40 if sign==-1 else 48,43,55],'direction':[sign,1,0]},{'site':[40,35,55],'direction':[0,sign,0]},8,335)
    out.append({'sign':sign,'route':r})
atomic_json(E/'GEOMETRIA_HABITAT_R2_0TICKS.json',{'routes':out,'native_ticks':0,'not_a_physical_validation':True});print(json.dumps([{'sign':z['sign'],'arrival':z['route']['arrival_tick'],'endpoint':z['route']['destination'],'turns':len(z['route']['turns'])}for z in out]),flush=True)
