from pathlib import Path
import argparse,hashlib,json,zipfile,xml.etree.ElementTree as ET
p=argparse.ArgumentParser();p.add_argument('manual',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
with zipfile.ZipFile(a.manual) as z:root=ET.fromstring(z.read('word/document.xml'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
paragraphs=[''.join(p.itertext()) for p in []]
paragraphs=[''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in root.findall('.//w:body//w:p',ns)]
lines=[f'{i+1:04d} {t}'for i,t in enumerate(paragraphs)if t.strip()]
a.out.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'manual':str(a.manual),'sha256':hashlib.sha256(a.manual.read_bytes()).hexdigest(),'paragraphs':len(paragraphs),'nonempty':len(lines),'text_bytes':a.out.stat().st_size,'text_file':str(a.out)},ensure_ascii=False))
