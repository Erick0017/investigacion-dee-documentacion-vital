"""Final new-prose spacing/GFM correction before first DOCX authoring; no DEE."""
from pathlib import Path
import re,json,hashlib,importlib.util,shutil
P=Path(__file__).resolve().parents[1]; H=P/'codigo'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=P/'fuentes/HECHOS_INFORME_PI11_Root_R02.json'
f=json.loads(source.read_text('utf8'))
def prose(s):
    s=s.replace('C2C','ZZZCTWOCTOKENZZZ')
    s=re.sub(r'(?<=[a-záéíóúñ])(?=(?:RAW|FI|Native|MAIN|PI[0-9]|Q[12]|T[0-9]))',' ',s)
    s=re.sub(r'\b(FI|Native|RAW)(y|no|con|sin|de)(?=[0-9])',r'\1 \2 ',s)
    def number(m):
        word=m[1]; return word+('' if word.isupper() or word in ('pi','q','cp') else ' ')+m[2]
    s=re.sub(r'\b([A-Za-zÁÉÍÓÚáéíóúñ]+)([0-9]+)',number,s)
    s=re.sub(r'(?<![0-9]),(?=\S)',', ',s)
    s=re.sub(r'([:;])(?=\S)',r'\1 ',s)
    s=re.sub(r'%(?=[A-Za-záéíóúñ])','% ',s)
    for a,b in {'almenos':'al menos','ylos':'y los','entero13':'entero 13','a13':'a 13','en(':'en (','RAW no0':'RAW no 0','experienciaNative':'experiencia Native','actuacionesambientales':'actuaciones ambientales','cognitivoNative':'cognitivo Native','modoambiental':'modo ambiental','NoNative':'No Native','loteFI':'lote FI'}.items(): s=s.replace(a,b)
    return s.replace('ZZZCTWOCTOKENZZZ','C2C')
f['opening_paragraphs']=[prose(x) for x in f['opening_paragraphs']]
for sec in f['sections']:
    sec['heading']=prose(sec['heading']);sec['paragraphs']=[prose(x) for x in sec['paragraphs']]
for a in f['arms']: a['label']=prose(a['label']);a['explanation']=prose(a['explanation'])
for a in f['attribution_rows']:
    for k in a: a[k]=prose(a[k])
for k in f['front']:
    if k=='control_table': f['front'][k]={a:prose(b) for a,b in f['front'][k].items()}
    else:f['front'][k]=prose(f['front'][k])
new=P/'fuentes/HECHOS_INFORME_PI11_Root_R03.json'
assert not new.exists()
new.write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n','utf8')
sp=importlib.util.spec_from_file_location('PI11_report_source_for_new_editorial_format',H/'construir_informe_PI11_R01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
sources,words=m.validate(f)
report=P/'INFORME_CIENTIFICO.md'; docs=P/'documentos/HECHOS_REALES_1_40.json'
assert sha(report)=='88034a9938faed6ff1fe9fa9988d8cc83edb71a36cf88a44d9d65717c5a48702'
backup=P/'control/RESPALDO_REDACCION_ANTES_AUTORIA_PI11_R01';backup.mkdir()
shutil.copyfile(report,backup/report.name);shutil.copyfile(docs,backup/docs.name)
text=m.assemble(f,sources)
text=re.sub(r'(?m)(^\|[^\n]*\|)\n\n(?=\|)',r'\1\n',text)
report.write_text(text,'utf8')
facts=m.document_facts(f,sources,report);docs.write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'facts':str(new),'opening_words':words,'report_bytes':report.stat().st_size,'report_sha256':sha(report),'Native_imported':False,'DOCX_authored':False,'editorial_only':True}))

