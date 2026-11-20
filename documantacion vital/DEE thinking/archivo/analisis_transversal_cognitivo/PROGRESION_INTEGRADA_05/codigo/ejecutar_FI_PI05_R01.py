"""Root-only single legal FI128 use with a fixed prospective observer condition.
No owner on import. Public operands only enter the actor. Comparison reference
is evaluated AFTER the Native response. NULL is never replaced by material0.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,re,sys
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/candidato/sistema'
PROTOCOL=P/'control/PROTOCOLO_FI_PI05_R01.json';INSTRUMENT=S/'capacidades/PROTOCOLO_PI05_TRANSITO_R01.json';_GAP=None

def need(x,msg):
 if not x:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'path':str(Path(p).resolve()),'bytes':Path(p).stat().st_size,'sha256':sha(p)}
def literal(left,right,capture):return {'modo':'eci01-pi05-fiplus','izquierda':left,'derecha':right,'captura':capture}
def count_receipts(requests,before,after):
 ids={};aliases=0
 for item in requests:
  r=item['receipt'];rid=item['id'];need(type(rid)is int and rid==r['id'],'Native receipt identity mismatch')
  need(type(r['requested_tick'])is int and before<=r['requested_tick']<=after,'Native receipt outside actual trial')
  if rid in ids:need(ids[rid]==r,'Contradictory alias receipt');aliases+=1
  else:ids[rid]=r
 states={}
 for r in ids.values():states[r['status']]=states.get(r['status'],0)+1
 return {'unique_requested':len(ids),'applied':states.get('applied',0),'rejected_or_other':len(ids)-states.get('applied',0),'statuses':states,'aliases_deduplicated':aliases}
def summarize(actual,left,right):
 # This function is called ONLY after owner.material returns the actual result.
 row=actual['result']['rows'][0];before=actual['before_tick'];after=actual['after_tick'];need(row['before_tick']==before and row['after_tick']==after,'Wrapper/Native time mismatch')
 counts=count_receipts(row['requests'],before,after);q=row['Native_inputs'];need(all(counts[k]==q[k]for k in('unique_requested','applied','rejected_or_other')),'Native/runner receipt scope mismatch')
 expected=(left>right)-(left<right);early=row['early_physical_choice'];late=row['old_q6_choice']
 for choice in(early,late):need(choice is None or(type(choice)is int and choice in(-1,0,1)),'Unknown physical choice type/sign')
 if counts['rejected_or_other']:outcome='NATIVE_REJECTION_OR_OTHER_PRESERVED'
 elif early is None:outcome='NATIVE_NULL_PRESERVED'
 elif early==0:outcome='NATIVE_MATERIAL_ZERO'
 elif early==expected:outcome='VALID_NATIVE_CORRECT'
 else:outcome='VALID_NATIVE_INCORRECT'
 return {'before_tick':before,'after_tick':after,'new_Native_ticks':after-before,'public_operands':{'left':left,'right':right},'codec_bias':20,'calendar':row['calendar'],'early_physical_choice':early,'old_q6_choice':late,'evaluation_reader':'existing_panel_early_physical_choice_q4','reference_evaluator_only_after_actual_response':expected,'early_correct':early is not None and early==expected,'old_q6_correct':late is not None and late==expected,'NULL_is_not_material_zero':True,'early_is_NULL':early is None,'early_is_material_zero':type(early)is int and early==0,'outcome':outcome,'Native_inputs':counts,'external_global_capture':row['external_global_capture'],'fragmented_boundaries':row['fragmented_boundaries'],'legacy_result_unchanged':row['legacy_result']}

def frame_usage(root):
 usage={'anchors':0,'delta_frames':0,'frames':0,'directories':[]}
 if not root.exists():return usage
 for path in sorted(root.glob('*/*/FRAMES.jsonl')):
  rows=[json.loads(x)for x in path.read_text('utf8').splitlines()if x];index=path.with_name('INDEX.json')
  if index.exists():need(read(index)['frames']==rows,'Existing global index/journal disagree; no new capture until resolved')
  kinds=[r['kind']for r in rows];need(all(k in('anchor','xor_uint64')for k in kinds),'Unknown existing frame kind')
  usage['anchors']+=kinds.count('anchor');usage['delta_frames']+=kinds.count('xor_uint64');usage['frames']+=len(rows);usage['directories'].append({'path':str(path.parent.resolve()),'closed_index':index.exists(),'frames':len(rows),'anchors':kinds.count('anchor'),'deltas':kinds.count('xor_uint64')})
 return usage

def closed_ticks():
 global _GAP
 total=0
 for p in(S/'estado/vidas').glob('*/VIDA.json'):
  imp=S/'estado/servicios_persistentes'/p.parent.name/'IMPORTACION.json'
  if imp.exists():
   delta=read(p)['physical']['tick']-read(imp)['physical']['tick'];need(delta>=0,'Invalid imported age');total+=delta
 floor=read(P/'REGISTRO_CAMPANA.json').get('new_Native_ticks_closed_floor',0);need(type(floor)is int and floor>=0,'Invalid budget ledger')
 if _GAP is None:_GAP=max(0,floor-total)
 return max(total+_GAP,floor)

def main(a):
 need(re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_[A-Za-z0-9_]{1,32}',a.vida),'Strict PI05 diagnostic life only')
 need(re.fullmatch(r'PI05_[A-Z0-9_]{1,64}',a.tag),'Fresh explicit PI05 tag')
 need(a.izquierda==14 and a.derecha in(2,3,4),'R01 only public left14/right2,3,4; broader domain requires a new prospective protocol')
 need(not(S/'estado/ACTIVO.json').exists(),'No principal selection permitted in isolated system')
 out=P/'control'/(a.tag+'.json');need(not out.exists()and not(P/'ensayos'/(a.tag+'_FI.json')).exists(),'Used tag/request ID; never retry')
 p=read(PROTOCOL);need(p['status']=='PREREGISTERED_BEFORE_NATIVE'and p['runner_sha256']==sha(Path(__file__)),'Exact runner protocol must be frozen before Native')
 need(p['instrument_protocol_sha256']==sha(INSTRUMENT),'Instrument protocol differs from frozen runner protocol')
 instrument=read(INSTRUMENT);need(instrument['status']=='SEALED','Root must seal instrument before Native')
 for n,h in instrument['dependencies_sha256'].items():need(Path(n).name==n and sha(INSTRUMENT.with_name(n))==h,'Instrument dependency changed: '+n)
 cardpath=S/'estado/vidas'/a.vida/'VIDA.json';card=read(cardpath);need(card['physical']['N']==67 and card['physical']['tick']==817876,'R01 requires own full pre-FI prefixT817876')
 need(sha(S/card['snapshot'])==card['snapshot_sha256'],'Complete imported snapshot hash mismatch')
 budget=read(P/'REGISTRO_CAMPANA.json');need(datetime.datetime.now().astimezone()<datetime.datetime.fromisoformat(budget['science_cutoff_local']),'Scientific closure deadline reached')
 floor=closed_ticks();need(floor+198<=budget['budget']['Native_ticks_all_branches'],'Insufficient fixed all-branch Native budget')
 usage=frame_usage(S/'estado/observacion_pasiva');planned=[x for x in instrument['capture_offsets_q']if 817876<=817932+x<=818074];anchors=set(instrument['anchor_offsets_q'])&set(planned)
 if a.captura=='global':
  need(usage['anchors']+len(anchors)<=budget['budget']['full_global_anchors_max'],'Campaign full-anchor allowance exceeded')
  need(usage['delta_frames']+len(planned)-len(anchors)<=budget['budget']['one_tick_lossless_delta_frames_max'],'Campaign delta-frame allowance exceeded')
  need(len(planned)<=instrument['max_frames_per_trial'],'Per-trial capture frame allowance exceeded')
 request=literal(a.izquierda,a.derecha,a.captura)
 if a.dry_run:
  print(json.dumps({'mode':'READ_ONLY_PREFLIGHT_NO_OWNER','literal':request,'before_tick':817876,'planned_after_tick':818074,'planned_frames':len(planned)if a.captura=='global'else 0,'planned_anchors':len(anchors)if a.captura=='global'else 0,'capture_usage_before':usage,'Native_ticks':0,'owner_started':False},ensure_ascii=False,indent=2));return 0
 sys.path.insert(0,str(P/'codigo'));from servicio_ensayo_PI05 import Owner
 actual=None;summary=None;owner=None;error=None;closed=False;capture_verified=None;start_card=info(cardpath)
 try:
  with Owner(a.vida,a.tag)as owner:
   actual=owner.material(a.tag+'_FI',request,feedback='omit',allow_failure=True)
   need(isinstance(actual,dict)and isinstance(actual.get('result'),dict),'Material request did not complete; original uncertainty/failedreceipt preserved')
   summary=summarize(actual,a.izquierda,a.derecha)
   cap=summary['external_global_capture']
   if a.captura=='global':
    need(cap is not None,'Missing actual global capture summary');target=Path(cap['directory']).resolve(strict=True);allowed=(S/'estado/observacion_pasiva'/a.vida).resolve();need(target.is_relative_to(allowed),'Global output outside fixed diagnostic directory')
    index=target/'INDEX.json';need(sha(index)==cap['index_sha256'],'Actual capture index hash mismatch');idx=read(index);rows=idx['frames'];need(len(rows)==cap['captured_frames']and not cap['missing_planned_ticks'],'Global capture missing fixed ticks');need([r['tick']for r in rows]==[817932+x for x in planned],'Actual global capture ticks differ from frozen offsets')
    capture_verified={'directory':str(target),'index':info(index),'frames':len(rows),'anchors':sum(r['kind']=='anchor'for r in rows),'delta_frames':sum(r['kind']=='xor_uint64'for r in rows),'arrays_stored_outside_Native_metadata':True,'lossless_reconstruction':'Separate passive decoder must exhaust all frames; this runner checks index consistency and hashes only'}
   else:need(cap is None,'Normal/fragmented control unexpectedly stored global arrays')
   need(summary['before_tick']==817876 and summary['after_tick']==818074 and summary['new_Native_ticks']==198,'Actual horizon differs from fixed original198tick protocol')
   cal=summary['calendar'];expected={'query_tick':817932,'C_tick':817933,'S_tick':817935,'early_reader_tick':817936,'old_reader_tick':817938,'horizon_tick':818074};need(all(cal[k]==v for k,v in expected.items()),'Actual scheduler differs from preregistered original calendar')
   need(summary['Native_inputs']['unique_requested']==176,'Original Native dose differs; preserve future')
   owner.control('guardar')
 except Exception as exc:error={'type':type(exc).__name__,'message':str(exc),'no_retry':True}
 if owner is not None and owner.proc is not None:closed=bool(owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running'))
 try:after_usage=frame_usage(S/'estado/observacion_pasiva')
 except Exception as exc:
  after_usage={'unverified_error':type(exc).__name__+': '+str(exc)}
  if error is None:error={'type':'POST_CAPTURE_BUDGET_READ_ERROR','message':str(exc),'no_retry':True}
 actual_tick_delta=None
 if isinstance(actual,dict)and type(actual.get('before_tick'))is int and type(actual.get('after_tick'))is int:
  actual_tick_delta=actual['after_tick']-actual['before_tick']
 saved_after=read(cardpath);saved_tick_delta=saved_after['physical']['tick']-card['physical']['tick']if closed else None
 measured_ticks=saved_tick_delta if saved_tick_delta is not None else actual_tick_delta
 if closed and actual_tick_delta is not None and saved_tick_delta!=actual_tick_delta and error is None:error={'type':'SAVED_VS_PACKET_NATIVE_AGE_MISMATCH','message':'Saved Native age differs from material packet, preserve host/idle evidence without retry','no_retry':True}
 status='COMPLETED_FI_RECORDED'if closed and error is None and summary is not None else'STOPPED_PRESERVED'
 proof={'schema':'DEE.PI05.single_FI.actual.R01','status':status,'life_id':a.vida,'capture_condition':a.captura,'public_literal':request,'protocol':info(PROTOCOL),'instrument_protocol':info(INSTRUMENT),'imported_VIDA_before':start_card,'material_primary':str(P/'ensayos'/(a.tag+'_FI.json')),'actual':actual,'summary':summary,'capture_index_check':capture_verified,'capture_budget_before':usage,'capture_budget_after':after_usage,'budget_floor_before':floor,'budget_measured_after':closed_ticks(),'owner_closed_coherently':closed,'error':error,'new_Native_ticks':measured_ticks,'Native_tick_delta_from_actual_packet':actual_tick_delta,'Native_tick_delta_from_closed_saved_VIDA':saved_tick_delta,'last_saved_VIDA_after':info(cardpath),'host_reference_computed_only_after_actual_response':True,'expected_result_never_actor_input':True,'principal_modified':False,'new_observer_only_not_learned_recovery':True}
 with out.open('x',encoding='utf8')as h:json.dump(proof,h,ensure_ascii=False,indent=2)
 print(json.dumps({'proof':str(out),'status':status,'outcome':None if summary is None else summary['outcome'],'Native_ticks':proof['new_Native_ticks'],'owner_closed_coherently':closed,'error':error},ensure_ascii=False),flush=True)
 return 0 if status=='COMPLETED_FI_RECORDED'else 2
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--vida',required=True);ap.add_argument('--izquierda',type=int,required=True);ap.add_argument('--derecha',type=int,required=True);ap.add_argument('--captura',choices=('normal','global','fragmentar'),required=True);ap.add_argument('--tag',required=True);ap.add_argument('--dry-run',action='store_true');raise SystemExit(main(ap.parse_args()))
