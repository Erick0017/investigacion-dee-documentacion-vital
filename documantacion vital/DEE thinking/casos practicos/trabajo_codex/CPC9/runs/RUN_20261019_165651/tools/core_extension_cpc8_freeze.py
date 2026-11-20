from pathlib import Path
import hashlib,json
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE';MAT=RUN/'notes/core_extension_v2/materialized'
p=CORE/'configuraciones/RECUPERACION_EXTENSION_CONGELADA.json';v=json.loads(p.read_text(encoding='utf8'))
for group,names in(('qfm',('QFM_P01','QFM_H01','QFM_N01','QFM_C01','QFM_R01')),('l15',('L15_CAUSAL',))):
 rows=[]
 for name in names:
  relative='cpc8/resultados/cantidad/'+name+'/MEASUREMENTS.json'if group=='qfm'else'cpc8/resultados/diagnostico_L15_causal/MEASUREMENTS.json';path=MAT/relative;b=path.read_bytes()
  rows.append({'id':name,'input_configuration':{'case_id':name}if group=='qfm'else{},'primary':relative,'primary_sha256':hashlib.sha256(b).hexdigest(),'primary_top_keys':list(json.loads(b))})
 v['groups'][group]=rows
p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({g:len(v['groups'][g])for g in('qfm','l15')}))
