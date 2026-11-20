"""Ordinary wrapper unit test with a fake owner, not a DEE simulation."""
from pathlib import Path
import ast
import importlib.util
import json

HERE = Path(__file__).resolve().parent
OUT = HERE / 'PRUEBA_LOGICA_HELPER_CHUNKS_N0'


class WorldAdapter:
    """Only an integer/call-list mock for software restoration, no physics."""
    def __init__(self):self.tick=0;self.calls=[]
    def run_until(self, target):self.calls.append(target);self.tick=target;return ('mock-return', target)


def main():
    if OUT.exists():raise FileExistsError('The software unit test already exists')
    source = HERE / 'instrumentar_avance_chunks_apd04_r01.py'
    ast.parse(source.read_text(encoding='utf8'))
    spec = importlib.util.spec_from_file_location('prospective_owner_wrapper_software_only', source)
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    OUT.mkdir()
    owner = WorldAdapter()
    with module.owner_progress_chunks(owner, OUT / 'MOCK_PROGRESS.jsonl'):
        same = owner.run_until(0)
        final = owner.run_until(1349)
    expected = [0] + list(range(67, 1349, 67)) + [1349]
    assert owner.calls == expected and same == ('mock-return', 0) and final == ('mock-return', 1349)
    assert 'run_until' not in vars(owner)
    try:
        with module.owner_progress_chunks(owner, OUT / 'MOCK_EXCEPTION_PROGRESS.jsonl'):
            raise ValueError('deliberate software-only body exception')
    except ValueError:pass
    assert 'run_until' not in vars(owner)
    result = {'scope': 'Software-only fake integer/call-list owner; no DEE world exists in this test.',
        'Native_ticks': 0, 'Runtime_imports': 0, 'AST_checked': True,
        'same_tick_original_once': True, 'mock_future_owner_targets': expected,
        'mock_return_value_preserved': True, 'method_restored_normal_and_exception': True,
        'NOT_demonstrated': ['Native equivalence', 'real owner protocol invariance', 'physical noninterference']}
    with (OUT / 'RESULTADO_SOFTWARE_NO_FISICA.json').open('x', encoding='utf8') as stream:json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':main()
