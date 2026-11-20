"""Recalculate MUFI archived evidence in a separate directory, no DEE ticks."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidencia',type=Path,required=True)
    p.add_argument('--calculo',type=Path,required=True)
    p.add_argument('--referencia',type=Path,required=True)
    p.add_argument('--salida',type=Path,required=True)
    p.add_argument('--padre-temporal',type=Path)
    p.add_argument('--codigo-extra',type=Path,action='append',default=[])
    p.add_argument('--argumento-calculo',action='append',default=[])
    a = p.parse_args()
    reference_bytes = a.referencia.read_bytes()
    reference = json.loads(reference_bytes)
    root = Path(tempfile.mkdtemp(prefix='MUFI-recalc-',dir=a.padre_temporal))
    evidence = root/'EVIDENCIA';evidence.mkdir()
    script = root/a.calculo.name
    shutil.copyfile(a.calculo,script)
    before = {str(a.calculo.resolve()):sha(a.calculo),str(a.referencia.resolve()):sha(a.referencia)}
    extra_code=[]
    for source in a.codigo_extra:
        if source.name==script.name:raise ValueError('Duplicate main script')
        target=root/source.name;shutil.copyfile(source,target)
        before[str(source.resolve())]=sha(source)
        extra_code.append({'name':source.name,'sha256':sha(target)})
    copied=[]
    sources=reference.get('sources')
    if sources is None:
        sources=[{'file':row['file'],'sha256':row['sha256'],
                  'bytes':(a.evidencia/row['file']).stat().st_size}for row in reference['results']]
    for source in [*sources,*reference.get('worker_output_files',[])]:
        part=Path(source['file'])
        if part.is_absolute() or '..' in part.parts:
            raise ValueError('Unsafe evidence member')
        src=a.evidencia/part;dst=evidence/part
        dst.parent.mkdir(parents=True,exist_ok=True)
        if sha(src)!=source['sha256']:raise ValueError('Reference/source hash mismatch')
        before[str(src.resolve())]=sha(src)
        shutil.copyfile(src,dst)
        if sha(src)!=sha(dst):raise ValueError('Copied evidence changed')
        copied.append(source)
    out=root/'RECALCULADO.json'
    command=[sys.executable,'-I','-B','-X','utf8',str(script),*a.argumento_calculo,'--evidencia',str(evidence),'--salida',str(out)]
    done=subprocess.run(command,cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=120)
    after={path:sha(path) for path in before}
    equal=out.is_file() and out.read_bytes()==reference_bytes
    proof={'schema':'DEE.MUFI.archived_recalculation_portable.v1','new_dee_ticks':0,
           'independent_directory':str(root),'command':command,'exit_code':done.returncode,
           'stdout':done.stdout,'stderr':done.stderr,'copied_evidence':copied,
           'extra_code':extra_code,
           'calculation_source_sha256':sha(script),'reference_sha256':sha(a.referencia),
           'output_sha256':sha(out) if out.is_file() else None,
           'output_identical_to_reference_bytes':equal,'original_files_unchanged':before==after,
           'scope':'Separate-path archived calculation only; not native reproduction, new acquisition, or OS sandbox.'}
    a.salida.parent.mkdir(parents=True,exist_ok=True)
    a.salida.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:proof[k] for k in ('exit_code','new_dee_ticks','output_identical_to_reference_bytes','original_files_unchanged','output_sha256')},ensure_ascii=False))
    return 0 if done.returncode==0 and equal and before==after else 1


if __name__=='__main__':raise SystemExit(main())
