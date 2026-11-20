"""Inspect exact existing complete bytes after a documentary guard failure."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--evidence',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    prefix=args.evidence/'PREFIJO_COMPLETO.deetsnap.gz'
    encoded=prefix.read_bytes();decoded=gzip.decompress(encoded)
    proof=json.loads((args.evidence/'PREFIJO_TESTIGO.json').read_bytes())
    results=json.loads((args.evidence/'RESULTADOS.json').read_bytes())
    rows=[]
    for branch in results['branches']:
        p=args.evidence/('ARM_'+str(branch['index'])+'_'+branch['arm']['history']+'_'+str(branch['arm']['B_sign_auditor']))/'FUTURO_AL_FALLO_COMPLETO.deetsnap.gz'
        data=p.read_bytes();plain=gzip.decompress(data)
        rows.append({'index':branch['index'],'snapshot':p.relative_to(args.evidence).as_posix(),
            'encoded_bytes':len(data),'encoded_sha256':sha(data),'encoded_byte_identical_to_prefix':data==encoded,
            'decoded_bytes':len(plain),'decoded_sha256':sha(plain),'decoded_byte_identical_to_prefix':plain==decoded,
            'failure':branch['failure'],'physical_equal_to_prefix':branch['failure']['physical']==proof['physical']})
    record={'schema':'APD03.lexical_prefix_documentary_guard_diagnosis.N0.R01',
        'prefix':{'encoded_bytes':len(encoded),'encoded_sha256':sha(encoded),'decoded_bytes':len(decoded),'decoded_sha256':sha(decoded)},
        'prefix_witness':proof,'branches':rows,
        'all_six_complete_encoded_and_decoded_snapshots_identical':len(rows)==6 and all(r['encoded_byte_identical_to_prefix']and r['decoded_byte_identical_to_prefix']and r['physical_equal_to_prefix']for r in rows),
        'new_native_ticks':0,'new_states_loaded_into_Runtime':0,
        'scope':'Full encoded/decoded complete snapshot byte equality, not merely RAW/clocks. The previous guard compared a separately computed in-memory metadata hash and rejected every branch before any branch-specific teaching/query. Its exact differing key remains unmeasured.'}
    data=(json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    with args.output.open('xb')as stream:stream.write(data)
    print(json.dumps({'output':str(args.output),'bytes':len(data),'sha256':sha(data),
        'all_six_complete_encoded_and_decoded_snapshots_identical':record['all_six_complete_encoded_and_decoded_snapshots_identical']}))


if __name__=='__main__':main()
