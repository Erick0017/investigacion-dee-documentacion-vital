"""Copy the closed EO02 evidence to the analysis staging tree, without DEE ticks.

No originals are edited. The manifest describes exact original bytes, not a
claim that the small analysis archive is an operational/native-state backup.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, shutil, zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LAB = HERE.parent
EV = ROOT / 'evidencia/campanas/ENTE_DEE_EVOLUCION_02'
STAGE = HERE / 'PAQUETE_ANALISIS'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--manual', type=Path, required=True)
    p.add_argument('--revision', default='R1')
    a = p.parse_args()
    if not a.revision.isalnum():
        raise ValueError('Use one explicit alphanumeric staging revision')
    global STAGE
    STAGE = HERE / ('PAQUETE_ANALISIS_' + a.revision)
    a.manual = a.manual.resolve(strict=True)
    if not a.manual.is_relative_to(ROOT):
        raise ValueError('The current manual must belong to the local DCS root')
    STAGE.mkdir(parents=True, exist_ok=False)
    copied = []
    included = set()

    def put(source, member):
        source = Path(source).resolve(strict=True)
        member = Path(member)
        if member.is_absolute() or '..' in member.parts:
            raise ValueError('Unsafe staging member')
        destination = STAGE / member
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        if sha(source) != sha(destination):
            raise ValueError('Copied bytes differ: ' + str(source))
        included.add(source)
        copied.append({'member': member.as_posix(), 'original': str(source),
                       'original_relative_to_DCS': source.relative_to(ROOT).as_posix()
                       if source.is_relative_to(ROOT) else None,
                       'bytes': source.stat().st_size, 'sha256': sha(source),
                       'transformation': 'NONE_EXACT_BYTES'})

    def tree(source, destination, allowed=None):
        for f in sorted(Path(source).rglob('*')):
            if f.is_file() and '__pycache__' not in f.parts and (allowed is None or allowed(f)):
                put(f, Path(destination) / f.relative_to(source))

    # Final root reports/tables. Preparation/sealing tools are part of the code,
    # not synthetic scientific evidence.
    for f in sorted(HERE.iterdir()):
        if f.is_file() and f.suffix in ('.md', '.csv'):
            put(f, f.name)
    for f in sorted(EV.iterdir()):
        if f.is_file() and (f.name.endswith('.json') or f.name.endswith('.json.gz')):
            put(f, Path('EVIDENCIA_CAUSAL/RAIZ') / f.name)
    tree(EV / 'codigo_ejecutado', 'EVIDENCIA_CAUSAL/CODIGO_EJECUTADO')
    tree(EV / 'codigo_experimento', 'EVIDENCIA_CAUSAL/RAIZ/codigo_experimento')
    tree(EV / 'capacidad', 'EVIDENCIA_CAUSAL/CAPACIDAD')
    tree(EV / 'contexto', 'EVIDENCIA_CAUSAL/CONTEXTO')
    tree(EV / 'recalculo/ARCHIVOS_SERVICIOS', 'EVIDENCIA_CAUSAL/ARCHIVOS_SERVICIOS')
    put(EV / 'recalculo/INDICE_ARTEFACTOS_FINAL.json', 'EVIDENCIA_CAUSAL/INDICE_ARTEFACTOS_FINAL.json')
    put(EV / 'recalculo/IDENTIDAD_ESTADOS_FINALES.json', 'EVIDENCIA_CAUSAL/IDENTIDAD_ESTADOS_FINALES.json')
    tree(EV / 'recalculo/FINAL_V2', 'RECALCULO/REFERENCIA_RAIZ')
    for name in ('INDEPENDENCIA_CAPACIDAD_01.json', 'INDEPENDENCIA_RECALCULO_FINAL_V2.json'):
        put(EV / 'recalculo' / name, Path('RECALCULO/COMPROBACIONES_PREVIAS') / name)
    tree(HERE / 'recalculo', 'RECALCULO', lambda f: f.suffix in ('.py', '.md', '.json'))
    put(LAB / 'capacidad/recalcular_capacidad.py', 'RECALCULO/recalcular_capacidad.py')
    put(LAB / 'contexto/recalcular_contexto.py', 'RECALCULO/recalcular_contexto.py')
    put(EV / 'capacidad/RECALCULO_CAPACIDAD.json', 'RECALCULO/REFERENCIA_CAPACIDAD.json')
    put(EV / 'contexto/RECALCULO_CONTEXTO.json', 'RECALCULO/REFERENCIA_CONTEXTO.json')

    for f in sorted(LAB.iterdir()):
        if f.is_file() and f.suffix in ('.py', '.json', '.md'):
            put(f, Path('CODIGO_Y_PROTOCOLOS') / f.name)
    tree(LAB / 'revisiones', 'CODIGO_Y_PROTOCOLOS/revisiones')
    tree(LAB / 'capacidad', 'CODIGO_Y_PROTOCOLOS/capacidad',
         lambda f: f.suffix in ('.py', '.json', '.md', '.csv'))
    tree(LAB / 'contexto', 'CODIGO_Y_PROTOCOLOS/contexto',
         lambda f: f.suffix in ('.py', '.json', '.md', '.csv'))
    for f in ('preparar_analisis.py', 'sellar_analisis.py', 'verificar_analisis_final.py'):
        put(HERE / f, Path('RECALCULO') / f)

    # This is a reproducible source delta, not an installer and not a snapshot.
    for f in ('gestionar.py', 'capacidades/ente_evolucion_02_core.py',
              'capacidades/ente_evolucion_02.py', 'capacidades/ente_evolucion_02_sensorial.py',
              'capacidades/eo02_sensor_periferico.py', 'capacidades/eo02_trabajador_local.py',
              'capacidades/sensorial_r10.py', 'capacidades/CATALOGO_CAPACIDADES.json',
              'contratos/EO02_EVOLUCION_MULTIDOMINIO.json', 'contratos/EO02_SENSORIAL_R10.json',
              'documentacion/GUIA_ENTE_EVOLUCION_02.md'):
        put(ROOT / 'sistema' / f, Path('DELTA_OPERATIVO/sistema') / f)
    put(a.manual, Path('MANUAL') / a.manual.name)
    for f in ('CAMBIOS_MANUAL.md', 'CORRECCION_COBERTURA_MANUAL_R1.json',
              'EDICION_MANUAL_1_11_ENTE02.json'):
        put(LAB / 'documentos' / f, Path('MANUAL') / f)
    put(LAB / 'documentos/verificacion_final_R1/VERIFICACION_MANUAL_ENTE02.json',
        'MANUAL/VERIFICACION_MANUAL_ENTE02.json')

    # Exact local locators for omitted complete states; no anonymous omission.
    checkpoints = []
    cpdir = ROOT / 'sistema/estado/checkpoints'
    for f in sorted(cpdir.iterdir()):
        if f.is_file() and ('EO02' in f.name or f.name.startswith(('EO01_MAIN.', 'CF01_MAIN.', 'E1_SOCIAL_11.'))):
            checkpoints.append({'local_path': str(f), 'relative_to_DCS': f.relative_to(ROOT).as_posix(),
                                'bytes': f.stat().st_size, 'sha256': sha(f),
                                'included_in_small_analysis': False})
    omitted = []
    for base in (LAB, EV):
        for f in sorted(base.rglob('*')):
            if (not f.is_file() or f.resolve() in included
                    or any(parent.name.startswith('PAQUETE_ANALISIS') for parent in f.parents)
                    or '__pycache__' in f.parts or f.name.startswith('ESTIMACION_ANALISIS')):
                continue
            if base == LAB and (f.is_relative_to(HERE / 'recalculo') or f.is_relative_to(LAB / 'documentos')):
                reason = 'Redundant editorial/intermediate verification or retained historical revision; current Word and affected evidence included.'
            else:
                reason = 'Intermediate calculation/working artifact; original primary records and final calculation are included.'
            omitted.append({'local_path': str(f.resolve()), 'relative_to_DCS': f.relative_to(ROOT).as_posix(),
                            'bytes': f.stat().st_size, 'sha256': sha(f), 'reason': reason})
    dump(STAGE / 'INDICE_FUENTES_Y_OMISIONES.json', {
        'schema': 'EO02.analysis.sources_omissions.v1',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'exact_copies': copied,
        'complete_snapshots_local_only': checkpoints,
        'other_local_files_not_included': omitted,
        'no_engine_or_WHL': True,
        'all_root_capacity_context_primary_records_included': True,
        'initial_91833383_byte_record_included_losslessly_as_original_bytes': True,
        'scope': 'Scientific analysis package. Not the full operating distribution, and not sufficient to continue lives without their complete snapshots.'})
    dump(STAGE / 'DELTA_OPERATIVO/INDICE_DELTA.json', {
        'schema': 'EO02.source_delta.v1',
        'files': [x for x in copied if x['member'].startswith('DELTA_OPERATIVO/')],
        'not_standalone_installation': True,
        'instructions': 'Use the separately verified cognitive_sistem_colaborador.zip for execution. This delta records exact incorporated source/contract bytes; do not apply it blindly to a different release or replace learned snapshots.'})
    (STAGE / 'LEER_PRIMERO.md').write_text(
        '# ENTE02 — análisis científico\n\n'
        'Comience por INFORME_CIENTIFICO.md, CAPACIDAD_POR_NIVEL.csv y CAPACIDADES_POR_VIDA.csv. '
        'Las correcciones de alcance de serialización están en CODIGO_Y_PROTOCOLOS/capacidad/ACLARACION_ALCANCE_SERIAL32.md: '
        'R10 ensayó 16 como dos ventanas de ocho, no 32; R9 sí conservó intentos adversos de 32.\n\n'
        'EVIDENCIA_CAUSAL contiene los primarios exactos positivos y negativos, código ejecutado y los archivos reales producidos por los servicios locales. '
        'No son réplicas independientes las consultas o las bifurcaciones de un mismo prefijo.\n\n'
        'Para recalcular sin motor ni simulaciones: `python RECALCULO/verificar_analisis_final.py`. '
        'Opcionalmente, añada `--prohibir-raiz RUTA` para bloquear expresamente cualquier instalación original; la verificación de entrega bloquea ambas raíces reales. '
        'Python 3.10 o posterior, biblioteca estándar. La prueba reconstruye lecturas desde RAW, comprueba recibos y bytes de workers, y compara los tres cálculos con sus referencias archivadas. '
        'No importa DEE, no ejecuta trabajadores y no añade ticks.\n\n'
        'El manual 1.11 R1 tiene comprobación estructural; no se obtuvo validación visual por falta del renderizador autorizado. '
        'DELTA_OPERATIVO no es una instalación autónoma. Los estados completos permanecen localmente y en la distribución operativa seleccionada, '
        'no en este ZIP reducido. Sus localizadores y SHA-256 figuran en INDICE_FUENTES_Y_OMISIONES.json.\n', encoding='utf8')
    # Preliminary size only; the final archive is sealed after the full-package
    # proof arrives. Do not publish or rename this estimate as the canonical ZIP.
    estimate = HERE / ('ESTIMACION_ANALISIS_' + a.revision + '.zip')
    with zipfile.ZipFile(estimate, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(STAGE.rglob('*')):
            if f.is_file():
                z.write(f, f.relative_to(STAGE).as_posix())
    report = {'stage': str(STAGE), 'staged_files': sum(f.is_file() for f in STAGE.rglob('*')),
              'estimate_bytes': estimate.stat().st_size,
              'all_primary_records_included_without_lossy_extraction': True,
              'native_ticks': 0, 'full_distribution_proof_still_required_before_sealing': True}
    dump(HERE / ('ESTIMACION_ANALISIS_' + a.revision + '.json'), report)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
