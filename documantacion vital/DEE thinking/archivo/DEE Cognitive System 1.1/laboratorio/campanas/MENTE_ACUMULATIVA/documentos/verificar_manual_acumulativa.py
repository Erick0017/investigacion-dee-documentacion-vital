"""Preservation checks and one bounded packaged-render attempt; no DEE imports."""
from __future__ import annotations
import argparse, hashlib, json, os
from pathlib import Path
import subprocess, sys
from zipfile import ZipFile
from lxml import etree as E
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'documentos/historico_manuales/DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_11_R1_ENTE02_SIN_VALIDACION_VISUAL.docx'
OUT=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_12_MENTE_ACUMULATIVA_SIN_VALIDACION_VISUAL.docx'
SKILL=Path(r'C:\Users\Erik\.codex\plugins\cache\openai-primary-runtime\documents\26.1011.51657\skills\documents')
def text(p):return ''.join(n.text or '' for n in p.iter(W+'t'))
def style(p):
    n=p.find(f'{W}pPr/{W}pStyle');return n.get(W+'val','') if n is not None else ''
def get(p):
    with ZipFile(p) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(set(z.namelist()))
        return {n:z.read(n) for n in z.namelist()}
def fields(parts):return {n:[x.text for x in E.fromstring(b).iter(W+'instrText')] for n,b in parts.items() if n.endswith('.xml') and n.startswith(('word/document','word/header','word/footer'))}
def history(doc):
    b=list(doc.find(W+'body')); start=next(i for i,p in enumerate(b) if p.tag==W+'p' and style(p)=='Heading1' and text(p).startswith('20. '))
    end=next((i for i in range(start+1,len(b)) if b[i].tag==W+'p' and style(b[i])=='Heading1' and text(b[i]).startswith('29 ')),len(b))
    return [E.tostring(x) for x in b[start:end]]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True);ap.add_argument('--try-render',action='store_true');args=ap.parse_args()
    out=Path(__file__).parent/('qa_'+args.stage);out.mkdir(exist_ok=False)
    a,b=get(BASE),get(OUT);assert a.keys()==b.keys()
    da,db=E.fromstring(a['word/document.xml']),E.fromstring(b['word/document.xml'])
    changed=[n for n in a if a[n]!=b[n]]
    assert set(changed)<={'word/document.xml','word/header1.xml','word/footer1.xml','docProps/core.xml','word/settings.xml'}
    assert [E.tostring(x) for x in da.iter(W+'sectPr')]==[E.tostring(x) for x in db.iter(W+'sectPr')]
    assert fields(a)==fields(b)
    # Scientific chapters 20–28 must remain identical, excluding a new final chapter.
    aa=history(da);bb=history(db)
    if args.stage=='inicio':assert aa==bb
    else:
        # Compare only before appendix, where the final chapter is inserted.
        def old_chapters(d):
            values=[];active=False
            for n in d.find(W+'body'):
                if n.tag==W+'p' and style(n)=='Heading1':
                    if text(n).startswith('20. '):active=True
                    if text(n).startswith(('29 ','Apéndice A.')):break
                if active:values.append(E.tostring(n))
            return values
        assert old_chapters(da)==old_chapters(db)
    whole='\n'.join(text(x) for x in db.iter(W+'p'))
    for s in ('Edición documental 1.12','Desarrollo acumulativo de una línea principal','Capacidad utilizable y conocimiento de una vida','Retención y evaluación del uso','Incorporación proporcional durante el desarrollo','Uso situado de señales y herramientas','Continuación seleccionada y límites del relevo','Una autoridad documental y un cierre finito'):
        assert s in whole,s
    current=list(ROOT.glob('DEE_Cognitive_System_1_1_Manual_Maestro*.docx'));assert current==[OUT],current
    report={'schema':'MENTE_ACUMULATIVA.manual.qa.v1','stage':args.stage,'document':str(OUT),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'bytes':OUT.stat().st_size,'baseline_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'members':len(b),'unchanged_members':len(b)-len(changed),'changed_parts':changed,'geometry_preserved':True,'fields_preserved':True,'scientific_history_20_28_preserved':True,'unique_current_manual':True,'native_ticks':0,'visual_validation':'NOT_ATTEMPTED'}
    if args.try_render:
        deps=Path(sys.executable).parent.parent;env=os.environ.copy();env['PATH']=os.pathsep.join(map(str,[Path(sys.executable).parent,deps/'bin/override',deps/'bin/fallback',deps/'native/poppler/bin']));env['PYTHONIOENCODING']='utf-8'
        command=[sys.executable,str(SKILL/'render_docx.py'),str(OUT),'--output_dir',str(out/'render'),'--emit_pdf','--verbose']
        try:
            p=subprocess.run(command,cwd=out,env=env,capture_output=True,encoding='utf-8',errors='replace',timeout=50)
            report['render']={'command':command,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'authorized_PATH':env['PATH']}
        except subprocess.TimeoutExpired as exc:report['render']={'command':command,'timeout_seconds':50,'stdout':str(exc.stdout),'stderr':str(exc.stderr),'authorized_PATH':env['PATH']}
        pages=list((out/'render').glob('page-*.png'));report['render']['pages']=[str(x) for x in pages];report['visual_validation']='PAGES_REQUIRE_REVIEW' if pages else 'NOT_AVAILABLE_RENDER_FAILED'
    target=out/'VERIFICACION_MANUAL.json';target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('document','sha256','bytes','changed_parts','visual_validation')},ensure_ascii=True))
if __name__=='__main__':main()
