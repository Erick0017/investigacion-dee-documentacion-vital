"""Read-only streaming hashes/gzipCRC of every local snapshot, no engine import.

This is storage integrity, NOT a claim that every historical snapshot is newly
restored. The independent clean suite tests native loading/continuation for
selected physically important states separately.
"""
import argparse,gzip,hashlib,json,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(path):
 h=hashlib.sha256()
 with path.open('rb')as stream:
  for block in iter(lambda:stream.read(1024**2),b''):h.update(block)
 return h.hexdigest()
def run(out):
 started=time.monotonic();started_utc=datetime.now(timezone.utc).isoformat();script_sha=digest(Path(__file__));files=sorted(p for p in ROOT.rglob('*')if p.is_file()and(p.name.endswith('.deetsnap.gz')or p.name.endswith('.deetsnap')));rows=[];errors=[]
 for path in files:
  row={'path':path.relative_to(ROOT).as_posix(),'encoded_bytes':path.stat().st_size,'encoded_sha256':digest(path),'gzip':path.suffix=='.gz'}
  try:
   if row['gzip']:
    h=hashlib.sha256();size=0
    with gzip.open(path,'rb')as stream:
     for block in iter(lambda:stream.read(1024**2),b''):
      size+=len(block)
      if size>512*1024**2:raise ValueError('Declared finite512MiB decoded storage limit exceeded')
      h.update(block)
    row.update(decoded_bytes=size,decoded_sha256=h.hexdigest(),gzip_CRC_verified=True)
   row['status']='STORAGE_INTEGRITY_CHECKED'
  except Exception as e:row.update(status='ERROR',error=repr(e));errors.append(row['path'])
  if path.stat().st_size!=row['encoded_bytes']or digest(path)!=row['encoded_sha256']:errors.append(row['path']+' changed during pass')
  rows.append(row)
 result={'schema':'CPC8R.all_local_snapshot_storage.v1','status':'PASS'if not errors else'FAIL','started_utc':started_utc,'finished_utc':datetime.now(timezone.utc).isoformat(),'script_sha256':script_sha,'files':rows,'count':len(rows),'errors':errors,'elapsed_seconds':time.monotonic()-started,'scope':'Encoded byte hashes and streaming gzipCRC/decoded hashes only. Native semantic/schema loading and physical/operational continuity are separate selected clean gates. No snapshots or worlds modified.'}
 out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('x',encoding='utf8')as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
 print(json.dumps({k:result[k]for k in('status','count','errors','elapsed_seconds')}))
 if errors:raise SystemExit(1)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.out)
