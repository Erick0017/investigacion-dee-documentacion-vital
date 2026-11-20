"""Finite faithful extracts of two closed non-Native model Worlds; no restore/backup claim."""
import argparse,hashlib,json
from pathlib import Path
F=('checkpoint_id','body_pose','native_life_id','native_tick','S','executed_actions','rng','motor','world_id','boundary','events','physical','scenario_sha256')
def h(b):return hashlib.sha256(b).hexdigest()
def run(spec):
 out=[]
 for p in spec['parts']:
  source=Path(p['world']);rp=Path(p['result']);dst=Path(p['output']);raw=source.read_bytes();rb=rp.read_bytes();r=json.loads(rb);w=json.loads(raw)
  if dst.exists()or not dst.parent.is_dir():raise ValueError('Fresh output required')
  if r.get('owner_closed')is not True or r.get('new_Native_ticks')!=0 or r.get('Native_engine_loaded')is not False:raise ValueError('Closed non-Native part required')
  if h(raw)!=r['world_sha256']or w['boundary']['phase']!='BOUNDARY'or w['S']['completedCycles']!=r['global_completed']:raise ValueError('Closed World pin/boundary')
  d={k:w[k]for k in F if k in w};d['schema']='DEE.R07.ModelWorld.AnalysisExtract.Final.v1'
  d['derived_analysis_extract']={'original_source':str(source.resolve()),'original_bytes':len(raw),'original_sha256':h(raw),'closed_result_sha256':h(rb),'original_schema':w.get('schema'),'selected_fields':list(d),'omitted_fields':sorted(set(w)-set(F)),'S_boundary_body_pose_physical_copied_complete':True,'full_World_backup':False,'rollback':False,'scope':'Exact selected JSON fields, not controller/pose_trace/runtime/native service backup.'}
  if source.read_bytes()!=raw or rp.read_bytes()!=rb:raise ValueError('Inputs changed')
  dst.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');out.append({'output':str(dst),'bytes':dst.stat().st_size,'sha256':h(dst.read_bytes()),'source_sha256':h(raw)})
 return out
if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--inputs',type=Path,required=True);x=a.parse_args();print(json.dumps(run(json.loads(x.inputs.read_text('utf-8-sig')))))
