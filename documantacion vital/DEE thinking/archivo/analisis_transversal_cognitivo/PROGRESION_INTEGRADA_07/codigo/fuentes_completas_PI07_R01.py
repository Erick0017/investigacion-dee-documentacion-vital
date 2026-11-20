"""Exact frozen current-main pair allowance; no engine or state mutations."""
from pathlib import Path
import hashlib, json
P = Path(__file__).resolve().parents[1]
C = P.parents[2]/'DEE Cognitive 2.0'
EXACT = P.parent/'PROGRESION_INTEGRADA_06/pares/BASE_MAIN_T824911'
EXPECTED = 'adb71add120a24629ac836da00009011e670b2f890edd93ef80bb4483acc3524'

def allowed_pair(path):
    path = Path(path).resolve(strict=True)
    if path == EXACT.resolve(strict=True):
        f = path/'EXPORTACION_SERVICIO.json'
        if hashlib.sha256(f.read_bytes()).hexdigest() != EXPECTED:
            raise ValueError('The exact prior current-main export changed')
        m = json.loads(f.read_text(encoding='utf8'))
        if (m['life_id'] != 'ECI02_PI03_REPRO_PI04_PI05_MAIN_01' or
            m['snapshot_sha256'] != 'af74c8f47e43ed3b2395a338a23a6cbd42f105ec2cff4daac15b7a4d45e90832' or
            m['physical']['tick'] != 824911):
            raise ValueError('Not the corroborated complete current-main cut')
        current = json.loads((C/'sistema/estado/vidas'/m['life_id']/'VIDA.json').read_text(encoding='utf8'))
        if current['physical']['tick'] != m['physical']['tick'] or current['snapshot_sha256'] != m['snapshot_sha256']:
            raise ValueError('Main advanced; a historical cut cannot replace the real continuation')
        return True
    return (path.is_relative_to((C/'reproducibilidad/materiales').resolve()) or
            path.is_relative_to((P/'pares').resolve()) or
            path.is_relative_to((P/'estados').resolve()))
