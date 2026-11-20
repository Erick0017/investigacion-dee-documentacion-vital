"""Add required inherited CPC source closure to the un-applied PRE34 registrar."""
from pathlib import Path
import hashlib
H=Path(__file__).resolve().parent;source=H/'incorporar_RP_R03_PI07_R02.py';target=H/'incorporar_RP_R03_PI07_R03.py'
if target.exists():raise FileExistsError('Preserve prepared revision')
s=source.read_text('utf-8-sig')
old="for parent in(S/'app',S/'capacidades',S/'contratos'):"
new="for parent in(S/'app',S/'capacidades',S/'contratos',S/'organizaciones'):"
if s.count(old)!=1:raise ValueError('Exact source-loop revision only')
s=s.replace(old,new).replace("p.suffix in('.py','.json')","p.suffix in('.py','.json','.eventos')")
s=s.replace('RP_R03_INCORPORADA_PI07_R02.json','RP_R03_INCORPORADA_PI07_R03.json')
compile(s,str(target),'exec');target.write_text(s,encoding='utf8');print(str(target));print(hashlib.sha256(target.read_bytes()).hexdigest())
