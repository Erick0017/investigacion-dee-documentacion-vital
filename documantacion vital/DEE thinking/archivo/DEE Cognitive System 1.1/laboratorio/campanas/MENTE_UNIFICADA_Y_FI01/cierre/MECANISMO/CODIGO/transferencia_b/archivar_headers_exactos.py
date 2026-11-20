"""Regenerate exact emitted header bytes from archived hex, no DEE ticks.

Executed B02 used a shared host directory for matching tick/stage. Later arms
overwrote earlier header files. Primaries already preserved exact bytes+SHA.
This is an explicit archival repair, NOT a new emission or native experiment.
"""
import gzip,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import frontend_b01_r2 as f
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    out=f.OUT.parent/'B02';rows=[]
    for arm in('T','U','H'):
        p=out/(arm+'_ASSOCIATION_USE.json.gz');o=json.loads(gzip.decompress(p.read_bytes()))
        for r in o['result']['rows']:
            e=r['external_emission'];original=Path(e['file']);b=bytes.fromhex(e['bytes_hex'])
            if sha(b)!=e['sha256']:raise ValueError('Cannot regenerate exact emitted bytes')
            target=out/'headers_archivados'/arm/(r['stage']+'.header')
            if target.exists():raise FileExistsError(target)
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
            rows.append({'arm':arm,'stage':r['stage'],'primary':p.name,'primary_sha256':f.digest(p),'original_shared_path':str(original),
              'original_shared_path_current_sha256':f.digest(original),'original_emission_sha256':e['sha256'],'archive_path':str(target),
              'archive_sha256':f.digest(target),'bytes':len(b),'classification':'Exact archival regeneration from already recorded hexadecimal bytes, not a second emission or a historical original file.'})
    f.dump(out/'ARCHIVO_HEADERS_REGENERADOS.json',{'schema':'MUFI01.B02.header_archive.v1','native_ticks':0,'rows':rows,
      'limitation':'B02 shared output paths were overwritten across matched-age arms. Their exact primary hex and original hashes survive. Native inputs never read these headers; this bug affects artifact retention, not action generation or control isolation.'})
    print(json.dumps({'headers_archived':len(rows),'all_regenerated_exact':all(x['archive_sha256']==x['original_emission_sha256']for x in rows)}))
if __name__=='__main__':main()
