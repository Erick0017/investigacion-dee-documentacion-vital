"""Root-only additive PI06 scientific/instrumental annex; no operational writes.

Default stages the literal old registry and a proposal after actual RP addition.
--aplicar changes only one new PI06 key under the existing scientific register,
with a CAS check. All earlier statements and dates remain historical bytes in
the preserved original and equal JSON values in the updated registry.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,uuid
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
REV=P.parent/'REVISION_TRANSVERSAL.json';STAGE=H/'REVISION_PI06_INSTRUMENTAL_R01';KEY='progression_integrated_PI06_instrumental_science'
MAIN='ECI02_PI03_REPRO_PI04_PI05_MAIN_01';SNAP='af74c8f47e43ed3b2395a338a23a6cbd42f105ec2cff4daac15b7a4d45e90832'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def encoded(x):return (json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def regular(p):
 for q in(p,*p.parents):
  if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked registry/material path')
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(encoded(x))
def protected():
 act=C/'sistema/estado/ACTIVO.json';a=read(act);cardfile=C/'sistema/estado/vidas'/MAIN/'VIDA.json';card=read(cardfile)
 if a['life_id']!=MAIN or card['snapshot_sha256']!=SNAP or card['physical']['tick']!=824911:raise ValueError('Selected principal differs; reconcile instead of asserting unchanged')
 return {str(p):sha(p)for p in(act,cardfile,C/'sistema'/card['snapshot'])}
def reference(path):
 regular(path)
 return {'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path)}
def main(a):
 regular(REV);before=protected()
 if not a.aplicar:
  if STAGE.exists():raise FileExistsError('Prior scientific annex proposal is protected')
  proof=a.incorporacion.resolve(strict=True);regular(proof)
  if proof!= (P/'control/INCORPORACION_REPRODUCIBILIDAD_INSTRUMENTAL_PI06_R01.json').resolve():raise ValueError('Exact actual Root instrumental registration proof required')
  inc=read(proof)
  if inc.get('applied')is not True or inc.get('Native_executed')is not False or inc.get('new_ticks')!=0:raise ValueError('Do not document an incorporation that was only proposed')
  manifest=Path(inc['code_capsule'])/'SISTEMA_CODIGO.json'
  if sha(manifest)!=inc['capsule_manifest_sha256']:raise ValueError('Registered capsule manifest differs')
  record=read(P/'REGISTRO_CAMPANA.json')
  if record['Native_ticks_closed']!=7882 or record['latest_closed_science']['diagnostic_worlds']!=12 or record['current_native_plan']is not None:raise ValueError('Actual closed Native ledger differs; preserve and reconcile')
  oldbytes=REV.read_bytes();old=json.loads(oldbytes)
  if KEY in old:raise ValueError('Existing PI06 annex is protected')
  verification_folder=RP/'verificaciones/pi06_transitorio_izq0_y_continuacion_R01';verifications=[reference(f)for f in sorted(verification_folder.glob('*.json'))]
  if len(verifications)!=1:raise ValueError('Exactly one actual R01 cold verification is required')
  verified=read(Path(verifications[0]['path']))
  if any(verified.get(key)is not True for key in('fixed_local_criteria_met','actual_native_execution_completed','owner_closed_coherently')):raise ValueError('Use actual registered Native execution; do not infer from recipe PREPARADA status')
  sources=[reference(P/'control'/name)for name in('CONTRASTE_BASELINE_COMPLETO_PI06_R01.json','PI06_DISC_IZQ0_R01.json','RECALCULO_CAUSAL_INTERRUPCION_PI06_R02.json',
   'PI06_AMBIENTE_NUBE_R06.json','PI06_CONFIRMACION_FINA_R04.json','PI06_CONFIRMACION_CONTROL67_R04.json')]
  pair=RP/'materiales/PI06_POST_INTERFERENCIA_T826449/EXPORTACION_SERVICIO.json'
  if sha(pair)!='3e2e728b31b4f8e8b9bac165251c670c1f4691e5f4c1946895302d865be90e14':raise ValueError('Exact historical complete pre-intervention pair required')
  annex={'schema':'DEE.PI06.scientific_instrumental_annex.v1','recorded_utc':datetime.now(timezone.utc).isoformat(),'campaign':str(P),
   'state':'NATIVE_CLOSED_INSTRUMENTS_REGISTERED_NO_PRINCIPAL_ADOPTION','current_selection_corrobated':{'life_id':MAIN,'N':67,'T':824911,'snapshot_sha256':SNAP},
   'current_selection_authority':'Actual product ACTIVO/VIDA/checkpoint, not older current_operation or resume paragraphs in this historical scientific register.',
   'old_registry_fields_preserved':'All pre-existing keys, including older current_operation/resume statements, retain their prior historical values. No selector or principal state is changed by this annex.',
   'Native_ledger':reference(P/'REGISTRO_CAMPANA.json'),'new_Native_ticks_all_branches':7882,'diagnostic_worlds':12,
   'results':{'baseline938_normal_vs_global':'Complete bounded Native state/prefix identity; no universal passivity claim.',
    'R01':'Transient FI14>3 results -1,+1,-1 with529/529. Actual cold600 replay had complete Native state/prefix equality.',
    'R02':'Paired legal contraflow/sham201ticks177/177 each; subsequent original FI+1/-1. Operator intervention P0, not learned repair.',
    'R03':'Same fixed61-source cloud,58applied/3occupied; coarse host safety stopped+67 before FI/C2C. No measured functional failure.',
    'R04_fine':'Same source/pulse with every-boundary host safety stopped+15. Host stop, no learned regulation.',
    'R04_control':'Existing DISC advanced1300ticks; FAILED_PRESERVED for declared bound. Any observed material product does not erase protocol failure.'},
   'incorporation':reference(proof),'code_capsule':reference(manifest),'historical_complete_source_pair':reference(pair),'R01_actual_registered_Native_verifications':verifications,
   'availability':{'R01':'Existing recipe literal kept; separate actual Native verification registered.',
    'R02':'New executable diagnostic recipe prepared from conserved prefix; no independent Native cold replay yet.',
    'R03':'Recipe/materials preserved; new material execution blocked pending future resource/safety review.',
    'R04':'Code/evidence preserved with fixed historical IDs; not a fresh-ID replay recipe.'},
   'sources':sources,'limits':['No PI06 principal acquisition or mental faculty, autonomous repair, spontaneous regulation or general agency claimed.',
    'Common-prefix clones are paired controls, not independent organisms. Material0, NULL, occupied rejection and unresolved transport are distinct.',
    'Full states remain local; a small analysis ZIP is not an executable backup.']}
  new={**old,KEY:annex}
  STAGE.mkdir();(STAGE/'REVISION_ANTES.json').write_bytes(oldbytes);save(STAGE/'REVISION_PROPUESTA.json',new)
  plan={'schema':'DEE.PI06.transversal_annex.plan.v1','target':str(REV),'before_sha256':hashlib.sha256(oldbytes).hexdigest(),'after_sha256':sha(STAGE/'REVISION_PROPUESTA.json'),
   'new_key_only':KEY,'previous_keys_and_values_unchanged':{k:v for k,v in new.items()if k!=KEY}==old,
   'Native_executed':False,'product_files_modified':False,'protected':before,'incorporation_proof':reference(proof)}
  save(STAGE/'PLAN.json',plan);print(json.dumps({'plan':str(STAGE/'PLAN.json'),'sha256':sha(STAGE/'PLAN.json'),'Native_executed':False},ensure_ascii=False));return
 plan=read(STAGE/'PLAN.json');old=read(STAGE/'REVISION_ANTES.json');proposed=read(STAGE/'REVISION_PROPUESTA.json')
 if plan['protected']!=before or plan['before_sha256']!=sha(REV)or plan['before_sha256']!=sha(STAGE/'REVISION_ANTES.json')or plan['after_sha256']!=sha(STAGE/'REVISION_PROPUESTA.json'):raise ValueError('Scientific registry/protected-state CAS differs')
 if set(proposed)!=set(old)|{KEY}or{key:value for key,value in proposed.items()if key!=KEY}!=old:raise ValueError('Only one new scientific annex is permitted')
 tmp=REV.with_name(REV.name+'.PI06_'+uuid.uuid4().hex+'.tmp')
 with tmp.open('xb')as f:f.write((STAGE/'REVISION_PROPUESTA.json').read_bytes());f.flush();os.fsync(f.fileno())
 if sha(REV)!=plan['before_sha256']:raise ValueError('Concurrent transversal update; preserve staged temp')
 os.replace(tmp,REV)
 if protected()!=before or sha(REV)!=plan['after_sha256']:raise RuntimeError('Post-application verification differs')
 output=P/'control/REVISION_TRANSVERSAL_PI06_ANEXADA_R01.json';save(output,{'schema':'DEE.PI06.transversal_annex.applied.v1','applied':True,'recorded_utc':datetime.now(timezone.utc).isoformat(),
  'target':str(REV),'before_sha256':plan['before_sha256'],'after_sha256':sha(REV),'new_key_only':KEY,'all_preexisting_values_unchanged':True,'original_literal_preserved':str(STAGE/'REVISION_ANTES.json'),
  'Native_executed':False,'new_ticks':0,'product_or_selector_or_principal_modified':False,'protected_before':before,'protected_after':protected()})
 print(json.dumps({'proof':str(output),'sha256':sha(output),'Native_executed':False},ensure_ascii=False))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--incorporacion',type=Path);ap.add_argument('--aplicar',action='store_true');a=ap.parse_args()
 if not a.aplicar and a.incorporacion is None:ap.error('--incorporacion actual is mandatory for proposal')
 main(a)
