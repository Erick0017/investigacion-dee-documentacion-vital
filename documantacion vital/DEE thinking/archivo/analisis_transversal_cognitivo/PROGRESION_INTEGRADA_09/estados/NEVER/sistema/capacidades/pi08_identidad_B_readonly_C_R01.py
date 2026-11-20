"""Exact C-clone transport access to its inherited, frozen B dependencies.

Only a private Python namespace receives the identity adapter. The original
B/C scientific sources, Native state, metadata, clocks and episodes are intact.
B START/EP are denied; only B STATE/dependencies may validate inherited files.
"""
from pathlib import Path
import hashlib, importlib.util, json

VERSION = 'DEE.PI08.C.inherited_B_readonly_identity_transport.R01'
LIFE = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01'
SYSTEM_KEY = 'DEE.Cognitive.System.1.1.life.v1'
SOURCE_SHA = 'aebe20a4566046957b274b07b942a3843ab4b612a9214791ff38edeb6bc53480'
STATE = 'eci01-pi08-b-estado'
_PRIVATE = None


def require(ok, message):
    if not ok:
        raise ValueError(message)


def current(a):
    identity = json.loads(dict(a.world.runtime.snapshot_metadata_entries)[SYSTEM_KEY])
    require(identity.get('life_id') == LIFE and identity.get('profile') == 'fisica_directa'
            and int(a.world.runtime.dimension) == 67, 'Only the sealed exact C diagnostic identity, N67 fisica_directa')
    active = Path(__file__).resolve().parents[1] / 'estado/ACTIVO.json'
    require(not active.exists(), 'C transport adapter refuses any selected/ACTIVO system')
    return identity


def component(a, research_component):
    global _PRIVATE
    current(a)
    source = Path(research_component.__file__)
    require(hashlib.sha256(source.read_bytes()).hexdigest() == SOURCE_SHA, 'Literal sealed scientific B source changed')
    seal = json.loads(Path(research_component.SEAL).read_text('utf-8-sig'))
    require(seal.get('additional_readonly_life_ids') == [LIFE], 'C readonly identity must already be prospectively sealed')
    if _PRIVATE is None:
        spec = importlib.util.spec_from_file_location('capacidades._PI08_C_inherited_B_readonly_transport_R01', source)
        private = importlib.util.module_from_spec(spec); spec.loader.exec_module(private)
        original_validate = private.validate
        original_code_files = private.code_files
        private._identity = current

        def validate(a, row):
            current(a)
            require(row == {'modo': STATE}, 'C clone may only read B STATE/dependencies; B START/EP are forbidden')
            return original_validate(a, row)

        private.validate = validate
        private.code_files = lambda: list(dict.fromkeys([Path(__file__), *original_code_files()]))
        _PRIVATE = private
    return _PRIVATE


def scope():
    return {'version': VERSION, 'life_id': LIFE, 'B_source_sha256': SOURCE_SHA,
            'B_material_modes_allowed': False, 'actual_SYSTEM_identity_is_returned_unchanged': True,
            'identity_override_only_in_private_namespace': True, 'Native_inputs_or_state_modified': False}
