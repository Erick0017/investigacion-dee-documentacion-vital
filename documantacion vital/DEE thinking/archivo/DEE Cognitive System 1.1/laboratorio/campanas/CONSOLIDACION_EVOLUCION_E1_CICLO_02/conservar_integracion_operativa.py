"""Preserve useful domains without replacing MAIN's adverse future.
Both are exact identified forks of the predeclared20927 cut, never T0 rebuilds.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
parent='E1_CICLO02_CORTE_VALIDADO_20927'
ret='E1_CICLO02_RETENCION_01'
command('C02_RET_290_FORK',['bifurcar',parent,ret,'--modalidad','CANDIDATE'])
command('C02_RET_291_USO',['integrado-externo','--vida',ret,'--pasos','2'])
command('C02_RET_292_NUEVA_CONSECUENCIA',['integrado-experiencia','--vida',ret,'--tipo','puerta','--parametros',json.dumps({'forces':[85,100],'wear':[1,1]})])
command('C02_RET_293_USO_ANTERIOR',['integrado-externo','--vida',ret,'--pasos','1'])
command('C02_RET_294_PANEL',['integrado-panel','--vida',ret,'--breve'])
command('C02_RET_295_GUARDAR',['guardar','--vida',ret])
command('C02_RET_296_RECARGA',['integrado-estado','--vida',ret])
lat='E1_CICLO02_LATERAL_LOCAL_01'
command('C02_LATOP_300_FORK',['bifurcar',parent,lat,'--modalidad','CANDIDATE'])
p=command('C02_LATOP_301_SOCIAL',['integrado-experiencia','--vida',lat,'--tipo','social','--parametros',json.dumps({'name':'C2LAT301','value':20,'mode':'full'})])['result']
command('C02_LATOP_302_RETORNO',['integrado-experiencia','--vida',lat,'--tipo','proteger-retorno','--parametros',json.dumps({'name':'C2LAT301'})])
command('C02_LATOP_303_LATERAL',['integrado-experiencia','--vida',lat,'--tipo','preparar-lateral','--parametros',json.dumps({'name':'C2LAT301'})])
for label in('minus','plus'):command('C02_LATOP_304_RECORD_'+label,['entrada','--vida',lat,'back.'+label+'.record','5',str(p['source_tick']-1)])
command('C02_LATOP_305_CONTINUAR',['integrado-continuar','--vida',lat,'--hasta',str(p['end_tick'])])
command('C02_LATOP_306_USO',['integrado-externo','--vida',lat,'--pasos','1'])
command('C02_LATOP_307_GUARDAR',['guardar','--vida',lat])
command('C02_LATOP_308_RECARGA',['integrado-estado','--vida',lat])
command('C02_LATOP_309_SIN_NUEVO_B',['integrado-externo','--vida',lat,'--pasos','2'])
command('C02_LATOP_310_GUARDAR',['guardar','--vida',lat])
command('C02_LATOP_311_RECARGA',['integrado-estado','--vida',lat])
atomic_json(EV/'CONSERVACION_PERFILES_OPERATIVOS_311.json',{'retention':{k:Store().record(ret)[k]for k in('life_id','physical','snapshot','snapshot_sha256')},
 'lateral_local':{k:Store().record(lat)[k]for k in('life_id','physical','snapshot','snapshot_sha256')},
 'MAIN_future_not_changed':Store().record('E1_CICLO02_MAIN')['physical'],
 'not_global_promotion':True,'scope':'Separate useful domains, not a union of incompatible memories or an accumulated history of all three lives.'})
