"""Read only the current documentary front; never imports DEE or Word."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as E
P=Path(__file__).resolve().parents[1]
M=P.parents[2]/'DEE Cognitive 2.0/DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
with zipfile.ZipFile(M)as z:
 b=E.fromstring(z.read('word/document.xml')).find(W+'body')
 rows=[]
 for i,n in enumerate(list(b)[:30]):
  rows.append({'i':i,'text':''.join(x.text or ''for x in n.iter(W+'t')),'cells':[[''.join(x.text or ''for x in c.iter(W+'t'))for c in r.findall(W+'tc')]for r in n.findall('.//'+W+'tr')]})
 print(json.dumps(rows,ensure_ascii=False,indent=2))
