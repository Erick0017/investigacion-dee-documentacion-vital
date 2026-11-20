"""Prepared Root-only import0 for ONE private SDK identity, never a T0 world.

Importing this module and --help are stdlib-only. Actual execution loads the
official private Store/import_pair under the parent's bounded native Job.
No owner, Studio connection or autonomous Native advance is started here.
No R07 source is imported. Failures/partial identities are never retried.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time

ROOT = Path(__file__).resolve().parents[3]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def import0(home, runtime=ROOT, *, execute_root_only=False, context_sha256=None,
            deadline_utc_epoch=None, validation_campaign=False):
    if execute_root_only is not True:
        raise ValueError('EXPLICIT_ROOT_ONLY_MATERIAL_IMPORT0')
    runtime = Path(runtime).absolute(); home = Path(home).absolute()
    helper = load(Path(__file__).with_name('preparar_instancia_par28_sdk.py'), '_sdk_private_fs_preparer')
    now = time.time()
    helper.need(type(deadline_utc_epoch) in (int, float) and math.isfinite(deadline_utc_epoch) and
                now < deadline_utc_epoch <= now + 21600, 'EXPLICIT_FINITE_IMPORT0_DEADLINE')
    c = helper.resolve_context(home, runtime); system = Path(c['system']); life = c['life']
    helper.need(context_sha256 is not None and helper.hash_file(home / 'CONTEXTO_EJECUCION.json') == context_sha256,
                'EXACT_REVIEWED_PREPARATION_CONTEXT')
    cfg = helper.read(home / 'INSTANCE.json'); limits, budget_sha = helper.window(runtime)
    helper.need(budget_sha == c['budget_sha256'], 'SAME_FROZEN_SDK_MECHANICAL_BOUNDS')
    if validation_campaign:
        deadline_utc_epoch = min(deadline_utc_epoch, limits['hardFinishUtcEpoch'])
        helper.need(limits['startUtcEpoch'] <= now < deadline_utc_epoch, 'VALIDATION_CAMPAIGN_IMPORT0_WINDOW')
    helper.need(helper.hash_file(Path(c['template_manifest'])) == c['template_manifest_sha256'], 'TEMPLATE_CHANGED')
    template = helper.read(Path(c['template_manifest']))
    code_rows = helper.member_rows(template['members'], template=True)
    system_guard = helper.Guard(system)
    for name in ('app/lives.py', 'app/native_tools.py', 'app/importacion_emparejada.py', 'app/process_control.py'):
        helper.need(helper.hash_file(system_guard.path(name)) == code_rows[name]['sha256'],
                    'PREPARED_OFFICIAL_IMPORT_CODE_CHANGED:' + name)
    system_guard.recheck()
    helper.need(helper.hash_file(Path(c['prefix']) / 'EXPORTACION_SERVICIO.json') == c['prefix_manifest_sha256'],
                'ORIGINAL_COMPLETE_PREFIX_CHANGED')
    helper.need(cfg['sequenceOffset'] == 56 and cfg['runtimeVersion'] == '0.1.1', 'INHERITED_SEQUENCE_NOT_T0')
    for name in ('PREPARACION_EN_CURSO.json', 'PREPARACION_INCOMPLETA.json', 'IMPORT0_EN_CURSO.json',
                 'IMPORT0_INCOMPLETO.json', 'IMPORTACION_DIAGNOSTICA.json', 'SDK_READY.json'):
        helper.need(not (home / name).exists(), 'NO_RETRY_OR_EXISTING_IMPORT:' + name)
    helper.need(not (system / 'estado/ACTIVO.json').exists() and
                (not (system / 'estado/vidas').exists() or not any((system / 'estado/vidas').iterdir())) and
                (not (system / 'estado/servicios_persistentes').exists() or
                 not any((system / 'estado/servicios_persistentes').iterdir())), 'EMPTY_UNSELECTED_PRIVATE_SYSTEM_ONLY')
    helper.need(not (system / 'estado/locks' / (life + '.lock')).exists(), 'NO_NATIVE_WRITER')
    for pin in c['tool_sources']:
        helper.need(helper.hash_file(Path(pin['file'])) == pin['sha256'], 'PINNED_OFFICIAL_TOOL_CHANGED')
    observer_paths = [Path(row['file']) for row in c['tool_sources'] if Path(row['file']).name == 'observador_pasivo.py']
    helper.need(len(observer_paths) == 1, 'EXACT_OFFICIAL_PASSIVE_OBSERVER')
    helper.need(helper.hash_file(Path(c['source_world'])) == c['source_world_sha256'], 'WORLD_ANCHOR_CHANGED')
    helper.need(helper.hash_file(Path(c['source_record'])) == c['source_record_sha256'], 'PARENT_CARD_ANCHOR_CHANGED')
    parent = helper.read(Path(c['source_record']))
    helper.need(parent['life_id'] == helper.SOURCE and parent['snapshot_sha256'] == helper.SNAPSHOT and
                parent['physical']['N'] == 67 and parent['physical']['tick'] == 991187, 'EXACT_PARENT_CARD')
    # Never permit an already-imported app from a research or selected root.
    for name, module in list(sys.modules.items()):
        if name == 'app' or name.startswith('app.'):
            origin = getattr(module, '__file__', None)
            helper.need(origin is not None and Path(origin).resolve().is_relative_to(system), 'FOREIGN_APP_MODULE_ALREADY_LOADED')
    marker = home / 'IMPORT0_EN_CURSO.json'
    helper.new_json(marker, {'schema': helper.SCHEMA, 'lifeId': life, 'new_native_ticks': 0,
                            'automatic_retry': False, 'phase': 'BEFORE_OFFICIAL_IMPORT'})
    try:
        sys.dont_write_bytecode = True
        sys.path[:0] = c['import_paths']
        native_spec = importlib.util.find_spec('dee_thinking')
        helper.need(native_spec is not None and native_spec.origin is not None and
                    Path(native_spec.origin).resolve().is_relative_to(runtime), 'PRIVATE_PACKAGED_NATIVE_DEPENDENCY_ONLY')
        from app import process_control as pc
        resources = pc.protect_current(memory_limit=536870912)
        helper.need(isinstance(resources, dict) and resources['job_memory_limit'] == 536870912,
                    'EFFECTIVE_IMPORT0_JOB_512_MIB_REQUIRED')
        import dee_thinking as native
        helper.need(Path(native._native.__file__).resolve().is_relative_to(runtime), 'PRIVATE_NATIVE_BINARY_ONLY')
        from app.lives import Store
        from app.importacion_emparejada import import_pair
        from app.native_tools import atomic_json
        observer = load(observer_paths[0], '_sdk_official_passive_snapshot_observer')
        store = Store(system)
        result = import_pair(store, Path(c['prefix']), life)
        record = store.record(life); initial = record['snapshot_sha256']
        with store.writer(record['world_id']):
            record, adapter = store.load(life)
            record['parent'] = {'life_id': c['source_life_id'], 'snapshot_sha256': c['source_snapshot_sha256'],
                'tick': c['source_tick'], 'historical_parent': parent.get('parent'),
                'source_pair_manifest_sha256': c['prefix_manifest_sha256']}
            record = store.commit(record, adapter, {'kind': 'SDK_BIND_COMPLETE_PAR28_LINEAGE',
                'new_native_ticks': 0, 'parent_life_id': c['source_life_id'], 'parent_tick': 991187,
                'no_cognitive_content_written': True}, activate=False)
        snapshot = Path(c['system']) / record['snapshot']
        helper.need(snapshot.resolve().is_relative_to(system / 'estado'), 'IMPORTED_SNAPSHOT_INSIDE_PRIVATE_STATE')
        comparison = observer.compare_native(observer.snapshot_view(Path(c['prefix']) / 'VIDA.deetsnap.gz'),
                                              observer.snapshot_view(snapshot))
        helper.need(comparison['physical_equal'] is True and comparison['causal_prefix_equal'] is True and
                    record['physical']['N'] == 67 and record['physical']['tick'] == 991187 and
                    not (system / 'estado/ACTIVO.json').exists(), 'EXACT_IMPORT0_NO_SELECTION_OR_ADVANCE')
        scaffold = helper.preserve_source_empty_directories(home, runtime)
        mapping = system / 'estado/servicios_persistentes' / life / 'IMPORTACION.json'
        value = helper.read(mapping); value.update(initial_imported_snapshot_sha256=initial,
            imported_snapshot_sha256=record['snapshot_sha256'], explicit_parent=record['parent'], lineage_binding_ticks=0)
        atomic_json(mapping, value)
        result.update(snapshot_sha256=record['snapshot_sha256'], physical=record['physical'], explicit_parent=record['parent'])
        proof = {'schema': helper.SCHEMA, 'result': result, 'comparison': comparison, 'new_native_ticks': 0,
                 'life': life, 'source_life_id': c['source_life_id'], 'source_tick': 991187,
                 'source_parent': c['prefix'], 'principal_selected': False, 'owner_opened': False,
                 'service_started': False, 'source_empty_directories': scaffold,
                 'native_job_resources': resources}
        helper.need(time.time() < deadline_utc_epoch, 'IMPORT0_DEADLINE_REACHED_PRESERVE_PARTIAL')
        diagnostic = home / 'IMPORTACION_DIAGNOSTICA.json'
        helper.new_json(diagnostic, proof)
        helper.new_json(home / 'SDK_READY.json', {'schema': helper.SCHEMA,
                        'instanceId': cfg['instanceId'], 'lifeId': life,
                        'physical_equal': True, 'causal_prefix_equal': True, 'new_native_ticks': 0,
                        'sourceProofFile': diagnostic.name, 'sourceProofSha256': helper.hash_file(diagnostic)})
        marker.unlink()
        return proof
    except BaseException as error:
        try:
            helper.new_json(home / 'IMPORT0_INCOMPLETO.json', {'schema': helper.SCHEMA, 'lifeId': life,
                            'error': repr(error), 'partial_preserved': True, 'automatic_retry': False})
        except BaseException:
            pass
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, default=ROOT)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument('--home', type=Path)
    destination.add_argument('--instance', help='SDK_DEMO_<16 uppercase hex>; never a life/principal path')
    parser.add_argument('--context-sha256', required=True)
    parser.add_argument('--deadline-utc-epoch', type=float, required=True,
                        help='Prospective finite import-only deadline; parent native Job enforces it while blocked')
    parser.add_argument('--validation-campaign', action='store_true')
    parser.add_argument('--execute-root-only', action='store_true')
    args = parser.parse_args()
    home = args.home
    if args.instance is not None:
        import re
        if re.fullmatch(r'SDK_DEMO_[0-9A-F]{16}', args.instance) is None:
            raise ValueError('EXACT_PRIVATE_SDK_INSTANCE_ID')
        home = args.runtime / 'estado_demo/instancias' / args.instance
    print(json.dumps(import0(home, args.runtime, execute_root_only=args.execute_root_only,
                             context_sha256=args.context_sha256, deadline_utc_epoch=args.deadline_utc_epoch,
                             validation_campaign=args.validation_campaign), ensure_ascii=False, indent=2))
