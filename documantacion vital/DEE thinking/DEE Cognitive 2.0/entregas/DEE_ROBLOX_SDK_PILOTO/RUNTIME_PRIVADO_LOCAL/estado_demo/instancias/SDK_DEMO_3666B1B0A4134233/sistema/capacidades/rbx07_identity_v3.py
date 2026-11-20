"""RBX administrative bootstrap. Pure import, no new physical support.

RBX is a separate unselected experiment, not PI11 and not a promoted product.
Only the inherited C2C consumer's read-only Python identity is rebound.
"""
from pathlib import Path

VERSION = 'DEE.Roblox.SDK.identity.0.1.0'
C2C_SHA = '0cf6bf8508e071a1c8cf1448023a096bc43336d66b8a1deb98f488b29b4205fd'
_INSTALLED = False


def checked(a):
    from capacidades import rbx07_native_v3 as rbx
    from capacidades import pi10_transporte_ancestral_R01 as transport
    i = rbx.identity(a)
    if transport.config().get('role') != 'rbx01':
        raise ValueError('RBX explicit experimental administrative role required')
    return i


def readonly_C2C(component, a):
    i = checked(a)
    if component.protocol()[1] != C2C_SHA:
        raise ValueError('Literal inherited C2C32 protocol required')
    component.OPERATIONAL_LIFE_ID = i['life_id']
    return component


def deny_public(a, *args, **kwargs):
    checked(a)
    raise ValueError('RBX has no historical/public retention or promotion permission')


def validate_external(a, row, *, payload):
    checked(a)
    if payload.get('operacion') in ('reanudar', 'pausar', 'guardar', 'detener'):
        if row is not None or set(payload) != {'operacion'}:
            raise ValueError('Exact RBX administrative control')
        return
    from capacidades import rbx07_native_v3 as rbx
    if (payload.get('operacion') != 'sesion' or payload.get('retorno') != 'omit' or
            payload.get('actuador') != 'closed' or not isinstance(row, dict) or
            row.get('modo') not in rbx.MODES):
        raise ValueError('Only explicit bounded RBX physical phases; no historical material')
    rbx.validate(a, row)


def install(a):
    global _INSTALLED
    if _INSTALLED:
        return
    i = checked(a)
    from capacidades import pi10_permiso_operativo_R02 as permission
    permission.LIFE = i['life_id']
    permission.configure_C2C = readonly_C2C
    permission.diagnostic_real = lambda current: (checked(current) and False)
    permission.public_allowed = lambda current: (checked(current) and False)
    permission.routes_public = lambda current, row: (checked(current) and False)
    permission.validate_public = deny_public
    permission.execute_public = deny_public
    permission.validate_external = validate_external
    permission.install(a)
    _INSTALLED = True


def code_files():
    return (Path(__file__),)
