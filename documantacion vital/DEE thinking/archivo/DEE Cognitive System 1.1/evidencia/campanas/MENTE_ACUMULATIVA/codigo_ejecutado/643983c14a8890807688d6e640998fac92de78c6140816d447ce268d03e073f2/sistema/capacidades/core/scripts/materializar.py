"""Materialize selected exact members from the deduplicated inert byte store.

No pickle, eval, code execution, historical archives or laboratory paths.
Existing differing files are protected. Prefixes allow bounded reconstruction.
"""
from pathlib import Path,PurePosixPath
import argparse,base64,gzip,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def digest(b):return hashlib.sha256(b).hexdigest()
def materialize(destination,prefixes=()):
 destination=Path(destination).resolve()
 if destination==ROOT or ROOT.is_relative_to(destination)or destination.is_relative_to(ROOT):raise ValueError('Use an external recovery directory')
 index=json.loads((ROOT/'documentacion/INDICE_MIEMBROS.json').read_text(encoding='utf8'))
 store=ROOT/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz'
 if digest(store.read_bytes())!=index['content_store_sha256']:raise ValueError('Content store hash mismatch')
 chosen={n:r for n,r in index['paths'].items()if not prefixes or any(n.startswith(p)for p in prefixes)}
 by_hash={}
 for name,row in chosen.items():
  q=PurePosixPath(name)
  if q.is_absolute()or'..'in q.parts or':'in name or'\\'in name:raise ValueError('Unsafe recovered path')
  by_hash.setdefault(row['sha256'],[]).append(name)
 created=0;verified=0;total=0;seen=set();all_blobs=set()
 destination.mkdir(parents=True,exist_ok=True)
 with gzip.open(store,'rt',encoding='ascii')as f:
  for line in f:
   item=json.loads(line);h=item['sha256']
   if h in all_blobs:raise ValueError('Duplicate blob')
   all_blobs.add(h);b=base64.b64decode(item['base64'],validate=True)
   if len(b)!=item['bytes']or digest(b)!=h:raise ValueError('Blob checksum mismatch')
   if h not in by_hash:continue
   seen.add(h)
   for name in by_hash[h]:
    row=chosen[name]
    if row['bytes']!=len(b):raise ValueError('Index size mismatch')
    p=destination/name;p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():
     if not p.is_file()or digest(p.read_bytes())!=h:raise FileExistsError('Protected existing file: '+str(p))
     verified+=1
    else:
     with p.open('xb')as out:out.write(b)
     created+=1
    total+=len(b)
 if seen!=set(by_hash)or all_blobs!={r['sha256']for r in index['paths'].values()}:raise ValueError('Missing/unindexed blob(s)')
 return{'status':'PASS','paths':len(chosen),'created':created,'existing_identical':verified,'materialized_bytes':total,'unique_selected_blobs':len(seen),'all_store_blobs_decoded_and_hashed':len(all_blobs),'prefixes':list(prefixes),'root':str(destination),'content_store_sha256':index['content_store_sha256']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--prefix',action='append',default=[]);a=p.parse_args();print(json.dumps(materialize(a.out,a.prefix),ensure_ascii=False))
if __name__=='__main__':main()
