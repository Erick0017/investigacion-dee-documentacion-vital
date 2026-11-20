"""New passive stdlib decoder for preserved Root hex transport, not an engine.

The historical inline capture is not re-executed. Requires actual expected byte
count/SHA, strict hex and full C02 JSON. Never overwrites the original World.
"""
from pathlib import Path
import argparse,hashlib,json,re
def decode(source,expected_bytes,expected_sha256):
 text=Path(source).read_text('ascii');compact=''.join(text.split())
 if not compact or len(compact)%2 or re.fullmatch(r'[0-9a-fA-F]+',compact)is None:raise ValueError('Strict complete ASCII hex required')
 if len(compact)>128000000:raise ValueError('Bounded transport input required')
 raw=bytes.fromhex(compact);actual=hashlib.sha256(raw).hexdigest()
 if len(raw)!=expected_bytes or actual!=expected_sha256:raise ValueError('Transport length or SHA differs from actual expected checkpoint')
 def invalid(value):raise ValueError('Nonfinite JSON constant '+value)
 value=json.loads(raw.decode('utf8'),parse_constant=invalid)
 if value.get('schema')!='DEE.RBX01.C02.world_checkpoint.v1':raise ValueError('Full literal C02 World JSON required')
 return raw,value
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--hex',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 p.add_argument('--expected-bytes',type=int,required=True);p.add_argument('--expected-sha256',required=True);a=p.parse_args()
 if a.output.exists()or not a.output.parent.is_dir():raise ValueError('New output file with existing parent required')
 raw,value=decode(a.hex,a.expected_bytes,a.expected_sha256)
 with a.output.open('xb')as f:f.write(raw)
 print(json.dumps(dict(file=str(a.output),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
  completed=value['boundary']['completed_opportunities'],Native_calls=0,model_calls=0,MCP_calls=0,mode='PASSIVE_HEX_DECODING_NOT_CAPTURE_OR_WORLD_REPLAY'),indent=2))
