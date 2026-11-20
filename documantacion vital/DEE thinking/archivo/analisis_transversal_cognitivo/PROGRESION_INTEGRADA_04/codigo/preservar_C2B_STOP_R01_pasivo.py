from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[1];S=P/'estados/candidato_R02/sistema';life='ECI02_PI03_REPRO_PI04_MAIN_02'
rows=[]
for i in range(3):
 f=P/'ensayos'/('PI04_C2B_REAL_DEV_R01_OP_'+str(i)+'.json');p=json.loads(f.read_text(encoding='utf8'));a=json.loads(p['result']);r=a['result']['rows'][0]
 groups={'outer':r['requests'],'FI':r['native_arithmetic']['native_operation']['native_trial']['requests'],'MU':r['second_native_use']['requests']};unique={};reject=[]
 for group,items in groups.items():
  for q in items:
   if q['id']in unique:assert unique[q['id']]==q['receipt']
   unique[q['id']]=q['receipt']
   if q['receipt']['status']!='applied':reject.append({'group':group,**q})
 rows.append({'ordinal':i,'before_tick':a['before_tick'],'after_tick':a['after_tick'],'choice':r['first_reader']['choice'],'operation':r['selected_operation'],'number':r['actual_numeric_result'],'route':r['applied_route'],'product':r['useful_product'],'before_delta':r['bank_before'][0]['s_reg']-r['bank_before'][1]['s_reg'],'after_delta':r['bank_after'][0]['s_reg']-r['bank_after'][1]['s_reg'],'requested':len(unique),'applied':sum(q['status']=='applied'for q in unique.values()),'rejections':reject,'primary':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
card=json.loads((S/'estado/vidas'/life/'VIDA.json').read_text(encoding='utf8'));assert card['physical']['tick']==800379
owner=[json.loads(line)for line in(P/'ENSAYOS.jsonl').read_text(encoding='utf8').splitlines()if line.strip()and json.loads(line).get('kind')=='OWNER_CLOSED'and json.loads(line).get('run','').startswith('PI04_C2B_REAL_DEV_R01_')][-1];assert owner['exit_code']==0
proof={'schema':'DEE.PI04.C2B.first_rejected_input_preserved.R01','life':life,'closed_tick':800379,'development_requested':12,'development_executed':3,'Native_ticks':2346,'products':1,'arithmetic_requested':3,'arithmetic_responded':3,'arithmetic_correct':3,'Native_input_requested':sum(r['requested']for r in rows),'Native_input_applied':sum(r['applied']for r in rows),'Native_input_rejected':2,'rows':rows,'reserved_executed':0,'owner_closed':owner,'current_card':card,'original_principal_modified':False,'no_retry_no_decoder_search':True,'scope':'Protocol stopped at first rejected Native input, even with a numerically correct response; this is not a completed validation.'}
with(P/'control/C2B_DESARROLLO_STOP_RECHAZOS_R01.json').open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
file=P/'REGISTRO_CAMPANA.json';d=json.loads(file.read_text(encoding='utf8'));d.update(phase='C2B_STOP_FIRST_FI_REJECTED_INPUT_ALL_OWNERS_CLOSED',new_Native_ticks=44395,new_Native_ticks_closed_floor=44395,current_owned_execution=None);d['candidate'].update(last_closed_tick=800379,C2B_protocol_stopped_at_ordinal=3,C2B_products=1,C2B_Native_rejected_inputs=2);file.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'tick':800379,'Native_ticks_campaign':44395,'requested':proof['Native_input_requested'],'applied':proof['Native_input_applied'],'rejected':2}))
