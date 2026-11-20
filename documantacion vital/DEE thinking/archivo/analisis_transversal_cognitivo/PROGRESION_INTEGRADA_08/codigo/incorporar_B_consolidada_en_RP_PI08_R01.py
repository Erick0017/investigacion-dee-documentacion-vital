"""Conditional Root-only current B preservation, after actual selected public use.

No phase runs on import. Default writes a P8 review stage after all actual
prerequisites exist. --aplicar adds only a new RP capsule/recipe/current-pair
alias and small public-use evidence; it does not copy another whole state.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ast,copy,hashlib,importlib.util,json,os
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_REAL_01'
KEY='PI08_B_CONSOLIDADA_TRANSPORTE_R01';BASEKEY='PI08_B_REAL18_IDENTIDAD_TRANSPORTE_R01'
STAGE=H/'RP_B_CONSOLIDADA_R01_PROPUESTA';PLAN=P/'control/PLAN_RP_B_CONSOLIDADA_PI08_R01.json'
PROOF=P/'control/RP_B_CONSOLIDADA_INCORPORADA_PI08_R01.json'
PUBLIC_ALIAS='PI08_B_USO_PUBLICO_LITERAL_R01'
BKEY='DEE.Cognitive.PI08.successive_contextual_regulation.B.R01'
C2CKEY='DEE.Cognitive.PI04.C2C.coordination.R01'
FKEY='DEE.Cognitive.PI07.regulated_FI_access.R01'
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
base=load(H/'incorporar_B_adquisicion18_en_RP_PI08_R01.py','B_RP_preservation_utilities_only')
require,read,sha,put,regular,copy_new,local=base.require,base.read,base.sha,base.put,base.regular,base.copy_new,base.local

def prepare(usefile):
 require(not PROOF.exists(),'Existing current B registration protected')
 usefile=usefile.resolve(strict=True);require(usefile.is_relative_to(P.resolve()),'Bounded actual public proof')
 use=read(usefile);adopt=read(P/'control/ADOPCION_PRODUCTO_PI08_B.json')
 require(adopt.get('phase')=='COMMITTED'and adopt.get('life_id')==LIFE,'Actual B COMMITTED required')
 require(use.get('life_id')==LIFE and use.get('closed')is True and use.get('criteria_met')is True,'Actual selected public B use must have succeeded and closed')
 require(read(S/'estado/ACTIVO.json').get('life_id')==LIFE,'Exact current selected B required')
 card=read(S/'estado/vidas'/LIFE/'VIDA.json');tick=card['physical']['tick'];alias='PI08_B_CONSOLIDADA_T'+str(tick)
 pair=RP/'materiales'/alias;manifest=read(pair/'EXPORTACION_SERVICIO.json')
 require(manifest['life_id']==LIFE and manifest['physical']==card['physical']and manifest['snapshot_sha256']==card['snapshot_sha256'],'Exact current closed B pair, not pre-public875451')
 require(sha(pair/manifest['native_snapshot'])==card['snapshot_sha256'],'Current full snapshot SHA mismatch')
 preservation=read(pair.parent/(alias+'_PRESERVACION.json'))
 require(preservation.get('source_files_all_unchanged')is True and preservation.get('protected_A_unchanged')is True,'Actual checked closed export required')
 actualuse=preservation.get('actual_selected_public_use',{})
 require(Path(actualuse['path']).resolve()==usefile and actualuse['sha256']==sha(usefile),'Full pair must bind this actual public-use proof')
 if PLAN.exists():
  plan=read(PLAN);require(plan['source_prefix']['manifest_sha256']==sha(pair/'EXPORTACION_SERVICIO.json')and plan['actual_selected_public_use']['sha256']==sha(usefile),'Previous reviewed stage belongs to another cut');return plan
 require(not STAGE.exists(),'Partial stage preserved; a new revision is required')
 parser=load(RP/'observador_pasivo.py','current_B_pure_snapshot_parser')
 view=parser.snapshot_view(pair/manifest['native_snapshot']);meta=view['metadata']
 progress={k:json.loads(meta[v])for k,v in[('B',BKEY),('C2C',C2CKEY),('FI',FKEY)]}
 require(progress['B']['control']['arm']=='real'and 'reference_policy'not in progress['B']and not progress['B'].get('pending')and not progress['B'].get('uncertain'),'Coherent real B acquired prefix required')
 source_manifest=read(RP/'codigo_preservado'/BASEKEY/'SISTEMA_CODIGO.json')
 names={r['file']for r in source_manifest['bounded_used_sources']}|{r['file']for r in adopt['deployed_code']}
 require(len(names)==314,'313 source/provenance files plus the actual COMMITTED profile expected')
 cap=STAGE/'capsule';origins=[]
 for name in sorted(names):
  source=S/name;origin='actual_current_product'
  if not source.exists()and name.startswith('procedencia/ANTES_ACCESO_FI/'):
   source=RP/'codigo_preservado'/BASEKEY/name;origin='preserved_literal_historical_beforeimage'
  copy_new(source,local(cap,name));origins.append({'file':name,'bytes':source.stat().st_size,'sha256':sha(source),'source':str(source),'origin':origin})
 for name,digest in base.SCIENCE.items():require(sha(cap/'capacidades'/name)==digest,'Literal B scientific source changed')
 importer=cap/'app/importacion_emparejada.py';copy_new(importer,cap/'procedencia/ANTES_RP_B_CURRENT/importacion_emparejada.py')
 text=importer.read_text('utf8');anchor='def import_pair(store,directory,life):\n';require(text.count(anchor)==1,'Exact importer function')
 text=text.replace(anchor,anchor+"    if not life.startswith('"+base.PREFIX+"'):raise ValueError('Explicit fresh BRP descendant required; never principal.')\n")
 anchor="        mapping['external_directory_scaffold']=restore_known_device_directories(store.state/'servicios_locales'/life)\n";require(text.count(anchor)==1,'Pre-Native import transport hook')
 text=text.replace(anchor,anchor+"        from .estructuras_exportadas_PI08_R01 import restore_exported_directories\n        mapping['exported_directory_transport']=restore_exported_directories(source,m,folder,store.state/'servicios_locales'/life)\n")
 ast.parse(text);importer.write_text(text,encoding='utf8')
 owner=cap/'app/mundo_genesis_apd05.py';copy_new(owner,cap/'procedencia/ANTES_RP_B_CURRENT/mundo_genesis_apd05.py')
 lines=owner.read_text('utf8').splitlines(True);patched=[];count=0
 for line in lines:
  patched.append(line)
  if line.strip()=='from capacidades import pi08_revision_flexible_B_R01 as pi08b':
   indent=line[:len(line)-len(line.lstrip())];count+=1
   patched.extend([indent+'from capacidades import pi08_permiso_B_reproduccion_R02 as rp_identity\n',indent+'pi08b=rp_identity.component(self.a,pi08b)\n'])
 require(count==5,'Five exact current B owner paths');text=''.join(patched);ast.parse(text);owner.write_text(text,encoding='utf8')
 copy_new(H/'estructuras_exportadas_PI08_R01.py',cap/'app/estructuras_exportadas_PI08_R01.py')
 copy_new(H/'pi08_permiso_B_reproduccion_R02.py',cap/'capacidades/pi08_permiso_B_reproduccion_R02.py')
 rows=[]
 for f in sorted(cap.rglob('*')):
  if f.is_file():
   if f.suffix=='.py':ast.parse(f.read_text('utf-8-sig'))
   rows.append({'file':f.relative_to(cap).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
 require(len(rows)==318,'314 current/provenance files plus2helpers/2beforeimages')
 put(cap/'SISTEMA_CODIGO.json',{'schema':'DEE.PI08.B.current_code_capsule.explicit_transport.R01','files':rows,'current_sources':origins,'frozen_scientific_files':base.SCIENCE,'Native_executed':False,'new_material_frontdoor_replay_verified':False})
 public=STAGE/'public_evidence';copy_new(usefile,public/usefile.name)
 for row in use['rows']:
  source=Path(row['primary']).resolve(strict=True);require(source.is_relative_to(P.resolve())and sha(source)==row['primary_sha256'],'Actual selected-use primary hash')
  copy_new(source,public/source.name)
 put(public/'MANIFIESTO_ESTABLE.json',{'schema':'DEE.PI08.B.actual_selected_public_evidence.R01','files':[{'file':f.relative_to(public).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(public.rglob('*'))if f.is_file()],'Native_executed_by_preservation':False})
 rid='pi08_b_consolidada_uso_T'+str(tick)+'_R01'
 states=[{'label':name+'_STATE','literal':{'modo':mode},'require_zero_ticks':True,'read_path':['result','rows',0,'progress','ordinal'],'expected':progress[name]['ordinal']}
  for name,mode in[('B','eci01-pi08-b-estado'),('C2C','eci01-pi04-c2c-estado'),('FI','eci01-pi07-fi-acceso-estado')]]
 physicalchecks=[{'label':'physical_'+k,'operation':'value','values':[{'step':'B_STATE','path':['result','rows',0,'physical',k]}],'expected':v}for k,v in manifest['physical'].items()]
 variants={'estado_operativo':{'batches':[states],'final_checks':physicalchecks,'native_receipt_expectations':{'unique_requested':0,'applied':0,'rejected':0,'pending_or_other':0}}}
 remaining=progress['B']['control']['max_ordinal']-progress['B']['ordinal']
 if remaining>0:
  variants['siguiente_regulacion']={'batches':[[copy.deepcopy(states[0]),{'label':'B_NEXT','literal':{'modo':'eci01-pi08-b-episodio'},'feedback':'real','actuator':'closed','read_path':['result','rows',0,'actual_failed'],'expected':False,'receipt_paths':[['result','rows',0,'requests']],'stop_on_unapplied_receipt':False}]],'interpretation':'Prospective next resource, evaluated only after actual Native output; no successful replay is claimed.'}
 acquired=read(RP/'recetas'/(base.RID+'.json'))
 recipe={'schema':'DEE.reproduction.recipe.v1','id':rid,'title':'PI08 B: actual current acquired continuation and prospective next use','revision':'R01_CURRENT_COMMITTED_B_EXPLICIT_TRANSPORT',
  'prefix':alias,'code_capsule_key':KEY,'required_life_prefix':base.PREFIX,'requires_explicit_material':True,'reproduction_enabled':True,'variants':variants,'analysis':copy.deepcopy(acquired['analysis']),
  'verification':{'state':'PREPARADA_REPLAY_NATIVE_PENDIENTE','Native_replay_verified':False,'B_new_CLI_replay_verified':False},
  'assistance':['Exact full learned B prefix, fixed Native actor/body/readers, diagnostic identity/directory transport only.','Actual selected public route was tested separately; diagnostic descendants do not claim selection/public alias.'],
  'limitations':['Shares acquired full history; not independent T0 acquisition or replay of18.','New current-state material CLI remains pending.','Documentary recálculo is the previously preserved REAL18, not a new verification of future use.','Old R03 progress12 is historical and its six old resources are superseded by B; only B remaining'+str(remaining)+' is prospective.'],
  'sources':{'actual_current_full_pair_manifest_sha256':sha(pair/'EXPORTACION_SERVICIO.json'),'capsule_manifest_sha256':sha(cap/'SISTEMA_CODIGO.json'),'actual_selected_public_use':{'product_relative':'reproducibilidad/materiales/'+PUBLIC_ALIAS+'/'+usefile.name,'sha256':sha(usefile)},'remaining_B_resources':remaining}}
 put(STAGE/'receta.json',recipe)
 resources=read(RP/'RECURSOS.json');require(KEY not in resources['code_capsules']and alias not in resources['pairs']and not(RP/'recetas'/(rid+'.json')).exists(),'Only additive new RP aliases')
 resources['code_capsules'][KEY]={'product_relative':'reproducibilidad/codigo_preservado/'+KEY,'manifest':'SISTEMA_CODIGO.json','manifest_sha256':sha(cap/'SISTEMA_CODIGO.json')}
 resources['pairs'][alias]={'product_relative':'reproducibilidad/materiales/'+alias,'manifest_sha256':sha(pair/'EXPORTACION_SERVICIO.json'),'life_id':LIFE,'tick':tick};put(STAGE/'RECURSOS_PROPUESTOS.json',resources)
 plan={'schema':'DEE.PI08.B.RP.current_continuation.CAS_plan.R01','resource_before_sha256':sha(RP/'RECURSOS.json'),'recipe_id':rid,'recipe_sha256':sha(STAGE/'receta.json'),'capsule_key':KEY,'capsule_manifest_sha256':sha(cap/'SISTEMA_CODIGO.json'),'capsule_files':318,
  'source_prefix':{'path':str(pair),'manifest_sha256':sha(pair/'EXPORTACION_SERVICIO.json')},'actual_selected_public_use':{'path':str(usefile),'sha256':sha(usefile)},'public_evidence_manifest_sha256':sha(public/'MANIFIESTO_ESTABLE.json'),'remaining_B_resources':remaining,'Native_executed':False,'B_new_CLI_replay_verified':False}
 put(PLAN,plan);return plan

def main(args):
 plan=prepare(args.use_proof);require(sha(RP/'RECURSOS.json')==plan['resource_before_sha256'],'CAS registry changed')
 require(sha(STAGE/'receta.json')==plan['recipe_sha256'],'Staged recipe changed')
 for folder,name in[(STAGE/'capsule','SISTEMA_CODIGO.json'),(STAGE/'public_evidence','MANIFIESTO_ESTABLE.json')]:
  for row in read(folder/name)['files']:
   f=local(folder,row['file']);require(f.stat().st_size==row['bytes']and sha(f)==row['sha256'],'Staged member changed')
 if args.aplicar:
  destinations=[(STAGE/'capsule',RP/'codigo_preservado'/KEY),(STAGE/'public_evidence',RP/'materiales'/PUBLIC_ALIAS)]
  recdest=RP/'recetas'/(plan['recipe_id']+'.json');require(not recdest.exists()and all(not d.exists()for _,d in destinations),'Preserved destination already exists')
  copy_new(RP/'RECURSOS.json',P/'control/RECURSOS_ANTES_B_CURRENT_RP_PI08_R01.json')
  for source,dest in destinations:
   for f in sorted(source.rglob('*')):
    if f.is_file():copy_new(f,dest/f.relative_to(source))
  copy_new(STAGE/'receta.json',recdest);require(sha(RP/'RECURSOS.json')==plan['resource_before_sha256'],'Concurrent registry writer')
  temp=RP/'RECURSOS.json.PI08_B_CURRENT_WRITING'
  with temp.open('xb')as f:f.write((STAGE/'RECURSOS_PROPUESTOS.json').read_bytes());f.flush();os.fsync(f.fileno())
  os.replace(temp,RP/'RECURSOS.json')
  put(PROOF,{**plan,'schema':'DEE.PI08.B.RP.current_continuation.applied.R01','applied':True,'recorded_utc':datetime.now(timezone.utc).isoformat(),'recipe_path':str(recdest),'code_capsule':str(RP/'codigo_preservado'/KEY),'resources_after_sha256':sha(RP/'RECURSOS.json'),'new_full_state_or_engine_copy':False,'principal_or_source_code_modified':False})
 result=PROOF if args.aplicar else PLAN
 print(json.dumps({'proof':str(result),'sha256':sha(result),'mode':'APPLIED_ROOT_ONLY'if args.aplicar else'P8_PLAN_ONLY','Native_executed':False,'B_new_CLI_replay_verified':False}))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--use-proof',type=Path,required=True);p.add_argument('--aplicar',action='store_true');main(p.parse_args())
