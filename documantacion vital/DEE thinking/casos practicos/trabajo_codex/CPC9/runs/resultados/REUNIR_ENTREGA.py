"""Join and verify numbered segments. No-clobber hardlink publication requires NTFS or equivalent filesystem hardlink support."""
import argparse,hashlib,json,os
from pathlib import Path

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def leaf(s):
    if not isinstance(s,str) or not s or Path(s).name!=s or '/' in s or '\\' in s or ':' in s or s in('.','..'):raise ValueError('Unsafe leaf name')
    return s

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,default=Path(__file__).with_name('PARTES.json'));p.add_argument('--archivo');p.add_argument('--out',type=Path);a=p.parse_args()
    source=a.manifest.resolve(strict=True);data=json.loads(source.read_text(encoding='utf-8'));folder=source.parent;out=(a.out or folder).resolve();out.mkdir(parents=True,exist_ok=True)
    selected=[x for x in data['archives'] if a.archivo is None or x['name']==a.archivo]
    if not selected:raise ValueError('Archive not found in transport manifest')
    for entry in selected:
        target=out/leaf(entry['name'])
        if target.exists():
            if target.stat().st_size==entry['bytes'] and sha(target)==entry['sha256']:print('YA VERIFICADO: '+str(target));continue
            raise FileExistsError('Existing canonical does not match; preserved: '+str(target))
        if not entry['parts']:raise FileNotFoundError('This small canonical was not divided; obtain '+entry['name'])
        parts=entry['parts']
        if [x['index']for x in parts]!=list(range(1,len(parts)+1)):raise ValueError('Incorrect segment order')
        temporary=target.with_name(target.name+'.joining.'+str(os.getpid()))
        if temporary.exists():raise FileExistsError(str(temporary))
        with temporary.open('xb') as dst:
            for part in parts:
                path=folder/leaf(part['name'])
                if path.stat().st_size!=part['bytes'] or part['bytes']>data['maximum_part_bytes'] or sha(path)!=part['sha256']:raise ValueError('Part size/hash mismatch: '+path.name)
                with path.open('rb') as src:
                    for block in iter(lambda:src.read(1048576),b''):dst.write(block)
        if temporary.stat().st_size!=entry['bytes'] or sha(temporary)!=entry['sha256']:raise ValueError('Full reconstruction failed; evidence retained')
        # Atomic fail-if-exists: a concurrent writer cannot be overwritten.
        # Both names are in the same folder. Unsupported hardlinks fail safely.
        os.link(temporary,target);temporary.unlink();print('RECONSTRUIDO Y VERIFICADO: '+str(target))
if __name__=='__main__':main()
