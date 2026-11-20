"""Installed official engine, recovered sources, no historical filesystem reads.

Audit references are read only after each original native trajectory completes.
This is recovery of bounded contracts, not new independent scientific samples.
"""
import argparse,gc,hashlib,importlib,json,os,re,runpy,shutil,struct,sys,tempfile,time,types,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WHEEL='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
PYD='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def put(p,o):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def restrict_reads(materialized,out,native_temporary):
 allowed=((Path(__file__).resolve().parents[3]/'runtime').resolve(),ROOT.resolve(),materialized.resolve(),out.resolve(),native_temporary.resolve(),Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve(),Path(os.environ['WINDIR']).resolve())
 log=[]
 def audit(event,args):
  if event!='open'or not args or isinstance(args[0],int):return
  name=args[0]
  if not isinstance(name,(str,bytes,os.PathLike)):return
  path=Path(os.fsdecode(name)).resolve()
  if not any(path==r or path.is_relative_to(r)for r in allowed):
   log.append(str(path));raise PermissionError('Core recovery blocks undeclared historical/external file: '+str(path))
 sys.addaudithook(audit);return log
def identity():
 sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
 from app.process_control import protect_current
 protection=protect_current()
 import dee_thinking as d
 assert sys.version_info[:2]==(3,13)and struct.calcsize('P')==8 and sys.flags.isolated and sys.dont_write_bytecode
 assert d.__version__=='4.5.0'and d.kernel_identity()['kernel_version']==27
 assert Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
 assert sha(d._native.__file__)==PYD
 wheel=Path(__file__).resolve().parents[3]/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl';assert sha(wheel)==WHEEL
 return{'python':sys.executable,'version':d.__version__,'module':d.__file__,'pyd':d._native.__file__,'pyd_sha256':PYD,'wheel_sha256':WHEEL,'kernel':d.kernel_identity()}
def compare_data(actual,expected,ignore=()):
 # JSON is the neutral interchange contract: tuples in live Python and arrays
 # in the frozen JSON fixture denote the same ordered data, not different physics.
 actual=json.loads(json.dumps(actual));expected=json.loads(json.dumps(expected))
 diffs=[]
 def walk(a,b,path):
  if path.rsplit('/',1)[-1]in ignore:return
  if type(a)!=type(b):
   if a==b:return
   diffs.append({'path':path,'actual':a,'expected':b});return
  if isinstance(a,dict):
   for k in sorted(set(a)|set(b)):
    if k not in a or k not in b:diffs.append({'path':path+'/'+k,'missing':'actual'if k not in a else'expected'})
    else:walk(a[k],b[k],path+'/'+k)
  elif isinstance(a,list):
   if len(a)!=len(b):diffs.append({'path':path,'actual_length':len(a),'expected_length':len(b)})
   for i,(x,y)in enumerate(zip(a,b)):walk(x,y,path+'/'+str(i))
  elif a!=b:diffs.append({'path':path,'actual':a,'expected':b})
 walk(actual,expected,'');return diffs
def cpc1(mat,out):
 source=mat/'historico/CPC3/genealogia/CP01_C08';sys.path.insert(0,str(source/'src'))
 import fronts,laboratorio
 cfg=json.loads((source/'casos/EXPERIMENT_CONFIG.json').read_text(encoding='utf8'))
 rows=[]
 for field in('C01','C02','C03','C04','C05','C06','C07','C08_INTERFACE_V2'):
  actual=fronts.FIELDS[field](out,cfg[field])
  historical=source/'casos'/field/'RESULTADOS.json'
  expected=json.loads(historical.read_text(encoding='utf8'))
  diffs=compare_data(actual['measurements'],expected['measurements'])
  # Snapshot native containers can differ in4.5 metadata; exact physical digests remain comparable.
  a=[r['state']for r in actual['checkpoints']]
  b=[r['state']for r in expected['checkpoints']]
  state_diffs=compare_data(a,b)
  row={'field':field,'functional_fields_equal':not diffs,'checkpoint_physical_equal':not state_diffs,'function_differences':diffs,'physical_differences':state_diffs,'snapshot_filename_metadata':{'actual':[r['name']for r in actual['checkpoints']],'historical':[r['name']for r in expected['checkpoints']],'not_physical_state':True},'reference_sha256':sha(historical),'scope':'Original finite preparation/inputs/controls/reserves on4.5; no new E1integration'}
  rows.append(row);put(out/'CPC1_RECUPERACION.json',{'status':'RUNNING','cases':rows});gc.collect()
 return{'status':'PASS'if all(r['functional_fields_equal']and r['checkpoint_physical_equal']for r in rows)else'FAIL','cases':rows,'native_case_functions':7,'derived_diagnosis':1}
def cpc2(mat,out):
 source=mat/'historico/CPC3/genealogia/CP02_B';sys.path.insert(0,str(source/'src'))
 from predictor import PredictorSession,PersistentTransportHabitat,build,AuditLog,physical,panel,receipt
 rows=[];log=AuditLog(out/'PREDICCIONES.jsonl')
 for opened in(False,True):
  for history in('paired','none','unpaired'):
   s=PredictorSession(build((22,20,24),3),PersistentTransportHabitat(opened));s.experience_past_results(history)
   emission=s.predict([70],log,str((opened,history)),11);assert emission['emission_tick']<70
   snapshot=out/f'{int(opened)}_{history}_EMITTED.deetsnap';s.save(snapshot);copy=PredictorSession.load(snapshot)
   same=physical(copy.world)==physical(s.world);a=s.evaluate(70,log,'native');b=copy.evaluate(70,log,'restored')
   row={'gate':opened,'history':history,'emission':emission,'outcome':a,'restored_outcome':b,'physical_before_equal':same,'physical_after_equal':physical(copy.world)==physical(s.world),'physical_after':physical(s.world),'scope':'Native prediction before actual independent external habitat outcome; rule/habitat declared in original source'};rows.append(row);del s,copy;gc.collect()
 return{'status':'PASS'if all(r['physical_before_equal']and r['physical_after_equal']and(r['history']!='paired'or r['outcome']['absolute_error_binary']==0)for r in rows)else'FAIL','cases':rows,'scope':'Six fresh reserved-geometry source trajectories; paired/omitted/desynchronized experience, prospective output and exactrestore, not replay of original maternalMAIN'}
def product(mat,out):
 source=mat/'cpc8/base_validada/product45/tests/python';sys.path.insert(0,str(source))
 names=['test_wheel_api','test_organizational_api','test_cognitive_api','test_cognition_facilitators','test_informative4','test_consolidated_api','test_remote_reader_api','test_experimental_absence','test_experimental_regulation','test_integrated_protocols']
 suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n)for n in names)
 with(out/'UNITTEST.log').open('w',encoding='utf8')as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
 return{'status':'PASS'if result.wasSuccessful()else'FAIL','tests_run':result.testsRun,'errors':[{'test':str(t),'traceback':e}for t,e in result.errors],'failures':[{'test':str(t),'traceback':e}for t,e in result.failures],'scope':'Official preserved API regression cases, controls/persistence, not fresh proof of each historicalcampaign'}
def product_extra(mat,out):
 source=mat/'cpc8/base_validada/product45/tests/python';sys.path.insert(0,str(source))
 suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n)for n in('test_basal_api','test_mbp4_regressions'))
 with(out/'UNITTEST.log').open('w',encoding='utf8')as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
 return{'status':'PASS'if result.wasSuccessful()else'FAIL','tests_run':result.testsRun,'errors':[{'test':str(t),'traceback':e}for t,e in result.errors],'failures':[{'test':str(t),'traceback':e}for t,e in result.failures],'scope':'Original MBP4 productregressions including exacthistoricalT32/checkpointinitialstates andlocalcausalcontrols; thosesnapshots are declaredinitialfixtures,notnewlytrainedE1.'}

def product_persistence(mat,out):
 source=mat/'cpc8/base_validada/product45/tests/python';sys.path.insert(0,str(source))
 names=('test_cognition_facilitators.CognitionFacilitators.test_online_composition_and_native_operational_load','test_cognition_facilitators.CognitionFacilitators.test_ui_alias_restores_without_sidecar_or_hidden_reset','test_consolidated_api.ConsolidatedApiTests.test_other_process_continuation','test_consolidated_api.ConsolidatedApiTests.test_pending_query_gzip_restore_and_deep_fork','test_consolidated_api.ConsolidatedApiTests.test_snapshot_crc_bounds_and_hash','test_remote_reader_api.RemoteReaderTests.test_remote_cut_sham_save_load_do_not_replace_MAIN','test_experimental_absence.AbsenceTests.test_passive_observation_fork_and_pending_restore','test_experimental_regulation.ExperimentalRegulationTests.test_acquired_pulse_persistence_and_fork')
 suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n)for n in names)
 with(out/'UNITTEST.log').open('w',encoding='utf8')as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
 return{'status':'PASS'if result.wasSuccessful()else'FAIL','tests_run':result.testsRun,'tests':list(names),'errors':[{'test':str(t),'traceback':e}for t,e in result.errors],'failures':[{'test':str(t),'traceback':e}for t,e in result.failures],'scope':'Only eight persistence tests affected by candidate1 hostTEMP Unicode mistake. Other60 producttests and14 MBP4tests retain their exact sealedcandidate1 results; no engine/recipe/test alteration.'}
def cpc4(mat,out):
 root=mat/'historico/CPC4/ampliaciones/02_APRENDIZAJE_CONTINUO_RED_ABCD';sys.path.insert(0,str(root/'src'))
 from red import common_helpers,recipe_v3
 common_helpers.identity=identity;recipe_v3.identity=identity
 from red.regulated_habitat import run
 rows=[]
 for frozen in json.loads((ROOT/'configuraciones/RECUPERACION_CONGELADA.json').read_text(encoding='utf8'))['cases']['cpc4']:
  name=frozen['id'];ref=mat/frozen['original_primary'];actual=run(frozen['input_configuration'],out/name)
  old=json.loads(ref.read_text(encoding='utf8'));diffs=compare_data(actual,old)
  rows.append({'id':name,'all_primary_observations_receipts_equal':not diffs,'differences':diffs,'external_utility_observed':actual['external_utility'],'historical_primary_sha256':sha(ref)});gc.collect()
 return{'status':'PASS'if all(r['all_primary_observations_receipts_equal']for r in rows)else'FAIL','cases':rows,'scope':'Original fourregionfixedcounterflow/R0 vsnone/equaldoseoffrouteshams andreservedtranslation; notlearnedregulationpolicy.'}
def cpc5(mat,out):
 root=mat/'historico/CPC5';sys.path.insert(0,str(root/'src'));import common
 common.identity=identity
 from compound import run_case
 index=json.loads((ROOT/'documentacion/INDICE_MIEMBROS.json').read_text(encoding='utf8'))['paths'];rows=[]
 for frozen in json.loads((ROOT/'configuraciones/RECUPERACION_CONGELADA.json').read_text(encoding='utf8'))['cases']['cpc5']:
  name=frozen['id'];ref=mat/frozen['original_primary'];actual=run_case(frozen['input_configuration'],out/name);old=json.loads(ref.read_text(encoding='utf8'))
  keys=('lessons','readouts','native_windows','transition_neighborhoods','interventions','calls','receipts','final_physics','external_operations')
  diffs={key:compare_data(actual[key],old[key])for key in keys};checks={k:not v for k,v in diffs.items()}
  rows.append({'id':name,'comparisons':checks,'differences':{k:v for k,v in diffs.items()if v},'full_final_RAW_clocks_tick_equal':actual['final_physics']==old['final_physics'],'historical_primary_sha256':sha(ref)});gc.collect()
 return{'status':'PASS'if all(all(r['comparisons'].values())for r in rows)else'FAIL','cases':rows,'scope':'Sixcomponentphysicalcommonproductincorporatesfour separatelyexperiencedrelations/backups, causal messagecut/sham, opposite/unpaired/disconnected andreservedorder/query. No cognitiveworddepthfromload.'}
def cpc6(mat,out):
 root=mat/'historico/CPC6';sys.path.insert(0,str(root/'src'));import common
 common.identity=identity
 import life
 rows=[]
 for frozen in json.loads((ROOT/'configuraciones/RECUPERACION_CONGELADA.json').read_text(encoding='utf8'))['cases']['cpc6']:
  name=frozen['id'];ref=mat/frozen['original_primary'];actual=life.run(frozen['input_configuration'],out/name);old=json.loads(ref.read_text(encoding='utf8'))
  keys=('rows','requests','predictions','local_windows','summary','final_physical','final_operative','alias_admission','host_RAW_clock_edits_after_T0')
  diffs={key:compare_data(actual[key],old[key])for key in keys};checks={k:not v for k,v in diffs.items()}
  rows.append({'id':name,'comparisons':checks,'differences':{k:v for k,v in diffs.items()if v},'full_final_RAW_clocks_tick_equal':actual['final_physical']==old['final_physical'],'historical_primary_sha256':sha(ref)});gc.collect()
 return{'status':'PASS'if all(all(r['comparisons'].values())for r in rows)else'FAIL','cases':rows,'scope':'OriginalfourN67CPC6wordbus170horizon, ownorderforecastcomparisonconditionalP/Qnativeaction/return/newform/renewedreader; paired/no-repeat/unpaired/oppositehistory. Preparedselectionnotgeneralwhomtoask.'}
def sem01(mat,out):
 source=mat/'historico/CPC3/experimentos/SEM01_SIGNIFICADO_ADQUIRIDO/src'
 package=types.ModuleType('sem01_recovered');package.__path__=[str(source)];sys.modules['sem01_recovered']=package
 experiment=importlib.import_module('sem01_recovered.experiment');rows=[]
 for frozen in json.loads((ROOT/'configuraciones/RECUPERACION_CONGELADA.json').read_text(encoding='utf8'))['cases']['sem01']:
  name=frozen['id'];actual=experiment.run_case(frozen['input_configuration'],out/name);ref=mat/frozen['original_primary'];old=json.loads(ref.read_text(encoding='utf8'))
  keys=('initial','teaching','uses','final','external_operations_actual');diffs={k:compare_data(actual[k],old[k])for k in keys};checks={k:not v for k,v in diffs.items()}
  normalize=lambda x:[re.sub(r' at 0x[0-9A-Fa-f]+',' at <HOST_ADDRESS>',s)for s in x]
  checks['diagnostic_receipt_type_count_not_host_address_equal']=normalize(actual['diagnostic_edits_actual'])==normalize(old['diagnostic_edits_actual'])
  rows.append({'id':name,'comparisons':checks,'differences':{k:v for k,v in diffs.items()if v},'historical_primary_sha256':sha(ref),'nonphysical_legacy_metadata':{'actual':actual['diagnostic_edits_actual'],'historical':old['diagnostic_edits_actual'],'limit':'Legacystr(object)retainsclass/countandhostmemoryaddress,nottypedreceiptfields. HostaddressesareNOTphysicalDEEstate; exactphysicalpre/postandusesremaincompared.'}});gc.collect()
 return{'status':'PASS'if all(all(r['comparisons'].values())for r in rows)else'FAIL','cases':rows,'scope':'OriginalSEM01nativehistory/signal-onlyanticipation/functionalaction+current-outcomesensor, opposite/none/unpaired/action-omission andtwohistoricalreservedrealizations. Fixedexternaltransducerandpreparedactioncouplingdeclared; noNSMmeaninginferred.'}
def cpc7(mat,out):
 root=mat/'cpc8';source=root/'genealogia/CPC7/src';sys.path[:0]=[str(source),str(source/'endogenous'),str(root/'base_validada')]
 import common,reproducir_cpc7 as adapter
 common.identity=adapter.identity45
 import integrated,integrated_revision
 integrated.Session.save=adapter.save_gzip
 config=root/'genealogia/CPC7/configuraciones/integrated_revision.json';cfg=json.loads(config.read_text(encoding='utf8'));rows=[]
 for case in cfg['cases']:
  target=out/case['id'];actual=integrated_revision.execute(case,target,sha(config))
  reference=root/'genealogia/CPC7/resultados/integrated_revision'/case['id']/'MEASUREMENTS.json';old=json.loads(reference.read_text(encoding='utf8'))
  row={'id':case['id'],'full_final_RAW_clocks_tick_equal':actual['final_physical']==old['final_physical'],'base338_RAW_clocks_tick_equal':actual['base338']['final_physical']==old['base338']['final_physical'],'post_revision_calculations_equal':actual['calculations']==old['calculations'],'base_calculations_equal':actual['base338']['calculations']==old['base338']['calculations'],'receipts_equal':actual['final_operational']['receipts']==old['final_operational']['receipts'],'actual':actual['calculations'],'expected':old['calculations'],'historical_primary_sha256':sha(reference)}
  row['passed']=all(row[k]for k in('full_final_RAW_clocks_tick_equal','base338_RAW_clocks_tick_equal','post_revision_calculations_equal','base_calculations_equal','receipts_equal'));rows.append(row);put(out/'CPC7_RECUPERACION.json',{'cases':rows});gc.collect()
 return{'status':'PASS'if all(r['passed']for r in rows)else'FAIL','cases':rows,'scope':'Four originalCPC7 trajectories0→472, originalrecipes/inputs/controls; officialversionassertion and losslessgzipstorage adapter only. AllhistoricalT0snapshots omitted; exactbase338/final472digests compared with originalimmutableprimaryJSON.'}
def mcts(mat,out):
 root=mat/'cpc8';script=root/'src/transferencia_magnitud/run_cts.py';rows=[]
 for name in('MCTS_P01_SOURCE31','MCTS_H01_SOURCE11','MCTS_C01_SOURCE_OMITTED','MCTS_C02_SOURCE_UNPAIRED','MCTS_R101_VALUE17_NEW_HISTORY'):
  target=out/name;sys.argv=[str(script),'--case',name,'--out',str(target)];runpy.run_path(str(script),run_name='__main__')
  actual=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf8'));ref=root/'resultados/transferencia_magnitud'/name/'MEASUREMENTS.json';old=json.loads(ref.read_text(encoding='utf8'))
  checks={key:actual[key]==old[key]for key in('final_physical','frames','requests','magnitude_readings','quantity_observations','contact_social_observations','initiative_captures','return_use_observations','renewal_observations','mode_captures','social_captures','receipt_statuses')}
  row={'case':name,'exact_comparisons':checks,'passed':all(checks.values()),'historical_primary_sha256':sha(ref),'native_final_physical':actual['final_physical']};rows.append(row);put(out/'MCTS_RECUPERACION.json',{'cases':rows});gc.collect()
 return{'status':'PASS'if all(r['passed']for r in rows)else'FAIL','cases':rows,'scope':'Original freshCPC8 MCTS35support131portworlds0→616; positive,opposite,omitted,unpaired,reserve. These are five distinctrecoveries,notfiveknowledgeblocksinsideoneE1.'}
def repertoire(mat,out):
 root=mat/'cpc8';script=root/'base_validada/reproducir_repertorio65.py';rows=[]
 for name in('K65_PAIRED','K65_UNPAIRED','K65_RESERVE','K65_REVISION_CADENCE','K65_REVISION_OFFPATH'):
  target=out/name;sys.argv=[str(script),'--case',name,'--out',str(target)];runpy.run_path(str(script),run_name='__main__')
  v=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf8'));correct=[r['auditor_correct']for r in v['all65queries']];rev=v['revision']
  row=assess_repertoire(mat,name,v);rows.append(row);put(out/'K65_RECUPERACION.json',{'cases':rows});gc.collect()
 return{'status':'PASS'if all(r['passed']for r in rows)else'FAIL','cases':rows,'scope':'Published N13165opaqueformcorrespondences,32+33acquisitions/threequeriesandfiniteL01revision with equal-doseoffpathcontrol. NOT65NSMmeanings orsameE1asCPC7/MCTS.'}
def assess_repertoire(mat,name,v):
 alias='K65_PAIRED_RECOVER658'if name=='K65_PAIRED'else name
 ref=mat/'cpc8/resultados/repertorio65_referencia'/alias/'MEASUREMENTS.json';old=json.loads(ref.read_text(encoding='utf8'))
 checks={'full_final_RAW_clocks_tick_equal':v['final']==old['final'],'captured_all_queries_equal':[r['captured']for r in v['all65queries']]==[r['captured']for r in old['all65queries']],'first32query_equal':v['first32query']==old['first32query'],'exact_input_journal_equal':v['inputs']==old['inputs']}
 if v['revision']is not None:
  checks['revision_captured_exact']=v['revision']['captured']==old['revision']['captured']
 return{'case':name,'correct':[r['auditor_correct']for r in v['all65queries']],'denominator':65,'revision':v['revision'],'final_physical':v['final'],'historical_primary_sha256':sha(ref),'exact_historical_checks':checks,'passed':all(checks.values()),'interpretation':'Reproductionstatuschecksactualhistoricaltrajectory,notassumednegativeanswer. Unpaired32/65→65/65→65/65showslearningduringevaluation; offpathL01revisionfailsandretains63/64others,not64.'}
def rca(mat,out):
 from copy import deepcopy
 root=mat/'cpc8';sys.path.insert(0,str(root/'src'))
 from dee_thinking import _native as d
 from dee_thinking.consolidated import exact_receipt
 from integracion.quantity_core import physical
 from regulacion_acoplada.mcts import CoupledMagnitudeCTSSession
 cfg=json.loads((root/'configuraciones/transferencia_magnitud/CTS_CONGELADO.json').read_text(encoding='utf8'))['cases'][0]
 prepkeys=('guard_mode','actor_mode','include_order','include_contact','event_state_offset','medium_load','actor_state','quantity_guards','regulation')
 ticks=(4,5,9,10,11,15,53,54,69,70,77,78,79,136,137,147,206,214,281,428,549,554,559,563,616);rows=[];forks=[]
 for medium,name in((1,'RCAM_R201_FUNCTION_PLUS'),(-1,'RCAM_R202_FUNCTION_MINUS')):
  target=out/name;target.mkdir();s=CoupledMagnitudeCTSSession.create(identifier=name,medium=medium,routing='onpath',**{k:v for k,v in cfg.items()if k in prepkeys});s.curriculum(regulation_reference=31,regulation_objects=(16,37),**{k:v for k,v in cfg.items()if k not in('id',*prepkeys)})
  frames=[];snap=target/'T77.deetsnap.gz'
  for tick in ticks:
   s.run_until(tick);f=s.view();f['mode'].pop('captures',None);f['mode'].pop('social_captures',None);frames.append(f)
   if tick==77:s.save(snap)
  final=physical(s.world);requests=s.receipts();receipts=[exact_receipt(x)for x in s.world.runtime.receipts];s.save(target/'T616.deetsnap.gz');del s;gc.collect()
  restored=CoupledMagnitudeCTSSession.load(snap);restored.run_until(616);restore_equal=physical(restored.world)==final and[exact_receipt(x)for x in restored.world.runtime.receipts]==receipts;del restored;gc.collect()
  reference=root/'resultados/regulacion_acoplada'/name/'MEASUREMENTS.json';old=json.loads(reference.read_text(encoding='utf8'));at={f['tick']:f for f in old['frames']};checks={'native_captured_fields_equal':all(f==at[f['tick']]for f in frames),'full_final_RAW_clocks_tick_equal':final==old['final_physical'],'all_exact_requests_equal':requests==old['requests'],'restore77_to616_state_and_receipts_equal':restore_equal}
  row={'case':name,'checks':checks,'frames':frames,'final_physical':final,'reference_sha256':sha(reference),'passed':all(checks.values())};rows.append(row);put(target/'MEASUREMENTS.json',row)
  if medium==1:
   parent=CoupledMagnitudeCTSSession.load(snap);before_state=physical(parent.world);site=parent.geometry['coupled_regulation']['counterflows']['P']['pre_interception_site'];before=parent.observe(site);assert before['s_reg']==114 and before['direction']==[-1,0,0]
   for condition in('cut','sham'):
    edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.raw=0 if condition=='cut'else int(before['raw']);edit.clock=None;edit.label='CORE RCA '+condition
    world=parent.world.diagnostic_fork([edit],True);child=CoupledMagnitudeCTSSession(world,parent.geometry,deepcopy(parent.state),parent.identifier)
    child.run_until(136);operands=child.view()['coupled_regulation']['quantity'];child.run_until(137);output=child.view()['coupled_regulation']['quantity']['center'];child.run_until(616)
    forks.append({'condition':condition,'before':before,'operand_fields136':operands,'native_output137':output,'native_final':physical(world),'parent_unchanged':physical(parent.world)==before_state,'terminal_equal_parent_unedited616':physical(world)==final,'passed':output['active']and output['direction']==([1,0,0]if condition=='cut'else[-1,0,0])and physical(parent.world)==before_state});del child,world;gc.collect()
   del parent;gc.collect()
 return{'status':'PASS'if all(r['passed']for r in rows+forks)else'FAIL','cases':rows,'diagnostic_forks':forks,'scope':'Two fresh72supportMCTS+RCA organizations; physicalconsequence-dependentpreparedpolicyproducesregulator. Equalmaterialoppositehistory andselectiveformedregulatorcut/shamchange137direction(-X/+X), evenwhenfinalstatesconverge. NotgeneralutilitylearningorselectedCPC9E1.'}
def count(mat,out):
 root=mat/'cpc8';script=root/'reproduccion/repetir_count_sign.py';rows=[]
 selected=(('CNS_G13_ONE_B','count_sign_final_fixed','COUNT_SIGN_FINAL_READER_FROZEN.json'),('CNS_G51_B_NO_FORM','count_sign_Bonly_confirm','COUNT_SIGN_BONLY_CONFIRMATION_FROZEN.json'),('CNS_G31_RESERVE_ONE_B','count_sign_final_fixed','COUNT_SIGN_FINAL_READER_FROZEN.json'))
 for name,group,config in selected:
  target=out/name;reference=root/'resultados/semantica'/group/name/'MEASUREMENTS.json';sys.argv=[str(script),'--out',str(target),'--case',name,'--config',str(root/'configuraciones/semantica'/config),'--reference',str(reference)];runpy.run_path(str(script),run_name='__main__');v=json.loads((target/'CHECK.json').read_text(encoding='utf8'));rows.append(v)
  if name=='CNS_G13_ONE_B':
   target2=out/(name+'_RESTORE');sys.argv=[str(script),'--out',str(target2),'--case',name,'--restore',str(target/'T94.deetsnap.gz'),'--reference',str(reference)];runpy.run_path(str(script),run_name='__main__');rows.append(json.loads((target2/'CHECK.json').read_text(encoding='utf8')))
  gc.collect()
 return{'status':'PASS'if all(r['passed']for r in rows)else'FAIL','cases':rows,'scope':'Calibratedunit2/threshold8B-onlyacquiredopaquecue, use114/148afteradditionalexperience100; noformandreservedstatehistoryplusrestore94→171. Notgenericcardinality,notjointONE/TWOlexiconorCPC9E1.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('family',choices=('cpc1','cpc2','product','product_extra','product_persistence','sem01','cpc4','cpc5','cpc6','cpc7','mcts','repertoire','rca','count'));p.add_argument('--materialized',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
 # Published 4.5 persists through an ASCII native temporary path, even when
 # the final Python-compressed snapshot/output directory contains Unicode.
 # This is host I/O plumbing, not a world/RAW/clock/policy intervention.
 temp_owner=tempfile.TemporaryDirectory(prefix='dee-core-native-')
 temp=Path(temp_owner.name).resolve()
 if not str(temp).isascii():raise ValueError('Official 4.5 requires an available ASCII TEMP/TMP parent; set it before launching recovery')
 os.environ['TMP']=str(temp);os.environ['TEMP']=str(temp);tempfile.tempdir=str(temp)
 mat=a.materialized.resolve();wheel=Path(__file__).resolve().parents[3]/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl';alias=mat/'cpc8/runtime'/wheel.name;alias.parent.mkdir(parents=True,exist_ok=True)
 if not alias.exists():shutil.copyfile(wheel,alias)
 assert sha(alias)==WHEEL
 ident=identity();blocked=restrict_reads(mat,out,temp);start=time.monotonic();value={'family':a.family,'identity':ident,'started_monotonic':start,'native_temporary_directory':str(temp),'temporary_path_contract':'Generated ASCII native temporary only; scientific outputs retain caller Unicode path. No historical filesystem access.'}
 try:value.update(globals()[a.family](a.materialized.resolve(),out))
 except BaseException as e:
  import traceback;value.update(status='ERROR',error=repr(e),traceback=traceback.format_exc())
 value.update(elapsed_seconds=time.monotonic()-start,undeclared_read_attempts=blocked);put(out/'RECOVERY.json',value);print(json.dumps({'family':a.family,'status':value['status'],'seconds':value['elapsed_seconds']}))
 if value['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
