"""Write external receipt for the already sealed Core; never edits its ZIP."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, shutil, zipfile

RUN = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--zip', type=Path, required=True)
p.add_argument('--recovery', type=Path, required=True)
p.add_argument('--job', type=Path, required=True)
a = p.parse_args()

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

artifact = a.zip.resolve()
folder = artifact.parent
proof = a.recovery/'PRUEBA_RECUPERACION_DESDE_CERO.json'
data = json.loads(proof.read_text(encoding='utf8'))
assert data['status'] == 'PASS'
assert len(data['family_results']) == 34
assert data['artifact_sha256'] == sha(artifact)
assert data['integrity_before'] == data['integrity_after']
assert data['blocked_external_reads'] == 0
assert all(value['status'] == 'PASS' for value in data['family_results'].values())
assert all(command['status'] == 'PASS' and command['exit_code'] == 0 and command['owned_worker_waited'] for command in data['commands'])
job = json.loads(a.job.read_text(encoding='utf8'))
assert job['exit_code'] == 0 and job['owned_job_closed'] and job['owned_worker_waited']
with zipfile.ZipFile(artifact) as archive:
    assert archive.testzip() is None
    matrix = json.loads(archive.read('DEE_COGNITIVE_CORE/documentacion/MATRIZ_CAPACIDADES.json'))
    compression = json.loads(archive.read('DEE_COGNITIVE_CORE/documentacion/COMPRESION.json'))
    manifest = json.loads(archive.read('DEE_COGNITIVE_CORE/MANIFIESTO.json'))
    expanded = sum(member.file_size for member in archive.infolist())
    for internal, external in (
        ('MATRIZ_CAPACIDADES.csv', 'CORE_MATRIZ_CAPACIDADES.csv'),
        ('MATRIZ_CAPACIDADES.md', 'CORE_MATRIZ_CAPACIDADES.md'),
        ('DEE_COGNITIVE_CORE_MANUAL_RECONSTRUCCION.md', 'DEE_COGNITIVE_CORE_MANUAL_RECONSTRUCCION.md'),
        ('INFORME_COMPRESION_Y_PERDIDA_DE_INFORMACION.md', 'INFORME_COMPRESION_Y_PERDIDA_DE_INFORMACION.md'),
        ('documentacion/COMPRESION.json', 'CORE_COMPRESION.json'),
        ('documentacion/MATRIZ_CAPACIDADES.json', 'CORE_MATRIZ_CAPACIDADES.json'),
        ('documentacion/INVENTARIO_SELECCION.json', 'CORE_INVENTARIO_SELECCION.json'),
        ('DEPENDENCIAS.json', 'CORE_DEPENDENCIAS.json')):
        (folder/external).write_bytes(archive.read('DEE_COGNITIVE_CORE/'+internal))
for name in ('PRUEBA_RECUPERACION_DESDE_CERO.json', 'PRUEBA_RECUPERACION_DESDE_CERO.md'):
    shutil.copyfile(a.recovery/name, folder/name)
shutil.copyfile(a.job, folder/'SUPERVISION_FINAL_CORE.json')
receipt = {
    'schema': 'DEE_CORE.exact_zip_external_verification.v1',
    'verified_utc': datetime.now(timezone.utc).isoformat(),
    'status': 'PASS',
    'verification_scope': 'BOUNDED_OPERATIVE_CONTRACTS_NOT_ALL_HISTORICAL_DOMAINS',
    'artifact_name': artifact.name, 'artifact_sha256': sha(artifact),
    'compressed_bytes': artifact.stat().st_size, 'expanded_bytes': expanded,
    'outer_archive_members': len(manifest['files'])+2,
    'wheel_sha256': '09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c',
    'native_extension_sha256': '17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d',
    'kernel_source_sha256': 'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31',
    'clean_recovery_proof': 'PRUEBA_RECUPERACION_DESDE_CERO.json',
    'clean_recovery_proof_sha256': sha(proof),
    'clean_recovery_elapsed_seconds': data['elapsed_seconds'],
    'family_results': {name: value['status'] for name, value in data['family_results'].items()},
    'family_count': len(data['family_results']),
    'all_actual_commands_exit_zero': True,
    'actual_command_count': len(data['commands']),
    'historical_archives_opened': data['historical_archives_opened'],
    'undeclared_external_read_attempts': data['blocked_external_reads'],
    'dependency_limitations': data['external_dependencies'],
    'temp_path_limit': 'Official4.5 native temporary files require an ASCII TEMP/TMP location; Unicode extraction/results tested.',
    'isolation_scope': 'Python audit hooks plus explicit allowlisted paths and source review; not an OS security sandbox.',
    'capability_rows': len(matrix['rows']), 'capability_classification_counts': matrix['counts'],
    'no_automatic_CPC9_E1_attribution': True,
    'full_state_claim': 'Historical full RAW/clocks compared where original primaries supply full-state fingerprints. Direct-array CORE06/07 compare original local records and separately exact new port full initial/terminal fingerprints.',
    'corpus': compression,
    'supervision': job,
    'final_zip_was_not_modified': True,
    'no_background_runtime_remaining_in_owned_job': job['owned_job_closed'],
    'transport': 'Canonical ZIP retained; parent campaign produces sequential parts <=16,000,000 bytes and shared transport manifest.'
}
summary_path = folder/'CORE_RESUMEN_Y_PENDIENTES.json'
if summary_path.exists():
    summary = json.loads(summary_path.read_text(encoding='utf8'))
    assert summary['artifact_sha256'] == receipt['artifact_sha256']
    summary.update(status='PASS_BOUNDED_OPERATIVE_CONTRACTS', final_proof='VERIFICACION_FINAL_CORE.json',
                   clean_recovery_proof_sha256=receipt['clean_recovery_proof_sha256'],
                   all_34_requested_families_passed=True, all_actual_commands_exit_zero=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
lines = [
    '# DEE Cognitive Core: recuperación comprobada', '',
    'Las 34 familias del paquete exacto se ejecutaron correctamente desde una extracción independiente, un entorno nuevo e instalación local del WHL oficial. No se abrieron ZIP históricos ni se detectaron accesos Python fuera de las dependencias declaradas. La observación de archivos no equivale a una caja de seguridad del sistema operativo.', '',
    'Se preservan 56 filas de capacidades/procedencia: 39 reproducidas individualmente, una reproducida en organización auxiliar y 16 documentadas pendientes de reproducir su dominio completo. Las filas no son conceptos ni réplicas. No se atribuyen automáticamente al E1 de CPC9.', '',
    'El panel recupera acontecimientos CP01, predicción CP02, asociaciones SEM01, comunicación A/B/C/D, respaldos adquiridos, orden y redes de roles, K65, acceso renovado CPC6, comparación/discrepancia/ausencia CPC7, MCTS, transmisión social y actualización/retención del primer CPC8. Conserva los controles negativos. Las realizaciones originales CORE06 y CORE07 se portan mediante la transición oficial con arrays y escrituras externas explícitas; no se afirma compatibilidad con colas Runtime antiguas.', '',
    'K65 sigue siendo repertorio de correspondencias físicas, no dominio semántico de 65 primitivas. RIGHT conserva su condición de asociación nueva de la vida histórica correspondiente; no se convierte en una primitiva adicional del inventario. Ni la regulación preparada ni el mecanismo RCA se elevan a autonomía general.', '',
    f"ZIP: `{artifact.name}`. SHA-256: `{receipt['artifact_sha256']}`.",
    f"Tamaño comprimido: {receipt['compressed_bytes']:,} bytes; expandido del contenedor: {expanded:,} bytes. Tiempo de recuperación limpia: {data['elapsed_seconds']:.3f} segundos.", '',
    'Dependencias externas: Windows x64, CPython 3.13 x64 y runtime del sistema. Las 32 familias predeterminadas no necesitan NumPy. CORE06/07 requieren NumPy 2.2.6 explícito. La persistencia nativa oficial necesita TEMP/TMP ASCII; extracción, resultados y rutas de datos Unicode fueron comprobados.', '',
    'Los dominios pendientes conservan fuentes y evidencia terminal. Sus snapshots densos no seleccionados no se consideran recuperables desde este Core. El paquete es sustituto operativo únicamente de los contratos comprobados; no autoriza destruir los expedientes históricos.', '',
    'Consulte PRUEBA_RECUPERACION_DESDE_CERO.json para cada familia, comandos y rutas de importación; VERIFICACION_FINAL_CORE.json para identidad exacta y recursos; CORE_MATRIZ_CAPACIDADES.csv para dominios y límites.'
]
(folder/'CORE_CAPACIDADES_Y_LIMITES.md').write_text('\n'.join(lines)+'\n', encoding='utf8')
pending_receipt = folder/'VERIFICACION_FINAL_CORE.json.pending'
pending_receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
os.replace(pending_receipt, folder/'VERIFICACION_FINAL_CORE.json')
print(json.dumps({key: receipt[key] for key in ('status','artifact_sha256','compressed_bytes','expanded_bytes','family_count','capability_classification_counts')}, ensure_ascii=False))
