"""Execute selected frozen CPC6 trajectories ONLY on the official4.0 wheel.

The sole instrumentation adaptation is common.ROOT for wheel identity lookup.
No preparation, input, transition, decoder, criterion or reserve is changed.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sys


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--artifact-root',type=Path,required=True)
    p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.source.resolve()))
    import common
    common.ROOT=a.artifact_root.resolve()
    import life
    config=json.loads(a.config.read_text(encoding='utf-8'))
    selected=[config['cases'][i] for i in(0,1,4)]
    provenance={'schema':'DEE4.5.remote-port.baseline40.v1','instrument_sha256':sha(__file__),
                'source_directory':str(a.source),'source_hashes':{x.name:sha(x) for x in a.source.glob('*.py')},
                'source_config':str(a.config),'source_config_sha256':sha(a.config),
                'adaptation':'Only common.ROOT points to the verified official wheel artifact location; native and scientific code unchanged.',
                'cases':[x['id'] for x in selected],'compressed_snapshots':[],'results':[]}
    (a.out/'PROVENANCE.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    for case in selected:
        target=a.out/case['id'];r=life.run(case,target)
        for snapshot in target.glob('*.deetsnap'):
            digest=sha(snapshot);compressed=snapshot.with_name(snapshot.name+'.gz')
            with snapshot.open('rb') as src,compressed.open('wb') as raw:
                with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as dst:shutil.copyfileobj(src,dst,1048576)
            h=hashlib.sha256()
            with gzip.open(compressed,'rb') as src:
                for block in iter(lambda:src.read(1048576),b''):h.update(block)
            if h.hexdigest()!=digest:raise AssertionError('Compressed baseline snapshot differs')
            provenance['compressed_snapshots'].append({'path':str(compressed.relative_to(a.out)),
                'logical_sha256':digest,'encoded_sha256':sha(compressed),'logical_bytes':snapshot.stat().st_size,
                'encoded_bytes':compressed.stat().st_size,'gzip_crc_and_logical_hash_verified':True})
            snapshot.unlink()  # Only this worker's generated, already verified duplicate.
        provenance['results'].append({'case':case['id'],'path':str((target/'MEASUREMENTS.json').relative_to(a.out)),
                                    'sha256':sha(target/'MEASUREMENTS.json'),'final_physical':r['final_physical']})
        (a.out/'PROVENANCE.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    print(json.dumps({'status':'PASS','cases':len(provenance['results'])}))


if __name__=='__main__':main()
