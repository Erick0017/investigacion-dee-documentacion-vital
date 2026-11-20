"""Suplemento administrativo: exige reapertura Source D0 real antes del traslado.

Reutiliza literalmente el motor de movimiento R01. No abre DEE al importar,
no altera cuerpos científicos y no autoriza ninguna promoción por defecto.
"""
from pathlib import Path
import hashlib,importlib.util
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
SOURCE=H/'incorporar_D_PI09_misma_identidad_R01.py'
SOURCE_SHA='ec2c472d0543b954bbf333a8de76125f36f28a97cdaa57917fd7ec5617f57e9b'
if sha(SOURCE)!=SOURCE_SHA:raise ValueError('Cambió el incorporador D R01 conservado')
sp=importlib.util.spec_from_file_location('PI09_D_same_identity_R01_literal',SOURCE);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
original_validate=m.validate_D_evidence
def validate_source_zero(d):
 p=m.evidence(d['D_source_zero_reopening_proof'])
 flags=('physical_unchanged','causal_prefix_equal','operational_state_valid','pending_reconciled','stock_unchanged','all_scientific_metadata_literal_unchanged','source_code_unchanged','current_principal_unchanged','owner_closed','closed')
 fields={'physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase'}
 m.need(p.get('schema')=='DEE.PI09.D.mature_source.public_reopening0.R01'and p.get('life_id')==m.LIFE and p.get('selected')is False,'Se exige reapertura real de la misma Source D aislada')
 m.need(type(p.get('new_ticks'))is int and p['new_ticks']==0 and type(p.get('new_Native_inputs'))is int and p['new_Native_inputs']==0 and p.get('initial_tick')==p.get('final_tick')==d['source_tick'],'La reapertura Source no puede introducir ticks ni entradas')
 m.need(all(p.get(k)is True for k in flags)and set(p.get('Native_field_equalities',{}))==fields and all(v is True for v in p['Native_field_equalities'].values()),'Se exige igualdad completa Native, recursos, metadatos científicos y código')
 m.need(p.get('snapshot_sha256')==d['source_snapshot_sha256']==p['after_snapshot']['sha256']and p.get('stock_before')==p.get('stock_after'),'El checkpoint final y los recursos deben vincular la decisión actual')
 stock=p['stock_after']['D'];m.need(stock=={'ordinal':d['source_D_ordinal'],'total':12,'remaining':12-d['source_D_ordinal']},'No se inventa ni reinicia stock D')
 return True
def validate(d):
 original_validate(d);validate_source_zero(d);return True
m.validate_D_evidence=validate
def decision(file):
 d=m.decision(file);m.base().PARENT_SHA=d['protected_parent_snapshot_sha256'];return d
code=m.code;parent=m.parent;read=m.read;need=m.need;evidence=m.evidence;LIFE=m.LIFE;P=m.P;C=m.C;S=m.S;CS=m.CS;GATES=m.GATES
def base():
 b=m.base();b.validate_PI09_evidence=validate;b.decision=decision;return b
if __name__=='__main__':base().main()
