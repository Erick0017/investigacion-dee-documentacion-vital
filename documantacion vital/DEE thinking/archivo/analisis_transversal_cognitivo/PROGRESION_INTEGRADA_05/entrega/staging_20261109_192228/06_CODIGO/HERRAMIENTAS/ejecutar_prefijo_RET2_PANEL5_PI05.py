"""Root-only PI05 prefix: two actual C2C uses and five historical word uses.
No FIplus, Native execution on import, principal selection, reset or teaching.
The expected signs below are post-response evaluator checks, never actor input.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,re,sys
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/candidato/sistema'
PROTO=P/'control/PROTOCOLO_PREFIJO_RET2_PANEL5_PI05_R01.json'
_ACCOUNTING_GAP=None
def require(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(x,path):
 for key in path:x=x[key]
 return x

def add_receipts(all_receipts,groups,start,end):
 counts={};aliases=0
 for group,requests in groups.items():
  counts[group]=len(requests)
  for req in requests:
   r=req['receipt'];rid=req['id'];require(type(rid)is int and rid==r['id'],'Receipt identity mismatch')
   require(type(r['requested_tick'])is int and start<=r['requested_tick']<=end,'Current-call receipt outside time window')
   if rid in all_receipts:
    require(all_receipts[rid]['receipt']==r,'Contradictory receipt alias');aliases+=1
   else:all_receipts[rid]={'group':group,'receipt':r}
 return {'raw_group_counts':counts,'aliases_deduplicated':aliases}
def receipt_summary(items):
 states={}
 for v in items.values():states[v['receipt']['status']]=states.get(v['receipt']['status'],0)+1
 return {'unique_requested':len(items),'applied':states.get('applied',0),'rejected_or_other':len(items)-states.get('applied',0),'statuses':states}
def closed_ticks():
 global _ACCOUNTING_GAP
 total=0
 for path in(S/'estado/vidas').glob('*/VIDA.json'):
  imp=S/'estado/servicios_persistentes'/path.parent.name/'IMPORTACION.json'
  if imp.is_file():
   a=read(path);b=read(imp);n=a['physical']['tick']-b['physical']['tick'];require(n>=0,'Negative imported-life age');total+=n
 floor=read(P/'REGISTRO_CAMPANA.json').get('new_Native_ticks_closed_floor',0)
 require(type(floor)is int and floor>=0,'Invalid closed Native ledger floor')
 if _ACCOUNTING_GAP is None:_ACCOUNTING_GAP=max(0,floor-total)
 return max(total+_ACCOUNTING_GAP,floor)
def physical(packet):return packet['committed_snapshot']['physical']
def zero_tick(packet):require(packet['before_tick']==packet['after_tick'],'Administrative operation advanced Native')

def main(a):
 require(re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_[A-Za-z0-9_]{1,32}',a.vida),'Strict new PI05 diagnostic descendant ID required')
 require(re.fullmatch(r'PI05_[A-Z0-9_]{1,64}',a.tag),'Fresh explicit PI05 tag required')
 require(not(S/'estado/ACTIVO.json').exists(),'Isolated system must not select a principal')
 out=P/'control'/(a.tag+'.json');require(not out.exists(),'Existing proof: never replay IDs')
 recipe=C/'reproducibilidad/recetas/panel_12.json';rp=read(recipe);flat=[x for batch in rp['variants']['principal']['batches']for x in batch];selected=flat[:6]
 require([x['label']for x in selected]==['habitat_off','luma','nara','clasifica','suma','alfa'],'Existing panel exact first five witnesses required')
 protocol=read(PROTO);require(protocol['status']=='PREREGISTERED_BEFORE_NATIVE'and protocol['runner_sha256']==sha(Path(__file__)),'Exact preregistered runner required')
 require(protocol['panel_recipe_sha256']==sha(recipe),'Historical recipe changed; no reader adaptation')
 require(a.modo_oportunidad in protocol['allowed_opportunity_modes'],'Opportunity mode is not frozen in this protocol')
 if a.brazo=='yoke':require(a.extender_yoke,'Old YOKE plan exhausted; use explicit --extender-yoke after Root installs the frozen PI05 bridge')
 else:require(not a.extender_yoke,'Only the historical YOKE arm may receive its fixed future extension')
 card=read(S/'estado/vidas'/a.vida/'VIDA.json');require(card['physical']['N']==67 and card['physical']['tick']==816019,'Exact coherent ownT816019 prefix required')
 snapshot=S/card['snapshot'];require(sha(snapshot)==card['snapshot_sha256'],'Imported snapshot bytes differ')
 for suffix in ['YOKE_EXTENSION','STATE_EXTENDED','STATE_START','OP_20','OP_21','habitat_off','luma','nara','clasifica','suma','alfa','STATE_FINAL']:
  require(not(P/'ensayos'/(a.tag+'_'+suffix+'.json')).exists(),'Prior material request primary exists; new tag required')
 budget=read(P/'REGISTRO_CAMPANA.json');require(datetime.datetime.now().astimezone()<datetime.datetime.fromisoformat(budget['science_cutoff_local']),'Scientific closure time reached')
 floor=closed_ticks();require(floor+1857<=budget['budget']['Native_ticks_all_branches'],'Insufficient all-branch Native allowance')
 if a.dry_run:
  print(json.dumps({'mode':'READ_ONLY_PREFLIGHT_NO_OWNER','life':a.vida,'arm':a.brazo,'prefix_tick':816019,'literal_opportunities':[{'modo':a.modo_oportunidad}]*2,'word_literals':[x['literal']for x in selected],'yoke_extension_literal':{'modo':'eci01-pi05-yoke-extender'}if a.extender_yoke else None,'protocol_sha256':sha(PROTO),'Native_ticks':0,'owner_started':False},ensure_ascii=False,indent=2));return 0
 # Purpose-built existing owner is imported only after explicit execution and preflight.
 sys.path.insert(0,str(P/'codigo'));from servicio_ensayo_PI05 import Owner
 rows=[];ids={};initial=None;final=None;stop=None;error=None;owner=None;closed=False;before_tick=816019;last=before_tick
 try:
  with Owner(a.vida,a.tag)as owner:
   initial=owner.material(a.tag+'_STATE_START',{'modo':'eci01-pi04-c2c-estado'},feedback='omit');zero_tick(initial)
   state=initial['result']['rows'][0];progress=state['progress'];device=state['device'];expected_arm={'yoke':'yoked'}.get(a.brazo,a.brazo)
   require(progress['ordinal']==device['ordinal']==20 and progress['arm']==expected_arm,'Own history/ordinal changed; do not reset or relabel')
   require(not any(progress.get(x)for x in['pending','uncertain','halted_reason'])and not any(device.get(x)for x in['pending','feedback_pending','uncertain']),'Uncertain/task future must be preserved')
   require(len(device['resources'])==26 and physical(initial)['tick']==816019,'Exact finite fixture/age differs')
   if a.extender_yoke:
    frozen_old={k:progress[k]for k in['plan','arm','ordinal','rows']}
    extension=owner.material(a.tag+'_YOKE_EXTENSION',{'modo':'eci01-pi05-yoke-extender'},feedback='omit');zero_tick(extension)
    require(all(physical(initial)[k]==physical(extension)[k]for k in['N','tick','RAW_sha256','clocks_sha256']),'Prospective metadata extension changed Native physical state')
    viewed=owner.material(a.tag+'_STATE_EXTENDED',{'modo':'eci01-pi04-c2c-estado'},feedback='omit');zero_tick(viewed)
    require({k:viewed['result']['rows'][0]['progress'][k]for k in frozen_old}==frozen_old,'Historical plan/arm/rows/ordinal were rewritten')
   for ordinal in [20,21]:
    require(datetime.datetime.now().astimezone()<datetime.datetime.fromisoformat(budget['science_cutoff_local']),'Scientific closure time reached')
    actual=owner.material(a.tag+'_OP_'+str(ordinal),{'modo':a.modo_oportunidad},feedback='omit');r=actual['result']['rows'][0]
    require(r['ordinal']==ordinal and actual['before_tick']==last,'Nonconsecutive actual trajectory')
    local={};groups={'outer':r['requests']}
    if r['native_arithmetic']is not None:groups['FI']=r['native_arithmetic']['native_operation']['native_trial']['requests']
    if r['second_native_use']is not None and'requests'in r['second_native_use']:groups['MU']=r['second_native_use']['requests']
    add_receipts(local,groups,actual['before_tick'],actual['after_tick']);require(not(set(local)&set(ids)),'Prior input reused as a new event');ids.update(local)
    counts=receipt_summary(local);quality=r['native_input_summary'];require(counts['unique_requested']==quality['unique_requested']and counts['applied']==quality['applied'],'Runner/controller dose mismatch')
    first=r['first_reader']['choice'];second=None if r['second_native_use']is None or r['second_native_use'].get('reader')is None else r['second_native_use']['reader']['choice'];last=actual['after_tick']
    record={'kind':'C2C_RETENTION','ordinal':ordinal,'spec':r['spec'],'before_tick':actual['before_tick'],'after_tick':last,'first_choice':first,'selected_operation':r['selected_operation'],'actual_numeric_result':r['actual_numeric_result'],'second_choice':second,'actual_route':r['applied_route'],'useful_product':r['useful_product'],'actual_failed':r['actual_failed'],'returned_failed':r['returned_failed'],'Native_inputs':counts,'normalized_calendar':r['normalized_calendar'],'primary':str(P/'ensayos'/(a.tag+'_OP_'+str(ordinal)+'.json'))};rows.append(record);print(json.dumps(record,ensure_ascii=False),flush=True)
    if r['first_NULL_preserved']or r['first_rejected_preserved']or counts['rejected_or_other']or type(first)is not int or first not in(-1,0,1)or type(r['actual_numeric_result'])is not int or type(second)is not int or second not in(-1,0,1):
     stop={'stage':'RETENTION','ordinal':ordinal,'reason':'First NULL, rejection or unknown output preserved','actual_counts':counts};break
    require(last-actual['before_tick']==782 and counts['unique_requested']==186,'Actual dose/age differs from frozen retained opportunity; preserve and stop')
   if stop is None:
    # This 0-tick habitat pause is AFTER the two retention jobs, as in PI04.
    for spec in selected:
     literal=dict(spec['literal']);actual=owner.material(a.tag+'_'+spec['label'],literal,feedback='omit');require(actual['before_tick']==last,'Word-panel continuity differs');last=actual['after_tick']
     local={};groups={str(i):get(actual,path)for i,path in enumerate(spec.get('receipt_paths',[]))};add_receipts(local,groups,actual['before_tick'],actual['after_tick']);require(not(set(local)&set(ids)),'Material event re-counted across stages');ids.update(local);counts=receipt_summary(local)
     if spec.get('require_zero_ticks'):zero_tick(actual)
     observed=get(actual,spec['read_path'])if'read_path'in spec else None
     row={'kind':'HISTORICAL_WORD','label':spec['label'],'literal':literal,'before_tick':actual['before_tick'],'after_tick':last,'observed':observed,'expected_evaluator_only':spec.get('expected'),'correct':None if'expected'not in spec else observed==spec['expected'],'Native_inputs':counts,'primary':str(P/'ensayos'/(a.tag+'_'+spec['label']+'.json'))};rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
     if counts['rejected_or_other']or('read_path'in spec and (type(observed)is not int or observed not in(-1,0,1)or row['correct']is False)):
      stop={'stage':'HISTORICAL_WORD','label':spec['label'],'reason':'First wrong, silent or rejected named witness preserved','actual_counts':counts};break
   final=owner.material(a.tag+'_STATE_FINAL',{'modo':'eci01-pi04-c2c-estado'},feedback='omit');zero_tick(final);require(final['after_tick']==last,'Final passive state changed age');owner.control('guardar')
  closed=True
 except Exception as exc:error={'type':type(exc).__name__,'message':str(exc),'no_retry':True}
 if owner is not None and owner.proc is not None:closed=bool(owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running'))
 proof={'schema':'DEE.PI05.prefix_RET2_words5.actual.R01','life_id':a.vida,'historical_arm':a.brazo,'opportunity_mode':a.modo_oportunidad,'protocol':str(PROTO),'protocol_sha256':sha(PROTO),'recipe_sha256':sha(recipe),'initial':initial,'final':final,'rows':rows,'before_tick':before_tick,'after_tick':last,'new_Native_ticks':last-before_tick,'Native_inputs':receipt_summary(ids),'word_witnesses_executed':sum(r['kind']=='HISTORICAL_WORD'and r['correct']is not None for r in rows),'word_correct':sum(r.get('correct')is True for r in rows),'retention_opportunities_executed':sum(r['kind']=='C2C_RETENTION'for r in rows),'retention_products':sum(r.get('useful_product',False)for r in rows),'FIplus_executed':False,'owner_closed_coherently':closed,'stop_reason':stop,'error':error,'principal_modified':False,'no_control_memory_merge':True,'budget_floor_before':floor,'budget_measured_after':closed_ticks(),'expected_values_never_actor_inputs':True,'status':'COMPLETED_PREFIX_NO_FI'if closed and stop is None and error is None else'STOPPED_PRESERVED'}
 if proof['status']=='COMPLETED_PREFIX_NO_FI'and not(last==817876 and proof['new_Native_ticks']==1857 and proof['Native_inputs']=={'unique_requested':407,'applied':407,'rejected_or_other':0,'statuses':{'applied':407}}and proof['word_witnesses_executed']==proof['word_correct']==5):
  proof['status']='STOPPED_PRESERVED';proof['error']={'type':'FINAL_CRITERION_MISMATCH','message':'Final prefix age/dose/witness count differs; no FI or retry'}
 with out.open('x',encoding='utf8')as h:json.dump(proof,h,ensure_ascii=False,indent=2)
 print(json.dumps({'proof':str(out),'status':proof['status'],'Native_ticks':proof['new_Native_ticks'],'inputs':proof['Native_inputs'],'after_tick':last,'owner_closed_coherently':closed,'FIplus_executed':False},ensure_ascii=False),flush=True)
 return 0 if proof['status']=='COMPLETED_PREFIX_NO_FI'else 2
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--vida',required=True);ap.add_argument('--brazo',choices=('real','none','yoke'),required=True);ap.add_argument('--tag',required=True);ap.add_argument('--modo-oportunidad',default='eci01-pi04-c2c-oportunidad');ap.add_argument('--extender-yoke',action='store_true');ap.add_argument('--dry-run',action='store_true');raise SystemExit(main(ap.parse_args()))
