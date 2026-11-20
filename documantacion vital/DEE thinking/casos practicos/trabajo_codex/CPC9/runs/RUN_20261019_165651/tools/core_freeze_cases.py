"""Freeze historical INPUT configurations, not expected responses, before recovery."""
from pathlib import Path
import gzip,json,base64,hashlib
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE';idx=json.loads((CORE/'documentacion/INDICE_MIEMBROS.json').read_text())['paths']
groups={
 'cpc4':{n:'historico/CPC4/ampliaciones/02_APRENDIZAJE_CONTINUO_RED_ABCD/resultados/red/fixed_counterflow01/'+n+'/MEASUREMENTS.json'for n in('FILTER_FLAT','NO_FILTER_FLAT','SHAM_ZERO_FLAT','RESERVED_FILTER_FLAT')},
 'cpc5':{n:('historico/CPC5/resultados/compound_reuse_D01/MEASUREMENTS.json'if n=='COMP_REUSE_CORE_D01'else'historico/CPC5/resultados/compound_reuse_confirmation/'+n+'/MEASUREMENTS.json')for n in('COMP_REUSE_CORE_D01','CORE_UNCOUPLED_MATCHED','CORE_K3_OPPOSITE','CORE_K3_UNPAIRED','CORE_LATE_MESSAGE_REMOVE147','CORE_LATE_MESSAGE_SHAM147','CORE_RESERVED_ORDER_QUERY7')},
 'cpc6':{n:'historico/CPC6/resultados/R03_WORD_BUS_V2/'+n+'/MEASUREMENTS.json'for n in('WR01_BA_balanced_Qminus','WR03_AB_balanced_Qminus','WR04_BA_no_repeat','WR05_BA_unpaired_name')},
 'sem01':{n:'historico/CPC3/experimentos/SEM01_SIGNIFICADO_ADQUIRIDO/resultados/confirmacion/'+n+'/MEASUREMENTS.json'for n in('A_future_UV','B_future_UV','A_no_action','empty_UV','unpaired_UV','RESERVED_A_codec7_shift','RESERVED_B_codec7_order_shift')},
}
needed={idx[p]['sha256']:p for d in groups.values()for p in d.values()};fixtures={}
with gzip.open(CORE/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz','rt',encoding='ascii')as f:
 for line in f:
  v=json.loads(line);h=v['sha256']
  if h not in needed:continue
  b=base64.b64decode(v['base64']);assert hashlib.sha256(b).hexdigest()==h;fixtures[needed[h]]=json.loads(b)
out={'schema':'DEE_CORE.recovery_inputs.frozen.v1','cases':{},'scope':'Exact historical environmental/experience inputs extracted during preparation. Native participants receive physical events only. Expected observations are not part of this file.'}
for group,items in groups.items():
 out['cases'][group]=[]
 for name,p in items.items():
  old=fixtures[p];case=old['case']
  if group=='cpc4':case={**case,'translation':old['translation']}
  out['cases'][group].append({'id':name,'input_configuration':case,'original_primary':p,'original_primary_sha256':idx[p]['sha256']})
dest=CORE/'configuraciones/RECUPERACION_CONGELADA.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'groups':{k:len(v)for k,v in out['cases'].items()}}))
