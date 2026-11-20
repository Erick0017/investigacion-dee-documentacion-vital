"""Read-only directed reference extraction; never executes a historical runner."""
from pathlib import Path
import hashlib,json,re,zipfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
def main():
    product=ROOT.parents[2]/'4.0';out=ROOT/'genealogia/PRODUCT4';out.mkdir(exist_ok=True)
    reports=[]
    paths=[product/name for name in ('DEE_thinking_4_0_0_Maestro_Arquitectura_Reconstruccion.docx','DEE_thinking_4_0_0_Libro_Blanco_y_Manual_Tecnico.docx')]
    paths += [ROOT.parents[3]/'FISICA DEE Y PROCESAMIENTO NATIVO'/name for name in ('DEE_V4_0_1.docx','Procesamiento_Nativo_DEE_Libro_Manual_v1.docx')]
    for path in paths:
        name=path.name
        with zipfile.ZipFile(path) as z:
            xml=z.read('word/document.xml');tree=ET.fromstring(xml)
            paragraphs=[''.join(p.itertext()) for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')]
            matches=[i for i,t in enumerate(paragraphs) if re.search(r'(snapshot|MAIN|ResearchStateEdit|diagnostic_fork|lectura renovada|memoria relativa|observador|equivalencia funcional|revis.{0,5}pol.tica|F0[458])',t,re.I)]
            selected=sorted({j for i in matches for j in range(max(0,i-1),min(len(paragraphs),i+2))})
            reports.append({'file':name,'sha256':sha(path),'document_xml_sha256':hashlib.sha256(xml).hexdigest(),
                'paragraph_count':len(paragraphs),'selected_paragraphs':[{'index':i,'text':paragraphs[i]} for i in selected],
                'selection':'Directed contract/session/persistence/observation sections; text only, no layout audit or document changes',
                'embedded_capsules_present':[n for n in z.namelist() if n.startswith('dee_payload/')]})
    path=product/'DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip'
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if n in ('DEE_thinking_4_0_0/PRODUCT_CONTRACT.json','DEE_thinking_4_0_0/docs/API_AND_SCOPE.md','DEE_thinking_4_0_0/docs/BUILD_AND_MIGRATION.md'):
                data=z.read(n);dst=out/Path(n).name
                if dst.exists() and dst.read_bytes()!=data:raise ValueError('Will not overwrite a different reference')
                dst.write_bytes(data)
                reports.append({'archive':path.name,'archive_sha256':sha(path),'member':n,'copy':str(dst.relative_to(ROOT)),
                    'sha256':hashlib.sha256(data).hexdigest(),'size':len(data)})
    target=ROOT/'genealogia/DIRECTED_PRODUCT_READINGS.json';target.write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'documents':2,'sections':sum(len(r.get('selected_paragraphs',[])) for r in reports),'output':str(target)}))
if __name__=='__main__':main()
