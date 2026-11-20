"""Preserve the running PRE R01; derive POST with exact stored transport bytes."""
from pathlib import Path
import hashlib
H=Path(__file__).resolve().parent;source=H/'controlar_A1_por_Cola_PI08_R01.py';target=H/'controlar_A1_por_Cola_PI08_R02.py'
if target.exists():raise FileExistsError('Prepared POSTrevision preserved')
s=source.read_text('utf8')
old="  payload={'operacion':'sesion','situaciones':[literal],'actuador':'closed','retorno':'omit'}\n  admission=owner.q.put(identifier,payload);after=owner.q.get(identifier)"
new="  payload=json.loads(before['payload'])\n  if payload.get('operacion')!='sesion'or payload.get('situaciones')!=[literal]or payload.get('actuador','closed')!='closed'or payload.get('retorno','real')not in('real','omit'):raise ValueError('Actual completed transport must match the fixed literal; never invent feedback/settings')\n  admission=owner.q.put(identifier,payload);after=owner.q.get(identifier)"
if old not in s:raise ValueError('Exact PRE R01 transport helper source required')
s=s.replace(old,new).replace("'PI08_A1_'+args.fase.upper()+'CONTROL_REAL_R01.json'","'PI08_A1_'+args.fase.upper()+'CONTROL_REAL_R02.json'")
compile(s,str(target),'exec');target.write_text(s,encoding='utf8');print(str(target));print(hashlib.sha256(target.read_bytes()).hexdigest())
