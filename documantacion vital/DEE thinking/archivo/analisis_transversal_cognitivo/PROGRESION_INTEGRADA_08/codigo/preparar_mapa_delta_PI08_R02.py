"""Use the reviewed explicit lifecycle-release adapter in the bounded map."""
from pathlib import Path
import hashlib
H=Path(__file__).resolve().parent;source=H/'mapear_delta_operativo_PI08_R01.py';target=H/'mapear_delta_operativo_PI08_R02.py'
if target.exists():raise FileExistsError('Prepared bounded-map revision preserved')
s=source.read_text('utf8');old="'app/pi08_identidad_c2c_R01.py':H/'pi08_identidad_c2c_R01.py'";new="'app/pi08_identidad_c2c_R01.py':H/'pi08_identidad_c2c_R02.py'"
if old not in s:raise ValueError('Exact identity source override required')
s=s.replace(old,new);compile(s,str(target),'exec');target.write_text(s,encoding='utf8');print(str(target));print(hashlib.sha256(target.read_bytes()).hexdigest())
