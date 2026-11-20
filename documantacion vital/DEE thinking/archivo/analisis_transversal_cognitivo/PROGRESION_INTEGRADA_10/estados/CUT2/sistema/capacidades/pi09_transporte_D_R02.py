"""Exact D clone transport. No Native metadata/identity leaf is rewritten."""
from pathlib import Path
import hashlib,importlib.util,json
VERSION='DEE.PI09.D.exact_ancestral_readonly_transport.R02';SYSTEM='DEE.Cognitive.System.1.1.life.v1';SOURCE=Path(__file__).with_name('pi09_transporte_heredado_R02.py');SOURCE_SHA='e7ba613480fc24db22a72a4bf2a09439277a9ad3988ee94b1ea5f4ae6d71c712';SCOPE=Path(__file__).with_name('PI09_TRANSPORTE_D_R02.json');_BASE=None
def need(ok,why):
    if not ok:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def base():
    global _BASE
    if _BASE is None:
        need(sha(SOURCE)==SOURCE_SHA,'Literal ancestral transport changed');s=importlib.util.spec_from_file_location('capacidades._D_transport_private_ancestry_R02',SOURCE);b=importlib.util.module_from_spec(s);s.loader.exec_module(b);b.current=current;_BASE=b
    return _BASE
def config():
    c=read(SCOPE);ids={'real':'DISCOVERY','none':'STAGE3_NONE','yoked':'STAGE3_YOKE','reproduction':'DREPRO','reference':'D_WSLS'}
    need(c['schema']=='DEE.PI09.D.exact_readonly_transport_scope.R02'and c['role']in ids and c['life_id']=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_'+ids[c['role']]+'_01'and c['parent_R02_ordinal']==12,'Exact D role/identity and unchanged parent12')
    need(sha(Path(__file__).with_name('pi09_consulta_selectiva_R02.py'))=='3b81573f4dc0d9401db2210f3b23694e1f1f4a4d820d7654bcbd1e1b42b2dfbf','Scientific R02 stays literal')
    old=base().config();need(old['life_id']==c['life_id'],'Inherited C/B scope and current D identity disagree');return c,old
def applies(a):return SCOPE.is_file()and json.loads(dict(a.world.runtime.snapshot_metadata_entries)[SYSTEM]).get('life_id')==read(SCOPE).get('life_id')
def current(a):
    c,old=config();entries=dict(a.world.runtime.snapshot_metadata_entries);identity=json.loads(entries[SYSTEM]);need(identity.get('life_id')==c['life_id']and identity.get('profile')=='fisica_directa'and int(a.world.runtime.dimension)==67,'Exact D N67 current identity')
    for key,digest in old['inherited_metadata_sha256'].items():need(key in entries and hashlib.sha256(entries[key].encode('utf8')).hexdigest()==digest,'Ancestral C/B metadata changed')
    active=Path(__file__).resolve().parents[1]/'estado/ACTIVO.json'
    if active.exists():
        need(c['role']=='real','Control/replay/reference D can never load in a selected system')
        if read(active).get('life_id')!=identity['life_id']:
            # Optional future P0 administrative bridge, separate from D science.
            # Missing module is a closed failure. Dispatcher permits only3STATE
            # here; there is never a prepared-load material EP permission.
            from capacidades.pi09_permiso_operativo_D_R01 import validate_prepared_load
            validate_prepared_load(a,identity)
        else:
            from capacidades import pi09_entorno_persistente_D_R02 as D
            D._operational_permission(a,identity)
    return identity
def component_B(a,original):return base().component_B(a,original)
def component_C(a,original):return base().component_C(a,original)
def code_files():
    extra=Path(__file__).with_name('pi09_permiso_operativo_D_R01.py')
    return(Path(__file__),SCOPE,SOURCE,*([extra]if extra.is_file()else[]))
