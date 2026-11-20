"""Repair derived input indexing externally; never rewrite primary measurements."""
import hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rows=[]
 for path in sorted((ROOT/'resultados/integracion').glob('*/MEASUREMENTS.json')):
  m=json.loads(path.read_text(encoding='utf8'))
  if 'new_requests'not in m or 'parent'not in m:continue
  parent=ROOT/m['parent']['path'];parent_m=parent.parent/'MEASUREMENTS.json';pm=json.loads(parent_m.read_text(encoding='utf8'));old={r['id']for r in pm['requests']};new=[r for r in m['requests']if r['id']not in old]
  rows.append({'case_id':m['case']['id'],'primary':str(path.relative_to(ROOT)),'primary_sha256':sha(path),'parent_measurements':str(parent_m.relative_to(ROOT)),'parent_measurements_sha256':sha(parent_m),'formula':'child.requests filtered by id not in parent.requests; native receipt IDs are unique within this shared Runtime lineage','corrected_new_requests':new,'original_derived_field_equal':m['new_requests']==new,'original_derived_field_preserved':True})
 out=ROOT/'resultados/integracion/DERIVED_REQUESTS_RECONCILED.json';value={'schema':'CPC8R.input_delta.reconciliation.v1','script_sha256':sha(Path(__file__)),'issue':'Old derived new_requests used list-tail slicing, but receipt presentation concatenates base+mode; appending base requests moves mode rows. Full requests/native receipts and physical trajectories were already correct. Existing primary files and their exact executed source remain unchanged. Future runner versions filter unique IDs.','affected_cases':sum(not r['original_derived_field_equal']for r in rows),'rows':rows};temp=out.with_name(out.name+'.pending');temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,out);print(json.dumps({'cases':len(rows),'affected':value['affected_cases']}))
if __name__=='__main__':main()
