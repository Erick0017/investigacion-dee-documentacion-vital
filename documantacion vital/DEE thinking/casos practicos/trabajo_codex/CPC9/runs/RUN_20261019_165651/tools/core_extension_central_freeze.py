from pathlib import Path
import hashlib,json
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE';MAT=RUN/'notes/core_extension_v2/materialized'
p=CORE/'configuraciones/RECUPERACION_EXTENSION_CONGELADA.json';v=json.loads(p.read_text(encoding='utf8'));rows=[]
for group,names in(('central_discovery',('open_same','closed_same','open_changed','closed_changed')),('central_confirmation',('H0_actual','report_omitted','reserved_open_changed','reserved_closed_changed'))):
 for name in names:
  relative='historico/CPC3/experimentos/comparacion_seleccion/'+group+'/'+name+'/MEASUREMENTS.json';b=(MAT/relative).read_bytes();old=json.loads(b);rows.append({'id':name,'input_configuration':old['configuration'],'primary':relative,'primary_sha256':hashlib.sha256(b).hexdigest(),'primary_top_keys':list(old)})
v['groups']['central']=rows;p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'central':len(rows)}))
