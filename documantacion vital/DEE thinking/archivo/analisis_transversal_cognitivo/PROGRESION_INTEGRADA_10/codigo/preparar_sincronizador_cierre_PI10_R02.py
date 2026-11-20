from pathlib import Path
import ast,hashlib
H=Path(__file__).resolve().parent
src=(H/'sincronizar_cierre_actual_PI10_R01.py').read_text('utf-8-sig')
src=src.replace("ap.add_argument('--manual-edition',default='1.39');","ap.add_argument('--manual-edition',default='1.39');ap.add_argument('--compendium-sha256');ap.add_argument('--compendium-bytes',type=int);")
src=src.replace("now=datetime.now(timezone.utc).isoformat();manual=C/MANUAL","now=datetime.now(timezone.utc).isoformat();manual=C/MANUAL;a.publication_proof=a.publication_proof.resolve()")
src=src.replace("'internal_edition':a.manual_edition,'publication_witness':witness(a.publication_proof)","'internal_edition':a.manual_edition,'edition':a.manual_edition,'document_publication':str(a.publication_proof),'publication_witness':witness(a.publication_proof)")
needle="need(after[FILES[2]]==before[FILES[2]],'ACTIVO was already correct: verify it, do not edit')"
assert src.count(needle)==1
extra="""if a.compendium_sha256 is not None or a.compendium_bytes is not None:
  need(a.compendium_sha256 is not None and a.compendium_bytes is not None,'Both actual Compendium SHA/bytes required')
  oldcomp=before[FILES[0]]['compendium_current'];compath=Path(oldcomp['path']).resolve()
  need(compath.is_relative_to(C.parent.resolve())and compath.is_file()and sha(compath)==a.compendium_sha256 and compath.stat().st_size==a.compendium_bytes,'Actual current Compendium identity mismatch')
  with zipfile.ZipFile(compath)as z:
   need(z.testzip()is None and a.manual_edition in z.read('word/document.xml').decode('utf-8'),'Compendium ZIP/internal current edition mismatch')
  compdesc=copy.deepcopy(oldcomp);compdesc.update({'sha256':a.compendium_sha256,'bytes':a.compendium_bytes,'internal_edition':a.manual_edition,'publication_witness':witness(a.publication_proof)})
  for name in(FILES[0],FILES[1],FILES[5]):
   after[name].setdefault('PI10_pre_final_compendium_historical',copy.deepcopy(before[name].get('compendium_current')))
   after[name]['compendium_current']=copy.deepcopy(compdesc)
 """+needle
src=src.replace(needle,extra).replace('DEE.PI10.final_current_metadata_sync.R01','DEE.PI10.final_current_metadata_sync.R02').replace('control/SINCRONIZACION_CIERRE_ACTUAL_PI10_R01','control/SINCRONIZACION_CIERRE_ACTUAL_PI10_R02')
ast.parse(src)
p=H/'sincronizar_cierre_actual_PI10_R02.py';assert not p.exists();p.write_text(src,'utf-8')
print(str(p));print(hashlib.sha256(p.read_bytes()).hexdigest())

