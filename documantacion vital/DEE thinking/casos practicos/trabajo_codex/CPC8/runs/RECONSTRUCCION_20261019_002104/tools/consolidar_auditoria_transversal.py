"""Read-only-source cumulative evidence overlay. No native import or trajectory.

The original47rows and original packages remain untouched. Derived documents
link exact primaries and explicitly distinguish whole historical domains from
bounded operations adapted into a different new E1 preparation.
"""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter,defaultdict
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
BASE=next(x for x in ROOT.parents if x.name=='documantacion vital')
OLD='65164c939621464c7d4faa800240bb1c2e25538ba9d878a65863016f57387c00'
WHEEL='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
PYD='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
KERNEL='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def relative(p):return Path(p).relative_to(ROOT).as_posix()
def proof(p,scope):
 p=ROOT/p;return{'path':relative(p),'sha256':sha(p),'bytes':p.stat().st_size,'scope':scope}
def measurement(name):
 p=ROOT/'resultados/integracion'/name/'MEASUREMENTS.json'
 if not p.exists():return None
 d=load(p)
 return d if d.get('status')=='MEASURED'else None
def group(identifier):
 if identifier.startswith('CP01'):return'CPC1'
 if identifier.startswith('CP02'):return'CPC2'
 if identifier.startswith(('CPC3','SEM01')):return'CPC3_SEM01'
 if identifier.startswith('CPC4'):return'CPC4'
 if identifier.startswith('CPC5'):return'CPC5'
 if identifier.startswith('CPC6'):return'CPC6'
 if identifier.startswith('CPC7'):return'CPC7'
 if identifier.startswith('PRODUCT'):return'PRODUCTO'
 return'CORE_INGENIERIAS_PROCESOS_MBP_FISICA'

def main():
 generated=datetime.now(timezone.utc).isoformat();original=ROOT/'genealogia/MATRIZ_ANTECEDENTES_47.json';originalsha=sha(original);matrix=load(original)
 assert len(matrix['capabilities'])==47 and len({c['id']for c in matrix['capabilities']})==47
 previous=ROOT.parent/'historico'/('CPC8_ORGANIZACION_COGNITIVA_NATIVA_APRENDIZAJE65_RESULTADOS__'+OLD+'.zip')
 assert sha(previous)==OLD
 priorrefs=[];prior_summaries={}
 selected=('VIDA_PRINCIPAL.json','CONSULTAS_Y_ACCESO.json','COMPOSICION_FUNCIONAL.json','APRENDIZAJE_ACUMULATIVO.json')
 with zipfile.ZipFile(previous)as z:
  for name in selected:
   member='CPC8/revision/'+name;data=z.read(member);target=ROOT/'genealogia/primer_cpc8/revision_historica'/name;target.parent.mkdir(parents=True,exist_ok=True)
   if target.exists():assert target.read_bytes()==data
   else:
    with target.open('xb')as f:f.write(data)
   prior_summaries[name]=json.loads(data);priorrefs.append({'archive_sha256':OLD,'member':member,'member_sha256':hashlib.sha256(data).hexdigest(),'copy':relative(target),'scope':'ANTECEDENTE_DOCUMENTAL; no reejecutado completo ni memoria operativa del participante nuevo'})
  # Relocate only the derived overlay's documentary references. The sealed
  # original historical summary remains byte-exact in revision_historica/.
  prior_main=json.loads(json.dumps(prior_summaries['VIDA_PRINCIPAL.json']))
  for entry in prior_main['evidence']:
   old_relative=entry['path'];member='CPC8/'+old_relative
   if old_relative.startswith('resultados/semantica/SOC_I21_'):
    target=ROOT/'genealogia/primer_cpc8/SOC_I21/MEASUREMENTS.json'
   else:
    data=z.read(member);target=ROOT/'genealogia/primer_cpc8/revision_historica/evidencia'/Path(old_relative).name;target.parent.mkdir(parents=True,exist_ok=True)
    assert hashlib.sha256(data).hexdigest()==entry['sha256']
    if target.exists():assert target.read_bytes()==data
    else:
     with target.open('xb')as f:f.write(data)
   assert sha(target)==entry['sha256']
   entry.update(path=relative(target),historical_relative_path=old_relative,historical_member=member,archive_sha256=OLD,reference_scope='Passive original evidence, relocated in this derived overlay only; not a new execution')
  prior_main['documentary_path_scope']='Evidence paths are relocated byte-exact selected copies in the new overlay. Original summary and old event strings remain historical; the current participant does not execute its old events or use them as memory.'
 parity=load(ROOT/'resultados/cpc7_reproduccion/SUMMARY.json');regression=load(ROOT/'resultados/regresion_producto45/RESULT.json');soc=load(ROOT/'resultados/rescate_SOC21/MEASUREMENTS.json');l15=load(ROOT/'revision/L15_ACCESO_VS_INTERFERENCIA.json')
 inventory=load(ROOT/'genealogia/INVENTARIO_RECONSTRUCCION.json');directed=load(ROOT/'genealogia/INVENTARIO_LECTURA_DIRIGIDA.json');conv=load(ROOT/'genealogia/CONVERSACIONES_ACCESIBLES.json');overlay=load(ROOT/'genealogia/MATRIZ_RESCATE_Y_REPRODUCCION.json')
 install=load(ROOT/'runtime/INSTALL_IDENTITY.json');reference=load(ROOT/'runtime/REFERENCE_IDENTITY_HEREDADA.json');kernel=ROOT/'genealogia/product45/kernel_v27.cpp';wheel=ROOT/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
 identity={'schema':'CPC8R.identity.audit.v1','generated_utc':generated,'library_version':'4.5.0','kernel_version':27,
  'wheel':{'path':relative(wheel),'expected_sha256':WHEEL,'actual_sha256':sha(wheel)},
  'kernel_source':{'path':relative(kernel),'original_member':'source/src/kernel_v27.cpp','expected_sha256':KERNEL,'actual_sha256':sha(kernel)},
  'native_extension':{'recorded_installed_path':install['native'],'expected_sha256':PYD,'recorded_sha256':install['native_sha256'],'current_sha256':sha(Path(install['native']))if Path(install['native']).exists()else None},
  'official_product_archive':{'original_path':reference['archive'],'expected_sha256':reference['archive_sha256'],'actual_sha256':sha(reference['archive'])if Path(reference['archive']).exists()else None,'copied_wholesale_into_new_delivery':False},
  'installation_observation':proof('runtime/INSTALL_IDENTITY.json','Isolated site-packages, CPython3.13x64, save/load, no hidden cognitive preparation for direct Runtime'),
  'current_regression':proof('resultados/regresion_producto45/RESULT.json','82actual inherited Python tests; not a new C++build or all original campaigns'),
  'native_cpp_scope':'C++consumer/build reports are historical product4.5validation, not recompiled or reexecuted by this reconstruction.',
  'checks':{'wheel_identity':sha(wheel)==WHEEL,'kernel_source_identity':sha(kernel)==KERNEL,'installed_extension_identity':Path(install['native']).exists()and sha(Path(install['native']))==PYD,
   'product_archive_identity':Path(reference['archive']).exists()and sha(reference['archive'])==reference['archive_sha256'],'product_regression82':regression['tests']==82 and regression['successful']},
  'operations':'No recompilation, product edit, kernel modification or legacy binary replacement. New research preparations/protocols use the frozen official installed product.'}
 put(ROOT/'revision/IDENTIDAD_KERNEL_Y_PRODUCTO.json',identity)
 cpc7={'schema':'CPC8R.CPC7.base.audit.v1','generated_utc':generated,'source':inventory['CPC7'],'actual_reproduction':proof('resultados/cpc7_reproduccion/SUMMARY.json','Four original configurations0→472, source identity/storage adaptation only'),
  'cases':parity['cases'],'criterion':'Complete RAW/clocks/tick and receipt entries, plus captured338/472 panels; positive full0/338/472 physical pair equality. File/container metadata are compared separately.',
  'counts':{'reference_preparations':4,'physical_checkpoints_positive':3,'lower_panel_requests':14,'unchanged_old_relations_after_one_revision':13},
  'scope_correction':'14versus6 is the number of covered responses under guard placement, not the number of guards. Fourcases do not reproduce every CPC7 scientific branch. M1 is replayed; M2 remains historical.',
  'operative_command':'python -I -B base_validada/reproducir_cpc7.py --out NUEVA_SALIDA','external_original_archive_needed_for_command':False,
  'technical_status':parity['status'],'new_E1_scope':'CPC7 U0 is an antecedent, not silently reused as a trained new individual. New E1 has its own postT0 histories and tests.'}
 put(ROOT/'revision/CPC7_BASE_OPERATIVA.json',cpc7)
 rescue={'schema':'CPC8R.prior.positive.rescue.v1','generated_utc':generated,'protected_archive_sha256':OLD,'protection':proof('genealogia/PROTECCION_ENTREGA_ANTERIOR.json','Byte-exact backup and CRC; historical ZIP is outside the new package'),
  'historical_small_summaries':priorrefs,'prior_main':prior_main,
  'historical_denominators':[{'value':65,'meaning':'Opaque correspondence interfaces in the N131capacity apparatus, not65NSMmeanings'},{'value':63,'of':65,'meaning':'SOC_I21 directly covered old interfaces after integration; L15/L17 original ports unavailable/reorganized'},{'value':63,'of':63,'meaning':'Previously available old relations reported retained1051 in oldcontinuation; not reexecuted now'},{'value':13,'of':13,'meaning':'Unchanged lower-bank relations in CPC7 after revising one of14; not comparable to65bodycapacity by itself'}],
  'replayed_interval':{'primary':proof('resultados/rescate_SOC21/MEASUREMENTS.json','Complete saved state138→166; native pedagogical encounter140, receiver157 and consequence166'),
   'configuration':soc['config'],'preparations':0,'normal_continuations':1,'diagnostic_forks':2,'actual_receiver157':soc['observed_receiver157'],
   'reference166':soc['reference166'],'checks':{'intact_exact_full_physical_equal':soc['intact_exact_full_physical_equal'],'sham_exact_full_physical_equal':soc['sham_exact_full_physical_equal'],'parent_unchanged':soc['parent_unchanged']},
   'command':'python -I -B tools/rescatar_soc21.py --out NUEVA_SALIDA','dependencies_included':True,
   'not_replayed':'Prior acquisition0→138, later33newacquisitions, revisionL01, laterRIGHT andoldsemanticcases remain historical. Replay is not a newE1integration.'},
  'L15_access_diagnostic':{'primary':proof('revision/L15_ACCESO_VS_INTERFERENCIA.json','Six explicit diagnostic continuations of inheritedN131state, not the newE1'),
   'observed':'Learned16 andextraneous7 contribute23withnewdirection79. Cutting7preserves16initially but does notrestoreoriginal134access. A declared latealternativephysicalreader9 produces32@82; cutting learned16 leaves16=7+9. No unobserved83→130ancestry is invented.',
   'counts':l15['counts'],'command':'python -I -B src/diagnostico_l15_causal.py --out NUEVA_SALIDA','automatic_recovery_claim':False},
  'comparators':'The old B1/B2benchmark remains a historical reference only; no B1/B2model or answers participate in the newE1.',
  'positive_interpretation':'The protected old cut retains substantive cumulative acquisition and physical communication evidence. New late cuts distinguish access reorganization from global forgetting; none are promoted into a new mind merely by preserving a source.'}
 if(ROOT/'revision/REGULACION_POR_CONSECUENCIA_ANTECEDENTE.json').exists():
  rescue['native_consequence_policy_reference']=proof('revision/REGULACION_POR_CONSECUENCIA_ANTECEDENTE.json','Six exact historicalV2trajectories on4.5 plusfourlateactualreturncut/shamforks; finitepreparedR14stateupdate, notnewE1orlearningageneralstrategy')
 put(ROOT/'revision/CPC8_ANTERIOR_RESCATE_POSITIVO.json',rescue)
 # Reconcile copied/passive historical member identities without reinterpreting
 # a source hash as a new replication or a mathematical theorem as an apparatus.
 members={}
 for row in matrix['capabilities']:
  for source in row['historical_source_identities']:
   key=(source['archive_sha256'],source['member']);existing=members.get(key)
   if existing is None:
    entry=dict(source);entry['referenced_by']=[];target=ROOT/source['copied_as']if source.get('copied_as')else None
    entry['included_copy_verified_now']=bool(target and target.exists()and sha(target)==source['member_sha256']);members[key]=entry
   members[key]['referenced_by'].append(row['id'])
 source_inventory={'schema':'CPC8R.source.inventory.overlay.v1','generated_utc':generated,'historical_matrix':proof('genealogia/MATRIZ_ANTECEDENTES_47.json','Original47rows unchanged'),
  'historical_source_members':list(members.values()),'current_directed_corpus':directed,'original_archive_inventory':inventory['corpus_archives'],
  'conversation_access':conv,'documents45':{'state':'DESCRITOS_EN_CONVERSACION_NO_BYTES_ACCESIBLES_LOCALMENTE','complete_document_reading':False,'exact_links_and_ids':conv['documents45']},
  'read_scope':'35archiveinventories and selected members,4threads/16recentturns. Not a complete corpus/conversation/Wordreading. Exact partialtextwindows and unexpandedreferences remain in the linked inventories.',
  'counts':{'historical_capability_rows':47,'unique_historical_member_references':len(members),'verified_included_historical_members':sum(x['included_copy_verified_now']for x in members.values()),
   'archives_inventoried':directed['archives_inventoried'],'selected_corpus_members':directed['selected_members'],'recent_threads':conv['total_threads'],'recent_turns':conv['turns_returned']},
  'modification_policy':'Original packages are read-only sources. Byte-exact passive extracts, overlays and current results live only in this new work area. No historical report/manifests are rewritten.'}
 put(ROOT/'revision/INVENTARIO_FUENTES.json',source_inventory)
 # These operation-level links do not claim the entire historical domain has
 # been incorporated. The E1 evidence itself is new and must be measured.
 current=measurement('LCE_P01_FRESH_LONGITUDINAL');lce_ok=bool(current and current['last_complete_tick']==549 and not current['host_RAW_clock_edits_on_MAIN'])
 p_lce='resultados/integracion/LCE_P01_FRESH_LONGITUDINAL/MEASUREMENTS.json'
 lce_proofs=[proof(p_lce,'Fresh N67 MAIN0→549: order/contact/opaque names, nativeA→Bcontent, acquired quantity reference and later update; not a65bankworld')]if lce_ok else[]
 if lce_ok:
  for name,scope in(('LCE_C01_NO_ADDITION','Omit additive new experience withsameotherinputs'),('LCE_C02_UNPAIRED_ADDITION','Desynchronize paired addition'),('LCE_C03_SOCIAL_NAME_UNPAIRED','Unpaired socialnameexperience'),('LCE_C04_JOINT_NAME_UNPAIRED','Unpaired jointnameexperience'),('LCE_R101_BA_CONTACT','Wholehistoryreservedorder'),('LCE_R102_AB_FREE','Wholehistoryreservedcontactcontext'),('LCE_R103_BA_FREE','Wholehistoryreservedcombination')):
   if measurement(name):lce_proofs.append(proof('resultados/integracion/'+name+'/MEASUREMENTS.json',scope))
 integrated_operations={
  'CP01_C01':'Finite two-event temporal order is adapted into a freshN67body and later named/used jointly; not the originalN47case or unrestrictedsequencegrammar.',
  'CP01_C06':'Prepared native actor/contact consequence is experienced and laterused; not the entire originalmulti-episodefeedbackprotocol.',
  'CPC3_MAIN_AND_COMPARISON':'CurrentMAINobservations and acquired-reference comparison are available in new finite directional/quantityapparatuses, not the originalN47marker84.',
  'SEM01':'Paired opaqueforms and cue-only laterresponse are adapted for order/contact/social/jointfunctions; not an exact17/45historicalreplay.',
  'CPC4_AB':'Aphysicalcomparisonproduct reachesBand teachesB; latercue-onlyBresponse persists. The four-partyadaptiveCPC4network is not inherited.',
  'CPC5_COMPOUND':'Acquiredorder/contact physically meet in a common-usevector; not a replay of all originalmobilecascade depths.',
  'CPC5_LONGITUDINAL65':'Pattern of retaining earlierfunctionalaccess while acquiring/updatingotherrelations is adapted, but the newMAINdoesnotcontain65banks.',
  'CPC5_ORDER_AND_DIALOGUE':'Nativeorder-sensitivecommonuse and finitecommunication are adapted; no allpopulation/role-swap protocol is asserted.',
  'CPC6_INTEGRATED':'NewsingleN67MAINcouplesfiniteorder,contact,comparison,communicationandnames; the originalforecast apparatus is not inherited.',
  'CPC6_TWO_FORMS':'Earlieropaqueform can be queried after laterexperience in the newMAIN; differentphysicalgeometryandprotocol from historicalF1/F2.',
  'ING02_RELATIVE':'FreshsupportedA/Brelativeorderbody participatesinnewMAIN; not every temporalbank,phaseorrepresentation fromIngenieria02.',
  'CPC7_U0_CONTINUITY':'The continuity pattern is revalidated in a newgeometry, not loadedasatrainedU0 and not the whole16-formM1apparatus.',
  'CPC7_DIRECTIONAL_COMPOSITION_AND_POST_NAME':'Learnedorderandcontact feeda nativecommonoperation and lateropaquecue; fixedroles,finitewindows,notgeneralgrammar.'}
 iue_name='IUE_P01_RETURN_USED_PLUS';iue=measurement(iue_name);iue_ok=bool(iue and iue.get('last_complete_tick')==549 and not iue['host_RAW_clock_edits_on_MAIN'])
 iue_proofs=[];iue_profile=None
 if iue_ok:
  iuepath='resultados/integracion/'+iue_name+'/MEASUREMENTS.json';expected_iue_sha='c932e8a2523f8fae8e47cd5003a9bb8c0ac70485de6ee65b20d0f004ac053951';expected_source_sha='6078b7c0baeb647a842c14f017b9056ae1887772374438144f852168de324138'
  assert sha(ROOT/iuepath)==expected_iue_sha
  assert sha(ROOT/'src/integracion/initiative_use_e1.py')==expected_source_sha
  iue_proofs=[proof(iuepath,'Newfresh IUEprofile, not a retrospective change to LCE: acquiredquantitycomparison triggersnativequestion, sourcecontent and physicalreturnuse89; old/newE1functions continue549')]
  related=[]
  for name in('IUE_H01_RETURN_USED_MINUS','IUE_C01_NO_QUALIFIED_QUESTION','IUE_C02_SOURCE_UNPAIRED','IUE_R101_NEW_HISTORY','IUE_F11_RETURN_CUT','IUE_F12_RETURN_SHAM','IUE_T11_RESTORE_PLUS_NEW_QUERY','IUE_T12_RESTORE_MINUS_NEW_QUERY'):
   d=measurement(name)
   if d:
    rp='resultados/integracion/'+name+'/MEASUREMENTS.json';iue_proofs.append(proof(rp,'Current completed nativecontrol/reserve or explicitcausal/technicalcontinuation; distinctcounts retained'))
    used=[{'tick':o['tick'],'physical':rx['contact']}for o in d.get('return_use_observations',[])if o['tick']==89 for rx in o['receivers']if rx['contact']['active']and rx['contact']['direction']==[0,0,-1]and rx['contact']['s_reg']>13]
    last=d.get('frames',[])[-1]if d.get('frames')else None
    related.append({'case_id':name,'primary':rp,'primary_sha256':sha(ROOT/rp),'status':d['status'],'preparations':d['preparations'],'continuations':d['continuations'],'diagnostic_forks':d['diagnostic_forks'],
     'native_return_use89':used,'baseline_comparison549':d.get('baseline_comparison549'),'parent_file_unchanged':d.get('parent_file_unchanged'),'unmodified_parent_physical_equal':d.get('unmodified_parent_physical_equal'),
     'final_tick':last['tick']if last else None,'new_requests':d.get('new_requests'),
     'word616_all_fixed_ports':{k:v['delivery_site']for k,v in last['joint'].items()}if last and last['tick']==616 else None})
  iue_profile={'profile':'IUE_NATIVE_RETURN_USE_E1','not_a_retcon_of':'LCE_P01_FRESH_LONGITUDINAL','source':{'path':'src/integracion/initiative_use_e1.py','sha256':expected_source_sha},
   'primary':iue_proofs[0],'same_world_per_trajectory':True,'fresh_T0':True,'N':67,'horizon':549,'receipt_statuses':iue['receipt_statuses'],
   'finite_operation':'Native+Xquantitycomparison70 meetsfixedtap72, askslearnedsource77, native return30at86 enters fixedreceiver13and produces43at89/emits90. Opposite acquiredsourcechanges recipient with equalpayload, while noqualifiedquestion/unpairedsource remove43.',
   'prepared_vs_acquired':'Reference/sourcecontent acquired afterT0; positive-Xrequestpolicy,geometry,allcandidate supplies/recipients and readwindows prepared. No host read/decide/write callback.',
   'preserved':{'oldword549_allports':{k:v['delivery_site']for k,v in iue['frames'][-1]['joint'].items()},'late_new_contact':'Samefreshprofile has newcontact340 and ownlaterqueries411/478; originalcontact/order/MODE/quantity readouts retained undertheirindividualcriteria.'},
   'related_completed_cases':related,'proofs':iue_proofs,'inference_limit':'This profile addsoneboundedoperation in oneexistingmodel. It doesnotintegrateall47historicaldomains or the separatefeedbackF3regulationapparatus.'}
 mcts_primary=ROOT/'resultados/transferencia_magnitud/MCTS_P01_SOURCE31/MEASUREMENTS.json';mcts_audit=ROOT/'revision/TRANSFERENCIA_MAGNITUD.json';mcts_ok=False;mcts_proofs=[]
 if mcts_primary.exists()and mcts_audit.exists():
  mcts=load(mcts_primary);mcts_ok=mcts.get('status')=='MEASURED'and mcts.get('last_complete_tick')==616 and all(x['qualified']for x in mcts.get('magnitude_readings',[]))and len(mcts.get('magnitude_readings',[]))==3
  if mcts_ok:
   assert sha(ROOT/'src/transferencia_magnitud/cts_integrado.py')=='20865f8848441846a46362a081db0438ea89642798fcaf0fda37cc52a877c504'
   assert sha(mcts_primary)=='10bde5693986bf3511a4117a10d80ea9628b0c276302ae47ca1519b19d185a53'
   mcts_proofs=[proof(relative(mcts_primary),'FreshMCTS0→616: independently acquiredmagnitude36travelsnativelytorecipientB, usedagainst23/50/36; previousCTSfunctionsretainlocalreadouts'),proof('revision/TRANSFERENCIA_MAGNITUD.json','12primarycontainers=10preparations+fourdiagnosticforks+tworestoredcontinuations nestedintwoaggregates;16trajectoriesnot12independentreplicas')]
 inherited={x['id']:x for x in overlay['capabilities']};caprows=[]
 for c in matrix['capabilities']:
  old=inherited[c['id']];states=dict(old['states']);states.pop('integrada_en_MAIN',None);states['integrada_en_MAIN_con_limites']=False;states['todo_dominio_historico_integrado']=False;states['referencia_documental_no_replicas']=True
  newproofs=list(old['proofs_in_this_reconstruction']);adaptation=None
  if lce_ok and c['id']in integrated_operations:
   states.update(adaptada=True,integrada_en_MAIN_con_limites=True);adaptation=integrated_operations[c['id']];newproofs+=lce_proofs
  elif iue_ok and c['id']=='CPC7_PREPARED_DISCREPANCY_REQUEST':
   states.update(adaptada=True,integrada_en_MAIN_con_limites=True);adaptation='New IUEprofile: acquiredquantityreferenceconditionsafixednativequestion, anotheracquiredsourceanswersphysically, itsreturnisused89. This isnotallCPC7originalrequest/absencepolicies andnotutilitytrainedselection.';newproofs+=iue_proofs
  elif mcts_ok and c['id']=='CP01_C05':
   states.update(adaptada=True,integrada_en_MAIN_con_limites=True);adaptation='NewfreshMCTSprofile: onlysourceAreceivesactualcue5+value31; native36isreroutedbyzero-loadcontacts70/80intorecipientreference, thenused147/214/281witholdCTSfunctionsavailablethrough616. NotoriginalCP01recipe,notsnapshotcopy,norarbitrarybodilyreinstantiation.';newproofs+=mcts_proofs
  elif c['id']in('CP01_C03','CP01_C07','CPC6_RETENTION_CAUSAL','CORE16_OBSERVER_INFORMATION'):
   states['adaptada']=True;adaptation='Externalaudittool: preserved fullstate, latephysicalprobe and selectiveRAW/clocks-preservingforks distinguishaccess/memory/context. Not spontaneousE1introspection and not originalCORE16domainreproduction.';newproofs.append(proof('revision/L15_ACCESO_VS_INTERFERENCIA.json','Adapted external causaldiagnostic on inheritedworld'))
  item={'id':c['id'],'group':group(c['id']),'mechanism_historical':c['mechanism'],'domain_historical':c['domain'],'controls_historical':c['controls'],'limits_historical':c['limits'],
   'states':states,'source_member_keys':[{'archive_sha256':s['archive_sha256'],'member':s['member'],'member_sha256':s['member_sha256'],'included_copy':s.get('copied_as')}for s in c['historical_source_identities']],
   'historical_original_row':'genealogia/MATRIZ_ANTECEDENTES_47.json#/capabilities/'+str(matrix['capabilities'].index(c)),
   'new_operation_with_limits':adaptation,'proofs_in_this_reconstruction':newproofs,'exact_historical_reproduction_command':old['autocontained_reproduction_command'],
   'new_E1_reproduction_command':'python -I -B src/integracion/run_longitudinal_e1.py --config configuraciones/integracion/LONGITUDINAL_E1_CONFIRMATORY_FROZEN.json --case-id LCE_P01_FRESH_LONGITUDINAL --out NUEVA_SALIDA'if lce_ok and c['id']in integrated_operations else None,
   'scope_rule':'A family-leveladaptation/suboperationisnotwholehistoricaldomainintegration. Relatedclaims shareevidence andmustnotbecountedasindependentreplications.',
   'pending':'Preservedhistoricalsource; no newexactreproductionorE1integration claimed beyondtheexplicitoperation/proofabove.'}
  if iue_ok and c['id']=='CPC7_PREPARED_DISCREPANCY_REQUEST':item['new_E1_reproduction_command']='python -I -B src/integracion/run_initiative_use_e1.py --config configuraciones/integracion/INITIATIVE_USE_E1_FROZEN.json --case-id IUE_P01_RETURN_USED_PLUS --out NUEVA_SALIDA'
  if mcts_ok and c['id']=='CP01_C05':item['new_E1_reproduction_command']='python -I -B src/transferencia_magnitud/run_cts.py --case MCTS_P01_SOURCE31 --out NUEVA_SALIDA'
  if mcts_ok and c['id']in('CPC4_AB','CPC5_COMPOUND','CPC5_LONGITUDINAL65'):item['additional_distinct_MCTS_profile']=mcts_proofs
  if c['id']in('CPC3_POLICY','ING01_R04_R14')and(ROOT/'revision/REGULACION_POR_CONSECUENCIA_EN_MCTS.json').exists():
   item['related_auxiliary_coexistence_CMCTS']=proof('revision/REGULACION_POR_CONSECUENCIA_EN_MCTS.json','SeparatefreshCMCTS0→616, finitepreparedconsequencepolicy withnohostcomponentinputsafterT0. Twohistories/fourlateforks; oldfunctionalpanelretained, actualtransientinteraction73preserved. NotdefaultMCTSapp, nolearningageneralutilityrule.')
   item['states']['adaptada']=True;item['states']['integrada_en_candidato_auxiliar_con_limites']=True
  if c['id']in('ING01_R04_R14','CPC4_REGULATION_ABCD')and(ROOT/'revision/REGULACION_R0_R1_R2.json').exists():
   item['related_but_not_integrated_regulation']=proof('revision/REGULACION_R0_R1_R2.json','Separatecurrentcohorts: prepared/acquiredpulse/nativefeedback/distinctlongitudinaladverse; not4partyR2strategy or wholeR14domain')
   if(ROOT/'revision/REGULACION_POR_CONSECUENCIA_ANTECEDENTE.json').exists():item['historical_finite_consequence_policy_replay']=proof('revision/REGULACION_POR_CONSECUENCIA_ANTECEDENTE.json','ExactV2contact2→return4→comparison5→policy9→interception12→delivery15; sixreferences/fourforks, nohostinputsafterT0, notcurrentE1')
   if(ROOT/'revision/REGULACION_E1_FINITA.json').exists():item['distinct_finite_E1_regulation_profile']=proof('revision/REGULACION_E1_FINITA.json','SeparatefreshE1profile: acquireddirectionandfourdeclaredexternalmaintenanceexperiences; nottheIUEquestionprofileorR2generalstrategy')
  caprows.append(item)
 assert sha(original)==originalsha
 counts={'rows':len(caprows),'historical_reference_rows':47,'exact_or_partial_current_reproductions':sum(r['states']['reproducida_en_reconstruccion']or r['states']['reproducida_parcialmente']for r in caprows),
  'bounded_MAIN_operation_links':sum(r['states']['integrada_en_MAIN_con_limites']for r in caprows),'whole_historical_domains_integrated':0}
 put(ROOT/'revision/MATRIZ_CAPACIDADES_ACUMULADAS.json',{'schema':'CPC8R.capabilities.overlay.v1','generated_utc':generated,'original47_byte_exact':{'path':relative(original),'sha256':originalsha},'counts':counts,'count_scope':'Counts are provenance rows, not distinct capabilities, meanings,individualsorreplicas. Multiplehistoricalfamiliescanlinkthesamenewoperation.','capabilities':caprows})
 bygroup=defaultdict(list)
 for c in caprows:bygroup[c['group']].append(c['id'])
 put(ROOT/'revision/MAPA_CPC1_A_7.json',{'schema':'CPC8R.campaign.map.v1','generated_utc':generated,'groups':[{'id':k,'capability_row_ids':v,'new_status_source':'revision/MATRIZ_CAPACIDADES_ACUMULADAS.json','historical_source_lookup':'revision/INVENTARIO_FUENTES.json'}for k,v in bygroup.items()],
  'relations':[{'from':'CPC1/CPC2','to':'CPC3/SEM01','kind':'Earlierfiniteprotocols,association,currentMAINandforecastreferences; notoneindividual'},{'from':'SEM01','to':'CPC4','kind':'Cue/consequenceacquisitionextendedtophysicalcommunication'},{'from':'CPC4','to':'CPC5','kind':'Communication/regulationreferencesandarchitecturecomparisons; differentworlds'},{'from':'CPC5','to':'CPC6','kind':'Acquiredrelationsandphysicalcompositionpatterns'},{'from':'CPC6','to':'CPC7','kind':'NewsingleMAINcontinuity,accessandfiniteM1revision'},{'from':'CPC7','to':'PRODUCT4.5','kind':'Compiledoptionalpreparationsandinstalledfiniteprotocolfacades'},{'from':'PRODUCT4.5','to':'NEW_CPC8_RECONSTRUCTION','kind':'FrozeninstrumentfornewpostT0histories; noautomaticinheritanceofresults'},{'from':'OLD_CPC8_SOC21','to':'NEW_CPC8_RESCUE','kind':'Fullsavedstate138→166replayonly; notnewE1'},{'from':'ING02/SEM01/CPC7','to':'NEW_E1_LCE','kind':'Explicitboundedfamilyadaptationsandnewjointvalidation'}],
  'new_profile_links':{'LCE':{'measured':lce_ok,'primary':p_lce},'IUE':{'measured':iue_ok,'source':'src/integracion/initiative_use_e1.py','primary':'resultados/integracion/IUE_P01_RETURN_USED_PLUS/MEASUREMENTS.json','relation':'FreshT0successorprofile addsphysicalrequestandreturnuse; neverrelabelsLCEasifitalreadyhadthosefunctions.'},'MCTS':{'measured':mcts_ok,'primary':relative(mcts_primary),'source':'src/transferencia_magnitud/cts_integrado.py','relation':'FreshT0successorofCTSwithseparatelyexperiencedmagnitudesourceandsevenrecipientcontexts; notretroactiveadditiontoLCE/IUE/CTSsavedindividuals.'}},
  'denominators_not_pooled':{'65_catalogue':'SourcedNSMdocumentaryinventory,not65learnedmeanings','65_capacity':'HistoricalopaqueinterfacesN131','64_unchanged_if_one_of65_revised':'Arithmeticpaneldenominatoronly; notanobservednewE1score','63_old_SOC21':'Actuallyreportedcoveredoldoriginalinterfaces; historicalcut','13_old_CPC7':'Measuredunchangedothersafteroneof14revised','new_E1':'ItsownN67finiterepertoireandhorizon549oractuallaterextension; do not poolcohorts'}})
 word549=next((f['joint']for f in(current or{}).get('frames',[])if f['tick']==549),None)
 core_summary={'active':lce_ok,'horizon':549 if lce_ok else None,'receipt_statuses':current.get('receipt_statuses')if current else None,'word549_all_fixed_ports':word549,
  'quantity_pre_and_outputs':[{'tick':o['tick'],'reference':o['reference'],'object':o['object'],'center':o['center']}for o in(current or{}).get('quantity_observations',[])if o['tick']in(69,70,136,137,203,204,270,271,337,338,404,405,471,472,538,539)],'proofs':lce_proofs}
 put(ROOT/'revision/E1_INTEGRACION_AUDITADA.json',{'schema':'CPC8R.E1.bounded.integration.audit.v3','generated_utc':generated,'source_primary':p_lce,'scope':'LCE,IUE,CTS,MCTSareseparatefreshT0profiles. Eachlateroperationhasitsownactualprimary/control/reserve; noneisretconnedintotheother.','data':core_summary,'new_IUE_profile':iue_profile,'new_MCTS_profile':{'measured':mcts_ok,'proofs':mcts_proofs,'full_scope_report':'revision/TRANSFERENCIA_MAGNITUD.json'},'auxiliary_CMCTS_profile':proof('revision/REGULACION_POR_CONSECUENCIA_EN_MCTS.json','Twofreshcombinedworldsandfourforks; finitepreparedpolicy, physicalcoexistence, notthedefaultapporlearnedR2strategy')if(ROOT/'revision/REGULACION_POR_CONSECUENCIA_EN_MCTS.json').exists()else None,'interpretation':'Earlierfunctioncanstillbequeriedafternewexperienceandadditivereferenceupdate; fixedreaders/resources/guards remainprepared. SameRuntime doesnotmeanalloperationsarelearnedorallhistoricaldomainsintegrated.'})
 text=f'''# Auditoría transversal de CPC1–7 y reconstrucción CPC8

La reconstrucción conserva mecanismos útiles y los vuelve a distinguir por su procedencia. Cuatro trayectorias CPC7 se reprodujeron en el instrumento oficial4.5 con igualdad de RAW, clocks, tick y recibos. El positivo conserva13/13 relaciones no revisadas después de cambiar una de14; el contraste de guardas conserva el resultado adverso de6/13. No se reemplazó ese dato por una etiqueta favorable.

## Herencia y nueva integración

Las47 filas históricas permanecen byte-exactas en `genealogia/MATRIZ_ANTECEDENTES_47.json`. La matriz nueva añade enlaces a operaciones verificadas; no declara incorporado todo el dominio de ninguna familia histórica. Sus {counts['bounded_MAIN_operation_links']} enlaces parciales comparten evidencias y no representan ese número de descubrimientos independientes. CP02 con barrera externa, ausencia general, todos los aparatos CORE y el banco65 no se convierten en órganos del nuevo individuo por compartir API.

El nuevo LCE se preparó desdeT0 enN67. Recibe acontecimientos de orden, una consecuencia de contacto, referencias y señales por interfaces declaradas. Sus productos se encuentran físicamente; la asociación posterior permite consultar una emisión anterior después de otras adquisiciones. Se midió hasta549 sin ediciones externas de RAW/clocks en MAIN. `E1_INTEGRACION_AUDITADA.json` conserva los cuatro puertos de la palabra549 —incluidos los que sólo contienen recursos— y los operandos/salidas de cantidad. Las oportunidades, guías, comparador y recursos son preparados; la experiencia cambia relaciones y referencias. Los controles de nombres y adquisición nueva y las reservas AB/BA-contacto/libre son mundos separados, no recuerdos añadidos retrospectivamente a esa vida.

El perfil nuevo IUE, identificado por fuente `6078b7c0baeb647a842c14f017b9056ae1887772374438144f852168de324138` y primario `c932e8a2523f8fae8e47cd5003a9bb8c0ac70485de6ee65b20d0f004ac053951`, añade una cadena real de solicitud72→fuente77→retorno86→uso43en89 sin cambiar retrospectivamente LCE. La historia del proveedor cambia cuál de dos receptores recibe el efecto con la misma carga; falta de pregunta cualificada, experiencia desacoplada y corte tardío87 eliminan43. El sham y las reservas lo conservan. La restauración completa reproduce549 y permite una nueva consulta613→616 de una palabra anterior, sin reenseñarla. Ese perfil mantiene las funciones anteriores y una experiencia de contacto nueva340; sus costes y ventanas siguen siendo preparados, no una estrategia general adquirida.

El perfil fresco posterior MCTS conserva el CTS comunicativo e incorpora transferencia de magnitud: un portador36, adquirido por dos experiencias adicionales reales en la fuente, llega nativamente al receptorB mediante encuentros de carga0. B lo utiliza frente a objetos23/50/36 en147/214/281. Las historias11 y17 y sus reservas cambian los operandos y respuestas con la misma API; omitida/desacoplada/corte/sham separan adquisición y transporte. Las funciones CTS anteriores, incluida su comunicación554 y palabra616, se conservan en las observaciones locales comparables. Son35 materiales y131interfaces, no recursos iguales al CTS28/120. La referencia antigua del E1 y esta nueva fuente tuvieron exposiciones separadas, no una clonación gratuita. `TRANSFERENCIA_MAGNITUD.json` cuenta12 contenedores primarios:10 preparaciones y, dentro de dos agregados,4 forks y2 restauraciones;16 trayectorias, no12 réplicas independientes. MCTS es una vida nueva desdeT0, no un añadido retrospectivo a los snapshots anteriores.

Como candidato auxiliar distinto, CMCTS añade desdeT0 el aparatoV2 traducido de política finita por consecuencia:2vidas completas0→616 y4forks causales4→616, sin entradas del host en ese componente después deT0. El contacto actual cambiaP/Q y conserva una entrega3en15; cortar el retorno formado4 elimina esa función y el sham reproduce el estado completo616. El repertorio funcional MCTS se conserva, aunque el positivo sí presenta una interacción transitoria73: un portador11 ocupa un puerto antiguo fuera de su ventana de uso. No se sustituye esa diferencia por una afirmación de aislamiento perfecto. Su perfil preparado y sus59materiales no son la aplicación MCTS35materiales seleccionada ni una estrategia general adquirida; los datos y el alcance están en `REGULACION_POR_CONSECUENCIA_EN_MCTS.json`.

## Rescate positivo del corte anterior

SOC_I21 no fue descartado: su estado completo138 se continuó hasta166. El mensaje intacto y su sham reproducen exactamente el estado histórico; el receptor emite72(0,+1,+1)157, mientras el corte sólo deja el lector7(0,0,+1). Esta prueba reabre de forma reproducible el encuentro pedagógico y su utilización, sin afirmar haber reejecutado aquí toda la vida0–1182.

L15 distingue acceso de desaparición global. Un producto aprendido16 encuentra otro7 y se transforma en23 con dirección distinta79. Eliminar7 conserva inicialmente16, pero no recupera por sí solo el acceso original134. Una sonda física alternativa9 produce32@82; al cortar el componente aprendido queda16=7+9. Son forks diagnósticos explícitos de la genealogía anterior, no recuperación autónoma ni datos reintroducidos en MAIN.

El antecedente V2 de regulación por consecuencia también se reejecutó: seis configuraciones mantienen estados completos y observaciones históricas exactos; cuatro cortes/shams tardíos localizan el retorno físico que cambia la políticaP/Q y conserva una entrega3 en15. Son episodios finitos con reglaR14 y rutas preparadas, sin entradas del host después deT0. No se añaden retrospectivamente al nuevoE1 ni acreditan adquirir una estrategia general. La ficha `REGULACION_POR_CONSECUENCIA_ANTECEDENTE.json` conserva fuente,39miembros seleccionados, denominadores y reproducción. El perfil distinto `REGULACION_E1_FINITA.json` añade regulación adquirida con mantenimiento externo explícito en otra trayectoria nueva.

## Denominadores y significados

65 corresponde tanto a un inventario documental NSM como, en otro aparato, a interfaces opacasN131: son dominios diferentes. El corte histórico SOC21 informa63/65 accesos directos, después63/63 de su subconjunto disponible. Revisar una de65 dejaría un denominador aritmético64, no un resultado observado del nuevoE1. CPC7 acredita13 relaciones no modificadas de un panel14. Ninguna de esas cifras prueba65 significados. La matriz semántica vigente conserva sus niveles y sus pendientes por separado; esta auditoría no la reescribe ni suma funciones de cohortes distintas como conocimiento de un solo individuo.

## Instrumento, fuentes y observadores

El WHL4.5 y su extensión coinciden con las identidades oficiales; la copia fuente de kernel_v27 conserva SHA-256 `{KERNEL}`. Pasaron82 tests Python disponibles. Esto es una regresión técnica, no una ejecución nueva de todo el corpus ni un nuevo consumidorC++. Los informes compilados originales permanecen como evidencia histórica.

Se inventariaron35 paquetes y se seleccionaron55 miembros del corpus además de referencias de las47 filas; no hubo lectura lineal total. Se leyeron exactamente4 hilos y16 turnos recientes, con páginas anteriores y referencias no expandidas identificadas. Los dos Word4.5 están descritos y enlazados en conversaciones accesibles, pero sus bytes no fueron recuperados en este entorno: no se afirma lectura completa ni inexistencia de los documentos. El registro exacto de URLs/IDs y las lecturas de Física/entrelazamiento está enlazado desde `INVENTARIO_FUENTES.json`.

RAW desempaquetado, dirección, fase, contexto, estado de admisión y lectura funcional siguen siendo observadores distintos. Una dirección cero activa no es silencio; una sonda rechazada no es olvido; una diferencia RAW no demuestra uso. CORE15–17, Ingenierías y Procesos sustentan esas distinciones en sus dominios, pero sus teoremas, aparatos ejecutados y analogías no se confunden con conocimientos adquiridos por el participante nuevo.

## Recalcular y reproducir

`python tools/consolidar_auditoria_transversal.py` reconstruye este overlay sin importar el motor ni ejecutar mundos; necesita los antecedentes seleccionados y, para verificar identidad/proteger el pasado en el entorno de desarrollo, el ZIP histórico externo identificado. Los comandos operativos de CPC7, SOC21 y L15 incluidos en sus fichas sólo requieren la extracción y el WHL instalado; el archivo histórico completo no es una dependencia del participante ni se anida en la entrega nueva.

La lectura provisional final puede ampliar estos enlaces únicamente con resultados nuevos cerrados. Esta auditoría fija alcance por operación y no emite un veredicto universal de mente ni una promesa de capacidad no medida.
'''
 (ROOT/'revision/ANALISIS_TRANSVERSAL.md').write_text(text,encoding='utf-8')
 print(json.dumps({'capability_rows':47,'source_members':len(members),'verified_included_members':source_inventory['counts']['verified_included_historical_members'],'counts':counts,'product_checks':identity['checks'],'LCE_measured':lce_ok,'original47_unchanged':sha(original)==originalsha}))
if __name__=='__main__':main()
