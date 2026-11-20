"""Read only selected mechanism documents and current declared interfaces."""
import sys,hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile
L=Path(__file__).resolve().parent;R=L.parents[2];S=R/'sistema';E=R/'evidencia/campanas/MENTE_DEE_INTEGRAL_MI01'
sys.path.insert(0,str(S))
from app.lives import Store
from app.native_tools import physical
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def extract(p):
    with ZipFile(p)as z:
        root=ET.fromstring(z.read('word/document.xml'));ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        return [''.join(t.text or''for t in node.findall('.//w:t',ns))for node in root.findall('.//w:p',ns)]
base=R.parents[3] # tests/documantacion vital, overwritten by explicit scoped source below
tests=R.parents[4];vital=tests/'documantacion vital'
obp=vital/'mente basal/ORGANIZACION_BASAL_PERSISTENTE_DOCUMENTO_MAESTRO_V2_1.docx'
proc=vital/'FISICA DEE Y PROCESAMIENTO NATIVO/Procesamiento_Nativo_DEE_Libro_Manual_v1.docx'
sources=[]
for key,p in(('OBP21',obp),('ProcesamientoNativo',proc)):
    paras=extract(p)
    if key=='OBP21':chosen=paras[-170:]
    else:
        chosen=[];active=False
        for text in paras:
            if text.startswith(('16. Competencia','18. La historia','19. Reutilización','20. El procesamiento','21. Teoría')):active=True
            elif text.startswith(('17. ','22. ')):active=False
            if active:chosen.append(text)
    (E/(key+'_LECTURA_DIRIGIDA.txt')).write_text('\n'.join(chosen),encoding='utf8');sources.append({'source':str(p),'sha256':sha(p),'extract':key+'_LECTURA_DIRIGIDA.txt','paragraphs':len(chosen),'native_ticks':0})
s=Store();rec,a=s.load('E1_MI01_MAIN');pre=physical(a.world)
geometry={'tick':a.tick,'quantity':a.quantity.geometry,'two_memory':a.two_memory.geometry,'B':a.transferred_quantity.geometry,
  'B_channels':[{'name':v.name,'site':[v.channel.injection_site.x,v.channel.injection_site.y,v.channel.injection_site.z],'direction':[v.channel.direction.dx,v.channel.direction.dy,v.channel.direction.dz]}for v in a.world.interfaces if v.name.startswith('B.quantity.')],
  'read_only':True,'complete_source':rec['snapshot'],'sources':sources}
assert pre==physical(a.world)
(E/'GEOMETRIA_Y_FUENTES_DIRIGIDAS.json').write_text(json.dumps(geometry,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'tick':a.tick,'B':a.transferred_quantity.geometry,'channels':geometry['B_channels'],'sources':sources},ensure_ascii=False))
