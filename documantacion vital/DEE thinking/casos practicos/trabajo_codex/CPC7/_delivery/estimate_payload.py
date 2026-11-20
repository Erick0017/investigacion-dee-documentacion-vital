"""Live engineering size estimate, not a candidate or scientific verification."""
import argparse,json,hashlib,sys,time,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src/packaging'))
from bundle import select,put,sha,BLOCK

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--output',type=Path,required=True);a=p.parse_args();started=time.monotonic()
logical=json.loads((a.stage/'LOGICAL_STATES_CPC7.json').read_text(encoding='utf-8'))
states={row['logical_path']:row for row in logical['states']}
files,excluded=select(ROOT);payload=[];pending=[];unstable=[]
for path,rel in files:
    if rel.startswith(('resultados/','checkpoints/')) and rel.endswith('.deetsnap'):
        if rel in states:payload.append((a.stage/'encoded'/Path(states[rel]['encoded_path']),states[rel]['encoded_path']))
        else:pending.append({'path':rel,'bytes':path.stat().st_size})
    else:payload.append((path,rel))
compressed=0;expanded=0
for path,rel in payload:
    size=path.stat().st_size;processor=zlib.compressobj(9,zlib.DEFLATED,-15);encoded=0;read=0
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(BLOCK),b''):encoded+=len(processor.compress(block));read+=len(block)
    encoded+=len(processor.flush());compressed+=encoded;expanded+=read
    if size!=read or path.stat().st_size!=size:unstable.append(rel)
headers=sum(98+2*len(('CPC7/'+rel).encode('utf-8')) for _,rel in payload)
# Conservative explicit metadata allowance; not invented source hashes or data.
metadata_expanded=2*1024*1024;metadata_compressed=512*1024
result={'schema':'CPC7.live-size-estimate.v1','classification':'APPROXIMATION_NOT_A_RELEASE',
 'native_worlds_executed':0,'staged_snapshots':len(states),
 'staged_logical_bytes':logical['logical_bytes'],'staged_encoded_bytes':logical['encoded_bytes'],
 'selected_source_bytes_at_inventory':sum(path.stat().st_size for path,_ in files),
 'known_payload_expanded_bytes':expanded,'deflated_payload_bytes_measured':compressed,
 'estimated_ZIP_headers_bytes':headers,'metadata_expanded_allowance_bytes':metadata_expanded,
 'metadata_compressed_allowance_bytes':metadata_compressed,
 'estimated_ZIP_bytes_for_staged_cut':compressed+headers+metadata_compressed,
 'estimated_expanded_bytes_for_staged_cut':expanded+metadata_expanded,
 'not_yet_staged_snapshots':pending,'not_yet_staged_bytes':sum(x['bytes'] for x in pending),
 'files_that_changed_size_during_estimate':unstable,'selection_exclusions':excluded,
 'source_sha256':sha(Path(__file__)),'elapsed_seconds':time.monotonic()-started,
 'scope':'No archive built. Current ordinary files and exact staged encodings were deflated to counters only. Concurrent additions, final reports/manifests and corrections can change final size. Unstaged snapshots are listed, not silently represented as archived.'}
put(a.output,result);print(json.dumps(result,ensure_ascii=False,indent=2))
