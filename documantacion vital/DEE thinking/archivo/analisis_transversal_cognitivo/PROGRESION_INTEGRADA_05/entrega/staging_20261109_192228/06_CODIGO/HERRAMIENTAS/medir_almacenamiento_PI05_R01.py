"""Point-in-time logical storage of PI05 only; no Native or old-corpus census."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,re
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
LIMIT=6_000_000_000
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def measure(root):
 root=Path(root);stack=[root];count=0;size=0;links=[];errors=[];largest=[]
 while stack:
  current=stack.pop()
  try:
   if current.is_file():items=[current]
   else:
    with os.scandir(current)as ds:items=[Path(e.path)for e in ds]
   for f in items:
    try:
     s=f.lstat()
     if f.is_symlink()or getattr(s,'st_file_attributes',0)&1024:links.append(str(f));continue
     if f.is_dir():stack.append(f)
     elif f.is_file():count+=1;size+=s.st_size;largest.append((s.st_size,str(f)))
    except OSError as e:errors.append({'path':str(f),'type':type(e).__name__,'message':str(e)})
  except OSError as e:errors.append({'path':str(current),'type':type(e).__name__,'message':str(e)})
 return {'root':str(root),'files':count,'logical_bytes':size,'largest_files':[{'bytes':n,'path':p}for n,p in sorted(largest,reverse=True)[:5]],'links_not_followed':links,'stat_errors':errors}
def selected_roots():
 cfg=json.loads((RP/'RECURSOS.json').read_text(encoding='utf-8-sig'));roots=[P]
 for family in('pairs','code_capsules'):
  for k,v in cfg.get(family,{}).items():
   if 'PI05'in k:
    q=(C/v['product_relative']).resolve(strict=True)
    if not q.is_relative_to(RP.resolve()):raise ValueError('New PI05 resource outside reproducibility store')
    roots.append(q)
 for folder in('materiales','codigo_preservado','recetas','verificaciones'):
  q=RP/folder
  if q.exists():roots.extend(x for x in q.iterdir()if 'PI05'in x.name.upper())
 # Entire tiny shared record files are conservatively counted, rather than
 # pretend their unknown previous size was all newly allocated.
 roots.extend(RP/n for n in('RECURSOS.json','LEER_PRIMERO.md'))
 target='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
 for name in('vidas','servicios_persistentes','servicios_locales'):
  q=C/'sistema/estado'/name/target
  if q.exists():roots.append(q)
 checkpoint=C/'sistema/estado/checkpoints'
 if checkpoint.exists():roots.extend(x for x in checkpoint.iterdir()if x.is_file()and x.name.startswith(target+'.'))
 unique=[]
 for q in roots:
  q=q.resolve(strict=True)
  if not any(q==x or q.is_relative_to(x)for x in unique):unique.append(q)
 return unique
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--salida',default='ALMACENAMIENTO_NUEVO_PI05_MEDIDO_R01.json');args=ap.parse_args()
 if not re.fullmatch(r'ALMACENAMIENTO_NUEVO_PI05_[A-Za-z0-9_]+\.json',args.salida):raise ValueError('Fresh fixed PI05 control basename only')
 out=P/'control'/args.salida
 if out.exists():raise FileExistsError('Prior measurement preserved; create a new explicitly versioned proof')
 roots=selected_roots();start=now();first=[measure(x)for x in roots];middle=now();second=[measure(x)for x in roots];end=now()
 a=sum(x['logical_bytes']for x in first);b=sum(x['logical_bytes']for x in second);current=max(a,b)
 planned={'diagnostic_B4_one_complete_clone':237_000_000,'postfault_recovery_four_complete_clones':948_000_000,'order_phase_two_complete_clones':474_000_000,'final_stable_pair':240_000_000,'product_operational_import':240_000_000}
 proof={'schema':'DEE.PI05.scoped_new_logical_storage_measurement.v1','Native_ticks':0,'no_files_moved_deleted_or_original_modified':True,'start_utc':start,'between_scans_utc':middle,'end_utc':end,'unit':'decimal bytes, sum of file logical lengths, each separate copy counts; not allocated disk or recovered free space','scope':'Only new P5 campaign tree plus RECURSOS PI05 pair/capsule, PI05 recipe/verification trees and entire tiny shared RP registry/readme as conservative bound. No historical inventory.','first_scan':first,'second_scan':second,'first_total_bytes':a,'second_total_bytes':b,'point_in_time_conservative_max_bytes':current,'limit_bytes':LIMIT,'headroom_from_measured_max_bytes':LIMIT-current,'concurrent_change_between_samples_bytes':b-a,'planned_additions_parent_estimates_bytes':planned,'planned_total_bytes':sum(planned.values()),'projected_total_if_all_estimates_hold_bytes':current+sum(planned.values()),'projected_headroom_bytes':LIMIT-current-sum(planned.values()),'limits':'Samples while another owned process may write: not peak-memory/disk guarantee. Recheck before every large copy. Shared registry/readme full lengths overcount their new contribution. This proof file itself is written after measurements.','bounded_recommendation':'Export final full pair directly to its stable RP destination through existing closed export contract if supported; otherwise preserve one source export and relocate it only after full hash/member validation, avoiding a second stable pair copy. Never substitute snapshots for whole operational pairs, delete unique futures, or purge pending queues.'}
 out.write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'measured_bytes':current,'headroom_bytes':LIMIT-current,'planned_bytes':sum(planned.values()),'projected_headroom_bytes':LIMIT-current-sum(planned.values()),'errors':sum(len(x['stat_errors'])for x in second),'concurrent_change_bytes':b-a},ensure_ascii=False))
