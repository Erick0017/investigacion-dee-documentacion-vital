"""Exact frozen contact-social acquisition, use and selective-message controls."""
from pathlib import Path
import argparse,gc,json,os,runpy,sys,tempfile,time,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent));import worker_core as audit
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('family',choices=('social',));p.add_argument('--materialized',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();mat=a.materialized.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);owner=tempfile.TemporaryDirectory(prefix='dee-core-native-');temp=Path(owner.name).resolve();assert str(temp).isascii();os.environ['TEMP']=str(temp);os.environ['TMP']=str(temp);tempfile.tempdir=str(temp)
 identity=audit.identity();blocked=audit.restrict_reads(mat,out,temp);start=time.monotonic();rows=[];v={'family':'social','identity':identity,'status':'RUNNING','cases':rows,'native_temporary_directory':str(temp)}
 try:
  frozen=json.loads((ROOT/'configuraciones/RECUPERACION_SOCIAL_CONGELADA.json').read_text(encoding='utf8'));cfg=out/'INPUTS.json';audit.put(cfg,{'cases':[x['case']for x in frozen['cases']]})
  for case in frozen['cases']:
   base=mat/case['frozen_source_root']
   for relative,h in case['source_sha256'].items():assert audit.sha(base/relative)==h
   script=base/'src/comunicacion/run_contact_social_regulated.py';target=out/case['id'];sys.argv=[str(script),'--config',str(cfg),'--case',case['id'],'--out',str(target)];runpy.run_path(str(script),run_name='__main__');actual=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf8'));ref=mat/case['primary'];assert audit.sha(ref)==case['primary_sha256'];old=json.loads(ref.read_text(encoding='utf8'))
   keys=('geometry','frames','windows','requests','final_physical','receipt_statuses','mode_captures','social_captures','quantity_observations','renewal_observations','initiative_captures','return_use_observations','contact_social_observations','contact_regulation_observations','host_RAW_clock_edits_on_MAIN');checks={k:not audit.compare_data(actual[k],old[k])for k in keys};rows.append({'id':case['id'],'checks':checks,'historical_primary_sha256':case['primary_sha256'],'full_final_RAW_clocks_tick_equal':actual['final_physical']==old['final_physical'],'passed':all(checks.values())});audit.put(out/'RECOVERY.json',v);gc.collect()
  parent=out/'CTS_R1_P11_NEW_CONTACT';script=mat/'cpc8/src/comunicacion/contact_social_diagnostics.py'
  for case in frozen['diagnostics']:
   target=out/case['id'];sys.argv=[str(script),'--parent-dir',str(parent),'--mode',case['mode'],'--out',str(target)];runpy.run_path(str(script),run_name='__main__');actual=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf8'));ref=mat/case['primary'];assert audit.sha(ref)==case['primary_sha256'];old=json.loads(ref.read_text(encoding='utf8'));keys=('parent_physical_before','parent_physical_after','parent_unchanged','edits','same_load_state_semantic_clock_for_content_control','new_inputs_after_fork','requests','contact_social_observations_after_fork','final_word','physical');checks={k:not audit.compare_data(actual[k],old[k])for k in keys};rows.append({'id':case['id'],'checks':checks,'full_final_RAW_clocks_tick_equal':actual['physical']==old['physical'],'historical_primary_sha256':case['primary_sha256'],'passed':all(checks.values())});audit.put(out/'RECOVERY.json',v);gc.collect()
  v['status']='PASS'if all(r['passed']for r in rows)else'FAIL'
 except BaseException as e:v.update(status='ERROR',error=repr(e),traceback=traceback.format_exc())
 v.update(elapsed_seconds=time.monotonic()-start,undeclared_read_attempts=blocked,scope='Four original finite source histories, receiver acquisition and later use; omitted source association, changed contact/history and historical reserve. Three selective formed-message diagnostic cut/sham/same-load-content controls from the freshly regenerated positive parent, which stays intact. Simple recipient B, not a second complete mind or general language. A direction change also changes routing; no arbitrary convention inferred.')
 audit.put(out/'RECOVERY.json',v);print(json.dumps({'status':v['status'],'cases':len(rows),'seconds':v['elapsed_seconds']}))
 if v['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
