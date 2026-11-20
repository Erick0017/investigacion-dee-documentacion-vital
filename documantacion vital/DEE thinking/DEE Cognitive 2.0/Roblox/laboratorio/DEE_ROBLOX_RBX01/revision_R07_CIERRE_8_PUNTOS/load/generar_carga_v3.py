"""Version focal load to one prospective three-owner batch. FS/AST only."""
from pathlib import Path
import ast,hashlib,json
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'revision_R06_INTEGRAL_V2'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,text):
    ast.parse(text);p=ROOT/name
    if p.exists():raise FileExistsError(p)
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf8');return {'file':name,'sha256':digest(p),'bytes':p.stat().st_size}
pins={x:digest(ROOT/x)for x in('native/owner_support_v3.py','native/adapter_v3.py')}
profiles={}
for n in(1,2,3):
    profiles['LOAD'+str(n)]={'id':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_LOAD'+str(n),
      'lesson':[{'form':'luma','observedSign':1 if n!=2 else -1},{'form':'nara','observedSign':-1 if n==1 else 1}]}
protocol={'schema':'DEE.R07.three_owner_focal_load.R01','start_epoch':1794841620,'last_new_episode_epoch':1794859200,
 'hard_finish_epoch':1794863220,'latest_batch_start_epoch':1794852000,'latest_GO_epoch':1794855600,
 'stages':[{'simultaneous_lives':['LOAD1','LOAD2','LOAD3']}],'lifes':profiles,
 'episodes_per_life':3,'scope':'Native-only focal load; no Roblox movement/resource claim. Three independent descendant stores of the same PAR28 ancestry, not independent biological subjects.',
 'parent_tick':991187,'parent_completed_global':28,'parent_sequence':56,'global_tick_limit':160000,
 'declared_preparation':'Shared resources and observed sensor opportunities are fixed host preparation. Lesson then actualA then actualB are externally offered; this load test makes no cognitive planning claim.',
 'owner_memory_limit_bytes':536870912,'Native_threads':1,'raw_support_limit':10000}
(ROOT/'load/PROTOCOLO_CARGA_V3_R01.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2),encoding='utf8')
s=(OLD/'load/worker_carga.py').read_text('utf8')
s=s.replace('1794798600','1794859200').replace('1794802380','1794863220').replace('03:10UTC','20:00UTC')
start=s.index('PINS={');end=s.index('def sha',start);s=s[:start]+'PINS='+repr(pins)+'\n\n'+s[end:]
s=s.replace('PROTOCOLO_CARGA_R01.json','PROTOCOLO_CARGA_V3_R01.json').replace('RBX06_NATIVE_SCOPE_INTEGRAL_V2.json','RBX07_NATIVE_SCOPE_INTEGRAL_V3.json')
s=s.replace("scope['source_tick']==953651 and scope['parent_completed_opportunities']==4", "scope['source_tick']==991187 and scope['parent_completed_opportunities']==28")
s=s.replace("scope['max_cycles']==24", "scope['max_cycles']==3")
s=s.replace("need(a.stage==int(a.profile[-1]),'New LOAD1/2/3 enters only its declared first stage')", "need(a.stage==1,'One new three-owner batch; do not repeat a ladder')")
s=s.replace('RBX06_NATIVE_INTEGRAL_V2/events.jsonl','RBX07_NATIVE_INTEGRAL_V3/events.jsonl')
s=s.replace("sequence=8,", "sequence=56,").replace('native_tick=953651,world_time_ms=40750','native_tick=991187,world_time_ms=100000')
s=s.replace("owner_support_integral_v2.py", "owner_support_v3.py").replace("adapter_integral_v2.py", "adapter_v3.py").replace("tag='R06_'", "tag='R07_'")
s=s.replace("station=0,stage=2,contact=0,inventoryKey=False,inventoryResource=True,queryAvailable=False,", "station=2,stage=2,contact=2,inventoryKey=False,inventoryResource=False,queryAvailable=True,")
s=s.replace("stationSignal=-1,permissionStock=196,publicContactCode=0", "stationSignal=(1 if phase_name=='ROUTE_CHOICE' and state.get('query_applied')else-1),permissionStock=164,publicContactCode=2")
s=s.replace("numberAPresent=True,codeBPresent=True,numberAVersion=1,codeBCurrent=True", "numberAPresent=True,codeBPresent=False,numberAVersion=1,codeBCurrent=False")
s=s.replace("q2obs=observe('ROUTE_CHOICE');", "state['query_applied']=q1action['name']=='ASK_STATION';q2obs=observe('ROUTE_CHOICE');")
s=s.replace('DEE.RBX.IntegralV2.LoadWorker.R01','DEE.RBX.IntegralV3.LoadWorker.R01')
s=s.replace("choices=(1,2,3),required=True", "choices=(1,),required=True")
rows=[save('load/worker_carga_v3.py',s)]
s=(OLD/'load/ejecutar_etapa_carga.py').read_text('utf8')
s=s.replace('1794798600','1794859200').replace('1794802380','1794863220').replace('03:10UTC','20:00UTC')
s=s.replace('PROTOCOLO_CARGA_R01.json','PROTOCOLO_CARGA_V3_R01.json').replace('worker_carga.py','worker_carga_v3.py')
s=s.replace('100000','160000').replace('R06 global','R07 global')
s=s.replace('DEE.RBX01.R06.integrated.result.R01','DEE.RBX01.R07.integrated.result.R01').replace('INTEGRAL_V2_MAIN','INTEGRAL_V3_MAIN')
s=s.replace("need(time.time()<LAST_NEW,'No new load stage after20:00UTC')", "need(time.time()<protocol['latest_batch_start_epoch'],'Do not launch three owners too late; stage start before18:00UTC')")
s=s.replace("if ready and abort_reason is None:", "if ready and abort_reason is None and now<protocol['latest_GO_epoch']:")
s=s.replace("if not go_sent:\n            ready=", "if not go_sent:\n            if now>=protocol['latest_GO_epoch']:abort('LATEST_GO_MARGIN_EXPIRED')\n            ready=")
s=s.replace('DEE.RBX.IntegralV2.LoadStage.R01','DEE.RBX.IntegralV3.LoadStage.R01').replace('choices=(1,2,3),required=True','choices=(1,),required=True')
rows.append(save('load/ejecutar_carga3_v3.py',s))
(ROOT/'load/GENERACION_CARGA_V3.json').write_text(json.dumps({'Native_calls':0,'files':rows,'source':str(OLD),'protocol_sha256':digest(ROOT/'load/PROTOCOLO_CARGA_V3_R01.json')},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(rows))
