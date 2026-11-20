"""Explicit preT0 factory adapter; unchanged finite protocol/evaluator reused.

No branch, input content, decoder or result is selected from readouts here.
The new factory and generic native reader are identified on every progress
record, not hidden behind the earlier alias constructor's source hash.
"""
import argparse
from pathlib import Path
import shutil
import sys
SRC=Path(__file__).resolve().parents[1];sys.path.insert(0,str(SRC))
from integracion import run_alias
from integracion.relocated_lower import RelocatedSession


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--parent',type=Path);p.add_argument('--diagnostic',choices=('cut','sham'));a=p.parse_args()
    if bool(a.parent)!=bool(a.diagnostic):p.error('Explicit parent and diagnostic mode required together')
    import json
    config=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in config['cases'] if c['id']==a.case_id)
    adapter={'selection_modality':'EXPLICIT_RESEARCH_FACTORY_BEFORE_T0_OR_TYPED_RESTORE; no response-based selection',
        'factory':'integracion.relocated_lower.RelocatedSession','scope':'Third and final geometry family; not an unmodified native fixed-form factory',
        'sources':{x.name:run_alias.sha(x) for x in (Path(__file__),SRC/'integracion/relocated_lower.py')}}
    original_put=run_alias.put
    def instrumented_put(path,value):
        if Path(path).name=='MEASUREMENTS.json':value={**value,'factory_adapter':adapter}
        return original_put(path,value)
    # This chooses a complete initial Research construction, not an answer.
    run_alias.AliasSession=RelocatedSession;run_alias.put=instrumented_put
    run_alias.execute(case,a.out,a.config,parent=a.parent,diagnostic=a.diagnostic)
    for source in (Path(__file__),SRC/'integracion/relocated_lower.py'):shutil.copyfile(source,a.out/'executed_source'/source.name)


if __name__=='__main__':main()
