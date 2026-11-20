"""Byte-copy sealed prior delivery and its small proofs, never change canonical."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,zipfile
ROOT=Path(__file__).resolve().parents[1];RUNS=ROOT.parent
NAME='CPC8_ORGANIZACION_COGNITIVA_NATIVA_APRENDIZAJE65_RESULTADOS.zip'
EXPECTED='65164c939621464c7d4faa800240bb1c2e25538ba9d878a65863016f57387c00'
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def copy_protected(source,target):
 before=sha(source)
 if target.exists():
  if sha(target)!=before:raise FileExistsError('Existing historical copy differs: '+str(target))
  return {'path':str(target.relative_to(RUNS)),'sha256':before,'bytes':target.stat().st_size,'state':'EXISTING_IDENTICAL_NOT_DUPLICATED'}
 target.parent.mkdir(parents=True,exist_ok=True)
 with source.open('rb') as inp,target.open('xb') as out:
  for b in iter(lambda:inp.read(1024**2),b''):out.write(b)
  out.flush();os.fsync(out.fileno())
 if sha(target)!=before or sha(source)!=before:raise RuntimeError('Copy/source changed')
 return {'path':str(target.relative_to(RUNS)),'sha256':before,'bytes':target.stat().st_size,'state':'NEW_BYTE_EXACT_COPY'}
def main():
 canonical=RUNS/'resultados'/NAME
 if sha(canonical)!=EXPECTED:raise RuntimeError('Canonical is not the authorized prior cut; do not choose another silently')
 historic=RUNS/'historico';historic.mkdir(exist_ok=True)
 backup=historic/(Path(NAME).stem+'__'+EXPECTED+'.zip')
 item=copy_protected(canonical,backup)
 with zipfile.ZipFile(backup) as z:
  bad=z.testzip()
  if bad:raise RuntimeError('Prior ZIP CRC failure: '+bad)
 proofs=[]
 for name in ('CIERRE_CPC8.json','HASH_ZIP_FINAL.sha256','LECTURA_PROVISIONAL.md','LEER_PRIMERO.md','TRANSPORTE_NO_REQUERIDO.json','VERIFICACION_FINAL_EXTERNA.json'):
  source=canonical.parent/name
  if source.is_file():proofs.append(copy_protected(source,historic/('PRUEBAS_'+EXPECTED)/name))
 report={'schema':'CPC8.reconstruction.prior_protection.v1','checked_utc':datetime.now(timezone.utc).isoformat(),
  'canonical_untouched':True,'canonical_sha256_after':sha(canonical),'prior_delivery':item,'small_historical_proofs':proofs,
  'crc':'PASS','historical_not_nested_in_new_delivery':True,'publication_condition':'Keep canonical unchanged until a new exact ZIP is functionally validated; compare current canonical hash again at replacement.',
  'source_sha256':sha(Path(__file__))}
 target=ROOT/'genealogia/PROTECCION_ENTREGA_ANTERIOR.json';target.parent.mkdir(exist_ok=True)
 if target.exists():
  old=json.loads(target.read_text(encoding='utf-8'))
  if old['canonical_sha256_after']!=EXPECTED:raise RuntimeError('Existing protection report conflicts')
 else:target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
