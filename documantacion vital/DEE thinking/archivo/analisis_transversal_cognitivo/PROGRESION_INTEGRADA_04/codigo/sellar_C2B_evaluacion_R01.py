from pathlib import Path
import hashlib,json,shutil,datetime
P=Path(__file__).resolve().parents[1];S=P/'estados/candidato_R02/sistema';f=S/'capacidades/PROTOCOLO_PI04_C2B_R01.json'
cal=json.loads((P/'control/PI04_C2BCAL_R01.json').read_text(encoding='utf8'))
assert cal['actual_owner_closed']and cal['new_Native_ticks']==450
assert [(r['input'],r['reader']['choice'])for r in cal['Q']]==[(0,-1),(4,1),(6,1)]
assert all(len(r['requests'])==5 and all(q['receipt']['status']=='applied'for q in r['requests'])for r in cal['Q'])
criteria=P/'control/C2B_CRITERIOS_PRE_EVALUACION_R01.json';assert json.loads(criteria.read_text(encoding='utf8'))['executed_results']is None
old=f.read_bytes();p=json.loads(old);assert p['status']=='SEALED_FOR_CALIBRATION'and len(p['schedule'])==26
for n,h in p['dependencies_sha256'].items():assert hashlib.sha256((f.parent/n).read_bytes()).hexdigest()==h
archive=P/'codigo/revisiones/C2B_PROTOCOLO_CAL_ANTES_EVAL_R01';archive.mkdir(exist_ok=False);(archive/f.name).write_bytes(old)
p['status']='SEALED_FOR_EVALUATION';f.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
proof={'schema':'DEE.PI04.C2B.sealed_evaluation.R01','local':datetime.datetime.now().astimezone().isoformat(),'calibration':str(P/'control/PI04_C2BCAL_R01.json'),'protocol_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'criteria_sha256':hashlib.sha256(criteria.read_bytes()).hexdigest(),'only_status_changed':True,'calibration_history_not_transferred_to_candidate':True,'Native_reserve_executed':0,'new_Native_ticks':0}
with(P/'control/C2B_SELLADO_EVALUACION_R01.json').open('x',encoding='utf8')as out:json.dump(proof,out,ensure_ascii=False,indent=2)
ledger=P/'REGISTRO_CAMPANA.json';d=json.loads(ledger.read_text(encoding='utf8'));d.update(phase='C2B_DEVELOPMENT_RUNNING_NEW_INTERFACE_SAME_TRAJECTORY',new_Native_ticks=42049,new_Native_ticks_closed_floor=42049);ledger.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(proof,ensure_ascii=False))
