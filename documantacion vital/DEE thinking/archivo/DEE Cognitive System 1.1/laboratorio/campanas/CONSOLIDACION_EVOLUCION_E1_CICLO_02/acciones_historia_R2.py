import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import ic_native_core as core
CASES=[('C02_ACT_040_HISTORIA_MENOS',[12,44,55]),('C02_ACT_041_SOPORTE_HEREDADO',[15,15,50])]
atomic_json(EV/'ACCIONES_HIPOTESIS_R2.json',{'cases':CASES,
    'diagnosis':'Single+ teaching produced a real Y-70 state. Opposing teaching returned no future payload. Test one opposite experience, without rewriting the memory or naming the later correct route.',
    'teaching':[-1],'future_availability':[1,1,1,1,-1,-1,-1,-1],
    'frozen_utility':'Native [1,r,0] payload>0 must reach the physically available route r. Constant+ or- gives4/8. Future environmental material is scheduled before observing actions.',
    'scope':'Exploratory two bounded supports, not retrospective redefinition of failed R1 answers.'})
for name,center in CASES:
    fork('E1_CICLO02_MAIN',name)
    def trial(a):
        initial=physical(a.world,occupation=True);h=ic.attach(a,record=False)
        try:
            teaching=core.train(a,episode=name,contexts=(-1,),center=center)
            a.save(EV/(name+'.PRE_ACCION.deetsnap.gz'))
            rows=core.situated(a,name=name,availability=(1,1,1,1,-1,-1,-1,-1),mode='intact',compact=True,gap=0,stream=True,shunt='a_only',trace=True)
        finally:h['detach']()
        return{'initial':initial,'teaching':teaching,'rows':rows,'final':physical(a.world,occupation=True)}
    run(name,name,trial,{'spec':'ACCIONES_HIPOTESIS_R2.json'})
