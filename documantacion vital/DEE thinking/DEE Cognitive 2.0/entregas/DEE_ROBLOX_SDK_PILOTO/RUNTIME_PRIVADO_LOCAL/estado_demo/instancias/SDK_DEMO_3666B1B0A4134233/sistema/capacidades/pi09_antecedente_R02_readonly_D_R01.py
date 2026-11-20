"""Private identity-only view of acquired R02_12. External STATE/deps only."""
from pathlib import Path
import hashlib,importlib.util
VERSION='DEE.PI09.D.R02_ancestor_readonly_alias.R01';KEY='DEE.Cognitive.PI09.selective_registered_consultation.R02';STATE='eci01-pi09-estado';MODES={STATE};SOURCE=Path(__file__).with_name('pi09_consulta_selectiva_R02.py');SOURCE_SHA='3b81573f4dc0d9401db2210f3b23694e1f1f4a4d820d7654bcbd1e1b42b2dfbf';_PRIVATE=None
def need(ok,why):
    if not ok:raise ValueError(why)
def identity(a):
    from capacidades import pi09_transporte_D_R02 as transport
    identity=transport.current(a);private()._C().LIFE=identity['life_id'];return identity
def private():
    global _PRIVATE
    if _PRIVATE is None:
        need(hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA,'Literal ancestor R02 changed');s=importlib.util.spec_from_file_location('capacidades._D_readonly_ancestor_R02',SOURCE);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m._identity=identity;original=m.validate
        def validate(a,row):
            need(row=={'modo':STATE},'Historical R02 only STATE; never PREPARE/EPISODE/reset');return original(a,row)
        m.validate=validate;_PRIVATE=m
    return _PRIVATE
def validate_literal(row):need(row=={'modo':STATE},'Only historical R02 STATE; new D has a separate supplied namespace')
def validate(a,row):validate_literal(row);return private().validate(a,row)
def dispatch(a,row,*,actuator='closed',directory=None):validate(a,row);return private().state(a)
def operational_dependencies(a,directory):return private().operational_dependencies(a,directory)
def uncertain(a):return private().uncertain(a)
def code_files():return tuple(dict.fromkeys([Path(__file__),SOURCE,*private().code_files()]))
