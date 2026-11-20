"""Freeze REAL2 EVALUATION code only for future RP12; no state/Native copy.

Run after REAL2 code compilation under its sealed evaluation protocol. Never
uses the calibration-force capsule as an evaluation template, and never reads
or opens the current principal/owner/SQLite.
"""
from pathlib import Path
import argparse,hashlib,json,shutil
P=Path(__file__).resolve().parents[1];H=P/'codigo';NEUTRAL_SHA='ff303ead4e4e4a0221ef41ae40a5ea34e01bf0b6e27beee3fd0fa9a2754ce9a7'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regular(p):
 for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No linked/reparse code')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--sistema',type=Path,default=P/'estados/REAL2/sistema');ap.add_argument('--destino',type=Path,default=H/'CAPSULA_EVALUACION_REAL2_R02');ap.add_argument('--congelar',action='store_true');a=ap.parse_args();system=a.sistema.resolve(strict=True);dest=a.destino.resolve();need(system.name=='sistema'and system.parent.parent==(P/'estados').resolve()and dest.parent==H.resolve()and not(system/'estado/ACTIVO.json').exists(),'Exact isolated evaluation code and new campaign capsule')
 scope=read(system/'capacidades/PI10_EXPERIMENTO_R02.json');need(scope['life_id']=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'and scope['role']=='evaluation'and scope['arm']=='real'and scope['trace_control']=='none'and scope['force_query']is None and scope['source_full_pair_manifest_sha256']==NEUTRAL_SHA,'Actual unforced REAL2 evaluation scope from closed neutral P02')
 proto=system/'capacidades/PROTOCOLO_PI10_R02.json';need(read(proto)['status']=='SEALED_FOR_EVALUATION'and sha(proto)==scope['protocol_sha256'],'Frozen Root evaluation seal, never calibration-force template')
 codefile=system.parent/'SISTEMA_CODIGO_PI10.json';code=read(codefile);rows=code['files'];need(sum(r['bytes']for r in rows)<100000000,'Small code closure only')
 for row in rows:
  f=system/row['file'];regular(f);need(not row['file'].startswith(('estado/','runtime/'))and sha(f)==row['sha256'],'Exact unchanged compiled evaluation code')
 if not a.congelar:print(json.dumps({'mode':'PLAN_ONLY','files':len(rows),'bytes':sum(r['bytes']for r in rows),'Native':0}));return
 need(not dest.exists(),'Fresh capsule, never overwrite a prior source');dest.mkdir();before={str(system/r['file']):sha(system/r['file'])for r in rows}
 for row in rows:
  target=dest/row['file'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(system/row['file'],target);need(sha(target)==row['sha256'],'Frozen evaluation-code copy mismatch')
 (dest/'SISTEMA_CODIGO.json').write_text(json.dumps({'schema':'DEE.PI10.actual_evaluation_code_capsule.R02','files':rows},ensure_ascii=False,indent=2)+'\n','utf8');need(before=={p:sha(p)for p in before},'Source code changed during freeze')
 proof={'schema':'DEE.PI10.frozen_real2_evaluation_code.R02','source_system':str(system),'source_code_manifest_sha256':sha(codefile),'capsule_manifest_sha256':sha(dest/'SISTEMA_CODIGO.json'),'neutral_P02_manifest_sha256':NEUTRAL_SHA,'evaluation_protocol_sha256':sha(proto),'template_life_id':scope['life_id'],'operator_force_query':None,'source_unchanged':True,'Native_executed':False,'states_or_engine_copied':False,'RP_registered':False};(dest/'CONGELACION_CAPSULA_REAL2_R02.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'capsule':str(dest),'manifest_sha256':proof['capsule_manifest_sha256'],'proof_sha256':sha(dest/'CONGELACION_CAPSULA_REAL2_R02.json'),'Native':0}))
if __name__=='__main__':main()
