"""Read existing Word structure, not a render or an edit."""
import json
from pathlib import Path
from docx import Document
L=Path(__file__).resolve().parent;R=L.parents[2];E=R/'evidencia/campanas/MENTE_DEE_INTEGRAL_MI01';p=R/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_6_CICLO02_SIN_VALIDACION_VISUAL.docx';d=Document(p)
headings=[{'index':i,'style':p.style.name,'text':p.text}for i,p in enumerate(d.paragraphs)if p.style.name.startswith(('Heading','Title'))or p.text.startswith(('23 ','23.','Índice de consulta','Apéndice','1. Qué','22. '))]
tables=[{'index':i,'rows':[[c.text for c in row.cells]for row in t.rows]}for i,t in enumerate(d.tables[:2])]
out={'path':str(p),'headings':headings,'control_tables':tables,'headers':[[p.text for p in s.header.paragraphs]for s in d.sections],'footers':[[p.text for p in s.footer.paragraphs]for s in d.sections],'not_visual_validation':True};(E/'INSPECCION_EDITORIAL_WORD_0TICKS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False,indent=2))
