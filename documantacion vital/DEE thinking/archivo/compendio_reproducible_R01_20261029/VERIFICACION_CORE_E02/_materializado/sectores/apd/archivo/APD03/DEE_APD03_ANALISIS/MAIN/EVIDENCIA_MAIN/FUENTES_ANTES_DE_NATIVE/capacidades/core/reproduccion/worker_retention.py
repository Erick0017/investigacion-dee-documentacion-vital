"""Original CPC6 diagnostics on declared inherited parents, not new E1s."""
from pathlib import Path
import argparse,gc,importlib,json,os,sys,tempfile,time,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent));import worker_core as audit
ROOT=Path(__file__).resolve().parents[1]
KEYS={
 'early':('intervention','rows','requests','query_already_queued_in_parent','response97','unmodified_parent_response97','response97_identical_to_parent','MAIN_physical_before','MAIN_physical_after','MAIN_operational_unchanged','final_physical','final_operational','postfork_added_inputs'),
 'word':('intervention','rows','comparison162','new_participant_inputs_after_fork','all_parent_requests','MAIN_physical_before','MAIN_physical_after','MAIN_operational_unchanged','final_physical','final_operational'),
 'late':('selected_access','geometry','query_tick','query_receipt','rows','requests','parent_operational_before','physical_before','final_physical','final_operational','original_parent_snapshot_unchanged','external_RAW_clock_writes','R1_reteaching','prepared_worlds','continued_boundaries')}
def main():
 p=argparse.ArgumentParser();p.add_argument('group',choices=KEYS);p.add_argument('--materialized',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();mat=a.materialized.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
 owner=tempfile.TemporaryDirectory(prefix='dee-core-native-');temp=Path(owner.name).resolve();assert str(temp).isascii();os.environ['TEMP']=str(temp);os.environ['TMP']=str(temp);tempfile.tempdir=str(temp)
 identity=audit.identity();blocked=audit.restrict_reads(mat,out,temp);started=time.monotonic();rows=[];v={'group':a.group,'identity':identity,'status':'RUNNING','native_temporary_directory':str(temp),'cases':rows,'modality':'Declared historical snapshot parents restored as exact controlled diagnostic continuations, zero new E1 preparations. All cuts remain in forks and never return to parent.'}
 try:
  source=mat/'historico/CPC6/src';sys.path.insert(0,str(source));import common;common.identity=audit.identity
  module=importlib.import_module({'early':'consolidation_controls','word':'word_bus_controls','late':'late_access'}[a.group]);frozen=json.loads((ROOT/'configuraciones/RECUPERACION_RETENCION_CONGELADA.json').read_text(encoding='utf8'))['groups'][a.group];cfg=frozen['configuration']
  for case in frozen['cases']:
   target=out/case['id']
   if a.group=='early':actual=module.run(case['parent'],case['mechanism'],case['arm'],cfg,target)
   elif a.group=='word':actual=module.run(case['case'],cfg,target)
   else:actual=module.run(case['parent'],case['arm'],cfg,case['selected'],target)
   ref=mat/case['primary'];assert audit.sha(ref)==case['primary_sha256'];old=json.loads(ref.read_text(encoding='utf8'));diffs={k:audit.compare_data(actual[k],old[k])for k in KEYS[a.group]};checks={k:not d for k,d in diffs.items()};rows.append({'id':case['id'],'checks':checks,'differences':{k:d for k,d in diffs.items()if d},'full_final_RAW_clocks_tick_equal':actual['final_physical']==old['final_physical'],'historical_primary_sha256':case['primary_sha256'],'passed':all(checks.values())});audit.put(out/'RECOVERY.json',v);gc.collect()
  v['status']='PASS'if all(r['passed']for r in rows)else'FAIL'
 except BaseException as e:v.update(status='ERROR',error=repr(e),traceback=traceback.format_exc())
 v.update(elapsed_seconds=time.monotonic()-started,undeclared_read_attempts=blocked,scope='Original early memory/carrier interventions, late reader/memory dissociation and alternate original-history access at110/111 with no-query controls. Prepared/observed access, not autonomous selection or free memory relocation.')
 audit.put(out/'RECOVERY.json',v);print(json.dumps({'group':a.group,'status':v['status'],'cases':len(rows),'seconds':v['elapsed_seconds']}))
 if v['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
