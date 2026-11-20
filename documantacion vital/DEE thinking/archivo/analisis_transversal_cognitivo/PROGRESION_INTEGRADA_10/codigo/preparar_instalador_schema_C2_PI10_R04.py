"""Pure prospective correction of pre-write schema error; R03 retained."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;src=H/'incorporar_reproducibilidad_estable_PI10_R03.py';out=H/'incorporar_reproducibilidad_estable_PI10_R04.py';text=src.read_text('utf8');old="contrast=read(contrastfile);rr=contrast['groups']['real'];nn=contrast['groups']['nonfailure'];need(rr['complete_horizon']and nn['complete_horizon']and rr['observed']==nn['observed']==12 and rr['reserved_useful']==9 and rr['physical_delivered']==10 and rr['attributed_useful']==9,'Actual closed paired12 contrast');gain=rr['reserved_useful']-nn['reserved_useful'];physicalgain=rr['physical_delivered']-nn['physical_delivered'];need(gain>=2 and physicalgain>=1,'Prospective bounded gain gate not met; do not register as accepted material')";new="rr,nn,gain,physicalgain=load('PI10_registration_actual_C2_schema',H/'pi10_registro_gate_c2_R04.py').check(contrastfile,P,recalc)";assert text.count(old)==1;text=text.replace(old,new);ast.parse(text)
if out.exists():assert out.read_text('utf8')==text
else:
 with out.open('x',encoding='utf8')as f:f.write(text)
print(json.dumps({'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'Native':0}))
