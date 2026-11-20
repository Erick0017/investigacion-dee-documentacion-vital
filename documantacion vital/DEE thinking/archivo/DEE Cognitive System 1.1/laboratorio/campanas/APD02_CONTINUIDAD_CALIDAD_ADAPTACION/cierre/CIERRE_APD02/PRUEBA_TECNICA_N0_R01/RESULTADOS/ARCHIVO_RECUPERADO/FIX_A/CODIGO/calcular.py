"""Technical CAS fixture only: external Python numbers, no DEE capability."""
import argparse,gzip,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.exists():raise FileExistsError('Do not overwrite fixture result')
values=json.loads(gzip.decompress(a.evidence.read_bytes()))
result={'fixture_only':True,'native_ticks':0,'values':values,'external_Python_sum':sum(values)}
a.output.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
