"""One real continuation of the improved-but-specialized candidate, not MAIN.
All calls use the existing fenced manager in separate processes.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
name='E1_CICLO02_COMUNICACION_01'
command('C02_OP_250_FORK',['bifurcar','C02_DETOUR_240_FANTASMA',name,'--modalidad','CANDIDATE'])
p=command('C02_OP_251_SOCIAL',['integrado-experiencia','--vida',name,'--tipo','social','--parametros',json.dumps({'name':'C2OP251','value':24,'mode':'full'})])['result']
command('C02_OP_252_RETORNO',['integrado-experiencia','--vida',name,'--tipo','proteger-retorno','--parametros',json.dumps({'name':'C2OP251'})])
command('C02_OP_253_MENSAJE',['integrado-experiencia','--vida',name,'--tipo','proteger-mensaje','--parametros',json.dumps({'name':'C2OP251'})])
for label in('minus','plus'):command('C02_OP_254_RECORD_'+label,['entrada','--vida',name,'back.'+label+'.record','5',str(p['source_tick']-1)])
command('C02_OP_255_CONTINUAR',['integrado-continuar','--vida',name,'--hasta',str(p['end_tick'])])
command('C02_OP_256_USO',['integrado-externo','--vida',name,'--pasos','1'])
command('C02_OP_257_GUARDAR',['guardar','--vida',name])
command('C02_OP_258_RECARGA',['integrado-estado','--vida',name])
command('C02_OP_259_OTRO_PROCESO',['integrado-externo','--vida',name,'--pasos','1'])
command('C02_OP_260_PUERTA',['integrado-experiencia','--vida',name,'--tipo','puerta','--parametros',json.dumps({'forces':[91,100],'wear':[0,0]})])
command('C02_OP_261_ANTERIORES',['integrado-panel','--vida',name,'--breve'])
command('C02_OP_262_GUARDAR',['guardar','--vida',name])
command('C02_OP_263_RECARGA',['integrado-estado','--vida',name])
atomic_json(EV/'DESVIO_INCORPORACION_OPERATIVA_263.json',{'life':name,'physical':Store().record(name)['physical'],
    'snapshot':Store().record(name)['snapshot'],'sha256':Store().record(name)['snapshot_sha256'],
    'not_a_global_promotion':True,'scope':'Specialized social continuation plus gate learned-reference and two previous comparisons. No claim that old+ memory survives or that P0 anatomy is learned.'})
command('C02_CAPAS_217_CONTINUACION',['integrado-externo','--vida','C02_CAPAS_210_OPERATIVO_R2','--pasos','1'])
command('C02_CAPAS_218_RECARGA',['integrado-estado','--vida','C02_CAPAS_210_OPERATIVO_R2'])
