"""Pure mocks of identity/read-only/journal guards; no DEE imports or Native."""
from pathlib import Path
from types import SimpleNamespace as NS
import hashlib, importlib.util, json

P = Path(__file__).resolve().parents[1]; H = P / 'codigo'
S = P / 'estados/C_R03/sistema'
DEST = H / 'pruebas/C_IDENTIDAD_TRANSPORTE_R01'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def main():
    if DEST.exists(): raise ValueError('Fresh pure fixture only')
    (DEST / 'estado').mkdir(parents=True)
    adapter = load('pure_C_identity_adapter', H / 'pi08_identidad_B_readonly_C_R01.py')
    adapter.__file__ = str(DEST / 'capacidades/pi08_identidad_B_readonly_C_R01.py')
    research = load('pure_C_original_B', S / 'capacidades/pi08_revision_flexible_B_R01.py')
    identity_original = research._identity
    entries = {adapter.SYSTEM_KEY: json.dumps({'life_id': adapter.LIFE, 'profile': 'fisica_directa'})}
    a = NS(world=NS(runtime=NS(dimension=67, snapshot_metadata_entries=list(entries.items()))))
    checked = []

    def check(name, cond):
        if not cond: raise AssertionError(name)
        checked.append(name)

    def rejects(name, call):
        try: call()
        except ValueError: checked.append(name)
        else: raise AssertionError(name)

    b = adapter.component(a, research)
    check('literal_original_B_identity_not_modified', research._identity is identity_original)
    check('private_namespace_is_distinct', b is not research)
    check('actual_C_SYSTEM_identity_not_projected_to_REAL', b._identity(a)['life_id'] == adapter.LIFE)
    b.validate(a, {'modo': b.STATE}); checked.append('B_STATE_validation_allowed_without_Native')
    rejects('B_START_explicitly_forbidden', lambda: b.validate(a, {'modo': b.START}))
    rejects('B_EP_explicitly_forbidden', lambda: b.validate(a, {'modo': b.EPISODE}))
    rejects('B_dispatch_EP_forbidden_before_execution', lambda: b.dispatch(a, {'modo': b.EPISODE}, directory=DEST))
    for name, identity, dimension in [('another_life', 'OTHER', 67), ('wrong_dimension', adapter.LIFE, 66)]:
        fake = NS(world=NS(runtime=NS(dimension=dimension, snapshot_metadata_entries=[(adapter.SYSTEM_KEY, json.dumps({'life_id': identity, 'profile': 'fisica_directa'}))])))
        rejects(name+'_refused', lambda fake=fake: adapter.component(fake, research))
    active = DEST / 'estado/ACTIVO.json'; active.write_text('{}', encoding='utf8')
    rejects('any_selected_ACTIVO_refused', lambda: adapter.component(a, research))
    active.unlink()

    # Exercise the literal dependency validator with a minimal MOCK journal;
    # only the Native decoder/host directory accessors are replaced by fakes.
    rows = [{'ordinal': i} for i in range(12)]
    keys = ('MOCK.R01', 'MOCK.R02', 'DEE.Cognitive.PI07.regulation.environment.R03')
    for key in keys: entries[key] = '{}'
    _, ph = b.protocol(True)
    m = {'version': b.VERSION, 'protocol_sha256': ph, 'ordinal': 12, 'rows': rows,
         'old_metadata_sha256': {key: b._sha(entries[key].encode('utf8')) for key in keys},
         'inherited_rows_sha256': b._sha(b._json(rows).encode('utf8')), 'log_chain_sha256': '00'*32,
         'log_count': 0, 'control': {'arm': 'real', 'max_ordinal': 32}, 'pending': None, 'uncertain': False}
    entries[b.KEY] = json.dumps(m); a.world.runtime.snapshot_metadata_entries = list(entries.items())
    home = DEST / 'MOCK_B_JOURNAL'; home.mkdir(); journal = home / 'eventos.jsonl'; journal.write_bytes(b'')
    homes = []
    def mock_home(directory, life): homes.append(life); return home
    fake = NS(_native=lambda: (None, None, None, json.loads, None), _home=mock_home,
        body=NS(KEY=keys[0], SYSTEM_KEY=adapter.SYSTEM_KEY, _home=mock_home), previous=NS(KEY=keys[1]), code_files=lambda: [])
    b._component = lambda: fake
    result = b.operational_dependencies(a, DEST)
    check('original_dependency_validator_passes_exact_MOCK_journal', result['ordinal'] == 12 and result['new_native_ticks'] == 0)
    check('journal_home_uses_actual_C_identity', homes and all(life == adapter.LIFE for life in homes))
    journal.write_bytes(b'{}\n')
    rejects('original_journal_guard_still_rejects_changed_content', lambda: b.operational_dependencies(a, DEST))
    check('original_scientific_B_source_still_literal', hashlib.sha256(Path(research.__file__).read_bytes()).hexdigest() == adapter.SOURCE_SHA)
    proof = P / 'control/PRUEBAS_FIX_C_IDENTIDAD_TRANSPORTE_PI08_R01.json'
    value = {'schema': 'DEE.PI08.C.identity_transport.pure_mock_tests.R01', 'passed': True,
             'Native_executed': False, 'DEE_imported': False, 'fixture_MOCK_ONLY_NOT_NATIVE': True,
             'checks': checked, 'count': len(checked), 'C_actual_readiness_or_episode_success_proved': False}
    with proof.open('x', encoding='utf8') as stream: json.dump(value, stream, indent=2); stream.write('\n')
    print(json.dumps({'proof': str(proof), 'sha256': hashlib.sha256(proof.read_bytes()).hexdigest(), 'checks': len(checked)}))


if __name__ == '__main__': main()
