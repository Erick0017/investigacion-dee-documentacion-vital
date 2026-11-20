"""Adopción D con un suplemento administrativo explícito de una fila/24.

PREPARACION y decisión se leen literalmente y permanecen sin sobrescribir.
Sólo su vista privada del registro de código utiliza el alias D aprobado.
"""
from pathlib import Path
import copy,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;P=H.parent
SOURCE=H/'incorporar_D_PI09_misma_identidad_R03.py';PIN='c18518aff06ece505061b40e5b75ad47232c78599772196e3729eb9f04da0d8f'
SUPPLEMENT=P/'control/SUPLEMENTO_REGISTRO_D_ALIAS_APLICADO_PI09_R01.json';SUPPLEMENT_SHA='2712d73a91be8a659cfdccd5245734695c52b59d256c8a806df4919975acb1b8';FILE='capacidades/PI09_PLUGINS_D_R02.json';OLD='PI09_TRANSPORTE_HEREDADO_R02.json';NEW='PI09_TRANSPORTE_D_ANCESTRO_R02.json';DIGEST='3504effe949237c74fb805ade9ce15a5749f7ae06ae844d38e795f7b1a95f38d'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def need(ok,msg):
 if not ok:raise ValueError(msg)
need(sha(SOURCE)==PIN,'Incorporador R03 conservado alterado');sp=importlib.util.spec_from_file_location('D_same_identity_R03_literal_with_admin_alias_supplement',SOURCE);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def supplemental_view(prepared):
 need(sha(SUPPLEMENT)==SUPPLEMENT_SHA,'Suplemento Root aplicado distinto');p=read(SUPPLEMENT)
 need(p.get('schema')=='DEE.PI09.D.one_registry_alias.applied.R01'and p.get('applied')is True and p.get('file')==FILE and p.get('old_name')==OLD and p.get('new_name')==NEW and p.get('same_digest')==DIGEST and p.get('original_decision_and_preparation_literal_unchanged')is True,'Sólo suplemento CAS Root exacto')
 for key in('prepared','decision','before','after','global_Native_scope','ancestral_D_scope'):
  item=p[key];need(sha(Path(item['path']))==item['sha256'],'Referencia administrativa cambió: '+key)
 need(Path(p['prepared']['path']).resolve()==m.base().PREPARED.resolve()and prepared['decision']['sha256']==p['decision']['sha256'],'Suplemento no corresponde a esta preparación/decisión')
 before=read(p['before']['path']);after=read(p['after']['path']);expected=copy.deepcopy(before);pins=expected['files_sha256'];need(pins.get(OLD)==DIGEST and NEW not in pins,'Mapa ancestral original exacto');expected['files_sha256']={NEW if k==OLD else k:v for k,v in pins.items()};need(after==expected,'No se permite otro cambio semántico del registro D')
 target=m.S/FILE;need(sha(target)==p['after']['sha256']and p['target']['sha256']==p['after']['sha256'],'Target no coincide con CAS Root aplicado')
 view=copy.deepcopy(prepared);rows=[r for r in view['deployed_code']if r['file']==FILE];need(len(rows)==1 and rows[0]['sha256']==p['before']['sha256'],'Una sola fila original preparada requerida')
 rows[0].update(sha256=p['after']['sha256'],bytes=Path(p['after']['path']).stat().st_size,source=p['after']['path'])
 need(len(view['deployed_code'])==24 and sum(a!=b for a,b in zip(view['deployed_code'],prepared['deployed_code']))==1,'Sólo1de24filas; otras23 literales')
 view['administrative_alias_supplement']={'path':str(SUPPLEMENT),'sha256':SUPPLEMENT_SHA};return view
def base():
 b=m.base()
 if not getattr(b,'D_registry_alias_supplement_R04',False):
  original_read=b.read;original_write=b.write
  def guarded_read(path):
   value=original_read(path)
   return supplemental_view(value)if Path(path).resolve()==b.PREPARED.resolve()else value
  def witnessed_write(path,value,replace=False):
   if Path(path).resolve()in(b.ADOPTED.resolve(),(P/'control/DECISION_PROMOCION_D_PRODUCTO_PI09.json').resolve()):value={**value,'administrative_code_registry_supplement':{'path':str(SUPPLEMENT),'sha256':SUPPLEMENT_SHA},'original_preparation_and_decision_not_rewritten':True}
   return original_write(path,value,replace)
  b.read=guarded_read;b.write=witnessed_write;b.D_registry_alias_supplement_R04=True
 return b
if __name__=='__main__':base().main()
