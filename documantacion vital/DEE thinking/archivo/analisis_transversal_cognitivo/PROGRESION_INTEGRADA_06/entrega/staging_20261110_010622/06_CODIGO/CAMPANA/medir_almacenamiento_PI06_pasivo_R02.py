"""Two bounded logical-size readings: PI06 and only new PI06 RP items.

No old principal/project-wide inventory, hashes, Native imports or file changes.
One fresh output in PI06/control is the only write; the output itself is noted
outside the measured totals. Hardlinks count as logical files, not free space.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os,stat,time
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
def roots():
 result=[('P6',P)]
 for folder in('codigo_preservado','materiales','recetas','verificaciones','EJECUCIONES','diagnosticos'):
  base=RP/folder
  if not base.is_dir():continue
  with os.scandir(base)as entries:
   for e in entries:
    if e.name.upper().startswith('PI06_')or 'PI06_'in e.name.upper():result.append(('RP/'+folder+'/'+e.name,Path(e.path)))
 return result
def scan():
 start=datetime.now(timezone.utc).isoformat();files={};errors=[];links=[];summaries=[];worlds=[]
 for tag,root in roots():
  count=0;size=0;stack=[root]
  while stack:
   current=stack.pop()
   try:
    info=current.stat(follow_symlinks=False)
    if stat.S_ISLNK(info.st_mode)or getattr(info,'st_file_attributes',0)&1024:links.append(str(current));continue
    if stat.S_ISDIR(info.st_mode):
     with os.scandir(current)as entries:
      for entry in entries:stack.append(Path(entry.path))
    elif stat.S_ISREG(info.st_mode):
     key=str(current.absolute()).casefold();files[key]=(int(info.st_size),int(info.st_mtime_ns),tag);size+=info.st_size;count+=1
     if current.name=='VIDA.json'and current.parent.parent.name=='vidas'and(current.is_relative_to(P/'estados')or current.is_relative_to(RP/'diagnosticos')):worlds.append(str(current.parent))
    else:errors.append({'path':str(current),'error':'Nonregular item excluded'})
   except OSError as exc:errors.append({'path':str(current),'error':type(exc).__name__+': '+str(exc)})
  summaries.append({'scope':tag,'root':str(root),'logical_bytes':size,'files':count})
 return {'started_utc':start,'ended_utc':datetime.now(timezone.utc).isoformat(),'files_internal':files,'roots':summaries,
  'logical_bytes':sum(v[0]for v in files.values()),'files_count':len(files),'errors':errors,'link_exclusions':links,'diagnostic_world_directories':worlds}
def main(a):
 output=a.salida.resolve(strict=False)
 if not output.is_relative_to((P/'control').resolve())or output.exists():raise ValueError('Only fresh P6/control output')
 for q in(output,*output.parents):
  if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked audit output')
 t=time.monotonic();one=scan();two=scan();f1=one.pop('files_internal');f2=two.pop('files_internal');keys=set(f1)|set(f2)
 changed=[k for k in keys if f1.get(k)!=f2.get(k)];union_max=sum(max(f1.get(k,(0,0,''))[0],f2.get(k,(0,0,''))[0])for k in keys)
 record=json.loads((P/'REGISTRO_CAMPANA.json').read_text('utf-8-sig'));limit=record['budget']['new_logical_storage_ceiling_bytes']
 proof={'schema':'DEE.PI06.bounded_two_pass_logical_storage.R02_operational_world_scope','recorded_utc':datetime.now(timezone.utc).isoformat(),
  'scope':'PI06 entire campaign plus only RP entries whose names contain PI06_. Old product principal, historical states and other RP entries excluded.',
  'passes':[one,two],'fixed_limit_bytes':limit,'observed_union_max_logical_bytes':union_max,'observed_headroom_bytes':limit-union_max,
  'concurrent_changed_or_new_or_vanished_files':len(changed),'changed_examples':changed[:30],
  'two_passes_exactly_stable':not changed and not(one['errors']or two['errors']or one['link_exclusions']or two['link_exclusions']),
  'complete_size_read_within_declared_scope':not(one['errors']or two['errors']or one['link_exclusions']or two['link_exclusions']),
  'projected_additional_bytes':a.proyectar_bytes,'projected_total_observed_plus_declared':union_max+a.proyectar_bytes,
  'projection_fits_fixed_limit':union_max+a.proyectar_bytes<=limit,'measurement_duration_seconds':time.monotonic()-t,
  'Native_executed':False,'writes':'This fresh proof only; its eventual bytes are not included in the preceding readings.',
  'not_a_measurement_of_freed_or_physical_disk_bytes':True,'diagnostic_world_count_excludes_control_Fake_fixtures':True,
  'R01_count_correction':'R01 logical-byte measurement remains valid; its four VIDA-like paths included one explicit control/FAKE_VACIOS fixture. That was not a Native world or independent organism.',
  'not_a_future_size_guarantee':'Concurrent Native activity and future writes require margin; observations do not authorize exceeding the frozen limit.'}
 with output.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(output),'proof_bytes':output.stat().st_size,'observed_bytes':union_max,'headroom_bytes':limit-union_max,
  'stable':proof['two_passes_exactly_stable'],'complete':proof['complete_size_read_within_declared_scope'],'changed_files':len(changed),
  'errors':[len(one['errors']),len(two['errors'])],'links':[len(one['link_exclusions']),len(two['link_exclusions'])],
  'diagnostic_worlds_observed':len(set(one['diagnostic_world_directories'])|set(two['diagnostic_world_directories'])),'Native_executed':False},ensure_ascii=False,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--salida',type=Path,required=True);ap.add_argument('--proyectar-bytes',type=int,default=0);a=ap.parse_args()
 if a.proyectar_bytes<0:raise ValueError('No negative future allocation')
 main(a)
