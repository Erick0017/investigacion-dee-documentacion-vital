"""FS-only deadline copies; preserves every R05 source. No Native imports."""
from pathlib import Path
import ast,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def create(target,text):
    ast.parse(text)
    with target.open('x',encoding='utf8',newline='\n')as f:f.write(text)
def replace_time(text):return text.replace('1794880800','1794902400').replace('1794884820','1794906420')
def run():
    bundle=ROOT/'native/lease_R06_bundle';need(not bundle.exists(),'FRESH_BUNDLE');bundle.mkdir()
    sources=[]
    for name in('rbx07_native_v3.py','rbx07_identity_v3.py','rbx07_funciones_v3.py'):
        old=ROOT/'native/lease_R05_bundle'/name;target=bundle/name
        if name=='rbx07_native_v3.py':
            need(sha(old)=='89fe4343694b546d480b6d80d73af6d6d6813fec1b67b9f5a067d96846c03b4e','EXACT_12H_ACTOR')
            text=old.read_text('utf8');need(text.count('1794880800')==1 and text.count('1794884820')==1,'TWO_DATE_LITERALS_ONLY')
            changed=replace_time(text)
            norm=lambda s:s.replace('1794880800','DATE_LAST').replace('1794902400','DATE_LAST').replace('1794884820','DATE_END').replace('1794906420','DATE_END')
            need(ast.dump(ast.parse(norm(text)))==ast.dump(ast.parse(norm(changed))),'ACTOR_AST_IDENTICAL_EXCEPT_TWO_DATES')
            create(target,changed)
        else:
            with target.open('xb')as f:f.write(old.read_bytes())
        sources.append({'file':str(target.relative_to(ROOT)),'bytes':target.stat().st_size,'sha256':sha(target),'original_preserved_sha256':sha(old)})
    for old_name,new_name in(('ledger_v3_R05.py','ledger_v3_R06.py'),('owner_support_v3_R05.py','owner_support_v3_R06.py')):
        old=ROOT/'native'/old_name;text=replace_time(old.read_text('utf8'))
        if 'owner_support'in old_name:
            text=text.replace('ledger_v3_R05.py','ledger_v3_R06.py').replace('LEASE_APPLIED_R05.json','LEASE_APPLIED_R06.json')
        target=ROOT/'native'/new_name;create(target,text)
        sources.append({'file':str(target.relative_to(ROOT)),'bytes':target.stat().st_size,'sha256':sha(target),'original_preserved_sha256':sha(old)})
    path=ROOT/'control/FUENTES_LEASE_R06_PREPARADAS.json'
    with path.open('x',encoding='utf8')as f:json.dump({'original_start_epoch':1794841620,'last_new_epoch':1794902400,'hard_finish_epoch':1794906420,
      'Native_calls':0,'no_policy_sensor_reader_or_reward_change':True,'files':sources},f,indent=2)
    print(json.dumps({'sources':len(sources),'manifest':str(path),'sha256':sha(path)},indent=2))
if __name__=='__main__':run()
