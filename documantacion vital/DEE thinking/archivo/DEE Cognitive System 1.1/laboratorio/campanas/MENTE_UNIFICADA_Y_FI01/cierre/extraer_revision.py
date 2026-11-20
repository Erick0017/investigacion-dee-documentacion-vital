"""Materializa una versión exacta archivada; no ejecuta su contenido."""
import argparse,hashlib,json
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('revision');ap.add_argument('destination',type=Path);a=ap.parse_args()
base=Path(__file__).resolve().parents[1]/'CODIGO_EJECUTADO'
versions=json.loads((base/'REVISIONES.json').read_text(encoding='utf-8'))
if a.destination.exists():raise FileExistsError('Use a new directory')
for name,entry in versions[a.revision].items():
    relative=Path(name)
    assert not relative.is_absolute()and'..'not in relative.parts
    data=(base/'objetos'/entry['sha256']).read_bytes()
    assert len(data)==entry['bytes']and hashlib.sha256(data).hexdigest()==entry['sha256']
    out=a.destination/relative;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
print(json.dumps({'revision':a.revision,'files':len(versions[a.revision]),'native_ticks':0}))
