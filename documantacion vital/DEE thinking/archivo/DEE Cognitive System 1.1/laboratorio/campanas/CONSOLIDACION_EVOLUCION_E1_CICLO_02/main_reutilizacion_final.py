import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
life='E1_CICLO02_MAIN';before=Store().record(life);assert before['physical']['tick']==20927
spec={'before':{'life':life,'snapshot':before['snapshot'],'sha256':before['snapshot_sha256'],'tick':20927},
      'preserved_official_cut':'E1_CICLO02_CORTE_VALIDADO_20927','new_private_B_values':[20,52],
      'protection':'Same transient two-zero diversion, no absorbers or universe cleanup',
      'record_challenge':'Two legal5inputs each social event; admission and private content checked independently',
      'new_gate_forces':[85,100],'new_wear':[5,5],
      'sequence':'Two further private acquisitions and external uses, brief old functions, gate uses after social updating, external use,save/reload',
      'failure_policy':'Keep actual MAIN future; never replace it with the preserved cut or import alternative knowledge.'}
atomic_json(EV/'MAIN_REUTILIZACION_FINAL_PROTOCOLO_170.json',spec)
command('C02_MAIN_170_PRESERVAR',['bifurcar',life,spec['preserved_official_cut'],'--modalidad','CANDIDATE'])
for i,value in enumerate(spec['new_private_B_values']):
    tag='C02_MAIN_'+str(171+i)
    p=command(tag+'_SOCIAL',['integrado-experiencia','--vida',life,'--tipo','social','--parametros',json.dumps({'name':tag,'value':value,'mode':'full'})])
    command(tag+'_PROTECCION',['integrado-experiencia','--vida',life,'--tipo','proteger-retorno','--parametros',json.dumps({'name':tag})])
    for label in('minus','plus'):command(tag+'_RECORD_'+label,['entrada','--vida',life,'back.'+label+'.record','5',str(p['result']['source_tick']-1)])
    command(tag+'_CONTINUAR',['integrado-continuar','--vida',life,'--hasta',str(p['result']['end_tick'])])
    command(tag+'_USO',['integrado-externo','--vida',life,'--pasos','1'])
command('C02_MAIN_173_ANTERIORES',['integrado-panel','--vida',life,'--breve'])
command('C02_MAIN_174_PUERTA',['integrado-experiencia','--vida',life,'--tipo','puerta','--parametros',json.dumps({'forces':[85,100],'wear':[5,5]})])
command('C02_MAIN_175_EXTERNO',['integrado-externo','--vida',life,'--pasos','1'])
command('C02_MAIN_176_GUARDAR',['guardar','--vida',life])
command('C02_MAIN_177_RECARGA',['integrado-estado','--vida',life])
atomic_json(EV/'MAIN_CORTE_OPERATIVO_FINAL_177.json',{'main':Store().record(life),'preserved_cut':Store().record(spec['preserved_official_cut']),
    'protected_active':Store().record(),'spec':spec,'not_a_global_promotion':True})
