"""Root-only post-import code/registry CAS. Never edits estado or runs Native."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,importlib.util,json,os,sqlite3
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0'
HELPER=P/'codigo/pi09_aritmetica_temporal_P0_R01.py';HSHA='ebff5dbe0d3b85000a33b7f789a72688e7c24c0151076558a01e32a803824656'
PROTO=P/'codigo/PROTOCOLO_PI09_ARITMETICA_TEMPORAL_P0_R02.json';SEAL=P/'control/SELLO_PANEL_DISCOVERY_P0_PI09_R01.json'
PAIR=P/'pares/NATIVE_POST12_T903603';PAIRSHA='0cce6bcfe366551b52b0ca25c5959bd6e07ed4493221ec26b76af962c13b6553'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def data(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def require(ok,message):
 if not ok:raise ValueError(message)
def unlinked(p):
 for x in(p,*p.parents):
  if x.exists():require(not x.is_symlink()and not(getattr(x.lstat(),'st_file_attributes',0)&1024),'Reparse/symlink refused')
def mapping(slug):
 require(slug in ('PANEL','DISCOVERY'),'Exact two closed diagnostic targets only')
 root=P/'estados'/slug;return root,root/'sistema','ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_'+slug+'_01'
def require_source():
 seal=read(SEAL);require(sha(HELPER)==HSHA and sha(PROTO)==seal['protocol']['sha256']and sha(PAIR/'EXPORTACION_SERVICIO.json')==PAIRSHA,'Sealed source changed')
 require(read(PROTO)['execution_enabled']is True,'Prepared protocol not bound');return seal
def propose(registry,manifest,context,preparation,protocol_sha,seal_sha):
 registry=copy.deepcopy(registry);manifest=copy.deepcopy(manifest);context=copy.deepcopy(context);preparation=copy.deepcopy(preparation)
 require(HELPER.stem not in registry['plugins'],'Already installed; do not overwrite/retry')
 registry['plugins'].append(HELPER.stem);registry['files_sha256'][HELPER.name]=HSHA;registry['files_sha256'][PROTO.name]=protocol_sha
 changed={'capacidades/'+HELPER.name:HELPER.read_bytes(),'capacidades/'+PROTO.name:PROTO.read_bytes(),'capacidades/PI09_PLUGINS_R02.json':data(registry)}
 table={r['file']:r for r in manifest['files']}
 for name,blob in changed.items():table[name]={'file':name,'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest()}
 manifest['files']=[table[n]for n in sorted(table)]
 manifest.setdefault('instrumentation_deltas',[]).append({'kind':'PI09_prepared_clock_access_P0','seal_sha256':seal_sha,'files':list(changed),'Native_inputs':0,'Native_ticks':0,'old_scientific_bodies_unchanged':True})
 mb=data(manifest);context['source_code_manifest_sha256']=hashlib.sha256(mb).hexdigest();context['post_import_P0_code_only']={'seal_sha256':seal_sha,'no_Native_or_state_edit':True}
 cb=data(context);preparation['context_sha256']=hashlib.sha256(cb).hexdigest();preparation['post_import_P0_code_only']=context['post_import_P0_code_only']
 return changed,{'SISTEMA_CODIGO_PI09.json':mb,'CONTEXTO_EJECUCION.json':cb,'PREPARACION_PI09.json':data(preparation)}
def state_guard(root,system,life):
 require(not(system/'estado/ACTIVO.json').exists(),'Selected systems forbidden')
 importproof=read(root/'IMPORTACION_PI09.json');require(importproof['closed']and importproof['error']is None and importproof['new_Native_ticks']==0 and importproof['source_pair_manifest_sha256']==PAIRSHA,'Full Root import must be closed0tick first')
 cardfile=system/'estado/vidas'/life/'VIDA.json';card=read(cardfile);mf=read(PAIR/'EXPORTACION_SERVICIO.json')
 require(card['life_id']==card['world_id']==life and card['physical']['tick']==903603 and card['parent']['source_tick']==903603,'Only the actual imported post12 before any use')
 require(all(card['physical'][k]==mf['physical'][k]for k in ('N','tick','RAW_sha256','clocks_sha256')),'Full physical prefix mismatch')
 snapshot=(system/card['snapshot']).resolve(strict=True);require(snapshot.is_relative_to(system.resolve())and sha(snapshot)==card['snapshot_sha256'],'Current coherent snapshot required')
 require(not(cardfile.parent/'FUTURO_INTERRUMPIDO.json').exists()and not(system/'estado/servicios_persistentes'/life/'IMPORTACION_EN_CURSO.json').exists(),'Incomplete future protected')
 locks=system/'estado/locks';require(not locks.exists()or not any(locks.iterdir()),'Target has a writer lock')
 db=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
 require(all(not Path(str(db)+suffix).exists()or Path(str(db)+suffix).stat().st_size==0 for suffix in ('-wal','-journal')),'Live SQLite auxiliary refused')
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0]);statuses=dict(con.execute('SELECT status,COUNT(*) FROM requests GROUP BY status'))
  require(not owner.get('running')and not any(statuses.get(k,0)for k in ('queued','processing','uncertain')),'Target transport not closed')
 finally:con.close()
 return {str(p):sha(p)for p in (cardfile,snapshot,db,cardfile.parent/'HISTORIA.jsonl')}
def main(a):
 seal=require_source();root,system,life=mapping(a.slug)
 if not a.aplicar:
  print(json.dumps({'mode':'PLAN_ONLY_NO_NATIVE','target':str(system),'life_id':life,'target_exists':system.exists(),'requires':'Completed clonar_post12 import0 before --aplicar','writes':['two new code/protocol files','registry','three code/context descriptors','P9 beforeimages+proof'],'estado_writes':0,'Native':0},ensure_ascii=False));return
 require(not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists()and not(C/'reproducibilidad/EJECUCION_MATERIAL.lock').exists(),'Writer/importer still declared')
 for x in(root,system):unlinked(x);require(x.is_dir(),'Post12 clone missing')
 state_before=state_guard(root,system,life)
 mfpath=root/'SISTEMA_CODIGO_PI09.json';contextpath=root/'CONTEXTO_EJECUCION.json';preppath=root/'PREPARACION_PI09.json';regpath=system/'capacidades/PI09_PLUGINS_R02.json'
 manifest=read(mfpath)
 for row in manifest['files']:
  path=(system/row['file']).resolve(strict=True);require(path.is_relative_to(system.resolve())and not row['file'].startswith(('estado/','runtime/'))and sha(path)==row['sha256'],'Closed code manifest mismatch')
 require(read(preppath)['context_sha256']==sha(contextpath)and read(contextpath)['source_code_manifest_sha256']==sha(mfpath),'Context/code/preparation CAS disagreement')
 changed,descriptors=propose(read(regpath),manifest,read(contextpath),read(preppath),sha(PROTO),sha(SEAL))
 require(not(system/'capacidades'/HELPER.name).exists()and not(system/'capacidades'/PROTO.name).exists(),'Unregistered P0 files already present; preserve and inspect')
 require(hashlib.sha256(changed['capacidades/PI09_PLUGINS_R02.json']).hexdigest()==seal['expected_installed_registry_sha256'],'Registry differs from pre-Native seal')
 writes={system/name:blob for name,blob in changed.items()};writes.update({root/name:blob for name,blob in descriptors.items()})
 require(all(not p.is_relative_to(system/'estado')and p.is_relative_to(root)for p in writes),'No estado/source/main write permitted')
 before={str(p):sha(p)if p.exists()else None for p in writes};backup=P/'control'/('P0_POST12_'+a.slug+'_R01_ANTES');require(not backup.exists(),'Beforeimages already exist; inspect previous attempt')
 backup.mkdir()
 for p in writes:
  if p.exists():
   dest=backup/p.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True)
   with dest.open('xb')as f:f.write(p.read_bytes())
 for p,blob in writes.items():
  require((sha(p)if p.exists()else None)==before[str(p)],'Concurrent code/context change; preserve beforeimages')
  temp=p.with_name(p.name+'.PI09_P0_NEW');require(not temp.exists(),'Unresolved previous code-stage file')
  with temp.open('xb')as f:f.write(blob)
  os.replace(temp,p)
 require(state_before=={path:sha(Path(path))for path in state_before},'State unexpectedly changed; stop without rollback/retry')
 report={'schema':'DEE.PI09.P0.post12_code_only_CAS_install.R01','slug':a.slug,'life_id':life,'actual_applied':True,'recorded_utc':datetime.now(timezone.utc).isoformat(),'protocol_sha256':sha(PROTO),'seal_sha256':sha(SEAL),'beforeimages':str(backup),'changes':[{'file':str(p),'before_sha256':before[str(p)],'after_sha256':sha(p),'bytes':p.stat().st_size}for p in writes],'state_hashes_before':state_before,'state_hashes_after':{path:sha(Path(path))for path in state_before},'Native_inputs':0,'Native_ticks':0,'selected_or_promoted':False}
 proof=P/'control'/('INSTALACION_P0_POST12_'+a.slug+'_R01.json')
 with proof.open('x',encoding='utf8')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(proof),'sha256':sha(proof),'applied':True,'Native':0}))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--slug',choices=('PANEL','DISCOVERY'),required=True);parser.add_argument('--aplicar',action='store_true');main(parser.parse_args())
