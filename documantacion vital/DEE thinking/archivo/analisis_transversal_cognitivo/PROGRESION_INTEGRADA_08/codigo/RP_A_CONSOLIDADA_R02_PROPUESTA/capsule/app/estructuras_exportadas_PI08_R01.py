"""PI08 RP capsule-only import supplement, before Store.import_state.

Preserves declared empty directory transport exactly. No Native dependency or
file/resource/state reconstruction; incomplete source contents remain errors.
"""
from pathlib import Path, PurePosixPath
import hashlib

VERSION = 'PI08.full_paired_export.directory_transport.R01'

def _require(ok, message):
    if not ok: raise ValueError(message)

def _regular(path):
    for node in (path, *path.parents):
        _require(not node.exists() or not(node.is_symlink() or getattr(node.lstat(), 'st_file_attributes', 0)&1024), 'No linked exported/imported directory')
    return path

def restore_exported_directories(source, manifest, service, worker):
    """Called only inside a new full-pair import before opening Native state."""
    source, service, worker = (_regular(Path(p)) for p in (source, service, worker))
    names = manifest.get('empty_directories_preserved', [])
    _require(isinstance(names, list) and len(names) == len(set(names)), 'Unique declared source directory list required')
    planned = []
    for name in names:
        _require(isinstance(name, str) and name and ':' not in name and '\\' not in name, 'Unsafe source directory')
        rel = PurePosixPath(name)
        _require(not rel.is_absolute() and all(p not in ('.', '..') for p in rel.parts), 'Directory escapes full pair')
        if rel.parts[0] == 'artefactos_trabajador': target = worker.joinpath(*rel.parts[1:])
        elif rel.parts[0] == 'resultados': target = service.joinpath(*rel.parts)
        else: raise ValueError('Only declared worker/result mappings are supported')
        _regular(target)
        if target.exists():
            _require(target.is_dir(), 'A directory name is occupied by a file')
            continue
        origin = _regular(source.joinpath(*rel.parts))
        _require(origin.is_dir(), 'Declared source directory absent')
        for child in origin.rglob('*'):
            _regular(child)
            _require(child.is_dir() and child.relative_to(source).as_posix() in names,
                     'Missing directory with file contents is an incomplete import, never silently recreated')
        planned.append((name, target))
    created = []
    for name, target in sorted(planned, key=lambda row: (len(row[1].parts), row[0])):
        _require(target.parent.is_dir(), 'Missing ancestor is not part of declared empty transport')
        target.mkdir(exist_ok=False)
        created.append(name)
    return {'version': VERSION, 'declared_directories': len(names), 'created_directories': created,
            'new_native_ticks': 0, 'files_written': 0, 'resource_contents_reconstructed': False,
            'before_native_import': True,
            'scope': 'Only empty source directories from the paired manifest; no checksum relaxation, physiology, policy, memory or metadata change.'}
