"""Selected official documentation, no physical experiment or engine import."""
import json,hashlib,zipfile,io,xml.etree.ElementTree as ET
from pathlib import Path
L=Path(__file__).resolve().parent;R=L.parents[2];E=R/'evidencia/campanas/MENTE_DEE_INTEGRAL_MI01';tests=R.parents[4]
p=tests/'documantacion vital/DEE thinking/4.5/DEE_THINKING_4_5_0_COMPILACION_Y_VALIDACION_RESULTADOS.zip'
with zipfile.ZipFile(p)as z:
    names=[n for n in z.namelist()if n.endswith('.docx')and('Libro_Blanco' in n or'Maestro_Arquitectura' in n)]
    output=[];sources=[]
    for name in names:
        b=z.read(name)
        with zipfile.ZipFile(io.BytesIO(b))as d:tree=ET.fromstring(d.read('word/document.xml'))
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};paras=[''.join(v.text or''for v in q.findall('.//w:t',ns))for q in tree.findall('.//w:p',ns)]
        selected=set()
        for i,t in enumerate(paras):
            if any(k in t.lower()for k in('snapshot','observaci','sonda','integratedsession','cola pendiente','paisaje causal','f04','persistencia','repertoiresession')):
                selected.update(range(max(0,i-1),min(len(paras),i+2)))
        output.append('SOURCE '+name+' SHA256 '+hashlib.sha256(b).hexdigest())
        output.extend(str(i)+': '+paras[i]for i in sorted(selected))
        sources.append({'archive':str(p),'archive_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'member':name,'member_sha256':hashlib.sha256(b).hexdigest(),'selected_paragraphs':len(selected),'complete_paragraphs':len(paras),'scope':'Directed published contracts/observation/persistence, not a claim of complete re-reading'})
(E/'THINKING45_CONSULTA_DIRIGIDA.txt').write_text('\n'.join(output),encoding='utf8')
(E/'THINKING45_FUENTES_CONSULTADAS.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf8')
print('\n'.join(output))
