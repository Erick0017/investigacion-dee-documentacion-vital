"""Scoped metadata-only logical-byte count. Does not hash or open Native."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
def regular(p):
 for n in(p,*p.parents):
  if n.exists()and(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024):raise ValueError('No reparse paths')
def tree(root):
 regular(root);total=0;files=0;hardlinks=0
 if root.is_file():s=root.stat();return{'root':str(root),'files':1,'logical_bytes':s.st_size,'hardlinked_file_names':int(s.st_nlink>1)}
 for base,ds,ns in os.walk(root,followlinks=False):
  for n in ds:regular(Path(base)/n)
  for n in ns:
   p=Path(base)/n;regular(p)
   try:s=p.stat()
   except FileNotFoundError:continue
   total+=s.st_size;files+=1;hardlinks+=int(s.st_nlink>1)
 return {'root':str(root),'files':files,'logical_bytes':total,'hardlinked_file_names':hardlinks}
def main(a):
 roots=[P]
 for parent in(RP/'materiales',RP/'codigo_preservado',RP/'recetas',RP/'verificaciones'):
  for p in parent.iterdir():
   if p.name.startswith(('PI07_','pi07_')):roots.append(p)
 rows=[tree(p)for p in roots];total=sum(r['logical_bytes']for r in rows)
 d={'schema':'DEE.PI07.scoped_new_storage.logical.v1','at_utc':datetime.now(timezone.utc).isoformat(),'source': 'File metadata only; fixed experiment and newPI07RP roots, no whole-project census.', 'roots':rows,'current_logical_bytes':total,'budget_bytes':5500000000,'remaining_logical_bytes':5500000000-total,'within_budget':total<=5500000000,'includes_duplicate_names_even_for_hardlinks':True,'Native_ticks':0,'measurement_is_not_free_space_recovered':True,'live_write_possible':a.live}
 out=P/'control'/a.output
 if out.exists()or not out.resolve().is_relative_to((P/'control').resolve()):raise ValueError('Fresh scoped result only')
 with out.open('x',encoding='utf8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in d.items()if k!='roots'}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True);ap.add_argument('--live',action='store_true');main(ap.parse_args())
