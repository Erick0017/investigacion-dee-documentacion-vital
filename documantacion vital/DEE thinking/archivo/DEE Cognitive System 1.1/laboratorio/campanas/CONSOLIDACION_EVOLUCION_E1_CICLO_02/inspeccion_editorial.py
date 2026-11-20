from pathlib import Path
from docx import Document
import json
L=Path(__file__).resolve().parent;R=L.parents[2]
p=R/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_6_CICLO02_SIN_VALIDACION_VISUAL.docx';d=Document(p)
out=[]
for i,x in enumerate(d.paragraphs):
 if '1.5'in x.text and('edición'in x.text.lower()or'este libro'in x.text.lower()):out.append({'paragraph':i,'text':x.text})
tables=[]
for i,t in enumerate(d.tables):
 for j,r in enumerate(t.rows):
  if any('1.5'in c.text for c in r.cells):tables.append({'table':i,'row':j,'cells':[c.text for c in r.cells]})
print(json.dumps({'paragraphs':out,'tables':tables},ensure_ascii=False))
