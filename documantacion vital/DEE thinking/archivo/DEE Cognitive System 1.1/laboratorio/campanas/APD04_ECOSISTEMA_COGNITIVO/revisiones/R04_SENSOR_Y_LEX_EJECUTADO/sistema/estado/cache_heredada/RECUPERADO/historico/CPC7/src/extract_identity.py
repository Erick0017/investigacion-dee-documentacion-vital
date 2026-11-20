"""Read-only extraction of frozen identity source and existing notices."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT.parents[2]/'4.0/DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip'
def sha(blob):return hashlib.sha256(blob).hexdigest()
before=sha(source.read_bytes());rows=[]
with zipfile.ZipFile(source) as z:
    candidates=[n for n in z.namelist() if n.endswith('/source/src/kernel_v27.cpp') or n=='source/src/kernel_v27.cpp']
    assert len(candidates)==1,candidates
    name=candidates[0];blob=z.read(name);assert sha(blob)=='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
    target=ROOT/'genealogia/kernel_v27.cpp'
    if target.exists():assert target.read_bytes()==blob
    else:target.write_bytes(blob)
    rows.append({'member':name,'destination':'genealogia/kernel_v27.cpp','sha256':sha(blob)})
    notices=[n for n in z.namelist() if not n.endswith('/') and (Path(n).name.lower().startswith(('license','notice','copying')) or 'notices' in Path(n).name.lower())]
    for i,n in enumerate(notices):
        blob=z.read(n);p=ROOT/'runtime/AVISOS'/f'{i+1:02d}_{Path(n).name}';p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists():assert p.read_bytes()==blob
        else:p.write_bytes(blob)
        rows.append({'member':n,'destination':p.relative_to(ROOT).as_posix(),'sha256':sha(blob)})
assert sha(source.read_bytes())==before
(ROOT/'genealogia/ENGINE_SOURCE_IDENTITY.json').write_text(json.dumps({'archive':source.name,'archive_sha256':before,'selected':rows,'source_unchanged':True},indent=2),encoding='utf-8')
print(json.dumps({'kernel_source_verified':True,'notices_selected':len(notices),'source_unchanged':True}))
