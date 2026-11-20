"""Read-only comparison of exactly the eleven protected files captured at R07 start.

This script imports no DEE modules and never consults or opens a Native world.
It writes only the explicitly requested new R07 proof. It proves this scope only.
"""
from pathlib import Path
import argparse, datetime, hashlib, json

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    base=json.loads(a.baseline.read_text(encoding='utf-8-sig'))
    if a.output.exists():
        raise ValueError('Preserve existing proof; output must be new')
    if len(base['files'])!=11:
        raise ValueError('Expected exact eleven-file baseline')
    rows=[]
    for entry in base['files']:
        f=Path(entry['path'])
        row={'role':entry['role'],'path':str(f),'expected_bytes':entry['bytes'],
             'expected_sha256':entry['sha256'],'present':f.is_file()}
        if row['present']:
            before=f.stat()
            row.update(bytes=before.st_size,sha256=sha(f))
            after=f.stat()
            row['stable_during_hash']=(before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
            row['matches_baseline']=row['bytes']==entry['bytes'] and row['sha256']==entry['sha256'] and row['stable_during_hash']
        else:
            row['matches_baseline']=False
        rows.append(row)
    result={'schema':'DEE.R07.ProtectedEleven.EndComparison.R01',
        'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'baseline':str(a.baseline.resolve()),'baseline_sha256':sha(a.baseline),
        'scope':'Exactly eleven explicit files; not whole-project immutability or current Native functionality',
        'files':rows,'all_match':all(x['matches_baseline'] for x in rows),
        'Native_loaded':False,'new_ticks':0,'source_files_written':0}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as out:
        json.dump(result,out,ensure_ascii=False,indent=2)
    print(json.dumps({'checked':len(rows),'all_match':result['all_match'],'output':str(a.output)},ensure_ascii=False))
    return 0 if result['all_match'] else 1

if __name__=='__main__':
    raise SystemExit(main())
