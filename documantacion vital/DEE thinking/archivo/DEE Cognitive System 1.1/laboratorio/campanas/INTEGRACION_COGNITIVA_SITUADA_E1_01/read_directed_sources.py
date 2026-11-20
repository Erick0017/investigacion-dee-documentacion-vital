from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as E
import json,hashlib
ROOT=Path(__file__).resolve().parents[3]
VITAL=ROOT.parents[3]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def paragraphs(path):
    with ZipFile(path)as z:r=E.fromstring(z.read('word/document.xml'))
    return[''.join(p.itertext())if False else''.join(t.text or''for t in p.findall('.//w:t',NS))for p in r.findall('.//w:body/w:p',NS)]
paths=[ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_4_CANDIDATO_SIN_VALIDAR.docx',VITAL/'mente basal/ORGANIZACION_BASAL_PERSISTENTE_DOCUMENTO_MAESTRO_V2_1.docx',VITAL/'FISICA DEE Y PROCESAMIENTO NATIVO/Procesamiento_Nativo_DEE_Libro_Manual_v1.docx']
out=[]
for path in paths:
    if not path.exists():out.append({'path':str(path),'missing':True});continue
    pp=paragraphs(path)
    if 'OBP' in path.name or 'BASAL' in path.name:indices=list(range(max(0,len(pp)-60),len(pp)))
    elif 'Manual_Maestro' in path.name:indices=[i for i,p in enumerate(pp)if any(x in p for x in('3154','6100','6167','7509','1.4','CANDIDATO'))]
    else:indices=[i for i,p in enumerate(pp)if p.startswith(('16.','18.','19.','20.','21.'))or 'W00' in p or 'W11' in p or 'reutilizaci' in p.lower()][:65]
    out.append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'paragraph_count':len(pp),'read_selection':[{'p':i,'text':pp[i]}for i in indices]})
print(json.dumps(out,ensure_ascii=False,indent=2))
