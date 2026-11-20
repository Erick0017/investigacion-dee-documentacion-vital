"""Passive proof binding for Root's ONE eventual RP evidence registration."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';D=P/'estados/RP_A_PANEL12_R01'
RID='pi08_a_panel12_regulado_T861426_R01';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_ARP_PANEL12_01'
A='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01';OUT=P/'control/VERIFICACION_RO_A_PANEL12_PI08_R01.json'
def require(ok,text):
 if not ok:raise ValueError(text)
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def at(v,path):
 for k in path:v=v[k]
 return v
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
resultfile=D/'RESULTADO_REPRODUCCION.json';supfile=P/'control/SUPERVISION_RP_A_PANEL12_PI08_R01.json'
result=read(resultfile);supervision=read(supfile);context=read(D/'CONTEXTO_EJECUCION.json');imported=read(D/'IMPORTACION_DIAGNOSTICA.json')
require(result['recipe']==context['recipe']==RID and result['life']==context['life']==LIFE,'Exact actual recipe/life')
require(result['status']=='COMPLETED'and result['owner_closed_coherently']is True and supervision['closed']is True and supervision['original_A_unchanged']is True,'Actual coherent completion/source protection required')
require(result['criteria_met']is True and result['denominators']['correct']==12 and result['denominators']['evaluated_step_responses']==12,'Actual12/12 required; no fabricated pending result')
require(imported['new_native_ticks']==0 and imported['comparison']['physical_equal']and imported['comparison']['causal_prefix_equal'],'Complete exact0Native initial import required')
recipe=read(RP/'recetas'/(RID+'.json'));require(sha(RP/'recetas'/(RID+'.json'))==context['recipe_sha256'],'Frozen published recipe differs')
steps={s['label']:s for s in recipe['variants'][context['variant']]['batches'][0]}
runner=load('RP_pure_direct_receipt_paths',RP/'ejecutar_diagnostico.py');all_ids={};rows=[];outputs={}
for entry in result['rows']:
 step=steps[entry['step']];file=(D/entry['primary']).resolve(strict=True);require(file.is_relative_to(D.resolve()),'Bounded original primary')
 primary=read(file);value=primary['result'];value=json.loads(value)if isinstance(value,str)else value
 require(primary['status']=='completed'and primary['id']==entry['transport_id'],'Terminal actual primary required')
 direct=runner.receipts(value,step.get('receipt_paths',[]));require(not set(direct)&set(all_ids),'No inherited/previous-step Native IDs')
 for path in step.get('receipt_paths',[]):
  for item in at(value,path):
   receipt=item['receipt'];tick=receipt.get('requested_tick',item.get('tick',item.get('requested_tick')))
   require(type(tick)is int and value['before_tick']<=tick<=value['after_tick'],'Current-step Native input window required')
 all_ids.update(direct);literal=json.loads(primary['payload'])['situaciones'][0];observed=at(value,step['read_path'])if'read_path'in step else None
 if'expected'in step:require(type(observed)is type(step['expected'])and observed==step['expected'],'Actual witness mismatch')
 if step.get('actual_integer_binding'):
  binding=step['actual_integer_binding'];require(type(outputs[binding['from_step']])is int and literal[binding['field']]==outputs[binding['from_step']],'Literal must carry the actual preceding number')
 outputs[entry['step']]=observed
 rows.append({'step':entry['step'],'literal':literal,'before_tick':value['before_tick'],'after_tick':value['after_tick'],'observed':observed,'expected_evaluator_only':step.get('expected'),'primary':ref(file),'Native_inputs':{'unique_requested':len(direct),'status_counts':dict(Counter(v['status']for v in direct.values()))}})
counts=Counter(v['status']for v in all_ids.values());require(len(all_ids)==947 and counts=={'applied':947},'Exact947 direct terminal Native inputs')
require(result['native_receipts']['unique_requested']==result['native_receipts']['applied']==947 and result['native_receipts']['rejected']==result['native_receipts']['pending_or_other']==0,'Generic RP collector disagrees')
parser=load('RP_native_source_view_only',RP/'observador_pasivo.py');pair=Path(context['prefix']);manifest=read(pair/'EXPORTACION_SERVICIO.json')
require(sha(pair/'EXPORTACION_SERVICIO.json')==context['prefix_manifest_sha256'],'Complete source prefix hash changed')
source=parser.snapshot_view(pair/manifest['native_snapshot']);cardfile=D/'sistema/estado/vidas'/LIFE/'VIDA.json';card=read(cardfile);after=parser.snapshot_view(D/'sistema'/card['snapshot'])
require(after['encoded_sha256']==card['snapshot_sha256']and after['physical']=={k:card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')}and after['physical']['tick']==result['last_tick'],'Final actual card/physical/native snapshot mismatch')
require(after['native_receipts']-source['native_receipts']==947,'Runtime complete receipt-count delta differs from947 explicit current inputs')
sourcecardfile=C/'sistema/estado/vidas'/A/'VIDA.json';sourcecard=read(sourcecardfile)
require(sourcecard['physical']['tick']==861426 and sourcecard['snapshot_sha256']=='2eeef08e3bebac4e218178ed379fd99aa5fdeb03650c0454ad55c6534824c133','Protected sourceA changed')
keys={'R03':'DEE.Cognitive.PI07.regulation.environment.R03','C2C':'DEE.Cognitive.PI04.C2C.coordination.R01','regulated_FI':'DEE.Cognitive.PI07.regulated_FI_access.R01'}
progress={name:{'source_ordinal':json.loads(source['metadata'][key])['ordinal'],'diagnostic_final_ordinal':json.loads(after['metadata'][key])['ordinal']}for name,key in keys.items()}
require(progress['R03']=={'source_ordinal':12,'diagnostic_final_ordinal':12}and progress['C2C']=={'source_ordinal':31,'diagnostic_final_ordinal':31},'No R03/C2C opportunity may be consumed')
require(progress['regulated_FI']['diagnostic_final_ordinal']-progress['regulated_FI']['source_ordinal']==3,'Exactly three fixed regulated FI calls')
target=RP/'verificaciones'/RID/(LIFE+'.json')
proof={'schema':'DEE.PI08.A.RP.actual_panel12_passive_binding.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),'Native_executed_by_this_verifier':False,'DEE_imported':False,'RP_or_product_modified_by_verifier':False,
 'actual_material_control_completed':True,'life_id':LIFE,'recipe':RID,'variant':context['variant'],'rows':rows,
 'source_prefix':{'path':str(pair),'manifest_sha256':sha(pair/'EXPORTACION_SERVICIO.json'),'physical':source['physical'],'native_receipts':source['native_receipts']},
 'final_record':{'card':ref(cardfile),'snapshot':ref(D/'sistema'/card['snapshot']),'physical':after['physical'],'native_receipts':after['native_receipts'],'pending_native':after['pending_native']},
 'source_current_record':{'card':ref(sourcecardfile),'physical':sourcecard['physical'],'snapshot_sha256':sourcecard['snapshot_sha256']},'progress':progress,
 'actual_new_Native_ticks':after['physical']['tick']-861426,'functional_witnesses':12,'correct':12,'NULL':0,
 'Native_current_direct_unique':947,'Native_current_status_counts':dict(counts),'Runtime_receipt_delta':947,
 'result':ref(resultfile),'context':ref(D/'CONTEXTO_EJECUCION.json'),'import':ref(D/'IMPORTACION_DIAGNOSTICA.json'),'supervision':ref(supfile),
 'registration_executed_by_I4':False,'registration_target':str(target),'registration_already_exists':target.exists(),
 'Root_command':[str(C/'motor/python313/python.exe'),'-I','-B','-X','utf8',str(RP/'registrar_verificacion.py'),'--resultado',str(resultfile),'--nota','PI08 prospective A861426 panel12: actual12/12,947/947, actual13 then13-5=8; no C2C use. SourceA protected. Does not repair or promote B.'],
 'interpretation':['Availability of this exact acquired A prefix was demonstrated through the real RP frontdoor and fixed panel.','A and B panels begin at different complete cuts/phases; A success alone does not isolate a B-learning cause.','B conservation10/12 remains false. Existing None control is conditional and separate.']}
with OUT.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(OUT),'sha256':sha(OUT),'actual12':True,'Native947':True,'final_tick':after['physical']['tick'],'progress':progress,'registered_by_I4':False}))
