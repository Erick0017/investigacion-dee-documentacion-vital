"""Finish the already closed R07 documentary package; never runs DEE/Studio/model."""
import argparse, datetime, hashlib, importlib.util, json, runpy, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'control/PLAN_FINAL_R07_PREPRIVACIDAD.json'
EXPECTED_PLAN='2074ad154d9532c5ed796d10cd727ffdd97b1b90dda88eebc7c97e4d0f01079d'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadmod(p,name,expected):
 if sha(p)!=expected:raise ValueError('Source pin changed: '+name)
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 a=argparse.ArgumentParser();a.add_argument('--privacy-sha256',required=True);a=a.parse_args()
 if sha(PLAN)!=EXPECTED_PLAN:raise ValueError('Plan changed')
 priv=ROOT/'analisis/REVISION_PRIVACIDAD_FINAL_R09.json'
 if sha(priv)!=a.privacy_sha256:raise ValueError('Privacy proof changed')
 pr=json.loads(priv.read_text('utf-8-sig'))
 if pr['plan_sha256']!=EXPECTED_PLAN or pr['read_and_hashed_members']!=532 or pr['selected_members']!=532 or pr['findings']:raise ValueError('Privacy review incomplete or candidates need judgment')
 if any(r['archive']!='EVIDENCIA_PARCIAL/RAW_NATIVE_MAIN35_CLIP01.mp4'for r in pr['skipped_or_limited']):raise ValueError('Unexpected privacy limitation')
 cp=ROOT/'control/CRITICOS_DESPUES_R07.json'
 if sha(cp)!='788957c2f3f4647bf9cbf5692d7a448705ab43fff70d8570fa2b8559196daa14' or not json.loads(cp.read_text('utf-8-sig'))['all_match']:raise ValueError('Critical proof mismatch')
 p=loadmod(ROOT/'control/expediente_compacto_v3_R04.py','r07_final_packager','62222e7be90d37f2dafea2f14f78da8fefed987fcdb111ef3fc08542a3487bc2')
 frozen=ROOT/'control/PLAN_FINAL_R07_CONGELADO.json';approved=ROOT/'control/PLAN_FINAL_R07_APROBADO.json'
 if frozen.exists()or approved.exists():raise ValueError('No overwrites allowed')
 result=p.freeze(PLAN,frozen);spec=json.loads(frozen.read_text('utf-8-sig'));spec['finalized']=True
 spec['status']='CLOSED_WITH_EXPLICIT_SCIENTIFIC_NEGATIVES_AND_VIDEO_BLOCKER'
 spec['final_protection_pending']=False;spec['privacy_incremental_pending']=False
 spec['root_finalization']={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privacy_proof':str(priv),'privacy_sha256':sha(priv),'selected_scanned_members':532,'candidate_count':0,'binary_scope':'Only independently reviewed RAW Main35; not comparative movie','scope':'Source freeze and packaging permission only; not global scientific approval','scientific_experiences_closed':True,'Native_Studio_model_requested':False}
 approved.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 delivery=ROOT.parent/'entrega';zp=delivery/'DEE_ROBLOX_CIERRE8_R07_2026_11_17_ANALISIS.zip';ext=delivery/'VERIFICACION_LIMPIA_CIERRE8_R07_2026_11_17'
 build=p.build(approved,zp);verify=p.verify(zp,ext)
 driver=ROOT/'control/verificar_cinco_recetas_desde_zip_R07.py'
 if sha(driver)!='2b6f17d95996ae25cc98d8940863dac521e01394405bf3b1101e857f3ad1ddba':raise ValueError('Recipe checker changed')
 oldargv=sys.argv[:];rc=0
 try:
  sys.argv=[str(driver),'--root',str(ext),'--output',str(ext/'QA_RECALCULOS_LIMPIOS_R07')]
  try:runpy.run_path(str(driver),run_name='__main__')
  except SystemExit as ex:rc=ex.code if isinstance(ex.code,int)else(0 if ex.code is None else 1)
 finally:sys.argv=oldargv
 rp=ext/'QA_RECALCULOS_LIMPIOS_R07/VERIFICACION_CINCO_RECETAS.json';rr=json.loads(rp.read_text('utf-8-sig'))
 final=p.verify(zp)
 proof={'schema':'DEE.R07.final_package_close.v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'freeze':result,'build':build,'clean_extraction':verify,'five_recipes_proof':str(rp),'five_recipes_proof_sha256':sha(rp),'five_recipes_exit_code':rc,'all_five_zero_issues':rr['all_five_zero_issues'],'final_ZIP_verification':final,'privacy_proof':str(priv),'privacy_proof_sha256':sha(priv),'source_plan_sha256':EXPECTED_PLAN,'approved_plan_sha256':sha(approved),'Native_Studio_MCP_model_runs_requested':0,'scope':'Archive and documentary recalculation only; the scientific negatives and video blocker remain as reported.'}
 out=ROOT/'control/CIERRE_DOCUMENTAL_EJECUTADO_R07.json'
 with out.open('x',encoding='utf-8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(out),'ZIP':final,'five_recipes_zero_issues':rr['all_five_zero_issues']},ensure_ascii=False));return 0 if rc==0 and rr['all_five_zero_issues']else 1
if __name__=='__main__':raise SystemExit(main())
