"""Minimal prospective AI-only clock revision before its first opportunity."""
from pathlib import Path
import ast,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy_change(old,new,replacements):
 a=ROOT/old;b=ROOT/new;assert not b.exists(),'New revision only'
 before=sha(a);text=a.read_text('utf8')
 for x,y in replacements:
  assert x in text,(old,x);text=text.replace(x,y)
 ast.parse(text);b.write_text(text,encoding='utf8',newline='');assert sha(a)==before
 return dict(original=old,original_sha256=before,original_preserved=True,new=new,new_sha256=sha(b))
files=[copy_change('control/orquestar_comparador_C02_R05.py','control/orquestar_comparador_C02_R06.py',[
 ('HARD_FINISH=1794766500','HARD_FINISH=1794773700'),('2026-11-15 18:15UTC','2026-11-15 20:15UTC'),
 ('puente/run_comparador_C02_R03.py','puente/run_comparador_C02_R04.py'),('R05 resumed deadline','R06 resumed deadline')]),
 copy_change('puente/run_comparador_C02_R03.py','puente/run_comparador_C02_R04.py',[
 ('MAX_CUTOFF=1794766500','MAX_CUTOFF=1794773700'),('2026-11-15 18:15 UTC','2026-11-15 20:15 UTC'),
 ('protocolo/PRESUPUESTO_AI_C02_R05.json','protocolo/PRESUPUESTO_AI_C02_R06.json'),
 ('puente/run_comparador_C02_R03.py','puente/run_comparador_C02_R04.py'),
 ('DEE.RBX01.C02.AI_resumed_budget.R05','DEE.RBX01.C02.AI_resumed_budget.R06')])]
quota_path=ROOT/'comparadores/CUOTA_LLM_C02.json';quota=json.loads(quota_path.read_text('utf8'))
assert quota['limit']==128
old_budget=ROOT/'protocolo/PRESUPUESTO_AI_C02_R05.json'
budget=json.loads(old_budget.read_text('utf8'));budget.update(
 schema='DEE.RBX01.C02.AI_resumed_budget.R06',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 reason='Root reports GUI approval completed only2026-11-15T18:01:51UTC(g6:302); AI world remained unstarted. A sufficient fixed prospective AI window is authorized before ANY AI opportunity.',
 AI_absolute_cutoff_epoch=1794773700,AI_absolute_cutoff_utc='2026-11-15T20:15:00+00:00',
 prior_R05_budget_preserved=dict(path='protocolo/PRESUPUESTO_AI_C02_R05.json',sha256=sha(old_budget),
  cutoff_epoch=1794766500,executed_AI_opportunities_reported_by_Root=0,
  not_used_for_AI_due_to_late_GUI_approval=True),
 expired_or_insufficient_windows=[dict(epoch=1794744900,utc='2026-11-15T12:15:00+00:00',reason='Missed during system approval interruption'),
  dict(epoch=1794766500,utc='2026-11-15T18:15:00+00:00',reason='Only13minutes remained at GUI approval; replaced prospectively before firstAI, not retrospectively extended')],
 quota_before_R06=dict(path='comparadores/CUOTA_LLM_C02.json',sha256=sha(quota_path),used=quota['used'],limit=quota['limit']),
 files=files,new_GUI_launches_authorized=0,scientific_criteria_changed=False,
 postprocessing='Video and QC remain follow-up processing; this is the fixed model/AI execution deadline, not a Native extension.')
assert budget['new_Native_ticks_authorized']==0 and budget['global_LLM_call_limit']==128 and budget['AI_opportunities']==18
out=ROOT/'protocolo/PRESUPUESTO_AI_C02_R06.json';assert not out.exists();out.write_text(json.dumps(budget,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(files=files,budget=str(out),budget_sha256=sha(out),quota_used_before=quota['used'],AI_cutoff_epoch=1794773700),indent=2))
