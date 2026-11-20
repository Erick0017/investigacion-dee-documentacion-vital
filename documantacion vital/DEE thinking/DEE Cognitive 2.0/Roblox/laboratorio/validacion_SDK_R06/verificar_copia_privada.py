"""Closed diagnostic case byte comparison; never imports or advances DEE."""
import argparse, hashlib, json, os
from pathlib import Path
from datetime import datetime, timezone

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def run(source,target,output):
    a=Path(source).resolve(strict=True); b=Path(target).resolve(strict=True); out=Path(output)
    if a==b or a.name!='SDK_DEMO_82379FB770E94794' or b.name!=a.name: raise ValueError('Explicit closed case only')
    if out.exists(): raise FileExistsError(out)
    for base in(a,b):
        if (base/'SDK_SERVICE.lock').exists(): raise RuntimeError('Service lock present')
    rows=[]; dirs=set(); total=0
    for p in sorted(a.rglob('*')):
        st=p.lstat()
        if p.is_symlink() or getattr(st,'st_file_attributes',0)&1024: raise ValueError('Reparse prohibited')
        rel=p.relative_to(a).as_posix(); q=b/rel
        if p.is_dir():
            if not q.is_dir(): raise ValueError('Missing directory: '+rel)
            dirs.add(rel); continue
        before=(st.st_size,st.st_mtime_ns); h=sha(p)
        if not q.is_file() or q.stat().st_size!=st.st_size or sha(q)!=h: raise ValueError('Copy mismatch: '+rel)
        after=p.stat()
        if before!=(after.st_size,after.st_mtime_ns): raise RuntimeError('Source changed: '+rel)
        total+=st.st_size; rows.append({'file':rel,'bytes':st.st_size,'sha256':h})
    if {p.relative_to(b).as_posix() for p in b.rglob('*') if p.is_file()}!={r['file'] for r in rows}: raise ValueError('File set mismatch')
    value={'schema':'DEE.SDK.closed_private_copy.v1','utc':datetime.now(timezone.utc).isoformat(),'source':str(a),'target':str(b),'NativeOpened':False,'allFilesIdentical':True,'files':len(rows),'bytes':total,'directories':len(dirs),'members':rows,'scope':'Closed one-life complete instance only; not entire project immutability or a paired GUI continuation claim.'}
    with out.open('x',encoding='utf8') as f: json.dump(value,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:v for k,v in value.items() if k!='members'},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--target',required=True);p.add_argument('--output',required=True);a=p.parse_args();run(a.source,a.target,a.output)
