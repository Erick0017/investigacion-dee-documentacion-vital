"""Join sequential binary parts with per-part and whole-file SHA256 checks."""
from pathlib import Path
import argparse,hashlib,json,os
def digest(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('archivo',help='Exact canonical ZIP name in PARTES.json');p.add_argument('--manifiesto',type=Path,default=Path(__file__).with_name('PARTES.json'));p.add_argument('--salida',type=Path);a=p.parse_args();m=json.loads(a.manifiesto.read_text(encoding='utf8'));entry=next(x for x in m['archives']if x['archive']==a.archivo);folder=a.manifiesto.resolve().parent;dest=(a.salida or folder/a.archivo).resolve()
    if dest.exists():
        if dest.stat().st_size==entry['bytes']and digest(dest)==entry['sha256']:print('El ZIP canónico ya existe y coincide: '+str(dest));return
        raise FileExistsError('No se sobrescribe un archivo diferente: '+str(dest))
    ordered=sorted(entry['parts'],key=lambda x:x['order'])
    if [x['order']for x in ordered]!=list(range(1,len(ordered)+1)):raise ValueError('Orden incompleto o duplicado')
    for row in ordered:
        if Path(row['name']).name!=row['name']:raise ValueError('Nombre de parte no seguro')
        source=folder/row['name']
        if not 0<row['bytes']<16000000 or source.stat().st_size!=row['bytes']or digest(source)!=row['sha256']:raise ValueError('Identidad o tamaño de parte incorrecto: '+row['name'])
    dest.parent.mkdir(parents=True,exist_ok=True);temporary=dest.with_name(dest.name+'.incompleto')
    with temporary.open('xb')as target:
        for row in ordered:
            with(folder/row['name']).open('rb')as source:
                for b in iter(lambda:source.read(1048576),b''):target.write(b)
        target.flush();os.fsync(target.fileno())
    if temporary.stat().st_size!=entry['bytes']or digest(temporary)!=entry['sha256']:raise ValueError('No coincide la reconstrucción; se conserva .incompleto para diagnóstico')
    if dest.exists():raise FileExistsError('El destino apareció mientras se reconstruía; no se sobrescribe')
    temporary.rename(dest);print(json.dumps({'file':str(dest),'bytes':dest.stat().st_size,'sha256':digest(dest),'verified':True},ensure_ascii=False))
if __name__=='__main__':main()
