from pathlib import Path
import hashlib,json,shutil
P=Path(__file__).resolve().parents[1];code=P/'codigo';dst=P/'estados/candidato_R02/sistema/capacidades'
backup=code/'revisiones/ANTES_C2C_R01';backup.mkdir(exist_ok=False)
names=['pi04_coordinacion_central_C2C.py','pi04_sensor_central_C2C_R01.py','PROTOCOLO_PI04_C2C_R01.json']
old=code/'pi04_dispatcher.py';shutil.copy2(old,backup/old.name)
s=old.read_text(encoding='utf8').replace("('eci01-pi04-c2b-','pi04_coordinacion_simetrica_C2B'))", "('eci01-pi04-c2b-','pi04_coordinacion_simetrica_C2B'),\n         ('eci01-pi04-c2c-','pi04_coordinacion_central_C2C'))")
s=s.replace("'pi04_sensor_simetrico_C2B_R01.py']", "'pi04_sensor_simetrico_C2B_R01.py','pi04_sensor_central_C2C_R01.py']")
assert "('eci01-pi04-c2c-'"in s;old.write_text(s,encoding='utf8')
for name in names+['pi04_dispatcher.py']:
 if(dst/name).exists():shutil.copy2(dst/name,backup/('INSTALADO_'+name))
 shutil.copy2(code/name,dst/name)
proof={'only_isolated_code_changed':True,'new_Native_ticks':0,'files':{n:hashlib.sha256((dst/n).read_bytes()).hexdigest()for n in names+['pi04_dispatcher.py']}}
with(P/'control/INSTALACION_C2C_R01.json').open('x',encoding='utf8')as f:json.dump(proof,f,indent=2)
print(json.dumps(proof))
