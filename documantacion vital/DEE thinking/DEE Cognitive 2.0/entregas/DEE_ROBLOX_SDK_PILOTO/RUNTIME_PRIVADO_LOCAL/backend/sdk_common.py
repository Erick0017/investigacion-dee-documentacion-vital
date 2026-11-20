"""Private SDK contracts. Stdlib only; import never creates a DEE world."""
from pathlib import Path
import hashlib
import json
import os
import re
import sqlite3
import time

SCHEMA = 'DEE.Roblox.SDK.private.0.1.0'
NATIVE_VERSION = 'DEE.Roblox.SDK.native.0.1.0'
RUNTIME = Path(__file__).resolve().parents[1]
INSTANCE = re.compile(r'SDK_DEMO_[0-9A-F]{16}')
LIFE_PREFIX = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'
IDENTIFIER = re.compile(r'[A-Za-z0-9_-]{1,90}')

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''): h.update(part)
    return h.hexdigest()

def digest(value):
    return hashlib.sha256(canonical(value).encode('utf8')).hexdigest()

def read(path):
    deadline = time.monotonic() + 2.0
    while True:
        try:
            return json.loads(Path(path).read_text('utf-8-sig'))
        except OSError as error:
            sharing = getattr(error, 'winerror', None) in (5, 32) or os.name == 'nt' and error.errno == 13
            if not sharing or time.monotonic() >= deadline:
                raise
            time.sleep(.02)  # Same passive read only; never re-admit an operation.

def safe(root, relative, *, exists=False):
    root = Path(root).resolve(strict=True)
    p = Path(relative)
    if p.is_absolute() or any(x in ('..', '.') for x in p.parts) or ':' in str(relative):
        raise ValueError('Relative contained path required')
    target = root / p
    cursor = root
    for part in p.parts:
        cursor = cursor / part
        if cursor.exists() or cursor.is_symlink():
            st = cursor.lstat()
            if cursor.is_symlink() or getattr(st, 'st_file_attributes', 0) & 1024:
                raise ValueError('Linked/reparse path prohibited')
    resolved = target.resolve(strict=exists)
    if not resolved.is_relative_to(root): raise ValueError('Escaped runtime')
    return resolved

def atomic(path, value, *, new=False):
    path = Path(path)
    if new and path.exists(): raise FileExistsError(path)
    tmp = path.with_name(path.name + '.WRITING')
    data = (canonical(value) + '\n').encode('utf8')
    with tmp.open('xb') as out:
        out.write(data); out.flush(); os.fsync(out.fileno())
    if new and path.exists(): raise FileExistsError(path)
    # Windows readers/antivirus can hold a destination without share-delete.
    # Retry only this SAME prepared rename, never the Native/HTTP operation.
    intended = hashlib.sha256(data).hexdigest()
    deadline = time.monotonic() + 2.0
    while True:
        try:
            os.replace(tmp, path)
            break
        except OSError as error:
            if getattr(error, 'winerror', None) not in (5, 32) or time.monotonic() >= deadline:
                raise  # .WRITING stays preserved; no material retry.
            if sha(tmp) != intended:
                raise RuntimeError('Prepared atomic bytes changed; preserve without retry') from error
            time.sleep(.02)

def instance_home(instance_id, runtime=RUNTIME):
    if not isinstance(instance_id, str) or INSTANCE.fullmatch(instance_id) is None:
        raise ValueError('Only fresh SDK_DEMO_<16HEXUPPER> diagnostic IDs')
    home = safe(runtime, 'estado_demo/instancias/' + instance_id, exists=True)
    if (home / 'sistema/estado/ACTIVO.json').exists():
        raise ValueError('Selected life prohibited')
    cfg = read(home / 'INSTANCE.json')
    if cfg.get('instanceId') != instance_id or cfg.get('lifeId') != LIFE_PREFIX + instance_id:
        raise ValueError('Diagnostic identity mismatch')
    return home, cfg

def budget(runtime=RUNTIME, now=None):
    p = safe(runtime, 'configuracion/VENTANA_CONGELADA.json', exists=True)
    c = read(p)
    required = {'schema', 'startUtcEpoch', 'lastNewUtcEpoch', 'hardFinishUtcEpoch',
                'maxNativeTicks', 'maxSdkCycles', 'ownerMemoryBytes', 'threads',
                'maxRawSupport', 'minimumHostFreeBytes', 'sealed'}
    if set(c) != required or c['schema'] != SCHEMA or c['sealed'] is not True:
        raise ValueError('Explicit prospective frozen SDK budget required')
    if not (c['startUtcEpoch'] < c['lastNewUtcEpoch'] < c['hardFinishUtcEpoch']
            and c['hardFinishUtcEpoch'] - c['startUtcEpoch'] <= 21600
            and c['maxNativeTicks'] == 40000 and c['maxSdkCycles'] == 3
            and c['ownerMemoryBytes'] == 536870912 and c['threads'] == 1
            and c['maxRawSupport'] == 10000 and c['minimumHostFreeBytes'] == 3758096384):
        raise ValueError('SDK prospective bounds changed')
    when = time.time() if now is None else now
    if when >= c['hardFinishUtcEpoch']: raise RuntimeError('SDK hard deadline reached')
    return c

def operational_window(cfg, runtime=RUNTIME, now=None):
    """Product session is finite; the campaign is an additional optional clip."""
    c = budget(runtime, now=0)
    lease = cfg.get('operationalLease')
    if not isinstance(lease, dict) or lease.get('schema') != 'DEE.Roblox.SDK.operational_lease.0.1.0':
        raise ValueError('Explicit start/continue operational lease required')
    if (lease.get('instanceId'), lease.get('lifeId'), lease.get('sessionId')) != (cfg['instanceId'], cfg['lifeId'], cfg['sessionId']):
        raise ValueError('Lease identity mismatch')
    if not (lease['startUtcEpoch'] < lease['lastNewUtcEpoch'] < lease['hardFinishUtcEpoch']
            and lease['hardFinishUtcEpoch'] - lease['startUtcEpoch'] <= 21600
            and 1 <= lease['additionalCycles'] <= 3
            and lease['cumulativeCycleCap'] == lease['startingCompletedCycles'] + lease['additionalCycles'] <= 3):
        raise ValueError('Finite demo lifetime/profile/session cap')
    if lease['validationCampaign']:
        if (lease['validationCampaignSha256'] != sha(Path(runtime) / 'configuracion/VENTANA_CONGELADA.json')
                or lease['lastNewUtcEpoch'] > c['lastNewUtcEpoch'] or lease['hardFinishUtcEpoch'] > c['hardFinishUtcEpoch']):
            raise ValueError('Current validation campaign clip required')
    when = time.time() if now is None else now
    if when >= lease['hardFinishUtcEpoch']: raise RuntimeError('Operational session has expired; explicit closed renewal required')
    return {**c, 'startUtcEpoch': lease['startUtcEpoch'], 'lastNewUtcEpoch': lease['lastNewUtcEpoch'],
            'hardFinishUtcEpoch': lease['hardFinishUtcEpoch']}

def closed_native(home, cfg):
    """Closed-only RO inspection; never opens a Native runtime."""
    system = home / 'sistema'; life = cfg['lifeId']
    if (system / 'estado/ACTIVO.json').exists() or (system / 'estado/locks' / (life + '.lock')).exists():
        raise RuntimeError('Selected/owned Native is not a closed instance')
    cardfile = system / 'estado/vidas' / life / 'VIDA.json'
    card = read(cardfile)
    db = system / 'estado/servicios_persistentes' / life / 'cola.sqlite3'
    for suffix in ('-wal', '-journal'):
        side = Path(str(db) + suffix)
        if side.exists() and side.stat().st_size: raise RuntimeError('Live/uncertain SQLite sidecar')
    con = sqlite3.connect(db.resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
    try:
        ownerrow = con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()
        owner = {} if ownerrow is None else json.loads(ownerrow[0])
        pending = con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]
        if owner.get('running') is True or pending: raise RuntimeError('Native writer/pending requests must be preserved')
    finally: con.close()
    snapshot = safe(system, card['snapshot'], exists=True)
    return {'lifeId': life, 'nativeTick': card['physical']['tick'], 'dimension': card['physical']['N'],
            'cardSha256': sha(cardfile), 'snapshotSha256': sha(snapshot),
            'databaseSha256': sha(db), 'writerClosed': True, 'pending': 0}

def native_payload(kind, payload, sequence_offset):
    """Translate only the declared local sequence; never sensors or answers."""
    result = json.loads(canonical(payload))
    fields = ('observationId', 'seq', 'phase', 'worldTimeMs', 'sampleTimeMs', 'previousActionId', 'sensors')
    def project(observation):
        if not isinstance(observation, dict) or any(k not in observation for k in fields if k != 'previousActionId'):
            raise ValueError('Complete actual connector observation required')
        # Lua nil is omitted by JSONEncode. The effective P08 driver used
        # get('previousActionId') too: absence is None, never a fabricated ID.
        return {k: observation.get(k) if k == 'previousActionId' else observation[k] for k in fields}
    if kind in ('decision', 'query_sensor'):
        if set(result) != {'observation'}: raise ValueError('Observation-only Native ABI')
        result['observation'] = project(result['observation'])
        o = result['observation']; local = o['seq']; observation_id = o['observationId']
        if type(local) is not int or not 1 <= local <= 6: raise ValueError('SDK local sequence bound')
        o['seq'] = sequence_offset + local
    elif kind == 'feedback':
        local = result['seq']; observation_id = result['observationId']
        if result['lastObservation']['seq'] != local: raise ValueError('Feedback sequence correlation')
        result['lastObservation'] = project(result['lastObservation'])
        result['seq'] = sequence_offset + local
        result['lastObservation']['seq'] = sequence_offset + local
    elif kind == 'function':
        raise ValueError('SDK 0.1 simple demo does not advertise function RPC')
    else: raise ValueError('Closed Native kind')
    return result, local, observation_id
