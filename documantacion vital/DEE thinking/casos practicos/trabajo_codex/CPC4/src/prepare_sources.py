"""Directed passive extraction. No historical campaign is executed."""
import json
from pathlib import Path
import sys
import zipfile
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import sha, put, PARENT_SHA, KERNEL_SHA


def main():
    practical = ROOT.parents[1]
    product = practical.parent / '4.0'
    corpus = practical.parent.parent
    parent = practical / 'CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip'
    assert sha(parent) == PARENT_SHA
    extracted = []
    prefix = 'CPC3/experimentos/SEM01_SIGNIFICADO_ADQUIRIDO/'
    exact = ['INFORME.md', 'CAPACIDADES.json', 'configuraciones/EXPERIMENT_CONFIG.json',
             'resultados/CONFIRMATORY_SUMMARY.json', 'resultados/causal_memory02/SUMMARY.json',
             'resultados/reversal02_phase/SCOPE_AND_ADMISSION.json',
             'resultados/repertorio4/MECHANISM_REVIEW.json',
             'src/memory.py', 'src/habitat.py', 'src/participant.py', 'src/experiment.py',
             'src/repertoire4.py', 'src/reversal.py',
             'fuentes/textos/manual40.txt', 'fuentes/textos/maestro40.txt',
             'fuentes/CORE06/NATIVE_LEARNING.md', 'fuentes/CORE06/LEARNING_CAUSAL_MECHANISM.md',
             'fuentes/CORE07/LEARNING_TRANSFER.md', 'fuentes/CORE07/MATTER_REPROGRAMMING.md',
             'fuentes/CPC3/fuentes_pertinentes/documentos/ORGANIZACION_BASAL_PERSISTENTE_DOCUMENTO_MAESTRO_V2_1.txt',
             'fuentes/CPC3/fuentes_pertinentes/documentos/Procesamiento_Nativo_DEE_Libro_Manual_v1.txt',
             'fuentes/producto4/source/src/kernel_v27.cpp',
             'fuentes/producto4/source/src/cognitive.cpp',
             'fuentes/producto4/source/src/informative.cpp',
             'fuentes/producto4/source/src/organization_recipes.cpp',
             'fuentes/producto4/docs/COGNITIVE_API_4.md',
             'fuentes/producto4/docs/INFORMATIVE_API_4.md']
    with zipfile.ZipFile(parent) as z:
        for relative in exact:
            name = prefix + relative
            if name not in z.namelist():
                extracted.append({'member': name, 'status': 'NOT_PRESENT_IN_PARENT'})
                continue
            output = ROOT / 'referencias/fuentes' / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(z.read(name))
            extracted.append({'archive_sha256': PARENT_SHA, 'member': name,
                              'local': output.relative_to(ROOT).as_posix(), 'sha256': sha(output),
                              'classification': 'HISTORICAL_REFERENCE_NOT_NEW_CPC4_EXECUTION'})
    # One precise contemporary text, not the whole corpus or all books.
    physics = corpus / 'FISICA DEE Y PROCESAMIENTO NATIVO/DEE_V4_0_1.docx'
    with zipfile.ZipFile(physics) as z:
        element = ET.fromstring(z.read('word/document.xml'))
        text = '\n'.join(''.join(p.itertext()) for p in element.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
    output = ROOT / 'referencias/FISICA_DEE_4_0_1_TEXTO.txt'
    output.write_text(text, encoding='utf-8')
    sources = [{'path': str(parent), 'sha256': sha(parent)},
               {'path': str(product / 'DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip'),
                'sha256': sha(product / 'DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip')},
               {'path': str(physics), 'sha256': sha(physics),
                'text_file': output.relative_to(ROOT).as_posix(), 'text_sha256': sha(output)}]
    kernel = ROOT / 'referencias/fuentes/fuentes/producto4/source/src/kernel_v27.cpp'
    if kernel.exists():
        assert sha(kernel) == KERNEL_SHA
    put(ROOT / 'referencias/PROVENANCE.json', {'sources': sources, 'selected_members': extracted,
         'scope': 'Passive, directed source reading; no original file modified; no nested CPC3 ZIP'})
    print(json.dumps({'selected': len(extracted), 'missing': [x['member'] for x in extracted if 'status' in x]}))


if __name__ == '__main__':
    main()
