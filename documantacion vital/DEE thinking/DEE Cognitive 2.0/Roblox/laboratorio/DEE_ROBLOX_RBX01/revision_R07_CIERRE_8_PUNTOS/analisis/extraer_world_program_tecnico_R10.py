"""Pure closed-file analysis projection, never a restorable World backup."""
import argparse, hashlib, json
from pathlib import Path
FIELDS=('checkpoint_id','body_pose','native_life_id','native_tick','S','executed_actions','rng','motor','world_id','boundary','events')
def sha(b):return hashlib.sha256(b).hexdigest()
def main(a):
    if a.output.exists()or not a.output.parent.is_dir():raise ValueError('Fresh output with existing parent required')
    rb=a.closed_result.read_bytes();result=json.loads(rb)
    if result.get('owner_closed')is not True or result.get('new_Native_ticks')!=0 or result.get('Native_engine_loaded')is not False:raise ValueError('Closed no-Native technical result required')
    raw=a.source.read_bytes()
    if len(raw)>8_000_000 or sha(raw)!=result['world_sha256']:raise ValueError('Closed source World pin mismatch')
    world=json.loads(raw)
    if world['boundary']['phase']!='BOUNDARY' or world['S']['completedCycles']!=46:raise ValueError('Exact closed technical boundary required')
    extracted={k:world[k]for k in FIELDS};extracted['schema']='DEE.R07.ProgramTechnicalAnalysisExtract.R10.v1'
    extracted['derived_analysis_extract']={'original_source':str(a.source.resolve()),'original_bytes':len(raw),'original_sha256':sha(raw),'original_schema':world.get('schema'),'closed_result_source':str(a.closed_result.resolve()),'closed_result_sha256':sha(rb),'selected_fields':FIELDS,'omitted_fields':sorted(set(world)-set(FIELDS)),'field_sha256':{k:sha(json.dumps(world[k],sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())for k in FIELDS},'full_S_boundary_body_pose_copied':True,'full_world_backup':False,'restore_or_rollback_claim':False,'scope':'Faithful JSON field extraction only; no geometry/controller/pose_trace or runtime/native service backup. Exact original full World remains local.'}
    if a.source.read_bytes()!=raw or a.closed_result.read_bytes()!=rb:raise ValueError('Closed inputs changed')
    a.output.write_text(json.dumps(extracted,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(a.output),'bytes':a.output.stat().st_size,'sha256':sha(a.output.read_bytes()),'source_sha256':sha(raw),'full_world_backup':False,'Native_calls':0}))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--closed-result',type=Path,required=True);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
