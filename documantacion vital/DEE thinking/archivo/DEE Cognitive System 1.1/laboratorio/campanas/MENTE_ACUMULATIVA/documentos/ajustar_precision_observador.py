"""One-sentence scope correction after independent primary review. No DEE imports."""
from copy import deepcopy
from pathlib import Path
import hashlib, json, shutil
from zipfile import ZipFile
from lxml import etree as E
from actualizar_manual_acumulativa import ROOT,HERE,NAME,W,txt,put,digest

path=ROOT/NAME
before=digest(path)
assert before=='7e27b63775a5157303a0ac50770bb4d9c106be6c39bbdbfae64c4ae16b0a6070'
historical=ROOT/'documentos/historico_manuales'/('DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_12_PRE_PRECISION_'+before[:12]+'.docx')
assert not historical.exists()
shutil.copy2(path,historical)
data=json.loads((HERE/'RESULTADOS_FINALES_MANUAL.json').read_text(encoding='utf-8'))
replacement=next(q['text'] for q in data['chapter'] if q['text'].startswith('El registro profundo reprodujo técnicamente'))
with ZipFile(path) as z:
    infos=z.infolist();members={i.filename:z.read(i.filename) for i in infos}
d=E.fromstring(members['word/document.xml']);matches=[p for p in d.iter(W+'p') if txt(p).startswith('El registro profundo reprodujo técnicamente')]
assert len(matches)==1
old=txt(matches[0]);put(matches[0],replacement)
members['word/document.xml']=E.tostring(d,xml_declaration=True,encoding='UTF-8',standalone=True)
temp=path.with_suffix('.precision.tmp.docx')
with ZipFile(temp,'w') as z:
    for i in infos:z.writestr(i,members[i.filename])
with ZipFile(temp) as z:assert z.testzip() is None
temp.replace(path)
proof={'schema':'MENTE_ACUMULATIVA.manual.precision.v1','document':str(path),'old_sha256':before,'sha256':digest(path),'bytes':path.stat().st_size,'old_revision':str(historical),'old':old,'new':replacement,'native_ticks':0,'basis':'Independent primary review confirmed input/receipt schedule and RAW/clocks/commands, not all metadata/protocol bytes.'}
(HERE/'EDICION_FINAL_PRECISION_1_12.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:proof[k] for k in ('document','sha256','bytes','native_ticks')},ensure_ascii=True))
