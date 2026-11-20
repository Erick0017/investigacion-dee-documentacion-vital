"""Nueva adquisición periférica en E1 vivido; no copia de un selector entrenado."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import ic_native_core as core
S=[12,44,55]
CASES=[('C02_ACT_020_UNA_RAPIDA',(1,),0,'a_only'),
       ('C02_ACT_021_DOS_RAPIDA',(1,-1),0,'a_only'),
       ('C02_ACT_022_UNA_ESPACIADA',(1,),67,'a_only'),
       ('C02_ACT_023_DOS_ESPACIADA',(1,-1),67,'a_only')]
atomic_json(EV/'ACCIONES_PROTOCOLO_EXPLORATORIO_R1.json',{'parent':'E1_CICLO02_MAIN','parent_tick':17289,
    'new_component_center':S,'cases':CASES,'contexts':[1,1,1,1,-1,-1,-1,-1],
    'same_architecture_regions_across_cases':True,'no_old_memory_fields_changed':True,
    'designed':'New physical supports/opportunities, native feedback law and transient protection are external design. No solution or future selected from observed actions.',
    'useful_action':'A payload-bearing native direction [1,r,0] is useful exactly when r equals physical availability of that opportunity. Availability fixes contact material on BOTH branches before action.',
    'benchmark_not_claimed':'Finite native route task, not Pendulum policy. A fixed constant route has4/8 useful opportunities here; this comparison is audit only.'})
for name,teach,gap,shunt in CASES:
    fork('E1_CICLO02_MAIN',name)
    def test(a):
        before=physical(a.world,occupation=True);pre=observe(a.world,S);h=ic.attach(a,record=False)
        try:
            teaching=core.train(a,episode=name,contexts=teach,center=S)
            a.save(EV/(name+'.PRE_ACCION.deetsnap.gz'))
            rows=core.situated(a,name=name,availability=(1,1,1,1,-1,-1,-1,-1),mode='intact',compact=True,gap=gap,stream=True,shunt=shunt,trace=True)
        finally:h['detach']()
        return{'initial':before,'new_center_pre':pre,'teaching':teaching,'rows':rows,'final':physical(a.world,occupation=True),
               'note':'Training is a declared new experience on new physical possibilities in the same lived N67 world. No old trained selector is transplanted.'}
    run(name,name,test,{'spec':'ACCIONES_PROTOCOLO_EXPLORATORIO_R1.json'})
