from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import hashlib,re
R=Path(__file__).resolve().parents[3]
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
for name in ['DEE_thinking_4_5_0_Libro_Blanco_y_Manual_Tecnico.docx','DEE_thinking_4_5_0_Maestro_Arquitectura_Reconstruccion.docx']:
    p=R/'4.5'/name
    print('\nFUENTE',name,'SHA',hashlib.sha256(p.read_bytes()).hexdigest())
    with ZipFile(p) as z:tree=etree.fromstring(z.read('word/document.xml'))
    paras=[''.join(e.itertext()) for e in tree.xpath('//w:body/w:p//w:t',namespaces=ns)]
    # Texto por párrafo evita fragmentar runs de los mismos encabezados.
    paras=[''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in tree.xpath('//w:body/w:p',namespaces=ns)]
    candidates=[]
    for i,t in enumerate(paras):
        if re.match(r'^(35|36|37|38|39|40)([ .]|$)',t) or (len(t)<130 and any(q in t.lower() for q in ['persistencia','observa','sesion','sesión','f04','paisaje','sonda','snapshot','interfaz','interfaces'])):
            candidates.append(i)
    covered=set()
    for i in candidates:
        for j in range(i,min(i+6,len(paras))):
            if j not in covered: print(j,paras[j]);covered.add(j)
