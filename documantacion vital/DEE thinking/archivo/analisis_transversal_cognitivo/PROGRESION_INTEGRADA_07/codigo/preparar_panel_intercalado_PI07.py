"""Prepare literal heritage plan from its existing authority; no Native."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';file=C/'reproducibilidad/recetas/panel_12.json';recipe=json.loads(file.read_text('utf8'));steps=recipe['variants']['principal']['batches'][0]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=P/'control/PLAN_PANEL_INTERCALADO_PI07_R01.json'
 if out.exists():raise FileExistsError('Preserve prepared plan')
 plan={'schema':'DEE.PI07.heritage.actual_result_binding.prepared_plan.R01','status':'PREPARADO_NO_EJECUTADO','authority':{'path':str(file),'sha256':sha(file),'variant':'principal','native_receipt_expectations':recipe['variants']['principal']['native_receipt_expectations']},
 'phases':{'panel12':steps,'new_R03_next':{'label':'new_R03_next','literal':{'modo':'eci01-pi07-r03-episodio'},'maximum_native_ticks':1300,'feedback':'omit','actuator':'closed','not_extra_supply':True},'old_C2C_next':{'label':'old_C2C_next','literal':{'modo':'eci01-pi04-c2c-oportunidad'},'maximum_native_ticks':1500,'feedback':'real','actuator':'closed','not_extra_supply':True}},
 'preconditions':['Root chooses exact phase placement before material use; no selection target or answer goes to the actor.','Use one existing candidate, same organization, no reset or old re-teaching.','The old PI05 C2C environment has only ordinal28/30 and two actual offers; consumption must be recorded without resetting counters.','Existing extension helper26to30 is NOT a30to32resupply and must never be replayed as such.','Check current R03 ordinal/remaining explicitly; a new use consumes an actual registered offer.','A material regression stops and preserves that future; no query reader/answer changes to force a pass.'],
 'scope':'Prepared Root plan only. Exact historical input/decoder contracts and actual integer binding; positive/negative/zero FI all included. New R03/C2C phases are optional explicit material uses, not completed tests or new opportunities.','Native_executed':False}
 with out.open('x',encoding='utf8')as f:json.dump(plan,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'plan':str(out),'sha256':sha(out),'Native_executed':False}))
if __name__=='__main__':main()
