"""Recover unique positive and adverse first-CPC8 genealogy, without old ZIPs."""
from pathlib import Path
import base64,gzip,hashlib,json,zipfile
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE';CASES=RUN.parents[3]
archive=CASES/'trabajo_codex/CPC8/runs/historico/CPC8_ORGANIZACION_COGNITIVA_NATIVA_APRENDIZAJE65_RESULTADOS__65164c939621464c7d4faa800240bb1c2e25538ba9d878a65863016f57387c00.zip';ah=hashlib.file_digest(archive.open('rb'),'sha256').hexdigest();assert ah=='65164c939621464c7d4faa800240bb1c2e25538ba9d878a65863016f57387c00'
index=CORE/'documentacion/INDICE_MIEMBROS.json';idx=json.loads(index.read_text(encoding='utf8'));known={r['sha256']for r in idx['paths'].values()};store=CORE/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz';added=[];pending=[]
with zipfile.ZipFile(archive)as z:
 for i in z.infolist():
  if i.filename.endswith(('.py','.json','.md','.toml','.ps1','.cfg','.ini','.yaml','.yml','.csv','.sha256'))and i.file_size<=8000000:
   logical='cpc8_inicial/'+i.filename.removeprefix('CPC8/')
   if logical not in idx['paths']:pending.append((i,logical))
 if pending:
  with gzip.open(store,'ab',compresslevel=9)as target:
   for i,logical in pending:
    data=z.read(i.filename);h=hashlib.sha256(data).hexdigest()
    if h not in known:target.write(json.dumps({'sha256':h,'bytes':len(data),'base64':base64.b64encode(data).decode('ascii')},separators=(',',':')).encode('ascii')+b'\n');known.add(h)
    idx['paths'][logical]={'sha256':h,'bytes':len(data),'origin':{'archive':archive.name,'archive_sha256':ah,'member':i.filename,'reason':'First CPC8 unique source/configuration/primary, both positive and adverse. Historical comparators/maintenance remain inert, never launched by recovery.'}};added.append({'logical':logical,'sha256':h,'bytes':len(data)})
 idx['content_store_sha256']=hashlib.file_digest(store.open('rb'),'sha256').hexdigest();index.write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 frozen={'schema':'DEE_CORE.first_CPC8_inputs.v1','source_archive_sha256':ah,'cases':[],'scope':'Original N131 first-CPC8 apparatus, not the later N67 MCTS or CPC9 E1.'}
 for cid in('SOC_I21_SOCIAL_THEN_L01_REVISION','SOC_I22_SOCIAL_L01_OFFPATH','SOC_I12_L17_SOURCE_UNPAIRED','SOC_I14_L17_RESERVED_NEGATIVE'):
  primary='cpc8_inicial/resultados/semantica/'+cid+'/MEASUREMENTS.json';old=json.loads(z.read('CPC8/resultados/semantica/'+cid+'/MEASUREMENTS.json'));frozen['cases'].append({'id':cid,'case':old['case'],'source_sha256':old['executed_source'],'frozen_source_root':'cpc8_inicial/resultados/semantica/'+cid+'/executed_source','primary':primary,'primary_sha256':idx['paths'][primary]['sha256']})
 frozen['continuity']={'configurations':{},'stages':[],'scope':'Freshly regenerated SOC_I21T690 continues to new RIGHT acquisition and later1182 use; two control branches share its parent but are not independent new individuals.'}
 for key,name in(('learn','LONGITUDINAL_690_FROZEN.json'),('read','RIGHT_ACCESS_1182_FROZEN.json')):
  logical='cpc8_inicial/configuraciones/integracion/'+name;frozen['continuity']['configurations'][key]={'logical':logical,'sha256':idx['paths'][logical]['sha256']}
 for kind,cids in(('learn',('LIF_P11_NEW_AB','LIF_C12_NO_RIGHT_CUE')),('read',('USE_P11_RIGHT_PAIRED','USE_C11_RIGHT_NO_CUE','USE_C12_RIGHT_UNPAIRED'))):
  for cid in cids:
   primary='cpc8_inicial/resultados/integracion/'+cid+'/MEASUREMENTS.json';old=json.loads(z.read('CPC8/resultados/integracion/'+cid+'/MEASUREMENTS.json'));frozen['continuity']['stages'].append({'kind':kind,'id':cid,'case':old['case'],'source_sha256':old['executed_source'],'frozen_source_root':'cpc8_inicial/resultados/integracion/'+cid+'/executed_source','primary':primary,'primary_sha256':idx['paths'][primary]['sha256']})
 initial=json.loads(z.read('CPC8/revision/NSM65_EVIDENCIAS.json'))
 comparison={'schema':'DEE_CORE.CPC8_campaigns.v1','initial':{'sha256':ah,'local_prime_levels':initial['local_prime_levels'],'semantic_claims':initial['current_executed_semantic_claims'],'social_profile':initial['generic_native_social_profile'],'localizer':'cpc8_inicial/revision/NSM65_EVIDENCIAS.json'},'reconstructed':{'sha256':'4cf266a0ab968e26986a9935317ba146a8f769fc5717092470c4bead8983b8ed','conservative_counts':{'E0':59,'E1':1,'E2':5,'E3':0,'E4':0,'E5':0},'noncumulative_dimensions':{'E4':['BEFORE','TOUCH'],'E5':['TOUCH','LIKE_AS']},'localizer':'cpc8/revision/NSM65_EVIDENCIAS.json'},'not_a_sum':'No son dos repertorios sumables de un mismo E1. Los resultados lingüísticos permanecen limitados y las funciones positivas se conservan aunque su operador sea preparado.'}
 (CORE/'configuraciones/CPC8_INICIAL_CONGELADO.json').write_text(json.dumps(frozen,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(CORE/'documentacion/COMPARACION_DOS_CPC8.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(RUN/'notes/core_audit/INITIAL_CPC8_ADDITIONS.json').write_text(json.dumps(added,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'selected':len(pending),'added':len(added),'selected_logical_bytes':sum(r['bytes']for r in added)}))
