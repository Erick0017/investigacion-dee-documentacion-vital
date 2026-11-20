"""Verify and freeze parent, copy only identified inherited helpers."""
import datetime as D,hashlib,json,shutil,sys,zipfile
from pathlib import Path
EXPECTED='12bd795fe35e1ebda884c440bd9b2a0f7677ed6ac0594393e55093146e626e8e'
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    parent=Path(sys.argv[1]).resolve();work=Path(__file__).resolve().parent
    if sha(parent)!=EXPECTED:raise ValueError('PARENT_MISMATCH; do not select another by date')
    sealed=work/'PARENT_SEALED.zip'
    if sealed.exists():assert sha(sealed)==EXPECTED
    else:shutil.copy2(parent,sealed)
    root=work/'02_REPERTORIO_NATIVO_Y_CIERRES';root.mkdir(exist_ok=True)
    members=[]
    with zipfile.ZipFile(sealed) as z:
        assert len(z.infolist())==1155;assert z.testzip() is None
        for info in z.infolist():
            data=z.read(info.filename);members.append({'name':info.filename,'size':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        for line in z.read('HASHES.sha256').decode('utf-8').splitlines():
            h,name=line.split('  ',1);assert hashlib.sha256(z.read(name)).hexdigest()==h
        copies={'RUNNER/apparatus.py':'RUNNER/apparatus.py','RUNNER/observations.py':'RUNNER/observations.py',
                'RUNNER/branches.py':'RUNNER/legacy_branches.py'}
        for name,dest in copies.items():
            q=root/dest;q.parent.mkdir(parents=True,exist_ok=True)
            if not q.exists():q.write_bytes(z.read(name))
        for name in ('CHECKPOINTS/L03/contingent_intact/T8.deetsnap','CHECKPOINTS/L03/contingent_intact/T13.deetsnap'):
            data=z.read(name)
            h=hashlib.sha256(data).hexdigest()
            expected='8f09341e2fa1bd6d48ced41246d3771b9e0af443edef37e28e2945b04d3a371c' if 'T8.' in name else '0420f3d68fd550124518a2d67b431c54bec12bb887f898a3fdaf3bc1a4c50610'
            assert h==expected,(name,h)
    manifest={'parent_sha256':EXPECTED,'parent_original':str(parent),'sealed_copy':str(sealed),
              'members':members,'count':len(members),'verified_utc':D.datetime.now(D.timezone.utc).isoformat(),
              'copied_helpers':copies,'scope':'All inherited uncompressed member bytes must remain identical; no parent summaries overwritten.'}
    (root/'PARENT_MEMBERS.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('VERIFIED_PARENT_1155_MEMBERS',EXPECTED,flush=True)
if __name__=='__main__':main()
