"""Root-only exact two-file public hook delta on CLOSED REAL2, no Native.

Default is read-only PLAN. --aplicar requires the exact closed owner proof and
pure tests, backs up the old code/closure once, changes only staged source and
administrative code manifests, and proves card/snapshot/DB and principal hashes
unchanged. No rebind of C2C metadata, no stock/reset, no state/contract edit.
"""
from pathlib import Path
import argparse,ast,hashlib,importlib.util,json,shutil,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';SYSTEM=P/'estados/REAL2/sistema';STAGE=H/'PERMISO_PI10_R02_PREPARADO';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01';KEY='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def regular(p):
 for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No linked/reparse path')
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--comprobante',type=Path,required=True);ap.add_argument('--aplicar',action='store_true');a=ap.parse_args();regular(SYSTEM)
 proof=a.comprobante.resolve(strict=True);need(proof.is_relative_to((P/'control').resolve()),'Exact local closed owner proof');closed=read(proof)
 need(closed.get('schema')=='DEE.PI10.actual.finite_owner_plan.R01'and closed.get('life_id')==LIFE and closed.get('closed')is True and closed.get('error')is None and closed.get('protected_before')==closed.get('protected_after'),'Only exact successful closed REAL2 phase')
 need(not(SYSTEM/'estado/ACTIVO.json').exists()and not(P/'PI10_ROOT_NATIVE_WRITER.lock').exists()and not(C/'reproducibilidad/EJECUCION_MATERIAL.lock').exists(),'Unselected closed diagnostic only; one writer rule')
 guard=H/'comprobar_proceso_PI10_R02.py';need(sha(guard)=='21d41a1e429f135d100f17826258561dc9f98ca52a465cc2015f30efb5966adb','Guard changed');inspection=load('PI10_permission_closed_guard',guard).inspect('PI10_exact_closed_code_permission',SYSTEM,LIFE);need(inspection['no_live_affected_writer'],'Affected writer/queue not proven closed')
 cardfile=SYSTEM/'estado/vidas'/LIFE/'VIDA.json';card=read(cardfile);snapshot=SYSTEM/card['snapshot'];need(card['physical']['tick']==closed['final_tick']and sha(snapshot)==card['snapshot_sha256']==closed['final_saved_Native']['encoded_sha256'],'Closed proof/current checkpoint mismatch')
 parser=C/'reproducibilidad/observador_pasivo.py';need(sha(parser)=='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873','Passive parser changed');view=load('PI10_permission_frozen_snapshot',parser).snapshot_view(snapshot);m=json.loads(view['metadata'][KEY]);need(m['ordinal']==len(m['rows'])and 12<=m['ordinal']<=18 and not m.get('pending')and not m.get('uncertain')and m.get('admission_control')=={'role':'evaluation','arm':'real','trace_control':'none','force_query':None},'Closed unforced Real12+ only')
 dest=SYSTEM.parent;codefile=dest/'SISTEMA_CODIGO_PI10.json';contextfile=dest/'CONTEXTO_EJECUCION.json';prepfile=dest/'PREPARACION_PI10.json';code=read(codefile);context=read(contextfile);prep=read(prepfile)
 need(context['life']==LIFE and context['source_code_manifest_sha256']==sha(codefile)and prep['final_code_manifest_sha256']==sha(codefile)and prep['context_sha256']==sha(contextfile),'Original coherent code/context/preparation closure required')
 for row in code['files']:need(sha(SYSTEM/row['file'])==row['sha256'],'Code changed before permission: '+row['file'])
 planfile=STAGE/'PLAN.json';plan=read(planfile);need(sha(planfile)=='7ed3370d1cd751422658c26c295139324df82639df27e003a281ee54f3344ac1'and plan['schema']=='DEE.PI10.public_permission.staged_owner_delta.R02','Exact reviewed staged permission')
 owner=SYSTEM/'app/mundo_genesis_apd05.py';need(sha(owner)==plan['source_owner_sha256'],'Staged delta not derived from this exact current owner')
 need({row['file']for row in plan['files']}=={'app/mundo_genesis_apd05.py','capacidades/pi10_permiso_operativo_R02.py'},'Only reviewed two-file delta')
 for row in plan['files']:
  source=STAGE/row['file'];regular(source);need(sha(source)==row['sha256'],'Staged file changed');ast.parse(source.read_text('utf8'))
 tests=load('PI10_permission_prewrite_pure_tests',H/'pruebas_puras_panel_permiso_PI10_R03.py').run();need(all(r['pass']for r in tests['tests']),'Pure tests failed before any write')
 active=C/'sistema/estado/ACTIVO.json';principal=read(active)['life_id'];principalcard=C/'sistema/estado/vidas'/principal/'VIDA.json';protected=[active,principalcard,C/'sistema'/read(principalcard)['snapshot'],cardfile,snapshot]
 db=Path(inspection['SQLite']['path']);protected.append(db)
 for suffix in('-wal','-shm'):
  auxiliary=Path(str(db)+suffix)
  if auxiliary.exists():protected.append(auxiliary)
 before={str(p):sha(p)for p in protected};backup=P/'control/PERMISO_DIAGNOSTICO_REAL2_R02';output=backup/'APLICACION.json'
 need(not backup.exists(),'Do not repeat/overwrite an applied or uncertain code delta')
 if not a.aplicar:print(json.dumps({'mode':'PLAN_ONLY_NO_NATIVE','system':str(SYSTEM),'closed_tick':card['physical']['tick'],'ordinal':m['ordinal'],'files':plan['files'],'pure_tests_passed':tests['passed'],'Native':0}));return
 need(Path(sys.executable).resolve()==(C/'motor/python313/python.exe').resolve(),'Root official Python only');backup.mkdir();dump(backup/'INTENT.json',{'schema':'DEE.PI10.diagnostic_public_permission.intent.R02','closed_proof':str(proof),'closed_proof_sha256':sha(proof),'stage_sha256':sha(planfile),'before':before,'Native_ticks':0});dump(backup/'PRUEBAS_PURAS.json',tests)
 for p in(codefile,contextfile,prepfile,owner):
  target=backup/('before_'+p.name);shutil.copyfile(p,target);need(sha(target)==sha(p),'Verified prewrite backup required')
 permission=SYSTEM/'capacidades/pi10_permiso_operativo_R02.py';need(not permission.exists(),'New reviewed permission file must be absent')
 for row in plan['files']:shutil.copyfile(STAGE/row['file'],SYSTEM/row['file']);need(sha(SYSTEM/row['file'])==row['sha256'],'Exact staged copy failed')
 rows={r['file']:r for r in code['files']}
 for row in plan['files']:rows[row['file']]={'file':row['file'],'bytes':(SYSTEM/row['file']).stat().st_size,'sha256':sha(SYSTEM/row['file'])}
 code['files']=[rows[k]for k in sorted(rows)];code['diagnostic_permission_delta']={'schema':'DEE.PI10.exact_public_permission.code_only.R02','stage_sha256':sha(planfile),'source_code_manifest_sha256':sha(backup/'before_SISTEMA_CODIGO_PI10.json'),'closed_proof_sha256':sha(proof),'Native_ticks':0,'state_modified':False};dump(codefile,code)
 context['source_code_manifest_sha256']=sha(codefile);dump(contextfile,context);prep.update(context_sha256=sha(contextfile),final_code_manifest_sha256=sha(codefile));dump(prepfile,prep)
 after={str(p):sha(p)for p in protected};need(after==before,'Protected state/principal changed; preserve evidence, no automatic retry');need(all(sha(SYSTEM/r['file'])==r['sha256']for r in read(codefile)['files']),'Updated code closure failed')
 result={'schema':'DEE.PI10.diagnostic_public_permission.actual.R02','life_id':LIFE,'tick_unchanged':card['physical']['tick'],'state_modified':False,'Native_ticks':0,'product_modified':False,'two_files':plan['files'],'source_code_manifest_sha256_before':sha(backup/'before_SISTEMA_CODIGO_PI10.json'),'source_code_manifest_sha256_after':sha(codefile),'context_sha256_after':sha(contextfile),'preparation_sha256_after':sha(prepfile),'protected_before':before,'protected_after':after,'closed_proof':str(proof),'closed_proof_sha256':sha(proof),'no_C2C_metadata_leaf_rebound':True,'pure_tests_passed':tests['passed']};dump(output,result);print(json.dumps({'proof':str(output),'sha256':sha(output),'code_manifest_sha256':sha(codefile),'Native':0}))
if __name__=='__main__':main()
