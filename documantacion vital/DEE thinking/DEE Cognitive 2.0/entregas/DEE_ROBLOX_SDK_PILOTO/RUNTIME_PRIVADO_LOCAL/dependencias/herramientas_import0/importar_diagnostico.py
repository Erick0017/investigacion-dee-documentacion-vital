"""Material phase1: explicit complete-pair import in an isolated destination.

Never run by listar/verificar/recalcular. Parent supervisor waits for this
process to exit before starting a persistent owner, preserving one writer.
"""
from pathlib import Path
import argparse, hashlib, json, sys
sys.dont_write_bytecode = True

def main():
    p = argparse.ArgumentParser(); p.add_argument('--contexto', required=True); a = p.parse_args()
    ctxpath = Path(a.contexto).resolve(strict=True)
    c = json.loads(ctxpath.read_text(encoding='utf-8'))
    for item in c.get('tool_sources', []):
        tool = Path(__file__).resolve().parent / item['file']
        if hashlib.sha256(tool.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('La revisión de instrumentación cambió tras congelar el contexto; no se abre Native')
    system = Path(c['system']).resolve(strict=True); dest = ctxpath.parent
    if system != dest / 'sistema' or not c['life'].startswith('ECI02_PI03_REPRO_'):
        raise ValueError('Sólo destino e identidad diagnósticos explícitos')
    if (system / 'estado/ACTIVO.json').exists(): raise ValueError('No se importa sobre ACTIVO')
    sys.path[:0] = [str(system), str(system / 'app'), str(Path(__file__).resolve().parent)]
    from app.lives import Store
    from app.importacion_emparejada import import_pair
    from observador_pasivo import snapshot_view, compare_native
    store = Store(system)
    result = import_pair(store, c['prefix'], c['life'])
    record = store.record(c['life'])
    comparison = compare_native(snapshot_view(Path(c['prefix']) / 'VIDA.deetsnap.gz'), snapshot_view(system / record['snapshot']))
    if (system / 'estado/ACTIVO.json').exists(): raise ValueError('Importación creó indebidamente ACTIVO')
    with (dest / 'IMPORTACION_DIAGNOSTICA.json').open('x', encoding='utf-8') as f:
        json.dump({'result': result, 'comparison': comparison, 'new_native_ticks': 0,
                   'source_parent': c['prefix'], 'life': c['life'], 'principal_selected': False}, f, ensure_ascii=False, indent=2)
    print(json.dumps({'life': c['life'], 'physical': record['physical'], 'new_native_ticks': 0}))

if __name__ == '__main__': main()
