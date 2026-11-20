"""Explicit, non-destructive restoration of diagnostic worlds for laboratory use.

This copies complete states only on request. It does not train or activate a
life, edit RAW/clocks, copy a response, or create another independent sample.
"""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[4]
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--sistema',type=Path,required=True);p.add_argument('--vidas',nargs='+',required=True);a=p.parse_args();base=ROOT/'laboratorio/candidatos/ESTADOS_AUXILIARES';idx=json.loads((base/'INDICE.json').read_bytes());dest=a.sistema.resolve(strict=True);active=dest/'estado/ACTIVO.json';before=sha(active);done=[]
    if not set(a.vidas)<=set(idx['lives']):raise ValueError('Unknown auxiliary life; no inferred mapping')
    for row in idx['files']:
        if not set(row['lives'])&set(a.vidas):continue
        rel=PurePosixPath(row['path'])
        if rel.is_absolute()or'..'in rel.parts or':'in str(rel):raise ValueError('Unsafe state member')
        src=base/'sistema'/rel;target=(dest/rel).resolve()
        if not target.is_relative_to(dest):raise ValueError('Auxiliary destination escapes the declared system')
        if sha(src)!=row['sha256']:raise ValueError('Auxiliary source identity differs')
        if target.exists():
            if sha(target)!=row['sha256']:raise FileExistsError('An existing life/state differs; never overwrite: '+str(target))
            status='ALREADY_IDENTICAL'
        else:target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target);status='EXACT_COPY_EXPLICIT_AUXILIARY_RESTORATION'
        done.append({'path':str(rel),'sha256':sha(target),'status':status})
    if sha(active)!=before:raise AssertionError('Auxiliary restoration changed the active selection')
    print(json.dumps({'role':'INSTRUMENTO','operation':'RESTORE_LAB_AUXILIARY_COMPLETE_STATES','lives':a.vidas,'active_unchanged':True,'files':done,'knowledge_attribution':'Exact diagnostic history only, not new acquisition or promotion; no independent subject counted.'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
