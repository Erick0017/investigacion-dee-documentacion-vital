"""Root-only prospective world slots, unchanged tick/time/memory/storage limits."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,os,shutil
P=Path(__file__).resolve().parents[1];F=P/'REGISTRO_CAMPANA.json';O=P/'control/REVISION_PROSPECTIVA_MUNDOS_PI09_R02.json'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(a):
 if not a.aplicar:print(json.dumps({'mode':'PLAN_ONLY','old_world_limit':12,'proposed_world_limit':16,'other_limits_change':False,'Native_executed':False}));return
 assert not O.exists()and not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists()
 adopted=read(P/'control/ADOPCION_PRODUCTO_PI09.json');assert adopted['phase']=='COMMITTED'
 r=read(F);old=dict(r['budget']);assert old['diagnostic_worlds_all_new']==12 and old['Native_ticks_all_branches']==220000 and old['owned_Native_job_memory_bytes']==536870912
 assert datetime.now(timezone.utc)<datetime.fromisoformat(old['new_experimental_uses_cutoff_local'])
 code=P/'codigo/ledger_PI09_misma_identidad_R01.py'
 assert sha(code)=='bb1f326aa981ba00b9a6e3417700cca31d92a0d28a6e8a5ad601042bf2a26260'
 s=importlib.util.spec_from_file_location('PI09_prospective_budget_ledger',code);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);ledger=m.ledger()
 assert ledger['world_count']<=12 and ledger['ticks']+27360+13000<=220000
 backup=P/'control/REGISTRO_ANTES_REVISION_MUNDOS_PI09_R02.json';shutil.copyfile(F,backup)
 reason='Prospective additional diagnostic identities for usable RP fresh-ID cold12 (priority), D None/Yoke/replay, and optional separate contextual WSLS reference. Main/D real reuse existing identities. No new engine, cognition or memories are copied between worlds. Slots are ceilings, not mandatory experiments.'
 r.setdefault('initial_budget_literal',old);r['budget']['diagnostic_worlds_all_new']=16
 changes={k:{'before':old[k],'after':r['budget'][k]}for k in old if old[k]!=r['budget'][k]};assert set(changes)=={'diagnostic_worlds_all_new'}
 v={'schema':'DEE.PI09.prospective_world_budget_revision.R02','recorded_utc':datetime.now(timezone.utc).isoformat(),'reason':reason,'changes':changes,'initial_record':{'path':str(backup),'sha256':sha(backup)},'current_saved_ledger':ledger,'unchanged_limits':{k:v for k,v in old.items()if k!='diagnostic_worlds_all_new'},'allocation_order':['RP_R04 actual fresh-ID cold12, bound27360 and explicit closure reserve13000','D only if actual then-current ticks + bound78372 + closure reserve13000 fits220000','Optional WSLS6 only after actual D evidence, with bound13063 AND closing reserve still available'],'initial_budget_fixed_once_preserved_as_history':True,'prospective_only_no_retroactive_limit_change':True,'Native_executed':False}
 r.setdefault('budget_revisions',[]).append({'path':str(O),'changes':changes,'reason':reason,'recorded_utc':v['recorded_utc']});r['budget_fixed_once']=False;r['initial_budget_fixed_once']=True
 temp=F.with_name(F.name+'.PI09REV');temp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf8');os.replace(temp,F)
 O.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'proof':str(O),'sha256':sha(O),'world_limit':16,'Native_ticks_limit':220000,'current_ticks':ledger['ticks'],'worlds':ledger['world_count'],'Native_executed':False}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--aplicar',action='store_true');main(p.parse_args())
