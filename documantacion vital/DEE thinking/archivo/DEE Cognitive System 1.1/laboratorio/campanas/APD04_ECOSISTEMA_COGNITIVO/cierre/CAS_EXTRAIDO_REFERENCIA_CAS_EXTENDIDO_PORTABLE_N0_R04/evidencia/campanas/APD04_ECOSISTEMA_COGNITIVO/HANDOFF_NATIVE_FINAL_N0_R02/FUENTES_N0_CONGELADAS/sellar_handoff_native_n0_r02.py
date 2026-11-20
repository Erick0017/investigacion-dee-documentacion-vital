"""Freeze closed N0 calculations and indexes, not a new DEE experiment."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[4]
LAB = ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
EV = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
OUT = EV / 'HANDOFF_NATIVE_FINAL_N0_R02'


def write(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def item(path):
    content = path.read_bytes()
    return {'path': path.relative_to(ROOT).as_posix(), 'bytes': len(content),
            'sha256': hashlib.sha256(content).hexdigest()}


def main():
    if OUT.exists():
        raise FileExistsError('An existing final handoff must never be replaced')
    OUT.mkdir()
    source_names = [
        'contrastar_primeras6_a_c_portable_r02_n0.py',
        'contrastar_primeras6_a_c_apd04_n0.py',
        'recalcular_atencion_apd04_r01_n0.py',
        'recalcular_sensores_apd04_r01_n0.py',
        'extraer_campos_expansion_c_n0.py',
        'ampliar_expansion_c_con_contexto_n0.py',
        'verificar_contextos_c_exportados_n0.py',
        'contrastar_cortes_t658k_apd04_n0.py',
        'diferencias_cortes_ab_apd04_n0.py',
        'cerrar_c_por_reasignacion_root_r01.py',
        'capturar_pila_host_c_apd04_pasiva.py',
        'vigilar_owner_c_apd04_pasivo.py',
        'instrumentar_avance_chunks_apd04_r01.py',
        'prueba_logica_chunks_sin_motor_n0.py',
        Path(__file__).name,
    ]
    copied = []
    for name in source_names:
        original = LAB / 'native_candidates' / name
        target = OUT / 'FUENTES_N0_CONGELADAS' / name
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(original, target)
        original_item = item(original)
        assert hashlib.sha256(target.read_bytes()).hexdigest() == original_item['sha256']
        copied.append({'source': original_item, 'copied': target.relative_to(OUT).as_posix()})
    for name in ('CONTRASTE_A_C_PORTABLE_R02_N0.json', 'CONTRASTE_A_C_PRIMERAS6_T648684_N0.json'):
        original = EV / name
        target = OUT / name
        shutil.copy2(original, target)
        copied.append({'source': item(original), 'copied': name})
    evidence_groups = []
    for relative in ('ATENCION_CONSECUENCIAS_AUX_R02_BC/EVIDENCIA_PORTABLE_R02',
                     'C_DENSIFICACION_CONTEXTOS_R02_N0',
                     'SENSORES_Y_LEXICO_R01/EVIDENCIA_PORTABLE'):
        directory = EV / relative
        members = [item(path) for path in sorted(directory.rglob('*')) if path.is_file()]
        evidence_groups.append({'directory': directory.relative_to(ROOT).as_posix(),
                                'member_count': len(members), 'bytes': sum(row['bytes'] for row in members),
                                'members': members})
    write(OUT / 'INDICE_FINAL.json', {
        'schema': 'APD04.native_front.closed_handoff.N0.r02', 'new_Native_ticks': 0,
        'all_own_owners_closed': True, 'shared_system_changed_by_this_export': False,
        'closed_primary_portable_groups': evidence_groups,
        'frozen_analysis_sources_and_results': copied,
        'C_denominators': {
            'opportunities_in_completed_primary_rows': 6,
            'opportunities_requested_in_completed_transport_blocks': 6,
            'opportunities_requested_in_one_processing_transport_block_C5': 4,
            'C5_individually_started_admitted_completed': 'not established; no committed result',
            'completed_primary_native_inputs': 102, 'applied': 79, 'rejected_occupied': 23,
            'remaining_two_goal1_and_four_common_probe': 'not submitted',
        },
        'scope': 'Exact archived primaries and frozen N0 sources. RAW/clocks excerpts are not continuable snapshots. '
                 'A/B interrupted futures and C budget interruption are preserved, not Native crash findings. '
                 'The progress-chunks instrument is software-only proposal, no Native validation and not adopted.'
    })
    members = [item(path) for path in sorted(OUT.rglob('*')) if path.is_file()]
    write(OUT / 'MANIFIESTO_MIEMBROS.json', {'schema': 'sha256.members.no_self_reference.v1', 'members': members})
    print(json.dumps({'out': str(OUT), 'index': item(OUT / 'INDICE_FINAL.json'),
                      'manifest': item(OUT / 'MANIFIESTO_MIEMBROS.json'),
                      'groups': [{key: row[key] for key in ('directory', 'member_count', 'bytes')} for row in evidence_groups]},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
