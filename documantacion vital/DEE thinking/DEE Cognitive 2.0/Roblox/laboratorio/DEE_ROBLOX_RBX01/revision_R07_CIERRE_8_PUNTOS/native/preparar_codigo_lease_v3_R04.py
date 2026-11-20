"""Prepare future lease code ONLY; never write any operational Native root."""
from pathlib import Path
import ast,datetime,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
OLD_LAST=1794859200;OLD_END=1794863220;NEW_LAST=1794870000;NEW_END=1794874020
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(rel,text):
    ast.parse(text);p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8')as f:f.write(text)
    return {'file':rel,'bytes':p.stat().st_size,'sha256':sha(p)}
def epochs(text):return text.replace(str(OLD_LAST),str(NEW_LAST)).replace(str(OLD_END),str(NEW_END))
rows=[]
for name in('rbx07_native_v3.py','rbx07_identity_v3.py','rbx07_funciones_v3.py'):
    original=(ROOT/'native/bundle'/name).read_text('utf8');new=epochs(original)if name=='rbx07_native_v3.py'else original
    if name=='rbx07_native_v3.py':
        new=new.replace('cutoff04:13UTCNov16','cutoff00:07UTCNov17').replace('Q1 after03:10UTCNov16','Q1 after23:00UTCNov16')
        normalized=new.replace(str(NEW_LAST),str(OLD_LAST)).replace(str(NEW_END),str(OLD_END)).replace('cutoff00:07UTCNov17','cutoff04:13UTCNov16').replace('Q1 after23:00UTCNov16','Q1 after03:10UTCNov16')
        if ast.dump(ast.parse(normalized))!=ast.dump(ast.parse(original)):raise ValueError('Actor changed beyond lease constants/messages')
    rows.append(save('native/lease_R04_bundle/'+name,new))
s=epochs((ROOT/'native/ledger_v3.py').read_text('utf8'))
s=s.replace("        with self.lock():\n            if not self.path.exists():", "        with self.lock():\n            if not self.path.exists():raise RuntimeError('LEASE_REQUIRES_ORIGINAL_LEDGER_NO_RESET')\n            if not self.path.exists():")
s=s.replace("        if v['consumed']!=sum", "        if v.get('last_new_episode_epoch')!=LAST_NEW or v.get('cutoff_epoch')!=CUTOFF:raise ValueError('EXPLICIT_LEASE_HEADER_MIGRATION_REQUIRED')\n        if v['consumed']!=sum")
s=s.replace('NO_NEW_Q1_AFTER20UTC','NO_NEW_Q1_AFTER23UTC').replace('ABSOLUTE21_07UTC_CUTOFF','ABSOLUTE00_07UTC_NOV17_CUTOFF')
rows.append(save('native/ledger_v3_R04.py',s))
s=epochs((ROOT/'native/owner_support_v3.py').read_text('utf8')).replace('native/ledger_v3.py','native/ledger_v3_R04.py')
s=s.replace("    if not destination.is_relative_to(REVISION_ROOT)", "    if (destination/'LEASE_MIGRATION_IN_PROGRESS.json').exists():raise RuntimeError('LEASE_TRANSACTION_INCOMPLETE_NO_OWNER')\n    if not (destination/'LEASE_APPLIED_R04.json').is_file():raise RuntimeError('EXPLICIT_CLOSED_LEASE_MIGRATION_REQUIRED')\n    if not destination.is_relative_to(REVISION_ROOT)")
s=s.replace('cutoff04:13UTCNov16','cutoff00:07UTCNov17')
rows.append(save('native/owner_support_v3_R04.py',s))
s=(ROOT/'control/mcp_persistente_v3.py').read_text('utf8').replace('1<=seconds<=14400','1<=seconds<=32400')
rows.append(save('control/mcp_persistente_v3_R04.py',s))
s=(ROOT/'control/world_comprimido_v3_R03.py').read_text('utf8').replace('run_integrated_v3_R03.py','run_integrated_v3_R04.py').replace('_r07_original_world_base_R03','_r07_original_world_base_R04')
s=s.replace('mcp_persistente_v3.py','mcp_persistente_v3_R04.py').replace('remaining=min(14400,','remaining=min(32400,')
rows.append(save('control/world_comprimido_v3_R04.py',s))
s=epochs((ROOT/'control/run_integrated_v3_R03.py').read_text('utf8'))
s=s.replace('2026-11-16T21:07:00Z','2026-11-17T00:07:00Z').replace('2026-11-16T20:00:00Z','2026-11-16T23:00:00Z')
s=s.replace('world_comprimido_v3_R03.py','world_comprimido_v3_R04.py').replace('owner_support_v3.py','owner_support_v3_R04.py')
rows.append(save('control/run_integrated_v3_R04.py',s))
proof={'schema':'DEE.R07.prospective_lease_code.R04','prepared_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'original_start_epoch':1794841620,'old_last_new_epoch':OLD_LAST,'old_hard_finish_epoch':OLD_END,'new_last_new_epoch':NEW_LAST,'new_hard_finish_epoch':NEW_END,
 'scope':'Future closed migration only. No operational Native files changed; live Main29..34 remains old lease.',
 'Native_calls':0,'MCP_calls':0,'actor_AST_equal_after_normalizing_only_two_lease_constants_and_error_labels':True,
 'unchanged':['Native VERSION/KEY','MAX cycles','160000 aggregate tick budget','512MiB jobs','RAW10000','tick-block16','reader/decoder','feedback','teaching','physics','policy'],
 'files':rows}
with(ROOT/'control/CODIGO_LEASE_R04_PREPARADO.json').open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
print(json.dumps(proof,ensure_ascii=False))
