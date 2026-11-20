"""Root-only CAS refresh of five descriptive JSONs after a real selected use.
ACTIVO/VIDA/snapshot/contract/source-code remain untouched; adoption and panel
cuts remain historical. Default is a plan, never Native or product writes.
"""
from pathlib import Path
import argparse,copy,datetime,hashlib,json,os,sqlite3
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
FILES=('PROYECTO.json','CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json')
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
 for node in(p,*p.parents):
  if node.exists()and(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&0x400):raise ValueError('No linked current-cut reference')
def proposed_updates(values,card,closure,witness):
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();result=copy.deepcopy(values);project,continuity,personal,config,catalog=[result[name]for name in FILES];physical=copy.deepcopy(card['physical']);snapshot={'path_relative_to_product':'sistema/'+card['snapshot'],'sha256':card['snapshot_sha256']}
 project.setdefault('PI08_adoption_physical_cut_historical',copy.deepcopy(project.get('operational_adoption',{}).get('physical_cut')));project.update(latest_saved_tick=physical['tick'],operational_current_cut=physical,operational_current_snapshot=snapshot,latest_selected_use=witness)
 continuity.setdefault('PI08_adoption_point_historical',{'physical_cut':copy.deepcopy(continuity.get('physical_cut')),'latest_snapshot':copy.deepcopy(continuity.get('latest_snapshot'))});continuity.update(updated_utc=now,life_id=LIFE,world_id=card['world_id'],profile=card['profile'],physical_cut=physical,parent=card['parent'],latest_snapshot=snapshot,identity_card={'path_relative_to_product':'sistema/estado/vidas/'+LIFE+'/VIDA.json','sha256':sha(S/'estado/vidas'/LIFE/'VIDA.json')},latest_operational_use=witness,current_cut_scope='Actual saved cut after the selected public use; earlier panel/adoption cuts retain their exact historical coverage.')
 personal.update(current_saved_tick=physical['tick'],current_saved_snapshot_sha256=card['snapshot_sha256'],current_cut_updated_utc=now)
 config.setdefault('PI08_adopted_source_point_historical',{'source_tick':config.get('source_tick'),'source_snapshot_sha256':config.get('source_snapshot_sha256')});config.update(current_operational_tick=physical['tick'],current_operational_snapshot_sha256=card['snapshot_sha256'],current_operational_world_id=card['world_id'],latest_actual_use=witness,existing_continuation_only=True)
 catalog.setdefault('PI08_adoption_point_historical',copy.deepcopy(catalog.get('current_principal')));current=catalog['current_principal'];current.update(N=physical['N'],tick=physical['tick'],snapshot_sha256=card['snapshot_sha256'],world_id=card['world_id'],updated_utc=now,latest_actual_selected_use=witness)
 for entry in catalog['entries']:
  if entry.get('id')=='PI08_REGULACION_ADQUIRIDA_CONSOLIDADA_A_01':entry['latest_operational_use']={'proof':witness,'physical':physical,'snapshot_sha256':card['snapshot_sha256'],'scope':'One actual selected public use; no new complete retention panel inferred.'}
 return result
def main(a):
 if not a.aplicar:print(json.dumps({'mode':'PLAN_ONLY','life_id':LIFE,'updates':FILES,'leaves_untouched':['ACTIVO','VIDA','Native snapshot','contracts','source code','historical panel cuts'],'required_use_proof_fields':['life_id','closed','owner_closed','criteria_met','final_tick','snapshot_sha256'],'Native_executed':False}));return
 if a.use_proof is None or a.salida is None:raise ValueError('Actual closed selected-use proof and fresh output required')
 evidence=a.use_proof.resolve(strict=True);output=a.salida.resolve()
 if not evidence.is_relative_to((P/'control').resolve())or output.exists()or not output.is_relative_to((P/'control').resolve()):raise ValueError('Bounded actual proof/new output only')
 use=read(evidence);cardpath=S/'estado/vidas'/LIFE/'VIDA.json';card=read(cardpath);activepath=S/'estado/ACTIVO.json';active=read(activepath);contractpath=S/'contratos/PI08_USO_OPERATIVO_R01.json';contract=read(contractpath)
 if active.get('life_id')!=LIFE or active.get('snapshot_sha256')!=card['snapshot_sha256']or contract.get('status')!='COMMITTED'or contract.get('life_id')!=LIFE:raise ValueError('Actual exact committed selected principal required')
 if use.get('life_id')!=LIFE or any(use.get(key)is not True for key in('closed','owner_closed','criteria_met'))or use.get('final_tick')!=card['physical']['tick']or use.get('snapshot_sha256')!=card['snapshot_sha256']:raise ValueError('Real closed-use witness must match the actual current saved cut')
 snapshot=S/card['snapshot']
 if sha(snapshot)!=card['snapshot_sha256']:raise ValueError('Actual snapshot identity mismatch')
 db=S/'estado/servicios_persistentes'/card['world_id']/'cola.sqlite3';wal=db.with_name(db.name+'-wal')
 if(wal.exists()and wal.stat().st_size)or(S/'estado/locks'/(card['world_id']+'.lock')).exists():raise ValueError('Nonempty WAL or writer remains; never clear it')
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();owner=json.loads(row[0])if row else{};pending=con.execute("SELECT COUNT(*)FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]
  if owner.get('running')is not False or pending:raise ValueError('Actual owner/transport is not closed')
 finally:con.close()
 protected={str(path):sha(path)for path in(cardpath,activepath,snapshot,contractpath)};values={name:read(C/name)for name in FILES};before={name:sha(C/name)for name in FILES};witness={'path':str(evidence),'sha256':sha(evidence)};new=proposed_updates(values,card,use,witness);backup=output.with_suffix('')
 if backup.exists():raise FileExistsError('Prior refresh backup preserved')
 backup.mkdir()
 for name in FILES:
  path=C/name;regular(path);old=backup/name;old.parent.mkdir(parents=True,exist_ok=True);old.write_bytes(path.read_bytes())
 for name in FILES:
  if sha(C/name)!=before[name]:raise ValueError('Concurrent descriptor change; no overwrite')
 if any(sha(Path(path))!=digest for path,digest in protected.items()):raise ValueError('Native selected state changed before descriptive refresh')
 for name,value in new.items():
  target=C/name;temporary=target.with_name(target.name+'.PI08_CURRENT_WRITING')
  with temporary.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  os.replace(temporary,target)
 result={'schema':'DEE.PI08.current_cut.descriptive_refresh.v1','applied':True,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'life_id':LIFE,'tick':card['physical']['tick'],'snapshot_sha256':card['snapshot_sha256'],'actual_selected_use':witness,'before_hashes':before,'after_hashes':{name:sha(C/name)for name in FILES},'literal_backups':str(backup),'Native_and_ACTIVO_contract_hashes_unchanged':all(sha(Path(path))==digest for path,digest in protected.items()),'Native_executed':False,'historical_adoption_source_panel_cuts_preserved':True}
 with output.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(output),'sha256':sha(output),'current_tick':result['tick'],'snapshot_sha256':result['snapshot_sha256'],'Native_executed':False}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--use-proof',type=Path);ap.add_argument('--salida',type=Path);ap.add_argument('--aplicar',action='store_true');main(ap.parse_args())
