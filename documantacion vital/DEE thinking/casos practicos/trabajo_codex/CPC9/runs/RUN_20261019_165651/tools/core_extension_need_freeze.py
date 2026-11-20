from pathlib import Path
import hashlib,json
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE';MAT=RUN/'notes/core_extension_v2/materialized';p=CORE/'configuraciones/RECUPERACION_EXTENSION_CONGELADA.json';v=json.loads(p.read_text(encoding='utf8'))
groups={'need':[(g,n)for g,n in(('comparison_discovery','NEED_D01_CURRENT_MATCH'),('comparison_discovery','NEED_D02_CURRENT_MISMATCH'),('comparison_confirm','NEED_C02_SOURCE_NONE'),('comparison_confirm','NEED_C05_NO_EXPECTATION_HISTORY'),('comparison_confirm','NEED_C07_FORMED_QUESTION_CUT'),('comparison_confirm','NEED_C08_FORMED_QUESTION_SHAM'),('comparison_confirm','NEED_H01_OPPOSITE_HISTORY_NEW_LOCATION'))], 'missing':[('missing_actual_fallback',n)for n in('FALL_D01_MISSING_ACTUAL','FALL_C01_CURRENT_MATCH','FALL_C02_CURRENT_MISMATCH','FALL_C03_MISSING_ACTUAL_SOURCE_NONE','FALL_C04_READER_FAILURE','FALL_H01_OPPOSITE_HISTORY_LOCATION')]}
for group,items in groups.items():
 rows=[]
 for folder,name in items:
  relative='historico/CPC7/resultados/endogenous/'+folder+'/'+name+'/MEASUREMENTS.json';b=(MAT/relative).read_bytes();old=json.loads(b);rows.append({'id':name,'input_configuration':old['case'],'primary':relative,'primary_sha256':hashlib.sha256(b).hexdigest(),'primary_top_keys':list(old)})
 v['groups'][group]=rows
p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({g:len(v['groups'][g])for g in groups}))
