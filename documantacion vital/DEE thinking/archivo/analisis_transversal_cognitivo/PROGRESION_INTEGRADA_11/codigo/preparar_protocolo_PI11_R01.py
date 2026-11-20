"""Pure prospective protocol writer. Never imports DEE or opens a world."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ast,hashlib,json,random
P=Path(__file__).resolve().parents[1];H=P/'codigo'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(path,value):
 with Path(path).open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def events(seed,start,stop):
 rng=random.Random(seed);offset=start;mode='need';rows=[]
 while offset<stop:
  rows.append({'at_offset':offset,'mode':mode,'cue':rng.choice(['z']*7+['x','none'])})
  offset+=rng.randint(1279,3491)
  if rng.random()<0.72:mode='bypass'if mode=='need'else'need'
 return rows
def main(a):
 for f in('pi11_actor_R01.py','pi11_habitat_persistente_R01.py'):ast.parse((H/f).read_text('utf8'))
 rows=events(2026111101,0,18000)+events(2026111102,18000,60000)
 p={'schema':'DEE.PI11.persistent_habitat.protocol.R01','status':'SEALED_FOR_DEVELOPMENT'if a.development else'SEALED_FOR_EVALUATION','sealed_utc':datetime.now(timezone.utc).isoformat(),'N':67,'query_origin':[24,12,12],'old_origin':[8,40,50],'query_prefix':'PI10.Q1.TC.R01','max_ticks_per_episode':2016,'max_opportunities':24,'evaluation_opportunities':16,'development_opportunities':3,'FI_operands':[18,7],
 'habitat':{'stock':24,'initial_permissions':4,'permission_cap':4,'replenish_ticks':4687,'query_busy_ticks':233,'certificate_ticks':4200},'events':rows,'exogenous_seeds_auditor_only':[2026111101,2026111102],'reserved_environment_start_offset':18000,
 'Native_sensors':'Actual sampled preview STATE; actual bit released only after admitted physical material question. No environment mode, optimal action, seed or ordinal enters Native.',
 'new_control':'Q2 positive renews a certificate with an actual FI interaction. Negative/zero skips FI and reuses an unexpired result in the external environment. This is fixed transduction, not a discovered plan. Q1 physical eligibility receives generic failure; Q2 retains fixed nonfailure disposal.',
 'information_provenance':'RAW sample at q1-1, release q1+8, age9ticks; external certificate of actual FI result is environmental state, never Native learned memory.',
 'controls':{'inherited':'Same complete parent, habitat and feedback; always performs FI, matching the inherited fixed host continuation.','nonfailure':'Same Native-gated continuation; fixed nonpunitive outcome with the same contact calendar.','yoked':'Same Native-gated continuation; independent prospectively sampled balanced outcome bits, no shift of case blocks.','replay':'Exact complete prefix and frozen code; same errors expected. A technical replication, not another independent organism.'},
 'primary_observables':['attributed useful64B deliveries','physical deliveries','fresh FI operations','successful uses of prior certificate','Native positive/negative/NULL continuation outputs','queries admitted/denied','cost/readaptation and actual stocks over Native time'],
 'adoption_criteria':{'new_control':'At least two executed positive renewals and two executed negative/reuse decisions, with at least two useful prior-certificate uses.','functional_tradeoff':'At least inherited useful deliveries minus2 over same16opportunities, and >=25percent fewer fresh FI operations. Report all other measures separately; no composite reward rewrite.','history':'At least one Q1 reference change and a later changed use under common frozen codec; compare nonfailure/yoked and do not require exclusive real-feedback superiority.','core':'At least10/12 inherited uses, including correct luma/nara/alfa, both nonzero comparisons and actual two-step arithmetic result transport. Any missing critical use blocks promotion.','continuation':'Complete coherent save/reopen, a useful later new-habitat interaction, decisive Native acquisition replay and public material use before final closure.'},
 'stopping':'Stop at fixed horizon/budget, unreadable current preview, unknown receipts, inconsistent operational state or inherited host safety. A zero/NULL choice is retained as a task failure, not repaired.',
 'assistance':['Host initiates opportunities and aligns existing physical eligibility calendars.','Prepared Q1/access/Q2 order remains; only conditional FI continuation transfers to observed Native output.','Environmental law, supplies, certificate and codec are designed.','No autonomous initiative, metabolism, consciousness or general intelligence claim follows.'],
 'sources_sha256':{n:sha(H/n)for n in('pi11_actor_R01.py','pi11_habitat_persistente_R01.py')}}
 target=H/('PROTOCOLO_PI11_DESARROLLO_R01.json'if a.development else'PROTOCOLO_PI11_EVALUACION_R01.json');write(target,p)
 c={'schema':'DEE.PI11.fixed_experiment_scope.R01','life_id':a.life,'protocol_sha256':sha(target),'role':'development'if a.development else'evaluation','return_arm':a.arm,'continuation':a.continuation}
 if a.arm=='yoked':
  rng=random.Random(2026111191);values=[False,True]*12;rng.shuffle(values);c['yoked_values']=values;c['yoked_seed_auditor_only']=2026111191
 write(H/('PI11_EXPERIMENTO_'+a.tag+'_R01.json'),c)
 print(json.dumps({'protocol':str(target),'protocol_sha256':sha(target),'scope':str(H/('PI11_EXPERIMENTO_'+a.tag+'_R01.json')),'Native':0}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--development',action='store_true');ap.add_argument('--life',required=True);ap.add_argument('--tag',required=True);ap.add_argument('--arm',choices=['real','nonfailure','yoked'],default='real');ap.add_argument('--continuation',choices=['native','fixed'],default='native');main(ap.parse_args())
