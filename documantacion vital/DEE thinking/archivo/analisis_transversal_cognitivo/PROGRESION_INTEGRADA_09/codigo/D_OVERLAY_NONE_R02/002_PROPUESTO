"""Existing FI8 private namespace; D controls only read its inherited history."""
from pathlib import Path
import hashlib,importlib.util,json
VERSION='DEE.PI09.D.FI8_current_identity_alias.R01';KEY='DEE.Cognitive.PI09.explicit_FI_eight_offer_lot.R01';ADMIT='eci01-pi09-fi-lote-admitir';QUERY='eci01-pi09-fi-lote-consultar';STATE='eci01-pi09-fi-lote-estado';MODES={ADMIT,QUERY,STATE};SOURCE=Path(__file__).with_name('pi09_lote_FI8_R01.py');SOURCE_SHA='ecbf6cf65bdfce0359ed840bd803e5775e494bc10d8b50716bfd4124cfd12d96';_PRIVATE=None
def need(ok,why):
    if not ok:raise ValueError(why)
def identity(a):
    from capacidades import pi09_transporte_D_R02 as transport
    return transport.current(a)
def private():
    global _PRIVATE
    if _PRIVATE is None:
        need(hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA,'Original admitted FI8 module must remain literal')
        s=importlib.util.spec_from_file_location('capacidades._D_FI8_private_literal',SOURCE);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.identity=identity;component=m.component()
        # Separate the old R03 identity namespace as well: FI8 uses its helpers
        # internally; no external old R03 episode is routed through this alias.
        source=Path(component.regulation.__file__);need(hashlib.sha256(source.read_bytes()).hexdigest()=='40648fd81c5b1f278ee9c18d0d464c5a4b5e9fd808054afe6ff072a10fda0ac5','Original R03 body must remain literal');sp=importlib.util.spec_from_file_location('capacidades._D_FI8_R03_identity_only',source);reg=importlib.util.module_from_spec(sp);sp.loader.exec_module(reg);reg._identity=identity
        component.regulation=reg;_PRIVATE=m
    return _PRIVATE
def validate_literal(row):return private().validate_literal(row)
def validate(a,row):
    validate_literal(row);i=identity(a)
    if row['modo']!=STATE:need(i['life_id']=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01','FI8 material use only the real Discovery; control/replay/reference only STATE/deps')
    return private().validate(a,row)
def dispatch(a,row,*,actuator='closed',directory=None):validate(a,row);return private().dispatch(a,row,actuator=actuator,directory=directory)
def operational_dependencies(a,directory):return private().operational_dependencies(a,directory)
def uncertain(a):return private().uncertain(a)
def code_files():return tuple(dict.fromkeys([Path(__file__),SOURCE,*private().code_files()]))
