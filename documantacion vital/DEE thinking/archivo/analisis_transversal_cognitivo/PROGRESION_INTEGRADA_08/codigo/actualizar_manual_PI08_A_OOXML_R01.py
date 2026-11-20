"""PI08 A: surgical OOXML staging. Default is read-only. No DEE/Word imports.

Root must register the documents skill authoring marker before --author. This
program does not publish documents, touch selectors, execute Native or render.
Old chapter/apendix XML bytes and all non-editorial package parts are retained.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, re, shutil, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.parsers import expat
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET

P8=Path(__file__).resolve().parents[1]
R=P8.parents[2]
C=R/'DEE Cognitive 2.0'
MANUAL=C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
COMP=R/'CPC - Experimentos y mecanismos'/'COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
BASE={'manual':'410c133cc9b37f18df45205603492326c0ae17f2dcc057f1b9ff916933470779',
      'compendio':'9bb28f24cc350050047b47a4574cbaa35f2d9a298086629524ad72ef71c8a8a6'}
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W}
ANCHOR='DEE_PI08_A_CAP51'
TITLE='51 PI08 A Consolidación operativa y capacidades recuperables'

def sha(data): return hashlib.sha256(data).hexdigest()
def file_sha(p): return sha(Path(p).read_bytes())
def read_json(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write_json(p,j):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(j,f,ensure_ascii=False,indent=2);f.write('\n')
def pointer(j,p):
    if p=='': return j
    if not p.startswith('/'): raise ValueError('JSON pointer must start with /')
    for key in p[1:].split('/'):
        key=key.replace('~1','/').replace('~0','~')
        j=j[int(key)] if isinstance(j,list) else j[key]
    return j
def contained(p,root):
    p=Path(p).resolve();root=Path(root).resolve()
    if not p.is_relative_to(root): raise ValueError(f'Out of authorized directory: {p}')
    if any(q.is_symlink() for q in [p,*p.parents] if q.is_relative_to(root)):
        raise ValueError('Symlink refused')
    return p

def body_parts(raw):
    """Locate direct w:body children without reserializing original XML."""
    depth=0; body_depth=None; spans=[]; current=None; parser=expat.ParserCreate()
    def start(name,attrs):
        nonlocal depth,body_depth,current
        depth+=1
        if name=='w:body': body_depth=depth
        elif body_depth is not None and depth==body_depth+1:
            i=parser.CurrentByteIndex;j=raw.index(b'>',i)+1
            current=[i,None,raw[i:j].rstrip().endswith(b'/>')]
            if current[2]: current[1]=j
    def end(name):
        nonlocal depth,body_depth,current
        if body_depth is not None and depth==body_depth+1:
            if not current[2]: current[1]=raw.index(b'>',parser.CurrentByteIndex)+1
            spans.append((current[0],current[1]));current=None
        if name=='w:body': body_depth=None
        depth-=1
    parser.StartElementHandler=start;parser.EndElementHandler=end;parser.Parse(raw,True)
    if not spans: raise ValueError('No body children')
    # Retain whitespace between siblings as part of the preceding literal chunk.
    chunks=[raw[a:(spans[i+1][0] if i+1<len(spans) else b)] for i,(a,b) in enumerate(spans)]
    return raw[:spans[0][0]],chunks,raw[spans[-1][1]:],spans

def node(raw,prefix):
    # Inherit namespace declarations only for parsing, never serialize old XML.
    opening=prefix[:prefix.find(b'>',prefix.find(b'<w:document'))+1]
    declarations=b' '.join(re.findall(rb'xmlns(?::[\w]+)?="[^"]+"',opening))
    return ET.fromstring(b'<x '+declarations+b'>'+raw+b'</x>')[0]
def info(raw,prefix):
    n=node(raw,prefix);t=''.join(x.text or '' for x in n.iter('{'+W+'}t'))
    s=n.find('w:pPr/w:pStyle',NS)
    return n,t,s.get('{'+W+'}val') if s is not None else None
def paragraph(text,style=None,bookmark=None,link=None,pagebreak=False):
    pr=(f'<w:pStyle w:val="{escape(style)}"/>' if style else '')
    if style in ('Ttulo1','Ttulo2'): pr+='<w:keepNext/>'
    if pagebreak: pr+='<w:pageBreakBefore/>'
    txt='<w:r><w:t xml:space="preserve">'+escape(text)+'</w:t></w:r>'
    if link: txt=f'<w:hyperlink w:anchor="{link}" w:history="1">'+txt+'</w:hyperlink>'
    if bookmark:
        ident,name=bookmark
        txt=f'<w:bookmarkStart w:id="{ident}" w:name="{name}"/>'+txt+f'<w:bookmarkEnd w:id="{ident}"/>'
    return ('<w:p><w:pPr>'+pr+'</w:pPr>'+txt+'</w:p>').encode('utf-8')
def replace_texts(raw,replacements):
    # Text-node replacement in front only: keeps paragraph/table/run formatting.
    count=0
    def sub(m):
        nonlocal count
        text=ET.fromstring(b'<x>'+m.group(1)+b'</x>').text or ''
        if text in replacements:
            count+=1
            return m.group(0).split(b'>',1)[0]+b'>'+escape(replacements[text]).encode()+b'</w:t>'
        return m.group(0)
    result=re.sub(rb'<w:t(?:\s[^>]*)?>(.*?)</w:t>',sub,raw,flags=re.S)
    return result,count
def whole_paragraph(raw,prefix,newtext):
    n,t,s=info(raw,prefix)
    if n.tag!='{'+W+'}p': raise ValueError('Expected paragraph')
    # Existing direct pPr copied literally; only selected front paragraph rebuilt.
    opening=raw[:raw.index(b'>')+1]
    m=re.search(rb'<w:pPr(?:\s[^>]*)?>.*?</w:pPr>|<w:pPr\s*/>',raw,re.S)
    pp=m.group(0) if m else b''
    return opening+pp+('<w:r><w:t xml:space="preserve">'+escape(newtext)+'</w:t></w:r></w:p>').encode()

def render_sections(sections,first_heading,title,bookmark_id=None):
    result=[paragraph(title,'Ttulo1',None if bookmark_id is None else (bookmark_id,ANCHOR),pagebreak=True)]
    if not sections or len(sections)>10: raise ValueError('Need 1..10 explained subsections')
    for i,s in enumerate(sections,1):
        result.append(paragraph(f'{first_heading}.{i} '+s['heading'],'Ttulo2'))
        if not s.get('paragraphs'): raise ValueError('Empty scientific subsection')
        for t in s['paragraphs']:
            if not isinstance(t,str) or not t.strip(): raise ValueError('Empty paragraph')
            result.append(paragraph(t))
        for t in s.get('sources',[]): result.append(paragraph('Fuente: '+t,'Source'))
    return b''.join(result)

def check_facts(f):
    if f.get('schema')!='DEE.PI08.A.document_facts.v1': raise ValueError('Wrong facts schema')
    if f.get('closed_for_authoring') is not True: raise ValueError('Facts not closed by Root')
    p=f['principal']
    if p['status']!='COMMITTED' or p['N']!=67 or p['T']<=860622:
        raise ValueError('Require actual committed principal beyond adoption after public use')
    if not re.fullmatch('[0-9a-f]{64}',p['snapshot_sha256']): raise ValueError('Snapshot SHA missing')
    if not p.get('parent_as_recorded') or not p.get('complete_pair_path'): raise ValueError('Genealogy/pair missing')
    def no_placeholders(x):
        if isinstance(x,str) and (re.search(r'\bROOT:',x) or '{{' in x): raise ValueError('Unresolved editorial placeholder')
        if isinstance(x,dict):
            for v in x.values(): no_placeholders(v)
        if isinstance(x,list):
            for v in x: no_placeholders(v)
    for key in ('front','manual_sections','compendium_sections'): no_placeholders(f[key])
    record_path=Path(f['evidence']['current_record']['path'])
    if not record_path.is_absolute() or not record_path.resolve().is_relative_to(C.resolve()):
        raise ValueError('Current record must be actual product VIDA JSON under Cognitive')
    for key in ('adoption','selected_public_use','current_record','full_pair'):
        e=f['evidence'][key];q=Path(e['path'])
        if not q.is_absolute(): q=P8/q
        if file_sha(q)!=e['sha256']: raise ValueError('Evidence CAS mismatch '+key)
        j=read_json(q)
        if not e.get('checks'): raise ValueError('Actual evidence checks required '+key)
        for ptr,expected in e['checks'].items():
            if pointer(j,ptr)!=expected: raise ValueError(f'Evidence mismatch {key}:{ptr}')
    adoption=read_json(Path(f['evidence']['adoption']['path']) if Path(f['evidence']['adoption']['path']).is_absolute() else P8/f['evidence']['adoption']['path'])
    if adoption.get('phase')!='COMMITTED' or adoption.get('life_id')!=p['life_id']:
        raise ValueError('Actual adoption principal mismatch')
    for key in ('selected_public_use','current_record','full_pair'):
        e=f['evidence'][key];q=Path(e['path']);q=q if q.is_absolute() else P8/q;j=read_json(q)
        for field in ('life_id','T','snapshot_sha256'):
            ptr=e.get('principal_bindings',{}).get(field)
            if ptr is None or pointer(j,ptr)!=p[field]: raise ValueError(f'Principal binding missing/mismatch {key}:{field}')
    for key in ('R03_remaining','C2C_remaining','FI_uses'):
        if not isinstance(f['finite_resources'][key],int) or f['finite_resources'][key]<0:
            raise ValueError('Actual finite resources required')
    if f.get('actual_authoring_marker_registered_by_root') is not True:
        raise ValueError('Root must register actual documents edit/2DOCX marker before authoring')
    for source,key in ((MANUAL,'manual'),(COMP,'compendio')):
        if file_sha(source)!=BASE[key]: raise ValueError('Original document changed '+key)

def edit_manual(raw,f):
    pre,parts,post,spans=body_parts(raw);allinfo=[info(x,pre) for x in parts]
    first=next(i for i,(_,t,s) in enumerate(allinfo) if s=='Ttulo1' and re.match(r'^1(?:\.\s|\s)',t))
    append=next(i for i,(_,t,s) in enumerate(allinfo) if s=='Ttulo1' and t.startswith('Apéndice A'))
    if any(s=='Ttulo1' and t.startswith('51 ') for _,t,s in allinfo): raise ValueError('51 already exists')
    old_history=b''.join(parts[first:])
    changed=[]
    replacements={8:'DEE thinking 4.5.0 | DEE Cognitive 2.0 | Edición documental 1.35 | DCS11-MM-001',
       9:f['front']['edition_summary'],13:f['front']['principal_summary'],14:f['front']['functional_summary'],
       15:f['front']['conservation_summary'],16:f['front']['resume_summary'],
       18:'Funciones heredadas: evidencia histórica por vida y corte; continuidad actual en el capítulo 51',
       26:f['front']['coverage_summary']}
    for i,t in replacements.items():
        if i>=first: raise ValueError('Front replacement escapes front')
        parts[i]=whole_paragraph(parts[i],pre,t);changed.append(i)
    table_replacements=f['front']['control_table_exact_text_replacements']
    parts[23],n=replace_texts(parts[23],table_replacements)
    if n!=len(table_replacements): raise ValueError('Control table exact anchor count mismatch')
    changed.append(23)
    # Add a link next to existing modern chapter index, no assumed page number.
    toc=next(i for i,(_,t,s) in enumerate(allinfo[:first]) if t=='50 PI07 Regulación adquirida y descubrimiento')
    ids=[int(x) for x in re.findall(rb'<w:bookmarkStart\b[^>]*w:id="(\d+)"',raw)]
    new=render_sections(f['manual_sections'],'51',TITLE,max(ids,default=0)+1)
    additions={toc+1:paragraph(TITLE,'TOCline',link=ANCHOR),append:new}
    out=pre+b''.join(additions.get(i,b'')+x for i,x in enumerate(parts))+post
    # Old history is built from the original literal children, only insertion before A.
    preserved=b''.join(parts[first:append])+b''.join(parts[append:])
    if preserved!=old_history: raise AssertionError('Historical XML changed')
    return out,{'front_children_modified':changed,'old_history_elements':len(parts)-first,
      'old_history_literal_sha256':sha(old_history),'old_history_literal_unchanged':True,
      'new_bookmark':ANCHOR,'new_heading':TITLE,'historical_pages_guessed':False}

def edit_compendium(raw,f):
    pre,parts,post,_=body_parts(raw)
    index=next((i for i,x in enumerate(parts) if info(x,pre)[0].tag=='{'+W+'}sectPr'),len(parts))
    old=b''.join(parts)
    add=render_sections(f['compendium_sections'],'PI08 A','PI08 A Consolidación operativa y continuidad adoptada')
    return pre+b''.join(parts[:index])+add+b''.join(parts[index:])+post,{
      'old_body_elements':len(parts),'old_body_literal_sha256':sha(old),
      'old_body_literal_unchanged':True,'append_before_section_properties':True}

def core_edit(raw,f,is_manual):
    text=raw.decode()
    vals={'cp:version':'1.35','cp:revision':'35','dcterms:modified':f['cut_utc'],
      'dc:description':f['document_description']}
    if is_manual: vals['dc:title']='DEE Cognitive 2.0 Manual Maestro Edición 1.35 PI08 A'
    for tag,value in vals.items():
        pattern=r'(<'+re.escape(tag)+r'(?:\s[^>]*)?>).*?(</'+re.escape(tag)+r'>)'
        text,n=re.subn(pattern,lambda m:m[1]+escape(value)+m[2],text,flags=re.S)
        if n!=1: raise ValueError('Missing/duplicate core field '+tag)
    return text.encode()
def settings_edit(raw):
    item=b'<w:updateFields w:val="true"/>'
    if re.search(rb'<w:updateFields\b',raw):
        return re.sub(rb'<w:updateFields\b[^>]*(?:/>|>.*?</w:updateFields>)',item,raw,flags=re.S)
    return raw.replace(b'</w:settings>',item+b'</w:settings>')

def build_package(source,dest,f,manual):
    result={};member_proof=[]
    with zipfile.ZipFile(source) as zin:
        if zin.testzip(): raise ValueError('Source CRC failed')
        oldparts={i.filename:zin.read(i) for i in zin.infolist()}
        changes={}
        changes['word/document.xml'],bodyproof=(edit_manual(oldparts['word/document.xml'],f) if manual else edit_compendium(oldparts['word/document.xml'],f))
        changes['docProps/core.xml']=core_edit(oldparts['docProps/core.xml'],f,manual)
        if 'word/settings.xml' in oldparts: changes['word/settings.xml']=settings_edit(oldparts['word/settings.xml'])
        if manual:
            for name,data in oldparts.items():
                if re.fullmatch(r'word/(?:header|footer)\d+\.xml',name):
                    new=data.replace(b'1.34',b'1.35').replace(b'PI07 cierre',b'PI08 A consolidado')
                    if new!=data: changes[name]=new
        for name,data in changes.items(): ET.fromstring(data)
        with zipfile.ZipFile(dest,'x') as zout:
            for zi in zin.infolist(): zout.writestr(copy.copy(zi),changes.get(zi.filename,oldparts[zi.filename]))
    with zipfile.ZipFile(dest) as z:
        if z.testzip(): raise ValueError('Staged CRC failed')
        if set(z.namelist())!=set(oldparts): raise AssertionError('Package parts added/removed')
        for name,old in oldparts.items():
            now=z.read(name);changed=now!=old
            if changed and name not in changes: raise AssertionError('Unapproved package change')
            if name.endswith('.xml') or name.endswith('.rels'): ET.fromstring(now)
            member_proof.append({'part':name,'before_sha256':sha(old),'after_sha256':sha(now),'changed':changed})
        body=ET.fromstring(z.read('word/document.xml'))
        if manual:
            if len([x for x in body.iter('{'+W+'}bookmarkStart') if x.get('{'+W+'}name')==ANCHOR])!=1:
                raise AssertionError('Missing/duplicate chapter bookmark')
            pre2,p2,_,_=body_parts(z.read('word/document.xml'))
            inf2=[info(x,pre2) for x in p2]
            h1=next(i for i,(_,t,s) in enumerate(inf2) if s=='Ttulo1' and re.match(r'^1(?:\.\s|\s)',t))
            h51=next(i for i,(_,t,s) in enumerate(inf2) if s=='Ttulo1' and t==TITLE)
            apx=next(i for i,(_,t,s) in enumerate(inf2) if s=='Ttulo1' and t.startswith('Apéndice A'))
            if sha(b''.join(p2[h1:h51])+b''.join(p2[apx:]))!=bodyproof['old_history_literal_sha256']:
                raise AssertionError('Reopened package historical XML mismatch')
        else:
            pre2,p2,_,_=body_parts(z.read('word/document.xml'));inf2=[info(x,pre2) for x in p2]
            pos=next(i for i,(_,t,s) in enumerate(inf2) if s=='Ttulo1' and t=='PI08 A Consolidación operativa y continuidad adoptada')
            sec=next((i for i,(n,_,_) in enumerate(inf2) if n.tag=='{'+W+'}sectPr'),len(p2))
            if sha(b''.join(p2[:pos])+b''.join(p2[sec:]))!=bodyproof['old_body_literal_sha256']:
                raise AssertionError('Reopened compendium old body XML mismatch')
    return {'source':str(source),'source_sha256':file_sha(source),'output':str(dest),
      'output_bytes':dest.stat().st_size,'output_sha256':file_sha(dest),'CRC_all_members':True,
      'XML_parse_all_parts':True,'body_preservation':bodyproof,'parts':member_proof,
      'rendered_pdf':None,'page_count':None,'visual_validation':'NOT_YET_ATTEMPTED_BY_THIS_BUILDER'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--facts',type=Path,required=True)
    ap.add_argument('--author',action='store_true');ap.add_argument('--output',type=Path)
    a=ap.parse_args();f=read_json(a.facts)
    if not a.author:
        print(json.dumps({'schema':'DEE.PI08.A.document_plan.v1','read_only':True,'new_Native_ticks':0,
          'DOCX_authored':False,'closed_for_authoring':f.get('closed_for_authoring'),
          'current_sources':[{ 'path':str(p),'bytes':p.stat().st_size,'sha256':file_sha(p)} for p in (MANUAL,COMP)],
          'required_before_author':'Root documents skill marker edit/2DOCX; actual closed facts/evidence; explicit --author',
          'publication':'Separate literal CAS publication by Root; this script only stages'},ensure_ascii=False,indent=2));return
    check_facts(f)
    out=contained(a.output if a.output else P8/'documentos'/('staging_A_1_35_'+datetime.now().strftime('%Y%m%d_%H%M%S')),P8/'documentos')
    if out.exists(): raise FileExistsError('Fresh staging directory required')
    # All facts/CAS checks completed before the first authorized output write.
    backup=P8/'documentos'/'respaldo_1_34';backup.mkdir(parents=True,exist_ok=True)
    for src,key in ((MANUAL,'manual'),(COMP,'compendio')):
        dst=backup/src.name
        if dst.exists():
            if file_sha(dst)!=BASE[key]: raise ValueError('Existing backup differs')
        else:
            shutil.copy2(src,dst)
            if file_sha(dst)!=BASE[key]: raise AssertionError('Backup hash mismatch')
    out.mkdir(parents=True,exist_ok=False)
    docs=[build_package(MANUAL,out/MANUAL.name,f,True),build_package(COMP,out/COMP.name,f,False)]
    for src,key in ((MANUAL,'manual'),(COMP,'compendio')):
        if file_sha(src)!=BASE[key]: raise AssertionError('Original changed concurrently')
    proof={'schema':'DEE.PI08.A.staged_surgical_OOXML.v1','at':datetime.now(timezone.utc).isoformat(),
      'facts_source':str(a.facts.resolve()),'facts_sha256':file_sha(a.facts),'edition':'1.35',
      'principal':f['principal'],'new_Native_ticks':0,'DEE_imports':0,'originals_modified':False,
      'published':False,'documents':docs,'visual_validation':'PENDING_ROOT_BOUNDED_RENDER_AND_REVIEW',
      'prior_visual_limitation_preserved_in_original':'PI07 could not prove Word instance ownership; no old app closed'}
    write_json(out/'VALIDACION_ESTRUCTURAL_PI08_A_1_35.json',proof)
    print(json.dumps({'staging':str(out),'proof_sha256':file_sha(out/'VALIDACION_ESTRUCTURAL_PI08_A_1_35.json'),
      'documents':[{'file':d['output'],'sha256':d['output_sha256'],'bytes':d['output_bytes']} for d in docs]},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
