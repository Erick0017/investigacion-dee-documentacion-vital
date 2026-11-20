"""Root-only C complete paired import under the existing512MiB owned Job.

Default prints a plan. --importar starts the official importer once and waits
for its exit BEFORE any owner may open this new diagnostic world. No time step,
selection, copying of separate memories, state editing or automatic retry.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, importlib.util, json, os, sys, time

P = Path(__file__).resolve().parents[1]
C = P.parents[2]/'DEE Cognitive 2.0'
RP = C/'reproducibilidad'
PY = C/'motor/python313/python.exe'


def read(path): return json.loads(Path(path).read_text('utf-8-sig'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(ok, message):
    if not ok: raise ValueError(message)


def main(args):
    item = read(P/'control/SISTEMA_C_PI08_R02_PREPARADO.json')
    system = Path(item['system']); destination = Path(item['directory']); life = item['life']
    context = Path(item['context']); require(sha(context) == item['context_sha256'], 'Fixed complete-pair context changed')
    command = [str(PY), '-I', '-B', '-X', 'utf8', str(RP/'importar_diagnostico.py'), '--contexto', str(context)]
    if not args.importar:
        print(json.dumps({'mode': 'PLAN_ONLY_NO_NATIVE', 'command': command, 'memory_limit': 536870912,
                          'life': life, 'new_Native_ticks': 0, 'no_automatic_owner_start': True}, ensure_ascii=False, indent=2))
        return
    require(system.resolve().is_relative_to((P/'estados').resolve()) and not (system/'estado/ACTIVO.json').exists(), 'Explicit unselected PI08 system only')
    for folder in ('vidas', 'servicios_locales', 'servicios_persistentes'):
        require(not (system/'estado'/folder/life).exists(), 'Identity already used; no repeat import')
        require(not (C/'sistema/estado'/folder/life).exists(), 'Identity already exists in product')
    require(not (destination/'IMPORTACION_DIAGNOSTICA.json').exists(), 'Preserve prior import proof')
    marker = P/'PI08_ROOT_NATIVE_WRITER.lock'
    require(not marker.exists() and not (RP/'EJECUCION_MATERIAL.lock').exists(), 'A Native/import writer remains')
    for name in ('estado/locks',):
        path = system/name; require(not path.exists() or not any(path.iterdir()), 'A diagnostic lock remains')
    seal = read(P/'codigo/SELLO_PI08_C_R02.json')
    original = C/'sistema/estado/ACTIVO.json'; active_before = sha(original)
    require(read(original)['life_id'] != life, 'Never import the selected principal')
    require(read(context)['prefix_manifest_sha256'] == seal['source_prefix']['manifest_sha256'], 'Do not substitute a source future')
    cutoff = datetime.fromisoformat(read(P/'REGISTRO_CAMPANA.json')['budget']['new_experimental_uses_cutoff_local']).astimezone(timezone.utc)
    require(datetime.now(timezone.utc) < cutoff, 'Research cutoff reached')
    sys.path.insert(0, str(system))
    from app import process_control as pc  # stdlib Windows Job supervisor only.
    with marker.open('x', encoding='utf8') as out: json.dump({'pid': os.getpid(), 'operation': 'COMPLETE_PAIR_IMPORT_ONLY', 'life': life}, out)
    process = job = None; error = None; resources = {}; peak = 0; started = time.monotonic()
    stdout = (destination/'importar_diagnostico.py.stdout.txt').open('x', encoding='utf8')
    stderr = (destination/'importar_diagnostico.py.stderr.txt').open('x', encoding='utf8')
    try:
        process, job, jobname = pc.spawn_owned(command, cwd=str(P), stdout=stdout, stderr=stderr, memory_limit=536870912)
        while process.poll() is None:
            resources = pc.job_resources(job); peak = max(peak, resources.get('peak_job_committed_bytes', 0))
            if time.monotonic()-started > 240:
                raise TimeoutError('Importer finite host wait exceeded; preserve destination and exact Job, no retry or cleanup')
            time.sleep(.1)
        resources = pc.job_resources(job); peak = max(peak, resources.get('peak_job_committed_bytes', 0))
        require(process.returncode == 0, 'Complete-pair importer failed; preserve logs/future')
        imported = read(destination/'IMPORTACION_DIAGNOSTICA.json')
        require(imported['new_native_ticks'] == 0 and imported['principal_selected'] is False, 'Importer advanced/selected unexpectedly')
        require(sha(original) == active_before, 'Original adopted A selection changed')
    except Exception as exc:
        error = {'type': type(exc).__name__, 'message': str(exc), 'automatic_retry': False}
    closed = process is not None and process.poll() is not None
    output = {'schema': 'DEE.PI08.C.actual_complete_import.R02', 'role': 'C_single_world_partial', 'life_id': life,
              'status': 'IMPORTED_CLOSED_NO_NATIVE_TICKS' if error is None and closed else 'FAILED_IMPORT_PRESERVED',
              'closed': closed, 'error': error, 'new_Native_ticks': 0, 'importer_Runtime_opened': process is not None,
              'exit_code': None if process is None else process.poll(), 'job_resources': resources,
              'peak_job_committed_bytes': peak, 'memory_limit_bytes': 536870912,
              'context': str(context), 'context_sha256': sha(context), 'command': command,
              'full_import_proof': str(destination/'IMPORTACION_DIAGNOSTICA.json'),
              'no_owner_started': True, 'principal_unchanged': sha(original) == active_before}
    proof = P/'control/IMPORTACION_C_PI08_R02.json'
    with proof.open('x', encoding='utf8') as out: json.dump(output, out, ensure_ascii=False, indent=2); out.write('\n')
    if closed:
        stdout.close(); stderr.close()
        if job is not None: pc.close_job(job)
        if error is None: marker.unlink()
    print(json.dumps({'proof': str(proof), 'sha256': sha(proof), 'status': output['status'], 'error': error}, ensure_ascii=False))
    if error: raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--importar', action='store_true')
    main(parser.parse_args())
