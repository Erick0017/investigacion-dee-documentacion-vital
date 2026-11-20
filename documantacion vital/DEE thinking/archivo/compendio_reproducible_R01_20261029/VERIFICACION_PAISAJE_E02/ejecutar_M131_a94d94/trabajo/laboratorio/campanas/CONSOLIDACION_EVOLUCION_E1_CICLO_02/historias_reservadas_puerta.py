import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import gate_world
parent=json.loads((EV/'C02_ADMISION_OPERATIVA_IC01.json').read_text(encoding='utf8'))['main']
cases=[('C02_HIST_140_DESGASTE6',6,'intact'),('C02_HIST_141_DESGASTE13',13,'intact'),
       ('C02_HIST_142_OMIT13',13,'omit'),('C02_HIST_143_SHAM13',13,'sham')]
atomic_json(EV/'HISTORIAS_PUERTA_RESERVA_PROTOCOLO_140.json',{
    'source_snapshot':parent['snapshot'],'source_sha256':parent['snapshot_sha256'],'cases':cases,
    'common_observation_after_different_actual_consequences':9,'first_force':100,
    'frozen_decoder':'Same native -X7 attempt/+X7 retreat, phases20/23; no new reader fit',
    'new_relation':'First actual wear6 versus13, then exactly the same current force9; neither old reference nor correct action is supplied in the second query',
    'limits':'Exact shared inherited prefix, not independent biological subjects; environmental histories differ legitimately after the first contact.'})
for name,quantum,mode in cases:
    fork('E1_CICLO02_MAIN',name,checkpoint=parent['snapshot'])
    def test(a):
        prep=gate_world.prepare(a,name=name);h=ic.attach(a,record=False)
        try:r=gate_world.run(a,forces=[100,9],wear=[quantum,6],mode=mode)
        finally:h['detach']()
        return{'preparation':prep,'gate':r,'final':physical(a.world,occupation=True)}
    run(name,name,test,{'spec':'HISTORIAS_PUERTA_RESERVA_PROTOCOLO_140.json'})
