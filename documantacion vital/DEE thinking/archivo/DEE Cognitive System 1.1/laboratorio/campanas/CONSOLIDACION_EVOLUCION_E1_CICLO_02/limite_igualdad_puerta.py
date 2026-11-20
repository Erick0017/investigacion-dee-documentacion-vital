import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import gate_world
parent=json.loads((EV/'MAIN_INTEGRACION_FINAL_ETAPA3.json').read_text(encoding='utf8'))['main']
assert parent['physical']['tick']==20927
atomic_json(EV/'LIMITE_PUERTA_IGUALDAD_PROTOCOLO_145.json',{
    'source_snapshot':parent['snapshot'],'source_sha256':parent['snapshot_sha256'],'gate_resistance':87,
    'cases':[{'id':'C02_BOUND_145_IGUALDAD','forces':[87,88,86],'wear':0},
             {'id':'C02_BOUND_146_SIN_SONDA','forces':[88,86],'wear':0,'native_only_age_control_ticks':134}],
    'fixed_decoder':'No change: only pureX7 counts as an actuator response. A material zero-direction code is not silence, NO, an intelligent retreat or a new learned Spanish word.',
    'question':'Does an equality probe expose a codec limit or affect later access? Same native age at the two subsequent comparisons.'})
for name,forces,gap in [('C02_BOUND_145_IGUALDAD',[87,88,86],0),('C02_BOUND_146_SIN_SONDA',[88,86],134)]:
    fork('E1_CICLO02_MAIN',name,checkpoint=parent['snapshot'])
    def test(a):
        initial=physical(a.world,occupation=True)
        if gap:ic.advance(a,until=a.tick+gap,record=False)
        h=ic.attach(a,record=False)
        try:r=gate_world.run(a,forces=forces,wear=0)
        finally:h['detach']()
        return{'initial':initial,'gate':r,'final':physical(a.world,occupation=True),'audit_probe_gap_ticks':gap}
    run(name,name,test,{'spec':'LIMITE_PUERTA_IGUALDAD_PROTOCOLO_145.json'})
