"""Exportación compacta de MENTE_ACUMULATIVA; no ejecuta DEE ni altera estados."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, shutil, zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LAB = HERE.parent
EV = ROOT / 'evidencia/campanas/MENTE_ACUMULATIVA'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''): h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manual', type=Path, required=True)
    p.add_argument('--revision', default='R1')
    p.add_argument('--delta', action='append', default=[])
    p.add_argument('--vida', action='append', default=[])
    p.add_argument('--documento-editorial', type=Path, action='append', default=[])
    a = p.parse_args()
    if not a.revision.isalnum(): raise ValueError('Revisión explícita alfanumérica requerida.')
    manual = a.manual.resolve(strict=True)
    if not manual.is_relative_to(ROOT) or manual.suffix.lower() != '.docx':
        raise ValueError('El Word vigente debe pertenecer a la raíz del sistema existente.')
    stage = HERE / ('PAQUETE_ANALISIS_' + a.revision)
    stage.mkdir(parents=True, exist_ok=False)
    included, copies = set(), []

    def put(source, member):
        source = Path(source).resolve(strict=True); member = Path(member)
        if member.is_absolute() or '..' in member.parts: raise ValueError('Miembro inseguro.')
        target = stage / member
        if target.exists(): raise ValueError('No se sustituye un miembro exportado: ' + str(member))
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, target)
        digest = sha(source)
        if sha(target) != digest: raise ValueError('La copia no coincide con los bytes originales.')
        included.add(source)
        copies.append({'member': member.as_posix(), 'original': str(source),
                       'relative_to_DCS': source.relative_to(ROOT).as_posix() if source.is_relative_to(ROOT) else None,
                       'bytes': source.stat().st_size, 'sha256': digest, 'transformation': 'NONE_EXACT_BYTES'})

    def permitted(path):
        return (path.is_file() and '__pycache__' not in path.parts
                and path.suffix.lower() not in ('.zip', '.whl', '.dll', '.pyd', '.exe', '.pyc', '.deetsnap')
                and not path.name.endswith('.deetsnap.gz'))

    for f in sorted(HERE.iterdir()):
        if f.is_file() and f.suffix in ('.md', '.csv'): put(f, f.name)
        elif f.is_file() and f.name.startswith('SECUENCIA_') and f.suffix == '.json':
            put(f, Path('CODIGO_Y_PROTOCOLOS/CIERRE') / f.name)
    for name in ('INFORME_RESULTADOS.md', 'CAPACIDADES_ANTES_DESPUES.json', 'DECISIONES_INCORPORACIONES.md'):
        if (LAB/name).is_file(): put(LAB/name, name)
    # Todos los primarios nuevos, incluidos negativos y código exacto, no sólo
    # los dictámenes. El ZIP reducido no pretende ser un respaldo de estados.
    for f in sorted(EV.rglob('*')):
        if permitted(f): put(f, Path('EVIDENCIA_CAUSAL') / f.relative_to(EV))
    for f in sorted(LAB.rglob('*')):
        if not permitted(f) or f.resolve() in included: continue
        relative = f.relative_to(LAB)
        if any(x.startswith(('PAQUETE_ANALISIS', 'ESTIMACION_ANALISIS')) for x in relative.parts): continue
        if relative.parts[0] == 'documentos': continue
        if f.is_relative_to(HERE):
            sub = f.relative_to(HERE)
            if sub.parts[0] == 'recalculo': put(f, Path('RECALCULO') / Path(*sub.parts[1:]))
            elif f.suffix == '.py': put(f, Path('RECALCULO') / f.name)
        elif relative.as_posix() == 'mecanismo/recalcular_mecanismo.py':
            put(f, Path('RECALCULO') / f.name)
        elif f.suffix in ('.py', '.json', '.md', '.csv', '.txt') or f.name.endswith('.json.gz'):
            put(f, Path('CODIGO_Y_PROTOCOLOS') / relative)
    for relative in a.delta:
        part = Path(relative)
        if part.is_absolute() or '..' in part.parts: raise ValueError('Delta fuera de sistema/.')
        put(ROOT / 'sistema' / part, Path('DELTA_OPERATIVO/sistema') / part)
    put(manual, Path('MANUAL') / manual.name)
    for f in a.documento_editorial: put(f, Path('MANUAL') / f.name)
    checkpoints = []
    for name in a.vida:
        recordfile = ROOT / 'sistema/estado/vidas' / name / 'VIDA.json'
        record = json.loads(recordfile.read_bytes())
        snap = (ROOT / 'sistema' / record['snapshot']).resolve(strict=True)
        if not snap.is_relative_to(ROOT / 'sistema/estado/checkpoints'): raise ValueError('Estado fuera del almacén declarado.')
        digest = sha(snap)
        if digest != record['snapshot_sha256']: raise ValueError('Snapshot final difiere de su ficha.')
        checkpoints.append({'life': name, 'tick': record['physical']['tick'], 'local_path': str(snap),
                            'relative_to_DCS': snap.relative_to(ROOT).as_posix(), 'bytes': snap.stat().st_size,
                            'sha256': digest, 'included': False, 'reason': 'Estado operativo completo local y en la distribución; no en el análisis reducido.'})
        projection = {k:record.get(k) for k in ('schema','life_id','world_id','profile','branch','parent','knowledge','memberships','snapshot','snapshot_sha256','physical','interfaces','protocols','availability')}
        projection['source_record'] = {'local_path':str(recordfile), 'bytes':recordfile.stat().st_size,
                                       'sha256':sha(recordfile), 'extraction':'Exact listed metadata fields; operational history/result journal omitted, not a complete native snapshot.'}
        target = stage/'CONTINUIDAD/FICHAS'/(name+'.json'); target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(projection,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    for f in sorted(ROOT.glob('CONTINUIDAD_MENTE*.json')):
        put(f, Path('CONTINUIDAD') / f.name)
    omitted = []
    for base in (LAB, EV):
        for f in sorted(base.rglob('*')):
            if not f.is_file() or f.resolve() in included or '__pycache__' in f.parts: continue
            if any(x.name.startswith(('PAQUETE_ANALISIS', 'ESTIMACION_ANALISIS')) for x in f.parents): continue
            omitted.append({'local_path': str(f), 'relative_to_DCS': f.relative_to(ROOT).as_posix(),
                            'bytes': f.stat().st_size, 'sha256': sha(f),
                            'reason': 'Intermedio editorial, respaldo operativo o archivo de trabajo no necesario para el recálculo exportado; primarios nuevos se preservan sin filtrar éxitos.'})
    index = {'schema': 'MENTE_ACUMULATIVA.analysis.sources.v1', 'created_utc': datetime.now(timezone.utc).isoformat(),
             'exact_copies': copies, 'complete_selected_states_local_only': checkpoints,
             'other_local_omissions': omitted, 'no_engine_or_WHL': True,
             'scope': 'Análisis científico con primarios. No respaldo operativo completo ni sustituto de los snapshots completos.'}
    (stage / 'INDICE_FUENTES_Y_OMISIONES.json').write_text(json.dumps(index, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    estimate = HERE / ('ESTIMACION_ANALISIS_' + a.revision + '.zip')
    with zipfile.ZipFile(estimate, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(stage.rglob('*')):
            if f.is_file(): z.write(f, f.relative_to(stage).as_posix())
    print(json.dumps({'stage': str(stage), 'files': sum(f.is_file() for f in stage.rglob('*')),
                      'estimate_bytes': estimate.stat().st_size, 'new_ticks': 0,
                      'full_distribution_proof_required_before_final_seal': True}, ensure_ascii=False))


if __name__ == '__main__': main()
