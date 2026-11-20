"""Prepare, DO NOT DEPLOY, two small RP instrument extensions for C2C.

Read-only recipe-specific recalculation and preservation of inner-stage
NULL/rejections do not alter the engine, decoder, actor policy or any state.
Root must review/apply while no RP material run is live. No RP write here.
"""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parents[1];R=P.parent.parent.parent
RP=R/'DEE Cognitive 2.0/reproducibilidad'

def once(s,a,b):
    if s.count(a)!=1:raise ValueError('RP source locator changed: '+a[:100])
    return s.replace(a,b,1)

if __name__=='__main__':
    folder=P/'codigo/RP_C2C_PROPUESTA_OP1'
    if folder.exists():raise ValueError('Preserve prior tool proposal')
    folder.mkdir()
    hashes={};originals={}
    for name in('reproducir.py','ejecutar_diagnostico.py'):
        originals[name]=(RP/name).read_bytes();hashes[name]=hashlib.sha256(originals[name]).hexdigest()
    s=originals['reproducir.py'].decode('utf-8-sig').replace('\r\n','\n')
    helper='''def recipe_analysis_check(r):
    """Static evidence/script verification only; no Native/actor import."""
    a = r.get('analysis')
    if not isinstance(a, dict) or a.get('interface') != 'DEE.recalculation.root_outdir.v1':
        raise ValueError('La receta no tiene recálculo stdlib incorporado con esta interfaz')
    root = resource(a)
    manifest = inside(root, a.get('manifest', 'MANIFIESTO_ESTABLE.json'))
    if sha(manifest) != a['manifest_sha256']:
        raise ValueError('El manifiesto del recálculo de receta cambió')
    rows = read(manifest).get('files')
    if not isinstance(rows, list):
        raise ValueError('Se requiere lista files del material de recálculo')
    checked = checked_files(root, rows, exact=True, omit=(manifest.relative_to(root).as_posix(),))
    script = inside(root, a['recalculation_script'])
    if script.suffix != '.py':
        raise ValueError('Recálculo Python preservado; no shell/comando arbitrario')
    return {'path': str(root), 'script': str(script), 'manifest_sha256': sha(manifest), **checked}


'''
    s=once(s,'def verification(name):',helper+'def verification(name):')
    s=once(s,"    check('full_prefix', lambda: verify_pair(c['pairs'][r['prefix']]))",
        "    check('full_prefix', lambda: verify_pair(c['pairs'][r['prefix']]))\n    if r.get('analysis'):\n        check('recipe_documentary_recalculation', lambda: recipe_analysis_check(r))")
    s=once(s,"def recalculate(args):\n    c = config(); a = c['analysis']; root = resource(a)",'''def recalculate(args):
    if getattr(args, 'receta', None):
        if args.grupos:
            raise ValueError('Los grupos históricos PI02 no se aplican a otra receta')
        r = recipe(args.receta)
        verified = recipe_analysis_check(r)
        root = Path(verified['path'])
        dest = fresh_destination(args.destino)
        if dest.exists():
            raise ValueError('El recálculo de receta exige un directorio NUEVO')
        command = [sys.executable, '-I', '-B', '-X', 'utf8', verified['script'], '--root', str(root), '--out-dir', str(dest)]
        process = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding='utf-8',
                                 errors='strict', creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if process.stdout:
            sys.stdout.write(process.stdout); sys.stdout.flush()
        if process.stderr:
            sys.stderr.write(process.stderr); sys.stderr.flush()
        return process.returncode
    c = config(); a = c['analysis']; root = resource(a)''')
    s=once(s,"    calc = sub.add_parser('recalcular'); calc.add_argument('--destino', required=True)",
        "    calc = sub.add_parser('recalcular'); calc.add_argument('--destino', required=True)\n    calc.add_argument('--receta', help='Recálculo documental de una receta incorporada, sin Native')")
    s=once(s,"('id', 'title', 'prefix', 'modalities', 'assistance', 'limitations', 'verification')",
        "('id', 'title', 'prefix', 'modalities', 'assistance', 'limitations', 'verification', 'usage')")
    ast.parse(s);(folder/'reproducir.py').write_text(s,encoding='utf8',newline='')
    s=originals['ejecutar_diagnostico.py'].decode('utf-8-sig').replace('\r\n','\n')
    s=once(s,'def receipts(value, paths):','def receipts(value, paths, nullable_paths=(), preserve_stop=False):')
    s=once(s,'    for path in paths:\n        items = path_value(value, path)',
        '''    for path, nullable in [(p, False) for p in paths] + [(p, True) for p in nullable_paths]:
        try:
            items = path_value(value, path)
        except (KeyError, IndexError, TypeError):
            if nullable and preserve_stop:
                continue  # A declared unexecuted inner stage after actual preserved NULL/stop.
            raise
        if items is None and nullable and preserve_stop:
            continue
        if not isinstance(items, list):
            raise ValueError('La ruta fijada no contiene una lista de recibos Native')''')
    s=once(s,"                    collected = receipts(result, step.get('receipt_paths', []))",'''                    stop_flags = {}
                    for stop_path in step.get('preserved_stop_paths', []):
                        flag = path_value(result, stop_path)
                        if type(flag) is not bool:
                            raise ValueError('La bandera de parada preservada debe ser bool, no0/NULL')
                        stop_flags['/'.join(map(str, stop_path))] = flag
                    preserved_stage_stop = any(stop_flags.values())
                    collected = receipts(result, step.get('receipt_paths', []),
                                         step.get('nullable_receipt_paths', []), preserved_stage_stop)
                    if step.get('stop_on_unapplied_receipt') and any(x['status'] != 'applied' for x in collected.values()):
                        preserved_stage_stop = True''')
    s=once(s,"                           'primary': 'ensayos/' + identifier + '.json'}",
        "                           'primary': 'ensayos/' + identifier + '.json',\n                           'preserved_inner_stage_flags': stop_flags,\n                           'preserved_inner_stage_stop': preserved_stage_stop}")
    s=once(s,"                    if step.get('stop_on_NULL') and value is None:",
        "                    if (step.get('stop_on_NULL') and value is None) or preserved_stage_stop:")
    s=once(s,"                            'scope': 'Fixed reader returned NULL; stop after preserving this actual opportunity. Material0 is not NULL. No next material request or implicit repair.'}",
        "                            'scope': 'Fixed reader NULL, preserved inner-stage flag or unapplied receipt; close after this actual opportunity. Material0 is not NULL. No next material request or implicit repair.'}")
    ast.parse(s);(folder/'ejecutar_diagnostico.py').write_text(s,encoding='utf8',newline='')
    proof={'schema':'PI04.C2C.RP_tool_proposal.OP1','status':'PREPARED_NOT_APPLIED',
        'source_baselines':hashes,'proposals':{n:hashlib.sha256((folder/n).read_bytes()).hexdigest()for n in originals},
        'RP_originals_unchanged':all((RP/n).read_bytes()==b for n,b in originals.items()),'Native_ticks':0,
        'changes':['Optional recipe-specific documentary recalculation with preserved manifest; historical PI02 default intact',
            'Explicitly report/forward recalculation stdout on Windows','Nullable inner-stage receipt paths only when actual preserved stop flag is true',
            'Stop before next material request on NULL, rejected receipt or explicit inner-stage stop; no decoder/actor/engine changes'],
        'apply_preconditions':['Root review','No RP material guard/run live','Exact source baselines still match','Actual closed C2C20 reference and stable capsule/evidence before enabling recipe']}
    (folder/'PROPUESTA_Y_BASELINES.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(proof,ensure_ascii=False,indent=2))
