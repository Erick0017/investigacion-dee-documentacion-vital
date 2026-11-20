"""Recover exact first-CPC8 N131 social/retention/selective-update histories."""
from pathlib import Path
import argparse,gc,json,os,runpy,sys,tempfile,time,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent));import worker_core as audit
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('family',choices=('initial_cpc8',));p.add_argument('--materialized',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();mat=a.materialized.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);owner=tempfile.TemporaryDirectory(prefix='dee-core-native-');temp=Path(owner.name).resolve();assert str(temp).isascii();os.environ['TEMP']=str(temp);os.environ['TMP']=str(temp);tempfile.tempdir=str(temp);identity=audit.identity();blocked=audit.restrict_reads(mat,out,temp);start=time.monotonic();v={'family':'initial_cpc8','identity':identity,'status':'RUNNING','cases':[],'native_temporary_directory':str(temp)}
 try:
  frozen=json.loads((ROOT/'configuraciones/CPC8_INICIAL_CONGELADO.json').read_text(encoding='utf8'));baseline_import_paths=list(sys.path)
  for case in frozen['cases']:
   base=mat/case['frozen_source_root']
   for relative,h in case['source_sha256'].items():
    path=base/('ejecutar_social.py'if relative=='ejecutar_social.py'else'src/'+relative);assert audit.sha(path)==h,(relative,h)
   for name in list(sys.modules):
    if name=='integracion'or name.startswith('integracion.')or name=='comunicacion'or name.startswith('comunicacion.'):del sys.modules[name]
   sys.path[:]=baseline_import_paths
   config=out/(case['id']+'_INPUT.json');audit.put(config,{'cases':[case['case']]});script=base/'ejecutar_social.py';namespace=runpy.run_path(str(script),run_name='core_initial_frozen_runner');main_func=namespace['main']
   # The archived runner was copied from src/comunicacion into a frozen bundle.
   # Correct only its documented file-root lookup, never its physical operations.
   main_func.__globals__['ROOT']=base;target=out/'resultados/semantica'/case['id'];sys.argv=[str(script),'--config',str(config),'--case',case['id'],'--out',str(target)];main_func();actual=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf8'));ref=mat/case['primary'];assert audit.sha(ref)==case['primary_sha256'];old=json.loads(ref.read_text(encoding='utf8'));keys=('case','executed_source','frames','geometry','final_physical','requests','social_captures','native_readouts','final_tick','observed_counts','coverage','host_RAW_clock_edits_on_MAIN');diff={k:audit.compare_data(actual[k],old[k])for k in keys};checks={k:not d for k,d in diff.items()};v['cases'].append({'id':case['id'],'checks':checks,'differences':{k:d for k,d in diff.items()if d},'full_final_RAW_clocks_tick_equal':actual['final_physical']==old['final_physical'],'source_archive_sha256':frozen['source_archive_sha256'],'primary_sha256':case['primary_sha256'],'passed':all(checks.values())});audit.put(out/'RECOVERY.json',v);gc.collect()
  for stage in frozen['continuity']['stages']:
   base=mat/stage['frozen_source_root'];scriptname='longitudinal_native.py'if stage['kind']=='learn'else'longitudinal_right_read.py'
   for relative,h in stage['source_sha256'].items():assert audit.sha(base/relative)==h
   for name in list(sys.modules):
    if name=='integracion'or name.startswith('integracion.')or name=='comunicacion'or name.startswith('comunicacion.'):del sys.modules[name]
   sys.path[:]=baseline_import_paths;source=frozen['continuity']['configurations'][stage['kind']];original_config=mat/source['logical'];assert audit.sha(original_config)==source['sha256'];configuration=json.loads(original_config.read_text(encoding='utf8'))
   # Container identity is rebound to the newly regenerated exact physical
   # parent, never to a transplanted historical snapshot. Input ticks, doses,
   # windows, decoders and all scientific source bytes remain unchanged.
   if stage['kind']=='learn':
    prior=configuration['parent_sha256'];configuration['parent_sha256']=audit.sha(out/configuration['parent_snapshot'])
   else:
    selected=next(c for c in configuration['cases']if c['id']==stage['id']);prior=selected['parent_sha256'];selected['parent_sha256']=audit.sha(out/selected['parent'])
   config=out/(stage['id']+'_INPUT.json');audit.put(config,configuration);script=base/scriptname;ns=runpy.run_path(str(script),run_name='core_first_CPC8_continuation');func=ns['main'];func.__globals__['ROOT']=out;target=out/'resultados/integracion'/stage['id'];sys.argv=[str(script),'--config',str(config),'--case-id',stage['id'],'--out',str(target)];func();actual=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf8'));reference=mat/stage['primary'];assert audit.sha(reference)==stage['primary_sha256'];old=json.loads(reference.read_text(encoding='utf8'))
   keys=('frames','geometry','final_physical','requests','new_requests','executed_source','parent_file_preserved','host_RAW_clock_writes_on_MAIN','new_interfaces')
   keys+=('new_inputs','new_reads','retention','calculations','coverage')if stage['kind']=='learn'else('query_contract','native_readout','new_receipt_statuses','explicit_query_input','explicit_query_receipt_id')
   diffs={k:audit.compare_data(actual[k],old[k])for k in keys};checks={k:not d for k,d in diffs.items()};checks['parent_physical_exact']=actual['parent']['physical']==old['parent']['physical'];checks['case_inputs_exact']={k:w for k,w in actual['case'].items()if k!='parent_sha256'}=={k:w for k,w in old['case'].items()if k!='parent_sha256'}
   if stage['kind']=='read':
    expected={k:w for k,w in old['retention1051'].items()if k!='source_sha256'};observed={k:w for k,w in actual['retention1051'].items()if k!='source_sha256'};checks['retention1051']=not audit.compare_data(observed,expected)
   v['cases'].append({'id':stage['id'],'type':'continuation_of_regenerated_SOCI21_not_new_individual','checks':checks,'differences':{k:d for k,d in diffs.items()if d},'full_final_RAW_clocks_tick_equal':actual['final_physical']==old['final_physical'],'historical_parent_container_sha256':prior,'parent_container_rebound_reason':'Only paths/container byte identity of freshly regenerated physically identical parent; no input/decoder/state modification','primary_sha256':stage['primary_sha256'],'passed':all(checks.values())});audit.put(out/'RECOVERY.json',v);gc.collect()
  v['status']='PASS'if all(r['passed']for r in v['cases'])else'FAIL'
 except BaseException as e:v.update(status='ERROR',error=repr(e),traceback=traceback.format_exc())
 v.update(elapsed_seconds=time.monotonic()-start,undeclared_read_attempts=blocked,scope='Four original first-CPC8 N131 histories, including SOC_I21 selective L01 update after65-form/social acquisition, same-dose offpath revision, unpaired source, and reserved opposite social history. The freshly regenerated SOC_I21 then continues690→1051→1182 with new RIGHT acquisition and63/63 previously accessible relations retained; omitted-cue/unpaired controls are separate continuations. Not the N67 MCTS or CPC9 E1. Runner path roots and parent container identities are adapted explicitly; all scientific source bytes, inputs and physical comparisons remain exact.')
 audit.put(out/'RECOVERY.json',v);print(json.dumps({'status':v['status'],'cases':len(v['cases']),'seconds':v['elapsed_seconds']}));return 0 if v['status']=='PASS'else 1
if __name__=='__main__':raise SystemExit(main())
