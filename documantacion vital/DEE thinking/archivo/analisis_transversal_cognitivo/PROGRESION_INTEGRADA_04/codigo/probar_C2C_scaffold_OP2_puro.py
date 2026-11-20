"""Fake filesystem/AST tests only; no DEE import, world, tick or real resource."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import sys

P = Path(__file__).resolve().parents[1]
SRC = P / 'codigo/PI04_C2C_SCAFFOLD_OP2/pi04_coordinacion_central_C2C.py'
BASE = SRC.with_name('pi04_coordinacion_central_C2C_ANTES_OP1.py')
FIX = P / 'control/C2C_OP2_PURE_FIXTURES_R01'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def files(home): return {p.relative_to(home).as_posix(): sha(p) for p in home.rglob('*') if p.is_file()}
def dirs(home): return sorted(p.relative_to(home).as_posix() for p in home.rglob('*') if p.is_dir())


def remove_fake_empty_directories(home):
    for name in ('inflight_minus', 'inflight_plus', 'inflight_silence', 'consumed', 'rejected', 'products'):
        d = home / name
        if not d.resolve().is_relative_to(FIX.resolve()) or d.is_symlink(): raise ValueError('Pure fixture boundary')
        d.rmdir()  # Only these newly generated, known empty test directories.


def functions(tree):
    out = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef): out[node.name] = ast.dump(node, include_attributes=False)
        if isinstance(node, ast.ClassDef):
            for method in node.body:
                if isinstance(method, ast.FunctionDef): out[node.name + '.' + method.name] = ast.dump(method, include_attributes=False)
    return out


def native_calls(tree):
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_opportunity_body')
    wanted = {'a.run_until', '_helper().submit_query', '_helper().submit_motor_copy',
        '_sensor().submit_datum', 'arithmetic_api.execute', 'mu.current',
        '_helper().submit_generic_outcome', 'device.begin', 'device.complete', 'device.feedback', 'device.reconcile'}
    return [ast.unparse(n.func) for n in ast.walk(function) if isinstance(n, ast.Call) and ast.unparse(n.func) in wanted]


def main():
    if FIX.exists(): raise ValueError('Do not overwrite fake fixtures/proof')
    before_imports = set(sys.modules)
    spec = importlib.util.spec_from_file_location('C2C_OP2_FAKE_FILESYSTEM_ONLY', SRC)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    FIX.mkdir()
    original = ast.parse(BASE.read_text(encoding='utf8'))
    proposed = ast.parse(SRC.read_text(encoding='utf8'))
    old_functions, new_functions = functions(original), functions(proposed)
    changed = [name for name in old_functions if old_functions[name] != new_functions[name]]
    assert changed == ['_opportunity_body']
    assert native_calls(original) == native_calls(proposed)
    assert all(old_functions[n] == new_functions[n] for n in ('Device.__init__', 'state', 'operational_dependencies', 'Device.begin', 'Device.complete', '_motor', '_operation'))
    env = {'context_cut': 4, 'low_operation': 'diferencia', 'high_operation': 'suma',
        'numeric_cut': 20, 'low_route': -1, 'high_route': 1, 'resource_bytes': 64}
    home = FIX / 'missing_empty_dirs_fake'
    m.Device.prepare(home, 3, env)
    remove_fake_empty_directories(home)
    literal_before, dirs_before = files(home), dirs(home)
    d = m.Device(home)
    assert files(home) == literal_before and dirs(home) == dirs_before
    preparation = d.ensure_schema_directories()
    assert preparation['created_directories'] == ['inflight_minus', 'inflight_plus', 'inflight_silence', 'consumed', 'rejected', 'products']
    assert files(home) == literal_before
    after = files(home); again = d.ensure_schema_directories()
    assert again['created_directories'] == [] and files(home) == after
    intent = d.begin(-1, 'diferencia', 7, 2, 10, 20)
    assert intent['phase'] == 'inflight' and (home / 'inflight_minus/0000.resource').is_file()
    assert not (home / 'reservoir/0000.resource').exists()
    # Missing resource never becomes a new resource; every mkdir must wait.
    lost_home = FIX / 'missing_resource_fake'
    m.Device.prepare(lost_home, 2, env); remove_fake_empty_directories(lost_home)
    (lost_home / 'reservoir/0001.resource').replace(FIX / 'preserved_missing_resource.bin')
    lost_files, lost_dirs = files(lost_home), dirs(lost_home)
    refused_missing = False
    try: m.Device(lost_home).ensure_schema_directories()
    except ValueError as e: refused_missing = 'no regeneration' in str(e)
    assert refused_missing and files(lost_home) == lost_files and dirs(lost_home) == lost_dirs
    bad_home = FIX / 'altered_resource_fake'
    m.Device.prepare(bad_home, 1, env); remove_fake_empty_directories(bad_home)
    (bad_home / 'reservoir/0000.resource').write_bytes(b'fake-altered-content')
    bad_files, bad_dirs = files(bad_home), dirs(bad_home)
    refused_bad = False
    try: m.Device(bad_home).ensure_schema_directories()
    except ValueError as e: refused_bad = 'no regeneration' in str(e)
    assert refused_bad and files(bad_home) == bad_files and dirs(bad_home) == bad_dirs
    obstacle_home = FIX / 'file_in_directory_place_fake'
    m.Device.prepare(obstacle_home, 1, env); remove_fake_empty_directories(obstacle_home)
    (obstacle_home / 'products').write_bytes(b'fake-file-not-directory')
    obstacle_files, obstacle_dirs = files(obstacle_home), dirs(obstacle_home)
    refused_obstacle = False
    try: m.Device(obstacle_home).ensure_schema_directories()
    except ValueError as e: refused_obstacle = 'regular file occupies' in str(e)
    assert refused_obstacle and files(obstacle_home) == obstacle_files and dirs(obstacle_home) == obstacle_dirs
    forbidden = [n for n in set(sys.modules) - before_imports if n == 'app' or n.startswith(('app.', 'dee', 'DEE', 'numpy'))]
    assert not forbidden
    proof = {'schema': 'PI04.C2C.OP2.pure_filesystem_AST.v1', 'mode': 'FAKE_FIXTURES_AND_AST_NOT_NATIVE',
        'candidate': str(SRC), 'candidate_sha256': sha(SRC), 'preserved_base_literal_sha256': sha(BASE),
        'preserved_base_LF_sha256': hashlib.sha256(BASE.read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
        'changed_existing_functions': changed, 'only_added_method': 'Device.ensure_schema_directories',
        'Native_and_device_action_call_order_AST_identical': native_calls(original) == native_calls(proposed),
        'constructor_state_dependencies_and_actual_device_effect_AST_unchanged': True,
        'constructor_read_only_on_missing_directories': True, 'missing_fixed_directories_created': preparation['created_directories'],
        'original_state_resources_content_unchanged_by_ensure': True, 'second_ensure_no_writes': again['created_directories'] == [],
        'fake_begin_can_move_original_resource_after_schema': intent['phase'] == 'inflight',
        'missing_resource_refused_before_first_mkdir': refused_missing,
        'altered_resource_refused_without_content_repair': refused_bad,
        'file_in_fixed_directory_refused_without_overwrite': refused_obstacle,
        'forbidden_imports': forbidden, 'Native_ticks': 0, 'S2_or_product_modified': False,
        'failed_CTX01_retried': False,
        'limits': 'Host filesystem scaffolding P0 only. These generated fake resources are not experiment outcomes or Native products. Root must apply only after owners close, then execute a NEW control from the original PostDEV prefix and compare actual Native witnesses.'}
    out = P / 'control/C2C_SCAFFOLD_OP2_PRUEBAS_PURAS.json'
    if out.exists(): raise ValueError('Preserve prior proof')
    out.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(proof, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
