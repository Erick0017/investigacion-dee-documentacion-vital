from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
P=Path(__file__).resolve().parents[1]
protocol=P/'codigo/PROTOCOLO_PI07_R02.json'
steps=[{'label':'INICIAR','literal':{'modo':'eci01-pi07-iniciar','brazo':'real','registro_global':True},'max_native_ticks':0}]
steps += [{'label':f'EP{i:02d}','literal':{'modo':'eci01-pi07-episodio'},'max_native_ticks':1300} for i in range(8)]
d={'schema':'DEE.PI07.fixed_phase_plan.v1','status':'SEALED','initial_tick':824914,'max_native_ticks':10400,'steps':steps,'description':'R02 primeras ocho oportunidades de adquisición en candidata continua; decisiones físicas Native, ninguna acción forzada. Protocolo congelado previo a respuestas.','registration_utc':datetime.now(timezone.utc).isoformat(),'source_proof':{'protocol':str(protocol),'sha256':hashlib.sha256(protocol.read_bytes()).hexdigest()}}
out=P/'control/PLAN_ADQUISICION_PI07_R02.json'
with out.open('x',encoding='utf8') as f: json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
print(str(out))
