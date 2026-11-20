"""R02: another complete-pair AUX after the R01 pre-insertion validator failure.

R01 and its pending supervisor intent remain unchanged. No Native calibration
was admitted there; this invocation is not a retry of an applied physical event.
"""
from pathlib import Path
import importlib.util
import json
import sys

path = Path(__file__).with_name('ejecutar_calibracion_apd04_r01.py')
spec = importlib.util.spec_from_file_location('frozen_r01_driver', path)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
driver.LIFE = 'APD04_CALIB_R02'
driver.OUT = driver.ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/CALIBRACION_R02'
driver.FROZEN = driver.LAB / 'revisiones/R02_EJECUTADO'


if __name__ == '__main__':
    sys.path.insert(0, str(driver.SYSTEM))
    from app.cola_local import validate_request
    validate_request({'operacion': 'sesion', 'situaciones': [{
        'modo': 'apd04-calibrar', 'casos': [
            {'tipo': 'clasifica', 'valor': 19},
            {'tipo': 'clasifica', 'valor': 20},
            {'tipo': 'clasifica', 'valor': 21},
            {'tipo': 'equilibra', 'cargas': [6, 4]},
            {'tipo': 'equilibra', 'cargas': [4, 6]},
            {'tipo': 'equilibra', 'cargas': [6, 6]},
        ]}], 'retorno': 'omit', 'actuador': 'closed'})
    print(json.dumps({'transport_literal_validation': True, 'native_ticks': 0}))
    driver.main()
