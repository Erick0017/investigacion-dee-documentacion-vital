"""Extracción editorial de fuentes existentes; no ejecuta DEE."""
from pathlib import Path
from zipfile import ZipFile
import base64,xml.etree.ElementTree as E,io,hashlib,json
W=Path(__file__).resolve().parent
B=Path(r'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests')
P=B/'documantacion vital/FISICA DEE Y PROCESAMIENTO NATIVO/Procesamiento_Nativo_DEE_Libro_Manual_v1.docx'
def h(b):return hashlib.sha256(b).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
x=E.fromstring(ZipFile(P).read('customXml/dee_processing_capsule.xml'));blob=base64.b64decode(list(x)[0].text)
assert h(blob)==x.attrib['sha256']
z=ZipFile(io.BytesIO(blob));sources=[]
for member,name in [('verificar_dee.py','verificar_dee_original.py'),('verificaciones/VERIFICACION_EDITORIAL_LINUX.json','VERIFICACION_EDITORIAL_LINUX_original.json'),('fuentes/U1/C06_C07_EVIDENCE_ATOMS.jsonl','C06_C07_EVIDENCE_ATOMS_original.jsonl')]:
    b=z.read(member);target=W/name
    if target.exists():assert target.read_bytes()==b
    else:target.write_bytes(b)
    sources.append({'docx':str(P),'docx_sha256':h(P.read_bytes()),'capsule_member':member,'member_sha256':h(b),'capsule_sha256':h(blob),'local_copy':str(target),'bytes':len(b)})
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
r=E.fromstring(ZipFile(P).read('word/document.xml'))
paras=[''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in r.findall('.//w:p',ns)]
excerpts=[{'paragraph':i,'text':s} for i,s in enumerate(paras) if 280<=i<=306 or 'G07' in s]
save(W/'DOCX_PASAJES.json',excerpts)
save(W/'PROCEDENCIA.json',{'sources':sources,'new_native_ticks':0,'method':'Read DOCX and capsule bytes only; no execution of included verifier.'})
code=(W/'verificar_dee_original.py').read_text(encoding='utf8')
lines=code.splitlines()
hits=[i for i,s in enumerate(lines) if any(k in s for k in ['def g07','def group07','G07','group_07','C6H04'])]
print('VERIFIER_MATCHES',hits)
for i in hits:print('\n'.join(f'{j+1}: {lines[j]}' for j in range(max(0,i-4),min(len(lines),i+65))))
d=json.loads((W/'VERIFICACION_EDITORIAL_LINUX_original.json').read_text(encoding='utf8'))
print('REPORT_KEYS',list(d));print('REPORT_PREVIEW',json.dumps(d,ensure_ascii=False)[:1500])
