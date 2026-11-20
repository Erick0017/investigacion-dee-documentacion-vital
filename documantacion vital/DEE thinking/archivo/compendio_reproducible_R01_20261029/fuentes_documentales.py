from pathlib import Path
import json,re
from docx import Document
B=Path(__file__).resolve().parent
d=Document(B/'COMPENDIO_EDICION_ANTERIOR.docx');active=False;rows=[];current=None;previous=''
for p in d.paragraphs:
 t=p.text.replace('\u200b','').strip()
 if t=='Índice de fuentes, primarios y localizadores':active=True;continue
 if not active:continue
 if p.style.name.startswith('Heading')and t=='Cobertura y límite documental':break
 if t.startswith('Archivo:'):
  current=dict(id=previous,Archivo=t.split(':',1)[1].strip());rows.append(current)
 elif current and ':'in t:
  key,value=t.split(':',1)
  if key in('SHA-256','Localizador','Alcance'):current[key]=value.strip()
 previous=t
assert len(rows)==70,len(rows)
(B/'FUENTES_DOCUMENTALES.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('70 fuentes documentales conservadas con sus localizadores')
