"""Minimal 1.17 to 1.18 edit of the SAME DCS11-MM-001 manual.

--inspect is read-only. --edit must follow the one successful artifact edit
marker performed by Root. No rendering, Word writing or edition happens at
import or inspection. Physics, engine sources and system code are never read.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
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
HERE = Path(__file__).resolve().parent
BASE_NAME = 'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_17_APD03_AUTONOMIA_DESARROLLO_SIN_VALIDACION_VISUAL.docx'
OUT_NAME = 'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_18_APD04_ECOSISTEMA_SIN_VALIDACION_VISUAL.docx'
BASE_SHA = '67e8e8cba4360a387fb47391e305a89988692c139c40e5b99a3a780b5e496848'
TITLE = '35 Ecosistema cognitivo atención y transferencia funcional'
SKILL = Path(r'C:\Users\Erik\.codex\plugins\cache\openai-primary-runtime\documents\26.1011.51657\skills\documents')
DEPENDENCIES = Path(r'C:\Users\Erik\.cache\codex-runtimes\codex-primary-runtime\dependencies')


def load_helpers():
    path = HERE/'funciones_ooxml_apd03_preservadas.py'
    spec = importlib.util.spec_from_file_location('manual_prior_ooxml_functions_only', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_new(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def c14n(node):
    return E.tostring(node, method='c14n')


def historical_body(tree, helpers, *,skip_new=False):
    values = []
    on = False
    skip = False
    for node in tree.find(W+'body'):
        if node.tag == W+'p' and helpers.style(node) == 'Heading1':
            if helpers.text(node).startswith('1. Qué es'):
                on = True
            if skip_new and helpers.text(node) == TITLE:
                skip = True
            elif skip and helpers.text(node).startswith('Apéndice A.'):
                skip = False
        if on and not skip:
            values.append(c14n(node))
    return values


def inspect(root):
    helpers = load_helpers()
    path = root/BASE_NAME
    if sha(path) != BASE_SHA:
        raise ValueError('The actual current edition is not the selected 1.17 baseline. Do not replace it silently.')
    infos, members = helpers.parts(path)
    tree = E.fromstring(members['word/document.xml'])
    paragraphs = list(tree.iter(W+'p'))
    heading_index = next(i for i,p in enumerate(paragraphs) if helpers.style(p)=='Heading1' and helpers.text(p).startswith('1. Qué es'))
    all_text = ''.join(helpers.text(p) for p in paragraphs)
    if 'DCS11-MM-001' not in all_text or TITLE in all_text:
        raise ValueError('Different document identity or existing chapter35; no duplicate edition.')
    return {'schema':'APD04.manual.baseline.inspection.N0.v1', 'document':str(path),
            'sha256':BASE_SHA,'bytes':path.stat().st_size,'zip_members':len(infos),
            'paragraphs':len(paragraphs),'front_paragraphs':[{'index':i,'style':helpers.style(p),'text':helpers.text(p)} for i,p in enumerate(paragraphs[:heading_index])],
            'headings':[helpers.text(p) for p in paragraphs if helpers.style(p)=='Heading1'],
            'historical_nodes':len(historical_body(tree,helpers)),
            'fields':helpers.fields(members),'geometry':[E.tostring(n).decode('utf8')for n in tree.iter(W+'sectPr')],
            'new_Word_files':0,'new_native_ticks':0,'author_operation_not_marked_or_executed':True}


def render_once(out, report):
    # Only the packaged renderer and bundled dependency PATH are permitted.
    # Never search for or invoke a user's desktop LibreOffice as a fallback.
    expected_python = (DEPENDENCIES/'python/python.exe').resolve()
    if Path(sys.executable).resolve() != expected_python:
        raise ValueError('Run document work with the bundled workspace Python.')
    env = dict(os.environ)
    env['PATH'] = os.pathsep.join(str(path) for path in (
        expected_python.parent, DEPENDENCIES/'bin/override', DEPENDENCIES/'bin/fallback', DEPENDENCIES/'native/poppler/bin'))
    env['PYTHONIOENCODING'] = 'utf-8'
    work = Path(tempfile.mkdtemp(prefix='dee_apd04_docx_qa_'))
    copy = work/'manual.docx'
    shutil.copyfile(out, copy)
    if sha(copy) != sha(out):
        raise ValueError('Short-path render input is not byte-identical to the final Word.')
    target = work/'render'
    command = [str(expected_python),str(SKILL/'render_docx.py'),str(copy),'--output_dir',str(target),'--emit_pdf','--verbose']
    attempt = {'command':command,'input_copy':str(copy),'input_sha256':sha(copy),
               'bundled_dependency_PATH':env['PATH'],'desktop_LibreOffice_forbidden':True,'single_attempt':True}
    try:
        result = subprocess.run(command,cwd=Path(tempfile.gettempdir()),env=env,
                     capture_output=True,text=True,encoding='utf8',errors='replace',timeout=50)
        attempt.update(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
    except subprocess.TimeoutExpired as error:
        attempt.update(timeout_seconds=50,stdout=str(error.stdout),stderr=str(error.stderr))
    except OSError as error:
        attempt.update(error_type=type(error).__name__,error=str(error))
    attempt['pages'] = [str(path)for path in sorted(target.glob('page-*.png'))]
    attempt['page_count'] = len(attempt['pages'])
    report['render'] = attempt
    report['visual_validation'] = 'PAGES_REQUIRE_FULL_REVIEW' if attempt['pages'] else 'NOT_AVAILABLE_RENDER_FAILED_ZERO_PAGES'


def edit(root, results_path, report_path, try_render):
    data = json.loads(results_path.read_text(encoding='utf8'))
    if data.get('status') != 'FINAL_RESULTS_APPROVED_FOR_MANUAL' or data.get('logical_document_id') != 'DCS11-MM-001':
        raise ValueError('Root must approve the closed scientific prose for this same logical manual.')
    if data.get('baseline_sha256') != BASE_SHA or data.get('previous_edition') != '1.17' or data.get('new_edition') != '1.18':
        raise ValueError('Explicit edition and baseline identities are mandatory.')
    front = data['front']
    if set(front) != {'cover_cut','release','base','edition_status','reviewed'}:
        raise ValueError('Five explicit closed-cut front statements are required.')
    if not isinstance(data.get('chapter'),list) or len(data['chapter']) < 8:
        raise ValueError('The new chapter needs substantive approved content, not empty sections.')
    approved = json.dumps({'front':front,'chapter':data['chapter']},ensure_ascii=False)
    if '{{' in approved or '}}' in approved or '__declspec' in approved or '#include' in approved:
        raise ValueError('Unresolved placeholders or kernel code must not enter the Manual.')
    helpers = load_helpers()
    src = root/BASE_NAME
    out = root/OUT_NAME
    archive = root/'documentos/historico_manuales'/BASE_NAME
    if sha(src) != BASE_SHA or out.exists() or archive.exists() or report_path.exists():
        raise FileExistsError('Baseline/edition/archive/report conflict preserved; no overwrite or reauthoring.')
    if not archive.resolve().is_relative_to(root.resolve()) or not archive.parent.is_dir():
        raise ValueError('Historical manual destination must exist inside the same system root.')
    infos, base = helpers.parts(src)
    members = dict(base)
    tree = E.fromstring(base['word/document.xml'])
    body = tree.find(W+'body')
    paragraphs = list(tree.iter(W+'p'))
    first_chapter = next(i for i,p in enumerate(paragraphs) if helpers.style(p)=='Heading1' and helpers.text(p).startswith('1. Qué es'))
    original_history = historical_body(tree,helpers)
    expected_prefixes = {
        'cover_cut':'Edición documental 1.17Corte APD03:',
        'release':'26/10/2026 UTC; APD03_MAIN T604825 continúa',
        'base':'Edición 1.16 conservada por hash',
        'edition_status':'Word 1.17 actualizado en el mismo documento lógico.',
        'reviewed':'Este mismo Manual Maestro conserva sus capítulos científicos 20 a 33 sin reescribir el pasado.'}
    seen = {name:0 for name in front}
    changes = []
    for paragraph in paragraphs[:first_chapter]:
        old = helpers.text(paragraph)
        matching = [key for key,prefix in expected_prefixes.items() if old.startswith(prefix)]
        if matching:
            if len(matching) != 1:
                raise ValueError('Ambiguous front paragraph.')
            key = matching[0]
            seen[key] += 1
            new = front[key]
        else:
            new = old.replace('Edición documental 1.17','Edición documental 1.18')
        if old != new:
            helpers.put(paragraph,new)
            changes.append({'old':old,'new':new,'scope':'front_only'})
    if set(seen.values()) != {1}:
        raise ValueError('Every approved front statement must target exactly one existing paragraph: '+str(seen))
    front_text = ''.join(helpers.text(p)for p in list(tree.iter(W+'p'))[:first_chapter])
    if 'Edición documental 1.17' in front_text or 'DCS11-MM-001' not in front_text:
        raise ValueError('Stale edition or changed document identity on the current front.')
    toc = next(p for p in body if p.tag==W+'p' and helpers.style(p)=='TOCline' and helpers.text(p).startswith('Apéndice A.'))
    body.insert(list(body).index(toc),helpers.para('TOCline',TITLE))
    appendix = next(p for p in body if p.tag==W+'p' and helpers.style(p)=='Heading1' and helpers.text(p).startswith('Apéndice A.'))
    chapter = [helpers.para('Heading1',TITLE)]
    for item in data['chapter']:
        if item.get('type') == 'table':
            chapter.append(helpers.table(item['rows']))
        else:
            if item['style'] not in ('Heading2','Heading3','Normal','Code','Source','Small') or not item['text'].strip():
                raise ValueError('Use the existing styles and substantive approved text.')
            chapter.append(helpers.para(item['style'],item['text']))
    at = list(body).index(appendix)
    for offset,node in enumerate(chapter):
        body.insert(at+offset,node)
    members['word/document.xml'] = E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
    for name in ('word/header1.xml','word/footer1.xml'):
        part = E.fromstring(members[name])
        occurrences = 0
        for node in part.iter(W+'t'):
            if node.text and ('DOCUMENTAL 1.17' in node.text or 'documental 1.17' in node.text):
                node.text = node.text.replace('DOCUMENTAL 1.17','DOCUMENTAL 1.18').replace('documental 1.17','documental 1.18')
                occurrences += 1
        if occurrences != 1:
            raise ValueError('Unexpected edition header/footer count: '+name)
        members[name] = E.tostring(part,xml_declaration=True,encoding='UTF-8',standalone=True)
    core = E.fromstring(members['docProps/core.xml'])
    for node in core:
        if node.tag.endswith('}title'):
            node.text = 'DEE Cognitive System 1.1 Manual Maestro Edicion 1.18 Ecosistema cognitivo'
        elif node.tag.endswith('}subject'):
            node.text = 'APD04 organizacion situada atencion transferencia composicion y continuidad con alcance experimental declarado'
        elif node.tag.endswith('}version'):
            node.text = '1.18 documental / software1.1.0'
        elif node.tag.endswith('}revision'):
            node.text = str(int(node.text or '0')+1)
        elif node.tag.endswith('}modified'):
            node.text = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    members['docProps/core.xml'] = E.tostring(core,xml_declaration=True,encoding='UTF-8',standalone=True)
    with ZipFile(out,'w') as archive_writer:
        for info in infos:
            archive_writer.writestr(info,members[info.filename])
    final_infos, final = helpers.parts(out)
    final_tree = E.fromstring(final['word/document.xml'])
    changed = [name for name in base if base[name] != final[name]]
    if set(changed) != {'word/document.xml','word/header1.xml','word/footer1.xml','docProps/core.xml'}:
        raise ValueError('Unexpected changed OOXML parts: '+str(changed))
    assert list(base) == list(final)
    assert [info.filename for info in infos] == [info.filename for info in final_infos]
    assert helpers.fields(base) == helpers.fields(final)
    assert [c14n(n)for n in E.fromstring(base['word/document.xml']).iter(W+'sectPr')] == [c14n(n)for n in final_tree.iter(W+'sectPr')]
    assert original_history == historical_body(final_tree,helpers,skip_new=True)
    assert len(original_history) > 100
    headings = [helpers.text(p)for p in final_tree.iter(W+'p')if helpers.style(p)=='Heading1']
    assert headings.count(TITLE) == 1
    assert headings.index(TITLE)+1 == next(i for i,h in enumerate(headings)if h.startswith('Apéndice A.'))
    assert sum(helpers.style(p)=='TOCline' and helpers.text(p)==TITLE for p in final_tree.iter(W+'p')) == 1
    assert 'DCS11-MM-001' in ''.join(helpers.text(p)for p in final_tree.iter(W+'p'))
    assert E.fromstring(final['word/settings.xml']).find(W+'updateFields').get(W+'val') == 'true'
    assert sha(src) == BASE_SHA
    shutil.move(str(src),str(archive))
    assert sha(archive) == BASE_SHA
    assert list(root.glob('DEE_Cognitive_System_1_1_Manual_Maestro*.docx')) == [out]
    report = {'schema':'APD04.same_manual.edition.1_18.v1','logical_document_id':'DCS11-MM-001',
              'document':str(out),'sha256':sha(out),'bytes':out.stat().st_size,
              'baseline':str(archive),'baseline_sha256':BASE_SHA,'changed_parts':changed,
              'unchanged_member_payloads':len(base)-len(changed),'chapter':TITLE,
              'all_previous_chapters_and_appendices_XML_preserved':True,'historical_nodes_preserved':len(original_history),
              'geometry_styles_relationships_and_field_codes_preserved':True,
              'unique_current_manual':True,'front_changes':changes,'native_ticks':0,
              'approved_results':str(results_path),'approved_results_sha256':sha(results_path),
              'visual_validation':'NOT_ATTEMPTED','visual_reviewed_pages':0}
    if try_render:
        render_once(out,report)
    json_new(report_path,report)
    print(json.dumps({key:report[key]for key in ('document','sha256','bytes','visual_validation','visual_reviewed_pages','native_ticks')},ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--inspect',action='store_true')
    mode.add_argument('--edit',action='store_true')
    p.add_argument('--results',type=Path)
    p.add_argument('--report',type=Path,required=True)
    p.add_argument('--try-render',action='store_true')
    p.add_argument('--root-go',choices=('APD04_EDIT_EXISTING_MANUAL_APPROVED',))
    a = p.parse_args()
    root = a.root.resolve(strict=True)
    if a.inspect:
        result = inspect(root)
        json_new(a.report,result)
        print(json.dumps({key:value for key,value in result.items()if key not in('front_paragraphs','fields','geometry','headings')},ensure_ascii=False))
        return
    if not a.results or a.root_go != 'APD04_EDIT_EXISTING_MANUAL_APPROVED':
        p.error('Root must approve the results and mark the one edit operation immediately before this authoring command.')
    edit(root,a.results.resolve(strict=True),a.report.resolve(),a.try_render)


if __name__ == '__main__':
    main()
