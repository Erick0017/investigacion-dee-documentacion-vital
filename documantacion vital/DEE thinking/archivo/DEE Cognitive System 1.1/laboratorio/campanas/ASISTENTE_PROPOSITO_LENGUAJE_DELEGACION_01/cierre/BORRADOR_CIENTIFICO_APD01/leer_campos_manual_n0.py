"""Read current manual XML only, no authoring, renderer or native import."""
import json
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
BASE='DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_14_MENTE_UNIFICADA_Y_FI01_SIN_VALIDACION_VISUAL.docx'
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
with ZipFile(ROOT/BASE)as z:d=E.fromstring(z.read('word/document.xml'))
rows=[];headings=[]
for p in d.iter(W+'p'):
    text=''.join(n.text or''for n in p.iter(W+'t'));s=p.find(W+'pPr/'+W+'pStyle');style=s.get(W+'val','')if s is not None else''
    if style=='Heading1':headings.append(text)
    rows.append({'text':text,'style':style})
print(json.dumps({'headings':headings,'front':rows[:36],
    'current_fields':[r for r in rows if any(x in r['text']for x in('1.14','Apéndice A.','Apéndice D.','73 entradas','MU_MAIN_FASE_R3','ACTIVO','MA_MAIN_R9'))]},ensure_ascii=False))
