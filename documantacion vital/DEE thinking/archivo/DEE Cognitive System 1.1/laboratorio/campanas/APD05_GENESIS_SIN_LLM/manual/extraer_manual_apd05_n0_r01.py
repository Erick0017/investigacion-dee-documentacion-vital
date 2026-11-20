"""Extracción de lectura del Manual vigente, sin crear Word ni avanzar DEE."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def text(node):
    result = []
    for item in node.iter():
        if item.tag == W + 't':
            result.append(item.text or '')
        elif item.tag in (W + 'br', W + 'cr'):
            result.append('\n')
        elif item.tag == W + 'tab':
            result.append('\t')
    return ''.join(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manual', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source = args.manual.resolve(strict=True)
    raw = source.read_bytes()
    args.out.mkdir(parents=True, exist_ok=False)
    blocks = []
    with ZipFile(source) as archive:
        assert archive.testzip() is None
        tree = ET.fromstring(archive.read('word/document.xml'))
        parts = {name: hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist()}
        headfoot = [{'part': name, 'text': text(ET.fromstring(archive.read(name)))}
                    for name in archive.namelist() if re.fullmatch(r'word/(header|footer)\d+\.xml', name)]
        for index, node in enumerate(tree.find(W + 'body')):
            if node.tag == W + 'p':
                style = node.find(W + 'pPr/' + W + 'pStyle')
                blocks.append({'body_index': index, 'kind': 'paragraph',
                               'style': style.get(W + 'val') if style is not None else None,
                               'text': text(node)})
            elif node.tag == W + 'tbl':
                blocks.append({'body_index': index, 'kind': 'table',
                               'rows': [[text(cell) for cell in row.findall(W + 'tc')]
                                        for row in node.findall(W + 'tr')]})
    headings = [b for b in blocks if b.get('style') in ('Heading1', 'Heading2', 'Heading3')]
    report = {'schema': 'APD05.current_manual_read_only.N0.R01', 'manual': str(source),
              'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
              'logical_id': 'DCS11-MM-001', 'blocks': blocks, 'headings': headings,
              'headers_footers': headfoot, 'member_hashes': parts,
              'scope': 'OOXML body locators are not page numbers; no visual review or authoring.',
              'input_unchanged': source.read_bytes() == raw, 'new_native_ticks': 0}
    (args.out / 'INSPECCION_MANUAL_VIGENTE_N0.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    lines = ['LECTURA ESTRUCTURAL DEL MISMO MANUAL DCS11-MM-001',
             'SHA-256 ' + report['sha256'], 'Sin números de página ni validación visual.', '']
    for block in blocks:
        if block['kind'] == 'paragraph':
            lines.append(f"{block['body_index']} | {block.get('style')} | {block['text']}")
        else:
            lines.append(f"{block['body_index']} | TABLA")
            lines.extend(' | '.join(row) for row in block['rows'])
    (args.out / 'TEXTO_MANUAL_VIGENTE_N0.txt').write_text('\n'.join(lines) + '\n', encoding='utf8')
    print(json.dumps({key: report[key] for key in ('sha256', 'bytes', 'input_unchanged', 'new_native_ticks')},
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
