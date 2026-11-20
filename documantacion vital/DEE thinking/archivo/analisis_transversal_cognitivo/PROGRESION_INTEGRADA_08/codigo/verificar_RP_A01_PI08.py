"""Read-only closure/physical coincidence of the actual PI08 RP frontdoor run."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parents[1]
Q=P/'estados/RP_A01'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 c=read(Q/'CONTEXTO_EJECUCION.json');r=read(Q/'RESULTADO_REPRODUCCION.json')
 card=read(Q/'sistema/estado/vidas'/c['life']/'VIDA.json')
 expected=c['fixed_recipe']['variants'][c['variant']]['expected_final_physical']
 actual={k:card['physical'][k]for k in expected}
 logs=[json.loads(x)for x in(Q/'ENSAYOS.jsonl').read_text(encoding='utf8').splitlines()]
 closed=[x for x in logs if x.get('kind')=='OWNER_CLOSED']
 resources=[x for x in logs if x.get('kind')=='OWNED_PROCESS_RESOURCES']
 proof={'schema':'DEE.PI08.RP.frontdoor.actual.v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'life':c['life'],'recipe':c['recipe'],'variant':c['variant'],
  'actual_Native_run':True,'new_Native_ticks':sum(x['after_tick']-x['before_tick']for x in r['rows']),
  'result_status':r['status'],'local_criteria_met':r['criteria_met'],
  'expected_physical_predeclared':expected,'actual_physical':actual,'physical_coincidence':actual==expected,
  'coherent_closed':r['owner_closed_coherently']and len(closed)==1 and closed[0]['exit_code']==0 and not closed[0]['final_status']['running'],
  'Native_receipts':r['native_receipts'],'denominators':r['denominators'],
  'effective_job_memory_limit_bytes':sorted(set(x['job_memory_limit']for x in resources)),
  'observed_peak_job_committed_bytes':max(x['peak_job_committed_bytes']for x in resources),
  'sources':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}for p in(Q/'RESULTADO_REPRODUCCION.json',Q/'IMPORTACION_DIAGNOSTICA.json',Q/'CONTEXTO_EJECUCION.json',Q/'ENSAYOS.jsonl')],
  'scope':'Actual existing RP facade, preserved POST4 complete prefix. Same acquired state and output as historical OP04. This is technical reproduction of use, not a new independent acquisition or all-RP audit.'}
 out=P/'control/RP_A01_REAL_PI08_R01.json'
 with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
 assert proof['physical_coincidence']and proof['coherent_closed']and r['criteria_met']
 print(json.dumps({k:proof[k]for k in('life','new_Native_ticks','physical_coincidence','coherent_closed','Native_receipts','observed_peak_job_committed_bytes')},ensure_ascii=False))
if __name__=='__main__':main()
