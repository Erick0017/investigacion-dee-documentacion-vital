"""Closed actual RP12 vs immutable canonical prefix; stdlib, no Native.

Reports all metadata differences. Only SYSTEM/SERVICE transport and PI09's
current life/log hash are permitted, with byte-derived journal verification.
No broad exclusion of the scientific/environmental PI09 metadata object.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sqlite3
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0'
PAIR=P/'pares/NATIVE_POST12_T903603';PAIR_SHA='0cce6bcfe366551b52b0ca25c5959bd6e07ed4493221ec26b76af962c13b6553';NATIVE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01';REPRO='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_RPF_20261111A'
KEY='DEE.Cognitive.PI09.selective_registered_consultation.R02';FOLDER='PI09_CONSULTA_SELECTIVA_R02';SYSTEM='DEE.Cognitive.System.1.1.life.v1';SERVICE='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,msg):
 if not ok:raise ValueError(msg)
def normalize(v):
 if isinstance(v,dict):return {k:normalize(x)for k,x in v.items()}
 if isinstance(v,list):return [normalize(x)for x in v]
 return '__CURRENT_TRANSPORT_LIFE__'if isinstance(v,str)and v in(NATIVE,REPRO)else v
def differences(a,b,path=''):
 if type(a)is not type(b):return [path]
 if isinstance(a,dict):
  out=[]
  for key in sorted(set(a)|set(b)):out.extend([path+'/'+str(key)]if key not in a or key not in b else differences(a[key],b[key],path+'/'+str(key)))
  return out
 if isinstance(a,list):
  if len(a)!=len(b):return [path+'/length']
  return [p for i,(x,y)in enumerate(zip(a,b))for p in differences(x,y,path+'/'+str(i))]
 return []if a==b else[path]
def journal(file,meta):
 data=file.read_bytes();chain='00'*32;rows=[]
 for line in data.splitlines(keepends=True):rows.append(json.loads(line));chain=hashlib.sha256(bytes.fromhex(chain)+line).hexdigest()
 require(len(rows)==meta['log_count']and chain==meta['log_chain_sha256'],'El diario no corresponde al checkpoint')
 return rows,{'path':str(file),'sha256':sha(file),'rows':len(rows),'chain':chain}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--destino-replay',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
 dest=a.destino_replay.resolve(strict=True);out=a.salida.resolve();require(out.is_relative_to((P/'control').resolve())and not out.exists(),'Comprobante nuevo sólo bajo control PI09')
 result=read(dest/'RESULTADO_REPRODUCCION.json');require(result.get('status')=='COMPLETED'and result.get('owner_closed_coherently')is True and result.get('life')==REPRO,'Se requiere el cierre real de la reproducción REPRO exacta')
 context=read(dest/'CONTEXTO_EJECUCION.json');require(context['life']==REPRO and context['recipe']=='pi09_consulta_native12_familia_desde_C_R04'and context['prefix_manifest_sha256']=='08a8e65deb2071b7653bc0ab95f3d55b8038191a4f585c6803f6d81c16e8182f','Receta o prefijo de reproducción distinto')
 system=dest/'sistema';require(not(system/'estado/ACTIVO.json').exists(),'No se contrasta un principal seleccionado')
 capsule=C/'reproducibilidad/codigo_preservado/PI09_CONSULTA_R02_FAMILIA_R04';cm=read(capsule/'SISTEMA_CODIGO.json')
 require(sha(capsule/'SISTEMA_CODIGO.json')==context['source_code_manifest_sha256'] and context['source_code_capsule_key']=='PI09_CONSULTA_R02_FAMILIA_R04','Cápsula familiar distinta')
 bindingfile=dest/'VINCULO_FAMILIA_DIAGNOSTICA_PI09_R01.json';binding=read(bindingfile)
 expectedbinding={'recipe':context['recipe'],'exact_life_id':REPRO,'full_C_manifest_sha256':context['prefix_manifest_sha256'],'capsule_manifest_sha256':context['source_code_manifest_sha256'],'Native_inputs_changed':False,'Native_state_created_yet':False,'not_learning_or_new_principal':True}
 require(binding['schema']=='DEE.PI09.explicit_diagnostic_family.bound_before_native.v1'and all(binding.get(k)==v for k,v in expectedbinding.items())and binding.get('new_native_ticks')==binding.get('new_native_inputs')==0,'Vínculo administrativo anterior a Native inválido')
 changed={'capacidades/PI09_REPRODUCCION_FAMILIA_R01.json','capacidades/PI09_TRANSPORTE_HEREDADO_R02.json'}
 for item in cm['files']:
  current=system/item['file'];original=capsule/item['file']
  require(sha(original)==item['sha256'],'Cambió la cápsula estable')
  if item['file']not in changed:require(sha(current)==item['sha256'],'Otro código de clon cambió: '+item['file']);continue
  expected=read(original)
  if item['file'].endswith('PI09_REPRODUCCION_FAMILIA_R01.json'):expected['bound_life_id']=REPRO;expected['administrative_binding']=expectedbinding
  else:expected['life_id']=REPRO;expected['diagnostic_family_binding']=expectedbinding
  require(read(current)==expected and binding['files_before'].get(str(current))==item['sha256']and binding['files_after'].get(str(current))==sha(current),'Cambió algo distinto de la identidad administrativa declarada')
 card=read(system/'estado/vidas'/REPRO/'VIDA.json');require(card['physical']['tick']==903603 and sha(system/card['snapshot'])==card['snapshot_sha256'],'La reproducción no está en el corte903603')
 db=system/'estado/servicios_persistentes'/REPRO/'cola.sqlite3'
 require(not any(Path(str(db)+s).exists()and Path(str(db)+s).stat().st_size for s in('-wal','-journal')),'SQLite sigue con un journal material')
 require(not(system/'estado/locks'/(REPRO+'.lock')).exists(),'El owner aún conserva su lock')
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  require(con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite no íntegra');owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0]);require(owner.get('running')is False and not con.execute("SELECT COUNT(*)FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0],'Transporte no cerrado')
 finally:con.close()
 require(sha(PAIR/'EXPORTACION_SERVICIO.json')==PAIR_SHA,'Cambió el prefijo canonical cerrado')
 mf=read(PAIR/'EXPORTACION_SERVICIO.json');require(sha(PAIR/'VIDA.deetsnap.gz')==mf['snapshot_sha256'],'Snapshot canonical alterado')
 spec=importlib.util.spec_from_file_location('PI09_passive_comparison',C/'reproducibilidad/observador_pasivo.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
 source=parser.snapshot_view(PAIR/'VIDA.deetsnap.gz');target=parser.snapshot_view(system/card['snapshot']);changes=[];unexpected=[]
 for key in sorted(set(source['metadata'])|set(target['metadata'])):
  x=source['metadata'].get(key);y=target['metadata'].get(key)
  if x==y:continue
  row={'key':key,'source_sha256':None if x is None else hashlib.sha256(x.encode()).hexdigest(),'replay_sha256':None if y is None else hashlib.sha256(y.encode()).hexdigest()}
  if key==SYSTEM or key==SERVICE or key.startswith(SERVICE+'.queue.'):
   row['scope']='Explicit existing current-life/persistent-service/queue transport; listed, not Native memory'
  elif key==KEY and x is not None and y is not None:
   paths=differences(json.loads(x),json.loads(y));row['changed_paths']=paths
   if set(paths)-{'/life_id','/log_chain_sha256'}:unexpected.append(key)
   else:row['scope']='Exact current transport ID plus own journal hash only; all other PI09 fields compared literally'
  else:unexpected.append(key)
  changes.append(row)
 sx=json.loads(source['metadata'][KEY]);tx=json.loads(target['metadata'][KEY]);require(sx['ordinal']==tx['ordinal']==12,'Ambos prefijos deben conservar12 oportunidades')
 sj,si=journal(PAIR/'artefactos_trabajador'/FOLDER/'eventos.jsonl',sx);tj,ti=journal(system/'estado/servicios_locales'/REPRO/FOLDER/'eventos.jsonl',tx)
 journal_changes=differences(normalize(sj),normalize(tj));physical=source['physical']==target['physical'];causal=source['causal_prefix_sha256']==target['causal_prefix_sha256']
 if journal_changes:unexpected.append(KEY+'.journal.normalized_identity_only')
 proof={'schema':'DEE.PI09.RP.family_canonical12.full_passive_comparison.R04','physical_equal':physical,'causal_prefix_equal':causal,'source_physical':source['physical'],'replay_physical':target['physical'],'source_causal_prefix_sha256':source['causal_prefix_sha256'],'replay_causal_prefix_sha256':target['causal_prefix_sha256'],'unexpected_metadata_changes':unexpected,'metadata_changes_all_listed':changes,'PI09_journals':{'source':si,'replay':ti,'only_exact_current_identity_values_normalized':True,'normalized_equal':not journal_changes,'other_different_paths':journal_changes},'recipe_actual_criteria_met':result.get('criteria_met'),'overall':physical and causal and not unexpected and result.get('criteria_met')is True,'Native_executed':False,'DEE_imports':0,'new_ticks':0,'source_pair_manifest_sha256':PAIR_SHA,'family_binding':{'path':str(bindingfile),'sha256':sha(bindingfile),'only_two_administrative_code_bindings_verified':True},'replay_result':{'path':str(dest/'RESULTADO_REPRODUCCION.json'),'sha256':sha(dest/'RESULTADO_REPRODUCCION.json')},'preserve_failure_without_relaxation':True}
 out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(out),'sha256':sha(out),'overall':proof['overall'],'unexpected_metadata_changes':unexpected,'Native_executed':False}));return 0 if proof['overall']else 2
if __name__=='__main__':raise SystemExit(main())
