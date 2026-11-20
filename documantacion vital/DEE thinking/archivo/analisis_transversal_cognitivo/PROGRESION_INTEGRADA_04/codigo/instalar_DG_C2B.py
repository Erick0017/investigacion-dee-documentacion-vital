"""Install bounded PI04 plugins only in the isolated experimental system."""
from pathlib import Path
import hashlib,json,shutil
P=Path(__file__).resolve().parent.parent
src=P/'codigo';dst=P/'estados/candidato_R02/sistema/capacidades'
files=['pi04_diagnostico_campo.py','pi04_coordinacion_simetrica_C2B.py','pi04_sensor_simetrico_C2B_R01.py','PROTOCOLO_PI04_C2B_R01.json']
backup=src/'revisiones/ANTES_DG_C2B';backup.mkdir(parents=True,exist_ok=False)
d=src/'pi04_dispatcher.py';shutil.copy2(d,backup/d.name)
s=d.read_text(encoding='utf-8')
s=s.replace("('eci01-pi04-c2-','pi04_coordinacion_adquirida'))", "('eci01-pi04-c2-','pi04_coordinacion_adquirida'),\n         ('eci01-pi04-dg-','pi04_diagnostico_campo'),\n         ('eci01-pi04-c2b-','pi04_coordinacion_simetrica_C2B'))")
s=s.replace("'pi04_selector_contextual_C2_R01.py']", "'pi04_selector_contextual_C2_R01.py','pi04_sensor_simetrico_C2B_R01.py']")
assert 'eci01-pi04-dg-' in s and 'eci01-pi04-c2b-' in s
d.write_text(s,encoding='utf-8')
for name in files+['pi04_dispatcher.py']:
    if (dst/name).exists():shutil.copy2(dst/name,backup/('INSTALADO_'+name))
    shutil.copy2(src/name,dst/name)
proof={'only_isolated_system_changed':str(dst),'files':{n:hashlib.sha256((dst/n).read_bytes()).hexdigest()for n in files+['pi04_dispatcher.py']},'new_Native_ticks':0,'original_system_changed':False}
(P/'control/INSTALACION_DG_C2B_R01.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
print(json.dumps(proof))
