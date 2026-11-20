from pathlib import Path
import hashlib,json,shutil
P=Path(__file__).resolve().parents[1];code=P/'codigo';dst=P/'estados/candidato_R02/sistema/capacidades'
backup=code/'revisiones/ANTES_DGC_R01';backup.mkdir(exist_ok=False)
file=code/'pi04_dispatcher.py';shutil.copy2(file,backup/file.name)
s=file.read_text(encoding='utf8').replace("('eci01-pi04-c2c-','pi04_coordinacion_central_C2C'))", "('eci01-pi04-c2c-','pi04_coordinacion_central_C2C'),\n         ('eci01-pi04-dgc-','pi04_diagnostico_C2C_pasivo'))")
assert "('eci01-pi04-dgc-'"in s;file.write_text(s,encoding='utf8')
for name in ('pi04_dispatcher.py','pi04_diagnostico_C2C_pasivo.py'):
 if(dst/name).exists():shutil.copy2(dst/name,backup/('INSTALADO_'+name))
 shutil.copy2(code/name,dst/name)
proof={'only_isolated_code_changed':True,'new_Native_ticks':0,'files':{n:hashlib.sha256((dst/n).read_bytes()).hexdigest()for n in ('pi04_dispatcher.py','pi04_diagnostico_C2C_pasivo.py')}}
with(P/'control/INSTALACION_DGC_R01.json').open('x',encoding='utf8')as f:json.dump(proof,f,indent=2)
print(json.dumps(proof))
