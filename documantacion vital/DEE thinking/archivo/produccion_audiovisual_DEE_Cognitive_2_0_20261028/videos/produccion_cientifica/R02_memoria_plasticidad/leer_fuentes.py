"""Lectura editorial dirigida, sin ejecutar ejemplos ni importar el motor."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import re,hashlib,json
W=Path(__file__).resolve().parent
ROOT=next(p for p in W.parents if p.name=='DEE thinking')
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
FILES=[(ROOT.parent/'FISICA DEE Y PROCESAMIENTO NATIVO/Procesamiento_Nativo_DEE_Libro_Manual_v1.docx',{9,10,11,12}),
 (ROOT/'4.5/DEE_thinking_4_5_0_Libro_Blanco_y_Manual_Tecnico.docx',{3,23,27,28,35,36,37,38,60}),
 (ROOT/'4.5/DEE_thinking_4_5_0_Maestro_Arquitectura_Reconstruccion.docx',{41,48,49,50,51})]
def extract():
    results=[]
    for path,requested in FILES:
        raw=path.read_bytes()
        with ZipFile(path) as z:t=etree.fromstring(z.read('word/document.xml'))
        p=[''.join(e.xpath('.//w:t/text()',namespaces=NS)) for e in t.xpath('//w:body/w:p',namespaces=NS)]
        heads=[]
        for i,text in enumerate(p):
            m=re.match(r'^(\d+)\.\s+[^\d]',text)
            if m:heads.append((i,int(m[1]),text))
        chapters=[]
        for j,(i,k,title) in enumerate(heads):
            if k not in requested:continue
            end=heads[j+1][0] if j+1<len(heads) else min(len(p),i+70)
            chapters.append(dict(chapter=k,title=title,body_paragraph=i,paragraphs=[dict(index=n,text=p[n]) for n in range(i,end)]))
        results.append(dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),chapters=chapters))
    return results
if __name__=='__main__':
    for src in extract():
        print('\nFUENTE',src['path'],'SHA256',src['sha256'])
        for ch in src['chapters']:
            print('\n',ch['title'])
            for p in ch['paragraphs']:
                # Código disponible en origen; la lectura audiovisual se centra
                # en la explicación, magnitudes funcionales y atribución.
                if len(p['text'])<1800:print(p['index'],p['text'])
