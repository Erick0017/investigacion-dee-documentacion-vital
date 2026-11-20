"""Zero-tick audit of an interrupted owner, not a repair or restart."""
from pathlib import Path
import hashlib
import json
import shutil
import sqlite3

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/ATENCION_CONSECUENCIAS_AUX_R01'
LIFE = 'APD04_ATENCION_REAL_AUX'
DESTINATION = EVIDENCE / 'INCIDENCIA_INSTRUMENTAL_PRESERVADA_N0'


def main():
    if DESTINATION.exists():
        raise FileExistsError('The original incident extraction is already preserved')
    DESTINATION.mkdir()
    sources = [ROOT / 'sistema/estado/vidas' / LIFE / name
               for name in ('VIDA.json', 'FUTURO_INTERRUMPIDO.json', 'HISTORIA.jsonl')]
    protocol = ROOT / 'sistema/estado/entrada_sencilla/vidas' / LIFE
    sources.extend(protocol / name for name in ('PROTOCOLO.json', 'SESIONES.jsonl'))
    sources.extend((protocol / 'sesion_20261026T203710Z_1e48ce29').glob('OWNER_*.txt'))
    sources.extend([EVIDENCE / 'CONFIGURACION_LOCAL_NO_INSTALADA.json',
                    EVIDENCE / 'RECURSOS_DRIVER.json', EVIDENCE / 'A/START.json',
                    EVIDENCE / 'A/7_common_probe_no_quality.json'])
    members = []
    for order, source in enumerate(sources):
        if not source.is_file():
            continue
        encoded = source.read_bytes()
        target = DESTINATION / (str(order).zfill(2) + '_' + source.name)
        shutil.copy2(source, target)
        members.append({'source': source.relative_to(ROOT).as_posix(), 'exported': target.name,
            'sha256': hashlib.sha256(encoded).hexdigest(), 'bytes': len(encoded)})
    database = ROOT / 'sistema/estado/servicios_persistentes' / LIFE / 'cola.sqlite3'
    with sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True) as connection:
        connection.row_factory = sqlite3.Row
        requests = [dict(row) for row in connection.execute(
            "select * from requests where id like 'apd04_attention_A_%' or id=? order by seq",
            ('ui_c_38372f4df94f4844b1b31bf867aa3194',))]
        owner = json.loads(connection.execute("select value from meta where key='owner'").fetchone()[0])
    outcome = {'schema': 'APD04.preserved_interrupted_owner.N0.v1',
        'life': LIFE, 'members': members, 'owner_last_cached_not_current': owner,
        'queue_read_only_exact_rows': requests,
        'native_ticks': 0, 'runtime_loads': 0, 'no_repair_no_reopen': True,
        'demonstrated': ['Twelve functional opportunities committed with complete original results.',
            'A7 was processing, not merely queued; no completion or saved post-A7 state exists.',
            'STOP was queued without confirmation; pending IDs and future marker remain.',
            'The original operator config allowed7200seconds, while the final owner cache is214.83seconds.',
            'Both owner stdio files are empty; no owner exit code was saved by the original driver.'],
        'not_demonstrated': ['Cause of owner interruption or native future afterT658068.',
            'That the memory limit was or was not responsible in every nested Job.',
            'Cognitive failure, content erasure, or normal graceful owner closure.']}
    with (DESTINATION / 'INCIDENCIA.json').open('x', encoding='utf8') as stream:
        json.dump(outcome, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'destination': str(DESTINATION), 'members': len(members),
        'pending_requests': [{'id': r['id'], 'status': r['status']} for r in requests
                             if r['status'] != 'completed'], 'native_ticks': 0}, indent=2))


if __name__ == '__main__':
    main()
