"""Create a prospective draft only. Root separately pins/seals before Native."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
H=Path(__file__).resolve().parent;P=H.parent
out=H/'PROTOCOLO_PI10_R01.json';assert not out.exists()
Z='threat';X='falsecue';O='none'
groups=[('need',[Z,X,Z,O,X,Z]),('bypass',[X,Z,Z,Z,O,Z]),('need_return',[Z,O,X,Z,Z,X])]
pairs=[(18,5),(19,6),(16,7),(20,7),(17,6),(19,8),
       (20,9),(18,6),(17,5),(19,7),(16,4),(20,8),
       (19,5),(17,3),(20,6),(18,7),(16,5),(19,9),
       (20,9),(17,7),(18,5),(19,6),(16,3),(20,4)]
schedule=[]
for regime,cues in groups:
    for k,cue in enumerate(cues):
        ordinal=len(schedule);left,right=pairs[ordinal]
        schedule.append({'ordinal':ordinal,'regime':regime,'cue':cue,
          'role':'adaptation'if k<2 else'reserved','left':left,'right':right})
for regime,cue in[('need',Z),('need',X),('bypass',Z),('bypass',X),('need_return',Z),('need_return',O)]:
    ordinal=len(schedule);left,right=pairs[ordinal]
    schedule.append({'ordinal':ordinal,'regime':regime,'cue':cue,'role':'operational_future','left':left,'right':right})
v={'schema':'DEE.PI10.adaptive_query.protocol.R01','status':'DRAFT','created_utc':datetime.now(timezone.utc).isoformat(),
 'N':67,'query_origin':[24,12,12],'old_origin':[8,40,50],
 'query_prefix':'PI10.Q1.TC.R01','old_prefix':'PI07.TC.R01','q1_delay_laps':18,'q2_delay_laps':6,
 'max_ticks_per_episode':2016,'evaluation_horizon':18,'total_offers':24,
 'fi_required':True,'initial_old_q2_delta':-1,'schedule':schedule,
 'calibration_schedule':[
   {'ordinal':0,'regime':'need','cue':Z,'role':'diagnostic_forced','left':18,'right':5},
   {'ordinal':1,'regime':'need','cue':X,'role':'diagnostic_forced','left':19,'right':6},
   {'ordinal':2,'regime':'bypass','cue':Z,'role':'diagnostic_forced','left':20,'right':7}],
 'calibration_contract':'Two matched clones may force query globally true/false in their explicit diagnostic scopes. No forced experience is imported to the candidate. Both available-bin routes and Native consequence polarity must be measured, not presumed.',
 'sources_sha256':{},'Root_must_pin_sources_before_material':['pi10_consulta_adaptativa_R01.py','pi10_dos_trazas_legales_R01.py','pi10_entorno_dos_puertas_R01.py'],
 'actor_information':'Only actual Native preview STATE, actual gated prior RAW bit scaled0/2 and declared generic return. Regime, ordinal, role, availability and expected outcomes are not Native policy inputs.',
 'environment':'Actual RAW64B offer placed before first choice: available-bin follows actual preview bit in need/need_return and bin0 in bypass. Only the measured valid q2 command selects a bin. Local file transfer plus actual Native FI+ is the material consequence; no optimal-action or bank update algorithm.',
 'attribution':'Q1 new unlearned support and fixed return routing/calendar are external P0. Q2 uses its inherited Native bank and fixed0/2 codec; its nonfailure return disposes eligibility. Only Q1 receives the task consequence at its fixed hub. These prepared links do not themselves prove learning.',
 'ancestral_preservation':'Keep D7/12, FI8 3/8, C2C31/32 and R02 12/18 literal; new24 environment/FI offers are explicit supply, not resetting old counters or teaching memories.',
 'reserved_ordinals':[2,3,4,5,8,9,10,11,14,15,16,17],
 'feedback_controls':{'real':'actual whole-task failure, not predicted action',
   'nonfailure':'one material nonfailure return on the same first-selector calendar, not omission of all contact',
   'yoked':'actual Real18 failure sequence shifted by+5 modulo18; fixed before outcomes, no optimization'},
 'yoke_permutation':[(i+5)%18 for i in range(18)],
 'functional_gain_criterion':'At least2 more attributed material resources in the12 reserved cases than nonfailure, with valid Native q1/q2 and all cases/transition costs retained. Native querying/use must revise in bypass and return usefully in need_return; fewer queries alone is insufficient.',
 'strong_query_credit':'Conditional on actual q2 bank stability, all actual FI+ functions successful, intended Q1 eligibility/return contact and discriminating yoked and/or selective cut/sham controls. Otherwise describe a narrower joint or partly mediated gain, not specific question value.',
 'conservation_core':{
   'critical10':'luma+,nara-,clasifica-,suma+,alfa-; FI+/-/0; later alfa-/luma+ using current declared access',
   'numerical2':'13 and8 from a real arithmetic result chain, reported separately within the already partial arithmetic domain',
   'ideal':'12/12 and the new useful function after coherent save/reopen',
   'if_reserved_gain_is2':'Require12/12 conservation',
   'bounded_partial_tolerance':'Only if reserved resource gain>=3: ten critical uses10/10, at most one formed numerical failure without operational uncertainty, plus another real correct arithmetic use. Document the localized loss and cost; not beneficial pruning.',
   'adoption_blockers':'Two numerical failures, critical-core loss, incoherent/pending/uncertain operation or unavailable actual new use; no retrospective relaxation'},
 'reading_scope':'Fixed q+4 central readers; valid choice0 maps to actual motor-1 before consequence, distinct from NULL. Record raw Native choice, actual motor, all admissions, q1/q2 ticks and real residues67/391/782.',
 'reproduction':'One decisive actual Native acquisition replay from a complete prefix with fresh diagnostic ID/destination; documentary recalculation remains separate. Candidate and controls share a prefix and are not independent statistical replicates.',
 'budget_reference':'REGISTRO_CAMPANA.json is authoritative: PI10 Root180000 aggregate ticks,12 new worlds,14GB new logical storage plus1GB close reserve,536870912-byte owned Job,one Native thread. Old PI09 deadlines/limits are not copied.',
 'not_a_seal':'No Native result, law validation, gate success or adoption is claimed. Root must record actual source/physical preflight, source hashes, scope and prospective calibration/evaluation authorization.'}
assert len(schedule)==24 and len(v['reserved_ordinals'])==12
assert all(0<=r['right']<r['left']<=20 for r in schedule)
out.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'draft':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'scheduled':24,'evaluated':18,'reserved':12,'Native_executed':False}))
