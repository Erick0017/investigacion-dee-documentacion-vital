"""Export one exact indexed evidence object; no engine or simulation."""
from pathlib import Path
import argparse,json,tarfile,hashlib,gzip
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--paquete',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--id',required=True);p.add_argument('--salida',type=Path,required=True);p.add_argument('--descomprimir',action='store_true');a=p.parse_args();ev=a.paquete/'EVIDENCIA_CAUSAL';ix=json.loads((ev/'INDICE_PRIMARIOS.json').read_text(encoding='utf8'));e=next(v for v in ix['entries']if v['id']==a.id);data=None
for name in [ix['archive'],*[v['archive']for v in ix.get('additional_archives',[])]]:
    with tarfile.open(ev/name,'r:xz')as t:
        try:m=t.getmember(e['member'])
        except KeyError:continue
        data=t.extractfile(m).read();break
if data is None:raise FileNotFoundError(e['member'])
assert hashlib.sha256(data).hexdigest()==e['sha256']
if a.descomprimir and data[:2]==b'\x1f\x8b':data=gzip.decompress(data)
with a.salida.open('xb')as f:f.write(data)
print(json.dumps({'id':a.id,'original_sha256':e['sha256'],'output_sha256':hashlib.sha256(data).hexdigest(),'output_bytes':len(data),'decompressed_copy':a.descomprimir,'native_ticks':0},ensure_ascii=False))
