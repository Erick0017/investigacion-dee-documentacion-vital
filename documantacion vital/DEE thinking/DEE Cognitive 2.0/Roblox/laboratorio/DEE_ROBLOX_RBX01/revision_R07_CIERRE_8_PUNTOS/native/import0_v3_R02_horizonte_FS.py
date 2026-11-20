"""Prospective administrative import horizon only; Root explicit CLI.

R07's420MB/5327-member closed FS export took about45min on this host.
Allow at most3600s for the first zero-tick import, still bounded by21:07UTC.
No RAM/RAW/tick/cognitive deadline is changed; R01 source stays byte-exact.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, types

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = 'b9c2430649b75cafe8c1ebba17f146916298543bc174a44f5956bb38b78a0d57'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute-root-only',action='store_true')
    p.add_argument('--product',type=Path,required=True)
    p.add_argument('--destination',type=Path,required=True)
    p.add_argument('--native-cutoff-utc-epoch',type=float,required=True)
    a=p.parse_args()
    if not a.execute_root_only or a.native_cutoff_utc_epoch!=1794863220:
        raise ValueError('Explicit Root and unchanged global cutoff required')
    src=ROOT/'native/import0_v3.py';raw=src.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED:
        raise ValueError('Preserved R01 supervisor differs')
    anchor='time.monotonic() - started >= 900'
    text=raw.decode('utf8')
    if text.count(anchor)!=1:raise ValueError('Exact administrative horizon anchor')
    text=text.replace(anchor,'time.monotonic() - started >= 3600')
    module=types.ModuleType('_R07_import0_horizon_FS_R02');module.__file__=str(src)
    exec(compile(text,str(src),'exec'),module.__dict__)
    dest=a.destination.resolve(strict=True)
    if dest.parent!=ROOT/'native':raise ValueError('Diagnostic destination only')
    note=dest/'IMPORT0_HORIZONTE_FS_R02.json'
    if note.exists():raise ValueError('Fresh import only; preserve previous attempt')
    value={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope':'Prospective administrative copy/import walltime; not Native evolution',
        'source_supervisor_sha256':EXPECTED,'old_wall_max_seconds':900,
        'new_wall_max_seconds':3600,'cutoff_unchanged':1794863220,
        'memory_limit_unchanged_bytes':536870912,'ticks_guard_unchanged':True,
        'reason':'Prior closed FS export420051107bytes/5327members required about45min on this host',
        'no_previous_import_failure_hidden':True}
    with note.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(module.run(a.product,dest,a.native_cutoff_utc_epoch),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
