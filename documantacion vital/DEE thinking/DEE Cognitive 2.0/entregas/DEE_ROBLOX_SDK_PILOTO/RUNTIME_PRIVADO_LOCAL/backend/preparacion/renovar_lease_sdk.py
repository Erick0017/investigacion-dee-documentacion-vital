"""Prepared SDK lease transaction. No Native/SQLite work at import or --help.

stage is closed-only inspection plus small critical backups. apply is explicit
Root-only official Store.commit at zero ticks. Native data is never rolled back
or retried automatically. Only LEASE metadata and the exactly specified official
SYSTEM_KEY administrative commit fields may change. Parent publication registers
the lease and updates the closed pair/scopes; the transaction marker remains
until that callback completes. This file never executes an operating episode.
"""
from pathlib import Path
import argparse
import copy
import datetime
import hashlib
import importlib.util
import json
import os
import re
import sys
import time

RUNTIME = Path(__file__).resolve().parents[2]
SCHEMA = 'DEE.Roblox.SDK.operational_lease.0.1.0'
LEASE_KEY = 'DEE.Cognitive.Roblox.SDK.LEASE.0.1.0'
ACTOR_KEY = 'DEE.Cognitive.Roblox.SDK.native.0.1.0'
SYSTEM_KEY = 'DEE.Cognitive.System.1.1.life.v1'
MUTABLE_SCOPE = {'native_cutoff_utc_epoch', 'last_new_cycle_utc_epoch', 'operational_lease'}
FIELDS = {'schema', 'leaseId', 'instanceId', 'lifeId', 'sessionId', 'startUtcEpoch',
          'lastNewUtcEpoch', 'hardFinishUtcEpoch', 'additionalCycles', 'startingCompletedCycles',
          'startingConsumedTicks', 'cumulativeCycleCap', 'validationCampaign', 'validationCampaignSha256'}


def need(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def helpers(runtime):
    fs = load(Path(__file__).with_name('preparar_instancia_par28_sdk.py'), '_sdk_lease_fs')
    sys.path.insert(0, str(Path(runtime) / 'backend'))
    common = load(Path(runtime) / 'backend/sdk_common.py', '_sdk_lease_common')
    return fs, common


def validate_lease(lease, cfg, *, now=None, campaign=None, campaign_sha=None):
    need(isinstance(lease, dict) and set(lease) == FIELDS and lease['schema'] == SCHEMA, 'EXACT_LEASE_DTO')
    need(re.fullmatch(r'SDK_LEASE_[0-9A-F]{16}', lease['leaseId']) is not None, 'FINITE_LEASE_ID')
    for key in ('instanceId', 'lifeId', 'sessionId'):
        need(lease[key] == cfg[key], 'SAME_SDK_IDENTITY:' + key)
    for key in ('startUtcEpoch', 'lastNewUtcEpoch', 'hardFinishUtcEpoch', 'additionalCycles',
                'startingCompletedCycles', 'startingConsumedTicks', 'cumulativeCycleCap'):
        need(type(lease[key]) is int, 'EXACT_LEASE_INTEGER:' + key)
    need(0 <= lease['startingCompletedCycles'] < 3 and 0 <= lease['startingConsumedTicks'] <= 40000 and
         1 <= lease['additionalCycles'] <= 3 and
         lease['cumulativeCycleCap'] == lease['startingCompletedCycles'] + lease['additionalCycles'] <= 3,
         'NO_COUNTER_RESET_OR_EXTRA_LIFETIME_CYCLES')
    need(lease['startUtcEpoch'] < lease['lastNewUtcEpoch'] < lease['hardFinishUtcEpoch'] and
         lease['hardFinishUtcEpoch'] - lease['startUtcEpoch'] <= 21600, 'FINITE_PROSPECTIVE_LEASE')
    when = time.time() if now is None else now
    need(lease['startUtcEpoch'] <= when < lease['lastNewUtcEpoch'], 'PROSPECTIVE_LEASE_ADMISSION')
    need(type(lease['validationCampaign']) is bool, 'EXPLICIT_VALIDATION_MODE')
    if lease['validationCampaign']:
        need(isinstance(lease['validationCampaignSha256'], str) and
             re.fullmatch(r'[0-9a-f]{64}', lease['validationCampaignSha256']) is not None and
             campaign is not None and lease['validationCampaignSha256'] == campaign_sha and
             lease['startUtcEpoch'] >= campaign['startUtcEpoch'] and
             lease['lastNewUtcEpoch'] <= campaign['lastNewUtcEpoch'] and
             lease['hardFinishUtcEpoch'] <= campaign['hardFinishUtcEpoch'], 'VALIDATION_CAMPAIGN_CLIP')
    else:
        need(lease['validationCampaignSha256'] is None, 'NO_PRODUCT_EXPIRY_FROM_OLD_CAMPAIGN')
    return copy.deepcopy(lease)


def check_metadata(before, after, old_system, new_system, lease, old_snapshot_sha):
    """Root-authorized exact SYSTEM commit delta; no other metadata exception."""
    need(after.get(LEASE_KEY) == canonical(lease), 'EXACT_CANONICAL_NATIVE_LEASE')
    left = {k: v for k, v in before.items() if k not in (LEASE_KEY, SYSTEM_KEY)}
    right = {k: v for k, v in after.items() if k not in (LEASE_KEY, SYSTEM_KEY)}
    need(left == right, 'OTHER_METADATA_OR_ACTOR_COUNTERS_CHANGED')
    expected = copy.deepcopy(old_system)
    need(type(expected['operation_count']) is int, 'EXACT_OLD_OPERATION_COUNT')
    expected['operation_count'] += 1
    expected['previous_checkpoint_sha256'] = old_snapshot_sha
    need(new_system == expected, 'SYSTEM_COMMIT_DELTA_EXCEEDS_ROOT_AUTHORIZATION')


def require_new_import0(cfg, card, view, cycles, ready, source_proof_sha, prefix_sha, expected_prefix_sha):
    """Pure NEW-only guard; no Agent World/pair is invented by the backend."""
    need(card['physical']['N'] == 67 and card['physical']['tick'] == 991187 and cfg['nativeTick'] == 991187 and
         cfg['sequenceOffset'] == 56 and cfg['localSequence'] == cfg['completedCycles'] == cycles == 0 and
         ACTOR_KEY not in view['metadata'] and ready['physical_equal'] is True and
         ready['causal_prefix_equal'] is True and ready['new_native_ticks'] == 0 and
         source_proof_sha == ready['sourceProofSha256'] and prefix_sha == expected_prefix_sha,
         'NEW_ONLY_CLOSED_ORIGINAL_IMPORT0_NO_AGENT_WORLD')


def _view(fs, c, snapshot):
    rows = [p for p in c['tool_sources'] if Path(p['file']).name == 'observador_pasivo.py']
    need(len(rows) == 1 and fs.hash_file(Path(rows[0]['file'])) == rows[0]['sha256'], 'EXACT_OFFICIAL_OBSERVER')
    observer = load(Path(rows[0]['file']), '_sdk_lease_passive_observer')
    return observer.snapshot_view(snapshot)


def _closed(fs, common, home, cfg, c):
    need(not (home / 'sistema/estado/ACTIVO.json').exists(), 'NO_SELECTED_SYSTEM')
    for marker in ('PREPARACION_EN_CURSO.json', 'PREPARACION_INCOMPLETA.json', 'IMPORT0_EN_CURSO.json', 'IMPORT0_INCOMPLETO.json'):
        need(not (home / marker).exists(), 'UNFINISHED_INSTANCE_PRESERVED:' + marker)
    proof = common.closed_native(home, cfg)
    need(proof['writerClosed'] is True and proof['pending'] == 0, 'CLOSED_DATABASE_NO_WRITER_OR_PENDING')
    system = Path(c['system']); card = fs.read(system / 'estado/vidas' / cfg['lifeId'] / 'VIDA.json')
    snapshot = fs.Guard(system).path(card['snapshot'])
    view = _view(fs, c, snapshot); own = view['metadata'].get(ACTOR_KEY)
    if own is None:
        need(card['physical']['tick'] == 991187, 'ABSENT_ACTOR_ONLY_ORIGINAL_IMPORT0')
        cycles = 0
    else:
        m = json.loads(own)
        need(m['phase'] == 'IDLE' and m['pending'] is None and m['uncertain'] is False and
             type(m['cycles']) is int and type(m['last_sequence']) is int, 'ACTOR_NOT_CLOSED_IDLE')
        need(m['last_sequence'] == cfg['sequenceOffset'] + cfg['localSequence'], 'EXACT_NATIVE_LOCAL_SEQUENCE_OFFSET')
        cycles = m['cycles']
    need(cycles == cfg['completedCycles'] and cfg['nativeTick'] == card['physical']['tick'], 'EXACT_CLOSED_INSTANCE_CURSOR')
    need(not (system / 'estado/vidas' / cfg['lifeId'] / 'FUTURO_INTERRUMPIDO.json').exists(), 'NO_INTERRUPTED_NATIVE_FUTURE')
    return proof, card, snapshot, view, cycles


def stage(home, lease, runtime=RUNTIME, *, execute_root_only=False):
    need(execute_root_only is True, 'ROOT_ONLY_LEASE_STAGE')
    runtime = Path(runtime).absolute(); home = Path(home).absolute(); fs, common = helpers(runtime)
    c = fs.resolve_context(home, runtime); cfg = fs.read(home / 'INSTANCE.json')
    campaign, campaign_sha = fs.window(runtime)
    lease = validate_lease(lease, cfg, campaign=campaign, campaign_sha=campaign_sha)
    need(not (home / 'SDK_LEASE_IN_PROGRESS.json').exists(), 'NO_OTHER_OR_PARTIAL_LEASE_TX')
    proof, card, snapshot, view, cycles = _closed(fs, common, home, cfg, c)
    need(cycles == lease['startingCompletedCycles'], 'LEASE_STARTS_FROM_ACTUAL_ACTOR_COUNTER')
    ledger = fs.Guard(runtime).path('estado_demo/LEDGER_SDK.json'); ledger_value = fs.read(ledger)
    need(ledger_value['intents'] == {}, 'NO_LEDGER_INTENTS')
    world = ledger_value['worlds'].get(cfg['lifeId'])
    if world is None:
        need(cycles == lease['startingConsumedTicks'] == 0, 'ONLY_UNUSED_WORLD_CAN_BE_ABSENT_FROM_LEDGER')
    else:
        need(world['cycles'] == cycles and world['consumed'] == lease['startingConsumedTicks'] and world['reserved'] == 0,
             'EXACT_LEDGER_COUNTER_BASELINE')
    scope = home / 'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json'
    host = home / 'sistema/app/HOST_INTEGRAL_V3.json'
    pair = home / 'SDK_PAIR.json'; has_pair = pair.exists(); pair_value = fs.read(pair) if has_pair else None
    if has_pair:
        need(pair_value['instanceId'] == cfg['instanceId'] and pair_value['sessionId'] == cfg['sessionId'] and
             pair_value['localSequence'] == cfg['localSequence'] and
             all(pair_value['native'].get(k) == v for k, v in proof.items()) and
             pair_value['backendProof']['backendWriterClosed'] is True and
             pair_value['backendProof']['bridgeQuiescent'] is True, 'CLOSED_SAME_SESSION_PAIR')
    else:
        ready = fs.read(home / 'SDK_READY.json')
        require_new_import0(cfg, card, view, cycles, ready, fs.hash_file(home / 'IMPORTACION_DIAGNOSTICA.json'),
                            fs.hash_file(Path(c['prefix']) / 'EXPORTACION_SERVICIO.json'), fs.EXPORT_SHA)
    tx_rel = 'leases/' + lease['leaseId']; tx = fs.Guard(home).path(tx_rel, exists=False)
    need(not os.path.lexists(tx), 'NEW_TX_ONLY_NO_RETRY')
    tx.mkdir(parents=True)
    paths = {'snapshot': snapshot, 'card': home / 'sistema/estado/vidas' / cfg['lifeId'] / 'VIDA.json',
             'context': home / 'CONTEXTO_EJECUCION.json', 'instance': home / 'INSTANCE.json',
             'scope': scope, 'host': host, 'ledger': ledger,
             'source_world': Path(c['source_world']), 'source_record': Path(c['source_record']),
             'history': home / 'sistema/estado/vidas' / cfg['lifeId'] / 'HISTORIA.jsonl'}
    if has_pair: paths['pair'] = pair
    try:
        pins = {}; backup = tx / 'before'; backup.mkdir()
        for key, path in paths.items():
            rel = path.relative_to(runtime).as_posix(); p = fs.Guard(runtime).path(rel)
            row = {'bytes': p.stat().st_size, 'sha256': fs.hash_file(p)}
            fs.copy_checked(rel, key + '.bin', row, fs.Guard(runtime), fs.Guard(backup))
            pins[key] = {'path': rel, **row}
        again = _closed(fs, common, home, cfg, c)
        need(again[0] == proof and again[3] == view, 'CLOSED_STATE_CHANGED_DURING_STAGE')
        plan = {'schema': SCHEMA, 'home': home.relative_to(runtime).as_posix(), 'lease': lease,
                'pins': pins, 'closedProof': proof, 'actorCycles': cycles,
                'snapshotView': view, 'instance': cfg, 'scope': fs.read(scope), 'host': fs.read(host),
                'hasPair': has_pair, 'pair': pair_value, 'ledgerSha256': pins['ledger']['sha256'],
                'administrativeOperation': {'kind': 'SDK_OPERATIONAL_LEASE_ADMIN', 'leaseId': lease['leaseId'],
                                          'new_native_ticks': 0, 'classification': 'external_administrative_lease'}}
        fs.new_json(tx / 'PLAN.json', plan)
        fs.new_json(home / 'SDK_LEASE_IN_PROGRESS.json', {'leaseId': lease['leaseId'], 'tx': tx_rel,
                                                       'phase': 'STAGED_NO_NATIVE_MUTATION'})
        return {'status': 'STAGED_NO_NATIVE_MUTATION', 'transaction': str(tx), 'txPath': str(tx),
                'planPath': str(tx / 'PLAN.json'), 'planSha256': fs.hash_file(tx / 'PLAN.json')}
    except BaseException as error:
        try: fs.new_json(tx / 'INCOMPLETE_PRESERVED.json', {'error': repr(error), 'automatic_retry': False})
        except BaseException: pass
        raise


def apply(tx, expected_plan_sha256, runtime=RUNTIME, *, execute_root_only=False, finalize=None):
    need(execute_root_only is True, 'ROOT_ONLY_NATIVE_LEASE_COMMIT')
    runtime = Path(runtime).absolute(); tx = Path(tx).absolute(); fs, common = helpers(runtime)
    fs.Guard(runtime).path(tx.relative_to(runtime).as_posix())
    need(fs.hash_file(tx / 'PLAN.json') == expected_plan_sha256, 'EXACT_ROOT_REVIEWED_PLAN')
    p = fs.read(tx / 'PLAN.json'); home = fs.Guard(runtime).path(p['home'])
    need(tx == home / 'leases' / p['lease']['leaseId'], 'EXACT_PRIVATE_LEASE_TRANSACTION')
    need(not (tx / 'APPLY_INTENT.json').exists(), 'NO_PARTIAL_NATIVE_RETRY')
    marker = home / 'SDK_LEASE_IN_PROGRESS.json'; marker_value = fs.read(marker)
    need(marker_value['leaseId'] == p['lease']['leaseId'], 'OWN_STAGED_LEASE_MARKER')
    c = fs.resolve_context(home, runtime); cfg = fs.read(home / 'INSTANCE.json')
    campaign, campaign_sha = fs.window(runtime)
    lease = validate_lease(p['lease'], cfg, campaign=campaign, campaign_sha=campaign_sha)
    for row in p['pins'].values():
        need(fs.hash_file(fs.Guard(runtime).path(row['path'])) == row['sha256'], 'STAGED_CRITICAL_FILE_CHANGED')
    before = _closed(fs, common, home, cfg, c)
    need(before[0] == p['closedProof'] and before[3] == p['snapshotView'], 'CLOSED_NATIVE_CHANGED_SINCE_STAGE')
    fs.new_json(tx / 'APPLY_INTENT.json', {'planSha256': expected_plan_sha256, 'leaseId': lease['leaseId'], 'new_native_ticks': 0})
    try:
        sys.dont_write_bytecode = True; sys.path[:0] = c['import_paths']
        for name, module in list(sys.modules.items()):
            if name == 'app' or name.startswith('app.'):
                origin = getattr(module, '__file__', None)
                need(origin is not None and Path(origin).resolve().is_relative_to(Path(c['system'])), 'FOREIGN_APP_MODULE')
        need(fs.hash_file(Path(c['template_manifest'])) == c['template_manifest_sha256'], 'PRIVATE_TEMPLATE_CHANGED')
        import_rows = fs.member_rows(fs.read(Path(c['template_manifest']))['members'], template=True)
        for name in ('app/lives.py', 'app/native_tools.py', 'app/importacion_emparejada.py'):
            need(fs.hash_file(fs.Guard(Path(c['system'])).path(name)) == import_rows[name]['sha256'], 'PRIVATE_APP_CODE_CHANGED')
        spec = importlib.util.find_spec('dee_thinking')
        need(spec is not None and spec.origin is not None and Path(spec.origin).resolve().is_relative_to(runtime), 'PRIVATE_NATIVE_PACKAGE_ONLY')
        import dee_thinking as native
        need(Path(native._native.__file__).resolve().is_relative_to(runtime), 'PRIVATE_NATIVE_BINARY_ONLY')
        from app.lives import Store
        from app.native_tools import decode_metadata
        system = Path(c['system']); store = Store(system); old_card = before[1]
        started = time.time()
        with store.writer(old_card['world_id']):
            record, adapter = store.load(cfg['lifeId'])
            old_entries = dict(adapter.world.runtime.snapshot_metadata_entries)
            need(old_entries == before[3]['metadata'], 'NATIVE_LOADER_METADATA_CHANGED')
            old_system = decode_metadata(old_entries[SYSTEM_KEY])
            adapter.world.runtime.set_snapshot_metadata(LEASE_KEY, canonical(lease))
            record = store.commit(record, adapter, p['administrativeOperation'], activate=False)
            new_entries = dict(adapter.world.runtime.snapshot_metadata_entries)
            check_metadata(old_entries, new_entries, old_system, decode_metadata(new_entries[SYSTEM_KEY]),
                           lease, old_card['snapshot_sha256'])
        after = _closed(fs, common, home, cfg, c)
        need(after[3]['physical'] == before[3]['physical'] and
             after[3]['causal_prefix_sha256'] == before[3]['causal_prefix_sha256'], 'PHYSICS_AGENDA_INTERFACES_RECEIPTS_CHANGED')
        need(after[0]['databaseSha256'] == before[0]['databaseSha256'], 'DATABASE_OR_INTENTS_CHANGED')
        new_card = after[1]
        need(time.time() < lease['hardFinishUtcEpoch'], 'LEASE_COMMIT_HARD_DEADLINE')
        allowed_card = {'updated_utc', 'operations', 'snapshot', 'snapshot_sha256', 'storage'}
        need({k: v for k, v in new_card.items() if k not in allowed_card} ==
             {k: v for k, v in old_card.items() if k not in allowed_card}, 'OTHER_CARD_IDENTITY_GENEALOGY_OR_COUNTER_CHANGED')
        need(new_card['operations'] == old_card['operations'] + [p['administrativeOperation']], 'EXACT_ADMIN_OPERATION_ONLY')
        stamp = datetime.datetime.fromisoformat(new_card['updated_utc']).timestamp()
        need(started <= stamp <= time.time() and not (system / 'estado/ACTIVO.json').exists(), 'EXACT_UNSELECTED_ADMIN_COMMIT')
        observer_row = next(row for row in c['tool_sources'] if Path(row['file']).name == 'observador_pasivo.py')
        observer = load(Path(observer_row['file']), '_sdk_lease_original_raw_comparison')
        try:
            raw_comparison = {'equal': True, 'result': observer.compare_native(before[3], after[3]),
                              'originalObserverUnmodified': True}
        except ValueError as error:
            raw_comparison = {'equal': False, 'error': str(error), 'originalObserverUnmodified': True}
        result = {'status': 'NATIVE_COMMITTED_PENDING_PUBLISH', 'lease': lease, 'newNativeProof': after[0],
                  'physical_equal': True, 'causal_prefix_equal': True, 'other_metadata_equal': True,
                  'observerRaw': raw_comparison,
                  'authorizedSystemDelta': {'operation_count': old_system['operation_count'] + 1,
                                            'previous_checkpoint_sha256': old_card['snapshot_sha256']},
                  'new_native_ticks': 0, 'sourcePlanSha256': expected_plan_sha256}
        fs.new_json(tx / 'NATIVE_COMMITTED_PENDING_PUBLISH.json', result)
        if finalize is None:
            return result
        publication = finalize(home, lease, after[0], p['ledgerSha256'], tx)
        scope = fs.read(home / 'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json')
        host = fs.read(home / 'sistema/app/HOST_INTEGRAL_V3.json')
        need({k: v for k, v in scope.items() if k not in MUTABLE_SCOPE} ==
             {k: v for k, v in p['scope'].items() if k not in MUTABLE_SCOPE}, 'SCOPE_MECHANISM_CHANGED')
        need(scope['operational_lease'] == lease and scope['last_new_cycle_utc_epoch'] == lease['lastNewUtcEpoch'] and
             scope['native_cutoff_utc_epoch'] == lease['hardFinishUtcEpoch'], 'EXACT_PUBLISHED_LEASE_SCOPE')
        need({k: v for k, v in host.items() if k != 'native_cutoff_utc_epoch'} ==
             {k: v for k, v in p['host'].items() if k != 'native_cutoff_utc_epoch'} and
             host['native_cutoff_utc_epoch'] == lease['hardFinishUtcEpoch'], 'HOST_ONLY_DEADLINE_CHANGE')
        if p['hasPair']:
            pair = fs.read(home / 'SDK_PAIR.json')
            need(pair['snapshot'] == p['pair']['snapshot'] and pair['snapshotSha256'] == p['pair']['snapshotSha256'],
                 'WORLD_LITERAL_CHANGED')
        else:
            need(not (home / 'SDK_PAIR.json').exists(), 'NEW_MUST_NOT_FABRICATE_AGENT_WORLD')
        cfg_after = fs.read(home / 'INSTANCE.json')
        need(all(cfg_after[k] == cfg[k] for k in ('instanceId', 'lifeId', 'sessionId', 'localSequence',
                                                 'nextPhase', 'nativeTick', 'completedCycles')),
             'INSTANCE_COUNTER_OR_IDENTITY_RESET')
        result['status'] = 'LEASE_PUBLISHED_CLOSED_0TICKS'; result['publication'] = publication
        fs.new_json(tx / 'RESULTADO.json', result)
        marker.unlink()
        return result
    except BaseException as error:
        try: fs.new_json(tx / 'INCOMPLETE_PRESERVED.json', {'error': repr(error), 'automatic_retry': False, 'native_rollback': False})
        except BaseException: pass
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, default=RUNTIME)
    parser.add_argument('--execute-root-only', action='store_true')
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--stage', type=Path, metavar='INSTANCE_HOME')
    action.add_argument('--apply', type=Path, metavar='TRANSACTION')
    parser.add_argument('--lease-json', type=Path); parser.add_argument('--plan-sha256')
    args = parser.parse_args()
    if args.stage:
        if args.lease_json is None: parser.error('--stage requires --lease-json')
        value = stage(args.stage, json.loads(args.lease_json.read_text('utf8')), args.runtime,
                      execute_root_only=args.execute_root_only)
    else:
        if args.plan_sha256 is None: parser.error('--apply requires --plan-sha256')
        value = apply(args.apply, args.plan_sha256, args.runtime, execute_root_only=args.execute_root_only)
    print(json.dumps(value, ensure_ascii=False, indent=2))
