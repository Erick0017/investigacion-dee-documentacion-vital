"""Root-only stable RP registration after actual paired gain; default PLAN.

No Native import or material execution. Preserves one complete neutral prefix,
evaluation code, independent primary recalc, exact recipe and finite family
frontdoor under existing Cognitive reproducibilidad. Originals remain intact.
Never edits ACTIVO, snapshots, queues, engine or acquired memories.
"""
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import argparse,ast,copy,hashlib,importlib.util,json,os,shutil,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';RID='pi10_consulta12_familia_desde_P02_R02';CAP='PI10_CONSULTA12_FAMILIA_R02';PREFIX='PI10_R02_P02_NEUTRAL_T922377';ANALYSIS='PI10_R02_REAL12';NEUTRAL='ff303ead4e4e4a0221ef41ae40a5ea34e01bf0b6e27beee3fd0fa9a2754ce9a7';REAL12='706627e093182f35efd2125e189a6527fcf4c27ba9d75dfdc21b2152a3411840';CAP_SHA='2c2560ec44290235de2ba644409e67581d9be6e43642232e619aeaf6c6502a3c';RECIPE_SHA='a78b62c09025fdaa3f2470bf566880ac1ff3dd996d5c764bb02b948eed94cf65';INDEX_SHA='4e9ca5a3bbf45c5e656e208507c54cf9db9d7bc2ba238b1a475f848dd0c0dc30';OLD_FRONT='797865509cc2a255a5ef324ec6c8a0abc2bc7680f8c9121e4d16f2a32f80e7e2';FRESH='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RPF2_20261111A'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
_checked_components=set()
def regular(p):
 # Every existing component is checked at least once in this invocation.
 # File bytes are independently hashed before/after exact copy; this cache
 # avoids repeatedly lstating the same twenty immutable ancestors per file.
 for n in(p,*p.parents):
  if n in _checked_components:continue
  try:info=n.lstat()
  except FileNotFoundError:continue
  need(not(n.is_symlink()or getattr(info,'st_file_attributes',0)&1024),'No symlink/junction source or destination');_checked_components.add(n)
def inside(root,name):
 rel=PurePosixPath(name);need(isinstance(name,str)and rel.parts and not rel.is_absolute()and '\\'not in name and ':'not in name and all(x not in('.','..')for x in rel.parts),'Safe exact member path');p=root.joinpath(*rel.parts);regular(p);return p
def members(root,rows,omit=()):
 expected=set();total=0
 for r in rows:
  need(r['file']not in expected,'No duplicate members');f=inside(root,r['file']);need(f.is_file()and f.stat().st_size==r['bytes']and sha(f)==r['sha256'],'Member mismatch: '+r['file']);expected.add(r['file']);total+=r['bytes']
 actual=set()
 for base,dirs,files in os.walk(root,followlinks=False):
  for name in dirs:regular(Path(base)/name)
  for name in files:
   p=Path(base)/name;regular(p);rel=p.relative_to(root).as_posix()
   if rel not in omit:actual.add(rel)
 need(actual==expected,'Missing/unindexed member in source closure');return total
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def copy_file(source,target):
 regular(source);regular(target);target.parent.mkdir(parents=True,exist_ok=True);need(not target.exists(),'Never overwrite stable new material');shutil.copyfile(source,target);need(sha(source)==sha(target),'Exact preserved copy failed')
def copy_tree(source,target):
 need(not target.exists(),'Never replace stable material');target.mkdir()
 for base,dirs,files in os.walk(source,followlinks=False):
  rel=Path(base).relative_to(source)
  for name in dirs:regular(Path(base)/name);(target/rel/name).mkdir()
  for name in files:copy_file(Path(base)/name,target/rel/name)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--contraste',type=Path);ap.add_argument('--reserva-presupuesto',type=Path);ap.add_argument('--aplicar',action='store_true');a=ap.parse_args()
 neutral=P/'pares/P02_NEUTRAL_T922377';real=P/'pares/REAL2_12_T941139';cap=H/'CAPSULA_EVALUACION_REAL2_R02';recipefile=H/'RP12_RECETA_R02_PREPARADA/receta.json';primaries=P/'fuentes/REAL2_12_CERRADA_PORTABLE_R01';stage=H/'RP_PI10_DELTA_R03_PREPARADO';newpair=RP/'materiales'/PREFIX;newcap=RP/'codigo_preservado'/CAP;analysis=RP/'evidencia'/ANALYSIS;newrecipe=RP/'recetas'/(RID+'.json');backup=P/'control/INCORPORACION_RP_ESTABLE_PI10_R02';front=RP/'reproducir.py';resourcesfile=RP/'RECURSOS.json';readme=RP/'LEER_PRIMERO.md'
 for root in(neutral,real,cap,primaries,stage,RP):regular(root)
 need(sha(neutral/'EXPORTACION_SERVICIO.json')==NEUTRAL and sha(real/'EXPORTACION_SERVICIO.json')==REAL12 and sha(cap/'SISTEMA_CODIGO.json')==CAP_SHA and sha(recipefile)==RECIPE_SHA and sha(primaries/'INDEX.json')==INDEX_SHA,'Pinned actual neutral/fullReal12/evaluation/recipe/primary sources')
 nm=read(neutral/'EXPORTACION_SERVICIO.json');rm=read(real/'EXPORTACION_SERVICIO.json');need(nm['physical']['tick']==922377 and rm['physical']['tick']==941139 and nm['physical']['N']==rm['physical']['N']==67,'Exact frozen cuts, no current-state restoration');nbytes=members(neutral,nm['members'],('EXPORTACION_SERVICIO.json',));need(sha(neutral/'VIDA.deetsnap.gz')==nm['snapshot_sha256'],'Complete neutral Native snapshot')
 cm=read(cap/'SISTEMA_CODIGO.json');cbytes=members(cap,cm['files'],('SISTEMA_CODIGO.json','CONGELACION_CAPSULA_REAL2_R02.json'));need(len(cm['files'])==368,'Actual full evaluation code closure');need(read(cap/'CONGELACION_CAPSULA_REAL2_R02.json')['operator_force_query']is None,'Never calibration-force capsule')
 delta=read(stage/'DELTA_RP_PI10.json');need(delta['source_frontdoor_sha256']==OLD_FRONT and sha(front)==OLD_FRONT,'CAS original RP frontdoor changed; preserve and review');need({r['file']for r in delta['files']}=={'reproducir.py','pi10_vinculo_reproduccion_R02.py','pi10_guardia_reproduccion_R02.py'},'Exact reviewed standard-RP delta')
 for r in delta['files']:need(sha(stage/r['file'])==r['sha256'],'Reviewed RP source changed');ast.parse((stage/r['file']).read_text('utf8'))
 recalc=load('PI10_registration_primary_recalc_only',H/'recalcular_primarios_PI10_R03.py');reference=recalc.bundle(primaries/'INDEX.json');g=reference['groups']['real'];need(g['complete_horizon']and g['observed']==12 and g['physical_delivered']==10 and g['attributed_useful']==9 and g['reserved_useful']==9,'Actual expected unforced Real12 primary projection, not target repair')
 budget=read(P/'REGISTRO_CAMPANA.json')['budget'];newbytes=nbytes+cbytes+sum(f.stat().st_size for f in primaries.rglob('*')if f.is_file())+5000000;existing=sum(f.stat().st_size for f in P.rglob('*')if f.is_file());need(existing+newbytes+budget['closing_storage_reserve_bytes']<budget['new_logical_storage_bytes'],'Logical campaign budget must include stable copies plus closing reserve');need(shutil.disk_usage(RP).free>newbytes+budget['closing_storage_reserve_bytes'],'Real disk must retain closing reserve')
 targets=(newpair,newcap,analysis,newrecipe,RP/'pi10_vinculo_reproduccion_R02.py',RP/'pi10_guardia_reproduccion_R02.py');need(all(not t.exists()for t in targets)and not backup.exists(),'Fresh stable aliases/transaction only; no repeated or partial registration')
 need(all(t.parent.is_dir()for t in targets),'Every stable-store parent must already exist; no implicit new root');resources=read(resourcesfile);need(PREFIX not in resources['pairs']and CAP not in resources['code_capsules'],'Do not overwrite old resource identities');before_files=[front,resourcesfile,readme];cas={str(f):sha(f)for f in before_files}
 if not a.aplicar:print(json.dumps({'mode':'PLAN_ONLY_NO_NATIVE','sources_verified':{'neutral':NEUTRAL,'Real12':REAL12,'code':CAP_SHA,'recipe':RECIPE_SHA,'primary_index':INDEX_SHA},'complete_code_files':368,'logical_added_bound':newbytes,'planned_stable_locations':[str(t)for t in targets],'required_gain':{'reserved_attributed':2,'physical':1},'Native':0}));return
 need(Path(sys.executable).resolve()==(C/'motor/python313/python.exe').resolve(),'Root official Python only');need(a.contraste is not None and a.reserva_presupuesto is not None,'Actual closed NoFail contrast and explicit Root budget reservation required')
 contrastfile=a.contraste.resolve(strict=True);reservationfile=a.reserva_presupuesto.resolve(strict=True);need(contrastfile.is_relative_to(P.resolve())and reservationfile.is_relative_to((P/'control').resolve()),'Local campaign controls/reservation only');rr,nn,gain,physicalgain=load('PI10_registration_actual_C2_schema',H/'pi10_registro_gate_c2_R04.py').check(contrastfile,P,recalc)
 reservation=read(reservationfile);need(reservation.get('schema')=='DEE.PI10.Root.replay_budget_reservation.R02'and reservation.get('life_id')==FRESH and Path(reservation['destination']).resolve()==(P/'estados/RPF2').resolve()and reservation.get('new_worlds')==1 and reservation.get('maximum_new_Native_ticks')==24192 and reservation.get('memory_limit_bytes')==536870912 and reservation.get('budget_registry_sha256')==sha(P/'REGISTRO_CAMPANA.json')and reservation.get('approved_by')=='ROOT','Explicit current one-world/24192ticks/512MiB reservation required')
 need(not(RP/'EJECUCION_MATERIAL.lock').exists(),'No standard-RP material execution during frontdoor CAS')
 # Previously frozen diagnostic import contexts pin the old frontdoor. Their
 # official0tick imports must finish first; no historical context is rewritten.
 for slug in('CUT2','SHAM2','YOKE2'):
  f=P/'estados'/slug/'IMPORTACION_PI10.json';v=read(f);need(v.get('closed')is True and v.get('error')is None and v.get('new_Native_ticks')==0,'Import '+slug+' before changing pinned standard frontdoor')
 marker=P/'PI10_ROOT_NATIVE_WRITER.lock';unrelated=None
 if marker.exists():
  unrelated=read(marker);need(unrelated.get('life_id')=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_YOKE2_01'and unrelated.get('phase')=='OWNED_NATIVE_DRIVER','Only already-imported unrelated YOKE2 may run during static RP registration')
  need(not any(r['file']in('propietario_diagnostico.py','importar_diagnostico.py','ejecutar_diagnostico.py','observador_pasivo.py')for r in delta['files']),'Do not change live Owner/runner/parser tools')
 need(not(P/'estados/RPF2').exists(),'Do not reuse RPF2 destination')
 originalS=C/'sistema';active=originalS/'estado/ACTIVO.json';life=read(active)['life_id'];cardfile=originalS/'estado/vidas'/life/'VIDA.json';protected=[active,cardfile,originalS/read(cardfile)['snapshot']];protected_before={str(f):sha(f)for f in protected};source_before={str(neutral/r['file']):r['sha256']for r in nm['members']};source_before.update({str(cap/r['file']):r['sha256']for r in cm['files']});need(all(sha(Path(k))==v for k,v in cas.items()),'Concurrent frontdoor/config change before transaction')
 backup.mkdir();dump(backup/'INTENT.json',{'schema':'DEE.PI10.stable_RP.registration.intent.R02','started_utc':datetime.now(timezone.utc).isoformat(),'cas_before':cas,'protected_before':protected_before,'contrast':str(contrastfile),'contrast_sha256':sha(contrastfile),'reservation':str(reservationfile),'reservation_sha256':sha(reservationfile),'no_Native_execution':True})
 for f in before_files:copy_file(f,backup/f.name)
 copy_file(contrastfile,backup/'CONTRASTE_CERRADO.json');copy_file(reservationfile,backup/'RESERVA_ROOT.json');copy_tree(neutral,newpair);copy_tree(cap,newcap);need(members(newpair,nm['members'],('EXPORTACION_SERVICIO.json',))==nbytes,'Stable complete neutral copy');need(members(newcap,cm['files'],('SISTEMA_CODIGO.json','CONGELACION_CAPSULA_REAL2_R02.json'))==cbytes,'Stable literal code copy')
 analysis.mkdir();copy_tree(primaries,analysis/'primarios');copy_file(H/'recalcular_primarios_PI10_R03.py',analysis/'recalcular_primarios_PI10_R03.py');copy_file(H/'recalcular_receta_estable_PI10_R02.py',analysis/'recalcular_receta_estable_PI10_R02.py');copy_file(H/'RP12_RECETA_R02_PREPARADA/EXPECTATIVAS_REAL12.json',analysis/'EXPECTATIVAS_REAL12.json');dump(analysis/'REFERENCIA_RECALCULO_REAL12.json',reference)
 am={'schema':'DEE.PI10.stable_recipe_analysis.material.v1','files':[{'file':f.relative_to(analysis).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(analysis.rglob('*'))if f.is_file()]};dump(analysis/'MANIFIESTO_ESTABLE.json',am)
 recipe=read(recipefile);recipe['analysis']={'interface':'DEE.recalculation.root_outdir.v1','product_relative':analysis.relative_to(C).as_posix(),'manifest':'MANIFIESTO_ESTABLE.json','manifest_sha256':sha(analysis/'MANIFIESTO_ESTABLE.json'),'recalculation_script':'recalcular_receta_estable_PI10_R02.py'};recipe['modalities']={'A':'Frozen RAW/receipt/resource recalculation available,0Native','B':'Complete-prefix Native replay enabled but not yet verified','C':'Actual pre-learning P02 acquisition12 with unforced evaluation code; cold replay pending','D':'Real12 observed in original candidate; adoption separately gated','E':'No autonomous repair or unlimited recovery claimed'};recipe['usage']={'listar':'reproducir.py listar','verificar':'reproducir.py verificar '+RID,'recalcular':'reproducir.py recalcular --receta '+RID+' --destino <NUEVO>','material':'reproducir.py reproducir '+RID+' --variante real12 --vida <ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RPF2_IDNUEVO> --destino <NUEVO> --material'};recipe['stable_registration']={'original_actual_recipe_sha256':RECIPE_SHA,'actual_closed_contrast_sha256':sha(contrastfile),'bounded_gain':{'reserved_attributed':gain,'physical':physicalgain},'Native_replay_verified':False,'not_adoption_or_new_learning':True};dump(newrecipe,recipe)
 resources['pairs'][PREFIX]={'product_relative':newpair.relative_to(C).as_posix(),'manifest_sha256':NEUTRAL,'life_id':nm['life_id'],'tick':922377,'N':67,'members':len(nm['members']),'bytes':nbytes,'source_manifest':str(neutral/'EXPORTACION_SERVICIO.json'),'scope':'Complete neutral post-preparation/pre-admission P02, not a second principal; copied literal and source preserved'};resources['code_capsules'][CAP]={'product_relative':newcap.relative_to(C).as_posix(),'manifest':'SISTEMA_CODIGO.json','manifest_sha256':CAP_SHA,'files':368,'bytes':cbytes,'scope':'Unforced REAL2 evaluation code, not calibration force; exactly3 administrative family bindings before import'}
 need(all(sha(Path(k))==v for k,v in cas.items()),'CAS changed before registry update')
 for r in delta['files']:
  target=RP/r['file'];source=stage/r['file']
  if target==front:shutil.copyfile(source,target);need(sha(target)==r['sha256'],'Exact frontdoor delta copy failed')
  else:copy_file(source,target)
 dump(resourcesfile,resources);section='\n\n## PI10 R02: adquisición12 reproducible desde P02 neutral\n\nFuente neutral completa T922377; código de evaluación sin forzar. El catálogo y la comprobación de requisitos no importan DEE. El recálculo usa únicamente RAW/recibos/recursos archivados. La ejecución material exige un ID nuevo y destino diagnóstico explícitos; nunca selecciona ni promueve. Esta incorporación conserva los medios, no acredita todavía el replay Native ni la adopción.\n\nDesde la raíz de Cognitive, con motor\\python313\\python.exe:\n\n```text\nreproducibilidad\\reproducir.py listar\nreproducibilidad\\reproducir.py verificar '+RID+'\nreproducibilidad\\reproducir.py recalcular --receta '+RID+' --destino D:\\ruta\\NUEVA_RECALCULO_PI10\nreproducibilidad\\reproducir.py reproducir '+RID+' --variante real12 --vida '+FRESH+' --destino D:\\ruta\\NUEVA_REPRO_PI10 --material\n```\n\nLa última orden avanza una copia completa:12 episodios,4+8,512MiB, hasta24192ticks nuevos; no es equivalente al recálculo. Antes de ejecutarla durante PI10, el coordinador reserva1mundo y24192ticks en el presupuesto compartido. En otros usos debe fijarse igualmente un presupuesto y un ID nunca usado. No se reintentan IDs inciertos ni se vacían colas. Estado adquirido y recuerdos históricos permanecen separados.\n';readme.write_text(readme.read_text('utf-8-sig')+section,'utf8')
 api=load('PI10_stable_frontdoor_static_verification',front);verification=api.verification(RID);dump(backup/'VERIFICACION_REQUISITOS.json',verification);need(verification['requirements_available'],'New stable static requirements not satisfied; preserve transaction, no automatic retry')
 protected_after={str(f):sha(f)for f in protected};need(protected_after==protected_before and all(sha(Path(k))==v for k,v in source_before.items()),'Original principal/source bytes changed; preserve transaction')
 result={'schema':'DEE.PI10.stable_RP.registration.actual.R02','Native_imports':0,'Native_ticks':0,'not_Native_replay':True,'not_adoption':True,'recipe':RID,'recipe_sha256':sha(newrecipe),'stable_neutral_manifest_sha256':sha(newpair/'EXPORTACION_SERVICIO.json'),'stable_capsule_manifest_sha256':sha(newcap/'SISTEMA_CODIGO.json'),'stable_analysis_manifest_sha256':sha(analysis/'MANIFIESTO_ESTABLE.json'),'frontdoor_before':OLD_FRONT,'frontdoor_after':sha(front),'resources_before':cas[str(resourcesfile)],'resources_after':sha(resourcesfile),'protected_before':protected_before,'protected_after':protected_after,'original_sources_literal_unchanged':True,'unrelated_already_imported_YOKE2_Root_writer_preserved':unrelated,'bounded_gain':{'reserved_attributed':gain,'physical':physicalgain},'budget_reservation_sha256':sha(reservationfile),'logical_copied_prefix_bytes':nbytes,'logical_copied_code_bytes':cbytes,'stable_locations':[str(t)for t in targets],'requirements_available':True,'next':'Root may run read-only recalculation/list/verif, then explicit cold Native family under the reserved budget. Do not claim verified Native replay until its actual result and comparison.'};dump(backup/'INCORPORACION.json',result);print(json.dumps({'proof':str(backup/'INCORPORACION.json'),'sha256':sha(backup/'INCORPORACION.json'),'recipe_sha256':sha(newrecipe),'Native':0}))
if __name__=='__main__':main()
