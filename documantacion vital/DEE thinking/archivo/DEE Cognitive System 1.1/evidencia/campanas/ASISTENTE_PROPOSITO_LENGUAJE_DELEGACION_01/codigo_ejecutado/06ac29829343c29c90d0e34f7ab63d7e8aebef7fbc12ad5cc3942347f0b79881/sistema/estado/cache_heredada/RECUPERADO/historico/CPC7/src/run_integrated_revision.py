"""Fresh one-case CLI around the frozen integrated scientific executor."""
import argparse
import json
from pathlib import Path
import shutil
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import put,sha
import integrated_revision


def checks(m,case_directory):
    return {'schema':'CPC7.integrated_revision.checks.v1','case_id':m['case']['id'],'final_tick':m['final_physical']['tick'],
        'preparations':m['preparations'],'same_RUNTIME':m['same_RUNTIME'],
        'base338_lower':m['base338']['calculations']['lower_repertoire']['338'],
        'native_question19':len(json.loads((Path(case_directory)/m['base338']['path']).read_text(encoding='utf8'))['native_questions']),
        'opaque_covered142':m['base338']['calculations']['opaque_covered'],
        'post472':m['calculations'],'host_RAW_clock_writes_on_MAIN':m['host_RAW_clock_writes_on_MAIN'],
        'final_physical':m['final_physical'],'scope':'Post-trajectory checks, never an input or response oracle.'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case-id',required=True);a=p.parse_args()
    cfg=json.loads(a.config.read_text(encoding='utf8'));selected=[c for c in cfg['cases'] if c['id']==a.case_id]
    if len(selected)!=1:raise ValueError('Exactly one configured case_id required')
    target=a.out/a.case_id
    if target.exists():raise FileExistsError('Fresh execution refuses an existing case directory: '+str(target))
    m=integrated_revision.execute(selected[0],target,sha(a.config))
    shutil.copyfile(__file__,target/'executed_source/run_integrated_revision.py')
    result=checks(m,target);put(target/'CHECKS.json',result);put(a.out/'CHECKS.json',result)
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
