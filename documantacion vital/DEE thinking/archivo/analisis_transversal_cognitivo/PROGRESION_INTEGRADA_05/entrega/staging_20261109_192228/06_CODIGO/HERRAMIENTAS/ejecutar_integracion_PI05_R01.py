"""Root-only finite PI05 conservation/integration phases, no execution on import.
One inherited diagnostic life per phase; phases continue the same life, never
merge controls. Guard is checked in a frozen snapshot, NEVER reinjected here.
The actor receives only exact old operation literals/public fixtures.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,re,sys,struct
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/candidato/sistema';PROTO=P/'control/PROTOCOLO_INTEGRACION_PI05_R01.json';_GAP=None
PHASES={'panel','comparaciones','reserva','retencion','reapertura-final','comprobacion-final','orden-a','orden-b'}
GUARD_CHANNEL='PI05.P0.zero_carrier.guard.R01';GUARD_SITE=(19,53,20);GUARD_RAW=4<<60
class StopKnown(Exception):pass

def need(x,s):
 if not x:raise ValueError(s)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return{'path':str(Path(p).resolve()),'bytes':Path(p).stat().st_size,'sha256':sha(p)}
def module(p,n):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def get(v,path):
 for k in path:v=v[k]
 return v

def guard_snapshot(card):
 m=module(P/'codigo/contrastar_prefijos_C2C_PI05_pasivo.py','PI05_integration_frozen_parser');v=m.parse(S/card['snapshot'],card['snapshot_sha256']);i=(GUARD_SITE[0]*67+GUARD_SITE[1])*67+GUARD_SITE[2]
 rs=[r for r in v[5]if GUARD_CHANNEL in r['channels']]
 need(len(rs)==1 and rs[0]['status']==2 and rs[0]['kind']==1,'Exactly one applied legal guard birth required; no reinjection or diagnostic edit')
 need(not v[4],'Native agenda is not settled')
 need(int(v[1][i])==GUARD_RAW,'Persistent declared SEM4 support is absent/transformed; preserve and review, do not silently reinstall')
 channel=[x for x in v[3]if x[0]==GUARD_CHANNEL];need(len(channel)==1,'Exact fixed guard channel missing');spec=struct.unpack('<iiiIiiiBBB',bytes.fromhex(channel[0][1]));need(tuple(spec[:3])==GUARD_SITE and spec[3]==0 and tuple(spec[4:7])==(0,0,0)and spec[7]==4 and spec[8]==1,'Declared legal guard channel fields differ')
 return{'site':list(GUARD_SITE),'RAW':str(v[1][i]),'clock':int(v[2][i]),'receipt':rs[0],'channel_binary_spec':channel[0][1],'snapshot':v[0]['snapshot'],'physical':v[0]['physical'],'Native_pending':0,'guard_not_reinjected_by_this_runner':True}

def receipts(items,before,after,allids):
 local={};aliases=0
 for req in items:
  r=req['receipt'];rid=req['id'];need(type(rid)is int and rid==r['id'],'Receipt identity')
  need(before<=r['requested_tick']<=after,'Receipt outside actual call')
  if rid in local:need(local[rid]==r,'Contradictory receipt alias');aliases+=1
  else:local[rid]=r
 need(not(set(local)&set(allids)),'Repeated prior receipt counted as new');allids.update(local)
 return {'unique_requested':len(local),'applied':sum(r['status']=='applied'for r in local.values()),'rejected_or_other':sum(r['status']!='applied'for r in local.values()),'aliases':aliases}
def count_all(ids):return{'unique_requested':len(ids),'applied':sum(r['status']=='applied'for r in ids.values()),'rejected_or_other':sum(r['status']!='applied'for r in ids.values())}
def closed_ticks():
 global _GAP
 n=0
 for f in(S/'estado/vidas').glob('*/VIDA.json'):
  imp=S/'estado/servicios_persistentes'/f.parent.name/'IMPORTACION.json'
  if imp.exists():
   d=read(f)['physical']['tick']-read(imp)['physical']['tick'];need(d>=0,'Imported age rewound');n+=d
 floor=read(P/'REGISTRO_CAMPANA.json').get('new_Native_ticks_closed_floor',0);need(type(floor)is int and floor>=0,'Invalid ledger')
 if _GAP is None:_GAP=max(0,floor-n)
 return max(n+_GAP,floor)
def closed_state(owner,tag):
 value=owner.material(tag,{'modo':'eci01-pi04-c2c-estado'},feedback='omit');need(value['before_tick']==value['after_tick'],'Read-only task state advanced Native');return value

def main(a):
 need(a.etapa in PHASES and re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_[A-Za-z0-9_]{1,32}',a.vida),'Strict PI05 diagnostic life and fixed phase')
 need(re.fullmatch(r'PI05_[A-Z0-9_]{1,64}',a.tag),'Fresh PI05 tag')
 need(not(S/'estado/ACTIVO.json').exists(),'Never run conservation materially on selected principal')
 out=P/'control'/(a.tag+'.json');need(not out.exists(),'Existing phase proof; never retry IDs')
 pr=read(PROTO);need(pr['status']=='PREREGISTERED_BEFORE_RESERVES'and pr['runner_sha256']==sha(Path(__file__)),'Frozen integration protocol required')
 recipepath=C/'reproducibilidad/recetas/panel_12.json';need(sha(recipepath)==pr['historical_panel_recipe_sha256'],'Historical panel/reader changed');recipe=read(recipepath);specs=[x for batch in recipe['variants']['principal']['batches']for x in batch]
 need(sum('expected'in s for s in specs)==12,'Exactly12historical uses, not12independentfaculties')
 cardpath=S/'estado/vidas'/a.vida/'VIDA.json';card=read(cardpath);need(card['physical']['N']==67,'Same inherited N67 only');before=card['physical']['tick'];guard_before=guard_snapshot(card)
 expected_prior={'comparaciones':'panel','reserva':'comparaciones','retencion':'reserva','reapertura-final':'retencion','comprobacion-final':'reapertura-final'}
 prior=None
 if a.etapa in expected_prior:
  need(a.anterior is not None,'Previous coherent phase proof required');prior=read(a.anterior);need(prior['life_id']==a.vida and prior['phase']==expected_prior[a.etapa]and prior['status']=='COMPLETED_PHASE'and prior['owner_closed_coherently']is True,'Do not merge futures or skip phase')
  need(prior['closed_card']['physical']==card['physical'],'Candidate advanced outside the declared continuation; do not replace or hide it')
 if a.etapa.startswith('orden-'):need('_ORD_'in a.vida,'Order/phase controls require explicitly named control clones; never merge into main')
 budget=read(P/'REGISTRO_CAMPANA.json');deadline=datetime.datetime.fromisoformat(budget['science_cutoff_local']);need(datetime.datetime.now().astimezone()<deadline,'Science deadline')
 floor=closed_ticks();need(floor+pr['conservative_ticks_per_phase'][a.etapa]<=budget['budget']['Native_ticks_all_branches'],'Conservative Native budget insufficient')
 if a.dry_run:
  print(json.dumps({'mode':'READ_ONLY_NO_OWNER','phase':a.etapa,'life':a.vida,'before_tick':before,'guard':guard_before,'actor_never_receives_expected':True,'Native_ticks':0},ensure_ascii=False,indent=2));return 0
 sys.path.insert(0,str(P/'codigo'));from servicio_ensayo_PI05 import Owner
 rows=[];ids={};numbers={};owner=None;initial=None;final=None;last=before;stop=None;error=None
 def run_spec(owner,spec):
  nonlocal last
  need(datetime.datetime.now().astimezone()<deadline,'Science deadline');literal=dict(spec['literal'])
  if'actual_integer_binding'in spec:
   b=spec['actual_integer_binding'];actual=numbers[b['from_step']];need(type(actual)is int,'Actual priorintegerabsent; no expectedfallback');literal[b['field']]=actual
  actual=owner.material(a.tag+'_'+spec['label'],literal,feedback='omit');need(actual['before_tick']==last,'Trajectory discontinuity');last=actual['after_tick']
  req=[]
  for path in spec.get('receipt_paths',[]):req+=get(actual,path)
  counts=receipts(req,actual['before_tick'],last,ids)
  if spec.get('require_zero_ticks'):need(last==actual['before_tick'],'Administrative pauseadvancedNative')
  observed=get(actual,spec['read_path'])if'read_path'in spec else None
  if'read_path'in spec:numbers[spec['label']]=observed
  expected=spec.get('expected')
  if spec.get('evaluate_comparison_after_actual'):expected=(literal['izquierda']>literal['derecha'])-(literal['izquierda']<literal['derecha'])
  row={'kind':'OLD_FUNCTION','label':spec['label'],'literal':literal,'before_tick':actual['before_tick'],'after_tick':last,'observed':observed,'expected_evaluator_only':expected,'correct':None if expected is None else observed==expected,'Native_inputs':counts,'primary':str(P/'ensayos'/(a.tag+'_'+spec['label']+'.json'))};rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
  if counts['rejected_or_other']or(expected is not None and(type(observed)is not int or observed!=expected)):raise StopKnown('First incorrect,NULL,unknown or rejected old use: '+spec['label'])
 def cmp(label,left,right):return{'label':label,'literal':{'modo':'eci01-balance','izquierda':left,'derecha':right},'read_path':['result','rows',0,'early_physical_choice'],'receipt_paths':[['result','rows',0,'all_material_receipts']],'evaluate_comparison_after_actual':True}
 def run_c2c(owner,ordinal):
  nonlocal last
  need(datetime.datetime.now().astimezone()<deadline,'Science deadline');actual=owner.material(a.tag+'_C2C_'+str(ordinal),{'modo':'eci01-pi04-c2c-oportunidad'},feedback='omit');r=actual['result']['rows'][0];need(r['ordinal']==ordinal and actual['before_tick']==last,'C2Ccounter/trajectory mismatch');last=actual['after_tick']
  req=list(r['requests'])
  if r['native_arithmetic']is not None:req+=r['native_arithmetic']['native_operation']['native_trial']['requests']
  if r['second_native_use']is not None and'requests'in r['second_native_use']:req+=r['second_native_use']['requests']
  counts=receipts(req,actual['before_tick'],last,ids);quality=r['native_input_summary'];need(counts['unique_requested']==quality['unique_requested']and counts['applied']==quality['applied'],'C2Caudit scope mismatch')
  op=r['selected_operation'];ref=(r['spec']['left']+r['spec']['right']if op=='suma'else r['spec']['left']-r['spec']['right']if op=='diferencia'else None)
  product=r['actual_effect']['product'];verified=None
  if product is not None:
   rel=Path(product['path']);need(not rel.is_absolute()and len(rel.parts)==2 and rel.parts[0]=='products','Bounded product path');file=S/'estado/servicios_locales'/a.vida/'PI04_C2C_COORDINACION_R01/dispositivo'/rel;b=file.read_bytes();need(len(b)==product['bytes']==64 and hashlib.sha256(b).hexdigest()==product['sha256']and int.from_bytes(b[:2],'little')==r['actual_numeric_result'],'Actual64Bproduct/payload differs');verified=info(file)
  row={'kind':'C2C','ordinal':ordinal,'spec':r['spec'],'before_tick':actual['before_tick'],'after_tick':last,'first_choice':r['first_reader']['choice'],'operation':op,'actual_native_number':r['actual_numeric_result'],'arithmetic_reference_only_after_actual':ref,'arithmetic_correct':type(r['actual_numeric_result'])is int and r['actual_numeric_result']==ref,'second_choice':None if r['second_native_use']is None else r['second_native_use'].get('reader',{}).get('choice'),'actual_route':r['applied_route'],'useful_product':r['useful_product'],'actual_product':verified,'actual_failed':r['actual_failed'],'returned_failed':r['returned_failed'],'Native_inputs':counts,'normalized_calendar':r['normalized_calendar'],'primary':str(P/'ensayos'/(a.tag+'_C2C_'+str(ordinal)+'.json'))};rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
  if r['first_NULL_preserved']or r['first_rejected_preserved']or counts['rejected_or_other']or counts['unique_requested']!=186 or not row['arithmetic_correct']or not r['useful_product']:raise StopKnown('First C2CNULL,rejection,incorrectarithmetic or nonuseful effect preserved: '+str(ordinal))
 try:
  with Owner(a.vida,a.tag)as owner:
   initial=closed_state(owner,a.tag+'_STATE_START');need(initial['before_tick']==before,'Initialagechanged');m=initial['result']['rows'][0]['progress'];device=initial['result']['rows'][0]['device'];need(m['arm']=='real'and not any(m.get(k)for k in('pending','uncertain','halted_reason'))and not any(device.get(k)for k in('pending','feedback_pending','uncertain')),'Own closedrealhistory required')
   start={'panel':22,'comparaciones':22,'reserva':22,'retencion':24,'reapertura-final':26,'comprobacion-final':28,'orden-a':22,'orden-b':22}[a.etapa];need(m['ordinal']==device['ordinal']==start,'Wrong current counter; no reset or newlifeperphase')
   if a.etapa in('reserva','retencion','reapertura-final','comprobacion-final','orden-a','orden-b'):need(len(device['resources'])==30 and m['protocol_sha256']==pr['effective_C2C30_protocol_sha256'],'Explicit30resourceextension must be actuallyadmitted before reserves')
   if a.etapa=='panel':
    for spec in specs:run_spec(owner,spec)
   elif a.etapa=='comparaciones':
    for spec in[cmp('RES_POS_20_7',20,7),cmp('RES_NEG_4_16',4,16),cmp('RES_ZERO_13_13',13,13)]:run_spec(owner,spec)
   elif a.etapa in('reserva','retencion','reapertura-final'):
    for ordinal in{'reserva':[22,23],'retencion':[24,25],'reapertura-final':[26,27]}[a.etapa]:run_c2c(owner,ordinal)
   elif a.etapa=='comprobacion-final':
    for spec in[cmp('FINAL_FIplus',14,3),*[x for x in specs if x['label']in('luma','alfa')]]:run_spec(owner,spec)
   else:
    if a.etapa=='orden-b':
     wait=owner.material(a.tag+'_WAIT11',{'modo':'eci01-pi05-esperar','ticks':11},feedback='omit');need(wait['before_tick']==last and wait['after_tick']-last==11,'Actualwaitdiffers');last=wait['after_tick'];rows.append({'kind':'DECLARED_WAIT','ticks':11,'before_tick':wait['before_tick'],'after_tick':last})
    order=[cmp('ORDER_POS',14,3),cmp('ORDER_NEG',2,11),cmp('ORDER_ZERO',6,6)]
    if a.etapa=='orden-b':order=list(reversed(order))
    for spec in order:run_spec(owner,spec)
    for ordinal in[22,23]:run_c2c(owner,ordinal)
   final=closed_state(owner,a.tag+'_STATE_FINAL');need(final['after_tick']==last,'FinalstateadvancedNative');owner.control('guardar')
 except StopKnown as exc:stop=str(exc)
 except Exception as exc:error={'type':type(exc).__name__,'message':str(exc),'no_retry':True}
 closed=owner is not None and owner.proc is not None and owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running');newcard=read(cardpath);guard_after=None
 if closed:
  try:guard_after=guard_snapshot(newcard)
  except Exception as exc:
   if error is None:error={'type':'GUARD_CONTINUATION_CHECK_FAILED','message':str(exc),'no_reinstall':True}
 expected_counts={'panel':929,'comparaciones':528,'reserva':372,'retencion':372,'reapertura-final':372,'comprobacion-final':190,'orden-a':900,'orden-b':900}
 if closed and stop is None and error is None and(count_all(ids)['unique_requested']!=expected_counts[a.etapa]or count_all(ids)['rejected_or_other']or newcard['physical']['tick']!=last):error={'type':'FINAL_AGE_OR_DOSE_MISMATCH','message':'Closedphasecriterionnotmet; primariespreserved,no automaticretry'}
 status='COMPLETED_PHASE'if closed and stop is None and error is None else'STOPPED_PRESERVED'
 proof={'schema':'DEE.PI05.integration_phase.actual.R01','phase':a.etapa,'status':status,'life_id':a.vida,'initial_tick':before,'after_tick':newcard['physical']['tick']if closed else last,'new_Native_ticks':newcard['physical']['tick']-before if closed else None,'rows':rows,'Native_inputs':count_all(ids),'old_witnesses':sum(r['kind']=='OLD_FUNCTION'and r['correct']is not None for r in rows),'old_correct':sum(r.get('correct')is True for r in rows),'C2C_attempted':sum(r['kind']=='C2C'for r in rows),'C2C_products':sum(r.get('useful_product',False)for r in rows),'guard_before':guard_before,'guard_after':guard_after,'guard_injections_by_this_runner':0,'initial':initial,'final':final,'owner_closed_coherently':bool(closed),'closed_card':newcard,'closed_snapshot':info(S/newcard['snapshot'])if closed else None,'prior_phase_proof':None if a.anterior is None else info(a.anterior),'protocol':info(PROTO),'historical_recipe':info(recipepath),'error':error,'scientific_stop':stop,'Native_budget_before':floor,'Native_budget_after':closed_ticks(),'principal_modified':False,'no_promotion_by_runner':True,'host_prepared_sequence_not_learned_plan':True}
 with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
 print(json.dumps({'proof':str(out),'status':status,'phase':a.etapa,'Native_inputs':proof['Native_inputs'],'new_Native_ticks':proof['new_Native_ticks'],'closed':bool(closed)},ensure_ascii=False),flush=True);return 0 if status=='COMPLETED_PHASE'else 2
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--vida',required=True);ap.add_argument('--etapa',choices=sorted(PHASES),required=True);ap.add_argument('--tag',required=True);ap.add_argument('--anterior',type=Path);ap.add_argument('--dry-run',action='store_true');raise SystemExit(main(ap.parse_args()))
