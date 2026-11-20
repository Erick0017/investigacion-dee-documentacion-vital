"""Decode exported data only; no Native, network, inference or state mutation."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def safe(p):
 p=p.resolve();assert p.is_relative_to(ROOT/'evidencia')
 assert not any(q.is_symlink()for q in(p,*p.parents));return p
def main():
 p=argparse.ArgumentParser();p.add_argument('--root-run',action='store_true',required=True)
 for n in('hex-data','meta','output'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();src,mp,dst=map(safe,(a.hex_data,a.meta,a.output));assert not dst.exists()
 m=json.loads(mp.read_text('utf8'));raw=bytes.fromhex(src.read_text('ascii'));w=json.loads(raw)
 assert len(raw)==m['meta']['bytes'] and w['checkpoint_id']==m['meta']['checkpointId']
 assert w['native_tick']==0 and w['bridge']['session_id']==m['session_id']
 assert w['boundary']['completed_opportunities']==m['expected_completed']
 assert w['boundary']['next_opportunity']==m['expected_completed']+1
 assert w['boundary']['uncertain'] is False and w['S']['completedCycles']==m['expected_completed']
 with dst.open('xb')as f:f.write(raw)
 result={'file':str(dst),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'boundary':w['boundary'],
  'Native_calls':0,'model_calls':0,'source_meta':str(mp),'source_hex_sha256':hashlib.sha256(src.read_bytes()).hexdigest()}
 with dst.with_suffix('.root_provenance.json').open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps(result))
if __name__=='__main__':main()
