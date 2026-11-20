"""Stage the same complete Master1.29 and appended Compendium from closed facts.

No automatic scientific conclusion, promotion, renderer or Native import. The
required input is control/CIERRE_CIENTIFICO_PI02.json, closed_for_authoring=true,
with the agreed manual_1_29 block. The draft template is deliberately refused.
Root retains publication authority after rendering and affected-page QA.
"""
from pathlib import Path
from copy import deepcopy
import argparse,datetime,hashlib,importlib.util,json,re,zipfile
from lxml import etree as E

P=Path(__file__).resolve().parent.parent;R=P.parent.parent.parent
C=R/'DEE Cognitive 2.0';D=P/'documentos'
NAME='DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
MAN=C/NAME;COMP=R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
EXPECTED_MAN='d6f3b8d8cbf12353573f062bd7730b679aef2768f8487de79c9348c734c11f01'
EXPECTED_COMP='26b58062eac0a804bd73f27139dc5b9d7a9bafa1579d67babedc420105baf9c7'
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
XML='{http://www.w3.org/XML/1998/namespace}'
TITLE='45 PI02 Cierre integrado, acceso, advertencia y actuación'
def sha(data):return hashlib.sha256(data).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def utilities():
    path=P/'codigo/actualizacion_manual_PI02.py'
    spec=importlib.util.spec_from_file_location('pi02_documentary_helpers_A',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module,path
def paragraph(u,template,value,code=False):
    # Never apply old spacing heuristics to IDs, technical literals or prose.
    p=u.para(template,'',code=code);u.settext(p,value,verbatim=True)
    return p
def set_flag(parent,name,value='1'):
    node=parent.find(W+name)
    if node is None:node=E.SubElement(parent,W+name)
    node.set(W+'val',value)
def command_block(u,template,lines):
    if not lines or any(not isinstance(line,str)or'\n'in line for line in lines):raise ValueError('Explicit command lines required')
    if any('--nueva'in line for line in lines):raise ValueError('No new-world command in continuation example')
    p=paragraph(u,template,'',code=True);r=p.find(W+'r')
    for node in list(r):
        if node.tag!=W+'rPr':r.remove(node)
    pp=p.find(W+'pPr')
    if pp is None:pp=E.Element(W+'pPr');p.insert(0,pp)
    set_flag(pp,'keepLines')
    for i,line in enumerate(lines):
        if i:E.SubElement(r,W+'br')
        t=E.SubElement(r,W+'t');t.set(XML+'space','preserve');t.text=line
    return p
def make_table(u,template,spec):
    headers=spec['headers'];rows=spec['rows'];columns=len(headers)
    if not 2<=columns<=6 or any(len(row)!=columns for row in rows):raise ValueError('Rectangular compact table required')
    widths=spec.get('widths')or[9000//columns]*columns
    if len(widths)!=columns or any(type(w)is not int or w<700 for w in widths)or sum(widths)>9000:raise ValueError('Table exceeds known page width')
    table=E.Element(W+'tbl');pr=E.SubElement(table,W+'tblPr')
    tw=E.SubElement(pr,W+'tblW');tw.set(W+'w',str(sum(widths)));tw.set(W+'type','dxa')
    E.SubElement(pr,W+'jc').set(W+'val','center');E.SubElement(pr,W+'tblLayout').set(W+'type','fixed')
    borders=E.SubElement(pr,W+'tblBorders')
    for side in('top','left','bottom','right','insideH','insideV'):
        border=E.SubElement(borders,W+side);border.set(W+'val','single');border.set(W+'sz','4');border.set(W+'color','D9D9D9')
    margins=E.SubElement(pr,W+'tblCellMar')
    for side in('top','bottom','left','right'):
        margin=E.SubElement(margins,W+side);margin.set(W+'w','90');margin.set(W+'type','dxa')
    grid=E.SubElement(table,W+'tblGrid')
    for width in widths:E.SubElement(grid,W+'gridCol').set(W+'w',str(width))
    for index,values in enumerate([headers,*rows]):
        tr=E.SubElement(table,W+'tr');trp=E.SubElement(tr,W+'trPr');set_flag(trp,'cantSplit')
        if index==0:set_flag(trp,'tblHeader')
        for column,value in enumerate(values):
            tc=E.SubElement(tr,W+'tc');tcp=E.SubElement(tc,W+'tcPr')
            width=E.SubElement(tcp,W+'tcW');width.set(W+'w',str(widths[column]));width.set(W+'type','dxa')
            E.SubElement(tcp,W+'vAlign').set(W+'val','center');E.SubElement(tcp,W+'shd').set(W+'fill','E6EEF4'if index==0 else('FFFFFF'if index%2 else'F6F8FA'))
            p=paragraph(u,template,str(value));pp=p.find(W+'pPr')
            if pp is None:pp=E.Element(W+'pPr');p.insert(0,pp)
            for name in('pageBreakBefore','keepNext'):
                for node in pp.findall(W+name):pp.remove(node)
            set_flag(pp,'keepLines')
            if index==0:set_flag(pp,'keepNext')
            spacing=pp.find(W+'spacing')
            if spacing is None:spacing=E.SubElement(pp,W+'spacing')
            spacing.set(W+'before','30');spacing.set(W+'after','30')
            rp=p.find(W+'r').find(W+'rPr')
            if rp is None:rp=E.SubElement(p.find(W+'r'),W+'rPr')
            sz=rp.find(W+'sz')
            if sz is None:sz=E.SubElement(rp,W+'sz')
            sz.set(W+'val','19')
            if index==0:E.SubElement(rp,W+'b')
            tc.append(p)
    return table
def validate_input(closure):
    if closure.get('closed_for_authoring')is not True:raise ValueError('Scientific input is a draft; no DOCX authored')
    m=closure['manual_1_29']
    for label in('principal','candidate'):
        identity=m[label]
        if not isinstance(identity.get('life_id'),str)or not identity['life_id']or identity.get('N')!=67 or type(identity.get('tick'))is not int or identity['tick']<735843:raise ValueError('Actual final identity/cut missing:'+label)
    if not isinstance(m['principal'].get('selection'),str)or not m['principal']['selection']:raise ValueError('Selection status missing')
    required=('cover_summary','release_cut','state_of_edition','continuation_paragraph')
    for key in required:
        if not isinstance(m.get(key),str)or not m[key].strip():raise ValueError('Required final prose missing:'+key)
    if len(m.get('resume',[]))!=4:raise ValueError('Four resumption paragraphs required')
    if not m.get('chapter45_sections')or not m.get('compendium_paragraphs')or not m.get('sources'):raise ValueError('Sections/Compendium/sources missing')
    strings=[m[key]for key in required]+m['resume']+m['compendium_paragraphs']+[p for s in m['chapter45_sections']for p in s['paragraphs']]
    if any(not isinstance(s,str)or not s.strip()or'BORRADOR_NO_FINAL'in s for s in strings):raise ValueError('Unresolved draft text in closed input')
    for section in m['chapter45_sections']:
        if not section['title'].startswith('45.'):raise ValueError('Chapter45 subsection identifier required')
    return m
def main(args):
    if not args.artifact_marker_completed:raise ValueError('Root must declare the already completed documents authoring marker')
    input_path=args.input or P/'control/CIERRE_CIENTIFICO_PI02.json';input_bytes=input_path.read_bytes();closure=json.loads(input_bytes.decode('utf-8-sig'));m=validate_input(closure)
    if sha(MAN.read_bytes())!=EXPECTED_MAN or sha(COMP.read_bytes())!=EXPECTED_COMP:raise ValueError('Published1.28source changed; reconcile instead of overwriting')
    active_path=C/'sistema/estado/ACTIVO.json';active_bytes=active_path.read_bytes();active=json.loads(active_bytes.decode('utf-8-sig'))
    if active['life_id']!=m['principal']['life_id']or active['tick']!=m['principal']['tick']:raise ValueError('Closed manual principal differs from actual selector; complete adoption/reconciliation before authoring')
    u,helper_path=utilities();staged=args.staging or D/'staging_FINAL_1_29_R01';report_path=D/'ACTUALIZACION_DOCUMENTAL_PI02_FINAL_1_29.json'
    if report_path.exists():raise ValueError('Prior final authoring proof protected')
    if not staged.resolve().is_relative_to(D.resolve()):raise ValueError('Staging outside campaign documents is forbidden')
    backups={'Manual':u.preserve(MAN,D/'respaldo_1_28'),'Compendium':u.preserve(COMP,D/'respaldo_1_28')}
    cut_date=closure.get('cut_date_local')or datetime.datetime.now().astimezone().date().isoformat()
    with zipfile.ZipFile(MAN)as z:
        root=E.fromstring(z.read('word/document.xml'));body=root.find(W+'body');old=list(body);before={id(e):E.tostring(e)for e in old};allowed=set()
        heading=next(p for p in body if p.tag==W+'p'and u.text(p).startswith('44 PI02')and u.h1(p))
        h2=next(p for p in body if p.tag==W+'p'and u.text(p).startswith('44.1 '))
        ordinary=next(p for p in list(body)[list(body).index(heading)+2:]if p.tag==W+'p'and len(u.text(p))>180 and not u.h1(p)and not u.text(p).startswith('44.'))
        appendix=next(p for p in body if p.tag==W+'p'and u.text(p)=='Apéndice A. Inventario histórico de las 73 entradas'and u.h1(p))
        chapter44=old[old.index(heading):old.index(appendix)]
        prefixes=('Principal operativo:','Para el principal use','PI02 etapa A obtuvo','Se requiere snapshot completo,')
        for prefix,value in zip(prefixes,m['resume']):
            slots=[p for p in old[:60]if p.tag==W+'p'and u.text(p).startswith(prefix)]
            if len(slots)!=1:raise ValueError('Ambiguous current resumption slot:'+prefix)
            u.settext(slots[0],value,verbatim=True);allowed.add(id(slots[0]))
        for p in body:
            if p.tag!=W+'p':continue
            text=u.text(p);value=None
            if text.startswith('DEE thinking 4.5.0 |'):value=text.replace('Edición documental 1.28','Edición documental 1.29')
            elif text.startswith('Edición documental 1.28.'):value='Edición documental 1.29. '+m['cover_summary']
            elif text.startswith('Los capítulos 1–43 y los apéndices'):value='Los capítulos 1–44 y los apéndices conservan sus hechos y cortes históricos. El capítulo 44 corresponde a la edición intermedia 1.28 y el 45 incorpora el cierre posterior de PI02, con controles, asistencia, pérdidas e incorporación efectiva. No se fusionan historias divergentes.'
            elif'Su edición vigente 1.28'in text:value=text.replace('Su edición vigente 1.28','Su edición vigente 1.29')
            elif text.startswith('Para retomar, lea el punto inicial'):value=m['continuation_paragraph']
            if value is not None:u.settext(p,value,verbatim=True);allowed.add(id(p))
        control=next(table for table in body.findall(W+'tbl')if any(u.text(row.findall(W+'tc')[0])=='Documento'for row in table.findall(W+'tr')if row.findall(W+'tc')));allowed.add(id(control))
        values={'Documento':'DCS11-MM-001 / Edición documental 1.29 / Cierre PI02 / '+cut_date,
            'Corte de liberación registrado':m['release_cut'],
            'Base principal':'Mismo Manual rector y nombre operativo 1_21 por compatibilidad. La edición 1.28 completa y el Compendio anterior se preservan en respaldo_1_28 con hashes. El capítulo 44 mantiene literalmente el corte histórico de etapa A; el 45 añade el cierre posterior de la misma campaña.',
            'Estado de esta edición':m['state_of_edition']}
        found=set()
        for row in control.findall(W+'tr'):
            cells=row.findall(W+'tc')
            if len(cells)>=2 and u.text(cells[0])in values:
                key=u.text(cells[0]);u.settext(cells[1].find(W+'p'),values[key],verbatim=True);found.add(key)
        if found!=set(values):raise ValueError('Current documentary control slots changed')
        title=paragraph(u,heading,TITLE);u.insert_bookmark(root,title,'PI02_CIERRE');appendix.addprevious(title)
        introduction='Este capítulo cierra la progresión posterior al corte A. La edición 1.28 se publicó con PI01 como principal y la candidata en el corte científico A T740343. Ese pasado permanece en el capítulo 44; los cortes, resultados y selección siguientes pertenecen al cierre real de la misma campaña, sin restaurar aquel estado ni sumar experiencias de los controles.'
        appendix.addprevious(paragraph(u,ordinary,introduction))
        for section in m['chapter45_sections']:
            appendix.addprevious(paragraph(u,h2,section['title']))
            for value in section['paragraphs']:appendix.addprevious(paragraph(u,ordinary,value))
            if section.get('optional_table'):appendix.addprevious(make_table(u,ordinary,section['optional_table']))
            for lines in section.get('commands',[]):appendix.addprevious(command_block(u,ordinary,lines))
        appendix.addprevious(paragraph(u,ordinary,'Fuentes del cierre: '+'; '.join(m['sources'])+'. Los localizadores corresponden a registros privados ya producidos; el documento no ejecuta los comandos ni convierte al atlas del auditor en memoria del ente.'))
        index=next(p for p in old if p.tag==W+'p'and u.text(p).startswith('44 PI02')and not u.h1(p));index.addnext(u.index_entry(index,TITLE,'PI02_CIERRE'))
        protected=0
        for element in old:
            if id(element)not in allowed:
                if element.getparent()is not body or E.tostring(element)!=before[id(element)]:raise ValueError('Unapproved historical body rewrite')
                protected+=1
        if any(E.tostring(element)!=before[id(element)]for element in chapter44):raise ValueError('StageA chapter44 must remain literal')
        if'rechazos.Conservación'in u.text(control):raise ValueError('Known documentary punctuation issue remains')
        edits={'word/document.xml':u.xml(root)}
        for name in z.namelist():
            if not re.fullmatch(r'word/(header|footer)\d+\.xml',name):continue
            data=z.read(name);part=E.fromstring(data);changed=False
            for t in part.iter(W+'t'):
                if t.text:
                    after=t.text.replace('ED. 1.28','ED. 1.29').replace('Ed. documental 1.28','Ed. documental 1.29').replace('PI02 etapa A','PI02 cierre');changed=changed or after!=t.text;t.text=after
            candidate=u.xml(part)
            if u.fields(data)!=u.fields(candidate):raise ValueError('Header/footer field instructions changed')
            if changed:edits[name]=candidate
        core=E.fromstring(z.read('docProps/core.xml'));CP='{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}';DC='{http://purl.org/dc/elements/1.1/}';DT='{http://purl.org/dc/terms/}'
        for tag,value in((DC+'title','DEE Cognitive 2.0 Manual Maestro Edición 1.29 Cierre PI02'),(CP+'revision','29'),(DT+'modified',datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'))):
            child=core.find(tag)
            if child is None:child=E.SubElement(core,tag)
            child.text=value
        edits['docProps/core.xml']=u.xml(core)
    manual=u.package(MAN,staged/NAME,edits);manual.update(internal_edition='1.29',source_body_elements=len(old),protected_body_elements_exact=protected,editorial_body_elements_changed=len(allowed),chapter44_stageA_preserved=True,publication_status='STAGED_ONLY_RENDER_AND_QA_PENDING')
    with zipfile.ZipFile(COMP)as z:
        root=E.fromstring(z.read('word/document.xml'));body=root.find(W+'body');old=list(body);before={id(e):E.tostring(e)for e in old};ps=[p for p in old if p.tag==W+'p'];heading=next(p for p in ps if u.h1(p));ordinary=next(p for p in ps if len(u.text(p))>180 and not u.h1(p));sec=body.find(W+'sectPr')
        title=paragraph(u,heading,'Cierre PI02 y continuidad documentada en Manual 1.29');u.insert_bookmark(root,title,'PI02_CIERRE_COMPENDIO')
        additions=[title]+[paragraph(u,ordinary,value)for value in m['compendium_paragraphs']]
        additions.append(paragraph(u,ordinary,'Corte principal del cierre: '+m['principal']['life_id']+', N'+str(m['principal']['N'])+', T'+str(m['principal']['tick'])+', selección '+m['principal']['selection']+'. Fuentes: '+'; '.join(m['sources'])+'.'))
        for node in additions:
            if sec is not None:sec.addprevious(node)
            else:body.append(node)
        index=next(p for p in ps if u.text(p).startswith('Actualización PI02 etapa A')and not u.h1(p));index.addnext(u.index_entry(index,'Cierre PI02 y continuidad final','PI02_CIERRE_COMPENDIO'))
        if any(e.getparent()is not body or E.tostring(e)!=before[id(e)]for e in old):raise ValueError('Compendium historical content changed')
        comp=u.package(COMP,staged/COMP.name,{'word/document.xml':u.xml(root)});comp.update(source_body_elements=len(old),protected_body_elements_exact=len(old),new_body_elements=len(additions)+1,publication_status='STAGED_ONLY_RENDER_AND_QA_PENDING')
    if sha(MAN.read_bytes())!=EXPECTED_MAN or sha(COMP.read_bytes())!=EXPECTED_COMP or active_path.read_bytes()!=active_bytes or input_path.read_bytes()!=input_bytes:raise ValueError('Original/selector/scientific input changed during authoring')
    report={'schema':'PI02.final.editorial_staging.1.29.v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'Manual':manual,'Compendium':comp,'literal_prior_documents':backups,
        'closed_scientific_input':{'path':str(input_path),'bytes':len(input_bytes),'sha256':sha(input_bytes)},'authoring_helpers':{'path':str(helper_path),'sha256':sha(helper_path.read_bytes())},
        'principal_matches_current_ACTIVO_at_staging':m['principal'],'candidate_cut_from_closed_science':m['candidate'],'ACTIVO_sha256':sha(active_bytes),'stageA_chapter44_preserved_literal':True,
        'originals_modified':False,'new_native_ticks':0,'engine_imports':0,'adoption_performed_by_this_editor':False,'rendering_and_visual_QA':'PENDING; neither publication nor visual approval is claimed by staging.'}
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'proof':str(report_path),'Manual':manual,'Compendium':comp},ensure_ascii=False,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--artifact-marker-completed',action='store_true');parser.add_argument('--input',type=Path);parser.add_argument('--staging',type=Path);main(parser.parse_args())
