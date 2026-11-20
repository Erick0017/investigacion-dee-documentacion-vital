"""Root prospective optional external reference, no world/Native reads."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';F=H/'SELLO_PI09_D_WSLS_R01.json'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not F.exists();d=read(H/'SELLO_PI09_D_R02.json');r=read(P/'REGISTRO_CAMPANA.json');assert r['budget']['diagnostic_worlds_all_new']==16 and r['budget']['Native_ticks_all_branches']==220000
p=read(H/'PROTOCOLO_PI09_D_WSLS_R01.json');assert p['maximum_opportunities']==6 and p['maximum_ticks']==13063 and p['initial_second_motor_by_bit']=={'0':-1,'1':1}
names=('pi09_referencia_contextual_D_WSLS_R01.py','PROTOCOLO_PI09_D_WSLS_R01.json','pi09_entorno_persistente_D_R02.py')
v={'schema':'DEE.PI09.D.material_context_WSLS.source_seal.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),'life_id':p['life_id'],'protocol_sha256':sha(H/'PROTOCOLO_PI09_D_WSLS_R01.json'),'same_D_source_prefix':d['source_prefix'],'D_source_seal_sha256':sha(H/'SELLO_PI09_D_R02.json'),'Root_optional_execution_authorized':True,'minimum_prospective_world_slot':16,'closure_ticks_reserved':13000,'files_sha256':{n:sha(H/n)for n in names},'not_Native_or_principal':True,'execution_still_conditional_on_actual_remaining_time_ticks_resources':True,'rule_fixed_before_reference_material':'Only actual released bit; initial0:-1/1:+1, keep success/flip actual failure, Native query1 unchanged, force only reference motor2.','Native_executed':False}
F.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'seal':str(F),'sha256':sha(F),'Native_executed':False}))
