"""Dormant exact-life operational permission; no Native/state import or write.

Never deploy/activate its contract before a real COMMITTED adoption. It only
configures the old exact allowlist constant on the selected effective module;
all old readiness/identity/directory/preparation prohibitions remain intact.
No RAW, clocks, references, rows, acquisitions or environmental results change.
"""
from pathlib import Path
import json,re

VERSION='DEE.PI05.exact_principal_permission.R01_CANDIDATE'
LIFE='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
OLD='ECI02_PI03_REPRO_PI04_MAIN_02'
EXTENSION_KEY='DEE.Cognitive.PI05.C2C.explicit_environment30.R01'
CONTRACT='PI05_C2C_USO_PRINCIPAL_01.json'
SYSTEM_KEY='DEE.Cognitive.System.1.1.life.v1'

def configure(component,a):
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if SYSTEM_KEY not in entries or json.loads(entries[SYSTEM_KEY]).get('life_id')!=LIFE:
        return component # historical/diagnostic clones retain their old contract
    path=Path(component.__file__).resolve().parents[1]/'contratos'/CONTRACT
    if not path.exists():return component # no promotion => no permission activation
    for p in(path,*path.parents):
        if p.exists()and(p.is_symlink()or getattr(p.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked adopted-permission contract')
    contract=json.loads(path.read_text('utf-8-sig'))
    if (contract.get('schema')!='DEE.PI05.C2C.exact_adopted_permission.v1'or contract.get('status')!='COMMITTED'
        or contract.get('life_id')!=LIFE or contract.get('allowed_modes')!=[component.OPPORTUNITY,component.STATE]
        or contract.get('profile')!='fisica_directa' or contract.get('requires_environment30')is not True
        or not re.fullmatch('[0-9a-f]{64}',str(contract.get('adoption_decision_sha256','')))):
        raise ValueError('Only an actually COMMITTED exact PI05 main may receive two use permissions; no draft/dynamicACTIVO/general prefix')
    if EXTENSION_KEY not in entries:raise ValueError('Adopted permission requires the actual explicit30environment')
    ext=json.loads(entries[EXTENSION_KEY])
    if not ext.get('ready')or ext.get('uncertain')or ext.get('pending'):raise ValueError('Preserve incomplete environment, never bypass readiness')
    if component.OPERATIONAL_LIFE_ID not in(OLD,LIFE):raise ValueError('Another permission revision is protected')
    component.OPERATIONAL_LIFE_ID=LIFE # exact administrative permission, no callback/decoder/policy change
    return component

def administrative_identity_proposal(metadata,*,current_identity,source_identity):
    """Pure proposed copy for the adoption adapter; DOES NOT write metadata.

    Use only after genuine full-pair import of the same complete world and
    preserve this record alongside import provenance. The actual writer/root
    must prove physical/causal-prefix equality and reconcile journal hashes.
    """
    if current_identity!=LIFE or metadata.get('life_id')!=source_identity or source_identity==LIFE:
        raise ValueError('Exact new identity and explicit inherited current identity only')
    if any(metadata.get(k)for k in('pending','uncertain','halted_reason')):raise ValueError('No uncertain future identity rewrite')
    updated=dict(metadata);updated['life_id']=LIFE
    proof={'schema':'DEE.PI05.C2C.administrative_identity_mapping.v1','field':'life_id','from':source_identity,'to':LIFE,
        'source_history_remains_original':True,'no_memory_acquisition_or_transfer':True,'new_native_ticks':0}
    if {k:v for k,v in updated.items()if k!='life_id'}!={k:v for k,v in metadata.items()if k!='life_id'}:
        raise RuntimeError('Administrative identity proposal changed other fields')
    return updated,proof
