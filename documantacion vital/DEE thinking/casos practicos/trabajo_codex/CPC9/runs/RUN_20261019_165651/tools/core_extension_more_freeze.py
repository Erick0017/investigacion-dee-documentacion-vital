"""Freeze additional original inputs from immutable staged primaries before execution."""
from pathlib import Path
import hashlib,json
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE';MAT=RUN/'notes/core_extension_v2/materialized'
p=CORE/'configuraciones/RECUPERACION_EXTENSION_CONGELADA.json';v=json.loads(p.read_text(encoding='utf8'))
groups={
 'capacity':[(f'historico/CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/resultados/{group}/{name}/MEASUREMENTS.json','case')for group,name in(('capacity_discovery','CAP_D65_N131_G2'),('capacity_confirmation','CAP_C65_UNPAIRED'),('capacity_confirmation','CAP_C65_NO_EVENT'),('capacity_confirmation','CAP_H65_NEW_HISTORY_Q9'))],
 'longitudinal':[(f'historico/CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/resultados/capacity_longitudinal/{name}/MEASUREMENTS.json','case')for name in('CAP_L65_32_THEN33','CAP_L65_NO_EARLY_QUERY')],
 'policy':[(f'historico/CPC3/experimentos/seleccion_revisable/casos/{name}/MEASUREMENTS.json','configuration')for name in('D_P_GOOD_POS','D_P_BAD_POS','D_P_GOOD_NEG','D_P_BAD_NEG','D_LATE_ACTION_CUT','D_NO_ACTUAL','R_TRANSLATED_BAD','R_TRANSLATED_GOOD')],
 'native_loop':[(f'historico/CPC3/experimentos/comparacion_seleccion/{group}/{name}/MEASUREMENTS.json',None)for group,name in(('native_discovery','AB_changed'),('native_discovery','BA_changed'),('native_confirmation','H0_changed'),('native_confirmation','query_omitted'),('native_confirmation','selected_Q_cut'),('native_confirmation','unselected_P_cut'),('native_confirmation','reserved_AB'),('native_confirmation','reserved_BA'))],
}
for group,items in groups.items():
 rows=[]
 for relative,key in items:
  path=MAT/relative;b=path.read_bytes();old=json.loads(b);name=path.parent.name
  if group=='native_loop':
   config={k:old['metadata'][k]for k in('origin','context','report','consequence','history','distance','selected_cut')};config['post_query']=old['metadata'].get('post_query',False);config['query']=old['metadata']['query_enabled'];config['consequence_enabled']=old['metadata']['consequence_enabled']
  else:config=old[key]
  rows.append({'id':name,'input_configuration':config,'primary':relative,'primary_sha256':hashlib.sha256(b).hexdigest(),'primary_top_keys':list(old)})
 v['groups'][group]=rows
p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({g:len(v['groups'][g])for g in groups}))
