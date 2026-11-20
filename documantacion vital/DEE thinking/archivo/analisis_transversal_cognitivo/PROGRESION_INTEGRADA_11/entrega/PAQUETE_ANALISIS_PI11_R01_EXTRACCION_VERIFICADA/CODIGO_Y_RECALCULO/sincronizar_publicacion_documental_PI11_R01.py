"""PI11 two-file documentary publication synchronization; PLAN by default.

No Native/owner/SQLite/GUI or operational code import. Only --aplicar can
replace PROYECTO.json and CONTINUIDAD_DEE_COGNITIVE_2_0.json, and only their
explicit CURRENT documentary top-level fields. All old history is retained.
Owner closure must already be checked by Root and supplied as a pinned gate;
this script does not claim that absence of a lock independently proves closure.

Required gate schema DEE.PI11.owner_closed_documentary_gate.R01:
life_id,tick,snapshot_sha256,owner_closed_coherently:true,
no_live_affected_writer:true,unresolved_requests:0,evidence:[{path,sha256}].
Apply additionally requires exact --project-before-sha256 and
--continuity-before-sha256 from the final PLAN, after any six-selector CAS.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import copy
import hashlib
import json
import os
import re
import xml.etree.ElementTree as ET
import zipfile

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
C = R / 'DEE Cognitive 2.0'
PUBLICATION = P / 'documentos/PUBLICACION_EDICION_1_40_PI11_R01.json'
MANUAL = C / 'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
COMPENDIUM = R / 'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
FILES = (C / 'PROYECTO.json', C / 'CONTINUIDAD_DEE_COGNITIVE_2_0.json')
HISTORY_KEY = 'PI11_before_documentary_publication'
UPDATE_KEY = 'last_documentary_update_PI11'
FLAT = ('manual_internal_edition', 'manual_current_sha256', 'manual_current_bytes', 'manual_publication_witness')
CURRENT = {'manual', 'manual_current', 'compendium_current', *FLAT}
ALLOWED_TOP = CURRENT | {HISTORY_KEY, UPDATE_KEY}
WORK = P / 'control/SINCRONIZACION_PUBLICACION_DOCUMENTAL_PI11_R01'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def regular(path):
    p = Path(path).absolute()
    for node in (p, *p.parents):
        need(not node.is_symlink(), 'No linked source/output')
        if node.exists():
            need(not (getattr(node.lstat(), 'st_file_attributes', 0) & 1024), 'No reparse source/output')
    need(p.is_file() and p.resolve().is_relative_to(R.resolve()), 'Existing regular DEE source required')
    return p.resolve()


def info(path):
    p = regular(path)
    return {'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p)}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def write_new(path, value):
    with Path(path).open('xb') as f:
        f.write(encoded(value)); f.flush(); os.fsync(f.fileno())


def differences(a, b, path=''):
    if type(a) is not type(b):
        return [path]
    if isinstance(a, dict):
        return [p for key in sorted(set(a) | set(b)) for p in
                ([path + '/' + key] if key not in a or key not in b else differences(a[key], b[key], path + '/' + key))]
    if isinstance(a, list):
        return [path + '/length'] if len(a) != len(b) else [p for i, (x, y) in enumerate(zip(a, b)) for p in differences(x, y, path + '/' + str(i))]
    return [] if a == b else [path]


def publication():
    pub = info(PUBLICATION)
    value = read(PUBLICATION)
    need(value.get('schema') == 'DEE.PI11.actual_complete_DOCX_publication.R01'
         and value.get('internal_edition') == '1.40' and value.get('Native_imported') is False,
         'Actual complete two-document1.40publication required')
    need(value.get('visual_status') in ('rendered_and_reviewed', 'render_blocked_explicit_limitation'), 'Explicit real visual status required')
    rows = value.get('rows')
    need(isinstance(rows, list) and len(rows) == 2, 'Exactly two published DOCX rows required')
    expected = {MANUAL.resolve(), COMPENDIUM.resolve()}; checked = {}
    for row in rows:
        published = row['published']; p = regular(published['path'])
        need(p in expected and p not in checked and p.stat().st_size == published['bytes']
             and sha(p) == published['sha256'] == row['output']['sha256'], 'Published full DOCX identity/hash differs')
        with zipfile.ZipFile(p) as z:
            need(z.testzip() is None, 'Published DOCX CRC failure')
            core = ET.fromstring(z.read('docProps/core.xml'))
            version = core.find('{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}version')
            need(version is not None and version.text == '1.40', 'Published internal edition is not1.40')
        checked[p] = info(p)
    need(set(checked) == expected, 'Manual/Compendium publication set differs')
    return pub, value, checked[MANUAL.resolve()], checked[COMPENDIUM.resolve()]


def owner_gate(path, expected_hash):
    gate_ref = info(path)
    need(re.fullmatch('[0-9a-f]{64}', expected_hash or '') and gate_ref['sha256'] == expected_hash, 'Pinned Root owner-closure gate required')
    gate = read(path)
    need(gate.get('schema') == 'DEE.PI11.owner_closed_documentary_gate.R01'
         and gate.get('owner_closed_coherently') is True and gate.get('no_live_affected_writer') is True
         and gate.get('unresolved_requests') == 0 and gate.get('evidence'), 'Actual coherent closed-owner evidence required')
    active_path = C / 'sistema/estado/ACTIVO.json'; active = read(regular(active_path))
    need(gate['life_id'] == active['life_id'] and gate['tick'] == active['tick']
         and gate['snapshot_sha256'] == active['snapshot_sha256'], 'Owner closure must describe current exact selection')
    card_path = C / 'sistema/estado/vidas' / active['life_id'] / 'VIDA.json'; card = read(regular(card_path))
    need(card['physical']['tick'] == active['tick'] and card['snapshot_sha256'] == active['snapshot_sha256'], 'Current active/card mismatch')
    snapshot = regular(C / 'sistema' / card['snapshot'])
    need(sha(snapshot) == active['snapshot_sha256'], 'Current complete snapshot locator/hash differs')
    lock = C / 'sistema/estado/locks' / (active['life_id'] + '.lock')
    need(not lock.exists() and not lock.is_symlink(), 'Affected owner lock remains; do not clear it here')
    for ref in gate['evidence']:
        need(info(ref['path'])['sha256'] == ref['sha256'], 'Closure evidence changed')
    protected = {str(p.resolve()): sha(p) for p in (active_path, card_path, snapshot)}
    return gate_ref, gate, active, protected


def descriptor(old, artifact, pub, visual, manual):
    out = copy.deepcopy(old) if isinstance(old, dict) else {}
    out.update(artifact)
    out.update(internal_edition='1.40', publication_witness={'path': pub['path'], 'sha256': pub['sha256']},
               visual_validation=visual == 'rendered_and_reviewed', visual_status=visual)
    if manual:
        out.update(path_relative_to_product=MANUAL.name, edition='1.40', document_publication=pub['path'])
    return out


def plan(args):
    need(args.owner_closure is not None, 'Explicit final Root owner-closure gate required')
    pub, pub_value, manual, compendium = publication()
    gate_ref, gate, active, protected = owner_gate(args.owner_closure, args.owner_closure_sha256)
    before = {p.name: read(regular(p)) for p in FILES}
    cas = {p.name: sha(p) for p in FILES}
    need(before[FILES[1].name].get('life_id') == active['life_id'], 'Finish operational continuity synchronization before documentary synchronization')
    selected = before[FILES[0].name].get('selected_life')
    need(not isinstance(selected, str) or selected == active['life_id'], 'Project selection is not current; this tool only changes documentary fields')
    now = datetime.now(timezone.utc).isoformat()
    after = copy.deepcopy(before)
    already = all(HISTORY_KEY in j and j.get(UPDATE_KEY, {}).get('publication', {}).get('sha256') == pub['sha256'] for j in before.values())
    if already:
        for j in before.values():
            current = j['manual_current']
            if isinstance(current, dict):
                need(current['sha256'] == manual['sha256'] and current['bytes'] == manual['bytes'], 'Prior sync claim has inconsistent current Manual')
            else:
                need(j['manual_current_sha256'] == manual['sha256'] and j['manual_current_bytes'] == manual['bytes'], 'Prior sync claim has inconsistent flat Manual')
            need(j['compendium_current']['sha256'] == compendium['sha256'], 'Prior sync claim has inconsistent Compendium')
        return {'schema': 'DEE.PI11.documentary_publication_sync.R01', 'mode': 'ALREADY_APPLIED_VERIFIED',
                'publication': pub, 'cas_before': cas, 'modified_files': [], 'Native_calls': 0}, before, after, protected
    need(all(HISTORY_KEY not in j and UPDATE_KEY not in j for j in before.values()), 'Partial/different prior PI11 documentary synchronization preserved; inspect it first')
    for filename, j in after.items():
        old = before[filename]
        j[HISTORY_KEY] = {'captured_utc': now, 'source_file_sha256': cas[filename],
                          'fields': {k: copy.deepcopy(old[k]) for k in CURRENT if k in old}}
        for key in ('manual', 'manual_current'):
            if key in old:
                if isinstance(old[key], dict):
                    j[key] = descriptor(old[key], manual, pub, pub_value['visual_status'], True)
                else:
                    need(key == 'manual_current' and old[key] == MANUAL.name, 'Unexpected manual locator shape; no silent migration')
                    j[key] = MANUAL.name
        values = {'manual_internal_edition': '1.40', 'manual_current_sha256': manual['sha256'],
                  'manual_current_bytes': manual['bytes'], 'manual_publication_witness': pub['path']}
        for key in FLAT:
            if key in old or filename == 'PROYECTO.json':
                j[key] = values[key]
        j['compendium_current'] = descriptor(old.get('compendium_current'), compendium, pub, pub_value['visual_status'], False)
        j[UPDATE_KEY] = {'at': now, 'publication': {'path': pub['path'], 'sha256': pub['sha256']},
                         'manual_sha256': manual['sha256'], 'compendium_sha256': compendium['sha256'],
                         'scope': 'Current documentary fields only; no operational cut, selector, life, code or snapshot modification'}
    changes = {name: differences(before[name], after[name]) for name in before}
    need(all(path.split('/')[1] in ALLOWED_TOP for paths in changes.values() for path in paths), 'Proposed edit escaped documentary top-level whitelist')
    result = {'schema': 'DEE.PI11.documentary_publication_sync.R01', 'mode': 'APPLY' if args.aplicar else 'PLAN',
              'at': now, 'publication': pub, 'owner_closure_gate': gate_ref,
              'life_id_read_only': active['life_id'], 'tick_read_only': active['tick'],
              'cas_before': cas, 'changed_paths': changes, 'modified_files': [str(p) for p in FILES],
              'manual': manual, 'compendium': compendium, 'protected_hashes_before': protected,
              'Native_calls': 0, 'SQLite_opened': False, 'operational_fields_changed': False,
              'historical_fields_preserved': True, 'backup_and_intent_directory': str(WORK)}
    return result, before, after, protected


def apply(args, result, before, after, protected):
    if result['mode'] == 'ALREADY_APPLIED_VERIFIED':
        return result
    expected = {'PROYECTO.json': args.project_before_sha256, 'CONTINUIDAD_DEE_COGNITIVE_2_0.json': args.continuity_before_sha256}
    need(all(re.fullmatch('[0-9a-f]{64}', v or '') for v in expected.values()) and expected == result['cas_before'], 'Exact two CAS hashes from final PLAN required before apply')
    need(not WORK.exists() and not WORK.is_symlink(), 'Existing/partial documentary synchronization preserved')
    for p in FILES:
        need(not Path(str(p) + '.PI11.docs.pending').exists(), 'Unresolved pending JSON preserved')
    need(all(sha(Path(p)) == value for p, value in protected.items()), 'Protected state changed before writing')
    need(sha(PUBLICATION) == result['publication']['sha256'], 'Publication changed before synchronization')
    WORK.mkdir(parents=True)
    for p in FILES:
        need(sha(p) == expected[p.name], 'Concurrent descriptor edit before backup')
        with (WORK / p.name).open('xb') as f:
            f.write(p.read_bytes()); f.flush(); os.fsync(f.fileno())
        need(sha(WORK / p.name) == expected[p.name], 'Literal descriptor backup mismatch')
        write_new(Path(str(p) + '.PI11.docs.pending'), after[p.name])
    write_new(WORK / 'INTENCION.json', result)
    for p in FILES:
        need(sha(p) == expected[p.name], 'Concurrent descriptor edit during publication; backups/pending retained')
        os.replace(Path(str(p) + '.PI11.docs.pending'), p)
        need(read(p) == after[p.name], 'Published descriptor differs')
    need(all(sha(Path(p)) == value for p, value in protected.items()), 'Protected state changed concurrently; inspect, do not overwrite it')
    result.update(mode='APPLIED', cas_after={p.name: sha(p) for p in FILES},
                  protected_hashes_after={p: sha(Path(p)) for p in protected},
                  actual_changed_top_level_fields={name: sorted(k for k in set(before[name]) | set(after[name]) if before[name].get(k) != after[name].get(k)) for name in before})
    write_new(WORK / 'SINCRONIZACION.json', result)
    return result


def main(args):
    if not args.aplicar and (not PUBLICATION.exists() or args.owner_closure is None):
        print(json.dumps({'mode': 'REQUIREMENTS_ONLY_PLAN', 'writes': 0, 'Native_calls': 0,
                          'publication_required': str(PUBLICATION), 'publication_present': PUBLICATION.exists(),
                          'required': ['--owner-closure ACTUAL_PINNED_JSON', '--owner-closure-sha256 ACTUAL',
                                       '--project-before-sha256 FINAL_PLAN_HASH (apply only)',
                                       '--continuity-before-sha256 FINAL_PLAN_HASH (apply only)'],
                          'owner_gate_schema': 'DEE.PI11.owner_closed_documentary_gate.R01',
                          'allowed_files': [str(p) for p in FILES], 'default': 'Read-only plan; never opensSQLiteorOwner'}, ensure_ascii=False))
        return
    result, before, after, protected = plan(args)
    if args.aplicar:
        result = apply(args, result, before, after, protected)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--owner-closure', type=Path)
    ap.add_argument('--owner-closure-sha256')
    ap.add_argument('--project-before-sha256')
    ap.add_argument('--continuity-before-sha256')
    ap.add_argument('--aplicar', action='store_true')
    main(ap.parse_args())
