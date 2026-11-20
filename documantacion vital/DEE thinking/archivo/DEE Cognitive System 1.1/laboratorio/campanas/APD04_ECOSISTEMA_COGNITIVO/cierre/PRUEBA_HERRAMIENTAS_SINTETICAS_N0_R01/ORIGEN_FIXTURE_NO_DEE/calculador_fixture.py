import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
v={'fixture_not_DEE':True,'source_sha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),'new_native_ticks':0}
with a.out.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\n')
