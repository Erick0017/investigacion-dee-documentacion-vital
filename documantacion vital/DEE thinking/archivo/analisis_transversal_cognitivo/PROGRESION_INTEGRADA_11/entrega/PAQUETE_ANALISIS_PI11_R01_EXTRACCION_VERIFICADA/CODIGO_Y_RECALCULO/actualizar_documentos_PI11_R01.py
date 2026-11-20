"""Surgical PI11 Manual/Compendium authoring from explicit closed facts.

No DEE, Native or desktop Word import. Default is read-only. Root must run
the documents skill edit marker once for these two outputs before --author.
--preserve-base only preserves the two literal 1.39 sources. --check-facts
does not write. A report is evidence, never an instruction to fabricate facts.
Authoring stages full DOCX files; only --publish replaces the two rectors,
with pinned compare-and-swap, verified backups and explicit visual status.
"""
from pathlib import Path
from datetime import datetime, timezone
from xml.sax.saxutils import escape
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import zipfile
import xml.etree.ElementTree as ET

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
C = R / 'DEE Cognitive 2.0'
D = P / 'documentos'
MAN = C / 'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
COMP = R / 'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
BASE = D / 'base_1_39'
BASE_MANIFEST = BASE / 'FUENTES_ORIGINALES_1_39_PI11_R01.json'
PINS = {
    MAN.name: '5e6763fa8ebfb72f469f3dcb9a18fe59e5ed37f36e8bc5c682635d0ac64f88fc',
    COMP.name: 'fa390e35bc236e57c38bd30fcafec713e6759ad506d598a00c393a1b33327c5e',
}
HELPER = P / 'codigo/OOXML_HELPERS_PI08_B_LITERAL.py'
HELPER_SHA = 'ef5a23de5875c8ccd352f961417adfe068a190bdf46c131aeaf2d183f2790358'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
TITLE = '56 PI11 Hábitat persistente y adaptación sistémica'
ANCHOR = 'DEE_PI11_CAP56'
COMP_TITLE = 'PI11 Hábitat persistente y adaptación sistémica'
COMP_ANCHOR = 'DEE_PI11_COMPENDIO'
STAGE = D / 'edicion_1_40'
STRUCTURE = D / 'ESTRUCTURA_EDICION_1_40_PI11_R01.json'
PUBLICATION = D / 'PUBLICACION_EDICION_1_40_PI11_R01.json'
CONTROL_LABELS = {'Documento', 'Corte de liberación registrado', 'Base principal', 'Estado de esta edición'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def info(path):
    p = Path(path)
    return {'path': str(p.resolve()), 'bytes': p.stat().st_size, 'sha256': sha(p)}


def regular(path):
    original = Path(path)
    p = original.resolve(strict=True)
    for node in (original, *original.parents):
        require(not node.is_symlink() and not (getattr(node.lstat(), 'st_file_attributes', 0) & 1024),
                'Linked/reparse document or evidence path refused')
    require(p.is_file(), 'Existing regular file required')
    return p


def put(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def helper(anchor):
    require(sha(HELPER) == HELPER_SHA, 'Literal OOXML helper changed')
    spec = importlib.util.spec_from_file_location('PI11_literal_OOXML_helper', HELPER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.ANCHOR = anchor
    return m


def source_check(backup_required=True):
    for source in (MAN, COMP):
        regular(source)
        require(sha(source) == PINS[source.name], 'Current source is not the preserved 1.39 source; inspect concurrent changes')
        with zipfile.ZipFile(source) as z:
            require(z.testzip() is None, 'Source DOCX member CRC failure')
        if backup_required:
            regular(BASE / source.name)
            require(sha(BASE / source.name) == PINS[source.name], 'Literal source backup differs')
    if backup_required:
        manifest = read(BASE_MANIFEST)
        require(manifest['schema'] == 'DEE.PI11.literal_DOCX_sources_1_39.R01'
                and manifest['authoring_executed'] is False and manifest['published'] is False,
                'Unmodified literal backup manifest required')


def preserve_base():
    source_check(False)
    if BASE_MANIFEST.exists():
        source_check(True)
        return {'already_preserved': True, 'manifest': info(BASE_MANIFEST)}
    require(not BASE.exists(), 'Unresolved/partial backup directory preserved; inspect it before retrying')
    BASE.mkdir(parents=True)
    rows = []
    for source in (MAN, COMP):
        shutil.copyfile(source, BASE / source.name)
        require(sha(BASE / source.name) == PINS[source.name], 'Backup hash mismatch')
        rows.append({'source': info(source), 'backup': info(BASE / source.name)})
    put(BASE_MANIFEST, {'schema': 'DEE.PI11.literal_DOCX_sources_1_39.R01',
                        'at': datetime.now(timezone.utc).isoformat(), 'rows': rows,
                        'authoring_executed': False, 'published': False, 'Native_imported': False})
    return {'already_preserved': False, 'manifest': info(BASE_MANIFEST)}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_ref(ref):
    path = regular(ref['path'])
    require(path.is_relative_to(R.resolve()) and sha(path) == ref['sha256'], 'Actual DEE evidence/report reference changed')


def validate_facts(f, backup_required=False):
    require(f.get('schema') == 'DEE.PI11.final_document_facts.R01'
            and f.get('internal_edition') == '1.40' and f.get('closed_for_authoring') is True,
            'Explicit closed actual facts for edition1.40 required')
    require(datetime.fromisoformat(f['cut_utc'].replace('Z', '+00:00')).tzinfo is not None,
            'Timezone-aware actual cut required')
    require(nonempty(f.get('description')), 'Actual description required')
    front = f['front']
    for key in ('edition_summary', 'principal_summary', 'functional_summary', 'conservation_summary', 'resume_summary', 'coverage_summary'):
        require(nonempty(front.get(key)), 'Actual explained front field required: ' + key)
    require(set(front.get('control_table', {})) == CONTROL_LABELS
            and all(nonempty(v) for v in front['control_table'].values()),
            'Exactly four documentary-control values required')
    for key in ('manual_sections', 'compendium_sections'):
        sections = f.get(key)
        require(isinstance(sections, list) and 1 <= len(sections) <= 12, 'Need1..12 explained sections: ' + key)
        for section in sections:
            require(nonempty(section.get('heading')) and isinstance(section.get('paragraphs'), list)
                    and section['paragraphs'] and all(nonempty(v) for v in section['paragraphs']),
                    'Empty section/paragraph rejected before authoring')
            require(all(nonempty(v) for v in section.get('sources', [])), 'Empty source label')

    def unresolved(value):
        if isinstance(value, str):
            require('{{' not in value and not re.search(r'\bROOT:', value), 'Unresolved editorial placeholder')
        elif isinstance(value, dict):
            for v in value.values():
                unresolved(v)
        elif isinstance(value, list):
            for v in value:
                unresolved(v)

    unresolved({key: f[key] for key in ('front', 'manual_sections', 'compendium_sections')})
    selected = f['selected_life']
    require(selected.get('N') == 67 and type(selected.get('T')) is int and selected['T'] >= 947395
            and nonempty(selected.get('life_id')), 'Actual selected cut required; unchanged PI10 is allowed')
    require(re.fullmatch('[0-9a-f]{64}', selected.get('snapshot_sha256', '')) is not None,
            'Actual selected snapshot hash required')
    active = read(C / 'sistema/estado/ACTIVO.json')
    require(active['life_id'] == selected['life_id'] and active['tick'] == selected['T']
            and active['snapshot_sha256'] == selected['snapshot_sha256'], 'Facts must describe actual current ACTIVO')
    card = read(C / 'sistema/estado/vidas' / selected['life_id'] / 'VIDA.json')
    require(card['physical']['N'] == selected['N'] and card['physical']['tick'] == selected['T']
            and card['snapshot_sha256'] == selected['snapshot_sha256'], 'Facts/current stable life card differ')
    require(sha(C / 'sistema' / card['snapshot']) == selected['snapshot_sha256'], 'Snapshot locator/hash changed')
    require(isinstance(f.get('evidence'), list) and f['evidence'], 'Decisive evidence references required')
    for ref in f['evidence']:
        validate_ref(ref)
    validate_ref(f['scientific_report'])
    source_check(backup_required)


def append_paragraphs(paragraphs, style=None):
    """Render only new, explicitly supplied paragraphs; never rewrite history."""
    h = helper(ANCHOR)
    require(isinstance(paragraphs, list) and paragraphs and all(nonempty(t) for t in paragraphs),
            'Explicit nonempty paragraphs required')
    return b''.join(h.paragraph(t, style) for t in paragraphs)


def chapter(sections, number, title, anchor, bookmark_id, source_style='Source'):
    h = helper(anchor)
    chunks = [h.paragraph(title, 'Ttulo1', (bookmark_id, anchor), pagebreak=True)]
    for i, section in enumerate(sections, 1):
        chunks.append(h.paragraph(f'{number}.{i} ' + section['heading'], 'Ttulo2'))
        chunks.append(append_paragraphs(section['paragraphs']))
        if section.get('sources'):
            chunks.append(append_paragraphs(['Fuente: ' + s for s in section['sources']], source_style))
    return b''.join(chunks)


def edit_body(raw, f, manual):
    h = helper(ANCHOR if manual else COMP_ANCHOR)
    pre, parts, post, _ = h.body_parts(raw)
    infos = [h.info(x, pre) for x in parts]
    ids = [int(x) for x in re.findall(rb'<w:bookmarkStart\b[^>]*w:id="(\d+)"', raw)]
    new_id = max(ids, default=0) + 1
    if manual:
        first = next(i for i, (_, t, s) in enumerate(infos) if s == 'Ttulo1' and re.match(r'^1(?:\.\s|\s)', t))
        appendix = next(i for i, (_, t, s) in enumerate(infos) if s == 'Ttulo1' and t.startswith('Apéndice A'))
        require(any(s == 'Ttulo1' and t == '55 PI10 Consulta adaptativa y dos trazas nativas' for _, t, s in infos),
                'Complete prior chapter55 required')
        require(not any(s == 'Ttulo1' and t.startswith('56 ') for _, t, s in infos), 'PI11 already present; no duplicate authoring')
        old_history = b''.join(parts[first:])
        front = f['front']
        mapping = {8: 'DEE thinking 4.5.0 | DEE Cognitive 2.0 | Edición documental 1.40 | DCS11-MM-001',
                   9: front['edition_summary'], 13: front['principal_summary'], 14: front['functional_summary'],
                   15: front['conservation_summary'], 16: front['resume_summary'],
                   18: 'Funciones heredadas: evidencia histórica por vida y corte; continuidad actual en el capítulo 56',
                   26: front['coverage_summary']}
        require('Edición documental 1.39' in infos[8][1] and 'DCS11-MM-001' in infos[8][1], 'Exact old front anchor required')
        for index, text in mapping.items():
            require(index < first, 'Front edit escaped historical boundary')
            parts[index] = h.whole_paragraph(parts[index], pre, text)
        replacements = {}
        for row in infos[23][0].findall('.//{' + W + '}tr'):
            cells = row.findall('{' + W + '}tc')
            if len(cells) != 2:
                continue
            label = ''.join(t.text or '' for t in cells[0].iter('{' + W + '}t'))
            if label in CONTROL_LABELS:
                texts = list(cells[1].iter('{' + W + '}t'))
                require(len(texts) == 1, 'Split control cell; inspect before editing')
                replacements[texts[0].text or ''] = front['control_table'][label]
        require(len(replacements) == 4, 'Exactly four actual control-cell anchors required')
        parts[23], count = h.replace_texts(parts[23], replacements)
        require(count == 4, 'Control table anchor counts differ')
        toc = next(i for i, (_, t, _) in enumerate(infos[:first]) if t == '55 PI10 Consulta adaptativa y dos trazas nativas')
        additions = {toc + 1: h.paragraph(TITLE, 'TOCline', link=ANCHOR),
                     appendix: chapter(f['manual_sections'], '56', TITLE, ANCHOR, new_id)}
        out = pre + b''.join(additions.get(i, b'') + x for i, x in enumerate(parts)) + post
        require(b''.join(parts[first:]) == old_history, 'Old chapters1..55 or appendices changed')
        proof = {'old_history_XML_sha256': hashlib.sha256(old_history).hexdigest(),
                 'old_chapters1_to55_and_appendices_literal': True,
                 'front_modified_children': list(mapping) + [23], 'new_bookmark': ANCHOR}
    else:
        require(not any(s == 'Ttulo1' and t == COMP_TITLE for _, t, s in infos), 'PI11 compendium section already present')
        old = b''.join(parts)
        index = next((i for i, (node, _, _) in enumerate(infos) if node.tag == '{' + W + '}sectPr'), len(parts))
        toc = next(i for i, (_, t, s) in enumerate(infos) if s == 'Ttulo1' and t == 'Índice navegable')
        first_after_toc = next(i for i, (_, _, s) in enumerate(infos) if i > toc and s == 'Ttulo1')
        additions = {first_after_toc: h.paragraph(COMP_TITLE, None, link=COMP_ANCHOR),
                     index: chapter(f['compendium_sections'], 'PI11', COMP_TITLE, COMP_ANCHOR, new_id, 'Normal')}
        out = pre + b''.join(additions.get(i, b'') + x for i, x in enumerate(parts)) + additions.get(len(parts), b'') + post
        require(b''.join(parts) == old, 'Old compendium body changed')
        proof = {'old_body_XML_sha256': hashlib.sha256(old).hexdigest(), 'old_body_literal': True,
                 'index_entry_added': True, 'new_bookmark': COMP_ANCHOR}
    ET.fromstring(out)
    return out, proof


def build(source, target, f, manual):
    with zipfile.ZipFile(source) as zin:
        require(zin.testzip() is None, 'Source CRC failure')
        members = zin.infolist()
        old = {i.filename: zin.read(i) for i in members}
    document, proof = edit_body(old['word/document.xml'], f, manual)
    changes = {'word/document.xml': document}
    core = old['docProps/core.xml'].decode('utf8')
    values = {'cp:version': '1.40', 'cp:revision': '40', 'dcterms:modified': f['cut_utc'], 'dc:description': f['description']}
    if manual:
        values['dc:title'] = 'DEE Cognitive 2.0 Manual Maestro Edición 1.40 PI11'
    for tag, value in values.items():
        core, count = re.subn(r'(<'+re.escape(tag)+r'(?:\s[^>]*)?>).*?(</'+re.escape(tag)+r'>)',
                              lambda m: m[1] + escape(value) + m[2], core, flags=re.S)
        require(count == 1, 'Missing/duplicate core property ' + tag)
    changes['docProps/core.xml'] = core.encode('utf8')
    if 'word/settings.xml' in old:
        changes['word/settings.xml'] = helper(ANCHOR).settings_edit(old['word/settings.xml'])
    if manual:
        for name, data in old.items():
            if re.fullmatch(r'word/(?:header|footer)\d+\.xml', name):
                value = data.replace(b'1.39', b'1.40')
                if value != data:
                    changes[name] = value
    for data in changes.values():
        ET.fromstring(data)
    with zipfile.ZipFile(target, 'x') as zout:
        for member in members:
            zout.writestr(copy.copy(member), changes.get(member.filename, old[member.filename]))
    with zipfile.ZipFile(target) as z:
        require(z.testzip() is None, 'Output CRC failure')
        for name, value in old.items():
            if name.endswith('.xml'):
                ET.fromstring(z.read(name))
            if name not in changes:
                require(z.read(name) == value, 'Unapproved package member changed')
    return {'source': info(source), 'backup': info(BASE / source.name), 'output': info(target),
            'modified_members': list(changes), 'unchanged_members': [n for n in old if n not in changes],
            'structure_valid': True, 'visual_QA_not_implied': True, **proof}


def main(args):
    if args.preserve_base:
        print(json.dumps(preserve_base(), ensure_ascii=False))
        return
    if not (args.author or args.publish or args.check_facts):
        source_check(False)
        print(json.dumps({'mode': 'READ_ONLY_PLAN', 'edition': '1.40', 'sources': [info(s) for s in (MAN, COMP)],
                          'chapter': '56', 'facts_schema': 'DEE.PI11.final_document_facts.R01',
                          'staging': str(STAGE), 'Native_imported': False, 'authoring_executed': False}, ensure_ascii=False))
        return
    require(args.facts is not None, 'External closed actual facts JSON required')
    facts = read(args.facts)
    validate_facts(facts, backup_required=not args.check_facts)
    if args.check_facts:
        print(json.dumps({'facts_valid': True, 'edition': '1.40', 'read_only': True, 'Native_imported': False}))
        return
    if args.author:
        require(args.marker_confirmed and facts.get('actual_authoring_marker_registered_by_root') is True,
                'Root must execute the documents edit marker exactly once for these two outputs first')
        require(not STAGE.exists() and not STRUCTURE.exists(), 'Prior/partial staging preserved; no overwrite')
        STAGE.mkdir(parents=True)
        rows = [build(s, STAGE / s.name, facts, is_manual) for s, is_manual in ((MAN, True), (COMP, False))]
        put(STRUCTURE, {'schema': 'DEE.PI11.complete_DOCX_structural_staging.R01', 'facts': info(args.facts),
                        'scientific_report': info(facts['scientific_report']['path']), 'source_backup_manifest': info(BASE_MANIFEST),
                        'rows': rows, 'internal_edition': '1.40', 'published': False, 'Native_imported': False,
                        'visual_review_required': True})
        print(json.dumps({'staged': str(STAGE), 'documents': 2, 'old_history_preserved': True, 'published': False}))
        return
    proof = read(STRUCTURE)
    require(proof['facts']['sha256'] == sha(args.facts), 'Facts changed after authoring')
    require(args.visual_proof is not None, 'Actual visual review or explicit render limitation required')
    visual = read(args.visual_proof)
    require(visual.get('status') in ('rendered_and_reviewed', 'render_blocked_explicit_limitation') and visual.get('documents'),
            'Explicit actual visual-review status required')
    hashes = {r['sha256'] for r in visual['documents']}
    require({r['output']['sha256'] for r in proof['rows']} <= hashes, 'Visual proof must bind both staged DOCX hashes')
    if visual['status'] == 'render_blocked_explicit_limitation':
        require(args.accept_visual_limitation and nonempty(visual.get('limitation')), 'Explicit renderer limitation acknowledgement required')
    require(not PUBLICATION.exists(), 'Existing publication preserved')
    for row in proof['rows']:
        require(sha(row['source']['path']) == row['source']['sha256'] and sha(row['output']['path']) == row['output']['sha256'],
                'Document CAS changed before publication')
        require(not Path(row['source']['path'] + '.PI11.pending').exists(), 'Unresolved pending publication preserved')
    for row in proof['rows']:
        pending = Path(row['source']['path'] + '.PI11.pending')
        shutil.copyfile(row['output']['path'], pending)
        require(sha(pending) == row['output']['sha256'], 'Pending publication differs')
    put(D / 'PUBLICACION_PI11_EN_CURSO_R01.json', {'schema': 'DEE.PI11.two_document_publication_intent.R01',
        'facts': info(args.facts), 'structure': info(STRUCTURE), 'visual': info(args.visual_proof),
        'source_files': [r['source'] for r in proof['rows']], 'target_files': [r['output'] for r in proof['rows']]})
    for row in proof['rows']:
        source = Path(row['source']['path'])
        require(sha(source) == row['source']['sha256'], 'Concurrent source edit during publication')
        os.replace(Path(str(source) + '.PI11.pending'), source)
        require(sha(source) == row['output']['sha256'], 'Published identity differs')
    put(PUBLICATION, {'schema': 'DEE.PI11.actual_complete_DOCX_publication.R01', 'at': datetime.now(timezone.utc).isoformat(),
        'internal_edition': '1.40', 'facts': info(args.facts), 'source_backup_manifest': info(BASE_MANIFEST),
        'structural_proof': info(STRUCTURE), 'visual_proof': info(args.visual_proof), 'visual_status': visual['status'],
        'rows': [{**r, 'published': info(r['source']['path'])} for r in proof['rows']], 'Native_imported': False})
    print(json.dumps({'published': True, 'documents': 2, 'internal_edition': '1.40', 'manifest': str(PUBLICATION),
                      'visual_status': visual['status']}))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group()
    group.add_argument('--preserve-base', action='store_true')
    group.add_argument('--author', action='store_true')
    group.add_argument('--publish', action='store_true')
    group.add_argument('--check-facts', action='store_true')
    ap.add_argument('--facts', type=Path)
    ap.add_argument('--marker-confirmed', action='store_true')
    ap.add_argument('--visual-proof', type=Path)
    ap.add_argument('--accept-visual-limitation', action='store_true')
    main(ap.parse_args())
