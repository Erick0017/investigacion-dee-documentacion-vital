# OPT-IN C02 launcher: material wait900s and independent admin wait600s.
# Same explicit preflight, official owner, aggregate ledger and cutoff00:05MXNov13.
"""R02 Root-only finite LIVE wiring. Importing this file starts/imports no DEE.

Run only after Studio authorization and an independently verified full import0.
The explicit destination, existing aggregate ledger and sealed cutoff are
mandatory. This launcher never creates/clones a world or selects the main life.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import re
import sys
import time

BASE = Path(__file__).resolve().parents[1]
PRODUCT = BASE.parents[2]
PRIVATE = BASE / 'configuracion_privada'
PROTECTED = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
LAST_NATIVE_CUTOFF = 1794738600  # 2026-11-15 10:30 UTC; R02 last newQ1 at10:00.
_PRESERVED_OWNER = None  # Retain owner after a drain timeout; never GC its Job.
_PRESERVED_BRIDGE = None


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def no_links(path):
    for part in (path, *path.parents):
        require(not part.is_symlink() and not (getattr(part.lstat(), 'st_file_attributes', 0) & 1024),
                'Explicit diagnostic path must not contain links/reparse points')


def load_stdlib_module(path, name):
    # Fixed named helpers are stdlib-only on import; no client-selected module path.
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_bridge():
    """Load only the fixed sibling bridge under isolated Python (-I)."""
    path = (BASE / 'puente/rbx02_bridge_C02.py').resolve(strict=True)
    no_links(path)
    name = 'rbx01_bridge'
    existing = sys.modules.get(name)
    if existing is not None:
        require(Path(getattr(existing, '__file__', '')).resolve() == path,
                'Unexpected preloaded bridge module path')
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, 'Fixed bridge loader unavailable')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        if sys.modules.get(name) is module:
            del sys.modules[name]
        raise
    require(Path(module.__file__).resolve() == path, 'Fixed bridge source path changed')
    return module


def validate_http_session_config(config):
    bridge = load_bridge()
    bridge.integer(config['sessionSeconds'], 30, 28800)
    bridge.integer(config['requestsPerMinute'], 1, 60)
    require(config.get('port') == 8895 and config.get('worldId') == 'RBX01_R05_C02_R02',
            'Only fixed R02 loopback/world configuration is permitted')
    require(type(config['ownerUserId']) is int and config['ownerUserId'] > 0,
            'A confirmed positive Roblox owner UserId is required')
    require(config['allowControl'] is False, 'LIVE runner cannot enable other adapters')


def preflight(destination, ledger_file, cutoff_epoch, config_path=None):
    """Read-only checks before any official owner or native dependency is opened."""
    bridge = load_bridge()
    destination = Path(destination).resolve(strict=True)
    require(destination.is_dir() and destination.parent == (BASE / 'native').resolve(),
            'Explicit existing destination must be immediately under RBX01/native')
    no_links(destination)
    context = read(destination / 'CONTEXTO_EJECUCION.json')
    system = destination / 'sistema'
    scope_file = system / 'capacidades/RBX02_NATIVE_SCOPE_C02_R02.json'
    scope = read(scope_file)
    imported = read(destination / 'IMPORTACION_DIAGNOSTICA.json')
    code_scope_file = BASE / 'protocolo/CODE_SCOPE_C02_R02.json'
    code_scope = read(code_scope_file)
    require(code_scope.get('schema') == 'DEE.RBX01.CODE_SCOPE_C02_R02' and code_scope.get('sealed') is True and hashlib.sha256(code_scope_file.read_bytes()).hexdigest() == scope.get('code_scope_manifest_sha256'), 'Common C02 source law changed after preparation')
    for relative, expected in code_scope['source_files_sha256'].items():
        source = BASE / relative
        no_links(source)
        require(source.resolve(strict=True).is_relative_to(BASE) and hashlib.sha256(source.read_bytes()).hexdigest() == expected, 'Frozen C02 source changed: ' + relative)
    require(context.get('schema') == 'DEE.RBX01.official_import_context.R01' and
            Path(context['system']).resolve(strict=True) == system,
            'Exact existing diagnostic execution context required')
    life = context['life']
    require(isinstance(life, str) and life != PROTECTED and life.endswith('_RBX01_C02_MAIN_R02') and
            re.fullmatch(r'ECI02_[A-Z0-9_]+_RBX01_C02_[A-Z0-9_]{1,40}', life),
            'Only the explicit RBX descendant may be opened')
    require(not (system / 'estado/ACTIVO.json').exists(), 'A selected/main system is prohibited')
    require(scope.get('schema') == 'DEE.RBX01.fixed_native_scope.C02.R02' and scope.get('sealed') is True and scope.get('life_id') == life and scope.get('max_cycles') == 48 and scope.get('max_ticks_per_cycle') == 4096 and scope.get('max_total_ticks') == 200000 and scope.get('max_raw_support') == 10000 and scope.get('monitor_tick_block') == 16 and scope.get('max_permission_stock') == 200, 'Finite C02 Native scope required')
    require(type(cutoff_epoch) in (float, int) and
            time.time() < cutoff_epoch <= LAST_NATIVE_CUTOFF and
            cutoff_epoch == scope['native_cutoff_utc_epoch'],
            'Explicit cutoff must match the sealed finite Native scope')
    require(imported.get('new_native_ticks') == 0 and imported.get('life') == life and
            imported.get('comparison', {}).get('physical_equal') is True and
            imported.get('comparison', {}).get('causal_prefix_equal') is True,
            'A complete coherent zero-tick official import0 is required')
    import0 = load_stdlib_module(BASE / 'native/rbx02_import0_C02_R02.py', '_RBX01_live_closed_check')
    require(import0.closed(destination),
            'Import0 owner, queue, WAL/journal and locks must be coherently closed')
    pins = scope.get('sources_sha256', {})
    require(set(pins) == {'rbx02_native_C02.py', 'rbx02_identity_C02.py', 'c02_funciones_native.py'}, 'Exact pinned Native source pair required')
    for name, expected in pins.items():
        require(hashlib.sha256((system / 'capacidades' / name).read_bytes()).hexdigest() == expected,
                'Sealed Native source changed')
    ledger_file = Path(ledger_file).resolve(strict=True)
    require(ledger_file.is_file() and ledger_file.is_relative_to(BASE),
            'An existing RBX01 aggregate ledger is mandatory; never reset its budget')
    no_links(ledger_file)
    ledger = read(ledger_file)
    require(ledger.get('schema') == 'DEE.RBX01.C02.prospective_native_budget.R01' and
            ledger.get('limit') == 200000 and ledger.get('max_worlds') == 6 and
            ledger.get('intent') is None,
            'Finite aggregate ledger with no unresolved Native intent required')
    config, _token = bridge.load_private_config(config_path)
    validate_http_session_config(config)
    database = config['databaseFile']
    if database.exists():
        import sqlite3
        con = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
        try:
            exists = con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='session'").fetchone()
            row=con.execute('SELECT status FROM session LIMIT 1').fetchone() if exists else None
            require(row is None or (config.get('resumeAllowed') is True and row[0]=='SUSPENDED_BOUNDARY'), 'Existing session requires explicit bound C02 resume')
        finally:
            con.close()
    return destination, ledger_file, cutoff_epoch, life


def run(destination, ledger_file, cutoff_epoch, config_path=None):
    """Explicit material launcher; Root alone invokes this after authorization."""
    global _PRESERVED_OWNER, _PRESERVED_BRIDGE
    bridge = load_bridge()
    destination, ledger_file, cutoff_epoch, life = preflight(
        destination, ledger_file, cutoff_epoch, config_path)
    support = load_stdlib_module(BASE / 'fuentes/rbx02_owner_support_C02_R02.py', '_RBX01_live_owner_support')
    adapter_module = load_stdlib_module(BASE / 'native/rbx02_adapter_C02_R02.py', '_RBX01_live_adapter')
    require(support.LIMIT == 512 * 1024 * 1024, 'Official512MiB owner limit must be unchanged')
    owner = support.configured_owner(PRODUCT, destination, ledger_file,
                                     tag='RBX01_C02_R02_LIVE', cutoff_epoch=cutoff_epoch, continuous=True)
    entered = False
    try:
        owner.__enter__()
        entered = True
        adapter = adapter_module.create_adapter({'owner': owner})
        require(adapter.identity == 'LIVE_NATIVE' and adapter.public_life_id == life,
                'Live adapter must expose the verified explicit descendant')
        bridge.serve(adapter, config_path=config_path)
    except bridge.BridgeDrainTimeout as error:
        # A `with owner:` would close it while its material worker still runs.
        # Retain both objects and propagate a clear preserved-future failure.
        # The worker is non-daemon; the configured owner also has a finite
        # horizon and Native cutoff. No experience or action is retried here.
        _PRESERVED_OWNER, _PRESERVED_BRIDGE = owner, error.bridge
        print(json.dumps({'status': 'HOST_SHUTDOWN_DRAIN_TIMEOUT', 'lifeId': life,
                          'ownerClosed': False, 'databaseClosed': False,
                          'noAutomaticRetry': True, 'reconciliationRequired': True}))
        raise
    except BaseException:
        if entered or getattr(owner, 'proc', None) is not None:
            owner.__exit__(*sys.exc_info())
        raise
    else:
        owner.__exit__(None, None, None)
        return {'status': 'CLOSED', 'lifeId': life, 'ownerClosed': True,
                'writerDrained': True, 'promoted': False}


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--ledger', type=Path, required=True)
    parser.add_argument('--native-cutoff-utc-epoch', type=float, required=True)
    parser.add_argument('--config', type=Path, default=None,
                        help='Existing bridge JSON inside configuracion_privada only')
    return parser


if __name__ == '__main__':
    args = build_parser().parse_args()
    print(json.dumps(run(args.destination, args.ledger, args.native_cutoff_utc_epoch,
                         args.config), ensure_ascii=False, indent=2))
