"""Exact stopped MAIN pair for declared AUX contrasts; no Native owner/ticks."""
from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[4]
SYSTEM = ROOT / 'sistema'
TARGET = SYSTEM / 'estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01'
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/SELLO_MAIN_T639374_N0.json'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    if TARGET.exists() or OUT.exists():
        raise FileExistsError('Stopped cut already sealed; do not replace it')
    record = json.loads((SYSTEM / 'estado/vidas/APD04_MAIN/VIDA.json').read_text(encoding='utf8'))
    if (record['physical']['tick'] != 639374 or
            record['snapshot_sha256'] != '771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8'):
        raise ValueError('Another MAIN continuation exists; do not rewind or substitute')
    ui = load('current_existing_ui_for_poststop_N0', SYSTEM / 'app/usar_dee.py')
    sealer = load('existing_poststop_full_pair_N0', ROOT / 'laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/ejecutar_main_integrado_apd03_r01.py')
    pair = sealer.stopped_pair(ROOT, ui, 'APD04_MAIN', TARGET, allow_queued=False,
        scope='Exact APD04_MAIN reached stopped exploratory cut atT639374. Shared physical and environmental prefix for A/B/C histories; no AUX memory transferred into MAIN.')
    with OUT.open('x', encoding='utf8') as stream:
        json.dump(pair, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'pair': str(TARGET), 'manifest_sha256': pair['manifest_sha256'],
        'snapshot_sha256': record['snapshot_sha256'], 'tick': record['physical']['tick'],
        'verification': pair['verification'], 'new_ticks': 0}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
