"""Recover only two identified implementation sources; never execute them."""
import hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main(root):
    archive=root.parents[3]/'ingenieria/INGENIERIA_01_DEE_V27_MEMORIA_APRENDIZAJE_PLASTICIDAD_Y_PROCESAMIENTO_RESULTADOS.zip';rows=[]
    with zipfile.ZipFile(archive) as z:
        hashes={}
        for line in z.read('HASHES.sha256').decode('utf-8-sig').splitlines():
            if line.strip():h,n=line.split(maxsplit=1);hashes[n.strip().lstrip('*')]=h
        for member in ('RUNNERS/ing01_apparatus.py','RUNNERS/ing01_common.py','RUNNERS/VENDORED/core10_apparatus.py'):
            data=z.read(member);h=hashlib.sha256(data).hexdigest();assert hashes.get(member)==h,(member,'source manifest mismatch');dest=root/'fuentes_pertinentes/I01'/member;dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists():assert dest.read_bytes()==data
            else:dest.write_bytes(data)
            rows.append({'archive':str(archive),'member':member,'sha256':h,'manifest_verified':True,'destination':dest.relative_to(root).as_posix(),'historical_execution':False})
    (root/'experimentos/seleccion_revisable/SOURCE_PROVENANCE.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');print(json.dumps(rows))
if __name__=='__main__':main(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT)
