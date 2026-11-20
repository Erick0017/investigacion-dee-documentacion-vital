"""Round-trip exported E3 bytes through in-memory ZIP and fresh extraction.

No delivery ZIP is created and no original material is changed. Recalculation
runs only on that extraction, with fresh output; no DEE or Native process.
"""
from pathlib import Path,PurePosixPath
import hashlib,io,json,subprocess,sys,zipfile
P=Path(__file__).resolve().parents[2];source=P/'ensayos/EVIDENCIA_E3_PORTABLE'
root=P/'control/E3_VALIDACION_PORTABLE_R02'
if root.exists():raise FileExistsError('Preserve prior verification')
root.mkdir();extract=root/'EXTRACCION_LIMPIA';extract.mkdir();out=root/'RECALCULO'
memory=io.BytesIO()
with zipfile.ZipFile(memory,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
    for f in sorted(source.rglob('*')):
        if f.is_file():
            if f.is_symlink():raise ValueError('No linked export member')
            z.writestr(f.relative_to(source).as_posix(),f.read_bytes())
encoded=memory.getvalue()
with zipfile.ZipFile(io.BytesIO(encoded),'r')as z:
    if z.testzip()is not None:raise ValueError('Export round-trip CRC failed')
    for member in z.infolist():
        name=PurePosixPath(member.filename)
        if name.is_absolute()or any(p in('.','..')for p in name.parts)or':'in member.filename or'\\'in member.filename:raise ValueError('Unsafe member')
        target=extract/name;target.parent.mkdir(parents=True,exist_ok=True);data=z.read(member)
        if data!=(source/name).read_bytes():raise ValueError('Member bytes changed on round-trip')
        target.write_bytes(data)
command=[sys.executable,'-I','-B','-X','utf8',str(extract/'RECALCULAR_E3.py'),'--evidence',str(extract),'--out',str(out)]
proc=subprocess.run(command,cwd=str(extract),capture_output=True,text=True,encoding='utf-8',timeout=120)
(root/'STDOUT.txt').write_text(proc.stdout,encoding='utf-8');(root/'STDERR.txt').write_text(proc.stderr,encoding='utf-8')
if proc.returncode:raise RuntimeError(proc.stderr)
summary=json.loads(proc.stdout)
proof={'schema':'PI04.E3.fresh_extraction_portability.v1','new_native_ticks':0,'actual_DEE_imports':0,
       'in_memory_ZIP_bytes':len(encoded),'in_memory_ZIP_sha256':hashlib.sha256(encoded).hexdigest(),'delivery_ZIP_written':False,
       'CRC_all_members':True,'source_and_extracted_bytes_equal':True,'extraction':str(extract),'output':str(out),
       'result':summary,'scope':'Actual exported recorded data recalculated from a fresh standard ZIP extraction. Native experimental reproduction is a different modality.'}
target=P/'control/PORTABILIDAD_RECALCULO_E3_R02.json'
if target.exists():raise FileExistsError('Prior proof protected')
target.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(proof,ensure_ascii=False,indent=2))
