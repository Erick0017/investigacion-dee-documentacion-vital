"""Cierre logístico delta autorizado; no reaudita/reproduce 43 vidas anteriores.

Las bases APD04 se conservan desde su manifiesto gestionado. El sellado comprueba
los bytes finales de TODOS los miembros. No instala, no ejecuta Native, no toca
el origen ni trabajo_personal. Sólo añade el corte actual y código/documentos.
"""
import argparse
import importlib.util
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--distribution', type=Path, required=True)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    distribution, source = a.distribution.resolve(), a.source.resolve()
    spec = importlib.util.spec_from_file_location('updater_apd05_prepared', distribution / 'actualizaciones/actualizar.py')
    u = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(u)
    if u.ROOT != distribution:
        raise ValueError('El updater no pertenece a la distribución indicada')
    b = u.Build(source)
    if b.previous.get('source_campaign') != 'APD04_ECOSISTEMA_COGNITIVO':
        raise ValueError('Se requiere exactamente la base APD04 gestionada previa')
    b.members = dict(b.previous['members'])
    args = argparse.Namespace(cerrar='APD05_GENESIS_SIN_LLM',
        verificacion='entregas/SELLO_DISTRIBUCION_APD05_R01.json',
        manual='DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_19_APD05_GENESIS_SIN_VALIDACION_VISUAL.docx',
        vida=['APD05_MAIN'])
    b.prepare_release(args)
    for folder in ('app', 'capacidades', 'contratos', 'organizaciones', 'documentacion', 'pruebas_minimas'):
        b.tree(source / 'sistema' / folder, 'sistema/' + folder)
    for path in (source / 'sistema').iterdir():
        if path.is_file() and path.suffix in ('.py', '.ps1', '.md', '.json'):
            b.copy(path, 'sistema/' + path.name)
    b.copy(source / 'sistema/runtime' / u.WHEEL_NAME, 'motor/' + u.WHEEL_NAME)
    if b.members['motor/' + u.WHEEL_NAME]['sha256'] != u.WHEEL_SHA:
        raise ValueError('No es el WHL oficial')
    for name in u.GENESIS_FILES:
        b.copy(source / 'aplicacion/GENESIS' / name, 'aplicacion/GENESIS/' + name)
    b.copy(source / 'ABRIR_GENESIS.bat', 'ABRIR_GENESIS.bat')
    b.prepared_runtime313()
    # HABITAT_EXTERNO conserva su adaptación portable anterior; no se cambia
    # una ruta externa por la absoluta del autor al copiar contratos actuales.
    habitat = 'sistema/contratos/HABITAT_EXTERNO_01.json'
    if habitat in b.previous['members']:
        b.members[habitat] = b.previous['members'][habitat]
        b.staged.pop(habitat, None)
    old_catalog = u.read(distribution / 'entes/CATALOGO.json')
    desc = b.selection['descriptions']['APD05_MAIN']
    row = b.life('APD05_MAIN', **desc)
    rows = [r for r in old_catalog['cuts'] if r['source_life'] != 'APD05_MAIN'] + [row]
    b.json('entes/CATALOGO.json', {**old_catalog, 'cuts': rows,
        'default_source_protected': u.read(source / 'sistema/estado/ACTIVO.json')['life_id'],
        'APD05_method': 'Retained prior closed managed cuts; added one exact APD05 MAIN whole-pair cut. No memories merged.'})
    manual = source / args.manual
    b.copy(manual, manual.name)
    for name in list(b.members):
        if '/' not in name and 'Manual_Maestro' in name and name.endswith('.docx') and name != manual.name:
            del b.members[name]  # finish moves old exact bytes to recoverable backup
    b.json('documentos/MANUAL_VIGENTE.json', {'file': manual.name, 'root_copy': manual.name,
        'sha256': u.sha(manual), 'source_campaign': args.cerrar,
        'editorial_status': 'Actual structural update; soffice unavailable, zero visually validated pages.',
        'single_current_DOCX_authority': 'Root only; historical edition remains recoverable in update backup.'})
    for path, target in (
        (source / 'CONTINUIDAD_APD05_GENESIS_SIN_LLM.json', 'investigacion/APD05/CONTINUIDAD.json'),
        (source / 'laboratorio/campanas/APD05_GENESIS_SIN_LLM/INFORME_CIENTIFICO_CIERRE_PARCIAL.md', 'investigacion/APD05/INFORME_CIENTIFICO.md'),
        (source / 'laboratorio/campanas/APD05_GENESIS_SIN_LLM/cierre/INCORPORACIONES_APD05_CIERRE.md', 'investigacion/APD05/INCORPORACIONES.md'),
        (source / 'laboratorio/campanas/APD05_GENESIS_SIN_LLM/manual/VERIFICACION_MANUAL_1_19_R01.json', 'investigacion/APD05/VERIFICACION_MANUAL.json')):
        b.copy(path, target)
    b.json('actualizaciones/METODO_DELTA_APD05.json', {
        'schema': 'APD05.bounded_distribution_delta.N0.R01',
        'base_manifest_sha256': u.sha(distribution / 'actualizaciones/ARCHIVOS_GESTIONADOS.json'),
        'prior_life_rows_retained': len(old_catalog['cuts']), 'new_life': 'APD05_MAIN',
        'previous_dependency_trees_preserved_without_reinstallation': True,
        'full_member_hashes_checked_by_final_seal': True,
        'first_updater_staging_preserved': 'actualizaciones/temporales/20261027T155505Z',
        'first_updater_stopped_before_manifest_commit': True,
        'no_historical_reproduction': True, 'new_native_ticks': 0,
        'scope': 'Package logistics, not a new scientific audit or acquisition.'})
    manifest = b.finish()
    result = u.seal_zip(manifest)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
