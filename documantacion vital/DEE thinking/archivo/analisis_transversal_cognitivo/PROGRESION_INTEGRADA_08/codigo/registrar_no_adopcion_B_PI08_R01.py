"""Root actual no-adoption decision, from the closed scientific gate proof.

Writes campaign evidence only; no selector, source, world, request or import.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

P=Path(__file__).resolve().parents[1]
C=P.parents[2]/'DEE Cognitive 2.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))

evaluation=P/'control/EVALUACION_B_ACTUAL_PI08_R01.json'
panel=P/'control/PI08_B_CONSERVACION_R02.json'
if sha(evaluation)!='af9c9c72d8675b7fa68dbb864d40e81aea0f8840e7a95e56974ce7d8ddd9ca46':
    raise ValueError('Actual frozen evaluation required')
if sha(panel)!='bd9b211b5b17fb4f140478b88b7924ea1df54c993f1a617b020031caec07030a':
    raise ValueError('Actual closed conservation witness required')
e=read(evaluation);p=read(panel)
if not p['closed'] or p['criteria_met'] or p['panel_correct']!=10 or p['panel_witnesses']!=12:
    raise ValueError('Do not infer a failure/adoption from a planned protocol')
active=C/'sistema/estado/ACTIVO.json';a=read(active)
if a['life_id']!='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01' or a['tick']!=861426:
    raise ValueError('A later actual main must not be replaced or described as A')
card=C/'sistema/estado/vidas'/a['life_id']/'VIDA.json'
snap=C/'sistema'/a['snapshot']
if sha(snap)!=a['snapshot_sha256']:
    raise ValueError('Current adopted A snapshot does not match its selector')
proof=P/'control/DECISION_NO_ADOPCION_B_PI08_R01.json'
data={'schema':'DEE.PI08.actual_no_adoption.B.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),
      'approved_for_adoption':False,'decision_executed':'No B deployment or selection; retain already committed A.',
      'actual_principal':a,'actual_card_sha256':sha(card),'actual_active_sha256':sha(active),
      'evidence':[{'path':str(x),'sha256':sha(x)}for x in(evaluation,panel)],
      'positive_scope':'B real18 shows bounded bidirectional revision and useful contingency, 14/18 versus13/18 constant-nonfailure and9/18 fixed yoke; material contextual WSLS also14/18.',
      'reason':'Precommitted representative availability criterion not met:10/12. SUM6+7 gave7; subsequent DIF used that actual7 and gave2. This is one upstream arithmetic error and its transported consequence, not two independent losses.',
      'not_inferred':['No global memory erasure or universal incapacity.','No attribution of this error uniquely to B without an adequate control.','No B memories, outputs or observer maps inserted into A.'],
      'current_positive_scope_preserved':'A consolidation, migrated fixed FI access, C2C32 transaction and inherited acquired R03 remain adopted at their actual tested cuts.',
      'dormant_operational_B_code':'Prepared and preserved, not deployed. All B adoption/public-main helpers remain unexecuted.',
      'B_reproduction':'Actual four-arm Native executions retained. New RP B recipe requirements/recalculation available; new CLI material replay remains pending.',
      'new_Native_ticks':0,'DEE_imports':0,'selectors_or_operational_states_modified':False}
with proof.open('x',encoding='utf8')as out:json.dump(data,out,ensure_ascii=False,indent=2);out.write('\n')
print(json.dumps({'proof':str(proof),'sha256':sha(proof),'actual_principal':a['life_id'],'T':a['tick'],'new_Native_ticks':0}))
