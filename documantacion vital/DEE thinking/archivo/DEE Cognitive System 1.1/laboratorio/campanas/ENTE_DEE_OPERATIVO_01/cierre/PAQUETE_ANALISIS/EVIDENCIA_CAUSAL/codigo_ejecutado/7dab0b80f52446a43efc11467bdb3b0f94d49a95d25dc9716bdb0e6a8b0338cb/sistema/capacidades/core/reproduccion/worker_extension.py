"""Bounded original CPC5/6 recoveries; no scientific preparation changes."""
from pathlib import Path
import argparse,gc,importlib,json,os,sys,tempfile,time,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent))
import worker_core as audit
ROOT=Path(__file__).resolve().parents[1]
GROUPS={
 'ordered':('ordered_composition','run_case',('geometry','calls','receipts','trace','local_transition_windows','interventions','primary_observations','final','operative_final','technical','host_RAW_writes_in_MAIN','host_clock_writes_in_MAIN','resources')),
 'stream':('order_stream_science_v2','run_case',('geometry','calls','receipts','rows','local_windows','final_physical','final_operative','external_operations','post_T0_host_RAW_clock_edits')),
 'network':('network_dialogue','run_case',('geometry','inputs','receipts','rows','encounter_windows','encounters','calculations','diagnostic_edits','final_physical','final_operative','modality','resources')),
 'architectures':('architecture_screen','run',('geometry','rows','local_windows','calls','alias_admission_groups','predictions','summary','final_physical','final_operative','external_RAW_clock_edits_after_T0','interunit_host_callbacks')),
 'bridge':('architecture_bridge_delayed','run',('geometry','rows','local_windows','requests','alias_groups','summary','final_physical','final_operative','host_output_to_input_callbacks','host_RAW_clock_edits_after_T0')),
 'capacity':('capacity','run_case',('geometry','calls','receipts','lessons','readouts','local_contexts','calculations','final','operative_final','technical','direct_RAW_writes_after_T0','direct_clock_writes_after_T0')),
 'longitudinal':('capacity_longitudinal','run_case',('geometry','calls','receipts','lessons','readouts','local_windows','calculations','final','operative_final','technical','direct_RAW_writes_after_T0','direct_clock_writes_after_T0')),
 'policy':('core.revisable_selection','run',('configuration','metadata','trace','measurements','external_operations','interventions','receipts','host_cognitive_writes','operational_forks','diagnostic_forks','direct_RAW_clock_edits_on_native_cases')),
 'native_loop':('habitat.native_loop','run_native_loop',('metadata','trace','host_writes','receipts','external_operations','operational_forks','postT0_direct_RAW_or_clock_edits')),
 'qfm':('@qfm','run',('configuration','geometry','observations','word_calculations','inputs','final','MAIN_RAW_clock_edits')),
 'l15':('@l15','run',('base_sha256','parent_physical','parent_operational','prestate_Moore27','incoming_to79','incoming_state0_count','parent_gate78','conditions','checks','preparations','audit_continuation_forks','new_E1_histories')),
 'central':('@central','run',('prediction','before_report','event','trace','operations','events','operative_forks','comparison_phase_does_not_write_delta_or_clock')),
 'need':('run_need','run',('geometry','rows','local_windows','requests','diagnostic_edits','native_questions','received_information','later_physical_use','final_physical','final_operative','preparations','host_RAW_clock_writes_on_MAIN')),
 'missing':('run_need','run',('geometry','rows','local_windows','requests','diagnostic_edits','native_questions','received_information','later_physical_use','final_physical','final_operative','preparations','host_RAW_clock_writes_on_MAIN')),
}

def run_central(config,target):
 # The original run_central_comparison.py sequence, calling original sources.
 # Only the output directory and availability of unchanged4.5 differ.
 from core.entity import Entity
 from core.central_comparison import declare_comparison_channels,present_current_actual_report
 from core.comparison import observed,coordinate,plus
 target.mkdir(parents=True,exist_ok=False);spec=dict(config);history=spec.pop('history',True);report=spec.pop('report',True)
 e=declare_comparison_channels(Entity.create(**spec));e.save(target/'T0.deetsnap')
 if history:e.sense()
 else:e._advance_to(34)
 prediction=e.predict(horizon=46);e.save(target/'EMISSION.deetsnap');e.advance(prediction['target_tick']-e.tick);e.save(target/'BEFORE_REPORT.deetsnap');pre=e.observe();event=present_current_actual_report(e)if report else None;rows=[]
 for t in range(e.tick,91):
  e._advance_to(t)
  if t in(83,84,85,86,90):
   c=e.origin;rows.append({'tick':t,'observation':e.observe(),'local_context':[observed(e.world.runtime.observe(coordinate(plus(c,(x,y,z)))))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
 e.save(target/'FINAL.deetsnap');result=json.loads(json.dumps({'prediction':prediction,'before_report':pre,'event':event,'trace':rows,'operations':e.operation_calls,'events':e.events,'operative_forks':0,'comparison_phase_does_not_write_delta_or_clock':True}))
 loaded=Entity.load(target/'FINAL.deetsnap');before=e.physical_digest();equal=loaded.physical_digest()==before;e._advance_to(93);loaded._advance_to(93);result['restoration_control']={'full_physical90_equal':equal,'full_physical93_equal':e.physical_digest()==loaded.physical_digest(),'native_final90':before,'native_final93':e.physical_digest()};audit.put(target/'MEASUREMENTS.json',result);return result
def main():
 p=argparse.ArgumentParser();p.add_argument('group',choices=GROUPS);p.add_argument('--materialized',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);mat=a.materialized.resolve();owner=tempfile.TemporaryDirectory(prefix='dee-core-native-');native_temp=Path(owner.name).resolve();assert str(native_temp).isascii()
 os.environ['TEMP']=str(native_temp);os.environ['TMP']=str(native_temp);tempfile.tempdir=str(native_temp)
 identity=audit.identity();blocked=audit.restrict_reads(mat,out,native_temp);start=time.monotonic();rows=[];value={'group':a.group,'identity':identity,'native_temporary_directory':str(native_temp),'status':'RUNNING','cases':rows,'source_adapter':'Only common.identity function points to official4.5 identity; original scientific source bytes, geometry, inputs and decoders unchanged.'}
 try:
  source=mat/('cpc8/src'if a.group in('qfm','l15')else'historico/CPC7/src'if a.group in('need','missing')else'historico/CPC3/src'if a.group in('policy','native_loop','central')else'historico/CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/src'if a.group in('ordered','stream','network','capacity','longitudinal')else'historico/CPC6/src');sys.path.insert(0,str(source))
  if a.group in('need','missing'):sys.path.insert(0,str(source/'endogenous'))
  if a.group not in('policy','native_loop','central','qfm','l15'):
   import common
   common.identity=audit.identity
  module_name,function_name,keys=GROUPS[a.group]
  if a.group=='central':
   module=importlib.import_module('core.central_comparison');run=run_central
  elif a.group in('qfm','l15'):
   script=mat/('cpc8/tools/ejecutar_cantidad_forma_movil.py'if a.group=='qfm'else'cpc8/src/diagnostico_l15_causal.py');spec=importlib.util.spec_from_file_location('recovered_'+a.group,script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
   def run(config,target):
    if a.group=='qfm':module.run(config['case_id'],target)
    else:module.run(target)
    return json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf8'))
  else:
   module=importlib.import_module(module_name);run=getattr(module,function_name)
   if a.group=='missing':module.apparatus=importlib.import_module('comparison_need_v2')
  frozen=json.loads((ROOT/'configuraciones/RECUPERACION_EXTENSION_CONGELADA.json').read_text(encoding='utf8'))['groups'][a.group]
  for case in frozen:
   actual=run(case['input_configuration'],out/case['id'])
   # Expected primary data are not opened until the native trajectory ends.
   reference=mat/case['primary'];assert audit.sha(reference)==case['primary_sha256'];old=json.loads(reference.read_text(encoding='utf8'))
   projected_actual={k:actual[k]for k in keys};metadata_additions={}
   if a.group=='native_loop':
    # Later source explicitly names disabled optional post-query metadata.
    # Compare every original metadata field; retain all additions separately.
    metadata_additions={k:v for k,v in actual['metadata'].items()if k not in old['metadata']}
    projected_actual['metadata']={k:actual['metadata'][k]for k in old['metadata']}
    extra=[{'tick':new['tick'],'keys':[k for k in new if k not in prior]}for new,prior in zip(actual['trace'],old['trace'])if any(k not in prior for k in new)]
    metadata_additions['passive_observer_row_additions']=extra
    projected_actual['trace']=[{k:new[k]for k in prior}for new,prior in zip(actual['trace'],old['trace'])]
   if a.group=='ordered':
    metadata_additions['session_metadata_restore']={'current':actual['technical']['save_load_session_metadata_equal'],'historical':old['technical']['save_load_session_metadata_equal'],'scope':'Old first discovery retained a metadata-equality fault. All native state/operative comparisons remain exact; current restoration must work.'}
    projected_actual['technical']={k:v for k,v in actual['technical'].items()if k!='save_load_session_metadata_equal'}
    old['technical']={k:v for k,v in old['technical'].items()if k!='save_load_session_metadata_equal'}
   if a.group=='l15':
    # Compressed container hashes/timings/paths are I/O metadata, not DEE state.
    # Compare all captured native states, receipts and explicit interventions.
    condition_keys=('condition','parent_tick','entry_physical','parent_queue_receipts_preserved','interventions','frames','reader_receipt','actual79','alternate82','original_port134','final_receipts','final_physical','parent_unchanged_after_fork')
    project=lambda item:{k:item[k]for k in condition_keys if k in item}
    projected_actual['conditions']=[project(c)for c in actual['conditions']];old['conditions']=[project(c)for c in old['conditions']]
   differences={k:audit.compare_data(projected_actual[k],old[k],ignore=('monotonic_ns','wall_utc','path','domain_status','limits')if a.group=='central'else())for k in keys};checks={k:not v for k,v in differences.items()}
   if a.group=='central':
    allowed_annotations=('domain_status','represented_expectation_before_report','validity')
    annotations={k:[d for d in ds if d.get('missing')=='expected'and d['path'].rsplit('/',1)[-1]in allowed_annotations]for k,ds in differences.items()}
    metadata_additions['later_passive_auditor_annotations']=annotations
    differences={k:[d for d in ds if d not in annotations[k]]for k,ds in differences.items()};checks={k:not ds for k,ds in differences.items()}
   if a.group=='ordered':checks['current_saved_session_metadata_restored']=actual['technical']['save_load_session_metadata_equal']is True
   if a.group=='central':checks.update({k:v for k,v in actual['restoration_control'].items()if k.endswith('_equal')})
   statekey=None if a.group in('policy','native_loop','central','l15')else'final'if a.group in('ordered','capacity','longitudinal','qfm')else'final_physical'
   row={'id':case['id'],'checks':checks,'differences':{k:v for k,v in differences.items()if v},'later_source_metadata_additions':metadata_additions,'full_final_RAW_clocks_tick_equal':actual[statekey]==old[statekey]if statekey else None,'full_state_coverage_limit':None if statekey else'Original primary stores exact local native traces/receipts but no full-world RAW/clocks hash. No claim of historical whole-state equality.','historical_primary_sha256':case['primary_sha256'],'actual_source_sha256':audit.sha(Path(module.__file__)),'passed':all(checks.values())};rows.append(row);audit.put(out/'RECOVERY.json',value);gc.collect()
  value['status']='PASS'if all(r['passed']for r in rows)else'FAIL'
 except BaseException as e:value.update(status='ERROR',error=repr(e),traceback=traceback.format_exc())
 value.update(elapsed_seconds=time.monotonic()-start,undeclared_read_attempts=blocked,scope='Original finite CPC5/6 native preparation, controls and historical reserves on unchanged official4.5. Distinct technical recoveries, not new E1 acquisitions, generalsemanticclaims or independent scientific replications.')
 audit.put(out/'RECOVERY.json',value);print(json.dumps({'group':a.group,'status':value['status'],'seconds':value['elapsed_seconds'],'cases':len(rows)}))
 if value['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
