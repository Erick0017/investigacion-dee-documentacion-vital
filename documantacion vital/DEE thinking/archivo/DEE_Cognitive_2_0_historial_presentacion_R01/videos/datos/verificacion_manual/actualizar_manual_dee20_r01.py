"""N0 preparation and scoped edit of the same DCS11-MM-001 manual.

Inspect never creates a DOCX. Root alone runs --edit after approving the actual
demonstration results and performing the required one-time artifact marker.
Only the destination copy is changed; the original 1.1 system is read-only.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZipFile
from lxml import etree as E

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
BASE_NAME = 'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_19_APD05_GENESIS_SIN_VALIDACION_VISUAL.docx'
BASE_SHA = 'e7cfea845e3e7aa790f3a4b44f392661a35d3f2ccde70eab2d0ce7aeabc7ea48'
OUT_NAME = 'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_20.docx'
TITLE = '37 DEE Cognitive 2 0 uso diario y demostración continua'
SKILL = Path(r'C:\Users\Erik\.codex\plugins\cache\openai-primary-runtime\documents\26.1017.22136\skills\documents')
DEPS = Path(r'C:\Users\Erik\.cache\codex-runtimes\codex-primary-runtime\dependencies')


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def text(node):
    return ''.join(part.text or '' for part in node.iter(W+'t'))


def style(node):
    value = node.find(W+'pPr/'+W+'pStyle')
    return value.get(W+'val', '') if value is not None else ''


def put(node, value):
    if list(node.iter(W+'instrText')):
        raise ValueError('A field paragraph cannot be flattened.')
    run = node.find(W+'r')
    properties = deepcopy(run.find(W+'rPr')) if run is not None and run.find(W+'rPr') is not None else None
    for child in list(node):
        if child.tag != W+'pPr':
            node.remove(child)
    run = E.SubElement(node, W+'r')
    if properties is not None:
        run.append(properties)
    if style(node) in ('Title', 'Subtitle'):
        if properties is None:
            properties = E.SubElement(run, W+'rPr')
        color = properties.find(W+'color')
        if color is None:
            color = E.SubElement(properties, W+'color')
        color.attrib.clear()
        color.set(W+'val', '000000')
    for i, line in enumerate(value.split('\n')):
        if i:
            E.SubElement(run, W+'br')
        E.SubElement(run, W+'t', attrib={XMLSPACE:'preserve'}).text = line


def paragraph(role, value):
    node = E.Element(W+'p')
    E.SubElement(E.SubElement(node, W+'pPr'), W+'pStyle').set(W+'val', role)
    put(node, value)
    if role in ('Heading1', 'Heading2', 'Heading3'):
        run = node.find(W+'r')
        properties = run.find(W+'rPr')
        if properties is None:
            properties = E.Element(W+'rPr')
            run.insert(0, properties)
        E.SubElement(properties, W+'color').set(W+'val', '000000')
    return node


def cue_table(rows):
    if len(rows) < 2 or any(len(row) != 3 for row in rows):
        raise ValueError('Cue table requires three columns and actual events.')
    widths = [1100, 2700, 5867]
    node = E.Element(W+'tbl')
    properties = E.SubElement(node, W+'tblPr')
    E.SubElement(properties, W+'tblW', attrib={W+'w':'9667', W+'type':'dxa'})
    E.SubElement(properties, W+'tblLayout').set(W+'type', 'fixed')
    borders = E.SubElement(properties, W+'tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        E.SubElement(borders, W+edge, attrib={W+'val':'single', W+'sz':'4', W+'color':'D9D9D9'})
    margins = E.SubElement(properties, W+'tblCellMar')
    for edge in ('top', 'left', 'bottom', 'right'):
        E.SubElement(margins, W+edge, attrib={W+'w':'110', W+'type':'dxa'})
    grid = E.SubElement(node, W+'tblGrid')
    for width in widths:
        E.SubElement(grid, W+'gridCol').set(W+'w', str(width))
    for i, row in enumerate(rows):
        tr = E.SubElement(node, W+'tr')
        if i == 0:
            E.SubElement(E.SubElement(tr, W+'trPr'), W+'tblHeader')
        for j, value in enumerate(row):
            cell = E.SubElement(tr, W+'tc')
            props = E.SubElement(cell, W+'tcPr')
            E.SubElement(props, W+'tcW', attrib={W+'w':str(widths[j]), W+'type':'dxa'})
            E.SubElement(props, W+'shd', attrib={W+'val':'clear', W+'fill':'16324F' if i == 0 else ('F1F5F9' if i % 2 == 0 else 'FFFFFF')})
            E.SubElement(props, W+'vAlign').set(W+'val', 'center')
            par = paragraph('Normal', str(value))
            cell.append(par)
            ppr = par.find(W+'pPr')
            E.SubElement(ppr, W+'spacing', attrib={W+'before':'40', W+'after':'60', W+'line':'264', W+'lineRule':'auto'})
            if i == 0 or j == 0:
                E.SubElement(ppr, W+'jc').set(W+'val', 'center')
            run = par.find(W+'r')
            rpr = E.Element(W+'rPr')
            run.insert(0, rpr)
            if i == 0:
                E.SubElement(rpr, W+'b')
            E.SubElement(rpr, W+'color').set(W+'val', 'FFFFFF' if i == 0 else '000000')
            E.SubElement(rpr, W+'sz').set(W+'val', '22')
    return node


def parts(path):
    with ZipFile(path) as package:
        if package.testzip() is not None:
            raise ValueError('Unreadable DOCX member.')
        return package.infolist(), {name:package.read(name) for name in package.namelist()}


def c14n(node):
    return E.tostring(node, method='c14n')


def fields(members):
    return {name:[node.text for node in E.fromstring(payload).iter(W+'instrText')]
            for name, payload in members.items()
            if name.endswith('.xml') and name.startswith(('word/document', 'word/header', 'word/footer'))}


def history(tree, skip_new=False):
    result = []
    active = False
    skip = False
    for node in tree.find(W+'body'):
        if node.tag == W+'p' and style(node) == 'Heading1':
            if text(node).startswith('1. Qué es'):
                active = True
            if skip_new and text(node) == TITLE:
                skip = True
            elif skip and text(node).startswith('Apéndice A.'):
                skip = False
        if active and not skip:
            result.append(c14n(node))
    return result


def write_json_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def inspect(root, report_path):
    src = root/BASE_NAME
    if sha(src) != BASE_SHA:
        raise ValueError('Unexpected edition 1.19 baseline; no silent edition fallback.')
    infos, members = parts(src)
    tree = E.fromstring(members['word/document.xml'])
    paragraphs = list(tree.iter(W+'p'))
    first = next(i for i, node in enumerate(paragraphs) if style(node) == 'Heading1' and text(node).startswith('1. Qué es'))
    chapter = next(i for i, node in enumerate(paragraphs) if style(node) == 'Heading1' and text(node).startswith('36 '))
    end = next(i for i in range(chapter+1, len(paragraphs)) if style(paragraphs[i]) == 'Heading1')
    result = {'schema':'DEE20.manual.inspection.N0.v1', 'document':str(src), 'sha256':BASE_SHA,
        'bytes':src.stat().st_size, 'logical_document_id':'DCS11-MM-001', 'edition':'1.19',
        'members':[{ 'name': info.filename, 'bytes':info.file_size,
                    'sha256':hashlib.sha256(members[info.filename]).hexdigest()} for info in infos],
        'front':[{'index':i, 'style':style(node), 'text':text(node)} for i,node in enumerate(paragraphs[:first])],
        'chapter36':[{'index':i, 'style':style(paragraphs[i]), 'text':text(paragraphs[i])} for i in range(chapter,end)],
        'history_nodes':len(history(tree)), 'fields':fields(members),
        'geometry':[E.tostring(node).decode('utf-8') for node in tree.iter(W+'sectPr')],
        'new_DOCX':0, 'new_ticks':0}
    write_json_new(report_path, result)
    print(json.dumps({key:result[key] for key in ('document','sha256','bytes','history_nodes','new_DOCX','new_ticks')}, ensure_ascii=False))


def render_once(path, report):
    # The dependency loader did not expose a bundled LibreOffice executable.
    # Only the packaged renderer and authoritative dependency PATH are used.
    env = dict(os.environ)
    env['PATH'] = os.pathsep.join(map(str, [DEPS/'python', DEPS/'bin/override', DEPS/'bin/fallback', DEPS/'native/poppler/bin']))
    env['PYTHONIOENCODING'] = 'utf-8'
    work = Path(tempfile.mkdtemp(prefix='dee20_manual_qa_'))
    render_input = work/'manual.docx'
    shutil.copyfile(path, render_input)
    if sha(render_input) != sha(path):
        raise ValueError('Render input differs from actual final Word.')
    out = work/'render'
    command = [str(DEPS/'python/python.exe'), str(SKILL/'render_docx.py'), str(render_input), '--output_dir', str(out), '--emit_pdf', '--verbose']
    attempt = {'command':command, 'input_sha256':sha(render_input), 'desktop_LibreOffice_forbidden':True,
               'single_attempt':True, 'PATH':env['PATH']}
    try:
        process = subprocess.run(command, env=env, cwd=work, capture_output=True, text=True,
                                 encoding='utf-8', errors='replace', timeout=50)
        attempt.update(returncode=process.returncode, stdout=process.stdout, stderr=process.stderr)
    except subprocess.TimeoutExpired as error:
        attempt.update(timeout_seconds=50, stdout=str(error.stdout), stderr=str(error.stderr))
    attempt['pages'] = [str(item) for item in sorted(out.glob('page-*.png'))]
    attempt['page_count'] = len(attempt['pages'])
    report['render'] = attempt
    report['visual_validation'] = 'PAGES_AWAIT_REVIEW' if attempt['pages'] else 'PACKAGED_RENDER_FAILED_ZERO_PAGES'


def edit(root, approved_path, report_path, try_render):
    data = json.loads(approved_path.read_text(encoding='utf-8'))
    if (data.get('status') != 'DEE20_ACTUAL_RESULTS_APPROVED_FOR_MANUAL' or
        data.get('logical_document_id') != 'DCS11-MM-001' or data.get('baseline_sha256') != BASE_SHA or
        data.get('previous_edition') != '1.19' or data.get('new_edition') != '1.20'):
        raise ValueError('Root approval must identify actual results, document and editions.')
    if root.name != 'DEE Cognitive 2.0' or not root.is_dir():
        raise ValueError('Only the new DEE Cognitive 2.0 destination may be edited.')
    src, out = root/BASE_NAME, root/OUT_NAME
    archive = root/'documentos/historico_manuales'/BASE_NAME
    if not src.is_file() or sha(src) != BASE_SHA or out.exists() or archive.exists() or report_path.exists():
        raise FileExistsError('Preserve baseline, existing output or existing report; no overwrite.')
    def strings(value):
        if isinstance(value,str):
            yield value
        elif isinstance(value,dict):
            for nested in value.values():
                yield from strings(nested)
        elif isinstance(value,list):
            for nested in value:
                yield from strings(nested)
    if any(forbidden in value for value in strings(data) for forbidden in ('{{', '}}', '__declspec', '#include')):
        raise ValueError('Unresolved placeholders or kernel code are not allowed in this manual.')
    replacements = data['front_replacements']
    if len(replacements) < 9:
        raise ValueError('Explicit current title, edition, scope and evidence front replacements are required.')
    chapter = data['chapter']
    if len(chapter) < 8:
        raise ValueError('Substantive operating instructions and actual findings are required.')
    videos = data['videos']
    if abs(float(videos['original_duration_seconds']) - float(videos['explained_duration_seconds'])) > 0.001:
        raise ValueError('Do not state equal duration unless exact final timings agree.')
    cues = data['video_cues']
    if len(cues) < 6 or any(float(cue['at_seconds']) < 0 or float(cue['at_seconds']) > float(videos['original_duration_seconds']) for cue in cues):
        raise ValueError('At least six actual timestamped coverage events must be within the video.')
    if [float(cue['at_seconds']) for cue in cues] != sorted(float(cue['at_seconds']) for cue in cues):
        raise ValueError('The actual cue sequence must not reorder video events.')
    infos, base = parts(src)
    members = dict(base)
    tree = E.fromstring(base['word/document.xml'])
    body = tree.find(W+'body')
    all_paragraphs = list(tree.iter(W+'p'))
    first = next(i for i,node in enumerate(all_paragraphs) if style(node)=='Heading1' and text(node).startswith('1. Qué es'))
    old_history = history(tree)
    occurrences = {key:0 for key in replacements}
    changes = []
    for node in all_paragraphs[:first]:
        old = text(node)
        if old in replacements:
            new = replacements[old]
            if not new.strip():
                raise ValueError('A current front slot cannot be emptied.')
            put(node, new)
            occurrences[old] += 1
            changes.append({'old':old, 'new':new})
    if any(count != 1 for count in occurrences.values()):
        raise ValueError('Every approved front location must match exactly once: '+str(occurrences))
    toc = next(node for node in body if node.tag==W+'p' and style(node)=='TOCline' and text(node).startswith('Apéndice A.'))
    body.insert(list(body).index(toc), paragraph('TOCline',TITLE))
    appendix = next(node for node in body if node.tag==W+'p' and style(node)=='Heading1' and text(node).startswith('Apéndice A.'))
    nodes = [paragraph('Heading1',TITLE)]
    for item in chapter:
        if item['style'] not in ('Heading2','Heading3','Normal','Code','Source','Small') or not item['text'].strip():
            raise ValueError('Invalid style or empty approved chapter element.')
        nodes.append(paragraph(item['style'],item['text']))
    nodes.append(paragraph('Heading2','37 7 Recorrido y tiempos de los videos'))
    nodes.append(paragraph('Normal',data['video_coverage_intro']))
    rows = [['Tiempo','Uso mostrado','Resultado y atribución']]
    for cue in cues:
        seconds = int(float(cue['at_seconds']))
        timestamp = f'{seconds//3600:02d}:{seconds%3600//60:02d}:{seconds%60:02d}'
        rows.append([timestamp,cue['operation'],cue['result']])
    nodes.append(cue_table(rows))
    nodes.append(paragraph('Source',data['evidence_locator']))
    insert_at = list(body).index(appendix)
    for offset,node in enumerate(nodes):
        body.insert(insert_at+offset,node)
    members['word/document.xml'] = E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
    for name in ('word/header1.xml','word/footer1.xml'):
        part = E.fromstring(members[name])
        changed = 0
        for node in part.iter(W+'t'):
            if node.text and ('1.19' in node.text or 'DEE COGNITIVE SYSTEM 1.1' in node.text):
                node.text = node.text.replace('DEE COGNITIVE SYSTEM 1.1','DEE COGNITIVE 2.0').replace('1.19','1.20')
                changed += 1
        if changed != 1:
            raise ValueError('Unexpected header or footer edition count.')
        members[name] = E.tostring(part,xml_declaration=True,encoding='UTF-8',standalone=True)
    core = E.fromstring(members['docProps/core.xml'])
    for node in core:
        if node.tag.endswith('}title'):
            node.text = 'DEE Cognitive 2.0 Manual Maestro Edicion 1.20'
        elif node.tag.endswith('}subject'):
            node.text = 'Uso local continuidad y demostracion completa sin LLM'
        elif node.tag.endswith('}version'):
            node.text = '1.20 documental / presentacion 2.0 / thinking 4.5.0 / kernel v27'
        elif node.tag.endswith('}revision'):
            node.text = str(int(node.text or '0')+1)
        elif node.tag.endswith('}modified'):
            node.text = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    members['docProps/core.xml'] = E.tostring(core,xml_declaration=True,encoding='UTF-8',standalone=True)
    with ZipFile(out,'x') as package:
        for info in infos:
            package.writestr(info,members[info.filename])
    _, final = parts(out)
    final_tree = E.fromstring(final['word/document.xml'])
    changed_parts = [name for name in base if base[name] != final[name]]
    if set(changed_parts) != {'word/document.xml','word/header1.xml','word/footer1.xml','docProps/core.xml'}:
        raise ValueError('Unexpected package edits: '+str(changed_parts))
    if list(base) != list(final) or fields(base) != fields(final):
        raise ValueError('Package members or field codes changed.')
    if old_history != history(final_tree,skip_new=True):
        raise ValueError('Historical chapters 1 through 36 or appendices changed.')
    if [c14n(n) for n in E.fromstring(base['word/document.xml']).iter(W+'sectPr')] != [c14n(n) for n in final_tree.iter(W+'sectPr')]:
        raise ValueError('Section geometry changed.')
    if E.fromstring(final['word/settings.xml']).find(W+'updateFields').get(W+'val') != 'true':
        raise ValueError('Field refresh flag must remain enabled.')
    final_front = ''.join(text(node) for node in list(final_tree.iter(W+'p'))[:first])
    if 'DCS11-MM-001' not in final_front or 'Edición documental 1.19' in final_front or 'DEE Cognitive 2.0' not in final_front:
        raise ValueError('Stale current title/edition or lost document identity.')
    if sha(src) != BASE_SHA:
        raise ValueError('The local baseline changed during authoring.')
    archive.parent.mkdir(parents=True,exist_ok=True)
    if not archive.resolve().is_relative_to(root.resolve()):
        raise ValueError('Archive target is outside the explicitly selected destination.')
    shutil.move(str(src),str(archive))
    if sha(archive) != BASE_SHA:
        raise ValueError('Archived 1.19 copy hash mismatch.')
    report = {'schema':'DEE20.same_manual.edition_1_20.v1','logical_document_id':'DCS11-MM-001',
        'document':str(out),'sha256':sha(out),'bytes':out.stat().st_size,
        'previous_copy':str(archive),'previous_sha256':BASE_SHA,
        'source_original_untouched':True,'changed_parts':changed_parts,'untouched_parts':len(base)-len(changed_parts),
        'historical_nodes_preserved':len(old_history),'historical_chapters_1_36_and_appendices_preserved':True,
        'geometry_styles_relationships_and_fields_preserved':True,'native_ticks':0,
        'approved_results':str(approved_path),'approved_results_sha256':sha(approved_path),
        'front_changes':changes,'video_cues':cues,'video_duration_seconds':videos['original_duration_seconds'],
        'visual_validation':'NOT_ATTEMPTED','visually_reviewed_pages':0}
    if try_render:
        render_once(out,report)
    write_json_new(report_path,report)
    print(json.dumps({key:report[key] for key in ('document','sha256','bytes','native_ticks','visual_validation')},ensure_ascii=False))


def main():
    expected_python = (DEPS/'python/python.exe').resolve()
    if Path(sys.executable).resolve() != expected_python:
        raise ValueError('Only the authoritative bundled workspace Python is allowed for this document helper.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--inspect',action='store_true')
    mode.add_argument('--edit',action='store_true')
    parser.add_argument('--approved',type=Path)
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--try-render',action='store_true')
    parser.add_argument('--root-go',choices=('DEE20_EDIT_SAME_MANUAL_APPROVED',))
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    if args.inspect:
        inspect(root,args.report.resolve())
        return
    if not args.approved or args.root_go != 'DEE20_EDIT_SAME_MANUAL_APPROVED':
        parser.error('Root approval plus the one successful artifact edit marker are required before this command.')
    edit(root,args.approved.resolve(strict=True),args.report.resolve(),args.try_render)


if __name__ == '__main__':
    main()
