"""Reconcile exited owner, then consume existing Vivir/material IDs once."""
from pathlib import Path
import importlib.util
import json
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('walk_api_r05', HERE / 'ejecutar_walk_gui_r01.py')
w = importlib.util.module_from_spec(spec); spec.loader.exec_module(w)
OUT = HERE / 'WALK_R05_IDS_ORIGINALES'


def required(action, value=None, label=None):
    job, state = w.act(action, value, label=label, maximum=180)
    if job['status'] != 'completed': raise RuntimeError('Preserved interface error: ' + json.dumps(job.get('error')))
    return job, state


def main():
    if OUT.exists(): raise FileExistsError('Do not repeat the execution.')
    OUT.mkdir(); w.OUT = OUT; w.TOKEN = w.api('/api/session')['token']
    required('conciliar-propietario', label='01_OS_EXIT_CONCILIADO')
    required('abrir', label='02_MISMA_VIDA_ID_ANTIGUO')
    # A previously queued literal Vivir controls admission. Do not PUT another.
    until = time.monotonic() + 120
    last = None
    while time.monotonic() < until:
        job, state = required('resultado', label='03_RESULTADO_ID_UNICO')
        last = job
        if state.get('pending') is None: break
        time.sleep(.5)
    if state.get('pending') is not None: raise TimeoutError('The same ID remains pending; no new request submitted.')
    required('pausar', label='04_PAUSA_REAL')
    required('grabar', label='05_GRABAR_REAL')
    w.api('/api/frame'); time.sleep(2.5); w.api('/api/frame')
    required('guardar', label='06_GUARDAR')
    required('detener', label='07_STOP_CONFIRMADO')
    required('grabar', label='08_CERRAR_GRABACION')
    required('exportar', label='09_EXPORTAR_CONTEXTO')
    w.write('CIERRE_IDS_ORIGINALES_R05.json', {'status':w.api('/api/status'),'frame':w.api('/api/frame'),
        'existing_queued_material_id':'apd05_gui_walk_pending_r01','new_material_puts_by_this_driver':0,
        'new_vivir_puts_by_this_driver':0,'repeated_teaching':False,'software_errors_preserved_in_prior_revisions':True})
    print(json.dumps({'closed':True,'out':str(OUT)},ensure_ascii=False),flush=True)


if __name__ == '__main__': main()
