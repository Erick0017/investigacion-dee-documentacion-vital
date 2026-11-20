"""Pure administrative/causal-wiring tests. NO DEE import or Native execution."""
from pathlib import Path
import ast, copy, hashlib, importlib.util, json, sys, tempfile, types

HERE = Path(__file__).resolve().parent
P8 = HERE.parent


def load():
    spec = importlib.util.spec_from_file_location('PI08_B_pure', HERE/'pi08_revision_flexible_B_R01.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def main():
    m = load(); checks = []

    def check(name, assertion):
        if not assertion:
            raise AssertionError(name)
        checks.append({'check': name, 'passed': True})

    p, ph = m.protocol(False)
    check('fixed_episode_fingerprint_before_private_load', hashlib.sha256((HERE/'pi08_revision_flexible_B_episodio_R01.py').read_bytes()).hexdigest() == m.EPISODE_SHA)
    check('import_is_stdlib_only_NO_DEE', not any(n.startswith('dee_thinking') for n in sys.modules))
    check('draft_blocked_before_material', p['status'] == 'DRAFT_PENDING_ACTUAL_A_ADOPTION')
    try:
        m.protocol(True)
    except (ValueError, FileNotFoundError):
        check('material_gate_refuses_without_seal', True)
    else:
        check('material_gate_refuses_without_seal', False)
    check('32_offers_and12_preserved_prefix', len(p['schedule']) == 32 and p['start_ordinal'] == 12)
    original = HERE.parents[1]/'PROGRESION_INTEGRADA_07/codigo/PROTOCOLO_PI07_R03.json'
    check('prefix_first12_literal', p['schedule'][:12] == json.loads(original.read_text('utf-8-sig'))['schedule'][:12])
    perm = p['controls']['yoke_permutation']
    check('permutation18_complete', sorted(perm) == list(range(18)))
    check('derangement_no_fixedpoints', all(i != j for i, j in enumerate(perm)))
    check('permutation_not_constant_cyclic_shift', len({(j-i) % 18 for i, j in enumerate(perm)}) > 1)
    failed = [False, True, True, False, False, True, False, True, False, False, True, False, True, False, True, True, False, True]
    plan = {'schema': 'DEE.PI08.B.noncyclic_yoked_return.v1', 'permutation': perm,
            'source_failed': failed, 'values': [failed[i] for i in perm], 'source_evidence_sha256': 'a'*64}
    text = m._json(plan); parsed = m._plan(text, m._sha(text.encode()), p)
    check('yoke_preserves_actual_true_false_dose', sum(parsed['source_failed']) == sum(parsed['values']))
    bad = copy.deepcopy(plan); bad['values'][0] = not bad['values'][0]
    try:
        textbad = m._json(bad); m._plan(textbad, m._sha(textbad.encode()), p)
    except ValueError:
        check('yoke_tamper_refused', True)
    else:
        check('yoke_tamper_refused', False)
    for role in m.ROLES:
        row = {'modo': m.START, 'brazo': role, 'prefijo_sha256': 'b'*64, 'registro_global': False}
        if role == 'yoked':
            row.update(plan=text, plan_sha256=m._sha(text.encode()))
        m.validate_literal(row)
        check('strict_start_literal_'+role, True)
    for invalid in ({'modo': m.EPISODE, 'forzar': 'pulso'}, {'modo': m.EPISODE, 'cue': 'threat'},
                    {'modo': m.EPISODE, 'target': 1}, {'modo': m.STATE, 'ticks': 1}):
        try:
            m.validate_literal(invalid)
        except ValueError:
            check('actor_override_refused_'+next(k for k in invalid if k != 'modo'), True)
        else:
            raise AssertionError('Actor override accepted')
    for role in ('real', 'none', 'yoked'):
        progress = {'control': {'arm': role, 'from_ordinal': 12, 'yoked_values': parsed['values']}, 'ordinal': 12}
        for datum in range(4):
            for native in (-1, 1, None):
                check('Native_choice_identity_%s_%s_%s' % (role, datum, native), m._choose_action(progress, datum, native) is native)
        before = copy.deepcopy(progress); m._after_actual_outcome(progress, 1, 1, True)
        check('no_external_policy_or_update_'+role, progress == before and 'reference_policy' not in progress)
    reference = {'control': {'arm': 'reference'}, 'reference_policy': {str(i): -1 for i in range(4)}}
    check('reference_initial_action_is_fixed_prior', m._choose_action(reference, 1, 1) == -1)
    m._after_actual_outcome(reference, 1, -1, True)
    check('reference_switches_ONLY_visited_context_after_failure', reference['reference_policy'] == {'0': -1, '1': 1, '2': -1, '3': -1})
    before = copy.deepcopy(reference); m._after_actual_outcome(reference, 1, 1, False)
    check('reference_stays_after_actual_success', reference == before)
    check('negative_generic_return_real', m._return({'control': {'arm': 'real'}}, True) is True)
    check('nonfailure_is_materialFalse_notNULL', m._return({'control': {'arm': 'none'}}, True) is False)
    check('yoke_uses_only_frozen_position_boolean', m._return({'control': {'arm': 'yoked', 'from_ordinal': 12, 'yoked_values': parsed['values']}, 'ordinal': 12}, False) is parsed['values'][0])
    # Structural proof: every copied line is original except the four declared
    # replacements. Native circuit, reader windows, FI path and return ports stay.
    srcfile = HERE.parents[1]/'PROGRESION_INTEGRADA_07/codigo/pi07_regulacion_R03.py'
    source = srcfile.read_text('utf-8-sig'); tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'episode')
    source_episode = ''.join(source.splitlines(True)[node.lineno-1:node.end_lineno])+'\n'
    copied_file = HERE/'pi08_revision_flexible_B_episodio_R01.py'
    copied = copied_file.read_text('utf8'); node2 = next(n for n in ast.parse(copied).body if isinstance(n, ast.FunctionDef))
    copied_episode = ''.join(copied.splitlines(True)[node2.lineno-1:node2.end_lineno])+'\n'
    reversals = [
      ("used.run_until(q+4);reader=_read(a,q);used.run_until(q+6);native_motor=_motor(reader['choice']);reference_policy_before=dict(m['reference_policy'])if m['control']['arm']=='reference'else None;motor=_b_choose_action(m,datum,native_motor)", "used.run_until(q+4);reader=_read(a,q);used.run_until(q+6);native_motor=_motor(reader['choice']);motor=(1 if forced=='pulso'else -1)if forced is not None else native_motor"),
      ("arm=m['control']['arm'];_b_after_actual_outcome(m,datum,motor,actual_failed);returned=_return(m,actual_failed)", "arm=m['control']['arm'];returned=_return(m,actual_failed)"),
      ("'operator_forced_action':forced,'executed_action_source':'external_contextual_WSLS'if arm=='reference'else 'Native_TC','reference_policy_before':reference_policy_before,'reference_policy_after':dict(m['reference_policy'])if arm=='reference'else None,'B_ordinal':m['ordinal']-m['control']['from_ordinal'],'global_regulatory_ordinal':m['ordinal'],", "'operator_forced_action':forced,"),
      ("'forced':m['control']['arm']=='reference'", "'forced':forced is not None")]
    for old, new in reversals:
        check('single_declared_source_change_'+str(len(checks)), copied_episode.count(old) == 1)
        copied_episode = copied_episode.replace(old, new)
    check('copied_episode_rest_is_literal_original', copied_episode == source_episode)
    check('efference_copies_actual_executed_motor_before_return',
          copied.index('motor=_b_choose_action') < copied.index('submit_motor_copy(a.world,motor') < copied.index('actual_failed=') < copied.index('submit_generic_outcome'))
    # Explicit conservation identity: read-only B access, no new B episode.
    original_identity, original_protocol, original_get, original_seal = m._identity, m.protocol, m._get, m.SEAL
    with tempfile.TemporaryDirectory(prefix='PI08_B_conservation_pure_') as temporary:
        sealfile = Path(temporary)/'seal.json'
        conservation = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01'
        sealfile.write_text(json.dumps({'research_life_ids': {role:'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_'+role.upper()+'_01' for role in m.ROLES}, 'conservation_life_id':conservation}), encoding='utf8')
        m.SEAL = sealfile
        m._identity = lambda a: {'life_id':conservation}
        m.protocol = lambda material=False: (p,'PURE_PH')
        m._get = lambda a: {'protocol_sha256':'PURE_PH','ready':True,'admitted':True,'pending':None,'uncertain':False,'control':{'arm':'real','max_ordinal':32},'ordinal':30}
        a = types.SimpleNamespace(world=types.SimpleNamespace(runtime=types.SimpleNamespace(snapshot_metadata_entries=[])))
        m.validate(a,{'modo':m.STATE})
        check('followingC_readonly_STATE_allowed_noNative',True)
        for row in ({'modo':m.START,'brazo':'real','prefijo_sha256':'a'*64,'registro_global':False},{'modo':m.EPISODE}):
            try:
                m.validate(a,row)
            except ValueError:
                check('followingC_readonly_'+row['modo']+'_refused',True)
            else:
                raise AssertionError('Conservation clone cannot start/execute B')
    m._identity, m.protocol, m._get, m.SEAL = original_identity, original_protocol, original_get, original_seal
    # Pure fake material wiring, explicitly NOT Native data or a learning proof.
    fake_cases = []
    for role, native, state_value, policy, packet in [('real', 1, 1, None, None), ('none', -1, 1, None, None),
                                                   ('yoked', -1, 1, None, 5), ('reference', 1, 1, -1, None)]:
        result = fake_episode(m, role, native, state_value, policy, packet)
        fake_cases.append(result)
        expected_motor = policy if role == 'reference' else native
        check('FAKE_actual_efference_matches_executed_'+role, result['copied_motor'] == expected_motor)
        check('FAKE_keeps_native_choice_truthful_'+role, result['native_motor'] == native)
        check('FAKE_generic_return_has_no_action_or_bank_'+role, result['outcome_argument_keys'] == ['failed', 'tick'])
    out = {'schema': 'DEE.PI08.B.pure_tests.R04', 'passed': True, 'checks': checks, 'check_count': len(checks),
           'Native_executed': False, 'DEE_imported': False, 'scope': 'Pure validation, exact source diff and labelled Fake wiring only; no Native outcome or learning claim.',
           'fake_material_wiring_NOT_NATIVE': fake_cases,
           'files': {f: {'bytes': (HERE/f).stat().st_size, 'sha256': hashlib.sha256((HERE/f).read_bytes()).hexdigest()}
                     for f in ('pi08_revision_flexible_B_R01.py', 'pi08_revision_flexible_B_episodio_R01.py', 'PROTOCOLO_PI08_B_R01.json')}}
    target = P8/'control/PRUEBAS_PURAS_B_PI08_R04.json'
    if target.exists():
        raise FileExistsError('Preserve existing test witness')
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps({'passed': True, 'check_count': len(checks), 'proof': str(target), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}, indent=2))


def fake_episode(module, role, native, datum, reference_policy, packet):
    """Tiny deterministic interface fake. No engine import, physical claims or score."""
    requests = []; actions = []; copies = []; outcomes = []; logs = []
    progress = {'ordinal': 12, 'role': 'evaluation', 'control': {'arm': role, 'from_ordinal': 12, 'yoked_values': [False]*18},
                'rows': [{} for _ in range(12)], 'instrumentation': {'global_enabled': False},
                'body_P0': {'preparation_life_id': 'FAKE'}, 'uncertain': False, 'pending': None}
    if role == 'reference':
        progress['reference_policy'] = {str(i): reference_policy for i in range(4)}
    class Runtime:
        def receipt(self, rid):
            return {'status': 'applied', 'id': rid}
    a = types.SimpleNamespace(tick=0, world=types.SimpleNamespace(runtime=Runtime()))
    a.run_until = lambda tick: setattr(a, 'tick', tick)
    def request(kind, tick, motor=None):
        r = {'id': 'FAKE_%04d' % len(requests), 'kind': kind, 'tick': tick}
        requests.append(r)
        if motor is not None:
            copies.append(motor)
        return r
    def submit(world, channel, payload, tick, collection, **kwargs):
        r = request(channel, tick); collection.append(r); return r
    cal = {'query_tick': 100, 'seed_tick': 107, 'outcome_injection_tick': 508, 'collision_tick': 509, 'contact_tick': 510}
    def outcome(world, failed, tick, **kwargs):
        outcomes.append({'failed': failed, 'tick': tick}); return request('generic', tick)
    helper = types.SimpleNamespace(schedule_trial=lambda *args: cal,
          submit_query=lambda world, tick, **kwargs: [request('Q', tick) for _ in range(3)],
          submit_motor_copy=lambda world, motor, tick, **kwargs: request('copy', tick, motor), submit_generic_outcome=outcome)
    def observe(adapter, site):
        if site == (52, 48, 47):
            return {'state': datum, 'semantic': 1, 's_reg': 0, 'direction': [0, 0, 1], 'raw': datum, 'clock': 0}
        if site == (54, 48, 56):
            return {'state': int(packet is not None), 'semantic': 1, 's_reg': packet or 0, 'direction': [1, 0, 0], 'raw': packet or 0, 'clock': 0}
        return {'state': 0, 'semantic': 0, 's_reg': 0, 'direction': [0, 0, 0], 'raw': 0, 'clock': 0}
    def receipts(adapter, rows):
        return [{**r, 'receipt': {'status': 'applied'}} for r in rows]
    baseline = types.SimpleNamespace(FIPLUS='FAKE_FI', _calendar=lambda adapter: {'query_tick': 292},
          _fiplus=lambda adapter, row, directory: {'requests': [request('FI', 300+i) for i in range(176)],
                                                'old_q6_choice': -1 if role == 'reference' else 1, 'calendar': {'query_tick': 292}})
    package = types.ModuleType('capacidades'); package.pi05_transito_causal_R01 = baseline
    previous_package = sys.modules.get('capacidades'); sys.modules['capacidades'] = package
    used = types.SimpleNamespace(safety=[], run_until=a.run_until)
    namespace = {'validate': lambda *args: None, 'protocol': lambda **kwargs: ({'schedule': [{'cue': 'none', 'message_payload': None, 'left': 14, 'right': 3}]*12+[{'cue': 'threat', 'message_payload': packet, 'left': 14, 'right': 3}], 'max_ticks_per_episode': 1300}, 'FAKE'),
          '_identity': lambda adapter: {'life_id': 'FAKE'}, '_get': lambda adapter: progress,
          '_observe': observe, 'at': lambda v: tuple(v), '_helper': lambda: helper,
          '_instrumented': lambda *args: (used, used, None), '_old_literals': lambda adapter: {'FAKE': 'literal'},
          'CALIBRATE': 'NEVER', 'PREFIX': 'FAKE', 'SENSOR': (52, 48, 47), 'CUES': {'threat': ((52, 48, 46), (0, 0, 1))},
          '_save': lambda *args: None, '_record': lambda *args: logs.append(args[-1]), '_submit': submit,
          '_read': lambda *args: {'choice': native}, '_motor': lambda value: value,
          '_b_choose_action': module._choose_action, '_b_after_actual_outcome': module._after_actual_outcome,
          '_return': module._return, 'MESSAGE_CHANNEL': 'message', 'ACTUATOR': (53, 48, 56), 'MESSAGE_READER': (54, 48, 56),
          '_emit': lambda adapter, motor, seed, rows, ablation: submit(adapter, 'pulse', 0, seed, rows) if motor == 1 else None,
          '_native': lambda: (None, None, lambda value: value, None, None),
          '_receipts': receipts, '_summary': lambda rows, start, end: {'all_terminal': True, 'unique_requested': len(rows), 'applied': len(rows)},
          '_physical': lambda adapter: {'FAKE_tick': adapter.tick}, 'VERSION': module.VERSION, 'os': __import__('os'), '_sha': module._sha}
    try:
        with tempfile.TemporaryDirectory(prefix='PI08_B_pure_') as temporary:
            namespace['_home'] = lambda *args: Path(temporary)
            exec(compile((HERE/'pi08_revision_flexible_B_episodio_R01.py').read_bytes(), 'labelled_FAKE_episode', 'exec'), namespace)
            result = namespace['episode'](a, {'modo': module.EPISODE}, temporary)
    finally:
        if previous_package is None:
            sys.modules.pop('capacidades', None)
        else:
            sys.modules['capacidades'] = previous_package
    return {'FAKE_NOT_NATIVE': True, 'role': role, 'native_motor': result['native_motor'], 'actual_motor': result['actual_motor'],
            'copied_motor': copies[-1], 'outcome_argument_keys': sorted(outcomes[-1]), 'actual_failed': result['actual_failed'],
            'returned_failed': result['returned_failed'], 'reference_policy_after': result['reference_policy_after']}


if __name__ == '__main__':
    main()
