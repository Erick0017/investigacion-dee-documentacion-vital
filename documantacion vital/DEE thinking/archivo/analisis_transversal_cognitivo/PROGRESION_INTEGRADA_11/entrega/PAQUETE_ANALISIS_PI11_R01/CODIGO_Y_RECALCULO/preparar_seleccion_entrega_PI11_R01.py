"""Prepare Root's explicit final PI11 package selection, never copies/packages.

No Native, owner, Word, SQLite, network or subprocess API. --schema prints the
final closure shape. --closure FILE --output NEW_JSON validates and produces
input for empaquetar_PI11_R01.py only AFTER Root closes actual final evidence.

--verify-replay PROOF --criterion CRITERION --main-primaries DIRECTORY
--replay-primaries DIRECTORY --expected-overall true|false is a separate,
read-only documentary check for the small extracted ZIP. It checks literal
witness hashes, declared identity-only canonicalization and the consistency
of the archived strict-Native comparison. It does NOT re-read omitted Native
arrays, re-run DEE, or turn a documented mismatch into a positive replay.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime
import argparse
import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
C = R / 'DEE Cognitive 2.0'
MANUAL = C / 'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
COMPENDIUM = R / 'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
CENTRAL = 'CODIGO_Y_RECALCULO/recalcular_PI11_R01.py'
SELF_TARGET = 'CODIGO_Y_RECALCULO/preparar_seleccion_entrega_PI11_R01.py'
CLOSURE_TARGET = '03_MAPAS/CIERRE_ENTREGA_PI11_Root.json'
REPLAY_PROOF_TARGET = '04_EVIDENCIAS/REPRODUCCION/COMPARACION_NATIVE_LITERAL.json'
REPLAY_CRITERION_TARGET = '04_EVIDENCIAS/REPRODUCCION/CRITERIO_PROSPECTIVO.json'
# Closed owner JSON can be large yet compress well. Never truncate its events;
# the packager applies the strict final compressed limit separately.
MAX_FILE = 64_000_000
BLOCKED_SUFFIXES = {'.zip', '.sqlite', '.sqlite3', '.db', '.whl', '.pyd', '.dll', '.exe', '.mp4', '.pfx', '.p12', '.pem'}
BLOCKED_PARTS = {'.git', '.aws', '.venv', '__pycache__', 'site-packages', 'python313', 'motor'}
ALLOWED_CODE = {'.py', '.json', '.md', '.patch', '.txt'}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def source(path, directory=False, project=True):
    p = Path(path).absolute()
    for node in (p, *p.parents):
        need(not node.is_symlink(), 'Symlink refused: ' + str(node))
        if node.exists():
            need(not (getattr(node.lstat(), 'st_file_attributes', 0) & 1024), 'Reparse source refused')
    need(p.is_dir() if directory else p.is_file(), 'Required final source not accessible: ' + str(p))
    p = p.resolve()
    if project:
        need(p.is_relative_to(R.resolve()), 'Non-DEE source refused')
    return p


def target(value):
    need(isinstance(value, str) and value and '\\' not in value and '\x00' not in value, 'Relative POSIX member name required')
    q = PurePosixPath(value)
    need(q.parts and value != '.' and not q.is_absolute() and value == q.as_posix()
         and all(part not in ('.', '..') and ':' not in part for part in q.parts), 'Unsafe target')
    return q.as_posix()


def checked_ref(row):
    need(isinstance(row, dict) and 'source' in row and 'sha256' in row, 'Final source/hash reference required')
    need(Path(row['source']).is_absolute(), 'Final source locator must be absolute')
    p = source(row['source'])
    need(re.fullmatch('[0-9a-f]{64}', row['sha256']) and digest(p) == row['sha256'], 'Final source hash changed: ' + str(p))
    return p


def no_secrets_or_big_binary(p):
    need(p.stat().st_size <= MAX_FILE, 'Large source belongs in localized omissions, not compact selection: ' + str(p))
    need(p.suffix.lower() not in BLOCKED_SUFFIXES and not p.name.lower().endswith('.deetsnap.gz'), 'Large state/runtime/history must remain local')
    need(not {part.lower() for part in p.parts}.intersection(BLOCKED_PARTS), 'Engine/cache/system tree refused')
    name = p.name.lower()
    need(name not in {'.env', 'credentials.json', 'token.json', 'id_rsa', 'id_ed25519', 'secrets.json'}
         and not name.startswith('service_account'), 'Credential-looking file refused')
    if p.suffix.lower() in {'.py', '.json', '.jsonl', '.txt', '.md', '.csv', '.patch'}:
        text = p.read_text('utf-8-sig')
        need('-----BEGIN PRIVATE KEY-----' not in text and '-----BEGIN RSA PRIVATE KEY-----' not in text,
             'Private key material refused')
        need(not re.search(r'"(?:refresh_token|access_token|client_secret|private_key)"\s*:\s*"[^"\s]{8,}"', text),
             'Credential-valued JSON field refused')


def canonical(value, life):
    if isinstance(value, dict):
        return {k: copy.deepcopy(v) if k in ('requests', 'physical_anchor', 'trace_observations')
                else canonical(v, life) for k, v in value.items()}
    if isinstance(value, list):
        return [canonical(v, life) for v in value]
    if isinstance(value, str):
        if value == life:
            return '__CURRENT_LIFE_ID__'
        text = value.replace('\\', '/')
        marker = '/estado/servicios_locales/' + life + '/'
        if marker in text and (text.startswith('/') or len(text) > 3 and text[1:3] == ':/'):
            return '__CURRENT_WORKER_HOME__/' + text.split(marker, 1)[1]
    return value


def verify_replay(proof_path, criterion_path, main_root, replay_root, expected):
    proof_path = source(proof_path, project=False)
    criterion_path = source(criterion_path, project=False)
    main_root = source(main_root, True, False)
    replay_root = source(replay_root, True, False)
    proof = read(proof_path); criterion = read(criterion_path)
    need(proof.get('schema', '').startswith('DEE.PI11.exact_acquisition_replay.passive_comparison.'), 'Actual closed strict comparison proof required')
    need(proof.get('Native_executed') is False and proof.get('DEE_imported') is False
         and proof.get('new_Native_ticks') == 0, 'Archived comparison is passive, not a Native execution')
    need(proof['criteria_sha256'] == digest(criterion_path), 'Actual prospective criterion hash differs')
    need(type(expected) is bool and proof.get('overall') is expected, 'Reported replay outcome differs from Root final closure')
    slife = proof['source_life']; rlife = proof['replay_life']
    count = criterion['expected_opportunities']
    need(type(count) is int and count > 0 and len(proof['episode_witnesses']) == count, 'Complete recorded replay window required')
    rows = []
    for number, row in enumerate(proof['episode_witnesses']):
        need(row['ordinal'] == number, 'Replay comparison witness ordinals are not complete')
        a_path = source(main_root / f'episodio_{number:04d}.json', project=False)
        b_path = source(replay_root / f'episodio_{number:04d}.json', project=False)
        need(digest(a_path) == row['source_sha256'] and digest(b_path) == row['replay_sha256'], 'Archived complete witness hash mismatch')
        a = read(a_path); b = read(b_path)
        need(a['life_id'] == slife and b['life_id'] == rlife and a['ordinal'] == b['ordinal'] == number, 'Witness identity/ordinal mismatch')
        equal = canonical(a, slife) == canonical(b, rlife)
        need(equal is row['content_equal_except_declared_documentary_identity'], 'Recalculated witness equality disagrees with strict comparison')
        need(a['actual_failed'] == row['original_actual_failed'] and b['actual_failed'] == row['reproduced_actual_failed'], 'Recorded errors were altered')
        rows.append({'ordinal': number, 'canonical_complete_witness_equal': equal,
                     'source_actual_failed': a['actual_failed'], 'replay_actual_failed': b['actual_failed']})
    if proof['Native_strict_equal']:
        need(proof['physical_equal'] is True and proof['source_physical'] == proof['replay_physical']
             and proof['binary_causal_prefix_equal'] is True
             and proof['source_causal_prefix_sha256'] == proof['replay_causal_prefix_sha256']
             and proof['Native_normalization_performed'] is False, 'Archived strict Native assertions are internally inconsistent')
        need(all(v['exact_equal'] and v['source_sha256'] == v['replay_sha256'] for v in proof['Native_components_exact'].values()),
             'Archived Native component equality is inconsistent')
    if expected:
        need(proof['Native_strict_equal'] and not proof['unexpected_metadata_or_scientific_changes']
             and not proof['own_metadata_scientific_differences']
             and proof['closed_replay']['owner_closed_coherently'] is True
             and proof['closed_replay']['unresolved_requests'] == 0, 'Reported successful replay lacks coherent closure')
    return {'schema': 'DEE.PI11.extracted_documentary_replay_check.R01', 'verified_documentary_outcome': True,
            'archived_overall_outcome': expected, 'archived_Native_strict_equal': proof['Native_strict_equal'],
            'witnesses': rows, 'Native_arrays_re_read': False, 'Native_executed': False,
            'new_Native_ticks': 0, 'independent_learning_samples_claimed': False,
            'scope': 'Complete literal exported witnesses and consistency/hash binding of the archived Native proof. Native arrays remain local; this is not a fresh full-state Native comparison or replay.'}


def build_selection(closure_path):
    closure_path = source(closure_path)
    closure_hash = digest(closure_path)
    closed = read(closure_path)
    need(closed.get('schema') == 'DEE.PI11.closed_delivery_selection.R01'
         and closed.get('closed_for_packaging') is True
         and closed.get('closed_for_documentary_read') is True
         and isinstance(closed.get('closure_evidence'), (str, dict, list)), 'Root final documentary/packaging closure required')
    need(datetime.fromisoformat(closed['cut_utc'].replace('Z', '+00:00')).tzinfo is not None, 'Actual final cutoff required')
    files = []; seen = {}; hashes = {}
    def add(src, name, pin=None):
        src = source(src); name = target(name); no_secrets_or_big_binary(src)
        value = digest(src)
        need(pin is None or value == pin, 'Pinned final source changed')
        folded = name.casefold()
        if folded in seen:
            need(seen[folded] == (str(src), value), 'Conflicting package target: ' + name)
            return
        seen[folded] = (str(src), value); hashes[str(src)] = value
        files.append({'source': str(src), 'target': name, 'sha256': value})
    docs = closed['documents']
    need(set(docs) == {'report', 'manual', 'compendium'}, 'One report and two complete current documents required')
    report = checked_ref(docs['report']); manual = checked_ref(docs['manual']); compendium = checked_ref(docs['compendium'])
    need(report.parent == P and report.suffix.lower() == '.md', 'Unique campaign scientific report required')
    need(manual == MANUAL.resolve() and compendium == COMPENDIUM.resolve(), 'Current published rectors required; no old/staged substitute')
    for doc in (manual, compendium):
        with zipfile.ZipFile(doc) as z:
            need(z.testzip() is None, 'Final full DOCX CRC failure')
            core = ET.fromstring(z.read('docProps/core.xml'))
            version = core.find('{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}version')
            need(version is not None and version.text == '1.40', 'Final published edition1.40 required')
            body = ET.fromstring(z.read('word/document.xml'))
            body_text = ''.join(e.text or '' for e in body.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
            need('PI11' in body_text, 'Actual PI11 chapter/entry required; a property update alone is insufficient')
    add(report, '01_INFORME_CIENTIFICO.md', docs['report']['sha256'])
    manual_target = '02_MANUAL/' + manual.name; comp_target = '02_MANUAL/' + compendium.name
    add(manual, manual_target, docs['manual']['sha256']); add(compendium, comp_target, docs['compendium']['sha256'])
    add(closure_path, CLOSURE_TARGET, closure_hash)
    omissions = closed['omissions']
    checked_ref(omissions)
    need(nonempty(omissions.get('target')), 'Existing localized omissions target required')
    add(omissions['source'], omissions['target'], omissions['sha256'])
    for row in closed.get('files', []):
        checked_ref(row); add(row['source'], row['target'], row['sha256'])
    need('00_leer_primero.txt' in seen, 'Root final reading entry must be selected explicitly as00_LEER_PRIMERO.txt')
    # Top-level PI11 science/instrumentation/configuration only. No state trees,
    # old campaign bundles, installed engine or inherited full code capsule.
    for path in sorted((P / 'codigo').iterdir()):
        if path.is_file() and path.suffix.lower() in ALLOWED_CODE:
            add(path, 'CODIGO_Y_RECALCULO/' + path.name)
    roots = {}
    for primary in closed['primary_roots']:
        role = primary['role']
        need(re.fullmatch('[A-Za-z0-9_-]+', role) and role not in roots, 'Distinct simple primary role required')
        root = source(primary['source'], True)
        need(nonempty(primary.get('closure_evidence')) and nonempty(primary.get('life_id')), 'Root must cite actual completed owner/export closure')
        expected = primary['expected_ordinals']
        need(isinstance(expected, list) and expected and all(type(n) is int and n >= 0 for n in expected)
             and expected == sorted(set(expected)), 'Explicit complete ordered witness window required')
        paths = sorted(root.glob('episodio_*.json'))
        ordinals = []
        for path in paths:
            value = read(source(path))
            need(value['life_id'] == primary['life_id'] and path.name == 'episodio_%04d.json' % value['ordinal'], 'Actual witness identity/filename mismatch')
            ordinals.append(value['ordinal'])
            add(path, '04_EVIDENCIAS/PRIMARIOS_CERRADOS/' + role + '/' + path.name)
        need(sorted(ordinals) == expected, 'Missing/unexpected witnesses; no silent partial replacement: ' + role)
        roots[role] = (root, '04_EVIDENCIAS/PRIMARIOS_CERRADOS/' + role)
    need({'MAIN', 'HEREDADO', 'YOKE'} <= set(roots), 'Central MAIN/HEREDADO/YOKE closed primaries required; do not substitute summaries')
    replay = closed['replay']
    comparison = checked_ref(replay['comparison']); criterion = checked_ref(replay['criterion'])
    need(replay['main_role'] in roots and replay['replay_role'] in roots, 'Complete source/replay witness roots required')
    verified = verify_replay(comparison, criterion, roots[replay['main_role']][0], roots[replay['replay_role']][0], replay['expected_overall'])
    add(comparison, REPLAY_PROOF_TARGET, replay['comparison']['sha256'])
    add(criterion, REPLAY_CRITERION_TARGET, replay['criterion']['sha256'])
    recalculations = [
        {'script': CENTRAL, 'args': ['--primarios', '04_EVIDENCIAS/PRIMARIOS_CERRADOS', '--salida', 'RECALCULO_VERIFICADO/CENTRAL', '--cierre', CLOSURE_TARGET], 'timeout_seconds': 120},
        {'script': SELF_TARGET, 'args': ['--verify-replay', REPLAY_PROOF_TARGET, '--criterion', REPLAY_CRITERION_TARGET,
                                      '--main-primaries', roots[replay['main_role']][1], '--replay-primaries', roots[replay['replay_role']][1],
                                      '--expected-overall', str(replay['expected_overall']).lower()], 'timeout_seconds': 120},
    ]
    need(all(digest(Path(path)) == value for path, value in hashes.items()) and digest(closure_path) == closure_hash, 'Final source changed during selection')
    return {'schema': 'DEE.PI11.analysis_package_selection.R01', 'closed_for_packaging': True,
            'cut_utc': closed['cut_utc'], 'final_closure_sha256': closure_hash,
            'files': sorted(files, key=lambda row: row['target']),
            'expected_manual': {'target': manual_target, 'sha256': docs['manual']['sha256']},
            'expected_compendium': {'target': comp_target, 'sha256': docs['compendium']['sha256']},
            'recalculations': recalculations,
            'selection_check': {'files': len(files), 'uncompressed_bytes': sum(Path(r['source']).stat().st_size for r in files),
                                'estimated_compressed_size_claimed': False, 'final_compressed_limit_enforced_by_packager': 15_000_000,
                                'preferred_compressed_budget': 10_000_000, 'large_operational_state_not_transported': True,
                                'documentary_replay_check': verified, 'new_Native_ticks': 0}}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def schema():
    ref = {'source': 'ABSOLUTE_EXISTING_FINAL_FILE', 'sha256': 'ACTUAL_SHA256'}
    return {'schema': 'DEE.PI11.closed_delivery_selection.R01', 'closed_for_packaging': False,
            'closed_for_documentary_read': False, 'closure_evidence': 'ACTUAL_CLOSURE_PROOF_LOCATOR', 'cut_utc': 'ACTUAL_FINAL_TIME_WITH_ZONE',
            'documents': {'report': ref, 'manual': ref, 'compendium': ref},
            'omissions': {**ref, 'target': '03_MAPAS/OMISIONES_LOCALIZADAS.json'},
            'files': [{**ref, 'target': '03_MAPAS/CONTINUIDAD_PI11_FINAL.json'}],
            'primary_roots': [{'role': role, 'life_id': 'ACTUAL_LIFE', 'source': 'ABSOLUTE_CLOSED_EXPORT_ROOT',
                               'expected_ordinals': list(range(16)), 'closure_evidence': 'ACTUAL_CLOSURE_PROOF'}
                              for role in ('MAIN', 'HEREDADO', 'YOKE', 'REPLAY')],
            'replay': {'comparison': ref, 'criterion': ref, 'main_role': 'MAIN', 'replay_role': 'REPLAY', 'expected_overall': None}}


def main(args):
    if args.schema:
        print(json.dumps(schema(), ensure_ascii=False, indent=2)); return
    if args.verify_replay:
        need(args.criterion and args.main_primaries and args.replay_primaries and args.expected_overall is not None, 'Explicit extracted replay inputs required')
        result = verify_replay(args.verify_replay, args.criterion, args.main_primaries, args.replay_primaries, args.expected_overall == 'true')
        print(json.dumps(result, ensure_ascii=False)); return
    need(args.closure is not None, 'Actual final closure JSON required; no provisional selection')
    selection = build_selection(args.closure)
    if args.output:
        p = Path(args.output).absolute()
        need(p.parent.is_dir() and p.resolve().is_relative_to(P.resolve()) and not p.exists() and not p.is_symlink(), 'New selection output limited to this campaign')
        for node in p.parents:
            need(not node.is_symlink() and not (getattr(node.lstat(), 'st_file_attributes', 0) & 1024), 'No linked output ancestor')
        with p.open('x', encoding='utf8', newline='\n') as f:
            json.dump(selection, f, ensure_ascii=False, indent=2); f.write('\n')
        print(json.dumps({'selection': str(p), 'sha256': digest(p), 'files': len(selection['files']),
                          'uncompressed_bytes': selection['selection_check']['uncompressed_bytes'], 'copied_or_packaged': False}))
    else:
        print(json.dumps(selection, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--schema', action='store_true')
    ap.add_argument('--closure', type=Path)
    ap.add_argument('--output', type=Path)
    ap.add_argument('--verify-replay', type=Path)
    ap.add_argument('--criterion', type=Path)
    ap.add_argument('--main-primaries', type=Path)
    ap.add_argument('--replay-primaries', type=Path)
    ap.add_argument('--expected-overall', choices=('true', 'false'))
    main(ap.parse_args())
