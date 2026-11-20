"""Exact PREPARED moved-life administrative load, no scientific body edits.

The old inherited transport stays literal. Its private current() callback gets
one explicit alternate branch while the predecessor remains selected. Only
STATE requests are admitted there. Selected use still passes the original
exact COMMITTED validator. No Native input, reset, selector or card is written.
"""
from pathlib import Path
import ast,hashlib,json
VERSION='DEE.PI09.exact_prepared_unselected_load.R01'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'
PREDECESSOR='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
TRANSPORT_SHA='e7ba613480fc24db22a72a4bf2a09439277a9ad3988ee94b1ea5f4ae6d71c712'
STATES={'eci01-pi09-estado','eci01-pi04-c2c-estado','eci01-pi07-fi-acceso-estado'}
SYSTEM='DEE.Cognitive.System.1.1.life.v1';KEY='DEE.Cognitive.PI09.selective_registered_consultation.R02';_DONE=False
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def prepared(a,identity):
 from capacidades import pi09_permiso_operativo_R01 as permission
 p=permission.profile(a)
 need(identity.get('life_id')==LIFE and identity.get('profile')=='fisica_directa'and int(a.world.runtime.dimension)==67 and permission._selected()==PREDECESSOR,'Sólo la vida PI09 trasladada y todavía no seleccionada')
 need(p is not None and p.get('status')=='PREPARED_DIAGNOSTIC'and p.get('all_adoption_gates_met')is True and p.get('adoption_decision_sha256')is None,'Se requiere el perfil PREPARED exacto, sin promover anticipadamente')
 m=json.loads(dict(a.world.runtime.snapshot_metadata_entries)[KEY]);control=m.get('control',{})
 need(m.get('ordinal')==12 and len(m.get('rows',[]))==12 and m.get('sample_register')is None and m.get('ready')and not m.get('pending')and not m.get('uncertain')and control.get('arm')=='native_real'and control.get('query_policy')=='native'and control.get('information_policy')=='real','Sólo el prefijo Native12 cerrado; no otra preparación ni control')
 return p
def gate(a,identity,active):
 current=json.loads(Path(active).read_text('utf-8-sig')).get('life_id')
 if current==identity['life_id']:return True
 prepared(a,identity);return False
def guard_external(a,row):
 from capacidades import pi09_permiso_operativo_R01 as permission
 identity=permission._identity(a)
 if identity.get('life_id')==LIFE and permission._selected()!=LIFE:
  prepared(a,identity);need(isinstance(row,dict)and set(row)=={'modo'}and row.get('modo')in STATES,'La carga PREPARED sólo admite tres STATE; ningún uso material antes de COMMITTED')
def install():
 global _DONE
 if _DONE:return
 from capacidades import pi09_transporte_heredado_R02 as transport
 source=Path(transport.__file__);need(sha(source)==TRANSPORT_SHA,'Cambió el transporte heredado literal')
 text=source.read_text('utf-8-sig');tree=ast.parse(text);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='current');body=ast.get_source_segment(text,node)
 before='if active.exists():';need(body.count(before)==1,'Cambió el ancla de carga administrativa')
 body=body.replace(before,'if active.exists() and _prepared_load_gate(a,identity,active):')
 namespace=dict(transport.__dict__);namespace['_prepared_load_gate']=gate;exec(compile(body,str(source)+':PREPARED_load_identity_only','exec'),namespace)
 transport.current=namespace['current'];_DONE=True
