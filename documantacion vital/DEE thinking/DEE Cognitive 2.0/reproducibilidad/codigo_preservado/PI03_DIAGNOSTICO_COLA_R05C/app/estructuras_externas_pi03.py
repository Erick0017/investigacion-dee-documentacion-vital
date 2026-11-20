"""Restore only the fixed empty-directory scaffold of a copied PI03 device.

Files, Native snapshots, clocks, capsules, device state, policy and counters
are never created or changed. No DEE import. This is external apparatus import
support, not acquired recovery or a correction of the actor's output.
"""
from pathlib import Path
import hashlib,json

VERSION='PI03.external_device_directory_import.OP2'
DEVICE_VERSION='PI03.delayed_material_feeder.R02_PROPOSAL'
DIRECTORIES=('reservoir','inflight_minus','inflight_plus','inflight_silence','products','rejected')

def _check(path,root):
    for item in(path,*path.parents):
        try:attributes=getattr(item.lstat(),'st_file_attributes',0)
        except FileNotFoundError:attributes=0
        if item.is_symlink()or attributes&1024:
            raise ValueError('Linked/reparse external device path refused: '+str(item))
    resolved=path.resolve(strict=False)
    if not resolved.is_relative_to(root.resolve(strict=True)):
        raise ValueError('External device scaffold escapes explicit worker directory')
    return resolved

def restore_known_device_directories(worker_directory):
    root=Path(worker_directory).absolute()
    if not root.exists():
        return {'version':VERSION,'known_device_present':False,'created_directories':[],
                'scope':'No worker/device state; nothing is reconstructed.'}
    root=_check(root,root)
    home=_check(root/'PI03_TAREA_DIFERIDA_R02/dispositivo',root)
    state=_check(home/'ESTADO_DISPOSITIVO.json',root)
    if not state.exists():
        return {'version':VERSION,'known_device_present':False,'created_directories':[],
                'scope':'No ESTADO_DISPOSITIVO.json; never create an empty device.'}
    if not state.is_file():raise ValueError('Known device state must be a regular copied file')
    before=hashlib.sha256(state.read_bytes()).hexdigest()
    data=json.loads(state.read_text(encoding='utf-8'))
    if data.get('version')!=DEVICE_VERSION:
        raise ValueError('Unknown external-device version; no guessed directory repair')
    paths=[_check(home/name,root)for name in DIRECTORIES]
    for path in paths:
        if path.exists()and not path.is_dir():raise ValueError('Device scaffold destination is an existing file: '+str(path))
    created=[]
    for path in paths:
        if not path.exists():
            path.mkdir();created.append(path.relative_to(root).as_posix())
    if hashlib.sha256(state.read_bytes()).hexdigest()!=before:
        raise ValueError('Device state changed during external-directory import')
    return {'version':VERSION,'known_device_present':True,'device_state_version':DEVICE_VERSION,
            'device_state_sha256':before,'created_directories':created,'new_native_ticks':0,
            'files_written':0,'policy_or_content_updated':False,
            'scope':'Only missing six fixed external scaffold directories. No files, resources, counters, memories, clocks or Native outputs were supplied.'}
