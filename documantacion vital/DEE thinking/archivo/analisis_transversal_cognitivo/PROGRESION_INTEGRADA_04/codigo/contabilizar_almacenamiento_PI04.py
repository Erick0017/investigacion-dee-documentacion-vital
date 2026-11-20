"""Bounded campaign preservation accounting. Not a historical inventory or physical free-space claim."""
from pathlib import Path
import datetime,json,os,shutil
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
def main():
 roots=[P]
 for parent in ('materiales','codigo_preservado','observadores'):
  d=RP/parent
  if not d.exists():continue
  roots.extend(p for p in d.iterdir()if p.is_dir()and (p.name.startswith(('PI03_PI04','PI04'))or(parent=='observadores'and p.name=='F1_PI04')))
 rows=[]
 for root in sorted(set(roots)):
  count=total=0;skipped=[]
  for folder,dirs,files in os.walk(root,followlinks=False):
   base=Path(folder)
   for name in list(dirs):
    p=base/name
    if p.is_symlink()or getattr(p.lstat(),'st_file_attributes',0)&1024:dirs.remove(name);skipped.append(str(p))
   for name in files:
    p=base/name
    if p.is_symlink()or getattr(p.lstat(),'st_file_attributes',0)&1024:skipped.append(str(p));continue
    count+=1;total+=p.stat().st_size
  rows.append({'root':str(root),'files':count,'logical_bytes':total,'links_not_followed':skipped})
 value={'schema':'DEE.PI04.bounded_storage_accounting.v1','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'accounted_bytes_before':sum(r['logical_bytes']for r in rows),'scope_roots':[r['root']for r in rows],'roots':rows,'limit_bytes':8000000000,'actual_disk_free_bytes':shutil.disk_usage(P).free,'scope':'Only the new PI04 campaign and its newly preserved reusable materials/capsules/tools. Logical file sizes conservatively count hardlinked content; this is not a disk-space-recovered measurement. Existing PI03 base/materials and official engine are not new campaign allocation. Live files may grow; import gate adds a separate conservative estimate.'}
 out=P/'control'/('ALMACENAMIENTO_ANTES_INCORPORACION_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')+'.json')
 with out.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2)
 print(json.dumps({'proof':str(out),'accounted_bytes_before':value['accounted_bytes_before'],'limit_bytes':8000000000,'free':value['actual_disk_free_bytes']}))
if __name__=='__main__':main()
