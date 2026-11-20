"""Same logical manual1.16->1.17 from reviewed closed APD03 results; no DEE."""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import hashlib,json,os
from pathlib import Path
import shutil,subprocess,sys,tempfile
from zipfile import ZipFile
from lxml import etree as E
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).parent
BASE_NAME='DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_16_APD02_CONTINUIDAD_CALIDAD_SIN_VALIDACION_VISUAL.docx'
OUT_NAME='DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_17_APD03_AUTONOMIA_DESARROLLO_SIN_VALIDACION_VISUAL.docx'
BASE_SHA='8ef2f084621693b4a0d3d97fa6b7586ce402b7f0b6b7823680732945be39b855'
SKILL=Path(r'C:\Users\Erik\.codex\plugins\cache\openai-primary-runtime\documents\26.1011.51657\skills\documents')
TITLE='34 Autonomía práctica desarrollo y uso independiente'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def text(p):return ''.join(n.text or '' for n in p.iter(W+'t'))
def style(p):
    n=p.find(f'{W}pPr/{W}pStyle');return n.get(W+'val','') if n is not None else ''
def put(p,value):
    if list(p.iter(W+'instrText')):raise ValueError('Do not replace a field paragraph')
    r=p.find(W+'r');rp=deepcopy(r.find(W+'rPr')) if r is not None and r.find(W+'rPr') is not None else None
    for n in list(p):
        if n.tag!=W+'pPr':p.remove(n)
    r=E.SubElement(p,W+'r')
    if rp is not None:r.append(rp)
    for i,line in enumerate(value.split('\n')):
        if i:E.SubElement(r,W+'br')
        t=E.SubElement(r,W+'t');t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=line
def para(st,value):
    p=E.Element(W+'p');pr=E.SubElement(p,W+'pPr');E.SubElement(pr,W+'pStyle').set(W+'val',st);put(p,value);return p
def table(rows):
    if not rows or any(len(row)!=3 for row in rows):raise ValueError('Compact three-column life/scope/assistance matrix required')
    widths=[1600,4467,3600];tbl=E.Element(W+'tbl');pr=E.SubElement(tbl,W+'tblPr')
    E.SubElement(pr,W+'tblW',attrib={W+'w':'9667',W+'type':'dxa'})
    borders=E.SubElement(pr,W+'tblBorders')
    for side in('top','left','bottom','right','insideH','insideV'):E.SubElement(borders,W+side,attrib={W+'val':'single',W+'sz':'4',W+'color':'D9D9D9'})
    E.SubElement(pr,W+'tblLayout').set(W+'type','fixed')
    margins=E.SubElement(pr,W+'tblCellMar')
    for side in('top','left','bottom','right'):E.SubElement(margins,W+side,attrib={W+'w':'110',W+'type':'dxa'})
    grid=E.SubElement(tbl,W+'tblGrid')
    for width in widths:E.SubElement(grid,W+'gridCol').set(W+'w',str(width))
    for i,row in enumerate(rows):
        tr=E.SubElement(tbl,W+'tr')
        if i==0:E.SubElement(E.SubElement(tr,W+'trPr'),W+'tblHeader')
        for j,value in enumerate(row):
            tc=E.SubElement(tr,W+'tc');tp=E.SubElement(tc,W+'tcPr');E.SubElement(tp,W+'tcW',attrib={W+'w':str(widths[j]),W+'type':'dxa'})
            E.SubElement(tp,W+'shd',attrib={W+'fill':'16324F'if i==0 else('F1F5F9'if i%2==0 else'FFFFFF'),W+'val':'clear'})
            E.SubElement(tp,W+'vAlign').set(W+'val','center')
            p=para('Normal',str(value));tc.append(p)
            pp=p.find(W+'pPr');E.SubElement(pp,W+'spacing',attrib={W+'before':'40',W+'after':'60',W+'line':'264',W+'lineRule':'auto'})
            if i==0:E.SubElement(pp,W+'jc').set(W+'val','center')
            for run in p.findall(W+'r'):
                rp=E.Element(W+'rPr');run.insert(0,rp)
                if i==0:E.SubElement(rp,W+'b')
                E.SubElement(rp,W+'color').set(W+'val','FFFFFF'if i==0 else'000000');E.SubElement(rp,W+'sz').set(W+'val','22')
    return tbl
def parts(path):
    with ZipFile(path) as z:
        assert z.testzip() is None
        return z.infolist(),{n:z.read(n) for n in z.namelist()}
def fields(ps):return {n:[x.text for x in E.fromstring(v).iter(W+'instrText')] for n,v in ps.items() if n.endswith('.xml') and n.startswith(('word/document','word/header','word/footer'))}
def historical(d):
    values=[];on=False
    for p in d.find(W+'body'):
        if p.tag==W+'p' and style(p)=='Heading1':
            if text(p).startswith('20. '):on=True
            if text(p).startswith(('34 ','Apéndice A.')):break
        if on:values.append(E.tostring(p))
    return values
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True);ap.add_argument('--try-render',action='store_true');args=ap.parse_args()
    data=json.loads(args.results.read_text(encoding='utf-8'));assert data['status']=='FINAL_RESULTS_APPROVED_FOR_MANUAL'
    approved_text=json.dumps({k:data[k] for k in('inline_replacements','method_additions','chapter')},ensure_ascii=False)
    assert '{{' not in approved_text and '}}' not in approved_text,'Unresolved scientific placeholders must never enter the Word edition'
    src=ROOT/BASE_NAME;out=ROOT/OUT_NAME;assert sha(src)==BASE_SHA
    if out.exists():raise FileExistsError(out)
    infos,base=parts(src);members=dict(base);d=E.fromstring(base['word/document.xml']);body=d.find(W+'body')
    replacements=data['inline_replacements'];normalized={k.replace('\n',''):k for k in replacements};seen={};changes=[]
    assert len(normalized)==len(replacements),'Ambiguous line-break-normalized source keys'
    for p in list(d.iter(W+'p')):
        old=text(p);key=normalized.get(old);new=replacements.get(key)
        if new is not None:
            put(p,new);changes.append({'old':old,'new':new});seen[key]=seen.get(key,0)+1
    assert set(seen)==set(replacements),set(replacements)-set(seen)
    # Repeated headings may have one TOC line and one actual heading, intentionally.
    assert all(n in(1,2) for n in seen.values()),seen
    for heading,items in data.get('method_additions',{}).items():
        nodes=list(body);at=next(i for i,p in enumerate(nodes) if p.tag==W+'p' and style(p)=='Heading1' and text(p)==heading)
        end=next((i for i in range(at+1,len(nodes)) if nodes[i].tag==W+'p' and style(nodes[i])=='Heading1'),len(nodes))
        pos=next((i for i in range(at+1,end) if nodes[i].tag==W+'p' and style(nodes[i])=='Source'),end)
        for j,item in enumerate(items):body.insert(pos+j,para(item['style'],item['text']))
    toc=next(p for p in body if p.tag==W+'p' and style(p)=='TOCline' and text(p).startswith('Apéndice A.'))
    body.insert(list(body).index(toc),para('TOCline',TITLE))
    app=next(p for p in body if p.tag==W+'p' and style(p)=='Heading1' and text(p).startswith('Apéndice A.'))
    chapter=[para('Heading1',TITLE)]
    for item in data['chapter']:
        if item.get('type')=='table':chapter.append(table(item['rows']));continue
        assert item['style'] in('Heading2','Heading3','Normal','Code','Source','Small')
        chapter.append(para(item['style'],item['text']))
    at=list(body).index(app)
    for j,p in enumerate(chapter):body.insert(at+j,p)
    members['word/document.xml']=E.tostring(d,xml_declaration=True,encoding='UTF-8',standalone=True)
    for name in('word/header1.xml','word/footer1.xml'):
        tree=E.fromstring(members[name])
        for n in tree.iter(W+'t'):
            if n.text:n.text=n.text.replace('DOCUMENTAL 1.16','DOCUMENTAL 1.17').replace('documental 1.16','documental 1.17')
        members[name]=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
    c=E.fromstring(members['docProps/core.xml'])
    for n in c:
        if n.tag.endswith('}title'):n.text='DEE Cognitive System 1.1 Manual Maestro Edicion 1.17 Autonomia practica y desarrollo'
        if n.tag.endswith('}subject'):n.text='APD03_MAIN entrada unica seleccion dependiente de consecuencias y desarrollo acotado'
        if n.tag.endswith('}version'):n.text='1.17 documental / software1.1.0'
        if n.tag.endswith('}revision'):n.text=str(int(n.text or '0')+1)
        if n.tag.endswith('}modified'):n.text=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    members['docProps/core.xml']=E.tostring(c,xml_declaration=True,encoding='UTF-8',standalone=True)
    with ZipFile(out,'w') as z:
        for i in infos:z.writestr(i,members[i.filename])
    _,final=parts(out);fd=E.fromstring(final['word/document.xml']);bd=E.fromstring(base['word/document.xml'])
    changed=[n for n in base if base[n]!=final[n]]
    assert base.keys()==final.keys()
    assert set(changed)<={'word/document.xml','word/header1.xml','word/footer1.xml','docProps/core.xml'}
    assert fields(base)==fields(final)
    final_core=E.fromstring(final['docProps/core.xml'])
    assert next(n.text for n in final_core if n.tag.endswith('}version'))=='1.17 documental / software1.1.0'
    assert E.fromstring(final['word/settings.xml']).find(W+'updateFields').get(W+'val')=='true'
    assert [E.tostring(x) for x in bd.iter(W+'sectPr')]==[E.tostring(x) for x in fd.iter(W+'sectPr')]
    previous_history=historical(bd);current_history=historical(fd)
    assert len(previous_history)>100,'Historical preservation check did not find chapters20–33'
    assert previous_history==current_history,'Scientific historical chapters20–33 were changed'
    archive=ROOT/'documentos/historico_manuales'/BASE_NAME
    assert src.resolve().parent==ROOT.resolve()
    assert archive.resolve().is_relative_to(ROOT.resolve()) and archive.parent.is_dir()
    if archive.exists():raise FileExistsError(archive)
    shutil.move(str(src),str(archive));assert sha(archive)==BASE_SHA
    assert list(ROOT.glob('DEE_Cognitive_System_1_1_Manual_Maestro*.docx'))==[out]
    report={'schema':'APD03.manual.edition.v1','document':str(out),'sha256':sha(out),'bytes':out.stat().st_size,'baseline':str(archive),'baseline_sha256':BASE_SHA,'changed_parts':changed,'unchanged_members':len(base)-len(changed),'geometry_preserved':True,'fields_preserved_not_refreshed_by_XML':True,'history_chapters20_33_preserved':True,'unique_current_manual':True,'native_ticks':0,'changes':changes,'results_source':str(args.results.resolve()),'results_sha256':sha(args.results),'visual_validation':'NOT_ATTEMPTED'}
    if args.try_render:
        deps=Path(sys.executable).parent.parent;env=os.environ.copy();env['PATH']=os.pathsep.join(map(str,[Path(sys.executable).parent,deps/'bin/override',deps/'bin/fallback',deps/'native/poppler/bin']));env['PYTHONIOENCODING']='utf-8'
        work=Path(tempfile.mkdtemp(prefix='dee_apd03_docx_qa_'));render_input=work/'manual.docx';shutil.copyfile(out,render_input);assert sha(render_input)==sha(out)
        target=work/'render';cmd=[sys.executable,str(SKILL/'render_docx.py'),str(render_input),'--output_dir',str(target),'--emit_pdf','--verbose']
        report['render_source_copy']={'path':str(render_input),'sha256':sha(render_input),'identical_to_final_Word':True,'reason':'Short temporary QA path only; not another document authority or edition.'}
        try:
            render_cwd=Path(tempfile.gettempdir()).resolve(strict=True)
            p=subprocess.run(cmd,cwd=render_cwd,env=env,capture_output=True,encoding='utf-8',errors='replace',timeout=50)
            report['render']={'command':cmd,'cwd':str(render_cwd),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'authorized_PATH':env['PATH']}
        except subprocess.TimeoutExpired as exc:report['render']={'command':cmd,'timeout_seconds':50,'stdout':str(exc.stdout),'stderr':str(exc.stderr),'authorized_PATH':env['PATH']}
        except OSError as exc:report['render']={'command':cmd,'error_type':type(exc).__name__,'error':str(exc),'authorized_PATH':env['PATH']}
        pages=list(target.glob('page-*.png'));report['render']['pages']=[str(x) for x in pages];report['visual_validation']='PAGES_REQUIRE_FULL_REVIEW' if pages else 'NOT_AVAILABLE_RENDER_FAILED'
    (HERE/'EDICION_MANUAL_APD03.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in('document','sha256','bytes','visual_validation','native_ticks')},ensure_ascii=True))
if __name__=='__main__':main()
