"""Read-only complete OOXML text extraction, with paragraph/table/equation loci.

No DOCX authored/edited. A textual source reader is not a layout/render review.
"""
import argparse,hashlib,json,sys,zipfile
from pathlib import Path
from xml.etree import ElementTree as E
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M='{http://schemas.openxmlformats.org/officeDocument/2006/math}'
def extract(source,out):
 out.mkdir(parents=True,exist_ok=False);rows=[];members=[]
 with zipfile.ZipFile(source)as z:
  if z.testzip():raise ValueError('DOCX CRC differs')
  for name in z.namelist():
   if name=='word/document.xml'or(name.startswith('word/')and name.endswith('.xml')and any(q in name for q in('footnotes','endnotes','header','footer','comments'))):
    node=E.fromstring(z.read(name));count=0
    for p in node.iter(W+'p'):
     parts=[]
     for item in p.iter():
      if item.tag in(W+'t',M+'t'):parts.append(item.text or'')
      elif item.tag==W+'tab':parts.append('\t')
      elif item.tag==W+'br':parts.append('\n')
     text=''.join(parts)
     if text.strip():count+=1;rows.append({'member':name,'nonempty_paragraph':count,'text':text})
    members.append({'member':name,'nonempty_paragraphs':count})
 text='\n'.join(f"[{r['member']} p{r['nonempty_paragraph']}] {r['text']}"for r in rows)
 with(out/'TEXTO_COMPLETO.txt').open('x',encoding='utf-8')as f:f.write(text+'\n')
 with(out/'INDICE.json').open('x',encoding='utf-8')as f:json.dump({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'bytes':source.stat().st_size,'members':members,'text_rows':len(rows),'characters':len(text),'text_sha256':hashlib.sha256((text+'\n').encode()).hexdigest(),'scope':'Complete text extraction including tables/OMML, not a claim of complete reading until the investigator marks actual ranges; no layout verification','visual_render':'Bundled LibreOffice unavailable; no desktop LibreOffice invoked'},f,ensure_ascii=False,indent=2)
 print(json.dumps({'source':source.name,'paragraphs':len(rows),'characters':len(text),'out':str(out)},ensure_ascii=False))
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('--file',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();extract(a.file,a.out)
