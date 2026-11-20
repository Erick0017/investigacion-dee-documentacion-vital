"""Root-only final current-pointer/document CAS; no world or SQLite writes.

VIDA/ACTIVO and their actual snapshot are authoritative. Historical adoption
cuts and every entry's validated_lives remain literal. Only five descriptive
JSONs are written; ACTIVO, cards, snapshots, code and queues are protected.
Publication is a separate actual proof; a target edition is never publication.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,importlib.util,json,os,sqlite3
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad';LIVES={'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01','ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'}
TARGETS=('PROYECTO.json','CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json')
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def regular(p):
 for node in(p,*p.parents):need(not node.exists()or not(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&1024),'No linked/reparse final metadata target')
def put(p,value):
 regular(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def writer_proof(path,life):
 p=read(path);age=(datetime.now(timezone.utc)-datetime.fromisoformat(p['recorded_utc'])).total_seconds();need(0<=age<=600 and(p.get('no_live_affected_writers')is True or p.get('all_scoped_Native_writers_closed')is True),'Fresh actual scoped all-closed proof required (600s)')
 need(life in p.get('affected_life_ids',[])or any(r.get('life_id')==life for r in p.get('evidence',[])),'Actual current main must be in the closed process scope')
 return ref(path)
def current():
 need(not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'No final synchronization while Root/RP writer remains')
 activefile=S/'estado/ACTIVO.json';active=read(activefile);life=active['life_id'];need(life in LIVES,'Only the two exact adopted PI09 candidate IDs')
 cardfile=S/'estado/vidas'/life/'VIDA.json';card=read(cardfile);snapshot=(S/card['snapshot']).resolve(strict=True);need(snapshot.is_relative_to((S/'estado').resolve())and sha(snapshot)==card['snapshot_sha256'],'Current saved snapshot binding differs')
 need(card['world_id']==life and card['profile']=='fisica_directa'and card['physical']['N']==67 and active.get('snapshot_sha256')==card['snapshot_sha256']and active.get('tick')==card['physical']['tick'],'ACTIVO/current card disagree; no metadata-only repair of a physical mismatch')
 need(not(S/'estado/locks'/(life+'.lock')).exists()and not(cardfile.parent/'FUTURO_INTERRUMPIDO.json').exists(),'Current owner/interrupted future remains fenced')
 db=S/'estado/servicios_persistentes'/life/'cola.sqlite3';need(not any(Path(str(db)+v).exists()and Path(str(db)+v).stat().st_size for v in('-wal','-journal')),'Current standalone queue must be closed')
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  need(con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','Current queue integrity failure');row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();owner=json.loads(row[0])if row else{};need(owner.get('running')is False and not con.execute("SELECT COUNT(*)FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0],'Current owner/queue is not closed and reconciled')
 finally:con.close()
 parserfile=RP/'observador_pasivo.py';spec=importlib.util.spec_from_file_location('PI09_final_passive_snapshot',parserfile);parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser);view=parser.snapshot_view(snapshot);need(all(view['physical'][k]==card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')),'Actual snapshot physical prefix differs from its card')
 protected={str(p):sha(p)for p in(activefile,cardfile,snapshot,db)}
 for ancestor in('ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01','ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'):
  old=S/'estado/vidas'/ancestor/'VIDA.json'
  if old.exists():r=read(old);protected[str(old)]=sha(old);protected[str(S/r['snapshot'])]=sha(S/r['snapshot'])
 resources={}
 for label,key,total in(('PI09_R02','DEE.Cognitive.PI09.selective_registered_consultation.R02',18),('D','DEE.Cognitive.PI09.persistent_environment.D.R02',12),('FI8','DEE.Cognitive.PI09.explicit_FI_eight_offer_lot.R01',8),('FI_prior','DEE.Cognitive.PI07.regulated_FI_access.R01',8),('C2C','DEE.Cognitive.PI04.C2C.coordination.R01',32)):
  if key not in view['metadata']:continue
  value=json.loads(view['metadata'][key]);ordinal=value.get('ordinal')
  if type(ordinal)is not int:continue
  resources[label]={'ordinal':ordinal,'total_declared':total,'remaining':total-ordinal,'access':'historical_readonly'if life.endswith('DISCOVERY_01')and label in('PI09_R02','FI_prior')else'current_declared_finite_stock','supply_or_stock_is_not_Native_energy_or_learning':True}
 return life,active,card,cardfile,snapshot,protected,resources
def publication(path):
 p=read(path);need(p.get('schema')=='DEE.PI09.actual_complete_DOCX_publication.R01'and p.get('internal_edition')in('1.37','1.38')and len(p.get('rows',[]))==2,'Actual PI09 complete publication proof required')
 rows=[]
 for row in p['rows']:
  file=Path(row['source']).resolve(strict=True);need(file.suffix=='.docx'and sha(file)==row['published_sha256']and file.stat().st_size==row['bytes'],'Current literal published DOCX differs')
  rows.append({'path':str(file),'bytes':file.stat().st_size,'sha256':sha(file),'internal_edition':p['internal_edition'],'publication_witness':ref(path),'visual_validation':p.get('visual_validation')is True,'visual_status':p.get('visual_status','NOT_VERIFIED')})
 manual=next(r for r in rows if Path(r['path']).is_relative_to(C.resolve()));comp=next(r for r in rows if r is not manual);return manual,comp
def prepare(a):
 life,active,card,cardfile,snapshot,protected,resources=current();factsfile=a.facts.resolve(strict=True);facts=read(factsfile);need(factsfile.is_relative_to((P/'control').resolve()),'Actual final facts under P9/control');wp=writer_proof(a.writers_proof.resolve(strict=True),life)
 need(facts.get('closed')is True or facts.get('all_scoped_Native_writers_closed')is True,'Actual final facts must be closed; not an open documentary draft')
 out=a.destino.resolve();need(out.is_relative_to(H.resolve())and not out.exists(),'New final CAS proposal under codigo');out.mkdir();values={rel:read(C/rel)for rel in TARGETS};before={rel:sha(C/rel)for rel in TARGETS};catalog_validated=copy.deepcopy([{'id':e.get('id'),'validated_lives':e.get('validated_lives')}for e in values[TARGETS[4]].get('entries',[])])
 stamp=datetime.now(timezone.utc).isoformat();snap={'path_relative_to_product':'sistema/'+card['snapshot'],'sha256':card['snapshot_sha256']};info={'life_id':life,'world_id':card['world_id'],'profile':card['profile'],'physical':card['physical'],'snapshot':snap,'identity_card':{'path_relative_to_product':TARGETS[2].split('/estado/genesis/')[0]+'/estado/vidas/'+life+'/VIDA.json','sha256':sha(cardfile)},'recorded_utc':stamp,'authority':'Actual closed current VIDA/ACTIVO and parsed saved snapshot, not an intermediate Source/adoption cut','final_facts':ref(factsfile),'closed_writer_scope':wp,'finite_resources_at_actual_current_snapshot':resources}
 for rel,value in values.items():value.setdefault('PI09_final_sync_prior_current',{'recorded_utc':stamp,'current_binding_before_sync':{k:copy.deepcopy(value.get(k))for k in('selected_life','latest_saved_tick','operational_current_cut','operational_current_snapshot','current_operational_snapshot','current_operational_identity_card_sha256','physical_cut','latest_snapshot','current_principal','manual_current','manual_internal_edition','manual_current_sha256')}})
 project=values[TARGETS[0]];project.update(selected_life=life,latest_saved_tick=card['physical']['tick'],operational_current_cut=card['physical'],operational_current_snapshot=snap,current_operational_snapshot=snap,current_operational_identity_card_sha256=sha(cardfile),PI09_latest_closed_current=info)
 continuity=values[TARGETS[1]];continuity.update(life_id=life,world_id=card['world_id'],profile=card['profile'],physical_cut=card['physical'],latest_snapshot=snap,identity_card=info['identity_card'],PI09_latest_closed_current=info,updated_utc=stamp)
 personal=values[TARGETS[2]];need(personal.get('life_id')==life,'Personal selection does not identify the actual selected main');personal.update(current_saved_tick=card['physical']['tick'],current_saved_snapshot_sha256=card['snapshot_sha256'],current_identity_card_sha256=sha(cardfile),PI09_final_closed_cut=info)
 seed=values[TARGETS[3]];need(seed.get('source_life')==life or seed.get('source_alias')==life,'Launcher seed does not select the existing actual main');seed.update(current_operational_snapshot_sha256=card['snapshot_sha256'],current_operational_tick=card['physical']['tick'],current_operational_world_id=card['world_id'],existing_continuation_only=True,PI09_final_closed_cut=info)
 catalog=values[TARGETS[4]];principal=catalog.get('current_principal');need(isinstance(principal,dict)and principal.get('life_id')==life,'Catalog current principal differs; no implicit selection by metadata');principal.update(tick=card['physical']['tick'],N=67,snapshot_sha256=card['snapshot_sha256'],world_id=card['world_id'],latest_closed_current=info,updated_utc=stamp);catalog['PI09_latest_closed_current']=info
 if a.use_proof:
  use=a.use_proof.resolve(strict=True);need(use.is_relative_to(P.resolve()),'Actual selected use proof under P9');u=read(use);need(u.get('life_id')==life and(u.get('closed')is True or u.get('owner_closed')is True),'Actual selected use must be closed and correctly bound');project['latest_selected_use']=ref(use);continuity['latest_operational_use']=ref(use);principal['latest_actual_selected_use']=ref(use);project['selected_operational_use_pending']=False
 for entry in catalog.get('entries',[]):
  if any(v.get('life_id')==life for v in entry.get('validated_lives',[])if isinstance(v,dict)):
   entry['PI09_latest_available_state']=info;entry['PI09_final_evidence']=ref(factsfile)
 if a.publication:
  manual,comp=publication(a.publication.resolve(strict=True));project.update(manual_current=Path(manual['path']).name,manual_internal_edition=manual['internal_edition'],manual_current_sha256=manual['sha256'],manual_current_bytes=manual['bytes'],manual_publication_witness=str(a.publication.resolve()),compendium_current=comp)
  for value in(continuity,catalog):value['manual_current']=manual;value['compendium_current']=comp
 else:
  for value in(project,continuity,catalog):value['PI09_documentation_status']={'target_edition':'1.38','publication_confirmed_by_this_sync':False,'current_document_descriptors_preserved':True}
 need(catalog_validated==[{'id':e.get('id'),'validated_lives':e.get('validated_lives')}for e in catalog.get('entries',[])],'Validated lives/cuts must never be rewritten by final availability sync')
 for rel,value in values.items():put(out/'propuestos'/rel,value);target=out/'originales'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((C/rel).read_bytes())
 plan={'schema':'DEE.PI09.final_current_metadata.CAS_plan.R02','Native_executed':False,'SQL_writes':False,'world_state_writes':False,'facts':ref(factsfile),'writer_scope':wp,'actual_current':info,'targets':[{'file':rel,'before_sha256':before[rel],'after_sha256':sha(out/'propuestos'/rel)}for rel in TARGETS],'protected_unchanged':protected,'adoption_cuts_and_validated_lives_preserved':True,'ACTIVO_not_written':True,'publication':ref(a.publication.resolve())if a.publication else None,'applied':False};put(out/'PLAN.json',plan);return out/'PLAN.json'
def apply(file):
 plan=read(file);need(plan['schema']=='DEE.PI09.final_current_metadata.CAS_plan.R02','Exact reviewed final CAS plan');wp=writer_proof(Path(plan['writer_scope']['path']),plan['actual_current']['life_id']);need(wp==plan['writer_scope'],'Closed writer scope changed');need(all(sha(Path(p))==digest for p,digest in plan['protected_unchanged'].items()),'Actual current physical/card/queue/ACTIVO changed')
 for row in plan['targets']:need(row['file']in TARGETS and sha(C/row['file'])==row['before_sha256']and sha(file.parent/'propuestos'/row['file'])==row['after_sha256'],'Current metadata or proposal changed')
 for refx in(plan['facts'],plan['publication']):
  if refx:need(sha(Path(refx['path']))==refx['sha256'],'Final facts/publication changed')
 output=P/'control/SINCRONIZACION_FINAL_ACTUAL_PI09_R02.json';need(not output.exists(),'Final synchronization already recorded or partial future preserved')
 for row in plan['targets']:
  target=C/row['file'];temporary=target.with_name(target.name+'.PI09_FINAL_WRITING');need(not temporary.exists(),'Prior partial write preserved')
  with temporary.open('xb')as f:f.write((file.parent/'propuestos'/row['file']).read_bytes());f.flush();os.fsync(f.fileno())
  os.replace(temporary,target)
 need(all(sha(Path(p))==digest for p,digest in plan['protected_unchanged'].items()),'Protected state changed during descriptive sync');put(output,{**plan,'schema':'DEE.PI09.final_current_metadata.applied.R02','applied':True,'at':datetime.now(timezone.utc).isoformat(),'plan':ref(file)});print(json.dumps({'proof':str(output),'sha256':sha(output),'life_id':plan['actual_current']['life_id'],'tick':plan['actual_current']['physical']['tick'],'Native_executed':False,'ACTIVO_unchanged':True}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--preparar',action='store_true');ap.add_argument('--aplicar',type=Path);ap.add_argument('--facts',type=Path);ap.add_argument('--writers-proof',type=Path);ap.add_argument('--publication',type=Path);ap.add_argument('--use-proof',type=Path);ap.add_argument('--destino',type=Path,default=H/'SINCRONIZACION_FINAL_PI09_R02');a=ap.parse_args()
 if a.aplicar:apply(a.aplicar.resolve(strict=True))
 elif a.preparar:
  need(a.facts is not None and a.writers_proof is not None,'Explicit final facts and fresh scoped writer proof required');f=prepare(a);print(json.dumps({'plan':str(f),'sha256':sha(f),'product_writes':False,'Native_executed':False}))
 else:print(json.dumps({'mode':'PLAN_ONLY_NO_STATE_READ','targets':list(TARGETS),'allowed_main_ids':sorted(LIVES),'publication_required_for_document_update':True,'Native_executed':False,'ACTIVO_written':False}))
