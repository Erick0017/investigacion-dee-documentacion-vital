"""Fixed prospective UI/API walk. It records outputs; it never corrects them."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
import hashlib
import json
import shutil
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / 'WALK_R01_EJECUTADO'
URL = 'http://127.0.0.1:8766'
TOKEN = None


def now(): return datetime.now(timezone.utc).isoformat()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def api(path, value=None):
    req = Request(URL + path, data=None if value is None else json.dumps(value).encode(),
        headers={} if value is None else {'Content-Type': 'application/json', 'X-Genesis-Token': TOKEN})
    with urlopen(req, timeout=30) as f: return json.load(f)


def log(kind, **value):
    with (OUT / 'EVENTOS_DRIVER.jsonl').open('a', encoding='utf8') as f:
        f.write(json.dumps({'wall_utc': now(), 'kind': kind, **value}, ensure_ascii=False) + '\n')


def act(action, value=None, label=None, maximum=240):
    submitted = api('/api/action', {'action': action, 'value': value})
    log('submitted', action=action, value=value, ui_job=submitted)
    until = time.monotonic() + maximum
    while time.monotonic() < until:
        status = api('/api/status')
        found = next((r for r in status['jobs'] if r['id'] == submitted['id']), None)
        if found and found['status'] in ('completed', 'error'):
            log('completed_interface_job', action=action, ui_job=found)
            if label: write(label + '.json', {'job': found, 'status': status, 'frame': api('/api/frame')})
            return found, status
        time.sleep(.2)
    raise TimeoutError('No terminal UI job; preserved ID ' + submitted['id'])


def settle_pending():
    for i in range(20):
        state = api('/api/status')
        if not state['pending']: return state
        act('resultado', label='conciliacion_' + str(i), maximum=60)
        time.sleep(.2)
    raise TimeoutError('Exact material ID still pending; no re-PUT.')


def main():
    global TOKEN
    if OUT.exists(): raise FileExistsError('Executed records preserved; no rerun under same ID.')
    OUT.mkdir()
    (OUT / 'FUENTES_EJECUTADAS').mkdir()
    files = []
    for path in [*HERE.parent.glob('*.py'), *HERE.parent.glob('*.js'), *HERE.parent.glob('*.html'), *HERE.parent.glob('*.css'),
                 ROOT / 'ABRIR_GENESIS.bat', HERE / 'PLAN_GUI_WALK_R01.json', HERE / 'SELECCION_GUI_WALK_R01.json', Path(__file__)]:
        dest = OUT / 'FUENTES_EJECUTADAS' / path.name
        shutil.copyfile(path, dest)
        files.append({'file': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size})
    write('REVISION_EJECUTADA.json', {'begun_utc': now(), 'files': files, 'scope': 'Actual source bytes preserved before first native API open.'})
    TOKEN = api('/api/session')['token']
    act('abrir', label='01_ABRIR_COMPLETO')
    before = api('/api/status')
    unknown, after = act('ejecutar', {'texto': 'usar desconocida 4 5'}, label='02_DESCONOCIDA_SIN_ENTRADA')
    write('02_IGUALDAD_RECHAZO_INTERFAZ.json', {'before': before, 'after': after,
        'owner_ticks_equal': before['owner']['observation']['tick'] == after['owner']['observation']['tick'],
        'physical_equal': before['record']['physical'] == after['record']['physical'],
        'pending_before': before['pending'], 'pending_after': after['pending'],
        'expected_LookupError': unknown.get('error', {}).get('type') == 'LookupError'})
    act('vivir', label='03_VIVIR_EXPLICITO')
    for i, form in enumerate(('clasifica', 'luma', 'nara')):
        act('ejecutar', {'texto': 'palabra ' + form}, label='04_BASE_' + str(i) + '_' + form)
        settle_pending()
    act('ensenar', {'forma': 'clasifica', 'senal': -1, 'revision': True}, label='05_DOCENCIA_INVERTIDA')
    settle_pending()
    for i, form in enumerate(('clasifica', 'luma', 'nara')):
        act('ejecutar', {'texto': 'palabra ' + form}, label='06_USO_POST_' + str(i) + '_' + form)
        settle_pending()
    act('pausar', label='07_PAUSA_FISICA')
    act('grabar', label='08_GRABAR')
    act('guardar', label='09_GUARDAR')
    time.sleep(2.2)
    write('10_FOTOGRAMA_PAUSADO.json', api('/api/frame'))
    act('detener', label='11_DETENER')
    act('grabar', label='12_CERRAR_GRABACION')
    write('CIERRE_PRIMER_PROCESO.json', {'closed_utc': now(), 'status': api('/api/status'), 'frame': api('/api/frame'),
        'scientific_outcomes_not_overridden': True, 'pending_test_not_yet_executed': True})
    log('fixed_first_process_closed')
    print(json.dumps({'closed': True, 'out': str(OUT)}, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()
