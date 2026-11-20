import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
s=Store();main='E1_CICLO02_MAIN';parent=s.record(main);assert parent['physical']['tick']==20123
cases=[(main,True,False,True),('C02_ACCESO_SHAM_121',True,True,True),
       ('C02_ACCESO_SIN_RECURSO_122',False,False,True),('C02_ACCESO_SIN_CONSULTA_123',True,False,False)]
spec={'parent':{'life':main,'tick':20123,'snapshot':parent['snapshot'],'sha256':parent['snapshot_sha256']},'cases':cases,
      'support':'recovered predeclared zminus3 plane, both signs; not selected by current expected answer',
      'query_delay_periods':2,'post_query_repair_commands':0,
      'readout':'Same original+previous-alternative+new-fallback parallel ports in all four cases, fixed before the loss.',
      'main_end_use':{'old_panel':'brief quantity and two-memory only','gate_forces':[77,100],'gate_wear':[5,5]},
      'attribution':'P0 opportunities and external query; only physical history-dependent access activation can be P1. No P2 initiation or selection-of-reader assertion from an all-port instrument.'}
atomic_json(EV/'ACCESO_MAIN_RESERVA_PROTOCOLO_120.json',spec)
for life,enabled,sham,query in cases[1:]:fork(main,life,checkpoint=parent['snapshot'])
for i,(life,enabled,sham,query)in enumerate(cases):
    tag='C02_ACCESS_'+str(120+i)
    prep=command(tag+'_PREPARAR',['integrado-experiencia','--vida',life,'--tipo','acceso-previo','--parametros',json.dumps({'name':tag,'support':'recovered','enabled':enabled,'sham':sham})])
    anchor=prep['result']['anchor_tick'];qtick=anchor+134
    if query:command(tag+'_CONSULTA',['integrado-experiencia','--vida',life,'--tipo','acceso-consultar','--parametros',json.dumps({'name':tag,'support':'recovered','query_tick':qtick})])
    for role,t in [('RECURSO_PREVIO',anchor+3),('PRE_PERDIDA',qtick-1),('PERDIDA',qtick),('POST_NATIVO',qtick+3)]:
        command(tag+'_'+role,['integrado-continuar','--vida',life,'--hasta',str(t)])
    command(tag+'_USO4',['integrado-externo','--vida',life,'--pasos','4'])
    command(tag+'_RECARGA',['integrado-estado','--vida',life])
    if life==main:
        command('C02_MAIN_124_ANTERIORES',['integrado-panel','--vida',life,'--breve'])
        command('C02_MAIN_125_PUERTA',['integrado-experiencia','--vida',life,'--tipo','puerta','--parametros',json.dumps({'forces':[77,100],'wear':[5,5]})])
        command('C02_MAIN_126_RECARGA',['integrado-estado','--vida',life])
atomic_json(EV/'MAIN_INTEGRACION_FINAL_ETAPA3.json',{'main':s.record(main),'controls':[s.record(c[0])for c in cases[1:]],'spec':spec,'default':s.record()['life_id']})
