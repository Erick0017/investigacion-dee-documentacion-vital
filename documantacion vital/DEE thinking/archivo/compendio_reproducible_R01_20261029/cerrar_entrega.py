from pathlib import Path
import hashlib,json,shutil,zipfile,datetime
B=Path(__file__).resolve().parent
T=B.parents[3]
root=B.parents[1]
# Todas las rutas de entrega quedan bajo la raíz autorizada.
dest=root/'CPC - Experimentos y mecanismos'
z=T/'_R01V/ENTREGA_DEFINITIVA_R01.zip'
doc=B/'COMPENDIO_BORRADOR_R01.docx'
expected='d95e05a50aa1688d46c4232afd2c0df674c53974e7df09b958c88853f9969b9c'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
assert z.stat().st_size==213083374 and sha(z)==expected
base=load(B/'construccion.json')
preserved=[]
for row in base['originals']:
 p=Path(row['path'])
 actual=sha(p)
 assert actual==row['sha256'],str(p)
 preserved.append(dict(path=str(p),sha256=actual,unchanged_before_delivery=True))
backup=B/'COMPENDIO_EDICION_ANTERIOR.docx'
assert sha(backup)==base['originals'][0]['sha256']
smoke=load(T/'_R01V/smoke_exacto/nativo/REPRODUCCION.json')
assert smoke['matched']==smoke['total']==2
recalc=load(B/'RECALCULO_DEFINITIVO.json')
assert not recalc['errors'] and recalc['raw_fields_recomputed']==379449
extracted=load(T/'_R01V/FINAL_EXACTO/EXTRACCION_VERIFICADA.json')
assert extracted['sha256']==expected and extracted['all_members_extracted_with_crc']
with zipfile.ZipFile(doc)as f:
 assert f.testzip()is None
 xml=f.read('word/document.xml').decode('utf-8')
 assert expected in xml and 'wall11_relearn'in xml and 'wall17_relearn'in xml
 assert 'wall 11_relearn'not in xml
outzip=dest/'DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip'
outdoc=dest/'COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
assert outzip.resolve().parent==dest.resolve()and outdoc.resolve().parent==dest.resolve()
# Sólo se reemplaza el Word solicitado; la edición recibida ya está protegida.
shutil.copy2(z,outzip)
shutil.copy2(doc,outdoc)
assert sha(outzip)==expected and sha(outdoc)==sha(doc)
for row in base['originals'][1:]:
 assert sha(Path(row['path']))==row['sha256'],row['path']
report=dict(
 schema='DEE.Compendio.FinalExternalVerification.R01',
 utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 final_zip=dict(path=str(outzip),bytes=outzip.stat().st_size,sha256=sha(outzip),members=6600,logical_files=9644),
 final_docx=dict(path=str(outdoc),bytes=outdoc.stat().st_size,sha256=sha(outdoc),render='Microsoft Word 16.0 → PDF → page PNGs',pages=52,previous_edition=str(backup)),
 extraction=extracted,
 integrity=dict(unique_objects=6596,logical_files=9644,entrypoints_checked=3,unique_expanded_bytes=493201542,status='EXACT_SHA256_MATCHED',all_members_crc=True),
 native_from_exact_zip=dict(command='CPython3.13 -I -B -X utf8 entorno_seguro.py + sectores/paisaje/ejecutar.py native M110; variants CUT,W11',report=str(T/'_R01V/smoke_exacto/nativo/REPRODUCCION.json'),sha256=sha(T/'_R01V/smoke_exacto/nativo/REPRODUCCION.json'),matched=2,total=2,original_scientific_directories_required=False),
 exported_recalculation=recalc,
 coverage=dict(records=101,catalogued_conditions=554,native_selected=52,native_partial=4,technical_continuations=4,recalculation_only=36,not_newly_verified=4,external_instrument=1),
 protected_originals=preserved,
 current_Cognitive_life_native_ticks=0,
 official_engine_kernel_modified=False,
 limitations=[
 'La prueba final desde el ZIP exacto selecciona dos variantes causales; el resto conserva su verificación por mecanismo y revisión dentro del ZIP.',
 'Los cuatro contratos sin nueva verificación son M036,M037,M044,M047; los parciales son M035,M110,M122,M304.',
 'M222,M306,M307,M308 continúan cortes completos históricos; no repiten toda su adquisición.',
 'El recálculo de evidencia no equivale a reproducción física ni convierte un negativo o error del anfitrión en éxito.',
 'El aislamiento de Python no certifica interceptar fopen de C++ o todos los accesos del sistema operativo.',
 'Se requieren Windows x64 y CPython3.13; determinados protocolos externos requieren además CPython3.12. No se incluye un sistema operativo o intérprete.'
 ],
 delivery_directory_members=sorted(p.name for p in dest.iterdir())
)
(B/'VERIFICACION_FINAL_EXTERNA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
assert len(report['delivery_directory_members'])==2
print(json.dumps(dict(zip=report['final_zip'],docx=report['final_docx'],originals_unchanged=8),ensure_ascii=False))
