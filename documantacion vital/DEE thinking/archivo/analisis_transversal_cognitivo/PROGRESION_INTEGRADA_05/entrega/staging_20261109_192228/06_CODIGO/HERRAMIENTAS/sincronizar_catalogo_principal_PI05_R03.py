"""Root-only post-COMMITTED catalog pointer; default is read-only, zero Native."""
from pathlib import Path
import argparse,copy,datetime,hashlib,json,os,shutil
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';LIFE='ECI02_PI03_REPRO_PI04_PI05_MAIN_01';CURRENT='af74c8f47e43ed3b2395a338a23a6cbd42f105ec2cff4daac15b7a4d45e90832'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(x,s):
 if not x:raise ValueError(s)
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');a=ap.parse_args();out=P/'control/CATALOGO_PRINCIPAL_PI05_SINCRONIZADO_R03.json';need(not out.exists(),'Existing synchronization proof preserved')
 path=S/'capacidades/CATALOGO_CAPACIDADES.json';active_path=S/'estado/ACTIVO.json';card_path=S/'estado/vidas'/LIFE/'VIDA.json';adopt_path=P/'control/ADOPCION_PRODUCTO_PI05.json';reopen_path=P/'control/REAPERTURA_SELECCIONADA_PRODUCTO_PI05.json'
 j=read(path);old=copy.deepcopy(j);active=read(active_path);card=read(card_path);adopt=read(adopt_path);reopen=read(reopen_path);before=sha(path)
 need(adopt['phase']=='COMMITTED'and active['life_id']==LIFE and card['snapshot_sha256']==active['snapshot_sha256']==reopen['snapshot_sha256']==CURRENT and card['physical']['N']==67 and card['physical']['tick']==824911,'Actual selected current saved cut differs')
 need(reopen['new_ticks']==0 and reopen['owner_closed']and reopen['operational_state_valid']and reopen['physical_unchanged']and reopen['pending_reconciled'],'Actual selected0 must be valid and closed')
 need(j['current_principal']['life_id']=='ECI02_PI03_MAIN'and j['current_principal']['tick']==775355 and 'PI05_prior_current_principal'not in j,'Review existing catalog update; no overwrite or historical rewrite')
 protected={str(x):sha(x)for x in(active_path,card_path,S/card['snapshot'],adopt_path,reopen_path)}
 j['PI05_prior_current_principal']=copy.deepcopy(j['current_principal']);j['current_principal']={'life_id':LIFE,'profile':card['profile'],'N':67,'tick':824911,'physical_parent':adopt['physical_parent_protected'],'snapshot_sha256':CURRENT,'historical_committed_snapshot_sha256':adopt['active']['snapshot_sha256'],'selection':'COMMITTED','adoption_witness':str(adopt_path),'current_selected_reopening_witness':str(reopen_path),'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Actual selected/current saved main. PI03_current_principal and PI05_prior_current_principal remain literal historical records; administrative snapshots differ, no memory fusion.'}
 need({k:v for k,v in j.items()if k not in('current_principal','PI05_prior_current_principal')}=={k:v for k,v in old.items()if k!='current_principal'},'Unrelated catalog content changed')
 print(json.dumps({'mode':'APPLY_REQUESTED'if a.aplicar else'READ_ONLY_NO_WRITES','before':old['current_principal'],'proposed':j['current_principal'],'entries_unchanged':True,'entries':len(j['entries']),'Native_ticks':0},ensure_ascii=False),flush=True)
 if a.aplicar:
  backup=P/'control/CATALOGO_PRINCIPAL_PI05_ANTES_R03.json';need(not backup.exists(),'Existing literal backup preserved');need(sha(path)==before,'Concurrent catalog change');shutil.copyfile(path,backup);need(sha(backup)==before,'Backup differs')
  temp=path.with_name(path.name+'.pi05_current.tmp');need(not temp.exists(),'Existing temp preserved')
  with temp.open('x',encoding='utf8')as f:json.dump(j,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  os.replace(temp,path);need(all(sha(Path(x))==h for x,h in protected.items()),'Protected state/promotion changed')
  proof={'schema':'DEE.PI05.catalog_current_main_metadata_sync.R03','applied':True,'before_sha256':before,'after_sha256':sha(path),'literal_backup':str(backup),'prior_current_principal':old['current_principal'],'current_principal':j['current_principal'],'entries_and_history_unchanged':True,'ACTIVO_snapshots_life_queue_selectors_unchanged':True,'new_Native_ticks':0}
  with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
  print(json.dumps({'proof':str(out),'sha256':sha(out),'Native_ticks':0},ensure_ascii=False),flush=True)
