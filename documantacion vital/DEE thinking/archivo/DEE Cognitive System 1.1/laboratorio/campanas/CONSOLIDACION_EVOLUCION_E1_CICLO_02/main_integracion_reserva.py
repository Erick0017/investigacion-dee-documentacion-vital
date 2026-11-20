import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
life='E1_CICLO02_MAIN';before=Store().record(life)
assert before['physical']['tick']==18582
spec={'life':life,'parent_current_snapshot':before['snapshot_sha256'],
      'private_reserved_B_value':48,'old_record_challenge':5,'protected_variant':'transient diversion, no terminator',
      'reserved_gate_forces':[31,45,12,55,36,65],'reserved_wear':[9,9,13,13,13,13],
      'later_retention_forces':[2,100],'later_wear':13,
      'sequence':'Private B + protected legal record challenge, native communication,2actual Pendulumsteps,2old comparisons, reserved new gate forces/wear,external step,gate retention,save/reload',
      'no_checkpoint_selection_between_functions':True,'all_one_actual_life':True,
      'not_claimed':'Prepared motor addition is not native compositional semantics. Old transformed social forms are not reclassified.'}
atomic_json(EV/'MAIN_INTEGRACION_RESERVA_PROTOCOLO_100.json',spec)
p=command('C02_MAIN_100_SOCIAL',['integrado-experiencia','--vida',life,'--tipo','social','--parametros',json.dumps({'name':'C02_RESERVA_B48','value':48,'mode':'full'})])
plan=p['result'];T=plan['source_tick'];end=plan['end_tick']
command('C02_MAIN_101_PROTEGER',['integrado-experiencia','--vida',life,'--tipo','proteger-retorno','--parametros',json.dumps({'name':'C02_RESERVA_B48'})])
for label in('minus','plus'):
    command('C02_MAIN_102_RECORD_'+label,['entrada','--vida',life,'back.'+label+'.record','5',str(T-1)])
command('C02_MAIN_103_USO_SOCIAL',['integrado-continuar','--vida',life,'--hasta',str(end+67)])
command('C02_MAIN_104_EXTERNO',['integrado-externo','--vida',life,'--pasos','2'])
command('C02_MAIN_105_ANTERIORES',['integrado-panel','--vida',life,'--breve'])
command('C02_MAIN_106_RESERVA_PUERTA',['integrado-experiencia','--vida',life,'--tipo','puerta','--parametros',json.dumps({'forces':spec['reserved_gate_forces'],'wear':spec['reserved_wear']})])
command('C02_MAIN_107_EXTERNO',['integrado-externo','--vida',life,'--pasos','1'])
command('C02_MAIN_108_RETENCION',['integrado-experiencia','--vida',life,'--tipo','puerta','--parametros',json.dumps({'forces':spec['later_retention_forces'],'wear':spec['later_wear']})])
command('C02_MAIN_109_RECARGA',['integrado-estado','--vida',life])
atomic_json(EV/'MAIN_INTEGRACION_FINAL_ETAPA2.json',{'life':Store().record(life),'spec':spec,'active_unchanged':Store().record()['life_id']=='E1_SOCIAL_11'})
