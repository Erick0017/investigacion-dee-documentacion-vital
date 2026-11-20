from pathlib import Path
import hashlib,json
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE';MAT=RUN/'notes/core_extension_v2/materialized';rows=[]
for name in('CTS_R1_P11_NEW_CONTACT','CTS_R1_P12_NEW_FREE','CTS_R1_C14_SOURCE_NAME_OMITTED','CTS_R1_R31_NEW_HISTORY_CONTACT'):
 relative='cpc8/resultados/semantica/'+name+'/MEASUREMENTS.json';b=(MAT/relative).read_bytes();old=json.loads(b);rows.append({'id':name,'case':old['case'],'primary':relative,'primary_sha256':hashlib.sha256(b).hexdigest(),'frozen_source_root':'cpc8/resultados/semantica/'+name+'/executed_source','source_sha256':old['source_sha256']})
assert all(row['source_sha256']==rows[0]['source_sha256']for row in rows),'Use distinct processes for different executed source versions'
diagnostics=[]
for mode,name in(('cut','CTS_D31_MESSAGE_CUT'),('sham','CTS_D32_MESSAGE_SHAM'),('content','CTS_D33_MESSAGE_CONTENT')):
 relative='cpc8/resultados/semantica/'+name+'/MEASUREMENTS.json';b=(MAT/relative).read_bytes();diagnostics.append({'mode':mode,'id':name,'primary':relative,'primary_sha256':hashlib.sha256(b).hexdigest()})
v={'schema':'DEE_CORE.social.frozen.v1','cases':rows,'diagnostics':diagnostics,'input_information':'Only original experience/configuration reaches original participants; original expected primaries open after native run. Diagnostic parent generated during this recovery, not fetched from historical ZIP.'};(CORE/'configuraciones/RECUPERACION_SOCIAL_CONGELADA.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'cases':len(rows),'diagnostics':len(diagnostics)}))
