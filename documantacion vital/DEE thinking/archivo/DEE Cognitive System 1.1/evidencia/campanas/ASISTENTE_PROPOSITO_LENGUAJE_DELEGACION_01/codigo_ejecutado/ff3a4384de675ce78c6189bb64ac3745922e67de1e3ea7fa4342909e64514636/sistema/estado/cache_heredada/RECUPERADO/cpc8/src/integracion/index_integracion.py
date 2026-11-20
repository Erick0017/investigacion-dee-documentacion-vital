"""Reconcile exact primary artifacts without rerunning or classifying minds."""
import hashlib,json,os
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for block in iter(lambda:f.read(1024**2),b''):h.update(block)
 return h.hexdigest()
def main():
 rows=[];errors=[];out_of_scope=[]
 for path in sorted((ROOT/'resultados/integracion').glob('*/MEASUREMENTS.json')):
  m=json.loads(path.read_text(encoding='utf8'));case=m.get('case',{});checks=[]
  if not m.get('schema'):
   out_of_scope.append({'primary':str(path.relative_to(ROOT)),'sha256':sha(path),'case_id':m.get('case_id',path.parent.name),'reason':'Different owner/schema and source-bundle convention; intentionally not interpreted as this flat-executed-source integration schema. Requires its own or the campaign-global reconciler.'});continue
  declarations={**m.get('source',{}),**m.get('source_sha256',{}),**m.get('factory_adapter',{}).get('source_sha256',{})}
  for name,expected in declarations.items():
   if not isinstance(expected,str):continue
   p=path.parent/'executed_source'/name;ok=p.is_file()and sha(p)==expected;checks.append({'kind':'executed_source','path':str(p.relative_to(ROOT)),'sha256':expected,'verified':ok})
   if not ok:errors.append({'case':case.get('id',path.parent.name),'file':str(p.relative_to(ROOT)),'expected':expected})
  for item in m.get('snapshots',[]):
   p=path.parent/item['path'];expected=item.get('sha256');ok=p.is_file()and(expected is None or sha(p)==expected);checks.append({'kind':'snapshot','path':str(p.relative_to(ROOT)),'sha256':expected,'verified':ok})
   if not ok:errors.append({'case':case.get('id',path.parent.name),'file':str(p.relative_to(ROOT)),'expected':expected})
  req=m.get('requests',[]);counts=Counter(r['receipt']['status']for r in req)
  rows.append({'case_id':case.get('id',path.parent.name),'schema':m.get('schema'),'status':m.get('status'),'primary':str(path.relative_to(ROOT)),'sha256':sha(path),'preparations':m.get('preparations',0),'continuations':m.get('continuations',0),'diagnostic_forks':m.get('diagnostic_forks',0),'parent':m.get('parent'),'last_complete_tick':m.get('last_complete_tick',m.get('final_physical',{}).get('tick')),'requests_including_inherited':len(req),'admission_including_inherited':dict(counts),'source_and_snapshot_checks':checks,'main_edits_reported':m.get('host_RAW_clock_edits_on_MAIN',m.get('host_RAW_clock_writes_on_MAIN',[]))})
 result={'schema':'CPC8R.integration.artifact_index.v1','script_sha256':sha(Path(__file__)),'scope':'Only owned integration primaries with an explicit schema. Different-owner unversioned schemas are listed as out_of_scope, not silently dropped. Repetitions, continuations, forks, inherited requests and ticks are not independent preparations. This index validates exact artifacts and counts, not semantic mastery.','out_of_scope':out_of_scope,'primary_count':len(rows),'counts':{k:sum(r[k]for r in rows)for k in('preparations','continuations','diagnostic_forks')},'statuses':dict(Counter(r['status']for r in rows)),'integrity_errors':errors,'rows':rows}
 out=ROOT/'resultados/integracion/INDEX.json';temp=out.with_name(out.name+'.pending');temp.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,out);print(json.dumps({'primaries':len(rows),'counts':result['counts'],'errors':len(errors)}))
if __name__=='__main__':main()
