"""Replay archived commands only in the declared external model, no DEE life.

This is environmental reproduction, not new native learning or a host policy.
"""
from pathlib import Path
import sys,json,argparse,hashlib
def same(a,b):
    if isinstance(a,float)and isinstance(b,float):return a.hex()==b.hex()
    if isinstance(a,dict)and isinstance(b,dict):return set(a)==set(b)and all(same(a[k],b[k])for k in a)
    if isinstance(a,list)and isinstance(b,list):return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
    return a==b
def main():
    p=argparse.ArgumentParser();p.add_argument('--system-root',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.system_root))
    from capacidades.habitat_externo_01 import _Worker
    cases=['COST_NATIVE_73_PREFIX3.json','INTEGRATED_COST_SOCIAL_132_CONTINUE9.json','OPERATIONAL_RECOVERY_AGED_4_170.json','OPERATIONAL_RECOVERY_AGED_5_170.json'];results=[];w=_Worker()
    try:
        for name in cases:
            source=a.evidence/name;d=json.loads(source.read_text(encoding='utf8'));r=d['result'];w.call('restore',snapshot=r['initial_environment']);checks=[]
            for row in r['rows']:
                got=w.call('step',torque=row['executed_torque']);checks.append({'index':row['index'],'response_float_hex_and_structure_equal':same(got,row['response'])})
            final=w.call('snapshot')['snapshot'];expected=r['final_environment']['environment'];results.append({'file':name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'steps':len(checks),'per_step':checks,'exact_final_environment_equal':same(final,expected)})
    finally:w.close()
    out={'native_ticks':0,'DEE_lives_created_or_advanced':0,'kind':'REPRODUCTION_OF_DECLARED_EXTERNAL_MODEL_FROM_ARCHIVED_COMMANDS','not_new_learning':True,'results':results}
    a.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if not all(r['exact_final_environment_equal']and all(c['response_float_hex_and_structure_equal']for c in r['per_step'])for r in results):raise AssertionError('External model replay mismatch')
    print(json.dumps({'native_ticks':0,'reproduced_external_steps':sum(r['steps']for r in results),'exact_cases':len(results)}))
if __name__=='__main__':main()
