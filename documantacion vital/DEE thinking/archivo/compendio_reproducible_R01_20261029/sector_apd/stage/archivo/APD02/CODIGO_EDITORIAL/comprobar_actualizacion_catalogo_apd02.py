"""N0 documentary comparison; does not load DEE or modify the catalog."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    lab = a.root / 'laboratorio/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION'
    before = lab / 'historia_sistema_R04_CIERRE/CATALOGO_CAPACIDADES.json'
    after = a.root / 'sistema/capacidades/CATALOGO_CAPACIDADES.json'
    b = json.loads(before.read_text(encoding='utf-8-sig'))
    c = json.loads(after.read_text(encoding='utf-8-sig'))
    changes = [i for i, (x, y) in enumerate(zip(b['entries'], c['entries'])) if x != y]
    same_top = {k: b.get(k) == c.get(k) for k in set(b) | set(c) if k != 'entries'}
    report = {
        'schema': 'APD02.catalog_documentary_change.v1',
        'before': str(before.relative_to(a.root)), 'before_sha256': digest(before),
        'after': str(after.relative_to(a.root)), 'after_sha256': digest(after),
        'entries_before': len(b['entries']), 'entries_after': len(c['entries']),
        'changed_indices': changes,
        'unaffected_entries_exact_JSON_value': b['entries'][1:] == c['entries'][1:],
        'unaffected_entries_count': len(b['entries'][1:]),
        'other_top_level_values_equal': same_top,
        'interpretation': 'Documentary availability and scope only; not proof that all catalog capabilities belong to one life.',
        'new_native_ticks': 0,
    }
    if len(b['entries']) != len(c['entries']) or changes != [0] or not all(same_top.values()):
        raise RuntimeError('Unexpected catalog change; no files altered')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open('x', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
