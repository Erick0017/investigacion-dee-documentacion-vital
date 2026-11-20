"""Read-only OOXML context/manifests for PI08. Never writes or opens Word.

Emits only JSON/TXT in a fresh P8/codigo or P8/fuentes directory. Front matter
and the existing PI07 chapter are textual reading; other chapters are structural
fingerprints only. Optional comparison reports changes, never approves them.
"""
from pathlib import Path, PurePosixPath
import argparse
import datetime
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile

P8 = Path(__file__).resolve().parents[1]
R = P8.parents[2]
C = R/'DEE Cognitive 2.0'
MANUAL = C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
COMP = R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def text(node):
    return ''.join(x.text or '' for x in node.findall('.//w:t',NS))


def style(node):
    value=node.find('w:pPr/w:pStyle',NS)
    return None if value is None else value.get('{'+NS['w']+'}val')


def allowed(path):
    p=Path(path).resolve(strict=True)
    if p not in (MANUAL.resolve(),COMP.resolve()) and not p.is_relative_to((P8/'documentos').resolve()):
        raise ValueError('Only the two current originals or PI08 staged documents may be read')
    for node in(Path(path).absolute(),*Path(path).absolute().parents):
        st=node.lstat()
        if node.is_symlink()or getattr(st,'st_file_attributes',0)&1024:
            raise ValueError('Linked/reparse document rejected')
        if node==R:break
    return p


def inspect(path,kind):
    p=allowed(path);data=p.read_bytes()
    with zipfile.ZipFile(p)as z:
        if z.testzip()is not None:raise ValueError('DOCX CRC failure')
        names=z.namelist()
        if len(names)!=len(set(n.casefold()for n in names)):raise ValueError('Aliased DOCX members')
        parts=[]
        for n in names:
            q=PurePosixPath(n)
            if q.is_absolute()or'..'in q.parts or':'in n or'\\'in n:raise ValueError('Unsafe DOCX member')
            b=z.read(n)
            if n.endswith('.xml'):ET.fromstring(b)
            parts.append({'part':n,'bytes':len(b),'sha256':sha(b)})
        root=ET.fromstring(z.read('word/document.xml'));body=root.find('w:body',NS)
        if body is None:raise ValueError('Missing document body')
        h1={'Heading1','Heading 1','Ttulo1','Título1'}
        if 'word/styles.xml'in names:
            styles=ET.fromstring(z.read('word/styles.xml'))
            for s in styles.findall('w:style',NS):
                n=s.find('w:name',NS)
                if n is not None and n.get('{'+NS['w']+'}val','').lower()in('heading 1','título 1','titulo 1'):
                    h1.add(s.get('{'+NS['w']+'}styleId'))
        sequence=[];sections={};current='FRONT'
        for i,node in enumerate(body):
            t=text(node);st=style(node)
            is_heading=node.tag.endswith('}p')and st in h1
            if is_heading:
                m=re.match(r'^(\d+)\.\s',t)
                if m:current='CHAPTER_'+m.group(1)
                elif re.match(r'^Ap[eé]ndice\s+',t,re.I):current=t
            row={'body_child':i,'type':node.tag.rsplit('}',1)[-1],
                 'style':st,'text':t,'parsed_element_sha256':sha(ET.tostring(node,encoding='utf-8'))}
            sequence.append(row);sections.setdefault(current,[]).append(row)
        fingerprints={k:{'elements':len(v),'parsed_serialization_sequence_sha256':
                         sha(json.dumps([r['parsed_element_sha256']for r in v],separators=(',',':')).encode())}
                      for k,v in sections.items()}
        if kind=='Manual':
            excerpt=sections.get('FRONT',[])[:180]+sections.get('CHAPTER_50',[])
            scope='Front: at most180 body elements; chapter50 complete if recognized as Heading1. All other chapters structurally fingerprinted, not newly read semantically.'
            if not sections.get('CHAPTER_50'):raise ValueError('Actual Heading1 chapter50 not found; do not use a TOC match')
        else:
            excerpt=sequence[-100:]
            scope='Last100 body elements only; full package/parts structurally fingerprinted, not a fresh complete scientific reading.'
        header_footer=[]
        for n in names:
            if re.match(r'word/(header|footer)\d+\.xml$',n):
                header_footer.append({'part':n,'text':text(ET.fromstring(z.read(n)))})
    if p.read_bytes()!=data:raise ValueError('Document changed during passive inspection')
    return {'schema':'DEE.PI08.read_only_document_context.v1','kind':kind,'source':str(p),
            'bytes':len(data),'sha256':sha(data),'CRC_all_members':True,'parts':parts,
            'body_elements':len(sequence),'table_count':sum(r['type']=='tbl'for r in sequence),
            'paragraphs_including_tables':len(root.findall('.//w:p',NS)),
            'section_fingerprints':fingerprints,'excerpt':excerpt,'header_footer':header_footer,
            'reading_scope':scope,'fingerprint_representation':'ElementTree serialization within this tool; not original member byte spans.',
            'DOCX_authored_or_modified':False,'visual_review':False,'macros_links_executed':False,'new_Native_ticks':0}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manual',type=Path,default=MANUAL)
    ap.add_argument('--compendio',type=Path,default=COMP)
    ap.add_argument('--comparar-manual',type=Path)
    ap.add_argument('--salida',type=Path,required=True)
    a=ap.parse_args();dest=a.salida.resolve()
    if dest.exists()or not any(dest.is_relative_to((P8/n).resolve())for n in('codigo','fuentes')):
        raise ValueError('Fresh PI08 codigo/fuentes output directory required')
    manual=inspect(a.manual,'Manual');comp=inspect(a.compendio,'Compendium')
    compare=None
    if a.comparar_manual:
        newer=inspect(a.comparar_manual,'Manual')
        old=manual['section_fingerprints'];new=newer['section_fingerprints']
        compare={'source':newer['source'],'sha256':newer['sha256'],
                 'same_sections':[k for k in old if old[k]==new.get(k)],
                 'changed_sections':[k for k in old if k in new and old[k]!=new[k]],
                 'missing_sections':[k for k in old if k not in new],
                 'added_sections':[k for k in new if k not in old],
                 'approval':None,'scope':'Structural difference report only; intended changes require actual editorial review.'}
    dest.mkdir(parents=True)
    for name,obj in [('MANUAL_CONTEXTO.json',manual),('COMPENDIO_CONTEXTO.json',comp)]:
        (dest/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (dest/name.replace('.json','.txt')).write_text('\n'.join(
            f"[{r['body_child']} {r['type']} {r['style']}] {r['text']}"for r in obj['excerpt'])+'\n',encoding='utf-8')
    manifest={'schema':'DEE.PI08.document_context_manifest.v1','at':datetime.datetime.now().astimezone().isoformat(),
              'sources':[{'kind':o['kind'],'source':o['source'],'bytes':o['bytes'],'sha256':o['sha256']}for o in(manual,comp)],
              'files':[{'file':f.name,'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())}for f in sorted(dest.iterdir())],
              'comparison':compare,'new_Native_ticks':0,'DOCX_authored_or_modified':False,'visual_review':False}
    (dest/'MANIFIESTO_CONTEXTO.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(dest),'manual_sha256':manual['sha256'],'chapter50_elements':manual['section_fingerprints']['CHAPTER_50']['elements'],
                      'new_Native_ticks':0,'DOCX_modified':False},ensure_ascii=False))


if __name__=='__main__':main()
