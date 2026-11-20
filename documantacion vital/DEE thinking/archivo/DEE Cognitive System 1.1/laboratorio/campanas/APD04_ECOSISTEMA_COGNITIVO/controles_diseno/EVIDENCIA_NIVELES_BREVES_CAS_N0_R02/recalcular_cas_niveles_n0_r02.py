"""Verify/rehydrate/recalculate the lossless brief-level N0 dossier CAS.

Standard-library only. No Native engine, network, historic paths or actor.
This essential analysis is not a full operational-life backup.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def sha(b):return hashlib.sha256(b).hexdigest()
def reconstruct(base,destination=None):
    index=json.loads((base/'INDICE_CAS.json').read_bytes());seen=set();checked=[]
    if destination is not None:
        if destination.exists():raise FileExistsError('Never overwrite an extraction')
        destination.mkdir(parents=True);destination=destination.resolve()
    for x in index['original_members']:
        rel=Path(x['original_file'])
        if rel.is_absolute()or'..'in rel.parts or x['original_file']in seen:raise ValueError('Unsafe/duplicate relative path')
        seen.add(x['original_file']);source=(base/x['CAS_payload']).resolve()
        if not source.is_relative_to(base.resolve()):raise ValueError('CAS escaped analysis folder')
        z=source.read_bytes()
        if sha(z)!=x['CAS_payload_sha256']:raise ValueError('CAS payload hash mismatch')
        b=gzip.decompress(z)
        if sha(b)!=x['original_sha256']or len(b)!=x['original_bytes']:raise ValueError('Original bytes mismatch')
        if destination is not None:
            q=(destination/rel).resolve()
            if not q.is_relative_to(destination):raise ValueError('Rehydrated path escaped')
            q.parent.mkdir(parents=True,exist_ok=True)
            with q.open('xb')as f:f.write(b)
        checked.append({'file':x['original_file'],'original_sha256':sha(b),'bytes':len(b)})
    return checked


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--base',type=Path,default=Path(__file__).resolve().parent)
    ap.add_argument('--extract',type=Path);ap.add_argument('--verify-only',action='store_true');ap.add_argument('--output',type=Path)
    a=ap.parse_args();base=a.base.resolve();manifest=json.loads((base/'MANIFIESTO.json').read_bytes())
    for x in manifest['members']:
        p=(base/x['file']).resolve()
        if not p.is_relative_to(base)or sha(p.read_bytes())!=x['sha256']:raise ValueError('Analysis member hash mismatch')
    checked=reconstruct(base,a.extract)
    if a.verify_only:
        print(json.dumps({'all_original_files_verified':len(checked),'new_Native_ticks':0,'extracted':a.extract is not None}));return
    def run(folder):
        command=[sys.executable,'-I','-B','-X','utf8',str(folder/'recalcular_niveles_breves_n0_r01.py'),'--recalc',str(folder)]
        if a.output:command+=['--output',str(a.output.resolve())]
        r=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
        if r.returncode:raise RuntimeError('N0 recalc failed: '+r.stderr.decode('utf8',errors='replace'))
        text=r.stdout.decode('utf8');summary=json.loads(text)
        if summary['issues']:raise ValueError('Recalculated integrity issues: '+str(summary['issues']))
        print(json.dumps({'rehydrated_originals':len(checked),'Native_ticks':0,'source_bytes_exact':True,'recalculation':summary},ensure_ascii=False))
    if a.extract:run(a.extract.resolve())
    else:
        # Library-owned temporary directory; no broad/custom recursive deletion.
        # Extra depth keeps the byte-preserved historical script's unused ROOT
        # constant well-defined even on an OS with a short temporary base.
        with tempfile.TemporaryDirectory(prefix='DEE_APD04_CAS_N0_')as temp:
            folder=Path(temp)/'portable'/'analysis'/'contenido'
            reconstruct(base,folder);run(folder)


if __name__=='__main__':main()
