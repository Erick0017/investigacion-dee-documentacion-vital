"""Selective read-only rescue of sources; archive inventory is not full reading."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
BASE=next(p for p in ROOT.parents if p.name=='documantacion vital')
PRACTICAL=BASE/'DEE thinking/casos practicos'
CPC7=PRACTICAL/'CPC7_MENTE_DEE_ACCESO_SELECTIVO_Y_APRENDIZAJE_CONTINUO_RESULTADOS.zip'
EXPECTED_CPC7='64a9ca648d10bb8bc42c02e218091b4e7c5599a55301c65d67c7f6f8ac83a128'
OLD_SHA='65164c939621464c7d4faa800240bb1c2e25538ba9d878a65863016f57387c00'
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def put(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def protected_bytes(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():
  if path.read_bytes()!=data:raise FileExistsError('Different existing rescued source: '+str(path))
 else:
  with path.open('xb') as f:f.write(data)
def selected(z,member,destination,archive_id,archive_sha):
 info=z.getinfo(member);data=z.read(member);protected_bytes(destination,data)
 return {'source_id':archive_id,'archive_sha256':archive_sha,'member':member,'member_sha256':hashlib.sha256(data).hexdigest(),
   'bytes':len(data),'crc32':f'{info.CRC:08x}','copy':destination.relative_to(ROOT).as_posix(),'state':'PRESERVADA_BYTE_EXACTA; no ejecutada por rescate'}
def main():
 (ROOT/'genealogia').mkdir(exist_ok=True)
 if sha(CPC7)!=EXPECTED_CPC7:raise RuntimeError('CPC7 differs from expected source; stop before selecting another')
 sources=[];unresolved=[]
 with zipfile.ZipFile(CPC7) as z:
  names=set(z.namelist())
  seeds=['CPC7/src/'+n for n in ('integrated_public.py','integrated_revision.py','selective_native.py','residue_regulation.py','integrated.py','snapshot_storage.py','common.py')]
  queue=list(seeds);seen=set()
  while queue:
   member=queue.pop(0)
   if member in seen:continue
   if member not in names:unresolved.append({'member':member,'reason':'Missing static module'});continue
   seen.add(member);data=z.read(member)
   if '/comparadores/' in member or '/packaging/' in member:raise RuntimeError('Not operative historical comparators/packaging')
   sources.append(selected(z,member,ROOT/'genealogia'/member,'CPC7',EXPECTED_CPC7))
   tree=ast.parse(data.decode('utf-8-sig'))
   for node in ast.walk(tree):
    modules=[n.name.split('.')[0] for n in node.names] if isinstance(node,ast.Import) else [node.module.split('.')[0]] if isinstance(node,ast.ImportFrom) and node.module else []
    for module in modules:
     possibilities=['CPC7/src/'+module+'.py','CPC7/src/endogenous/'+module+'.py']
     found=next((n for n in possibilities if n in names),None)
     if found and found not in seen:queue.append(found)
  for member in ['CPC7/configuraciones/integrated_revision.json','CPC7/configuraciones/residue_regulation.json',
      'CPC7/resultados/integrated_revision/ANALYSIS.json','CPC7/resultados/integrated_revision/INDEX_ALL.json',
      'CPC7/resultados/integrated_revision/PUBLIC_GEOMETRY_CHECK.json','CPC7/revision/LECTURA_PROVISIONAL.md','CPC7/revision/RETENCION_Y_PLASTICIDAD.json']:
   sources.append(selected(z,member,ROOT/'genealogia'/member,'CPC7',EXPECTED_CPC7))
  for case in ('IR_P01_GUARDED_M1','IR_R607_GUARDED_M1','IR_C01_OFFPATH_GUARDS','IR_C02_AUX_OFFPATH'):
   for name in ('CONFIG.json','CHECKS.json','MEASUREMENTS.json'):
    member='CPC7/resultados/integrated_revision/'+case+'/'+name
    sources.append(selected(z,member,ROOT/'genealogia'/member,'CPC7',EXPECTED_CPC7))
  for name in ('T0.deetsnap.gz','T338.deetsnap.gz','T472.deetsnap.gz'):
   member='CPC7/resultados/integrated_revision/IR_P01_GUARDED_M1/'+name
   sources.append(selected(z,member,ROOT/'genealogia'/member,'CPC7',EXPECTED_CPC7))
  analysis=json.loads(z.read('CPC7/resultados/integrated_revision/ANALYSIS.json'))
  cpc7summary=[{'case_id':r['case_id'],'base204':r['base204'],'base338':r['base338'],'post472':r['post472']} for r in analysis['cases']]
 # New entanglement source: copy both complete DOCX files for ROOT's separately recorded full reading.
 quantum=BASE/'entrelazamiento cuantico explicacion y kernel completo/ENTRELAZAMIENTO_CUANTICO.zip'
 quantum_sha=sha(quantum)
 with zipfile.ZipFile(quantum) as z:
  for member in z.namelist():
   if member.lower().endswith('.docx'):sources.append(selected(z,member,ROOT/'referencias/entrelazamiento'/Path(member).name,'ENTRELAZAMIENTO',quantum_sha))
 # Restore47 rows as historical antecedents, never as already integrated reconstruction functions.
 old=ROOT.parent/'historico'/('CPC8_ORGANIZACION_COGNITIVA_NATIVA_APRENDIZAJE65_RESULTADOS__'+OLD_SHA+'.zip')
 if sha(old)!=OLD_SHA:raise RuntimeError('Sealed prior reference differs')
 with zipfile.ZipFile(old) as z:
  member='CPC8/genealogia/MATRIZ_CAPACIDADES_ACUMULADAS.json';data=z.read(member)
  destination=ROOT/'genealogia/antecedentes/MATRIZ_47_CIERRE_ANTERIOR.json'
  sources.append(selected(z,member,destination,'CPC8_CORTE_ANTERIOR',OLD_SHA))
  oldrows=json.loads(data)['capabilities']
  for member in ('CPC8/genealogia/INVENTARIO_FUENTES.json','CPC8/genealogia/PENDIENTES_RECUPERADOS.json'):
   sources.append(selected(z,member,ROOT/'genealogia/antecedentes'/Path(member).name,'CPC8_CORTE_ANTERIOR',OLD_SHA))
 rows=[{'id':c['id'],'mechanism':c['mechanism'],'domain':c['domain'],'controls':c['controls'],'limits':c['published_limits'],
  'historical_source_identities':c['origins'],'prior_state_historical_only':c['state'],
  'reconstruction_state':{'preservada':True,'reproducida':False,'adaptada':False,'integrada_en_MAIN':False,
    'state':'ANTECEDENTE_RESCATADO_NO_HEREDADO_AUTOMATICAMENTE','required':'Nuevo resultado de reconstrucción con identidad, control y alcance antes de atribuir integración'},
  'prior_matrix_pointer':'/capabilities/'+str(i)} for i,c in enumerate(oldrows)]
 assert len(rows)==47
 put(ROOT/'genealogia/MATRIZ_ANTECEDENTES_47.json',{'schema':'CPC8.reconstruction.antecedents47.v1','old_delivery_sha256':OLD_SHA,'capabilities':rows})
 # Fixed shallow inventory, not a full corpus read. Every CORE01-17 is present in this pass.
 dirs=('cores','ingenieria','mente basal','procesos','pensamiento','FISICA DEE UNI 1','FISICA DEE Y PROCESAMIENTO NATIVO','entrelazamiento cuantico explicacion y kernel completo')
 archives=[]
 for directory in dirs:
  for path in sorted((BASE/directory).glob('*.zip')):
   before=path.stat();digest=sha(path)
   with zipfile.ZipFile(path) as z:names=z.namelist();counts={'members':len(names),'expanded_bytes':sum(i.file_size for i in z.infolist())}
   archives.append({'id':path.stem,'path_relative_to_documentation':path.relative_to(BASE).as_posix(),'sha256':digest,'bytes':before.st_size,
      **counts,'read_scope':'Inventario central y hash; no lectura completa de sus miembros','source_modified':False})
 # Check claimed4.5 documents without substituting4.0 under the same name.
 product=BASE/'DEE thinking/4.5/DEE_THINKING_4_5_0_COMPILACION_Y_VALIDACION_RESULTADOS.zip'
 with zipfile.ZipFile(product) as z:product_docx=[n for n in z.namelist() if n.lower().endswith('.docx')]
 docs45={'requested':['Maestro de Arquitectura y Reconstrucción4.5','Libro Blanco y Manual Técnico4.5'],
   'filesystem_matches':[p.relative_to(BASE).as_posix() for p in (BASE/'DEE thinking').rglob('*.docx') if '4.5' in p.name or '4_5' in p.name],
   'official_product_zip_docx_members':product_docx,'state':'NO_LOCALIZADOS' if not product_docx else 'LOCALIZADOS_EN_PRODUCTO',
   'complete_reading_claim':False,'fallback':'Contratos/código4.5 y manuales4.0 identificados como4.0, no como4.5; ROOT registra su lectura real.'}
 report={'schema':'CPC8.reconstruction.source_rescue.v1','generated_utc':datetime.now(timezone.utc).isoformat(),
   'CPC7':{'path_relative_to_documentation':CPC7.relative_to(BASE).as_posix(),'sha256':EXPECTED_CPC7,'n':67,'horizon':472,'guard_scope':'14vs6 denotes covered responses, not number of guards','actual_prior_results':cpc7summary},
   'selected_members':sources,'unresolved_static_dependencies':unresolved,'corpus_archives':archives,'documents45':docs45,
   'unread_scope':'Archives only inventoried except explicit selected members; no new simulations; ROOT reads full documents independently. B1/B2 are historical context only, not participants or comparators in reconstruction.',
   'source_sha256':sha(Path(__file__))}
 put(ROOT/'genealogia/INVENTARIO_RECONSTRUCCION.json',report)
 print(json.dumps({'selected':len(sources),'corpus_archives':len(archives),'CPC7_source_modules':len(seen),'docs45':docs45,'unresolved':unresolved},ensure_ascii=False))
if __name__=='__main__':main()
