"""Passive normal/global comparison of closed PI05 FI cases.
Reads frozen complete Native snapshots and recorded material primaries only.
No DEE import, writer, tick, query, reset or content repair.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];P4=P.parent/'PROGRESION_INTEGRADA_04';S=P/'estados/candidato/sistema'
def need(x,s):
 if not x:raise ValueError(s)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def info(p):
 p=Path(p).resolve(strict=True);b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def module(p,n):
 spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def load_case(path,mode,parser,org):
 before=info(path);j=read(path);need(j['status']=='COMPLETED_FI_RECORDED'and j['owner_closed_coherently']is True,'Actual coherently closed FI case required')
 need(j['capture_condition']==mode and j['new_Native_ticks']==198,'Case mode/age differs')
 actual=j['actual'];summary=j['summary'];need(actual['before_tick']==817876 and actual['after_tick']==818074,'Same exact prefix/horizon required')
 need(summary['Native_inputs']['unique_requested']==summary['Native_inputs']['applied']==176 and summary['Native_inputs']['rejected_or_other']==0,'Exact176applied comparison only; preserve rejected histories separately')
 primary=Path(j['material_primary']).resolve(strict=True);need(primary.is_relative_to(P/'ensayos'),'Only actual PI05 primary path')
 value=read(primary);need(value['status']=='completed'and json.loads(value['result'])==actual,'Primary wrapper differs from recorded actual result')
 cut=actual['committed_snapshot'];need(cut['life_id']==j['life_id'],'Native identity differs')
 v=parser.parse(S/cut['snapshot'],cut['snapshot_sha256']);need(v[0]['physical']=={k:cut['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')},'Snapshot physical bytes differ from primary')
 o,ops=org.parse(v[6]);legacy=summary['legacy_result_unchanged'];need(legacy==actual['result']['rows'][0]['legacy_result'],'Recorded legacy result was changed')
 trial=legacy['original_result']['native_trial'];q=legacy['query_tick'];frames={int(f['tick']):f['fields']for f in trial['frames']}
 data={'proof':before,'primary':info(primary),'life_id':j['life_id'],'mode':mode,'public_literal':j['public_literal'],'protocol':j['protocol'],'instrument_protocol':j['instrument_protocol'],'snapshot':v[0],'organizational':o,'Native_material_requests':actual['result']['rows'][0]['requests'],'calendar':summary['calendar'],'early_choice':summary['early_physical_choice'],'old_q6_choice':summary['old_q6_choice'],'early_observation':legacy['early_observation'],'C_at_q1':frames[q+1]['C'],'S_at_q3':frames[q+3]['S'],'legacy_frames':trial['frames'],'legacy_reader_q6':trial['reader'],'references_pre':trial['references_pre'],'references_after':trial['references_after'],'legacy_result':legacy,'external_capture_summary':summary['external_global_capture'],'import':info(S/'estado/servicios_persistentes'/j['life_id']/'IMPORTACION.json'),'closed_saved_VIDA':j['last_saved_VIDA_after']}
 # Do not silently treat a later exported/reopened card as the original saved card.
 card=Path(j['last_saved_VIDA_after']['path']);current=info(card)
 if current==j['last_saved_VIDA_after']:
  record=read(card);closed=parser.parse(S/record['snapshot'],record['snapshot_sha256']);data['closed_saved_snapshot']=closed[0];data['material_vs_closed_snapshot']={'RAW_exact':closed[7]==v[7],'clocks_exact':closed[8]==v[8],'interfaces_exact':closed[3]==v[3],'agenda_exact':closed[4]==v[4],'receipts_exact':closed[5]==v[5],'metadata_differences':parser.metamap(v[6],closed[6])}
 else:data['closed_saved_snapshot_not_reopened_by_checker']={'reason':'CurrentVIDAbyteschangedaftertheclosedcase; frozen material snapshot+ownerclosureproofretained, no inferred identity of later administrativestate','recorded':j['last_saved_VIDA_after'],'current_file':current}
 need(info(path)==before,'Case proof changed concurrently')
 return data,v,o,ops

def compare(a,b,parser):
 ad,av,ao,aops=a;bd,bv,bo,bops=b;rd=[];cd=[]
 for i,(x,y)in enumerate(zip(av[1],bv[1])):
  if x!=y:rd.append({'site':[i//4489,(i//67)%67,i%67],'a':parser.decode(x),'b':parser.decode(y)})
  if av[2][i]!=bv[2][i]:cd.append([i//4489,(i//67)%67,i%67])
 ra={r['id']:r for r in av[5]};rb={r['id']:r for r in bv[5]};receipt=[{'id':k,'a':ra.get(k),'b':rb.get(k)}for k in sorted(set(ra)|set(rb))if ra.get(k)!=rb.get(k)]
 prefix=0
 while prefix<min(len(aops),len(bops))and aops[prefix]==bops[prefix]:prefix+=1
 suffix=0
 while suffix<min(len(aops)-prefix,len(bops)-prefix)and aops[-1-suffix]==bops[-1-suffix]:suffix+=1
 fields=('paused','next_event_id','next_sequence','backend_enum','threads','phase')
 checks={'GLOBAL_RAW_exact':av[7]==bv[7],'GLOBAL_clocks_exact':av[8]==bv[8],'interfaces_exact':av[3]==bv[3],'agenda_exact':av[4]==bv[4],'all_Runtime_receipts_exact':av[5]==bv[5],'execution_header_exact':all(av[0][k]==bv[0][k]for k in fields),'176_material_requests_exact':ad['Native_material_requests']==bd['Native_material_requests'],'calendar_exact':ad['calendar']==bd['calendar'],'q4_choice_exact':ad['early_choice']==bd['early_choice'],'q6_choice_exact':ad['old_q6_choice']==bd['old_q6_choice'],'q4_observation_RAW_clock_exact':ad['early_observation']==bd['early_observation'],'C_q1_RAW_clock_exact':ad['C_at_q1']==bd['C_at_q1'],'S_q3_RAW_clock_exact':ad['S_at_q3']==bd['S_at_q3'],'legacy_frames_all_fields_exact':ad['legacy_frames']==bd['legacy_frames'],'legacy_q6_reader_all_fields_exact':ad['legacy_reader_q6']==bd['legacy_reader_q6'],'references_pre_exact':ad['references_pre']==bd['references_pre'],'references_after_exact':ad['references_after']==bd['references_after'],'legacy_result_exact':ad['legacy_result']==bd['legacy_result'],'organizational_all_sections_exact':all(ao['sections'][k]['sha256']==bo['sections'][k]['sha256']for k in ao['sections'])}
 metadata=parser.metamap(av[6],bv[6])
 for m in metadata:
  key=m['key']
  if key.startswith('DEE.Cognitive.System.1.1.PERSISTENT_SERVICE'):m['scope']='Managed transport/owner/request metadata. Exact changed fields retained; not a universal claim of causal irrelevance.'
  elif key in('DEE.Cognitive.System.1.1.life.v1','DEE.Cognitive.PI04.C2C.central_sensor.R01','DEE.Cognitive.PI04.C2C.coordination.R01'):m['scope']='Identity/progress-bearing namespace; inspect listed field differences, do not excuse acquired fields by key alone.'
  elif key.startswith('dee_thinking.organizational.v1.'):m['scope']='Decoded separately into recipe/protocol/edit/operation/decoder/trace sections; do not mask log differences.'
  else:m['scope']='No prior exemption; requires explanation if unequal.'
 return {'checks':checks,'RAW_different_sites':rd,'clock_difference_positions':cd,'Runtime_receipt_difference_count':len(receipt),'Runtime_receipt_differences':receipt,'execution_header':{k:{'a':av[0][k],'b':bv[0][k]}for k in fields},'metadata_exact':av[6]==bv[6],'metadata_differences':metadata,'organizational_sections':{k:{'a':ao['sections'][k],'b':bo['sections'][k],'equal':ao['sections'][k]['sha256']==bo['sections'][k]['sha256']}for k in ao['sections']},'external_operations':{'a_count':len(aops),'b_count':len(bops),'common_prefix':prefix,'common_suffix':suffix,'a_differing_tail':aops[prefix:len(aops)-suffix if suffix else len(aops)],'b_differing_tail':bops[prefix:len(bops)-suffix if suffix else len(bops)]},'all_relevant_measured_checks_equal':all(checks.values()),'full_operational_identity_NOT_claimed':True}

def main(args):
 need(not args.out.exists(),'Existing comparison preserved; no overwrite')
 parser=module(P/'codigo/contrastar_prefijos_C2C_PI05_pasivo.py','PI05_exact_snapshot_reader');org=module(P/'codigo/analizar_organizational_prefijos_PI05_pasivo.py','PI05_exact_organizational_reader')
 normal=load_case(args.normal,'normal',parser,org);glob=load_case(args.global_case,'global',parser,org);need(normal[0]['public_literal']|{'captura':'global'}==glob[0]['public_literal'],'Different public FI operands/mode envelope')
 c=compare(normal,glob,parser);data={'schema':'DEE.PI05.FI.normal_global.passive_comparison.v1','inspection_local':datetime.datetime.now().astimezone().isoformat(),'mode':'RECORDED_CLOSED_NATIVE_RESULTS_AND_FULL_SNAPSHOTS','new_Native_ticks':0,'DEE_imports':0,'source_files_modified':False,'normal':normal[0],'global':glob[0],'comparison':c,'scope':'Equality/non-equality is reported at the actual final global state and all existing legacy observation/readout points. Normal has no full globaltrajectoryrecord between those points; do not infer universalpassivity or measuredidentityofeverytick.','global_frame_integrity':'Lossless anchor/delta reconstruction belongs to separate F1 verification; this checker does not substitute finalRawhashesforverifyingrecordedframes.','no_causal_field_excluded':'All RAW/clocks,channels,agenda,receipts,executionheader,metadataentries and all organizationalbinarysections compared. Changed identity/transport/log fields are listed, not called equal.','interpretation':'PASIVIDAD_ACOTADA_EN_COMPONENTES_COMPARADOS'if c['all_relevant_measured_checks_equal']else'DIFERENCIAS_OBSERVADAS_REQUIEREN_EXPLICACION'}
 # Existing old negative is a recorded reference, not another fresh execution.
 oldp=P4/'ensayos/PI04_MAIN_PANEL12_OP2_FIplus.json'
 if oldp.exists():
  old=read(oldp);oldactual=json.loads(old['result']);cut=oldactual['committed_snapshot'];ov=parser.parse(P4/'estados/candidato_R02/sistema'/cut['snapshot'],cut['snapshot_sha256']);oo,oops=org.parse(ov[6]);legacy=oldactual['result']['rows'][0];trial=legacy['original_result']['native_trial'];q=legacy['query_tick'];frames={int(f['tick']):f['fields']for f in trial['frames']};od={'Native_material_requests':legacy['all_material_receipts'],'calendar':normal[0]['calendar'],'early_choice':legacy['early_physical_choice'],'old_q6_choice':legacy['old_q6_choice'],'early_observation':legacy['early_observation'],'C_at_q1':frames[q+1]['C'],'S_at_q3':frames[q+3]['S'],'legacy_frames':trial['frames'],'legacy_reader_q6':trial['reader'],'references_pre':trial['references_pre'],'references_after':trial['references_after'],'legacy_result':legacy}
  data['old_PI04_negative_reference']={'primary':info(oldp),'Native_snapshot':ov[0],'comparison_normal_vs_old':compare(normal,(od,ov,oo,oops),parser),'calendar_scope':'Oldprimaryhasquery/readticksnotnewinstrumentcalendarwrapper; equalityofcalendardictionaryisnotseparatelymeasuredhere. The actual oldq4/q6/C/S ticks are compared in frames.'}
 # Compare the full closed checkpoints too, using their frozen recorded paths.
 if all('closed_saved_snapshot'in arm[0]for arm in(normal,glob)):
  closed=[]
  for arm in(normal,glob):
   src=arm[0]['closed_saved_snapshot']['snapshot'];vv=parser.parse(Path(src['path']),src['sha256']);oo,ops=org.parse(vv[6]);closed.append((arm[0],vv,oo,ops))
  data['closed_checkpoint_comparison']=compare(closed[0],closed[1],parser)
 # The disabled R04 bridge records each advance interval, including observer
 # segmentation. These fields remain reported, not normalized away.
 key='DEE.Cognitive.PI02.continuous_workbench.R04'
 states={name:json.loads(arm[1][6][key])for name,arm in [('normal',normal),('global',glob)]}
 diff=parser.jsondiff(states['normal'],states['global'])
 source=S/'capacidades/pi02_habitat_R04.py';text=source.read_text(encoding='utf-8-sig');matches=[{'line':i+1,'text':line.strip()}for i,line in enumerate(text.splitlines())if'paused_intervals'in line]
 confined=all(x['pointer'].startswith('/paused_intervals/')for x in diff)
 data['metadata_explanation']={'R04':{'source':info(source),'exact_localizers':matches,'enabled':{k:v['enabled']for k,v in states.items()},'active':{k:v['active']for k,v in states.items()},'uncertain':{k:v['uncertain']for k,v in states.items()},'last_tick':{k:v['last_tick']for k,v in states.items()},'only_paused_interval_fields_differ':confined,'changed_scalar_fields':len(diff),'explanation':'When enabled=False, advance calls base.run_until(target), setslast_tick and appends the disabled-bridge interval, retaining only last16. Global segmentation therefore changes this bookkeeping history. The exactdifferentfields remain in the full comparison. The installed disabled branch does not perform R04callbacks or send materialevents. This is an observed/local installed-code explanation, not universalmetadatairrelevance or totalstateidentity.'},'managed_service':'Recorded request IDs,payload/result hashes,owner PID and checkpoints differ by condition/identity and are explicitlylisted. No suchfield is silently declared equal.','life':'World/life IDs and previouscheckpointsha differ. Raw physical content is not inferred from thoseIDs.'}
 args.out.parent.mkdir(exist_ok=True,parents=True)
 with args.out.open('x',encoding='utf8')as f:json.dump(data,f,ensure_ascii=False,indent=2)
 print(json.dumps({'output':info(args.out),'interpretation':data['interpretation'],'checks':c['checks'],'metadata_differences':len(c['metadata_differences']),'Runtime_receipt_differences':c['Runtime_receipt_difference_count']},ensure_ascii=False,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--normal',type=Path,default=P/'control/PI05_REAL_FI_NORMAL_R01.json');ap.add_argument('--global-case',type=Path,default=P/'control/PI05_REAL_FI_GLOBAL_R01.json');ap.add_argument('--out',type=Path,default=P/'control/PASIVIDAD_CAPTURA_GLOBAL_FI_PI05_R01.json');main(ap.parse_args())
