"""AST/OOXML-anchor checks only; no document authoring or product writes."""
from pathlib import Path
import ast, hashlib, json, zipfile
import xml.etree.ElementTree as E


def main():
    p7=Path(__file__).resolve().parents[1];r=p7.parents[2];c=r/'DEE Cognitive 2.0'
    w='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    files={c/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx':
           '55f77c470b2b442e8fce341dd0eb9d669a6e8e565d35b9ca9f3236f34459922d',
           r/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx':
           '34ae6c7eddb0a72afa846c720eaa0b1b30d990a354350d67d5402d00978aa559'}
    proofs=[]
    def text(e):return''.join(x.text or''for x in e.iter(w+'t'))
    def h1(e):
        n=e.find(w+'pPr/'+w+'pStyle')
        return n is not None and n.get(w+'val','').lower()in('heading1','ttulo1','titulo1','title1')
    for index,(p,expected)in enumerate(files.items()):
        b=p.read_bytes();digest=hashlib.sha256(b).hexdigest();assert digest==expected
        with zipfile.ZipFile(p)as z:
            assert z.testzip()is None
            root=E.fromstring(z.read('word/document.xml'));body=root.find(w+'body');top=list(body)
            if index==0:
                checks={
                    'actual_H1_ch49':sum(e.tag==w+'p'and h1(e)and text(e).startswith('49 PI06 ')for e in top),
                    'style_source_49_1':sum(e.tag==w+'p'and text(e).startswith('49.1 ')for e in top),
                    'index_ch49':sum(e.tag==w+'p'and not h1(e)and text(e)=='49 PI06 Organización endógena y robustez funcional'for e in top),
                    'real_H1_appendix_A':sum(e.tag==w+'p'and h1(e)and text(e)=='Apéndice A. Inventario histórico de las 73 entradas'for e in top),
                    'existing_H1_ch50':sum(e.tag==w+'p'and h1(e)and text(e).startswith('50 PI07 ')for e in top)}
                assert all(v==1 for k,v in checks.items()if k!='existing_H1_ch50')and checks['existing_H1_ch50']==0
                ps=list(body.iter(w+'p'));assert '1.33'in text(ps[8])
            else:
                checks={'compendium_prior_index_PI06':sum(e.tag==w+'p'and not h1(e)and text(e)=='PI06 Organización endógena y robustez funcional'for e in top)}
                assert checks['compendium_prior_index_PI06']==1
        assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
        proofs.append({'path':str(p),'bytes':len(b),'sha256_before_and_after':digest,'unchanged':True,'anchors':checks})
    code=[]
    for name in ('actualizar_manual_PI07_R01.py','publicar_documentos_PI07_literal_R01.py','comprobar_disponibilidad_render_PI07.py','empaquetar_PI07_final_R01.py'):
        p=p7/'codigo'/name;b=p.read_bytes();ast.parse(b)
        code.append({'file':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'AST_valid':True})
    out=p7/'control/HELPERS_DOCUMENTALES_PI07_PREVIA_SOLO_LECTURA_R01.json'
    if out.exists():raise FileExistsError(out)
    out.write_text(json.dumps({'schema':'DEE.PI07.editorial_helpers.read_only_preflight.v1','source_documents':proofs,'prepared_code':code,'authoring_executed':False,'publication_executed':False,'visual_QA':False,'skill_marker_executed':False,'Native_ticks':0,'product_writes':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'all_static_checks':True,'Native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
