"""Dormant exact prospective PI07 C2C permission; pure on import.

Only an actual COMMITTED contract and selected exact life configure the
administrative allowlist of the already preserved effective C2C component.
No Native logic, protocol, data, bank, result or memory is changed.
"""
from pathlib import Path
import json,re
VERSION='DEE.PI07.exact_principal_C2C_permission.R01_CONDITIONAL'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_CAND_01'
OLD_PI04='ECI02_PI03_REPRO_PI04_MAIN_02';OLD_PI05='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
SYSTEM='DEE.Cognitive.System.1.1.life.v1';EXTENSION='DEE.Cognitive.PI05.C2C.explicit_environment30.R01'
CONTRACT='PI07_REGULACION_USO_PRINCIPAL_01.json'
R03_PROTOCOL_SHA='f69e8558799558a1ccceb70e0684a061a971b9521ad8985205d1662aea55d269'
C2C_PROTOCOL_SHA='5dda50c36fa72ea3932eded545e0bb673b40202d0d553cfa97a50ab31c67d1bc'
def _regular(path):
 for p in(path,*path.parents):
  if p.exists()and(p.is_symlink()or getattr(p.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked adopted permission')
def configure(component,a):
 entries=dict(a.world.runtime.snapshot_metadata_entries)
 if SYSTEM not in entries or json.loads(entries[SYSTEM]).get('life_id')!=LIFE:return component
 root=Path(component.__file__).resolve().parents[1];path=root/'contratos'/CONTRACT
 if not path.is_file():return component # absent adoption => dormant, original diagnostic path
 _regular(path);c=json.loads(path.read_text('utf-8-sig'));permissions=c.get('C2C_use',{})
 if(c.get('schema')!='DEE.PI07.exact_adopted_permission.v1'or c.get('status')!='COMMITTED'or c.get('life_id')!=LIFE or c.get('profile')!='fisica_directa'
    or c.get('protocol_sha256')!=R03_PROTOCOL_SHA or c.get('allowed_modes')!=['eci01-pi07-r03-episodio','eci01-pi07-r03-estado']
    or not re.fullmatch('[0-9a-f]{64}',str(c.get('adoption_decision_sha256','')))
    or permissions.get('allowed_modes')!=[component.OPPORTUNITY,component.STATE]or permissions.get('requires_environment30')is not True
    or permissions.get('protocol_sha256')!=C2C_PROTOCOL_SHA or permissions.get('current_C2C_life_id')!=LIFE):raise ValueError('Exact actually COMMITTED two-function PI07 permission required')
 active=root/'estado/ACTIVO.json';_regular(active)
 if not active.is_file()or json.loads(active.read_text('utf-8-sig')).get('life_id')!=LIFE:raise ValueError('Committed permission must agree with actual selected exact life')
 if EXTENSION not in entries:raise ValueError('Actual inherited environment30 required')
 ext=json.loads(entries[EXTENSION])
 if not ext.get('ready')or ext.get('pending')or ext.get('uncertain'):raise ValueError('Preserve incomplete environment; no bypass')
 m=component._get(a)
 if m.get('life_id')!=LIFE or m.get('protocol_sha256')!=C2C_PROTOCOL_SHA or any(m.get(k)for k in('pending','uncertain','halted_reason')):raise ValueError('Explicit one-leaf imported identity and closed preserved C2C required')
 if component.OPERATIONAL_LIFE_ID not in(OLD_PI04,OLD_PI05,LIFE):raise ValueError('Another exact permission revision is protected')
 component.OPERATIONAL_LIFE_ID=LIFE
 return component
