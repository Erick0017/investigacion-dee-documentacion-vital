"""Prepare12h maximum from un-applied9h files; original start never moves."""
from pathlib import Path
import ast,datetime,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def translate(s):
    return s.replace('_R04','_R05').replace('.R04','.R05').replace('lease_R04_bundle','lease_R05_bundle').replace('1794870000','1794880800').replace('1794874020','1794884820').replace('2026-11-16T23:00:00Z','2026-11-17T02:00:00Z').replace('2026-11-17T00:07:00Z','2026-11-17T03:07:00Z').replace('cutoff00:07UTCNov17','cutoff03:07UTCNov17').replace('Q1 after23:00UTCNov16','Q1 after02:00UTCNov17')
files=[('native/'+n+'_R04.py','native/'+n+'_R05.py')for n in('ledger_v3','owner_support_v3','lease_core_v3','migrar_lease_cerrada_v3')]+[
 ('control/mcp_persistente_v3_R04.py','control/mcp_persistente_v3_R05.py'),('control/world_comprimido_v3_R04.py','control/world_comprimido_v3_R05.py'),
 ('control/run_integrated_v3_R04.py','control/run_integrated_v3_R05.py'),('native/test_lease_v3_R04_offline.py','native/test_lease_v3_R05_offline.py'),
 ('control/sellar_codigo_lease_R04.py','control/sellar_codigo_lease_R05.py')]
rows=[]
for old,new in files:
    s=translate((ROOT/old).read_text('utf8'))
    if 'mcp_persistente'in new:s=s.replace('1<=seconds<=32400','1<=seconds<=43200')
    if 'world_comprimido'in new:s=s.replace('remaining=min(32400,','remaining=min(43200,')
    ast.parse(s);p=ROOT/new
    with p.open('x',encoding='utf8')as f:f.write(s)
    rows.append({'file':new,'bytes':p.stat().st_size,'sha256':sha(p)})
bundle=ROOT/'native/lease_R05_bundle';bundle.mkdir()
for name in('rbx07_native_v3.py','rbx07_identity_v3.py','rbx07_funciones_v3.py'):
    target=bundle/name
    if name=='rbx07_native_v3.py':
        s=translate((ROOT/'native/lease_R04_bundle'/name).read_text('utf8'));ast.parse(s)
        with target.open('x',encoding='utf8')as f:f.write(s)
    else:shutil.copyfile(ROOT/'native/bundle'/name,target)
    rows.append({'file':str(target.relative_to(ROOT)),'bytes':target.stat().st_size,'sha256':sha(target)})
proof={'schema':'DEE.R07.prospective_lease_code.R05','prepared_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'original_start_epoch':1794841620,'last_new_epoch':1794880800,'hard_finish_epoch':1794884820,
 'previous_R04_9h_prepared_not_applied':True,'operational_roots_modified':False,'Native_MCP_model_calls':0,
 'scope':'Prospective finite maximum12h same start;9h remains target if host overhead permits. Native algorithms, all caps/readers/codecs/policy unchanged.',
 'files':rows}
with(ROOT/'control/CODIGO_LEASE_R05_PREPARADO.json').open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
print(json.dumps(proof,ensure_ascii=False))
