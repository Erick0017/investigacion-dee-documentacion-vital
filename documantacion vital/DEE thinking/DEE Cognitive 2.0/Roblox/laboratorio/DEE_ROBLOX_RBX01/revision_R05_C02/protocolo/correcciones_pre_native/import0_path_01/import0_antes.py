"""Root-only explicit import0 command using official512MiB Windows Job.

Importing this file is stdlib only. Running main is an authorized Native-load
operation for Root; it advances zero physical ticks and opens no live owner.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, sqlite3, time

LIMIT = 512 * 1024 * 1024


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def atomic(path, value):
    temporary = path.with_name(path.name + '.WRITING')
    with temporary.open('x', encoding='utf8') as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write('\n'); out.flush(); os.fsync(out.fileno())
    os.replace(temporary, path)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def closed(destination):
    output = destination / 'IMPORTACION_DIAGNOSTICA.json'
    if not output.is_file(): return False
    context = read(destination / 'CONTEXTO_EJECUCION.json'); value = read(output)
    if not (value['new_native_ticks'] == 0 and value['life'] == context['life'] and
            value['comparison']['physical_equal'] and value['comparison']['causal_prefix_equal']): return False
    system = destination / 'sistema'; life = context['life']
    database = system / 'estado/servicios_persistentes' / life / 'cola.sqlite3'
    if not database.is_file(): return False
    if any(Path(str(database) + x).exists() and Path(str(database) + x).stat().st_size for x in ('-wal', '-journal')): return False
    if (system / 'estado/locks' / (life + '.lock')).exists(): return False
    if (system / 'estado/vidas' / life / 'FUTURO_INTERRUMPIDO.json').exists(): return False
    con = sqlite3.connect(database.resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
    try:
        if con.execute('PRAGMA integrity_check').fetchone()[0] != 'ok': return False
        owner = json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
        return (owner.get('running') is False and
                con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0] == 0)
    finally:
        con.close()


def run(product, destination, cutoff):
    product = Path(product).resolve(strict=True); destination = Path(destination).resolve(strict=True)
    root = Path(__file__).resolve().parents[1]
    if destination.parent != root / 'native':
        raise ValueError('C02 diagnostic destination only')
    context_file = destination / 'CONTEXTO_EJECUCION.json'; context = read(context_file)
    if Path(context['system']) != destination / 'sistema' or (destination / 'IMPORT0_JOB.json').exists():
        raise ValueError('Fresh exact explicit import destination only')
    if (destination / 'IMPORTACION_DIAGNOSTICA.json').exists():
        raise ValueError('Already imported destination is preserved')
    if not (time.time() < cutoff and cutoff == 1794738600):
        raise ValueError('Finite Root Native cutoff')
    for pin in context['tool_sources']:
        path = product / 'reproducibilidad' / pin['file']
        if hashlib.sha256(path.read_bytes()).hexdigest() != pin['sha256']:
            raise ValueError('Pinned official importer instrumentation changed')
    system = destination / 'sistema'
    pc = load(system / 'app/process_control.py', '_RBX01_import0_process_control')
    support = load(Path(__file__).resolve().parents[1] / 'fuentes/rbx01_owner_support_C02.py', '_RBX01_import0_support_C02')
    stdout = (destination / 'import0.stdout.txt').open('x', encoding='utf8')
    stderr = (destination / 'import0.stderr.txt').open('x', encoding='utf8')
    command = [str(product / 'motor/python313/python.exe'), '-I', '-B', '-X', 'utf8',
               str(product / 'reproducibilidad/importar_diagnostico.py'), '--contexto', str(context_file)]
    output = destination / 'IMPORT0_JOB.json'
    summary = {'schema': 'DEE.RBX01.owned_import0.C02', 'command': command,
               'life_id': context['life'], 'memory_limit_bytes': LIMIT, 'status': 'STARTED',
               'source_pair_manifest_sha256': context['prefix_manifest_sha256'], 'samples': []}
    atomic(output, summary)
    started = time.monotonic(); last = -10; job = None
    try:
        process, job, name = pc.spawn_owned(command, cwd=destination,
                                          stdout=stdout, stderr=stderr, memory_limit=LIMIT)
        summary.update(pid=process.pid, job=name)
        while True:
            resources = pc.job_resources(job); code = process.poll()
            if time.monotonic() - last >= 3:
                summary['samples'].append({'elapsed_seconds': time.monotonic() - started, **resources})
                atomic(output, summary); last = time.monotonic()
            active = resources.get('job_active_processes', 0)
            if code is not None and active == 0: break
            if code == 0 and active == 1 and closed(destination):
                summary['coherent_idle_helper_closed'] = True
                pc.close_job(job); job = None; break
            if time.time() >= cutoff or time.monotonic() - started >= 900:
                summary.update(status='HOST_SAFETY_STOP', no_automatic_retry=True,
                               reason='Finite import0 wall horizon/cutoff reached')
                atomic(output, summary)
                pc.close_job(job); job = None
                raise RuntimeError('HOST_SAFETY_STOP: owned import Job closed; partial markers preserved')
            time.sleep(.2)
        code = process.wait(timeout=1)
        if job is not None: pc.close_job(job); job = None
        summary.update(exit_code=code, elapsed_seconds=time.monotonic() - started)
        if code != 0 or not closed(destination):
            summary.update(status='FAILED_PRESERVED', no_automatic_retry=True)
            atomic(output, summary)
            raise RuntimeError('Import0 not coherent; preserve exact destination')
        scaffold = support.preserve_source_empty_directories(destination)
        imported = read(destination / 'IMPORTACION_DIAGNOSTICA.json')
        summary.update(status='COMPLETED', new_native_ticks=0, owner_opened=False,
                       comparison=imported['comparison'], physical=imported['result']['physical'],
                       empty_directory_scaffold=scaffold)
        atomic(output, summary)
        return summary
    except BaseException as exc:
        summary.update(error={'type': type(exc).__name__, 'detail': str(exc)}, no_automatic_retry=True)
        if summary['status'] == 'STARTED': summary['status'] = 'FAILED_PRESERVED'
        atomic(output, summary)
        raise
    finally:
        if job is not None: pc.close_job(job)
        stdout.close(); stderr.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--product', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--native-cutoff-utc-epoch', type=float, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.product, args.destination, args.native_cutoff_utc_epoch), ensure_ascii=False, indent=2))
