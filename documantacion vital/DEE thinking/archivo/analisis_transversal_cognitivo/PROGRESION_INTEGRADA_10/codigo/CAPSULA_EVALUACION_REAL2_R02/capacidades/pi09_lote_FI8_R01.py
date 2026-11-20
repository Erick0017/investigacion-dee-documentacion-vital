"""Explicit new eight-offer FI lot; old FI quota/history remain literal.

Prepared P0 supply only. Same frozen FI access/calendar/reader in a private
namespace. No new anatomy, Native learning, clock/bank edit or energy claim.
No DEE import/material action on import. Root must admit after actual panel.
"""
from pathlib import Path
import hashlib,importlib.util,json,os
VERSION='DEE.PI09.explicit_FI_eight_offer_lot.R01'
KEY='DEE.Cognitive.PI09.explicit_FI_eight_offer_lot.R01';FOLDER='PI09_FI_LOTE8_R01'
ADMIT='eci01-pi09-fi-lote-admitir';QUERY='eci01-pi09-fi-lote-consultar';STATE='eci01-pi09-fi-lote-estado';MODES={ADMIT,QUERY,STATE}
OLD_KEY='DEE.Cognitive.PI07.regulated_FI_access.R01';OLD_SOURCE=Path(__file__).with_name('pi07_acceso_FI_regulado_R01.py');OLD_SHA='cefe1174debca3650fffeba22f1f1c2d03420211993734e319b9e47684c5db46'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01';_PRIVATE=None
def require(ok,msg):
 if not ok:raise ValueError(msg)
def sha(data):return hashlib.sha256(data).hexdigest()
def entries(a):return dict(a.world.runtime.snapshot_metadata_entries)
def component():
 global _PRIVATE
 if _PRIVATE is None:
  require(sha(OLD_SOURCE.read_bytes())==OLD_SHA,'Cambió el acceso FI congelado')
  sp=importlib.util.spec_from_file_location('capacidades._PI09_FI8_literal_fixed_access',OLD_SOURCE);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
  m.VERSION,m.KEY,m.FOLDER=VERSION,KEY,FOLDER;m.START,m.QUERY,m.STATE=ADMIT,QUERY,STATE;m.NEW_MODES={ADMIT,QUERY,STATE};m.MODES={*m.regulation.MODES,*m.NEW_MODES};_PRIVATE=m
 return _PRIVATE
def identity(a):
 m=component();i=m.regulation._identity(a)
 require(i.get('life_id')==LIFE and int(a.world.runtime.dimension)==67,'Este lote P0 sólo se prepara en la descendencia Discovery exacta N67')
 return i
def validate_literal(row):
 require(isinstance(row,dict)and row.get('modo')in MODES,'Modo de lote FI explícito requerido')
 if row['modo']in(ADMIT,STATE):require(set(row)=={'modo'},'Admisión/estado sin contador, capacidad, respuesta ni objetivo')
 else:require(set(row)=={'modo','izquierda','derecha'}and all(type(row[k])is int and 0<=row[k]<=20 for k in('izquierda','derecha')),'Consulta FI pública con dos datos0..20; sin control de lector')
def _old(a):
 e=entries(a);require(OLD_KEY in e,'Falta la historia del acceso FI anterior');old=json.loads(e[OLD_KEY])
 require(old.get('ordinal')==7 and len(old.get('rows',[]))==7 and not old.get('pending')and not old.get('uncertain'),'La nueva oferta exige el corte anterior cerrado7/8; jamás amplía ni reinicia ese lote')
 return e[OLD_KEY]
def validate(a,row):
 validate_literal(row);identity(a);m=component();m.protocol(True)
 if row['modo']==ADMIT:
  require(not m.regulation._selected(a),'La admisión ambiental no se hace en ACTIVO');_old(a)
 elif row['modo']==QUERY:
  require(KEY in entries(a),'Admita explícitamente el nuevo lote antes de usarlo');m.validate(a,row)
def state(a):
 identity(a);present=KEY in entries(a);m=component();progress=m._get(a)if present else None
 return {'version':VERSION,'present':present,'progress':progress,'new_native_ticks':0,'new_lot_total':8,'new_lot_remaining':None if progress is None else 8-progress['ordinal'],'old_FI_ordinal':json.loads(entries(a)[OLD_KEY])['ordinal'],'old_lot_not_reset':True,'not_learning_or_energy':True}
def plan_values(old_literal,regulation_literal,tick):
 old=json.loads(old_literal)
 require(old.get('ordinal')==7 and len(old.get('rows',[]))==7 and not old.get('pending')and not old.get('uncertain'),'Sólo un lote anterior cerrado7/8')
 m={'version':VERSION,'protocol_sha256':None,'ready':True,'ordinal':0,'rows':[],'pending':None,'uncertain':False,'log_count':0,'log_chain_sha256':'00'*32,'R03_metadata_literal_sha256':sha(regulation_literal.encode('utf8')),'explicit_new_supply':{'offers':8,'old_KEY':OLD_KEY,'old_ordinal':7,'old_remaining':1,'old_literal_sha256':sha(old_literal.encode('utf8')),'admitted_at_tick':tick,'Native_inputs':0,'Native_ticks':0,'physical_banks_reset':False,'not_energy':True,'not_learning':True}}
 return m
def admit(a,directory):
 validate(a,{'modo':ADMIT});m=component();before_entries=entries(a);old=_old(a);before=m.body._physical(a)
 if KEY in before_entries:
  current=m._get(a);require(current['explicit_new_supply']['old_literal_sha256']==sha(old.encode('utf8')),'Cambió el antecedente después de la admisión; no se suministra otra vez')
  return {**state(a),'already_admitted':True,'new_offers_added_now':0,'idempotent_no_reset':True,'requests':[]}
 home=m._home(directory,a);require(not home.exists(),'Un namespace previo/particular se conserva sin recrearlo')
 for node in(home,*home.parents):require(not node.exists()or not(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&1024),'No se admiten enlaces en el nuevo lote')
 require(home.parent.is_dir(),'El hogar completo existente debe preceder al nuevo lote')
 progress=plan_values(old,before_entries[m.regulation.KEY],int(a.tick));_,ph=m.protocol(True);progress['protocol_sha256']=ph
 event={'index':0,'tick':int(a.tick),'kind':'EXPLICIT_NEW_EXTERNAL_FI_LOT8_ADMITTED_ZERO_NATIVE','new_KEY':KEY,'old_KEY':OLD_KEY,'old_literal_sha256':sha(old.encode('utf8')),'new_offers':8,'old_ordinal_preserved':7,'old_remaining_preserved':1,'no_energy_or_learning_claim':True}
 line=(json.dumps(m.body._safe(event),ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf8')
 progress.update(log_count=1,log_chain_sha256=sha(bytes.fromhex('00'*32)+line));encoded=m.body._encoded(progress)
 # Validate all bytes/namespace/old metadata before the first host artifact.
 # If I/O fails, its directory is preserved and never automatically reused.
 home.mkdir(exist_ok=False)
 with(home/'eventos.jsonl').open('xb')as f:f.write(line);f.flush();os.fsync(f.fileno())
 a.world.runtime.set_snapshot_metadata(KEY,encoded)
 require(m.body._physical(a)==before and all(entries(a).get(k)==v for k,v in before_entries.items())and set(entries(a))==set(before_entries)|{KEY},'La admisión cambió un antecedente o física; preservar sin repetir')
 return {**state(a),'admitted':True,'new_offers_added_now':8,'physical_unchanged':True,'all_old_metadata_literal_unchanged':True,'requests':[],'new_native_ticks':0}
def dispatch(a,row,*,actuator='closed',directory=None):
 validate(a,row)
 if row['modo']==STATE:return state(a)
 require(actuator=='closed'and directory is not None,'Actuador cerrado y hogar propietario existentes requeridos')
 if row['modo']==ADMIT:return admit(a,directory)
 old=entries(a)[OLD_KEY];value=component().query(a,row,directory)
 require(entries(a)[OLD_KEY]==old,'Cambió el lote anterior; no se consumen dos contadores')
 return {**value,'explicit_new_FI_lot':KEY,'old_FI_literal_unchanged':True,'P0_supply_not_learning':True}
def operational_dependencies(a,directory):
 if KEY not in entries(a):return {'version':VERSION,'present':False,'new_native_ticks':0}
 identity(a);result=component().operational_dependencies(a,directory);require(sha(_old(a).encode('utf8'))==component()._get(a)['explicit_new_supply']['old_literal_sha256'],'El antecedente FI dejó de ser literal')
 return {**result,'new_lot_total':8,'old_lot_ordinal_preserved':7,'old_lot_remaining_preserved':1}
def uncertain(a):return KEY in entries(a)and bool(component()._get(a).get('uncertain'))
def code_files():return tuple(dict.fromkeys([Path(__file__),*component().code_files()]))
