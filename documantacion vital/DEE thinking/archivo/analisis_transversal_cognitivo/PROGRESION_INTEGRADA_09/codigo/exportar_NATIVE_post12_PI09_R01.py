"""Root-only future paired preservation after the actual canonical12 closes.

Prepared while the source owner may be running: default only prints a plan.
--exportar reads source state only AFTER Root supplies its actual closed proof,
exact tick and encoded snapshot SHA. No Native import or source/state writes.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,shutil,sqlite3
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/NATIVE/sistema';RP=C/'reproducibilidad'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01';KEY='DEE.Cognitive.PI09.selective_registered_consultation.R02'
CKEY='DEE.Cognitive.PI08.conditional_sensor_register_access.C.R02';BKEY='DEE.Cognitive.PI08.successive_contextual_regulation.B.R01';SERVICE='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'
SOURCE_C=P/'pares/C_HEREDADA_T884835';C_SHA='08a8e65deb2071b7653bc0ab95f3d55b8038191a4f585c6803f6d81c16e8182f'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def require(ok,msg):
 if not ok:raise ValueError(msg)
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def protected_A():
 active=C/'sistema/estado/ACTIVO.json';card=C/'sistema/estado/vidas'/read(active)['life_id']/'VIDA.json';r=read(card)
 return {str(p):sha(p)for p in(active,card,C/'sistema'/r['snapshot'])}
def main():
 p=argparse.ArgumentParser();p.add_argument('--exportar',action='store_true');p.add_argument('--tick',type=int);p.add_argument('--snapshot-sha256');p.add_argument('--closed-proof',type=Path);a=p.parse_args()
 if not a.exportar:
  print(json.dumps({'mode':'PLAN_ONLY_NO_SOURCE_STATE_READ','source_system':str(S),'life_id':LIFE,'required_progress':'PI09R02native_real12; originalC6/B30literal','destination':'P9/pares/NATIVE_POST12_T<ACTUAL_CLOSED_TICK>','requires':['--exportar','--tick ACTUAL','--snapshot-sha256 ACTUAL','--closed-proof ACTUAL_CLOSED_JSON'],'Native_executed':False},ensure_ascii=False,indent=2));return
 require(a.tick and a.tick>884835 and a.snapshot_sha256 and len(a.snapshot_sha256)==64 and a.closed_proof,'Root debe fijar el corte y cierre reales')
 proof_file=a.closed_proof.resolve(strict=True);require(proof_file.parent==(P/'control').resolve(),'Comprobante dentro del controlPI09')
 closed=read(proof_file);require(closed['closed']is True and closed.get('error')is None and closed['life_id']==LIFE and closed['final_tick']==a.tick,'Cierre actual del Native canonical requerido')
 require(not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists(),'No se exporta mientras el writer/importador permanezca declarado')
 dest=P/'pares'/('NATIVE_POST12_T'+str(a.tick));report=dest.with_name(dest.name+'_PRESERVACION.json');require(not dest.exists()and not report.exists(),'Destino ya existe; no se sobrescribe')
 old=load('PI09_reuse_closed_export_helpers',P/'codigo/exportar_C_heredada_PI09_R01.py');legacy=old.load(old.LEGACY,'PI09_known_precommit_failure',old.LEGACY_SHA)
 parser=old.load(old.PARSER,'PI09_actual_passive_parser',old.PARSER_SHA)
 life=S/'estado/vidas'/LIFE;service=S/'estado/servicios_persistentes'/LIFE;worker=S/'estado/servicios_locales'/LIFE
 for root in(S,life,service,worker):old.regular(root);require(root.is_dir(),'Falta estado completo')
 require(not(S/'estado/ACTIVO.json').exists()and not(life/'FUTURO_INTERRUMPIDO.json').exists()and not(service/'IMPORTACION_EN_CURSO.json').exists(),'Fuente seleccionada/interrumpida/parcial')
 cardfile=life/'VIDA.json';history=life/'HISTORIA.jsonl';card=read(cardfile);snapshot=(S/card['snapshot']).resolve(strict=True)
 require(snapshot.is_relative_to(S)and card['life_id']==card['world_id']==LIFE and card['physical']['tick']==a.tick and card['snapshot_sha256']==sha(snapshot)==a.snapshot_sha256,'Puntero/tick/snapshot ya no son el cierre suministrado')
 require(not(S/'estado/locks'/(card['world_id']+'.lock')).exists(),'Writer lock de la fuente presente')
 require(json.loads(history.read_text('utf8').splitlines()[-1])['snapshot_sha256']==a.snapshot_sha256,'Historia y puntero no concuerdan')
 view=parser.snapshot_view(snapshot);original=parser.snapshot_view(SOURCE_C/'VIDA.deetsnap.gz')
 require(sha(SOURCE_C/'EXPORTACION_SERVICIO.json')==C_SHA,'Antecedente C cambió')
 for key in(CKEY,BKEY):require(view['metadata'][key]==original['metadata'][key],'Se editó el antecedente histórico '+key)
 meta=json.loads(view['metadata'][KEY]);require(meta['ordinal']==12 and meta['control']['arm']=='native_real'and meta.get('ready')and not meta.get('pending')and not meta.get('uncertain'),'No es el estado completo canonical12')
 require(all(view['physical'][k]==card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')),'Física de ficha y snapshot distinta')
 native=json.loads(view['metadata'][SERVICE]);require(native['native_tick_at_checkpoint']==a.tick and native['paused']and not native['uncertain_external_result'],'Protocolo de owner no pausado/coherente')
 db=service/'cola.sqlite3';aux={x:Path(str(db)+x).stat().st_size if Path(str(db)+x).exists()else 0 for x in('-wal','-shm','-journal')};require(not aux['-wal']and not aux['-journal'],'SQLite con WAL/journal no vacío')
 con=sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True);con.row_factory=sqlite3.Row
 try:
  require(con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite no íntegra')
  owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0]);counts=dict(con.execute('SELECT status,COUNT(*) FROM requests GROUP BY status'))
  require(owner.get('running')is False and owner['tick']==a.tick and not owner.get('uncertain_external_result')and not any(counts.get(k,0)for k in('queued','processing','uncertain')),'Transporte pendiente/ambiguo')
  expected_failure=legacy.verify_declared_precommit_failure(con,service);process=old.scoped_pid(owner['pid'],owner['wall_utc'])
  receipt=native['last_completed_receipt'];row=con.execute('SELECT * FROM requests WHERE id=?',(receipt['id'],)).fetchone();outbox=service/'resultados'/(receipt['id']+'.json')
  require(row and row['status']=='completed'and row['payload_sha']==receipt['payload_sha256']and outbox.is_file()and sha(outbox)==receipt['result_sha256'],'Último recibo/outbox no conciliado')
 finally:con.close()
 sources=[(snapshot,Path('VIDA.deetsnap.gz')),(db,Path('cola.sqlite3')),(cardfile,Path('procedencia/VIDA_ORIGINAL.json')),(history,Path('procedencia/HISTORIA_ORIGINAL.jsonl'))];directories=[]
 for root,prefix in((service/'resultados',Path('resultados')),(worker,Path('artefactos_trabajador'))):
  files,dirs=legacy.tree(root);sources.extend((f,prefix/r)for f,r in files);directories.extend((prefix/Path(d)).as_posix()for d in dirs)
 before={str(f):{'bytes':f.stat().st_size,'sha256':sha(f)}for f,_ in sources};A_before=protected_A();dest.mkdir(parents=True)
 for name in directories:(dest/name).mkdir(parents=True,exist_ok=True)
 rows=[]
 for source,name in sources:
  target=dest/name;target.parent.mkdir(parents=True,exist_ok=True)
  with source.open('rb')as src,target.open('xb')as dst:shutil.copyfileobj(src,dst)
  require(sha(target)==before[str(source)]['sha256'],'Copia parcial no íntegra; conservar destino')
  rows.append({'file':name.as_posix(),**before[str(source)]})
 require(before=={str(f):{'bytes':f.stat().st_size,'sha256':sha(f)}for f,_ in sources}and A_before==protected_A(),'Cambio concurrente de fuente o A')
 manifest={'schema':'DEE.persistent_service.paired_export.v1','life_id':LIFE,'profile':card['profile'],'backend':'mente_unificada','native_snapshot':'VIDA.deetsnap.gz','snapshot_sha256':a.snapshot_sha256,'physical':card['physical'],'members':rows,'queue_journal_required':True,'source_record':{'life_id':LIFE,'world_id':card['world_id'],'parent':card.get('parent')},'empty_directories_preserved':sorted(set(directories)),'expected_preserved_terminal_failure':expected_failure,'pending_Native_agenda_preserved':view['pending_native'],'no_engine_or_WHL':True,'not_a_new_cognitive_acquisition':True,'PI09_actual_progress':{'ordinal':12,'role':'native_real','protocol_sha256':meta['protocol_sha256']}}
 mf=dest/'EXPORTACION_SERVICIO.json';mf.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
 proof={'schema':'DEE.PI09.native_post12.full_closed_preservation.R01','life_id':LIFE,'tick':a.tick,'destination':str(dest),'manifest_sha256':sha(mf),'snapshot_sha256':a.snapshot_sha256,'members':len(rows),'bytes':sum(x['bytes']for x in rows),'directories':len(manifest['empty_directories_preserved']),'process_proof':process,'queue_status_counts':counts,'SQLite_auxiliaries':aux,'closed_proof':{'path':str(proof_file),'sha256':sha(proof_file)},'causal_prefix_sha256':view['causal_prefix_sha256'],'old_C_B_metadata_literal':True,'source_files_unchanged':True,'A_unchanged':True,'Native_executed':False,'new_native_ticks':0,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 report.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'exported':True,'manifest':str(mf),'manifest_sha256':sha(mf),'proof':str(report),'Native_executed':False},ensure_ascii=False))
if __name__=='__main__':main()
