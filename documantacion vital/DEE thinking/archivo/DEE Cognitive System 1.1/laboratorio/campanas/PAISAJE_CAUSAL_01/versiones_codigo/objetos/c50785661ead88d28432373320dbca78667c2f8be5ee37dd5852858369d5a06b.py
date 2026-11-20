"""Directed local DOCX extraction; no document modification or external access."""
from pathlib import Path
import argparse,hashlib,json,zipfile,xml.etree.ElementTree as ET
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(a.source)as z:tree=ET.fromstring(z.read('word/document.xml'))
rows=[]
for index,p in enumerate(tree.findall('.//w:p',ns)):
    text=''.join(t.text or''for t in p.findall('.//w:t',ns));style=p.find('w:pPr/w:pStyle',ns);style=style.get('{'+ns['w']+'}val','')if style is not None else''
    if text.strip():rows.append({'paragraph':index,'style':style,'text':text})
h=hashlib.sha256(a.source.read_bytes()).hexdigest();tag=a.source.stem
(a.out/(tag+'.json')).write_text(json.dumps({'source':str(a.source),'sha256':h,'paragraphs':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(a.out/(tag+'.txt')).write_text('\n'.join(f"{r['paragraph']} [{r['style']}] {r['text']}"for r in rows)+'\n',encoding='utf8')
heads=[r for r in rows if any(s in r['style'].lower()for s in('heading','titulo','título'))]
print(json.dumps({'source':str(a.source),'sha256':h,'paragraphs':len(rows),'headings':heads},ensure_ascii=False))
