"""Publish the two full, structurally verified A1.35 documents, literal CAS.
Visual rendering failure is recorded separately and never called approval.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,zipfile
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(a):
 stage=a.staging.resolve(strict=True)
 if not stage.is_relative_to((P/'documentos').resolve()):raise ValueError('Campaign document staging only')
 proof_file=stage/'VALIDACION_ESTRUCTURAL_PI08_A_1_35.json';p=read(proof_file)
 if p['edition']!='1.35'or p['originals_modified']or p['published']:raise ValueError('Exact validated unpublished stage required')
 active=read(C/'sistema/estado/ACTIVO.json')
 if any(active[k]!=p['principal'][j]for k,j in(('life_id','life_id'),('tick','T'),('snapshot_sha256','snapshot_sha256'))):raise ValueError('Principal advanced beyond document facts')
 rows=[]
 for d in p['documents']:
  src=Path(d['output']);dst=Path(d['source']);backup=P/'documentos/respaldo_1_34'/dst.name
  if sha(dst)!=d['source_sha256']or sha(backup)!=d['source_sha256']or sha(src)!=d['output_sha256']:raise ValueError('Document CAS/backup differs')
  with zipfile.ZipFile(src)as z:
   if z.testzip()is not None:raise ValueError('DOCX CRC failure')
  if not d['CRC_all_members']or not d['XML_parse_all_parts']:raise ValueError('Structural proof incomplete')
  rows.append({'source':str(src),'target':str(dst),'old_sha256':d['source_sha256'],'new_sha256':d['output_sha256'],'bytes':src.stat().st_size})
 out=P/'documentos/PUBLICACION_A_1_35.json'
 if out.exists():raise FileExistsError('Prior publication preserved')
 for r in rows:
  dst=Path(r['target']);tmp=dst.with_name(dst.name+'.PI08_DOC_WRITING')
  with Path(r['source']).open('rb')as source,tmp.open('xb')as target:shutil.copyfileobj(source,target);target.flush();os.fsync(target.fileno())
  if sha(tmp)!=r['new_sha256']:raise ValueError('Copy mismatch before publication')
  os.replace(tmp,dst)
 if any(sha(Path(r['target']))!=r['new_sha256']for r in rows):raise RuntimeError('Publication mismatch')
 result={'schema':'DEE.PI08.A.documents_published.v1','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'edition':'1.35','actual_main':active,'files':rows,'structural_proof':{'path':str(proof_file),'sha256':sha(proof_file)},'visual_render_attempt':{'path':str(P/'documentos/INTENTO_RENDER_A_1_35.json'),'sha256':sha(P/'documentos/INTENTO_RENDER_A_1_35.json')},'visual_validation':False,'visual_limitation':'LibreOffice soffice.exe unavailable; no foreign Word instance opened/closed. Whole original historical XML and non-editorial parts preserved; layout remains unverified.','old_full_documents_preserved':str(P/'documentos/respaldo_1_34'),'Native_executed':False}
 with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps({'publication':str(out),'sha256':sha(out),'edition':'1.35','full_documents':rows,'visual_validation':False},ensure_ascii=False))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--staging',type=Path,required=True);main(ap.parse_args())
