"""One directed identity inventory; never runs historical campaigns."""
import json
from pathlib import Path
import sys
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,BASE,sha,put,identity

NAME='CPC5_ARQUITECTURAS_COMPUESTAS_Y_APRENDIZAJE_ACUMULATIVO_RESULTADOS.zip'
EXPECTED='26c5b0f207b235b6f5990d85f586a5bd7dde440eeb989c4ae5e7eb47fe54b075'

def main():
    parent=BASE.parents[1]/NAME
    actual=sha(parent)
    if actual!=EXPECTED:
        put(ROOT/'PARENT_DISCREPANCY.json',{'path':str(parent),'expected':EXPECTED,'actual':actual})
        raise RuntimeError('Different parent cut: preserve and identify before continuing')
    rows=[]
    import hashlib
    with zipfile.ZipFile(parent) as z:
        assert z.testzip() is None
        for info in z.infolist():
            h=hashlib.sha256()
            with z.open(info) as f:
                for block in iter(lambda:f.read(1048576),b''):h.update(block)
            rows.append({'path':info.filename,'bytes':info.file_size,'sha256':h.hexdigest()})
        for name in ('CPC5/MANIFEST.json','CPC5/HASHES.sha256'):
            target=ROOT/'historial/corte_01'/Path(name).name
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(z.read(name))
    put(ROOT/'PARENT_MEMBERS.json',{'schema':'CPC5.extension.parent.v1','archive':NAME,'sha256':actual,'members':rows})
    kernel=BASE/'referencias/producto4/kernel_v27.cpp'
    assert sha(kernel)=='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
    put(ROOT/'PROVENANCE.json',{'schema':'CPC5.extension.provenance.v1','parent_sha256':actual,
                              'parent_members':len(rows),'instrument':identity(),
                              'kernel_sha256':sha(kernel),'budget':json.loads((ROOT/'BUDGET.json').read_text()),
                              'implementation':'Same official wheel; preparation/input/observation tools only. No historical main imported.'})
    print(json.dumps({'parent_sha256':actual,'members':len(rows),'status':'VERIFIED'}))

if __name__=='__main__':main()
