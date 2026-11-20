"""Post-trajectory static information-boundary inventory, not a cognition verdict.

AST inventory cannot prove semantic independence. The narrow automatic checks
detect old-runtime imports and direct physical setters in the public MAIN layer;
the report separately records the human agent's directed data-flow review.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CORE = ('common.py', 'order_memory.py', 'action_feedback.py',
        'action_feedback_access.py', 'language.py', 'integrated.py',
        'curriculum.py', 'consolidation.py', 'order_language.py', 'balanced_sources.py', 'word_bus.py')
PUBLIC = ('ejecutar.py', 'app.py')
RISK_NAMES = {'set_raw', 'set_clock', 'diagnostic_fork', 'ResearchStateEdit',
              'load_snapshot', 'read_text', 'read_bytes', 'open', 'loads',
              'load', 'eval', 'exec', 'compile', 'import_module'}
FORBIDDEN_IMPORTS = ('dee_universe', 'CPC3', 'CPC4', 'CPC5', 'SEM01', 'frontiers')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dotted(node):
    if isinstance(node, ast.Name): return node.id
    if isinstance(node, ast.Attribute): return dotted(node.value) + '.' + node.attr
    if isinstance(node, ast.Call): return dotted(node.func) + '(...)'
    return type(node).__name__


def inspect(path):
    source = path.read_text(encoding='utf-8-sig'); tree = ast.parse(source)
    imports = []; calls = []; strings = []; forbidden = []; setters = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [x.name for x in node.names] if isinstance(node, ast.Import) else [node.module or '']
            for name in names:
                imports.append({'line': node.lineno, 'module': name})
                if any(name == old or name.startswith(old + '.') for old in FORBIDDEN_IMPORTS): forbidden.append(imports[-1])
        elif isinstance(node, ast.Call):
            name = dotted(node.func); leaf = name.rsplit('.', 1)[-1]
            if leaf in RISK_NAMES: calls.append({'line': node.lineno, 'call': name, 'source': ast.get_source_segment(source, node)})
            if leaf in {'set_raw', 'set_clock', 'eval', 'exec', 'compile'}: setters.append({'line': node.lineno, 'call': name})
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            if re.search(r'[A-Za-z]:[\\/]', value) or any(x in value.lower() for x in ('target', 'expected', 'resultados', 'mapa', 'lookup', 'teaching')):
                strings.append({'line': node.lineno, 'value': value[:1200], 'truncated': len(value) > 1200})
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path),
            'imports': imports, 'boundary_related_calls': calls,
            'boundary_related_strings': strings, 'forbidden_old_runtime_imports': forbidden,
            'direct_setters_or_dynamic_code': setters}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--require-public', action='store_true')
    args = parser.parse_args(); rows = [inspect(ROOT / 'src' / name) for name in CORE]
    missing = []
    for name in PUBLIC:
        path = ROOT / name
        if path.is_file(): rows.append(inspect(path))
        else: missing.append(name)
    checks = {'no_previous_runtime_imports_in_reviewed_layer': not any(x['forbidden_old_runtime_imports'] for x in rows),
              'no_direct_RAW_clock_setters_or_dynamic_code_in_reviewed_layer': not any(x['direct_setters_or_dynamic_code'] for x in rows),
              'public_files_present': not missing}
    data = {'schema': 'CPC6.host-boundaries.v1', 'classification': 'STATIC_INSTRUMENT_AUDIT',
       'instrument_only': True, 'no_output_returned_to_participant': True,
       'static_cutoff_scope': 'Source inventory at the listed hashes; does not assert that all campaign trajectories had already completed.',
       'source_sha256': sha(Path(__file__)),
       'checks': checks, 'files': rows, 'missing_public_files': missing,
       'directed_manual_review': [
          {'layer': 'preparation', 'files': ['order_memory.py', 'action_feedback.py', 'consolidation.py'],
           'finding': 'Prepared support, finite branch geometry and opportunities are supplied by the designer at T0. Source data values are current environmental observations, not computed future outcomes or corrected policies.'},
          {'layer': 'MAIN transport', 'files': ['integrated.py', 'curriculum.py', 'action_feedback_access.py'],
           'finding': 'Only declared input/probe scheduling, native advance, passive read, native fork and complete save/load. Alias de-duplication examines identical public physical interface declarations, payload, tick and modality; it does not inspect learned state or pick a successful branch.'},
          {'layer': 'response', 'files': ['language.py', 'order_language.py'],
           'finding': 'The decoder emits actual active semantic1 records having the frozen direction sector, or an empty list. No history-to-meaning map, expected response or stored terminal measurement is read. Text is a fixed rendering of measured fields, not an arbitrary learned semantic dictionary.'},
          {'layer': 'persistence', 'files': ['integrated.py'],
           'finding': 'Session JSON stores public geometry, identity, request IDs and tick in native metadata. Native physical/operative snapshot is loaded without preparing a new body. Snapshot metadata is not a response cache.'},
          {'layer': 'auditor versus participant', 'finding': 'Scientific runners/analyses may read configurations and compare evaluator references after trajectories; they are not imported as hidden deciders by the reviewed MAIN core. Fixed R14 policy normalizers are a finite prepared controller, distinct from learned optimal regulation.'}],
       'limitations': ['AST cannot establish causal utilization, acquisition, retention or absence of every possible information leak.',
          'Boundary-related calls and strings are retained for review rather than silently approved.',
          'Changing any source changes its hash and requires regenerating this inventory. Native mechanisms still require measured controls and exact clean reproduction.'],
       'status': 'REVIEWED_STATIC_BOUNDARIES' if all(checks.values()) else 'INCOMPLETE_OR_REVIEW_REQUIRED'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': data['status'], 'files': len(rows), 'checks': checks}))
    assert checks['no_previous_runtime_imports_in_reviewed_layer'] and checks['no_direct_RAW_clock_setters_or_dynamic_code_in_reviewed_layer']
    if args.require_public: assert checks['public_files_present']


if __name__ == '__main__': main()
