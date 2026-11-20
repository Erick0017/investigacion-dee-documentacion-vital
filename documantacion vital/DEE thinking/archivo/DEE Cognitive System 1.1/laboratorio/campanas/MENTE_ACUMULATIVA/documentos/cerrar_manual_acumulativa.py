"""Close the same 1.12 logical Word from approved actual result data. Zero DEE ticks."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib, json
from pathlib import Path
import shutil
from zipfile import ZipFile
from lxml import etree as E
from actualizar_manual_acumulativa import ROOT, HERE, NAME, W, txt, sty, put, para, digest

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--results',required=True,type=Path);args=ap.parse_args()
    data=json.loads(args.results.read_text(encoding='utf-8'))
    assert data['status']=='FINAL_RESULTS_APPROVED_FOR_MANUAL'
    path=ROOT/NAME
    initial=json.loads((HERE/'EDICION_INICIAL_1_12.json').read_text(encoding='utf-8'))
    assert digest(path)==initial['sha256'],'Current manual changed after its initial edit'
    history=ROOT/'documentos/historico_manuales'/('DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_12_REVISION_INICIO_'+initial['sha256'][:12]+'.docx')
    if history.exists():raise FileExistsError(history)
    shutil.copy2(path,history);assert digest(history)==initial['sha256']
    with ZipFile(path) as z:
        infos=z.infolist();members={i.filename:z.read(i.filename) for i in infos}
    d=E.fromstring(members['word/document.xml']);body=d.find(W+'body');changes=[]
    for p in list(d.iter(W+'p')):
        old=txt(p);new=None
        if old.startswith('Edición 1.12 con metodología acumulativa integrada'):
            new=data['cover']
        elif old.startswith('24/10/2026 UTC; EO02_MAIN T169383 continúa'):
            new=data['control_cut']
        elif old.startswith('Edición 1.11 R1 ENTE02 preservada; metodología acumulativa incorporada'):
            new='Edición 1.11 R1 ENTE02 y revisión inicial 1.12 preservadas en el archivo histórico; metodología y resultados comprobados de MENTE_ACUMULATIVA integrados en este mismo Manual Maestro.'
        elif old.startswith('Word actualizado y estructura comprobada. La validación visual y el intento del renderizador autorizado'):
            new='Word 1.12 actualizado y comprobado estructuralmente. El renderizador autorizado no encontró soffice.exe; no se dispone de páginas para validar visualmente esta edición. El comprobante editorial conserva el intento y sus límites.'
        elif old.startswith('Este Manual Maestro conserva la genealogía desde el resumen funcional'):
            new=old.replace('No añade aprendizajes por el solo cambio editorial.','El capítulo 29 identifica la nueva continuación seleccionada, lo ejecutado y sus límites. Ningún aprendizaje se atribuye por el solo cambio editorial.')
        elif old.startswith('Los capítulos 20 a 28 conservan sus cortes científicos.'):
            new=data['current_scope']
        elif old.startswith('El software permanece en la capa Cognitive 1.1.0;'):
            new='El software permanece en la capa Cognitive 1.1.0; DEE thinking 4.5.0 y Universe v27 siguen congelados. La edición documental vigente es 1.12. MENTE_ACUMULATIVA añade exclusivamente los procedimientos, estados y resultados limitados identificados en el capítulo 29; no fusiona las historias de las vidas.'
        elif old.startswith('Las ediciones 1.5 a 1.9 incorporaron Integración Situada'):
            new=old.replace('El cierre de la nueva ejecución actualizará este mismo Word sólo con resultados comprobados.','El cierre actualiza este mismo Word con el corte real y los resultados comprobados descritos en el capítulo 29.')
        if old in data.get('inline_replacements',{}):new=data['inline_replacements'][old]
        if new is not None:
            put(p,new);changes.append({'old':old,'new':new})
    heading='29 Desarrollo cognitivo acumulativo y continuidad seleccionada'
    if any(txt(p)==heading for p in body if p.tag==W+'p'):raise AssertionError('Final chapter already present')
    toc=next(p for p in body if p.tag==W+'p' and sty(p)=='TOCline' and txt(p).startswith('Apéndice A.'))
    body.insert(list(body).index(toc),para('TOCline',heading))
    app=next(p for p in body if p.tag==W+'p' and sty(p)=='Heading1' and txt(p).startswith('Apéndice A.'))
    nodes=[para('Heading1',heading)]
    for item in data['chapter']:
        assert item['style'] in {'Heading2','Heading3','Normal','Source','Small','Code'}
        nodes.append(para(item['style'],item['text']))
    index=list(body).index(app)
    for j,n in enumerate(nodes):body.insert(index+j,n)
    members['word/document.xml']=E.tostring(d,xml_declaration=True,encoding='UTF-8',standalone=True)
    c=E.fromstring(members['docProps/core.xml'])
    for n in c:
        if n.tag.endswith('}modified'):n.text=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    members['docProps/core.xml']=E.tostring(c,xml_declaration=True,encoding='UTF-8',standalone=True)
    temp=path.with_name(path.stem+'.closing.tmp.docx')
    with ZipFile(temp,'w') as z:
        for info in infos:z.writestr(info,members[info.filename])
    with ZipFile(temp) as z:assert z.testzip() is None
    temp.replace(path)
    proof={'schema':'MENTE_ACUMULATIVA.manual.final.v1','stage':'CORTE_REAL_CERRADO','document':str(path),'sha256':digest(path),'bytes':path.stat().st_size,'initial_revision':str(history),'initial_sha256':initial['sha256'],'changes':changes,'chapter_items':len(data['chapter']),'results':str(args.results.resolve()),'results_sha256':digest(args.results),'native_ticks':0,'visual_validation':'NOT_AVAILABLE_RENDER_FAILED'}
    (HERE/'EDICION_FINAL_1_12.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:proof[k] for k in ('document','sha256','bytes','native_ticks')},ensure_ascii=True))
if __name__=='__main__':main()
