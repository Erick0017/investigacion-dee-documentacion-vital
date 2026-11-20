"""Compare exact pre-supply and saved failed future; no Native imports/actions."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];S=P/'estados/candidato/sistema';C=P.parents[2]/'DEE Cognitive 2.0';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_CAND_01'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def differences(a,b,path=''):
 if type(a)is not type(b):return[path]
 if isinstance(a,dict):
  result=[]
  for k in sorted(set(a)|set(b)):
   result+=([path+'/'+k]if k not in a or k not in b else differences(a[k],b[k],path+'/'+k))
  return result
 if isinstance(a,list):
  result=[]
  for i in range(max(len(a),len(b))):result+=([path+'/'+str(i)]if i>=len(a)or i>=len(b)else differences(a[i],b[i],path+'/'+str(i)))
  return result
 return[]if a==b else[path]
def main(a):
 out=a.salida.resolve()
 if out.exists()or not out.is_relative_to((P/'control').resolve()):raise ValueError('New P7/control proof only')
 primary=P/'ensayos/PI07_CIERRE_CONJUNTO_R03state_pre0.json';row=read(primary);before_record=json.loads(row['result'])['committed_snapshot'];card=read(S/'estado/vidas'/LIFE/'VIDA.json');left=S/before_record['snapshot'];right=S/card['snapshot'];before={str(p):sha(p)for p in(primary,left,right)}
 if before[str(left)]!=before_record['snapshot_sha256']or before[str(right)]!=card['snapshot_sha256']:raise ValueError('Frozen snapshot identity mismatch')
 spec=importlib.util.spec_from_file_location('PI07_failure_preservation_parser_only',C/'reproducibilidad/observador_pasivo.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);x=m.snapshot_view(left);y=m.snapshot_view(right)
 fields={k:x[k]==y[k]for k in('physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase')};changes={}
 for key in sorted(set(x['metadata'])|set(y['metadata'])):
  v=x['metadata'].get(key);w=y['metadata'].get(key)
  if v==w:continue
  try:paths=differences(None if v is None else json.loads(v),None if w is None else json.loads(w))
  except ValueError:paths=['encoded_literal']
  changes[key]={'changed_leaf_paths':paths,'old_literal_sha256':None if v is None else hashlib.sha256(v.encode()).hexdigest(),'new_literal_sha256':None if w is None else hashlib.sha256(w.encode()).hexdigest()}
 key='DEE.Cognitive.PI04.C2C.coordination.R01';old=json.loads(x['metadata'][key]);new=json.loads(y['metadata'][key]);invariants={k:old.get(k)==new.get(k)for k in('rows','ordinal','arm','life_id','ready','pending','uncertain','halted_reason')};history='DEE.Cognitive.PI05.C2C.explicit_environment30.R01';r3='DEE.Cognitive.PI07.regulation.environment.R03'
 result={'schema':'DEE.PI07.failed34.pre_supply_vs_preserved_future.v1','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'Native_imported_or_executed':False,'pre_supply_snapshot':{'path':str(left),'sha256':sha(left)},'saved_failed_snapshot':{'path':str(right),'sha256':sha(right)},'full_Native_field_equalities':fields,'all_Native_fields_equal':all(fields.values()),'C2C_history_invariants':invariants,'old_C2C_protocol_sha256':old['protocol_sha256'],'new_C2C_protocol_sha256':new['protocol_sha256'],'inherited_environment30_metadata_literal_unchanged':x['metadata'][history]==y['metadata'][history],'R03_metadata_literal_unchanged':x['metadata'][r3]==y['metadata'][r3],'metadata_changes':changes,'sources_unchanged_during_read':all(sha(Path(p))==digest for p,digest in before.items()),'interpretation':'Checkpoint commits the failed Native snapshot/card before operational_dependencies raises. The failed34 extension is saved readyFalse/uncertainTrue, not lost RAM or an old30snapshot. Native causal landscape/inputs are unchanged; external supplies/protocol/diary changed. This is a preserved blocked operational future, not an acquired improvement or a successful material continuation.','source_code_order':'app/servicio_persistente.py checkpoint: Store.commit; marker unlink; dirtyFalse; then operational_dependencies in returned object. Do not treat checkpoint_error as proof no snapshot was saved.'}
 with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(out),'sha256':sha(out),'Native_equalities':fields,'C2C_invariants':invariants,'old_protocol':old['protocol_sha256'],'new_protocol':new['protocol_sha256'],'R03_literal_unchanged':result['R03_metadata_literal_unchanged']}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--salida',type=Path,required=True);main(ap.parse_args())
