"""Another-process restoration before Bquery; endpoint only read AFTER execution."""
import argparse,hashlib,json,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source';shutil.copytree(a.parent_dir/'executed_source',bundle);shutil.copyfile(__file__,bundle/Path(__file__).name);sys.path.insert(0,str(bundle/'src'))
    from comunicacion.contact_social_regulated import RegulatedContactSocialE1Session
    from integracion.relational_pair import physical
    start=time.monotonic();s=RegulatedContactSocialE1Session.load(a.parent_dir/'T549.deetsnap.gz');initial=physical(s.world);before=len(s.state['contact_social_observations']);s.run_until(616);end=physical(s.world);new=s.state['contact_social_observations'][before:]
    expected=RegulatedContactSocialE1Session.load(a.parent_dir/'T616.deetsnap.gz')
    checks={'RAW_clocks_tick':end==physical(expected.world),'receipts_by_original_id':s.receipts()==expected.receipts(),'channels':sorted(s.world.runtime.channel_names)==sorted(expected.world.runtime.channel_names),'protocol_count':len(s.world.protocols)==len(expected.world.protocols),'external_operations':list(s.world.external_operations)==list(expected.world.external_operations),'native_social_queries_and_use':new==[x for x in expected.state['contact_social_observations']if x['tick']>549],'old_word616':s.view()['joint']==expected.view()['joint']}
    path=a.out/'T616.deetsnap.gz';storage=s.save(path)
    m={'schema':'CPC8R.contact_socialE1.restore.v1','case':{'id':a.out.name},'status':'PASS'if all(checks.values())else'FAIL','modality':'TECHNICAL_REPRODUCTION_NOT_SCIENTIFIC_REPLICA','preparations':0,'diagnostic_forks':0,'continuations':1,'parent':{'snapshot':str(a.parent_dir/'T549.deetsnap.gz'),'sha256':sha(a.parent_dir/'T549.deetsnap.gz'),'tick':549},'reference_after_execution':{'snapshot':str(a.parent_dir/'T616.deetsnap.gz'),'sha256':sha(a.parent_dir/'T616.deetsnap.gz')},'source_sha256':{p.relative_to(bundle).as_posix():sha(p)for p in bundle.rglob('*.py')},'initial':initial,'final':end,'checks':checks,'new_inputs_after_restore':[],'contact_social_observations_after_restore':new,'snapshot':{'path':path.name,'sha256':sha(path),'storage':storage},'elapsed_seconds':time.monotonic()-start,'full_operational_serialization_byte_equivalence':None}
    (a.out/'MEASUREMENTS.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'status':m['status'],'checks':checks}))
if __name__=='__main__':main()
