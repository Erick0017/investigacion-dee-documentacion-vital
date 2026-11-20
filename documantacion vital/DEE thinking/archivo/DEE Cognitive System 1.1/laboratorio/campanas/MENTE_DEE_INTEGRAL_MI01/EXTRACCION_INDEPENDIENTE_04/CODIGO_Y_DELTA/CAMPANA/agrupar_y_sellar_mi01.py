"""Reduce duplicación de metadatos por compresión conjunta, sin omitir bytes.
No cambia física, primarios, código sellado ni estados seleccionados.
"""
import lzma,hashlib,io,json,shutil,tarfile,zipfile
from pathlib import Path
from datetime import datetime,timezone
L=Path(__file__).resolve().parent;A=L/'PAQUETE_ANALISIS_CANDIDATO_02';P=L/'PAQUETE_ANALISIS_CANDIDATO_04';Z=L/'CANDIDATO_MI01_ANALISIS_04.zip';X=L/'EXTRACCION_INDEPENDIENTE_04'
assert not P.exists()and not Z.exists()and not X.exists(),'No sobrescribir revisión'
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
P.mkdir();group=[];stream=io.BytesIO()
with tarfile.open(fileobj=stream,mode='w',format=tarfile.PAX_FORMAT)as tar:
    for p in sorted(A.rglob('*')):
        if not p.is_file()or p.name=='MANIFIESTO_MIEMBROS.json':continue
        rp=p.relative_to(A)
        if rp.parts[:2]==('CONTINUIDAD','VIDAS'):
            b=p.read_bytes();name=Path(*rp.parts[2:]).as_posix();info=tarfile.TarInfo(name);info.size=len(b);info.mtime=0;info.mode=0o600;tar.addfile(info,io.BytesIO(b));group.append({'member':name,'original':'sistema/estado/vidas/'+name,'original_bytes':len(b),'original_sha256':sha(b)});continue
        q=P/rp;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
packed=lzma.compress(stream.getvalue(),format=lzma.FORMAT_XZ,preset=6);(P/'CONTINUIDAD/VIDAS_ORIGINALES.tar.xz').write_bytes(packed)
save(P/'CONTINUIDAD/VIDAS_ORIGINALES_INDICE.json',{'encoding':'TAR+XZ, exact original record bytes; grouped only for cross-file redundancy; readable with Python stdlib tarfile/lzma','native_ticks':0,'not_a_substitute_for_complete_snapshots':True,'members':group})
shutil.copy2(L/'verificar_paquete_mi01.py',P/'RECALCULO/verificar_paquete_mi01.py')
shutil.copy2(Path(__file__),P/'CODIGO_Y_DELTA/CAMPANA/agrupar_y_sellar_mi01.py')
save(P/'CONTINUIDAD/COMPACTACION_SIN_PERDIDA.json',{'native_ticks':0,'all_primary_JSON_preserved':True,'all17selected_states_preserved':True,'life_record_original_count':len(group),'life_record_original_bytes':sum(r['original_bytes']for r in group),'life_record_grouped_compressed_bytes':len(packed),'why':'The first unshared ZIP candidate exceeded16MB by209293bytes and grouped gzip still exceeded it by132418bytes. Joint XZ compression removes repeated ancestry/protocol text without deleting a single original record or selected state. Older candidates are not published.','no_record_bytes_changed':True,'verification':'Every decompressed record is checked by length andSHA from the independent extracted package.'})
files=sorted(p for p in P.rglob('*')if p.is_file());members=[{'path':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in files]
save(P/'MANIFIESTO_MIEMBROS.json',{'scope':'Every payload member; manifest excluded to avoid self reference. Container SHA lives outside.','members':members,'native_ticks_in_sealing':0})
with zipfile.ZipFile(Z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True)as out:
    for p in sorted(q for q in P.rglob('*')if q.is_file()):out.write(p,p.relative_to(P).as_posix(),compress_type=zipfile.ZIP_STORED if p.suffix=='.gz'else zipfile.ZIP_DEFLATED,compresslevel=9)
assert Z.stat().st_size<=16000000,('ZIP hard limit',Z.stat().st_size)
with zipfile.ZipFile(Z)as z:
    assert z.testzip()is None
    assert all(not Path(s).is_absolute()and'..'not in Path(s).parts for s in z.namelist())
    z.extractall(X);count=len(z.infolist());expanded=sum(i.file_size for i in z.infolist())
result={'candidate':str(Z),'sha256':sha(Z.read_bytes()),'compressed_bytes':Z.stat().st_size,'expanded_member_bytes':expanded,'members':count,'ZIP_CRC_valid':True,'hard_limit_bytes':16000000,'extracted_clean_directory':str(X),'native_ticks':0,'external_steps':0,'sealed_utc':datetime.now(timezone.utc).isoformat(),'independent_recalculation':'Not yet run from exact extracted ZIP. No publication until verified.'};save(L/'SELLO_CANDIDATO_PAQUETE_04.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))
