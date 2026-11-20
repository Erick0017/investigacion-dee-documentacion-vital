"""Compare a completed regenerated native trajectory with its sealed reference.

This is an auditor called AFTER the participant process has exited. Its output
never returns to MAIN. Versioned serialization metadata is compared separately.
"""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha

def normalized(value):
    v=json.loads(json.dumps(value))
    if isinstance(v.get('metadata'),dict):
        v['metadata']={k:x for k,x in v['metadata'].items() if not k.startswith('dee_thinking.organizational.')}
    return v

def main():
    p=argparse.ArgumentParser();p.add_argument('--generated',type=Path,required=True);p.add_argument('--source',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    source=ROOT/a.source
    assert source.resolve().is_relative_to(ROOT.resolve()) and source.is_file()
    old=json.loads(source.read_text(encoding='utf-8'));new=json.loads(a.generated.read_text(encoding='utf-8'))
    result={'schema':'CPC7.completed_native_reproduction.v1','source_member':a.source,'source_sha256':sha(source),
            'generated_sha256':sha(a.generated),'case_equal':old['case']==new['case'],
            'physical_equal':old['final_physical']==new['final_physical'],
            'operative_equal_without_serialization_envelope':normalized(old['final_operational'])==normalized(new['final_operational']),
            'calculated_results_equal':old['calculations']==new['calculations'],
            'scope':'Posttrajectory instrument; exact physical RAW/clock/tick hashes and operative session, not byte equality of refreshed serialization metadata.'}
    if 'base338' in old:
        result['pre_revision_physical_equal']=old['base338']['final_physical']==new['base338']['final_physical']
        result['pre_revision_calculations_equal']=old['base338']['calculations']==new['base338']['calculations']
    put(a.out,result)
    assert all(value for key,value in result.items() if key.endswith('_equal') or key.startswith('operative_equal_'))
    print(json.dumps({'physical_equal':result['physical_equal'],'case':old['case']['id']}))

if __name__=='__main__':main()
