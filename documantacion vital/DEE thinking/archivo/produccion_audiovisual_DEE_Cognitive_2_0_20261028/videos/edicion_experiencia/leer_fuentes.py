"""Lectura editorial dirigida. No importa ni ejecuta el motor DEE."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json,re,xml.etree.ElementTree as ET

W=Path(__file__).resolve().parent
DEE=W.parents[2]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def paragraphs(p):
    with ZipFile(p) as z:r=ET.fromstring(z.read('word/document.xml'))
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    return [''.join(x.text or '' for x in n.findall('.//w:t',ns)) for n in r.findall('.//w:p',ns)]

if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='details':
        p=DEE/'archivo/estructura_anterior_20261026/4.0/DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip'
        dest=W/'fuentes';dest.mkdir(exist_ok=True)
        with ZipFile(p) as z:
            for case in ['new_combined_query','omitted_combined_relation']:
                for name in ['CASE.json','MEASUREMENTS.json']:
                    member=f'DEE_thinking_4_0_0/experiments/BLOCK_II/{case}/{name}'
                    b=z.read(member);target=dest/f'{case}_{name}';target.write_bytes(b)
                    data=json.loads(b)
                    if name=='MEASUREMENTS.json':
                        print(case,'KEYS',list(data));print(json.dumps({k:v for k,v in data.items() if k not in ['product','trace','receipts','fields','final','snapshots','installed_python_member_hashes']},ensure_ascii=False)[:8500])
        for case in ['IR_P01_GUARDED_M1','IR_MATCH_CURRENT']:
            p=DEE/f'4.5/DEE_thinking_4_5_0/validation/cpc_ports_4_5_final6/{case}/RESULT.json'
            b=p.read_bytes();(dest/f'{case}_RESULT.json').write_bytes(b);data=json.loads(b)
            print(case,'KEYS',list(data));print(json.dumps({k:v for k,v in data.items() if k in ['case','config','prospective','information','action','physical','use','samples','observe','observation','source','rows','comparisons','current_prediction','received','result']},ensure_ascii=False)[:9000])
        sys.exit(0)
    if len(sys.argv)>1 and sys.argv[1]=='archive':
        p=DEE/'archivo/estructura_anterior_20261026/4.0/DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip'
        with ZipFile(p) as z:
            names=[n for n in z.namelist() if any(s in n for s in ['BLOCK_II','EXPERIMENT_REPORT']) and n.endswith(('.json','.md'))]
            print('\n'.join(names[:100]))
            results=next(n for n in names if n.endswith('BLOCK_II/RESULTS.json'))
            data=json.loads(z.read(results));print('RESULTS',json.dumps(data,ensure_ascii=False)[:12000])
            (W/'indice_fuente_composicion.json').write_text(json.dumps({'zip':str(p),'sha256':sha(p),'members':names,'results_member':results,'results':data},ensure_ascii=False,indent=2),encoding='utf8')
        sys.exit(0)
    out={}
    for name in ['DEE_thinking_4_5_0_Libro_Blanco_y_Manual_Tecnico.docx','DEE_thinking_4_5_0_Maestro_Arquitectura_Reconstruccion.docx']:
        p=DEE/'4.5'/name
        rows=paragraphs(p)
        hits=[]
        for i,s in enumerate(rows):
            if any(t.lower() in s.lower() for t in ['17 → 38','17 -> 38','CompositionSession','U0','60.','37.','17, 38, 65','prediction','pregunta física','consulta activada']):
                if len(hits)<90:hits.append({'paragraph':i,'text':s[:1600]})
        out[name]={'path':str(p),'sha256':sha(p),'paragraphs':len(rows),'hits':hits}
        (W/(name+'.txt')).write_text('\n'.join(f'{i}: {s}' for i,s in enumerate(rows)),encoding='utf8')
    (W/'lectura_dirigida.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(out,ensure_ascii=False,indent=2))
