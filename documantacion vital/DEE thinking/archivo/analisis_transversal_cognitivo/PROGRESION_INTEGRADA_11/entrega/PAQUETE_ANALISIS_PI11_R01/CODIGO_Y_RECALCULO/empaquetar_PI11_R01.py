"""Root-selected literal PI11 analysis package; no Native or product writes.

This helper is not a scientific selector. It only packages an explicit closed
selection, stages byte-identical files, makes one Deflate ZIP <=15,000,000B,
extracts into a new sibling directory and checks every byte. Only pure scripts
explicitly listed in selection.recalculations are run, under isolated bundled
Python. No discovered/archived script is executed automatically. A constrained
AST/import check is a guard, not a claim of a general Python security sandbox.

Input schema DEE.PI11.analysis_package_selection.R01:
  closed_for_packaging:true;
  files:[{source:ABSOLUTE,target:POSIX_RELATIVE,sha256:HEX}];
  expected_manual:{target:RELATIVE,sha256:HEX};
  expected_compendium:{target:RELATIVE,sha256:HEX};
  recalculations:[{script:RELATIVE,args:[STR,...],timeout_seconds:60}].

Only --selection, --stage NEW_DIRECTORY and --zip NEW_FILE are required.
The clean extraction is STAGE_NAME_EXTRACCION_VERIFICADA beside STAGE.
One external report is ZIP_NAME.VERIFICACION.json. No overwrite or deletion.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse
import ast
import csv
import hashlib
import io
import json
import os
import re
import stat
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
LIMIT = 15_000_000
MANIFEST = '05_CONTROL/MANIFIESTO_SHA256.json'
PYTHON = Path(r'C:\Users\Erik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe')
ALLOWED_IMPORTS = {
    '__future__', 'argparse', 'array', 'collections', 'copy', 'csv', 'datetime',
    'decimal', 'fractions', 'gzip', 'hashlib', 'io', 'itertools', 'json', 'math',
    'pathlib', 're', 'statistics', 'struct', 'sys', 'typing', 'xml', 'zipfile', 'zlib',
}
TEXT_EXTENSIONS = {'.txt', '.md', '.py', '.srt', '.jsonl', '.bat', '.patch', '.diff', '.yaml', '.yml'}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def regular_path(path, must_exist=True, directory=False):
    p = Path(path).absolute()
    for node in (p, *p.parents):
        need(not node.is_symlink(), 'Symlink path refused: ' + str(node))
        if node.exists():
            need(not (getattr(node.lstat(), 'st_file_attributes', 0) & 1024),
                 'Symlink/reparse path refused: ' + str(node))
    if must_exist:
        need(p.is_dir() if directory else p.is_file(), 'Required regular source/directory missing: ' + str(p))
    return p.resolve(strict=must_exist)


def local_output(path, directory=False):
    p = regular_path(path, False, directory)
    need(p.is_relative_to(R.resolve()), 'Output must remain in this DEE thinking project')
    need(not p.exists(), 'Existing output is preserved: ' + str(p))
    regular_path(p.parent, True, True)
    return p


def target_path(value):
    need(isinstance(value, str) and value and '\\' not in value and '\x00' not in value,
         'Nonempty POSIX relative target required')
    p = PurePosixPath(value)
    need(bool(p.parts) and value != '.' and not p.is_absolute() and value == p.as_posix()
         and all(part not in ('', '.', '..') and ':' not in part for part in p.parts),
         'Unsafe package member target: ' + value)
    need(not any(part.endswith((' ', '.')) for part in p.parts), 'Ambiguous Windows target')
    reserved = {'CON', 'PRN', 'AUX', 'NUL', *('COM' + str(i) for i in range(1, 10)), *('LPT' + str(i) for i in range(1, 10))}
    need(all(part.split('.')[0].upper() not in reserved for part in p.parts), 'Windows reserved member name')
    return p.as_posix()


def sha_string(value):
    need(isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value), 'Lowercase SHA256 required')
    return value


def reject_duplicate_json(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def load_json_bytes(data):
    return json.loads(data.decode('utf-8-sig'), object_pairs_hook=reject_duplicate_json)


def document_check(data, label):
    """Read package contents only. No macros, external links or fields execute."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        need(z.testzip() is None, 'DOCX CRC failure: ' + label)
        names = z.namelist()
        need(len(names) == len(set(names)), 'Duplicate DOCX package members')
        need({'[Content_Types].xml', 'word/document.xml', 'docProps/core.xml'} <= set(names), 'Complete DOCX package required')
        xml_members = 0
        for name in names:
            if name.endswith(('.xml', '.rels')):
                ET.fromstring(z.read(name))
                xml_members += 1
        body = ET.fromstring(z.read('word/document.xml'))
        texts = ''.join(n.text or '' for n in body.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
        need(bool(texts.strip()), 'Empty DOCX body refused')
        return {'format': 'docx', 'member_CRC': True, 'XML_members_parsed': xml_members,
                'complete_literal_source_copy': True, 'visual_review_implied': False}


def readable_check(path, target):
    data = Path(path).read_bytes()
    extension = PurePosixPath(target).suffix.lower()
    if extension == '.docx':
        return document_check(data, target)
    if extension == '.json':
        load_json_bytes(data)
        return {'format': 'json', 'UTF8_readable': True, 'duplicate_keys_rejected': True}
    if extension == '.csv':
        rows = list(csv.reader(io.StringIO(data.decode('utf-8-sig'), newline=''), strict=True))
        need(bool(rows), 'Empty CSV refused: ' + target)
        need(len({len(row) for row in rows}) == 1, 'CSV row widths differ: ' + target)
        return {'format': 'csv', 'UTF8_readable': True, 'rows': len(rows), 'columns': len(rows[0])}
    if extension in TEXT_EXTENSIONS:
        text = data.decode('utf-8-sig')
        if extension == '.jsonl':
            for line in text.splitlines():
                if line.strip():
                    load_json_bytes(line.encode('utf8'))
        return {'format': extension.lstrip('.'), 'UTF8_readable': True}
    return {'format': extension.lstrip('.') or 'binary', 'bytes_hash_verified': True}


def pure_script_check(path):
    """Reject motor/Native/process/network imports; Root remains code reviewer."""
    source = Path(path).read_text('utf-8-sig')
    tree = ast.parse(source, filename=str(path))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            need(node.level == 0 and node.module is not None, 'Relative imports refused in selected pure recalculation')
            imports.append(node.module)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                need(node.func.id not in {'eval', 'exec', 'compile', '__import__', 'breakpoint'},
                     'Dynamic interpreter call refused in pure recalculation')
            elif isinstance(node.func, ast.Attribute):
                need(node.func.attr not in {'exec_module', 'load_module', 'system', 'popen', 'spawn', 'run_module', 'run_path'},
                     'Dynamic/process call refused in pure recalculation')
        elif isinstance(node, ast.Attribute):
            need(not (isinstance(node.value, ast.Name) and node.value.id == 'sys' and node.attr in {'path', 'meta_path', 'modules'}),
                 'Import environment mutation refused')
    need(all(name.split('.')[0] in ALLOWED_IMPORTS for name in imports), 'Non-approved import in pure script: ' + repr(imports))
    return {'imports': sorted(set(imports)), 'AST_import_guard_passed': True, 'Root_explicit_selection': True,
            'security_sandbox_claimed': False}


def validate_selection(selection_path, stage, zip_path):
    source = regular_path(selection_path)
    need(source.is_relative_to(R.resolve()), 'Selection must be a local DEE campaign artifact')
    selection = load_json_bytes(source.read_bytes())
    need(selection.get('schema') == 'DEE.PI11.analysis_package_selection.R01'
         and selection.get('closed_for_packaging') is True, 'Root closed explicit scientific selection required')
    rows = selection.get('files')
    need(isinstance(rows, list) and rows, 'Explicit nonempty files selection required')
    seen = set()
    files = []
    for row in rows:
        need(set(row) == {'source', 'target', 'sha256'}, 'File rows require exactly source,target,sha256')
        need(Path(row['source']).is_absolute(), 'Absolute source path required')
        src = regular_path(row['source'])
        need(src.is_relative_to(R.resolve()), 'Non-DEE source refused')
        target = target_path(row['target'])
        key = target.casefold()
        need(key not in seen and key != MANIFEST.casefold(), 'Duplicate or reserved manifest target')
        need(src.suffix.lower() != '.zip' and PurePosixPath(target).suffix.lower() != '.zip', 'No nested historical ZIPs')
        need(not src.is_relative_to(stage) and src != zip_path, 'Output cannot be its own input')
        seen.add(key)
        expected = sha_string(row['sha256'])
        need(digest(src) == expected, 'Current source differs from explicit selection: ' + str(src))
        files.append({'source': str(src), 'target': target, 'sha256': expected, 'bytes': src.stat().st_size})
    by_target = {row['target']: row for row in files}
    all_targets = {*seen, MANIFEST.casefold()}
    for name in all_targets:
        need(not any(parent.as_posix() != '.' and parent.as_posix().casefold() in all_targets
                     for parent in PurePosixPath(name).parents), 'A selected file conflicts with a target directory')
    for field in ('expected_manual', 'expected_compendium'):
        expected = selection.get(field)
        need(isinstance(expected, dict) and set(expected) == {'target', 'sha256'}, 'Explicit complete ' + field + ' required')
        t = target_path(expected['target'])
        need(t in by_target and PurePosixPath(t).suffix.lower() == '.docx'
             and sha_string(expected['sha256']) == by_target[t]['sha256'], 'Full literal DOCX absent from selection: ' + field)
        document_check(Path(by_target[t]['source']).read_bytes(), t)
    need(selection['expected_manual']['target'] != selection['expected_compendium']['target'], 'Manual and Compendium are distinct documents')
    recalculations = selection.get('recalculations')
    need(isinstance(recalculations, list), 'Explicit recalculations list, possibly empty, required')
    checks = []
    for entry in recalculations:
        need(isinstance(entry, dict) and {'script', 'args'} <= set(entry)
             and set(entry) <= {'script', 'args', 'timeout_seconds'}, 'Unexpected recalculation entry')
        script = target_path(entry['script'])
        need(script in by_target and script.endswith('.py'), 'Recalculation must be an explicitly selected .py member')
        need(isinstance(entry['args'], list) and all(isinstance(arg, str) and '\x00' not in arg for arg in entry['args']),
             'Explicit argument string list required; no shell command')
        need(all(not Path(arg).is_absolute() and not re.match(r'^[A-Za-z]:', arg)
                 and '..' not in arg.replace('\\', '/').split('/') for arg in entry['args']),
             'Clean-extraction recalculation arguments must not depend on absolute/external paths')
        timeout = entry.get('timeout_seconds', 60)
        need(type(timeout) is int and 1 <= timeout <= 180, 'Bounded pure recalculation timeout1..180seconds')
        guard = pure_script_check(by_target[script]['source'])
        checks.append({'script': script, 'args': entry['args'], 'timeout_seconds': timeout, 'source_guard': guard})
    if checks:
        regular_path(PYTHON)
    return source, selection, files, checks


def write_new_json(path, value):
    data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')
    with Path(path).open('xb') as f:
        f.write(data)
    return data


def safe_copy(row, stage):
    src = regular_path(row['source'])
    need(digest(src) == row['sha256'] and src.stat().st_size == row['bytes'], 'Source changed before copy')
    target = stage.joinpath(*PurePosixPath(row['target']).parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    with src.open('rb') as inp, target.open('xb') as out:
        for chunk in iter(lambda: inp.read(1024 * 1024), b''):
            out.write(chunk)
        out.flush()
        os.fsync(out.fileno())
    need(digest(src) == row['sha256'] and digest(target) == row['sha256']
         and target.stat().st_size == row['bytes'], 'Source/destination CAS mismatch')
    return readable_check(target, row['target'])


def seal_zip(stage, zip_path, members):
    with zipfile.ZipFile(zip_path, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=False) as z:
        for name in sorted(members):
            z.write(stage.joinpath(*PurePosixPath(name).parts), arcname=name)
    need(zip_path.stat().st_size <= LIMIT, 'ZIP exceeds strict15,000,000byte limit; preserve it and revise selection prospectively')


def clean_extract(zip_path, destination, expected):
    destination.mkdir()
    with zipfile.ZipFile(zip_path) as z:
        need(z.testzip() is None, 'Final ZIP CRC failure')
        members = z.infolist()
        names = [target_path(m.filename) for m in members]
        need(len(names) == len(set(name.casefold() for name in names)) and set(names) == set(expected), 'Unexpected/duplicate final ZIP members')
        need(sum(m.file_size for m in members) <= 1_000_000_000, 'Bounded clean extraction required')
        for m in members:
            need(not m.is_dir() and m.compress_type == zipfile.ZIP_DEFLATED and not (m.flag_bits & 1), 'Only regular unencrypted Deflate members')
            mode = m.external_attr >> 16
            need(not stat.S_ISLNK(mode), 'Symlink ZIP member refused')
            name = m.filename
            target = destination.joinpath(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(m) as inp, target.open('xb') as out:
                for chunk in iter(lambda: inp.read(1024 * 1024), b''):
                    out.write(chunk)
            need(target.stat().st_size == expected[name]['bytes'] and digest(target) == expected[name]['sha256'],
                 'Clean extraction hash differs: ' + name)
    return {name: readable_check(destination.joinpath(*PurePosixPath(name).parts), name) for name in expected}


def run_pure_checks(entries, extraction):
    results = []
    for entry in entries:
        script = extraction.joinpath(*PurePosixPath(entry['script']).parts)
        guard = pure_script_check(script)
        command = [str(PYTHON), '-I', '-B', '-X', 'utf8', str(script), *entry['args']]
        try:
            r = subprocess.run(command, cwd=extraction, stdin=subprocess.DEVNULL, capture_output=True,
                               text=True, encoding='utf8', errors='strict', timeout=entry['timeout_seconds'], check=False)
            result = {'script': entry['script'], 'args': entry['args'], 'command': command,
                      'returncode': r.returncode, 'passed': r.returncode == 0,
                      'stdout': r.stdout[:24000], 'stderr': r.stderr[:12000],
                      'stdout_truncated': len(r.stdout) > 24000, 'stderr_truncated': len(r.stderr) > 12000,
                      'guard': guard, 'new_native_ticks': 0, 'mode': 'Root-selected passive documentary recalculation'}
        except subprocess.TimeoutExpired:
            result = {'script': entry['script'], 'args': entry['args'], 'passed': False,
                      'timeout_seconds': entry['timeout_seconds'], 'mode': 'bounded passive recalculation timed out'}
        results.append(result)
    return results


def package(args):
    stage = local_output(args.stage, True)
    zip_path = local_output(args.zip)
    need(zip_path.suffix.lower() == '.zip', 'A new standard .zip output required')
    need(not zip_path.is_relative_to(stage), 'ZIP must remain outside staging to avoid recursive packaging')
    extraction = local_output(stage.with_name(stage.name + '_EXTRACCION_VERIFICADA'), True)
    report_path = local_output(zip_path.with_name(zip_path.name + '.VERIFICACION.json'))
    selection_path, selection, files, recalculations = validate_selection(args.selection, stage, zip_path)
    selection_sha = digest(selection_path)
    need(not stage.exists() and not zip_path.exists() and not extraction.exists() and not report_path.exists(), 'Outputs appeared concurrently')
    stage.mkdir()
    initial_checks = {row['target']: safe_copy(row, stage) for row in files}
    manifest_path = stage.joinpath(*PurePosixPath(MANIFEST).parts)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    content = {row['target']: {'bytes': row['bytes'], 'sha256': row['sha256']} for row in files}
    manifest = {'schema': 'DEE.PI11.analysis_package_content_hashes.R01',
                'selection_sha256': selection_sha, 'files': content,
                'manifest_itself_excluded': True, 'ZIP_hash_not_inside_container': True,
                'literal_complete_manual': selection['expected_manual'],
                'literal_complete_compendium': selection['expected_compendium']}
    manifest_data = write_new_json(manifest_path, manifest)
    expected = {**content, MANIFEST: {'bytes': len(manifest_data), 'sha256': hashlib.sha256(manifest_data).hexdigest()}}
    seal_zip(stage, zip_path, expected)
    checks = clean_extract(zip_path, extraction, expected)
    runs = run_pure_checks(recalculations, extraction)
    # Recalculations may create declared result files but cannot alter evidence.
    unchanged = all(digest(extraction.joinpath(*PurePosixPath(name).parts)) == item['sha256']
                    and digest(stage.joinpath(*PurePosixPath(name).parts)) == item['sha256'] for name, item in expected.items())
    need(unchanged, 'Pure recalculation changed packaged content; result preserved for diagnosis')
    source_checks = []
    for row in files:
        equal = digest(regular_path(row['source'])) == row['sha256']
        source_checks.append({'source': row['source'], 'target': row['target'], 'sha256_still_equal': equal})
    need(digest(selection_path) == selection_sha, 'Selection changed during packaging')
    with zipfile.ZipFile(zip_path) as z:
        need(z.testzip() is None, 'Post-recalculation final ZIP CRC failure')
        for name, item in expected.items():
            need(hashlib.sha256(z.read(name)).hexdigest() == item['sha256'], 'Reopened final ZIP member differs')
    passed = all(r['passed'] for r in runs) and all(r['sha256_still_equal'] for r in source_checks)
    report = {'schema': 'DEE.PI11.analysis_package_external_verification.R01',
              'at': datetime.now(timezone.utc).isoformat(), 'status': 'VERIFIED' if passed else 'FAILED_PRESERVED',
              'ZIP': {'path': str(zip_path), 'bytes': zip_path.stat().st_size, 'sha256': digest(zip_path),
                      'strict_limit_bytes': LIMIT, 'within_limit': zip_path.stat().st_size <= LIMIT,
                      'format': 'standard ZIP Deflate, no encryption, no volumes', 'CRC_all_members': True,
                      'members': len(expected), 'hashes_all_members_match': True},
              'selection': {'path': str(selection_path), 'sha256': selection_sha},
              'stage': str(stage), 'clean_extraction': str(extraction), 'clean_extraction_checks': checks,
              'source_CAS_checks': source_checks, 'manual': selection['expected_manual'],
              'compendium': selection['expected_compendium'], 'recalculations': runs,
              'no_unlisted_script_executed': True, 'packaged_content_unchanged_after_checks': unchanged,
              'new_native_ticks': 0, 'new_experiments': False, 'operational_backup_claimed': False,
              'original_sources_modified_by_packager': False,
              'staging_initial_legibility_checks': initial_checks}
    write_new_json(report_path, report)
    print(json.dumps({'status': report['status'], 'ZIP': report['ZIP'], 'external_report': str(report_path),
                      'clean_extraction': str(extraction), 'pure_checks_passed': sum(r['passed'] for r in runs),
                      'pure_checks_total': len(runs)}, ensure_ascii=False))
    return 0 if passed else 2


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--selection', type=Path, required=True)
    ap.add_argument('--stage', type=Path, required=True)
    ap.add_argument('--zip', type=Path, required=True)
    raise SystemExit(package(ap.parse_args()))
