"""Publish the two complete 1.36 documents after structural and render evidence.
No authoring, Native import, state access or automatic repair.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, shutil, zipfile
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=R/'DEE Cognitive 2.0'
ALLOWED={C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx',
         R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'}
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def safe(p,root):
    p=Path(p).resolve(strict=True)
    if not p.is_relative_to(root.resolve()):raise ValueError('Document scope exceeded')
    for n in (p,*p.parents):
        if n.is_symlink() or getattr(n.lstat(),'st_file_attributes',0)&1024:raise ValueError('Linked publication target refused')
    return p
def main(a):
    stage=safe(a.staging,P/'documentos');render=safe(a.render_proof,P/'documentos')
    structural=stage/'VALIDACION_ESTRUCTURAL_PI08_B_1_36.json';v=read(structural)
    if v['edition']!='1.36' or v['originals_modified'] or v['published']:raise ValueError('Unpublished structural1.36 proof required')
    active=read(C/'sistema/estado/ACTIVO.json')
    if any(active[k]!=v['principal'][j]for k,j in(('life_id','life_id'),('tick','T'),('snapshot_sha256','snapshot_sha256'))):raise ValueError('Current principal differs from document facts')
    if len(v['documents'])!=2:raise ValueError('Exactly the two existing complete documents')
    qa=read(render)
    if qa.get('attempted')is not True or qa.get('visual_validation') not in(True,False):raise ValueError('Actual bounded render attempt required')
    rows=[]
    for d in v['documents']:
        src=safe(d['output'],stage);dst=safe(d['source'],R)
        if dst not in ALLOWED:raise ValueError('Unexpected rector document')
        backup=P/'documentos/respaldo_1_35'/dst.name
        if sha(dst)!=d['source_sha256'] or sha(backup)!=d['source_sha256'] or sha(src)!=d['output_sha256']:raise ValueError('Document CAS or full backup differs')
        with zipfile.ZipFile(src)as z:
            if z.testzip() is not None:raise ValueError('DOCX CRC failure')
        if not d['CRC_all_members']or not d['XML_parse_all_parts']:raise ValueError('Incomplete structural verification')
        rows.append({'source':str(src),'target':str(dst),'old_sha256':d['source_sha256'],'new_sha256':d['output_sha256'],'bytes':src.stat().st_size})
    out=P/'documentos/PUBLICACION_CIERRE_1_36.json'
    if out.exists():raise FileExistsError('Prior publication preserved')
    for row in rows:
        dst=Path(row['target']);tmp=dst.with_name(dst.name+'.PI08_CIERRE_DOC_WRITING')
        with Path(row['source']).open('rb')as f,tmp.open('xb')as g:shutil.copyfileobj(f,g);g.flush();os.fsync(g.fileno())
        if sha(tmp)!=row['new_sha256']:raise ValueError('Copy mismatch before publication')
        os.replace(tmp,dst)
    if any(sha(Path(x['target']))!=x['new_sha256']for x in rows):raise RuntimeError('Published bytes differ')
    result={'schema':'DEE.PI08.final_documents_published.v1','at_utc':datetime.now(timezone.utc).isoformat(),
            'edition':'1.36','actual_main':active,'files':rows,
            'structural_proof':{'path':str(structural),'sha256':sha(structural)},
            'visual_render_attempt':{'path':str(render),'sha256':sha(render)},
            'visual_validation':qa['visual_validation'],'visual_limitation':qa.get('limitation'),
            'old_full_documents_preserved':str(P/'documentos/respaldo_1_35'),'Native_executed':False}
    with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'publication':str(out),'sha256':sha(out),'files':rows,'visual_validation':qa['visual_validation']}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--staging',type=Path,required=True);p.add_argument('--render-proof',type=Path,required=True);main(p.parse_args())
