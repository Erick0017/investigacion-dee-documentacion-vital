"""Prepare the whole mechanism through the normal manager BEFORE B responds.
Same lived ancestor, real new episode, no trained control state imported.
"""
import sys,importlib.util
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
name='E1_CICLO02_SEPARACION_TRIPLE_01'
command('C02_SEPOP_350_FORK',['bifurcar','E1_CICLO02_CORTE_VALIDADO_20927',name,'--modalidad','CANDIDATE'])
p=command('C02_SEPOP_351_SOCIAL',['integrado-experiencia','--vida',name,'--tipo','social','--parametros',json.dumps({'name':'SEP351','value':20,'mode':'full'})])['result']
command('C02_SEPOP_352_RETORNO',['integrado-experiencia','--vida',name,'--tipo','proteger-retorno','--parametros',json.dumps({'name':'SEP351'})])
command('C02_SEPOP_353_LATERAL',['integrado-experiencia','--vida',name,'--tipo','preparar-lateral','--parametros',json.dumps({'name':'SEP351'})])
command('C02_SEPOP_354_SEPARACION_ANTICIPADA',['integrado-experiencia','--vida',name,'--tipo','separar-soportes','--parametros',json.dumps({'name':'SEP351'})])
for label in('minus','plus'):command('C02_SEPOP_355_RECORD_'+label,['entrada','--vida',name,'back.'+label+'.record','5',str(p['source_tick']-1)])
command('C02_SEPOP_356_CONTINUAR',['integrado-continuar','--vida',name,'--hasta',str(p['end_tick'])])
command('C02_SEPOP_357_USO4',['integrado-externo','--vida',name,'--pasos','4'])
r=Store().record(name);assert r['physical']['tick']==21309
sp=importlib.util.spec_from_file_location('snapshot_only',SYSTEM/'capacidades/observador_causal_retrospectivo_01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
ref=json.loads((EV/'C02_SEPARA_330_DOS_PULSOS.json').read_text(encoding='utf8'))['data']['result']['planned_cut'];a=m.Snapshot(Store().snapshot(r));b=m.Snapshot(ROOT/ref['path'])
atomic_json(EV/'SEPARACION_INCORPORACION_PARIDAD_357.json',{'life':name,'snapshot':r['snapshot'],'sha256':r['snapshot_sha256'],
    'RAW_equal_to_exploratory_cut':a.raw==b.raw,'clocks_equal_to_exploratory_cut':a.clocks==b.clocks,
    'not_a_claim_of_full_causal_snapshot_identity':'Inputs are now precommitted before B, names/event IDs/metadata can differ. Physical buffer equality and real uses are the technical correspondence.',
    'classification':'Technical reproduction through the ordinary manager, not an independent new learner.'})
command('C02_SEPOP_358_GUARDAR',['guardar','--vida',name])
command('C02_SEPOP_359_RECARGA',['integrado-estado','--vida',name])
command('C02_SEPOP_360_NUEVA_CONSECUENCIA',['integrado-experiencia','--vida',name,'--tipo','puerta','--parametros',json.dumps({'forces':[85,100],'wear':[1,1]})])
command('C02_SEPOP_361_ANTERIORES',['integrado-panel','--vida',name,'--breve'])
command('C02_SEPOP_362_USO_TRAS_APRENDER',['integrado-externo','--vida',name,'--pasos','1'])
command('C02_SEPOP_363_GUARDAR',['guardar','--vida',name])
command('C02_SEPOP_364_RECARGA',['integrado-estado','--vida',name])
atomic_json(EV/'SEPARACION_INCORPORACION_FINAL_364.json',{'life':name,'physical':Store().record(name)['physical'],'snapshot':Store().record(name)['snapshot'],
 'sha256':Store().record(name)['snapshot_sha256'],'protected_default':Store().record()['life_id'],'not_global_promotion':True,
 'limits':'One private acquisition, restored old content and one further scalar acquisition in this life; later private updating remains limited by the adverse330 continuation, which is retained.'})
