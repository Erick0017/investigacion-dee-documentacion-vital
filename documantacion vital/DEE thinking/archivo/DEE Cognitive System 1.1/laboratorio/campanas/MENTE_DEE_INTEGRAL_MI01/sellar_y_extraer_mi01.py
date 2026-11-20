"""Sella candidato científico, comprueba CRC y extrae a otra carpeta.
No ejecuta física. El hash del contenedor queda siempre FUERA de él.
"""
import hashlib,json,shutil,zipfile
from pathlib import Path
from datetime import datetime,timezone
L=Path(__file__).resolve().parent;P=L/'PAQUETE_ANALISIS_CANDIDATO_02';Z=L/'CANDIDATO_MI01_ANALISIS_02.zip';X=L/'EXTRACCION_INDEPENDIENTE_02'
assert P.is_dir()and not Z.exists()and not X.exists(),'No sobrescribir candidatos/verificaciones previos'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
shutil.copy2(L/'VERIFICACION_PREVIA_PAQUETE_02.json',P/'VERIFICACIONES/RECALCULO_Y_ESTADOS_PREVIO.json')
files=sorted(p for p in P.rglob('*')if p.is_file());members=[{'path':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in files]
save(P/'MANIFIESTO_MIEMBROS.json',{'scope':'Every payload member; this manifest excluded to avoid self reference. No container hash inside.','members':members,'native_ticks_in_sealing':0})
with zipfile.ZipFile(Z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True)as out:
    for p in sorted(q for q in P.rglob('*')if q.is_file()):
        out.write(p,p.relative_to(P).as_posix(),compress_type=zipfile.ZIP_STORED if p.suffix=='.gz'else zipfile.ZIP_DEFLATED,compresslevel=9)
assert Z.stat().st_size<=16000000,('Analysis ZIP exceeds hard limit',Z.stat().st_size)
with zipfile.ZipFile(Z)as z:
    assert z.testzip()is None
    for name in z.namelist():
        q=Path(name);assert not q.is_absolute()and'..'not in q.parts
    z.extractall(X)
    members_count=len(z.infolist());expanded=sum(i.file_size for i in z.infolist())
out={'candidate':str(Z),'sha256':sha(Z.read_bytes()),'compressed_bytes':Z.stat().st_size,'expanded_member_bytes':expanded,'members':members_count,'ZIP_CRC_valid':True,'hard_limit_bytes':16000000,'extracted_clean_directory':str(X),'native_ticks':0,'external_steps':0,'sealed_utc':datetime.now(timezone.utc).isoformat(),'independent_recalculation':'Pending execution from exact extracted ZIP; do not publish as verified yet.'}
save(L/'SELLO_CANDIDATO_PAQUETE_02.json',out);print(json.dumps(out,ensure_ascii=False,indent=2))
