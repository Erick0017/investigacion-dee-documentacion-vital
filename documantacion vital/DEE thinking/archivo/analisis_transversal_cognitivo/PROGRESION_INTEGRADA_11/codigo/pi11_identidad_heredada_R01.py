"""Diagnostic administrative identity binding, no Native or learned metadata edit.

Only the exact PI11 clone's local code namespace is rebound. The historical
permission/source files remain literal. Selected product use requires a
separate validated PI11 operational permission and is not enabled here.
"""
from pathlib import Path
import json,re
_INSTALLED=False
def install(a):
    global _INSTALLED
    if _INSTALLED:return
    from capacidades import pi10_transporte_ancestral_R01 as transport
    i=transport.identity(a);life=i['life_id'];root=Path(__file__).resolve().parents[1]
    if not re.fullmatch('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_[A-Z0-9_]{1,20}',life):raise ValueError('Exact PI11 diagnostic descendant required')
    if (root/'estado/ACTIVO.json').exists():raise ValueError('Diagnostic binding cannot select or enable a product principal')
    from capacidades import pi10_permiso_operativo_R02 as permission
    permission.LIFE=life
    # This is the current consumer used by owner and PI04's private namespace.
    # No state, RAW, clock, bank, counter, agenda or response is changed.
    permission.install(a)
    _INSTALLED=True
def code_files():return (Path(__file__),)
