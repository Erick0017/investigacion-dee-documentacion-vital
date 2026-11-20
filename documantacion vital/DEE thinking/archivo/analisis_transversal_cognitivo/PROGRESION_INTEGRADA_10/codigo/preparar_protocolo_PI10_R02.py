"""Prospective Root-ordered R02 draft only; no DEE/Native imports."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
H=Path(__file__).resolve().parent;out=H/'PROTOCOLO_PI10_R02.json';assert not out.exists()
Z='threat';X='falsecue';O='none'
groups=[('need',[X,Z,O,X]),('bypass',[Z,Z,O,Z]),('need_return',[Z,X,Z,O])]
schedule=[]
for regime,cues in groups:
    for k,cue in enumerate(cues):
        n=len(schedule);schedule.append({'ordinal':n,'regime':regime,'cue':cue,'role':'adaptation'if k==0 else'reserved','left':16+((7*n+3)%5),'right':3+((5*n+2)%9)})
for regime,cue in[('need',Z),('need',X),('bypass',Z),('bypass',X),('need_return',Z),('need_return',O)]:
    n=len(schedule);schedule.append({'ordinal':n,'regime':regime,'cue':cue,'role':'operational_future','left':16+((7*n+3)%5),'right':3+((5*n+2)%9)})
cal=[]
for n,((cue),(left,right))in enumerate(zip([Z,X,Z,O,X],[(18,5),(19,6),(16,7),(20,7),(17,6)])):
    cal.append({'ordinal':n,'regime':'need','cue':cue,'role':'diagnostic_forced','left':left,'right':right})
pins={'pi10_consulta_adaptativa_R02.py':'f7ba09cfea3ea93337ead47368ebbd9baba71b8590787aafe4515e6261cedf06',
 'pi10_dos_trazas_legales_R01.py':'139d9232d9261d699b1cbcfe5d7adf81e61f25110e432e622af6bd659f2edf90',
 'pi10_entorno_dos_puertas_R01.py':'43032d9cc6d62695ef1789dc08b80c8c4de7f0d036ad3a8ee10e60bb3d7c58b1',
 'pi10_transporte_ancestral_R01.py':'ad2d0a623f347a617a9329d055032884207ec43a3733290b96292f0e028c0577'}
for name,digest in pins.items():assert hashlib.sha256((H/name).read_bytes()).hexdigest()==digest,'Source changed: '+name
v={'schema':'DEE.PI10.adaptive_query.protocol.R02','status':'DRAFT','created_utc':datetime.now(timezone.utc).isoformat(),
 'N':67,'query_origin':[24,12,12],'old_origin':[8,40,50],'query_prefix':'PI10.Q1.TC.R01','old_prefix':'PI07.TC.R01',
 'q1_delay_laps':18,'q2_delay_laps':6,'max_ticks_per_episode':2016,'evaluation_horizon':12,'total_offers':18,
 'fi_required':True,'initial_old_q2_delta':-1,'schedule':schedule,'calibration_schedule':cal,'sources_sha256':pins,
 'reserved_ordinals':[1,2,3,5,6,7,9,10,11],'adaptation_ordinals':[0,4,8],
 'new_variant_authority':'Root prospective decision after R01 STOPPED_PRESERVED, before any R02 Native evaluation. No decoder/clock/kernel change, no import of the four R01 experiences or forced calibration history.',
 'source_neutral_prefix':{'life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_P0_01','N':67,'tick':922374,
   'RAW_sha256':'9f192d94b9b7fee74cd10a2d9910ee5c13fb4f2fb83bab76f933921447c55f89','clocks_sha256':'0a0fdac1d38f5d0077180a85ecc076da53ced981b2a12eba2d5582be1e63648b',
   'full_pair_manifest_sha256':'214062c2d706e1354e5bb22fa5c66b72f32c0e61a249913b71a5f4fa7d4cf7da',
   'inherited_R01_support':'ready true, admitted false, ordinal0, rows[], no pending/uncertain; literal R01 metadata retained and no bank reset'},
 'device_postread_stops':{'sites':[[30,40,32],[32,40,32]],'semantic':4,'state':0,'payload':0,
   'criterion':'Full RAW0 before any new ordinary interface birth, including inactive information. No clearing/resampling. Both receipts applied and exact RAW(4<<60) after preparation, prior R01 metadata literal and TC banks preserved.',
   'attribution':'External physical P0 route protection after read, not self-protection learned by E1. New consequences follow unchanged v27; possible retained-function interference must be checked.'},
 'calibration_contract':'Export neutral complete R02 preparation BEFORE admitting calibration. In the same separate prepared world, force Query true globally for five need cases Z,X,Z,None,X. Measure actual RAW contents, q1 signatures, question admission, Native q2/FI and effects. Reuse R01 calibrated+/- credit only because banks, aliases,18/6lap timing and q+4 reader remain unchanged. No forced history is imported into MAIN. A first NULL remains a failure, not a claimed Native choice.',
 'R01_adverse_preserved':{'status':'STOPPED_PRESERVED','attempted':5,'complete':4,'stopped_tick':928974,
   'snapshot_sha256':'a7f7d373a367c8c9bca8a020d8614b4cf16a5116e383e3202a02d53312082b5b',
   'finding':'Active SEM1 diagonal(+X,+Z) outside the original axis-only preview codec; no expected-bit fallback. This future remains separate. R02 is a declared new preparation from neutral P0, not a rewrite of that failed history.'},
 'actor_information':'Only actual Native preview STATE, actual gated RAW bit scaled0/2 and generic consequence. Actual cueNone does not guarantee RAW0. Regime, ordinal, reserve label, availability and target are not Native policy inputs.',
 'environment':'Actual measured RAW8bytes repeated8 gives one64B file offered before q1 choice. Need/need_return availability follows the actual admitted preview bit; bypass uses bin0. Only the measured admitted Nativeq2 output chooses a bin. Actual Native FI+ is additionally required. No host optimal-action or bank update.',
 'metric_distinction':'physical_delivered is actual64B move/readback; attributed_useful additionally requires valid Nativeq1. actual_failed=notattributed_useful may report a whole-task failure despite a physically delivered file after q1NULL. Do not call that absence of material or demonstrated damage.',
 'attribution':'Q1 support and return wiring, sensor protection, sample timing,0/2 codec, q2 disposal, FI work and schedule are P0. Only q1 receives task credit at its own fixed hub. Acquired selection must be demonstrated against fixed controls, not inferred from apparatus installation.',
 'ancestral_preservation':'D7/12, FI8 3/8, C2C31/32, R02 ancestral12/18 and neutral R01 preparation metadata stay literal. New18 PI10 offers are explicit prospective supply, not resetting those stocks.',
 'feedback_controls':{'real':'Actual composite task failure at the fixed q1 hub, same material input count per generic contact',
   'nonfailure':'One material nonfailure at the same q1 window; not omission of all contact',
   'yoked':'Actual Real12 failure sequence shifted by+5 modulo12, frozen permutation before observing outcomes'},
 'yoke_permutation':[(n+5)%12 for n in range(12)],
 'functional_gain_criterion':'At least2 additional attributed resources in the9 reserved cases versus nonfailure AND at least1 additional PHYSICAL64B reserved resource. Show useful NoQuery revision in bypass and useful return to Query in need_return; fewer queries or fewer NULLs alone is insufficient. All12 cases, errors, rejections and transition costs remain in denominators.',
 'strong_query_credit':'Requires actual q2 bank stability, actual FI+ and discriminating contingent/yoked and/or valid selective formed-trace controls. Divergent actual preview contents between arms must be reported; a total resource gain alone then has a joint sensory/history interpretation.',
 'conservation_core':{'critical10':'luma+,nara-,clasifica-,suma+,alfa-; FI+/-/0; later alfa-/luma+',
   'numerical2':'13 and8 via real arithmetic results; already partial domain, all outcomes reported',
   'ideal':'12/12 plus actual new useful function after coherent save/reopen',
   'if_reserved_gain_is2':'Require12/12 conservation',
   'bounded_partial_tolerance':'Only if reserved attributed gain>=3 and physical gain>=1: critical10/10, at most1 formed numerical failure without uncertainty plus another real correct arithmetic use. Explicit localized loss, no beneficial-pruning claim.',
   'adoption_blockers':'Two numerical failures, critical-core loss, incoherent/uncertain pending operation or unavailable real new use; no retrospective relaxation'},
 'reading_scope':'Fixed q+4 central q1/q2 readers; Nativechoice0 is valid and externally maps to motor-1, unlikeNULL. FI uses original q+6 six-site reader. Legacy calendar.query_read_tick=q+6 is only a planning label; report actual q+4 observations independently.',
 'external_references':'Offline Always/Never and keep-success/switch-failure global/STATE (including presence-initialized STATE) with the same observed information and fixed environmental law. Real FI is yoked; not a Native counterfactual, not an actor and not used to update DEE.',
 'budget_reference':'REGISTRO_CAMPANA.json governs: original180000 aggregate ticks,12 new worlds,14GB+1GBclose,512MiB owned Job,one Native thread,22:23:44UTC hardclose. This smaller12case variant does not restart or extend the budget.',
 'reproduction':'One decisive Native replay from the neutral complete prefix, not a documentary JSON recalc. Shared pasts are not independent individuals. Complete states remain local; export Native primaries, failures, controls and exact code.',
 'not_a_seal':'DRAFT only. Root must separately seal calibration, examine five actual outcomes and authorize evaluation. No Native calibration, capability, reserve success or adoption is claimed.'}
assert len(schedule)==18 and len(cal)==5 and all(0<=r['right']<r['left']<=20 for r in schedule+cal)
out.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'status':v['status'],'evaluation':12,'reserved':9,'supply':18,'Native_executed':False}))
