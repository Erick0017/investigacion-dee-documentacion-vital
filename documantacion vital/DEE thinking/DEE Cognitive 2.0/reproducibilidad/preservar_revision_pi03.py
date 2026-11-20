"""Register explicit PI03 code/full-pair materials and prepared task recipes.

Default is a read-only source check. --aplicar copies and hashes frozen files,
never imports DEE, opens a world, updates ACTIVO or promotes a diagnostic. The
descriptor is supplied after Root's own scientific/code validation.
"""
from pathlib import Path
import argparse,copy,datetime,hashlib,json,os,shutil,sqlite3,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;PRODUCT=HERE.parent;DEE=PRODUCT.parent
sys.path.insert(0,str(HERE))
from reproducir import checked_files,inside,sha,read,unlinked
from observador_pasivo import snapshot_view
ROW=['result','rows',0]

def bounded_source(value):
 p=Path(value).absolute();p=unlinked(p,DEE)
 if not p.is_relative_to(DEE.resolve()):raise ValueError('Only explicit sources inside this DEE tree')
 return p
def valid_name(value):
 import re
 if not re.fullmatch(r'PI03_[A-Za-z0-9_]{1,64}',value):raise ValueError('New PI03 alias/key required; historical entries are protected')
 return value
def cp(source,target,expected):
 before=sha(source)
 if before!=expected:raise ValueError('Source identity changed: '+str(source))
 target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():
  if sha(target)!=expected:raise FileExistsError('Different preserved destination protected: '+str(target))
 else:
  with source.open('rb')as a,target.open('xb')as b:shutil.copyfileobj(a,b)
 if sha(source)!=expected or sha(target)!=expected:raise ValueError('Copy/source changed during preservation')
def write_new_or_same(path,value):
 data=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8')
 if path.exists():
  if path.read_bytes()!=data:raise FileExistsError('Existing different recipe/proof is protected: '+str(path))
 else:
  path.parent.mkdir(parents=True,exist_ok=True)
  with path.open('xb')as f:f.write(data)
def pair_check(entry):
 source=bounded_source(entry['source']);manifest=source/'EXPORTACION_SERVICIO.json'
 if sha(manifest)!=entry['manifest_sha256']:raise ValueError('Frozen full-pair manifest differs')
 m=read(manifest)
 if m.get('schema')!='DEE.persistent_service.paired_export.v1'or not m.get('queue_journal_required'):
  raise ValueError('A complete paired export, not raw arrays or a live SQLite copy, is required')
 if m['life_id']!=entry['life_id']or m['physical']['tick']!=entry['tick']or m['physical']['N']!=entry['N']:
  raise ValueError('Frozen parent identity/N/tick differs')
 summary=checked_files(source,m['members'],exact=True,omit=('EXPORTACION_SERVICIO.json',))
 view=snapshot_view(source/'VIDA.deetsnap.gz')
 if any(view['physical'][key]!=m['physical'][key]for key in('N','tick','RAW_sha256','clocks_sha256'))or view['encoded_sha256']!=m['snapshot_sha256']:
  raise ValueError('Complete snapshot/manifest physical identity differs')
 con=sqlite3.connect((source/'cola.sqlite3').as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Frozen queue is not intact')
 finally:con.close()
 return source,m,summary
def task_recipe(descriptor,pairs,capsule,code_root):
 t=descriptor['task'];alias=t['warm_alias'];valid_name(alias)
 if alias not in pairs:raise ValueError('Warm pre-acquisition alias must be explicitly registered')
 if pairs[alias].get('role')!='warm':raise ValueError('Acquisition recipe requires an explicitly identified prepared/unlearned warm prefix, never a final learned state')
 protocol_path=inside(code_root,t['protocol_relative']);p=read(protocol_path)
 if p.get('schema')!='PI03.useful_delayed_task.protocol.v1':raise ValueError('Expected exact R02 task protocol')
 series=t.get('series','continuous')
 if series not in('continuous','development'):raise ValueError('Only fixed R02 development/continuous series')
 order=['development','reserved']if series=='continuous'else['development']
 count=sum(len(p['fixtures'][s]['delay_laps'])for s in order)
 if count not in(6,14):raise ValueError('Frozen finite R02 opportunity count differs')
 expectations=t.get('expected_products',{})
 if set(expectations)-{'real','return_nonfailure','actuator_null'}:raise ValueError('Only the three declared control histories')
 enabled=bool(t.get('enable_replay',False))
 if enabled and(p.get('status')!='SEALED_FOR_TASK'or set(expectations)!={'real','return_nonfailure','actuator_null'}):
  raise ValueError('Do not enable a draft/unscored recipe; Root must supply sealed protocol and observed reproduction expectations')
 variants={}
 for control in('real','return_nonfailure','actuator_null'):
  admit={'label':'admit','literal':{'modo':'eci01-pi03-tarea-admitir','serie':series,'control':control},'feedback':'omit'}
  if p['resource_source']=='native_arithmetic_chain':
   admit['receipt_paths']=[ROW+['resource_source',side,'native_operation','native_trial','requests']for side in('first','second')]
  steps=[admit]
  for i in range(count):
   steps.append({'label':'opportunity_%02d'%i,'literal':{'modo':'eci01-pi03-tarea-oportunidad'},'feedback':'omit',
    'read_path':ROW+['reader','choice'],'receipt_paths':[ROW+['requests']],'stop_on_NULL':True})
  steps.append({'label':'final','literal':{'modo':'eci01-pi03-tarea-estado'},'feedback':'omit'})
  v={'batches':[steps]}
  if control in expectations:
   expected=expectations[control]
   if type(expected)is not int or not 0<=expected<=count:raise ValueError('Bounded recorded product count required')
   v['final_checks']=[{'label':'actual_useful_products','operation':'sum_true',
    'values':[{'step':'opportunity_%02d'%i,'path':ROW+['useful_product']}for i in range(count)],'expected':expected}]
  receipt_expectations=t.get('expected_native_receipts',{}).get(control)
  if receipt_expectations is not None:
   if set(receipt_expectations)!={'unique_requested','applied','rejected'}or any(type(x)is not int or x<0 for x in receipt_expectations.values()):raise ValueError('Exact nonnegative Native receipt denominators required')
   v['native_receipt_expectations']=receipt_expectations
  variants[control]=v
 if t.get('expected_final_physical_from_real_alias'):
  expected_alias=t['expected_final_physical_from_real_alias'];entry=pairs[expected_alias]
  index=PRODUCT/entry['product_relative']/'EXPORTACION_SERVICIO.json'
  if sha(index)!=entry['manifest_sha256']:raise ValueError('Expected-physics reference manifest changed')
  reference=read(index)
  variants['real']['expected_final_physical']={key:reference['physical'][key]for key in('N','tick','RAW_sha256','clocks_sha256')}
  variants['real']['expected_final_physical_source']={'alias':expected_alias,'manifest_sha256':entry['manifest_sha256'],'source_life':entry['life_id'],'scope':'Predetermined real-history physical result for exact reproduction; metadata/transport identity is not required to be binary-identical. Check passively after closure, never feed to the actor.'}
 return {'schema':'DEE.reproduction.recipe.v1','id':t.get('recipe_id','pi03_tarea_R02_adquisicion'),
  'title':'PI03 R02 adquisición y uso con retorno diferido desde prefijo completo preparado, aún sin aprendizaje',
  'revision':'PI03_R02_PRESERVADA','prefix':alias,'code_capsule_key':capsule,'reproduction_enabled':enabled,'variants':variants,
  'modalities':{'A':'Protocol, source, manifest and Root evidence identified separately','B':'Native reproduction requires a new explicit diagnostic destination','C':'Acquisition starts from the real complete prepared/unlearned prefix, never an acquired final state','D':'Not a material test of protected MAIN','E':'Not restoration or general repair'},
  'assistance':'Prepared anatomy, opportunity order, device laws, queries, inverse efference and generic consequence transducers. Native produces bank choice; host does not choose a successful route. Arithmetic data transport is prepared and uses actual outputs.',
  'limitations':'Prepared recipe is not a completed reproduction. Native NULL stops the source protocol and preserves the future; no expected-answer fallback, reset, phase search or decoder override. Controls share a prefix, not independent replicas.',
  'protocol':{'product_relative':'reproducibilidad/codigo_preservado/'+capsule+'/'+t['protocol_relative'],'sha256':sha(protocol_path),'series':series,'opportunities':count,'source_status':p.get('status')},
  'sources':['codigo_preservado/'+capsule+'/'+t['protocol_relative']],
  'verification':{'state':'PREPARED_PENDING_NATIVE_REPRODUCTION','Root_observed_reproduction_expectations':expectations,
   'no_new_Native_execution_by_preservation_helper':True},
  'blockers':[]if enabled else['Root must finish the original R02 validation, provide exact observed reproduction expectations, and explicitly enable the sealed replay.']}
def panel_recipe(descriptor,pairs,key):
 p=descriptor['panel'];alias=p['final_alias'];valid_name(alias)
 if alias not in pairs:raise ValueError('Final complete-state alias required')
 if pairs[alias].get('role')!='final':raise ValueError('Final panel requires an explicitly identified complete final state')
 r=copy.deepcopy(read(HERE/'recetas/panel_12.json'));r['id']=p.get('recipe_id','pi03_panel_principal_R02')
 r['title']='Doce usos heredados desde el corte final PI03 identificado, en una copia diagnóstica'
 r['prefix']=alias;r['code_capsule_key']=key;r['revision']='PI03_FINAL_PREPARADA';r['reproduction_enabled']=bool(p.get('enable_replay',False))
 r['limitations']='Uses the explicitly pinned final PI03 full pair and its own source capsule, never the old PI02 owner with new metadata. Same twelve prepared witnesses/decoder, actual integer chaining and material queries. Not a new acquisition or a test materially performed on protected MAIN.'
 r['verification']={'state':'PREPARED_PENDING_NATIVE_VERIFICATION','source_final_life':pairs[alias]['life_id'],'source_final_tick':pairs[alias]['tick'],'do_not_inherit_old_panel_cut':True}
 r['blockers']=[]if r['reproduction_enabled']else['Root must finish final-state conservation/reopening validation before enabling this new recipe.']
 return r
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--descriptor',required=True,type=Path)
 parser.add_argument('--aplicar',action='store_true');parser.add_argument('--comprobante',type=Path);args=parser.parse_args()
 descriptor_path=bounded_source(args.descriptor);d=read(descriptor_path)
 if d.get('schema')!='DEE.reproducibility.PI03.materials_descriptor.v1':raise ValueError('Exact explicit descriptor schema required')
 if args.aplicar and d.get('readonly_check_only')is True:raise ValueError('This descriptor is a read-only helper test; it cannot register a scientific revision')
 cfgpath=HERE/'RECURSOS.json';before=cfgpath.read_bytes();cfg=json.loads(before);old_global=copy.deepcopy(cfg['code_capsule'])
 capsule=d['code_capsule'];key=valid_name(capsule['key']);source=bounded_source(capsule['source_system']);manifest=bounded_source(capsule['files_manifest'])
 if capsule.get('files_manifest_sha256')and sha(manifest)!=capsule['files_manifest_sha256']:raise ValueError('Frozen source-code index differs')
 m=read(manifest)
 if not{'gestionar.py','app/lives.py','app/cola_local.py','app/importacion_emparejada.py','app/process_control.py'}<={v['file']for v in m['files']}:
  raise ValueError('A complete shared Cognitive source capsule is required')
 for v in m['files']:
  if v['file'].startswith(('estado/','runtime/'))or Path(v['file']).suffix.lower()in('.pyd','.dll','.whl','.sqlite3'):
   raise ValueError('No state/engine duplication inside source capsule')
 codecheck=checked_files(source,m['files']);capsule_target=HERE/'codigo_preservado'/key
 pairdata=[];registered=copy.deepcopy(cfg['pairs'])
 for item in d.get('pairs',[]):
  alias=valid_name(item['alias']);src,pm,check=pair_check(item);dest=HERE/'materiales'/alias
  entry={'product_relative':dest.relative_to(PRODUCT).as_posix(),'manifest_sha256':item['manifest_sha256'],'life_id':item['life_id'],'N':item['N'],'tick':item['tick'],'role':item.get('role'),'source':str(src)}
  if alias in registered and any(registered[alias].get(k)!=entry[k]for k in('product_relative','manifest_sha256','life_id','tick')):
   raise FileExistsError('Existing different frozen pair alias is protected')
  registered[alias]=entry;pairdata.append((item,src,pm,dest,check))
 # Prepare recipes against the genuine source capsule; no source module imports.
 proposed=[]
 if d.get('task'):proposed.append(task_recipe(d,registered,key,source))
 if d.get('panel'):proposed.append(panel_recipe(d,registered,key))
 report={'schema':'DEE.reproducibility.PI03.preservation.v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'descriptor':str(descriptor_path),'descriptor_sha256':sha(descriptor_path),'code_capsule_key':key,'code_source':str(source),
  'code_manifest_sha256':sha(manifest),'code_check':codecheck,'pairs':[{'alias':a['alias'],'source':str(s),'destination':str(t),'verification':c}for a,s,_,t,c in pairdata],
  'recipes':[{'id':r['id'],'prefix':r['prefix'],'enabled':r['reproduction_enabled'],'verification':r['verification']}for r in proposed],
  'applied':args.aplicar,'new_native_ticks':0,'DEE_imports':0,'ACTIVO_changed':False,'global_PI02_capsule_changed':False}
 if not args.aplicar:print(json.dumps(report,ensure_ascii=False,indent=2));return 0
 if args.comprobante is None:raise ValueError('Explicit new preservation proof path is required when applying')
 proof=args.comprobante.absolute();unlinked(proof.parent,DEE)
 if proof.exists()or not proof.is_relative_to(DEE.resolve()):raise ValueError('New proof inside DEE tree only')
 for v in m['files']:cp(inside(source,v['file']),capsule_target/v['file'],v['sha256'])
 cp(manifest,capsule_target/'SISTEMA_CODIGO.json',sha(manifest));checked_files(capsule_target,m['files'])
 cfg.setdefault('code_capsules',{})
 capentry={'product_relative':capsule_target.relative_to(PRODUCT).as_posix(),'manifest':'SISTEMA_CODIGO.json','manifest_sha256':sha(manifest)}
 if key in cfg['code_capsules']and cfg['code_capsules'][key]!=capentry:raise FileExistsError('Existing different source revision protected')
 cfg['code_capsules'][key]=capentry
 for item,src,pm,dest,check in pairdata:
  for v in pm['members']:cp(inside(src,v['file']),dest/v['file'],v['sha256'])
  cp(src/'EXPORTACION_SERVICIO.json',dest/'EXPORTACION_SERVICIO.json',item['manifest_sha256'])
  checked_files(dest,pm['members'],exact=True,omit=('EXPORTACION_SERVICIO.json',))
 cfg['pairs']=registered
 for r in proposed:
  # Source path becomes the stable capsule path after preservation, not a
  # campaign temporary directory used during Root's original development.
  if r.get('protocol'):
   relative=d['task']['protocol_relative'];p=capsule_target/relative
   r['protocol']['product_relative']=p.relative_to(PRODUCT).as_posix();r['sources']=[p.relative_to(HERE).as_posix()]
  write_new_or_same(HERE/'recetas'/(r['id']+'.json'),r)
 if cfg['code_capsule']!=old_global:raise ValueError('Historical default capsule must remain unchanged')
 if cfgpath.read_bytes()!=before:raise RuntimeError('Resource registry changed concurrently; copies retained, no overwrite')
 report['previous_RECURSOS_sha256']=hashlib.sha256(before).hexdigest();report['previous_RECURSOS']=json.loads(before)
 temp=cfgpath.with_name('RECURSOS.PI03_'+sha(descriptor_path)[:12]+'.writing')
 with temp.open('x',encoding='utf8')as f:json.dump(cfg,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(temp,cfgpath);report['current_RECURSOS_sha256']=sha(cfgpath)
 write_new_or_same(proof,report);print(json.dumps({k:v for k,v in report.items()if k!='previous_RECURSOS'},ensure_ascii=False,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
