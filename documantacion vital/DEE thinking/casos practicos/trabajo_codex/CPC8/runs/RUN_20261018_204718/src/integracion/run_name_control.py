"""Explicit fixed linguistic-exposure controls, in the third geometry.

The selected exposure arm is frozen before Runtime creation. No observation
selects a word, response, decoder, physical history, or interface. The finite
protocol in run_alias is reused transparently and its exact source is saved.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys
SRC=Path(__file__).resolve().parents[1];sys.path.insert(0,str(SRC))
from integracion import run_alias
from integracion.relocated_lower import RelocatedSession


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    config=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in config['cases'] if c['id']==a.case_id)
    mode=case['name_mode']
    if mode not in('omitted','unpaired'):raise ValueError('Frozen omitted or one-tick delayed exposure control required')
    class NameControlSession(RelocatedSession):
        def teach_name(self,requested_mode='paired',payload=5):
            return super().teach_name(mode,payload)
    adapter={'selection_modality':'FIXED_EXPERIMENTAL_EXPOSURE_ARM_BEFORE_T0; never response-based',
        'factory':'integracion.relocated_lower.RelocatedSession','name_exposure':mode,
        'input_tick':None if mode=='omitted' else 137,'nominal_contact_tick':None if mode=='omitted' else 140,
        'candidate_interfaces':4,'submitted_cues':0 if mode=='omitted' else 4,'each_payload':5,'scope':'Third geometry unchanged; identical L17 acquisition, native question, action and fixed word reader.',
        'sources':{x.name:run_alias.sha(x) for x in(Path(__file__),SRC/'integracion/relocated_lower.py')}}
    original_put=run_alias.put
    def instrumented_put(path,value):
        if Path(path).name=='MEASUREMENTS.json':value={**value,'factory_adapter':adapter}
        return original_put(path,value)
    run_alias.AliasSession=NameControlSession;run_alias.put=instrumented_put
    run_alias.execute(case,a.out,a.config)
    for source in(Path(__file__),SRC/'integracion/relocated_lower.py'):shutil.copyfile(source,a.out/'executed_source'/source.name)


if __name__=='__main__':main()
