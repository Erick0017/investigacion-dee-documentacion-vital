"""PI11 non-REAL diagnostic identity and read-only C2C bootstrap transport.

Only roles none/yoked/reproduction, explicit N67 descendants without ACTIVO. No learned
metadata/Native fields are edited, and no public retention is enabled. This
fixes a bootstrap consumer asking REAL-only permission merely to enumerate
the inherited C2C code/state dependency. Main/replay R01 remains unchanged.
"""
from pathlib import Path
import json,re
VERSION='DEE.PI11.control_readonly_C2C_identity.R02'
C2CSHA='0cf6bf8508e071a1c8cf1448023a096bc43336d66b8a1deb98f488b29b4205fd'
_INSTALLED=False
def need(ok,msg):
    if not ok:raise ValueError(msg)
def checked(a):
    from capacidades import pi10_transporte_ancestral_R01 as transport
    c=transport.config();i=transport.identity(a);root=Path(__file__).resolve().parents[1]
    need(re.fullmatch('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_[A-Z0-9_]{1,20}',i['life_id'])and c['life_id']==i['life_id']and c.get('role')in('none','yoked','reproduction')and int(a.world.runtime.dimension)==67,'Exact non-REAL PI11 N67 control/replay')
    need(not(root/'estado/ACTIVO.json').exists(),'Never bind a selected/product world as a control')
    return i,c
def readonly_C2C(component,a):
    i,_=checked(a);need(component.protocol()[1]==C2CSHA,'Literal inherited C2C protocol')
    component.OPERATIONAL_LIFE_ID=i['life_id']
    return component
def deny_public(a,*args,**kwargs):
    checked(a);raise ValueError('PI11 control has no public retention/material permission')
def validate_external(a,row,*,payload):
    checked(a)
    if payload.get('operacion')in('reanudar','pausar','guardar','detener'):
        need(row is None and set(payload)=={'operacion'},'Exact administrative transport control');return
    from capacidades import pi10_transporte_ancestral_R01 as transport
    need(payload.get('operacion')=='sesion'and payload.get('retorno','omit')=='omit'and payload.get('actuador','closed')=='closed'and isinstance(row,dict)and set(row)=={'modo'},'Fixed control experiment/state only')
    allowed=transport.STATES|{'eci01-pi10-estado','eci01-pi11-preparar','eci01-pi11-episodio','eci01-pi11-estado'}
    need(row['modo']in allowed,'No retention query, historical use, new supply or public action on a control')
def install(a):
    global _INSTALLED
    if _INSTALLED:return
    i,c=checked(a)
    from capacidades import pi10_permiso_operativo_R02 as permission
    permission.LIFE=i['life_id']
    # Rebind only administrative consumers. Returning false for non-REAL
    # avoids invoking diagnostic_real's deliberate REAL-only assertion.
    permission.configure_C2C=readonly_C2C
    permission.diagnostic_real=lambda current:(checked(current)and False)
    permission.public_allowed=lambda current:(checked(current)and False)
    permission.routes_public=lambda current,row:(checked(current)and False)
    permission.validate_public=deny_public;permission.execute_public=deny_public;permission.validate_external=validate_external
    permission.install(a);_INSTALLED=True
def code_files():return (Path(__file__),)
