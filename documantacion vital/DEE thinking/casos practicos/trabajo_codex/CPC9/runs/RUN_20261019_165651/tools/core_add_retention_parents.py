"""Preserve only indispensable CPC6 causal-parent states, never every tick."""
from pathlib import Path
import base64,gzip,hashlib,json,zipfile
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE';CASES=RUN.parents[3]
archive=CASES/'CPC6_MENTE_DEE_INTEGRADA_APRENDIZAJE_Y_COMUNICACION_RESULTADOS.zip';index=CORE/'documentacion/INDICE_MIEMBROS.json';idx=json.loads(index.read_text(encoding='utf8'));store=CORE/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz';known={r['sha256']for r in idx['paths'].values()};added=[];selected=set();frozen={'schema':'DEE_CORE.retention_inputs.v1','historical_parent_states_not_new_E1':True,'groups':{}}
with zipfile.ZipFile(archive)as z:
 def get(member):return json.loads(z.read('CPC6/'+member).decode('utf-8-sig'))
 names=('CONSOLIDATION_CONTROLS_01.json','WORD_BUS_CONTROLS_01.json','LATE_ACCESS_01.json');configs={n:get('configuraciones/'+n)for n in names};selected.update('configuraciones/'+n for n in names)
 early=configs[names[0]];rows=[]
 for parent in early['parents']:
  folder='resultados/D04_OPEN_LANDING/'+parent['case_id'];selected.update(folder+'/'+n for n in('T88.deetsnap','T90.deetsnap','MEASUREMENTS.json'))
  for mechanism in early['mechanisms']:
   for arm in early['arms']:
    identifier=parent['case_id']+'_'+mechanism+'_'+arm;primary='resultados/CONSOLIDATION_CONTROLS_01/'+identifier+'/MEASUREMENTS.json';selected.add(primary);rows.append({'id':identifier,'parent':parent,'mechanism':mechanism,'arm':arm,'primary':'historico/CPC6/'+primary})
 frozen['groups']['early']={'configuration':early,'cases':rows}
 word=configs[names[1]];rows=[]
 for case in word['cases']:
  folder='resultados/B01_WORD_BUS/'+case['parent'];selected.update(folder+'/'+n for n in('T160.deetsnap','MEASUREMENTS.json'));primary='resultados/WORD_BUS_CONTROLS_01/'+case['id']+'/MEASUREMENTS.json';selected.add(primary);rows.append({'id':case['id'],'case':case,'primary':'historico/CPC6/'+primary})
 frozen['groups']['word']={'configuration':word,'cases':rows}
 late=configs[names[2]];rows=[]
 for parent in late['parents']:
  selected.add('resultados/D06_BILATERAL/'+parent+'/T110.deetsnap')
  for arm in late['arms']:
   identifier=parent+'_'+arm;primary='resultados/LATE_ACCESS_01/'+identifier+'/MEASUREMENTS.json';old=get(primary);selected.add(primary);rows.append({'id':identifier,'parent':parent,'arm':arm,'selected':old['selected_access'],'primary':'historico/CPC6/'+primary})
 frozen['groups']['late']={'configuration':late,'cases':rows}
 # Resolve compressed aliases and validate the entire selection BEFORE any
 # append. The historical loader supports .deetsnap -> .deetsnap.gz aliases.
 resolved=[];inventory=set(z.namelist())
 for member in sorted(selected):
  if 'CPC6/'+member not in inventory and 'CPC6/'+member+'.gz'in inventory:member+='.gz'
  assert 'CPC6/'+member in inventory,member
  resolved.append(member)
 with gzip.open(store,'ab',compresslevel=9)as target:
  for member in resolved:
   b=z.read('CPC6/'+member);h=hashlib.sha256(b).hexdigest();logical='historico/CPC6/'+member
   if logical in idx['paths']:assert idx['paths'][logical]['sha256']==h;continue
   if h not in known:target.write(json.dumps({'sha256':h,'bytes':len(b),'base64':base64.b64encode(b).decode('ascii')},separators=(',',':')).encode('ascii')+b'\n');known.add(h)
   idx['paths'][logical]={'sha256':h,'bytes':len(b),'origin':{'archive':archive.name,'archive_sha256':'9d8c72a2536a7d8a782e0f3885d6d9ceba48b5f3d9111f618386def13fff708b','member':'CPC6/'+member,'reason':'Indispensable declared historical causal parent with full queue/clock state, or exact primary needed by original diagnostic source. Not new E1.'}};added.append({'logical':logical,'bytes':len(b),'sha256':h})
idx['content_store_sha256']=hashlib.sha256(store.read_bytes()).hexdigest();index.write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for group in frozen['groups'].values():
 for case in group['cases']:case['primary_sha256']=idx['paths'][case['primary']]['sha256']
(CORE/'configuraciones/RECUPERACION_RETENCION_CONGELADA.json').write_text(json.dumps(frozen,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(RUN/'notes/core_audit/CPC6_RETENTION_ADDITIONS.json').write_text(json.dumps(added,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'added':len(added),'snapshots':sum(x['logical'].endswith(('.deetsnap','.deetsnap.gz'))for x in added),'groups':{k:len(v['cases'])for k,v in frozen['groups'].items()}}))
