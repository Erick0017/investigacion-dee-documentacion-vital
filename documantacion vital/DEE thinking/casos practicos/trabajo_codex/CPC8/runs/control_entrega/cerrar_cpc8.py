"""External final accounting; does not modify the tested container/source."""
import argparse,ctypes,hashlib,json
from datetime import datetime,timezone
from pathlib import Path

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--delivery',type=Path,required=True);p.add_argument('--control',type=Path,required=True);a=p.parse_args()
 budget=json.loads((a.source/'BUDGET.json').read_text(encoding='utf-8'))
 proof=json.loads((a.delivery/'VERIFICACION_FINAL_EXTERNA.json').read_text(encoding='utf-8'))
 artifact=Path(proof['zip']);checksum=sha(artifact)
 assert checksum==proof['artifact_sha256']
 jobs=[]
 for root in (a.source,a.control):
  for folder in sorted((root/'jobs').iterdir()):
   if not folder.is_dir():continue
   r=json.loads((folder/'COMMAND.json').read_text(encoding='utf-8'))
   closed=r.get('pid') is None or(r.get('owned_worker_waited')and r.get('owned_job_closed')and r.get('kill_on_job_close'))
   assert r['status']not in('STARTING','RUNNING')and closed,folder
   jobs.append({'scope':'scientific_and_preseal'if root==a.source else'postseal_delivery','name':folder.name,'status':r['status'],'exit_code':r.get('exit_code'),'owned_worker_closed':bool(closed)})
 size=artifact.stat().st_size
 if size<=20*1024**2:
  write(a.delivery/'TRANSPORTE_NO_REQUERIDO.json',{'artifact_sha256':checksum,'compressed_bytes':size,'threshold_bytes':20*1024**2,'parts_generated':0,'reason':'Canonical ZIP below the user-specified compressed20MiB threshold; no independent or binary part archives needed.'})
 else:
  parts=json.loads((a.delivery/'PARTES.json').read_text(encoding='utf-8'));assert parts['zip']['sha256']==checksum and len(parts['parts'])==2
 with (a.delivery/'HASH_ZIP_FINAL.sha256').open('x',encoding='ascii')as f:f.write(checksum+'  '+artifact.name+'\n')
 q=ctypes.c_longlong();ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(q))
 elapsed=(q.value-budget['start_qpc'])/budget['qpc_frequency']
 report={'status':'CLOSED_WITH_VERIFIED_PRIVATE_DELIVERY','scientific_scope':'Partial integrated positive results with all adverse cases preserved; no claim of65 semantic primitives or universal autonomy',
  'artifact_sha256':checksum,'artifact':str(artifact),'compressed_bytes':size,'expanded_bytes':proof['expanded_bytes'],
  'compressed_MiB':size/1024**2,'expanded_MiB':proof['expanded_bytes']/1024**2,
  'original_start_utc':budget['start_utc'],'closed_utc':datetime.now(timezone.utc).isoformat(),'elapsed_original_monotonic_seconds':elapsed,'original_budget_seconds':budget['budget_seconds'],'remaining_seconds':budget['budget_seconds']-elapsed,
  'exact_zip_clean_validation':proof['clean_validation']['status'],'clean_checks':len(proof['clean_validation']['checks']),
  'jobs':jobs,'unclosed_owned_jobs':[],'after_closure':'No simulations or automatic future continuations. A future campaign requires new authorization.',
  'source_immutable':'Post-seal validation/installation/publication logs and this closing accounting are external; no tested ZIP payload has been changed.'}
 write(a.delivery/'CIERRE_CPC8.json',report)
 print(json.dumps({k:report[k]for k in('status','artifact_sha256','compressed_bytes','expanded_bytes','elapsed_original_monotonic_seconds','unclosed_owned_jobs')}))
if __name__=='__main__':main()
