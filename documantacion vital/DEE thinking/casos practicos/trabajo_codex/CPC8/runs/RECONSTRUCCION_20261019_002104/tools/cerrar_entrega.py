"""Write external closure only after exact publication and transport checks."""
import argparse,ctypes,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from publicar_cpc8 import digest,replace_small,verify,confirm_owned_job_closure,write_new
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--delivery',type=Path,required=True);p.add_argument('--prior-proofs',type=Path,required=True);p.add_argument('--delivery-log-root',type=Path,required=True);p.add_argument('--operative-root',type=Path);a=p.parse_args();directory=a.delivery.resolve()
 name='CPC8_ORGANIZACION_COGNITIVA_NATIVA_APRENDIZAJE65_RESULTADOS.zip';artifact=directory/name;integrity=verify(artifact);external=json.loads((directory/'VERIFICACION_FINAL_EXTERNA.json').read_text(encoding='utf8'))
 assert external['artifact_sha256']==integrity['sha256'] and external['clean_validation']['status']=='PASS'
 cases=ROOT.parents[3]
 expected={'CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip':'1c10b8501ff0bb9756d6b1ebe5876a63ae7300ec4722d651e94dfe9e8f45a0f6','CPC4_COMUNICACION_NATIVA_Y_META_ROSETTA_RESULTADOS.zip':'4a14a81f913a434a8e54e47c0c700d7ee54418bb16913aedded8bf49a3294723','CPC5_ARQUITECTURAS_COMPUESTAS_Y_APRENDIZAJE_ACUMULATIVO_RESULTADOS.zip':'d31972a47f12bb574a71a14d7ddca3b7a011f320eaba37dcb2ac97abe1f4ce05','CPC6_MENTE_DEE_INTEGRADA_APRENDIZAJE_Y_COMUNICACION_RESULTADOS.zip':'9d8c72a2536a7d8a782e0f3885d6d9ceba48b5f3d9111f618386def13fff708b','CPC7_MENTE_DEE_ACCESO_SELECTIVO_Y_APRENDIZAJE_CONTINUO_RESULTADOS.zip':'64a9ca648d10bb8bc42c02e218091b4e7c5599a55301c65d67c7f6f8ac83a128'}
 preserved=[]
 for filename,expected_sha in expected.items():
  source=cases/filename;actual=digest(source)
  if actual!=expected_sha:raise ValueError('A source cut differs at closure; preserved, never overwritten: '+filename)
  preserved.append({'path':str(source),'sha256':actual,'matches_audited_source':True})
 identity=json.loads((ROOT/'revision/IDENTIDAD_KERNEL_Y_PRODUCTO.json').read_text(encoding='utf8'))['official_product_archive'];product=Path(identity['original_path']);actual=digest(product)
 if actual!=identity['expected_sha256']:raise ValueError('Official product archive changed; preserved, never overwritten')
 preserved.append({'path':str(product),'sha256':actual,'matches_audited_source':True})
 historical=ROOT.parents[0]/'historico'/'CPC8_ORGANIZACION_COGNITIVA_NATIVA_APRENDIZAJE65_RESULTADOS__65164c939621464c7d4faa800240bb1c2e25538ba9d878a65863016f57387c00.zip'
 assert digest(historical)=='65164c939621464c7d4faa800240bb1c2e25538ba9d878a65863016f57387c00'
 preserved.append({'path':str(historical),'sha256':digest(historical),'matches_audited_source':True})
 if integrity['compressed_bytes']>20*1024**2:
  manifest=json.loads((directory/'PARTES.json').read_text(encoding='utf8'));h=hashlib.sha256();parts=[]
  # The transport manifest uses a versioned schema; identify its actual list.
  part_rows=manifest.get('parts',manifest.get('partes'))
  if not isinstance(part_rows,list)or len(part_rows)!=2:raise ValueError('Exactly2 transport parts required')
  for number,row in enumerate(part_rows,1):
   f=directory/(name+f'.{number:03d}')
   expected=row.get('sha256');assert expected and digest(f)==expected
   with f.open('rb')as stream:
    for block in iter(lambda:stream.read(1024**2),b''):h.update(block)
   parts.append({'name':f.name,'bytes':f.stat().st_size,'sha256':expected})
  assert h.hexdigest()==integrity['sha256']
  rebuilt=json.loads((directory/'TRANSPORTE_VERIFICADO.json').read_text(encoding='utf8'))
  assert rebuilt['zip']['sha256']==integrity['sha256'] and rebuilt['actual_byte_comparison_equal'] is True and rebuilt['actual_bytes_compared']==integrity['compressed_bytes']
  transport={'required':True,'parts':parts,'concatenated_sha256':h.hexdigest(),'manifest':'PARTES.json','helper':'REUNIR_CPC8.py','actual_byte_comparison_equal':True,'actual_bytes_compared':rebuilt['actual_bytes_compared'],'real_rebuild':'Actual temporary reconstruction, full integrity and direct block-by-block byte comparison performed by publicar_cpc8.transport; this closure additionally verifies streaming concatenation'}
 else:transport={'required':False,'reason':'Canonical compressedZIP does not exceed20MiB','parts':[]}
 own=confirm_owned_job_closure(ROOT);delivery=confirm_owned_job_closure(a.delivery_log_root.resolve());b=json.loads((ROOT/'BUDGET.json').read_text(encoding='utf-8-sig'));q=ctypes.c_longlong();ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(q));elapsed=(q.value-b['start_qpc'])/b['qpc_frequency']
 record={'schema':'CPC8R.delivery.closed.v1','status':'EXACT_NEW_CANONICAL_PUBLISHED_AND_VERIFIED','closed_utc':datetime.now(timezone.utc).isoformat(),'artifact':str(artifact),'artifact_sha256':integrity['sha256'],'compressed_bytes':integrity['compressed_bytes'],'expanded_bytes':integrity['expanded_bytes'],'original_budget':b,'total_elapsed_monotonic_seconds':elapsed,'remaining_seconds':b['budget_seconds']-elapsed,'transport':transport,'external_clean_proof':'VERIFICACION_FINAL_EXTERNA.json','external_proof_sha256':digest(directory/'VERIFICACION_FINAL_EXTERNA.json'),'own_science_jobs':own,'own_delivery_jobs':delivery,'old_CPC8_protected_sha256':'65164c939621464c7d4faa800240bb1c2e25538ba9d878a65863016f57387c00','no_background_simulations_left':True,'privacy':'Private reconstructive package, not a sanitized third-party export'}
 record['frozen_original_archives_checked_at_closure']=preserved
 replace_small((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf8'),directory/'CIERRE_CPC8.json',a.prior_proofs)
 legacy={'status':'SUPERSEDED_BY_CURRENT_PARTES_JSON'if transport['required']else'CURRENT_TRANSPORT_NOT_REQUIRED','artifact_sha256':integrity['sha256'],'transport_required':transport['required'],'explanation':'Filename retained only as a compatibility pointer. Its prior historical bytes are protected in prior_proofs. Current authoritative transport fields are PARTES.json and CIERRE_CPC8.json.'}
 replace_small((json.dumps(legacy,ensure_ascii=False,indent=2)+'\n').encode('utf8'),directory/'TRANSPORTE_NO_REQUERIDO.json',a.prior_proofs)
 if a.operative_root:
  target=a.operative_root.resolve()/'EXPEDIENTE_VIGENTE.json'
  if target.parent!=ROOT.parents[1]:raise ValueError('Operative pointer must be at this CPC8 root, not another project')
  write_new(target,{'status':'CPC8_RECONSTRUIDO_OPERATIVO','created_utc':record['closed_utc'],'canonical_zip':str(artifact),'sha256':integrity['sha256'],'source_work_cut':str(ROOT),'external_verification':str(directory/'VERIFICACION_FINAL_EXTERNA.json'),'closure':str(directory/'CIERRE_CPC8.json'),'historical_previous_zip_sha256':record['old_CPC8_protected_sha256'],'prior_run_status':'RUN_20261018_204718 is an unchanged historical research source, not the operative campaign. Protected prior ZIP is outside the new package.','no_prior_research_deleted':True})
 print(json.dumps(record,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
