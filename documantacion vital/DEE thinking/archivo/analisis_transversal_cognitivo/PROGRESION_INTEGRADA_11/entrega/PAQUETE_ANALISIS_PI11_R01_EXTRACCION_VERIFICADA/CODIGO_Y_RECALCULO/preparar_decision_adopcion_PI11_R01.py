"""Pure final PI11 basis/contract/decision compiler; no DEE or state imports.

This program NEVER chooses scientific outcomes, approves a gate, promotes a
life, edits product/source code or opens SQLite. Root supplies explicit final
facts with exact existing JSON evidence and JSON-pointer checks. A failed or
pending gate prevents generation of an adoption contract/decision.

--schema prints the input shapes, deliberately without positive outcomes.
--basis-facts FILE prints a closed-source basis for the isolated IF clone.
--decision-facts FILE --output-dir NEW_DIRECTORY_UNDER_CODIGO prepares a MAIN
contract, literal PI10 rollback contract and exact reasoned decision. With no
--write it prints a preview and writes nothing. --write creates only that new
directory under codigo. Root must review and independently run pi11_adoptar's
read-only validator before considering any explicit movement command.
"""
from pathlib import Path, PurePosixPath
import argparse
import ast
import copy
import hashlib
import json
import re

H = Path(__file__).resolve().parent
P = H.parent
C = P.parents[2] / 'DEE Cognitive 2.0'
S = C / 'sistema'
PARENT = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
PARENT_T = 947395
PARENT_SHA = 'fd7372b7f2adc9040866fab8adfaca0d79e0bd18e997c0abc0651fe4fa3c23dc'
MAIN = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_MAIN01'
IFLIFE = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_IF01'
FINAL_OWNER_PROOF = P / 'control/PI11_MAIN01_POST4_OWNER_R01.json'
INTERFACE_PROOF = P / 'control/PI11_IF01_PUBLICO_OWNER_R01.json'
CONTRACT = 'PI11_USO_OPERATIVO_R01.json'
PI10CONTRACT = 'PI10_USO_OPERATIVO_R01.json'
GATES = ('functional_gain', 'conservation', 'causal_controls', 'source_reopening',
         'new_function_at_final_cut', 'decisive_recipe_replay')
PROOFS = ('source_final_owner', 'conservation_owner', 'source_reopening_owner',
          'replay_owner', 'replay_comparison', 'product_interface_test')
SELECTORS = ('PROYECTO.json', 'CONTINUIDAD_DEE_COGNITIVE_2_0.json',
             'sistema/estado/ACTIVO.json', 'sistema/estado/genesis/SELECCION_PERSONAL.json',
             'aplicacion/GENESIS/SELECCION_CANDIDATA.json',
             'sistema/capacidades/CATALOGO_CAPACIDADES.json')
OVERRIDES = {'app/mundo_genesis_apd05.py', 'capacidades/pi11_identidad_heredada_R02.py',
             'app/pi11_identidad_c2c_R01.py', 'gestionar.py', 'app/pi11_gestor_publico_R01.py'}
FROZEN = ('pi11_actor_R01.py', 'pi11_habitat_persistente_R01.py', 'pi11_dispatcher_R01.py',
          'pi11_identidad_heredada_R02.py', 'pi11_lote_FI8_R01.py',
          'PI11_FI8_SUMINISTRO_R01.json', 'PROTOCOLO_PI11_R01.json',
          'PI11_EXPERIMENTO_R01.json', 'PI11_PLUGINS_R01.json',
          'pi10_transporte_ancestral_R01.py', 'pi10_permiso_operativo_R02.py')
NARRATIVE = ('scope', 'gains', 'losses', 'uncertainties', 'assistance', 'regression_coverage')


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()


def regular(path):
    for node in (Path(path), *Path(path).parents):
        need(not node.is_symlink() and not (node.exists() and getattr(node.lstat(), 'st_file_attributes', 0) & 1024),
             'Linked/reparse path refused: ' + str(node))


def local(path, root=P, existing=True):
    path = Path(path)
    regular(path)
    path = path.resolve(strict=existing)
    need(path.is_relative_to(Path(root).resolve()), 'Path outside declared root: ' + str(path))
    return path


def relative(name):
    need(isinstance(name, str) and name and '\\' not in name and ':' not in name, 'Portable relative source name required')
    p = PurePosixPath(name)
    need(not p.is_absolute() and name == p.as_posix() and all(x not in ('.', '..') for x in p.parts), 'Unsafe source name')
    return p


def pointer(value, path):
    need(isinstance(path, str) and (not path or path.startswith('/')), 'JSON pointer must be empty or begin with /')
    for part in path[1:].split('/') if path else []:
        part = part.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def evidence(ref, checks=False):
    need(isinstance(ref, dict) and {'path', 'sha256'} <= set(ref), 'Explicit path/sha256 evidence reference required')
    file = local(ref['path'])
    need(re.fullmatch('[a-f0-9]{64}', ref['sha256']) and digest(file) == ref['sha256'], 'Actual evidence hash changed: ' + str(file))
    value = read(file)
    if checks:
        need(isinstance(ref.get('checks'), dict) and ref['checks'], 'Explicit real JSON-pointer checks required')
    for key, expected in ref.get('checks', {}).items():
        need(pointer(value, key) == expected, 'Actual evidence check differs: ' + key)
    return value


def normalized_ref(ref, checks=False):
    evidence(ref, checks)
    return {**copy.deepcopy(ref), 'path': str(local(ref['path']))}


def source_system(value):
    source = local(value)
    need(source.name == 'sistema' and source.parent.parent == (P / 'estados').resolve()
         and not (source / 'estado/ACTIVO.json').exists(), 'Explicit unselected PI11 diagnostic source required')
    return source


def exact_source(facts, life_key='life_id'):
    source = source_system(facts['source_system'])
    life = facts[life_key]
    need(life == MAIN, 'MAIN01 is the sole candidate; IF/control contracts are never reused')
    need(type(facts['source_tick']) is int and facts['source_tick'] > PARENT_T
         and re.fullmatch('[a-f0-9]{64}', facts['source_snapshot_sha256']), 'Explicit actual final source cut required')
    card = read(source / 'estado/vidas' / life / 'VIDA.json')
    need(card['life_id'] == card['world_id'] == life and card['physical']['N'] == 67
         and card['physical']['tick'] == facts['source_tick']
         and card['snapshot_sha256'] == facts['source_snapshot_sha256'], 'Source card differs from executive final facts')
    snapshot = local(source / card['snapshot'], source)
    need(digest(snapshot) == facts['source_snapshot_sha256'], 'Source snapshot bytes differ from the final fact')
    return source, card


def parent_intact():
    card = read(S / 'estado/vidas' / PARENT / 'VIDA.json')
    need(card['physical']['N'] == 67 and card['physical']['tick'] == PARENT_T
         and card['snapshot_sha256'] == PARENT_SHA and digest(S / card['snapshot']) == PARENT_SHA,
         'Protected PI10 principal must remain intact at 947395')
    need(read(S / 'estado/ACTIVO.json')['life_id'] == PARENT, 'PI10 must remain the selected principal before preparation')


def basis(facts):
    need(facts.get('schema') == 'DEE.PI11.explicit_closed_source_basis_facts.R01', 'Explicit closed-source basis facts schema required')
    exact_source(facts, 'source_life_id')
    ref = normalized_ref(facts['source_closed_proof'], True)
    need(Path(ref['path']) == FINAL_OWNER_PROOF.resolve(), 'The IF basis must use the actual final POST4 MAIN owner, never an earlier cut')
    owner = evidence(ref)
    need(owner.get('life_id') == facts['source_life_id'] and owner.get('closed') is True
         and owner.get('error') is None and owner.get('final_tick') == facts['source_tick'], 'Actual coherently closed MAIN owner required')
    return {'schema': 'DEE.PI11.closed_scientific_basis_for_interface.R01', 'not_adoption': True,
            'source_life_id': facts['source_life_id'], 'source_tick': facts['source_tick'],
            'source_snapshot_sha256': facts['source_snapshot_sha256'], 'source_closed_proof': ref,
            'all_adoption_gates_claimed': False, 'Native_executed': False, 'product_written': False}


def approved_sources(source, manifest_ref, product_code):
    manifest = evidence(manifest_ref)
    need(isinstance(manifest.get('files'), list) and manifest['files'], 'Actual source code manifest required')
    originals = {}
    for row in manifest['files']:
        name = relative(row['file']).as_posix()
        need(name not in originals, 'Duplicate source manifest member')
        path = local(source / name, source)
        need(path.is_file() and digest(path) == row['sha256'], 'Source manifest dependency changed: ' + name)
        originals[name] = path
    product_code = local(product_code, H)
    cm = read(product_code / 'CODIGO_PREPARADO.json')
    need(cm.get('schema') == 'DEE.PI11.prepared_product_code.R02'
         and Path(cm['source_system']).resolve() == source, 'Exact MAIN prepared product R02 manifest required')
    overrides = {}
    for row in cm['files']:
        name = relative(row['file']).as_posix()
        path = local(row['source'], product_code)
        need(name not in overrides and path == product_code / name and digest(path) == row['sha256'], 'R02 override hash/path differs')
        ast.parse(path.read_bytes())
        overrides[name] = path
    need(set(overrides) == OVERRIDES, 'Exactly the five reviewed R02 overrides required')
    final = {**originals, **overrides}
    return originals, overrides, final


def validate_gates_and_proofs(facts):
    need(facts.get('approved_for_adoption') is True, 'Root must explicitly approve the final reasoned decision; pending means no output')
    need(set(facts['gates']) == set(GATES) and set(facts['proofs']) == set(PROOFS), 'All six real scientific gates and proof modalities required')
    gates = copy.deepcopy(facts['gates'])
    for name, gate in gates.items():
        need(gate.get('satisfied') is True and gate.get('criterion') and gate.get('result')
             and isinstance(gate.get('evidence'), list) and gate['evidence'], 'Missing/failed/pending actual scientific gate: ' + name)
        gate['evidence'] = [normalized_ref(ref, True) for ref in gate['evidence']]
    proofs = {name: normalized_ref(ref, True) for name, ref in facts['proofs'].items()}
    values = {name: evidence(ref) for name, ref in proofs.items()}
    need(Path(proofs['source_final_owner']['path']) == FINAL_OWNER_PROOF.resolve()
         and Path(proofs['product_interface_test']['path']) == INTERFACE_PROOF.resolve(),
         'Final POST4 MAIN and actual IF01 public Owner proofs are the declared final evidence slots')
    for name in ('source_final_owner', 'conservation_owner', 'source_reopening_owner'):
        v = values[name]
        need(v.get('life_id') == facts['life_id'] and v.get('closed') is True and v.get('error') is None, 'Actual closed MAIN proof required: ' + name)
    need(values['source_final_owner'].get('final_tick') == facts['source_tick'], 'Final source Owner proof differs from exact MAIN cut')
    replay = values['replay_owner']
    need(replay.get('life_id', replay.get('life')) not in (None, facts['life_id'])
         and (replay.get('closed') is True or replay.get('status') == 'COMPLETED' and replay.get('owner_closed_coherently') is True)
         and replay.get('error') is None, 'Independent coherently closed actual replay required')
    interface = values['product_interface_test']
    need(interface.get('schema') == 'DEE.PI11.actual_public_interface_owner.R01'
         and interface.get('life_id') == IFLIFE and interface.get('phase') == 'interface'
         and all(interface.get(k) is True for k in ('Native_executed', 'owner_closed', 'material_use_completed'))
         and interface.get('product_originals_modified') is False and interface.get('error') is None,
         'Actual isolated finite IF01 material interface proof required')
    return gates, proofs


def compile_decision(facts, output):
    need(facts.get('schema') == 'DEE.PI11.explicit_adoption_generation_facts.R01', 'Explicit final adoption-generation facts required')
    source, card = exact_source(facts)
    parent_intact()
    gates, proofs = validate_gates_and_proofs(facts)
    sealed = normalized_ref(facts['sealed_criterion'], True)
    source_manifest = normalized_ref(facts['source_code_manifest'])
    need(local(source_manifest['path']).parent == source.parent, 'Use the actual MAIN source code manifest')
    need(type(facts['source_ordinal']) is int and 1 <= facts['source_ordinal'] < 24
         and re.fullmatch('[a-f0-9]{64}', facts['PI10_history_sha256']), 'Actual closed unexhausted MAIN ordinal and literal PI10 history hash required')
    need(re.fullmatch(r'[A-Za-z0-9_\-.]{1,100}', facts['decision_id']), 'Explicit final decision id required')
    for key in NARRATIVE:
        need(key in facts and facts[key] is not None, 'Root must provide actual reasoned field, including explicit empty losses/uncertainties when applicable: ' + key)
    need(facts['scope'] and facts['gains'] and facts['assistance'] and facts['regression_coverage'], 'Actual scope/gains/assistance/regression coverage required')
    need(isinstance(facts['catalog_entry'], dict) and facts['catalog_entry'].get('id'), 'Explicit reviewed catalog entry required')
    originals, overrides, final = approved_sources(source, source_manifest, facts.get('product_code', H / 'PRODUCTO_PREPARADO_R02'))
    exp = read(source / 'capacidades/PI11_EXPERIMENTO_R01.json')
    need(exp.get('life_id') == facts['life_id'] and exp.get('return_arm') == 'real' and exp.get('continuation') == 'native', 'Final contract is only for MAIN Native real continuation')
    contract = {'schema': 'DEE.PI11.exact_operational_permission.R01', 'life_id': facts['life_id'],
                'profile': 'fisica_directa', 'N': 67, 'status': 'PREPARED_DIAGNOSTIC',
                'all_adoption_gates_met': True, 'adoption_decision_sha256': None,
                'previous_principal': {'life_id': PARENT, 'tick': PARENT_T, 'snapshot_sha256': PARENT_SHA},
                'allowed_modes': ['eci01-pi11-episodio', 'eci01-pi11-estado'],
                'PI10_material_disabled': True, 'historical_material_disabled': True,
                'public_FI_backend': 'PI11_new_FI8_same_frozen_body',
                'new_FI8_key': 'DEE.Cognitive.PI11.explicit_FI_eight_offer_lot.R01', 'new_FI8_total': 8,
                'public_FI_domain': [0, 20], 'internal_FI_redirected': False,
                'public_arithmetic_policy': 'legacy_partial',
                'C2C_protocol_sha256': '0cf6bf8508e071a1c8cf1448023a096bc43336d66b8a1deb98f488b29b4205fd',
                'source_ordinal': facts['source_ordinal'],
                'PI11_protocol_sha256': digest(final['capacidades/PROTOCOLO_PI11_R01.json']),
                'PI10_history_sha256': facts['PI10_history_sha256'],
                'frozen_files_sha256': {name: digest(final['capacidades/' + name]) for name in FROZEN}}
    # No IF contract, marker, source Native bytes, card or SQLite is copied.
    payloads = {'contratos/' + CONTRACT: encoded(contract),
                'contratos/' + PI10CONTRACT: (S / 'contratos' / PI10CONTRACT).read_bytes()}
    rows = []
    for name, path in sorted(final.items()):
        target = S / name
        before = digest(target) if target.exists() else None
        after = digest(path)
        deploy = name in overrides or before != after
        if name in ('contratos/' + CONTRACT, 'contratos/' + PI10CONTRACT):
            continue
        if deploy:
            rel = relative(name)
            need(name != 'capacidades/CATALOGO_CAPACIDADES.json'
                 and path.suffix in ('.py', '.json')
                 and (rel.parts[0] in ('app', 'capacidades') or name == 'gestionar.py'),
                 'Unsupported changed inherited dependency must be resolved explicitly, never silently redeployed: ' + name)
            ast.parse(path.read_bytes()) if path.suffix == '.py' else read(path)
            rows.append({'file': name, 'source': str(path), 'sha256': after, 'before_sha256': before})
    for name, content in payloads.items():
        target = S / name
        rows.append({'file': name, 'source': str(output / name), 'sha256': hashlib.sha256(content).hexdigest(),
                     'before_sha256': digest(target) if target.exists() else None})
    selectors = {name: digest(C / name) for name in SELECTORS}
    process = local(facts['process_proof'])
    # This pins the actual scoped proof. Freshness/SQLite/process checks belong
    # to the exclusive Root movement engine immediately before its mutation.
    process_value = read(process)
    need(process_value.get('no_live_affected_writers') is True
         and process_value.get('recorded_utc') and process_value.get('scope') and process_value.get('evidence')
         and {facts['life_id'], PARENT} <= set(process_value.get('affected_life_ids', [])), 'Actual scoped closed-process proof required')
    decision = {'schema': 'DEE.PI11.reasoned_adoption_decision.R01', 'approved_for_adoption': True,
                'decision_id': facts['decision_id'], 'life_id': facts['life_id'], 'source_system': str(source),
                'source_tick': facts['source_tick'], 'source_snapshot_sha256': facts['source_snapshot_sha256'],
                'source_ordinal': facts['source_ordinal'], 'source_code_manifest': source_manifest,
                'gates': gates, 'proofs': proofs, 'approved_code_files': rows, 'selectors_cas': selectors,
                'catalog_entry': copy.deepcopy(facts['catalog_entry']), 'new_contract': contract,
                'process_proof': str(process), 'sealed_criterion': sealed,
                'evidence': [normalized_ref(ref) for ref in facts['evidence']],
                **{key: copy.deepcopy(facts[key]) for key in NARRATIVE}}
    payloads['DECISION_ADOPCION_PI11_R01.json'] = encoded(decision)
    report = {'schema': 'DEE.PI11.pure_final_adoption_compilation.R01', 'phase': 'PREPARED_DIAGNOSTIC_NOT_MOVED_NOT_COMMITTED',
              'source_life_id': facts['life_id'], 'source_tick': facts['source_tick'],
              'source_card_sha256': digest(source / 'estado/vidas' / facts['life_id'] / 'VIDA.json'),
              'source_snapshot_sha256': card['snapshot_sha256'], 'five_product_R02_overrides': sorted(overrides),
              'approved_code_count': len(rows), 'source_manifest_files_checked': len(originals),
              'selectors_cas': selectors, 'process_proof_sha256': digest(process),
              'files': {name: hashlib.sha256(content).hexdigest() for name, content in payloads.items()},
              'Native_executed': False, 'new_Native_ticks': 0, 'DEE_imported': False,
              'SQLite_opened': False, 'source_written': False, 'product_written': False,
              'adoption_claimed': False,
              'next': 'Root reviews final decision, runs pi11_adoptar_R01.py --decision FILE read-only, then supplies fresh process proof and exact decision SHA for any separately authorized move.'}
    payloads['PREPARACION_PURA_R01.json'] = encoded(report)
    return decision, report, payloads


def schema():
    ref = {'path': 'ABSOLUTE_EXISTING_PI11_JSON', 'sha256': 'ACTUAL_SHA256', 'checks': {'/ACTUAL_FIELD': None}}
    return {'basis': {'schema': 'DEE.PI11.explicit_closed_source_basis_facts.R01', 'source_system': 'ACTUAL_MAIN_SYSTEM',
                      'source_life_id': MAIN, 'source_tick': None, 'source_snapshot_sha256': None, 'source_closed_proof': ref},
            'decision': {'schema': 'DEE.PI11.explicit_adoption_generation_facts.R01', 'approved_for_adoption': False,
                         'decision_id': 'ROOT_EXPLICIT_FINAL_ID', 'life_id': MAIN, 'source_system': 'ACTUAL_MAIN_SYSTEM',
                         'source_tick': None, 'source_snapshot_sha256': None, 'source_ordinal': None, 'PI10_history_sha256': None,
                         'source_code_manifest': {k: v for k, v in ref.items() if k != 'checks'},
                         'product_code': str(H / 'PRODUCTO_PREPARADO_R02'),
                         'sealed_criterion': ref, 'gates': {name: {'satisfied': None, 'criterion': None, 'result': None, 'evidence': []} for name in GATES},
                         'proofs': {name: copy.deepcopy(ref) for name in PROOFS}, 'evidence': [],
                         'catalog_entry': {'id': 'ROOT_REVIEWED_ID'}, 'process_proof': 'ACTUAL_FRESH_SCOPED_CLOSED_PROCESS_PROOF',
                         **{key: None for key in NARRATIVE}}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--schema', action='store_true')
    group.add_argument('--basis-facts', type=Path)
    group.add_argument('--decision-facts', type=Path)
    ap.add_argument('--output-dir', type=Path)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    if args.schema:
        need(not args.write, 'Schema printing never writes')
        print(json.dumps(schema(), ensure_ascii=False, indent=2)); return
    output = local(args.output_dir, H, False) if args.output_dir else None
    need(not args.write or output is not None, 'Explicit new output directory under codigo required for writing')
    if output:
        need(output != H.resolve() and not output.exists(), 'New, previously nonexistent codigo child output directory required')
    facts_file = local(args.basis_facts or args.decision_facts)
    facts_hash = digest(facts_file)
    facts = read(facts_file)
    if args.basis_facts:
        result = basis(facts)
        payloads = {'BASE_CIENTIFICA_CERRADA_INTERFAZ_PI11_R01.json': encoded(result)}
        report = {'basis': result, 'writes': 0}
    else:
        need(output is not None, '--output-dir is needed to bind future exact contract source locators even in preview')
        _, report, payloads = compile_decision(facts, output)
    need(digest(facts_file) == facts_hash, 'Executive final facts changed during compilation')
    if args.write:
        output.mkdir(parents=False, exist_ok=False)
        for name, content in payloads.items():
            path = output / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as f:
                f.write(content)
        report = {**report, 'output_dir': str(output), 'files_written': len(payloads)}
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
