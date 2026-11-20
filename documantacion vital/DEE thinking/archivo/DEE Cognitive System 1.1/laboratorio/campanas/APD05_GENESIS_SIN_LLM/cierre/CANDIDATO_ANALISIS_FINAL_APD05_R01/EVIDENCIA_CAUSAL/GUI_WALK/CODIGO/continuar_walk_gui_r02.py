"""Continue the same R01 life, correcting only the passive viewer adapter."""
from pathlib import Path
import importlib.util
import json
import time
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('fixed_ui_walk', HERE / 'ejecutar_walk_gui_r01.py')
w = importlib.util.module_from_spec(spec); spec.loader.exec_module(w)
OUT = HERE / 'WALK_R02_CONTINUACION'


def main():
    if OUT.exists(): raise FileExistsError('Do not overwrite an executed continuation.')
    OUT.mkdir()
    w.OUT = OUT
    w.TOKEN = w.api('/api/session')['token']
    w.act('abrir', label='01_REABRIR_MISMA_VIDA')
    time.sleep(2.5)
    frame = w.api('/api/frame')
    w.write('02_VISOR_OFICIAL_MISMO_CORTE.json', frame)
    if not frame.get('available') or not frame.get('coordinate_proof', {}).get('official_observe_samples'):
        raise RuntimeError('No official coherent frame; no 3D fidelity claim.')
    w.act('grabar', label='03_GRABACION_R02')
    w.api('/api/frame')
    # The owner is paused. Submit exactly once; the UI returns a preserved
    # pending identity, never a guessed or repeated answer.
    w.act('ejecutar', {'texto': 'palabra clasifica', 'id': 'apd05_gui_walk_pending_r01'},
        label='04_PENDIENTE_UNA_INSERCION', maximum=170)
    state = w.api('/api/status')
    if (state.get('pending') or {}).get('id') != 'apd05_gui_walk_pending_r01':
        raise RuntimeError('Expected queued exact ID was not preserved.')
    w.act('guardar', label='05_GUARDAR_CON_COLA')
    w.act('detener', label='06_STOP_CON_COLA')
    w.act('grabar', label='07_CERRAR_GRABACION')
    w.act('exportar', label='08_CONTEXTO_NO_RESTAURABLE')
    w.write('CIERRE_SEGUNDO_PROCESO.json', {'status': w.api('/api/status'), 'frame': w.api('/api/frame'),
        'pending_id_expected': 'apd05_gui_walk_pending_r01', 'no_duplicate_put': True})
    print(json.dumps({'closed': True, 'out': str(OUT)}), flush=True)


if __name__ == '__main__': main()
