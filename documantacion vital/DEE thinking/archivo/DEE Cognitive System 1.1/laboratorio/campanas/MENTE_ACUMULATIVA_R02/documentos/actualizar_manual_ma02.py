"""Same logical manual 1.12 -> 1.13 from an approved actual cut. No DEE imports."""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import hashlib,json,os
from pathlib import Path
import shutil,subprocess,sys
from zipfile import ZipFile
from lxml import etree as E
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).parent
BASE_NAME='DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_12_MENTE_ACUMULATIVA_SIN_VALIDACION_VISUAL.docx'
OUT_NAME='DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_13_MENTE_ACUMULATIVA_R02_SIN_VALIDACION_VISUAL.docx'
BASE_SHA='a393df3f85ba3d24b2f7e11a366f02d9cb5de12b1e2c9a061b6137c6256892b0'
SKILL=Path(r'C:\Users\Erik\.codex\plugins\cache\openai-primary-runtime\documents\26.1011.51657\skills\documents')
TITLE='30 Interacciones útiles acceso repetible y desarrollo acumulativo'
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
            if text(p).startswith(('30 ','Apéndice A.')):break
        if on:values.append(E.tostring(p))
    return values
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True);ap.add_argument('--try-render',action='store_true');args=ap.parse_args()
    data=json.loads(args.results.read_text(encoding='utf-8'));assert data['status']=='FINAL_RESULTS_APPROVED_FOR_MANUAL'
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
        assert item['style'] in('Heading2','Heading3','Normal','Code','Source','Small')
        chapter.append(para(item['style'],item['text']))
    at=list(body).index(app)
    for j,p in enumerate(chapter):body.insert(at+j,p)
    members['word/document.xml']=E.tostring(d,xml_declaration=True,encoding='UTF-8',standalone=True)
    for name in('word/header1.xml','word/footer1.xml'):
        tree=E.fromstring(members[name])
        for n in tree.iter(W+'t'):
            if n.text:n.text=n.text.replace('DOCUMENTAL 1.12','DOCUMENTAL 1.13').replace('documental 1.12','documental 1.13')
        members[name]=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
    c=E.fromstring(members['docProps/core.xml'])
    for n in c:
        if n.tag.endswith('}title'):n.text='DEE Cognitive System 1.1 Manual Maestro Edicion 1.13 Mente Acumulativa R02'
        if n.tag.endswith('}modified'):n.text=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    members['docProps/core.xml']=E.tostring(c,xml_declaration=True,encoding='UTF-8',standalone=True)
    with ZipFile(out,'w') as z:
        for i in infos:z.writestr(i,members[i.filename])
    _,final=parts(out);fd=E.fromstring(final['word/document.xml']);bd=E.fromstring(base['word/document.xml'])
    changed=[n for n in base if base[n]!=final[n]]
    assert base.keys()==final.keys()
    assert set(changed)<={'word/document.xml','word/header1.xml','word/footer1.xml','docProps/core.xml'}
    assert fields(base)==fields(final)
    assert [E.tostring(x) for x in bd.iter(W+'sectPr')]==[E.tostring(x) for x in fd.iter(W+'sectPr')]
    assert historical(bd)==historical(fd),'Scientific chapters20–29 were changed'
    archive=ROOT/'documentos/historico_manuales'/BASE_NAME
    if archive.exists():raise FileExistsError(archive)
    shutil.move(str(src),str(archive));assert sha(archive)==BASE_SHA
    assert list(ROOT.glob('DEE_Cognitive_System_1_1_Manual_Maestro*.docx'))==[out]
    report={'schema':'MA02.manual.edition.v1','document':str(out),'sha256':sha(out),'bytes':out.stat().st_size,'baseline':str(archive),'baseline_sha256':BASE_SHA,'changed_parts':changed,'unchanged_members':len(base)-len(changed),'geometry_preserved':True,'fields_preserved':True,'history_chapters20_29_preserved':True,'unique_current_manual':True,'native_ticks':0,'changes':changes,'results_source':str(args.results.resolve()),'results_sha256':sha(args.results),'visual_validation':'NOT_ATTEMPTED'}
    if args.try_render:
        deps=Path(sys.executable).parent.parent;env=os.environ.copy();env['PATH']=os.pathsep.join(map(str,[Path(sys.executable).parent,deps/'bin/override',deps/'bin/fallback',deps/'native/poppler/bin']));env['PYTHONIOENCODING']='utf-8'
        target=HERE/'render_final';cmd=[sys.executable,str(SKILL/'render_docx.py'),str(out),'--output_dir',str(target),'--emit_pdf','--verbose']
        try:
            p=subprocess.run(cmd,cwd=HERE,env=env,capture_output=True,encoding='utf-8',errors='replace',timeout=50)
            report['render']={'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'authorized_PATH':env['PATH']}
        except subprocess.TimeoutExpired as exc:report['render']={'command':cmd,'timeout_seconds':50,'stdout':str(exc.stdout),'stderr':str(exc.stderr),'authorized_PATH':env['PATH']}
        pages=list(target.glob('page-*.png'));report['render']['pages']=[str(x) for x in pages];report['visual_validation']='PAGES_REQUIRE_FULL_REVIEW' if pages else 'NOT_AVAILABLE_RENDER_FAILED'
    (HERE/'EDICION_MANUAL_MA02.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in('document','sha256','bytes','visual_validation','native_ticks')},ensure_ascii=True))
if __name__=='__main__':main()
