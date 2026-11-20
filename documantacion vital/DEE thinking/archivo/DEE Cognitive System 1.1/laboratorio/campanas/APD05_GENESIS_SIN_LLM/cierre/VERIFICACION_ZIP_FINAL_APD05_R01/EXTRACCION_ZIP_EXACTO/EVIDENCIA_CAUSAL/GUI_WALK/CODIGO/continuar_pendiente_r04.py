"""Resume exact queued IDs after a preserved host failure; no new teaching."""
from pathlib import Path
import importlib.util
import json
import time
import hashlib
import shutil

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('walk_api_r04', HERE / 'ejecutar_walk_gui_r01.py')
w = importlib.util.module_from_spec(spec); spec.loader.exec_module(w)
OUT = HERE / 'WALK_R04_PENDIENTE_CONTINUADO'


def main():
    if OUT.exists(): raise FileExistsError('Preserve the executed restoration witness.')
    OUT.mkdir()
    w.OUT = OUT
    (OUT / 'FUENTES_EJECUTADAS_R04').mkdir()
    for path in [*HERE.parent.glob('*.py'), *HERE.parent.glob('*.js'), *HERE.parent.glob('*.html'), *HERE.parent.glob('*.css')]:
        shutil.copyfile(path, OUT / 'FUENTES_EJECUTADAS_R04' / path.name)
    w.TOKEN = w.api('/api/session')['token']
    checks = json.loads((HERE / 'VERIFICACION_CORTE_GUI_R02_N0_R01.json').read_text(encoding='utf8'))['checks']
    if any(value is False for value in checks.values()): raise RuntimeError('Saved cut did not verify; no Native restart.')
    # Existing queued guardar/detener have control precedence and are allowed to
    # complete. They are neither deleted nor submitted again.
    w.act('abrir', label='01_REAPERTURA_CONTROLES_YA_ENCOLADOS')
    until = time.monotonic() + 90
    while time.monotonic() < until:
        status = w.api('/api/status')
        if not (status.get('owner') or {}).get('observation', {}).get('running', True): break
        time.sleep(.3)
    w.act('conciliar-propietario', label='02_CONCILIAR_SALIDA_CONFIRMADA')
    state = w.api('/api/status')
    w.write('03_PENDING_PRESERVADO_TRAS_CONTROLES.json', state)
    if (state.get('pending') or {}).get('id') != 'apd05_gui_walk_pending_r01': raise RuntimeError('Material ID changed.')
    w.act('abrir', label='04_MISMA_VIDA_MISMO_CORTE')
    w.act('resultado', label='05_MISMO_ID_LECTURA_SIN_REPETIR')
    w.act('vivir', label='06_REANUDAR_EXPLICITO')
    until = time.monotonic() + 120
    while time.monotonic() < until:
        job, state = w.act('resultado', label='07_MISMO_ID_RECONCILIADO')
        if state.get('pending') is None: break
        time.sleep(.2)
    if state.get('pending') is not None: raise TimeoutError('No matching final receipt. No re-PUT.')
    w.act('pausar', label='08_PAUSA_FISICA')
    w.act('grabar', label='09_GRABAR_FOTOGRAMA')
    w.api('/api/frame')
    time.sleep(2.5)
    w.api('/api/frame')
    w.act('guardar', label='10_GUARDAR_CONTINUIDAD')
    w.act('detener', label='11_DETENER_CONFIRMADO')
    w.act('grabar', label='12_CERRAR_GRABACION')
    w.act('exportar', label='13_CONTEXTO_EXPORTADO')
    w.write('CIERRE_CONTINUIDAD_R04.json', {'status': w.api('/api/status'), 'frame': w.api('/api/frame'),
        'no_second_material_submission': True, 'same_life': 'APD05_GUI_WALK_R01',
        'host_failure_preserved_not_scientific_recovery': True})
    print(json.dumps({'closed': True, 'out': str(OUT)}, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()
