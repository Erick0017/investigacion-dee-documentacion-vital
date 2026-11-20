"""Editorial draft text only. Numbers/evidence/flags/selection remain literal."""
from pathlib import Path
import copy,hashlib,json
P=Path(__file__).resolve().parents[1];file=P/'documentos/HECHOS_FINALES_1_38_PI09_BORRADOR.json';before=file.read_bytes();d=json.loads(before);assert d['closed_for_authoring']is False
old=copy.deepcopy(d)
fixes={'Este JSON permanece cerrado para autoría:':'Este JSON no autoriza aún la autoría:','Edición1.38':'Edición 1.38','Manual1.37':'Manual 1.37','Native12/12':'Native 12/12','D experimental5/6':'D experimental 5/6','a3/6 y1/6':'a 3/6 y 1/6','STATE1':'STATE 1','motor2':'motor 2','5 frente a3 y1':'5 frente a 3 y 1','externa400':'externa de 400','de2346':'de 2346','global67':'global 67','internas391/782':'internas 391/782','Real1139':'Real 1139','NoFail1144':'NoFail 1144','Yoke1147':'Yoke 1147','aplicaron1137,1138 y1137, con2,6 y10':'aplicaron 1137, 1138 y 1137, con 2, 6 y 10','ordinal12/18':'ordinal 12/18','31/32 y4/8':'31/32 y 4/8','ordinal6/12':'ordinal 6/12','copias12/12':'copias 12/12','más5/5':'más 5/5','AR0guard':'AR0 guard','corpus. No':'corpus. No'}
def edit(text):
    for a,b in fixes.items():text=text.replace(a,b)
    return text
d['description']=edit(d['description'])
for key,value in d['front'].items():
    if isinstance(value,str):d['front'][key]=edit(value)
    else:d['front'][key]={k:edit(v)for k,v in value.items()}
for collection in('manual_sections','compendium_sections'):
    for section in d[collection]:section['heading']=edit(section['heading']);section['paragraphs']=[edit(x)for x in section['paragraphs']]
for key in d:
    if key not in('description','front','manual_sections','compendium_sections'):assert d[key]==old[key]
folder=P/'documentos/revisiones';folder.mkdir(exist_ok=True);backup=folder/('HECHOS_1_38_BORRADOR_ANTES_ESPACIADO_'+hashlib.sha256(before).hexdigest()[:12]+'.json')
with backup.open('xb')as f:f.write(before)
file.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'file':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'closed_for_authoring':False,'Native_or_DOCX_executed':False,'numbers_and_evidence_flags_unchanged':True,'prior_literal':str(backup)}))
