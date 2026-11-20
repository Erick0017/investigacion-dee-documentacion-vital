"""Pure localized supervisor revision; never executes the driver."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
src=H/'ejecutar_plan_PI10_R01.py';dst=H/'ejecutar_plan_PI10_R02.py'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='4b0847beeb0884883ff2ffdacd420e6fb658d436f5cd39b8eeb4f3ffaef79a1e'
t=src.read_text('utf8')
old="PROC=P9/'codigo/comprobar_procesos_adopcion_D_PI09_R01.py';PROC_SHA='9222b2fb422bb3c19d9ed4c5bf1785d2f987dd0d5533ddf9242600a563e22107'"
new="PROC=H/'comprobar_proceso_PI10_R02.py';PROC_SHA='21d41a1e429f135d100f17826258561dc9f98ca52a465cc2015f30efb5966adb'"
assert t.count(old)==1;t=t.replace(old,new)
old="'no_adoption':True,'outer_job_memory_limit_bytes'"
new="'technical_supervisor_revision':'R02 exact never-owned imported source exception; original strict used-owner guard retained','no_adoption':True,'outer_job_memory_limit_bytes'"
assert t.count(old)==1;t=t.replace(old,new);ast.parse(t)
if dst.exists():assert dst.read_text('utf8')==t
else:
 with dst.open('x',encoding='utf8')as f:f.write(t)
print(json.dumps({'file':str(dst),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'Native':0}))
