"""Read-only comparison of the 16 previously pinned originals. Never imports DEE."""
from pathlib import Path
import argparse, datetime, hashlib, json

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--before',type=Path,required=True)
    p.add_argument('--workspace',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); root=a.workspace.resolve(strict=True)
    if a.output.exists():raise FileExistsError('Fresh preservation result required')
    source=json.loads(a.before.read_text('utf-8-sig')); files=source['files']
    if len(files)!=16:raise ValueError('Expected the predeclared 16 critical files')
    rows=[]
    for row in files:
        f=Path(row['path'])
        if not f.resolve(strict=True).is_relative_to(root):raise ValueError('Outside original workspace')
        for q in (f,*f.parents):
            if q.is_symlink() or (q.exists() and getattr(q.lstat(),'st_file_attributes',0)&1024):
                raise ValueError('Reparse path rejected')
        before=f.stat(); actual=digest(f); after=f.stat()
        stable=(before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
        rows.append({**row,'actualBytes':after.st_size,'actualSha256':actual,
            'stableDuringHash':stable,'sameBytesAndSha256':stable and
            after.st_size==row['bytes'] and actual==row['sha256']})
    out={'schema':'DEE.SDK.Preservation16.R06','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'sourceBeforeSha256':digest(a.before),'files':rows,'checked':len(rows),
        'unchanged':sum(x['sameBytesAndSha256'] for x in rows),
        'scope':'Only these sixteen pinned files. Not proof of whole-project immutability.',
        'NativeImportedOrExecuted':False,'originalFilesWritten':False}
    with a.output.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'checked':out['checked'],'unchanged':out['unchanged'],
        'outputBytes':a.output.stat().st_size,'outputSha256':digest(a.output)},sort_keys=True))

if __name__=='__main__':main()
