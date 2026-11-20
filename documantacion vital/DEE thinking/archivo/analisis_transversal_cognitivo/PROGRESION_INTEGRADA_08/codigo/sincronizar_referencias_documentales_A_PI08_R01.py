"""Root-only CAS of current document references; default prepares P8-only plan.

No DOCX writing, Native import or scientific/state/selection update. Historical
editions remain literal. The old transversal scientific chapters/cuts are not
reinterpreted as PI08; a separate explicit current-document descriptor is added.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, copy, hashlib, json, os

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
C = R / 'DEE Cognitive 2.0'
PUBLICATION = P / 'documentos/PUBLICACION_A_1_35.json'
STAGE = P / 'control/REFERENCIAS_A_1_35_PROPUESTAS_R01'
PLAN = P / 'control/PLAN_REFERENCIAS_A_1_35_R01.json'
OUTPUT = P / 'control/REFERENCIAS_A_1_35_SINCRONIZADAS_R01.json'
TARGETS = {'PROYECTO': C / 'PROYECTO.json', 'CONTINUIDAD': C / 'CONTINUIDAD_DEE_COGNITIVE_2_0.json',
           'REVISION': R / 'archivo/analisis_transversal_cognitivo/REVISION_TRANSVERSAL.json'}

def require(ok, text):
    if not ok: raise ValueError(text)
def read(path): return json.loads(path.read_text('utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def put(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')
def regular(path):
    for node in (path, *path.parents):
        require(not node.exists() or not(node.is_symlink() or getattr(node.lstat(), 'st_file_attributes', 0)&1024), 'No linked document reference')

def proposed(values, publication):
    values = copy.deepcopy(values)
    manual, compendium = publication['files']
    witness = {'path': str(PUBLICATION), 'sha256': sha(PUBLICATION)}
    descriptors = []
    for source, edition in ((manual, '1.35'), (compendium, 'PI08 A cumulative publication,10nov2026')):
        target = Path(source['target']); old = P / 'documentos/respaldo_1_34' / target.name
        require(target.is_file() and target.stat().st_size == source['bytes'] and sha(target) == source['new_sha256'], 'Published complete document differs')
        require(old.is_file() and sha(old) == source['old_sha256'], 'Literal complete1.34 backup unavailable')
        descriptors.append({'path': str(target), 'bytes': source['bytes'], 'sha256': source['new_sha256'],
            'internal_edition': edition, 'same_logical_manual_and_filename': target == C / target.name,
            'prior_complete_document': {'path': str(old), 'bytes': old.stat().st_size, 'sha256': source['old_sha256']},
            'publication_witness': witness, 'structural_validation': publication['structural_proof'],
            'visual_qa': 'NOT_VALIDATED', 'validation_visual': 'NOT_VALIDATED',
            'visual_witness': publication['visual_render_attempt'], 'visual_limitation': publication['visual_limitation'],
            'rendered_pdf': None, 'reviewed_images': []})
    m, comp = descriptors
    project, continuity, revision = (values[key] for key in ('PROYECTO', 'CONTINUIDAD', 'REVISION'))
    fields = ('manual_current', 'manual_internal_edition', 'manual_current_sha256', 'manual_current_bytes', 'manual_publication_witness')
    require('manual_before_PI08_A_publication_historical' not in project, 'Existing PI08 publication references protected')
    project['manual_before_PI08_A_publication_historical'] = {key: copy.deepcopy(project.get(key)) for key in fields}
    project.update(manual_current=Path(manual['target']).name, manual_internal_edition='1.35',
                   manual_current_sha256=manual['new_sha256'], manual_current_bytes=manual['bytes'],
                   manual_publication_witness=str(PUBLICATION), compendium_current=comp)
    continuity['manual_before_PI08_A_publication_historical'] = {'manual': copy.deepcopy(continuity.get('manual')), 'manual_current': copy.deepcopy(continuity.get('manual_current'))}
    continuity['manual_current'] = m
    continuity['manual'] = {'edition': '1.35', 'path_relative_to_product': Path(manual['target']).name,
                            'sha256': manual['new_sha256'], 'bytes': manual['bytes'], 'document_publication': str(PUBLICATION),
                            'validation_visual': 'NOT_VALIDATED'}
    continuity['compendium_current'] = comp
    continuity['last_documentary_update_PI08_A'] = witness
    require('document_publication_PI08_A_1_35' not in revision, 'Existing transversal publication reference protected')
    current = {'manual': m, 'compendium': comp, 'publication': witness,
               'scope': 'Current published complete documents only; historical scientific entries and their edition/cut references remain unchanged. No visual QA inferred.'}
    if 'current_document_references' in revision:
        revision['current_document_references_before_PI08_A_historical'] = copy.deepcopy(revision['current_document_references'])
    revision['current_document_references'] = current
    revision['document_publication_PI08_A_1_35'] = copy.deepcopy(current)
    return values

def main(args):
    require(not OUTPUT.exists(), 'Completed reference synchronization protected')
    publication = read(PUBLICATION)
    require(publication['edition'] == '1.35' and publication['Native_executed'] is False and publication['visual_validation'] is False, 'Exact actual publication with honest visual limitation required')
    for name in ('structural_proof', 'visual_render_attempt'):
        row = publication[name]; require(sha(Path(row['path'])) == row['sha256'], 'Publication validation witness differs')
    activefile = C / 'sistema/estado/ACTIVO.json'; active = read(activefile)
    require(active['life_id'] == publication['actual_main']['life_id'] and active['tick'] == 861426, 'Actual stable adopted A required')
    cardfile = C / 'sistema/estado/vidas' / active['life_id'] / 'VIDA.json'; card = read(cardfile)
    require(card['snapshot_sha256'] == active['snapshot_sha256'], 'Actual current selected snapshot mismatch')
    protected = [activefile, cardfile, C / 'sistema' / card['snapshot'], C / 'sistema/contratos/PI08_USO_OPERATIVO_R01.json']
    critical = {str(path): sha(path) for path in protected}
    if not PLAN.exists():
        require(not STAGE.exists(), 'Partial prior reference stage preserved')
        originals = {key: read(path) for key, path in TARGETS.items()}
        result = proposed(originals, publication)
        STAGE.mkdir()
        rows = []
        for name, path in TARGETS.items():
            regular(path); target = STAGE / (name + '.json'); put(target, result[name])
            rows.append({'name': name, 'target': str(path), 'old_sha256': sha(path), 'staged': str(target), 'new_sha256': sha(target)})
        put(PLAN, {'schema': 'DEE.PI08.A.current_document_references.CAS_plan.R01',
                   'publication_sha256': sha(PUBLICATION), 'rows': rows, 'Native_critical_hashes': critical,
                   'historical_scientific_fields_retained': True, 'Native_executed': False})
    plan = read(PLAN)
    require(plan['publication_sha256'] == sha(PUBLICATION), 'Actual publication changed after plan')
    require(all(sha(Path(path)) == digest for path, digest in plan['Native_critical_hashes'].items()), 'Protected adopted A changed')
    for row in plan['rows']:
        require(sha(Path(row['target'])) == row['old_sha256'] and sha(Path(row['staged'])) == row['new_sha256'], 'CAS reference/stage differs')
    if args.aplicar:
        backup = P / 'control/REFERENCIAS_ANTES_A_1_35_R01'; require(not backup.exists(), 'Literal prior reference backups protected'); backup.mkdir()
        for row in plan['rows']:
            target = Path(row['target']); (backup / (row['name'] + '.json')).write_bytes(target.read_bytes())
        for row in plan['rows']:
            target = Path(row['target']); temporary = target.with_name(target.name + '.PI08_DOCREF_WRITING')
            with temporary.open('xb') as stream: stream.write(Path(row['staged']).read_bytes()); stream.flush(); os.fsync(stream.fileno())
            os.replace(temporary, target)
        require(all(sha(Path(path)) == digest for path, digest in critical.items()), 'Native/card/contract changed concurrently')
        put(OUTPUT, {'schema': 'DEE.PI08.A.current_document_references.synced.R01', 'applied': True,
                     'recorded_utc': datetime.now(timezone.utc).isoformat(), 'rows': plan['rows'],
                     'literal_before': str(backup), 'Native_critical_hashes_all_unchanged': True,
                     'publication': {'path': str(PUBLICATION), 'sha256': sha(PUBLICATION)},
                     'Native_executed': False, 'visual_qa': 'NOT_VALIDATED', 'historical_references_preserved': True})
    print(json.dumps({'mode': 'APPLIED_ROOT_ONLY' if args.aplicar else 'CAS_PLAN_READY_NO_PRODUCT_WRITE',
                      'proof': str(OUTPUT if args.aplicar else PLAN), 'sha256': sha(OUTPUT if args.aplicar else PLAN),
                      'Native_executed': False, 'files': len(plan['rows'])}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--aplicar', action='store_true')
    main(parser.parse_args())
