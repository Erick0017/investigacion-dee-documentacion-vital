"""Two selected published CPC5 references, not a new integrated65-meaning claim."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha
from repertoire_reference import run_case

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    base=ROOT/'genealogia/CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO'
    config=base/'configuraciones/capacity_confirmation.json'
    selected=('CAP_C65_NO_EVENT','CAP_H65_NEW_HISTORY_Q9')
    cases=[c for c in json.loads(config.read_text(encoding='utf-8'))['cases'] if c['id'] in selected]
    assert len(cases)==2
    put(a.out/'FROZEN_SELECTION.json',{'source_configuration':str(config.relative_to(ROOT)),'sha256':sha(config),
        'cases':cases,'scope':'Technical repetition of two published finite preparations; no independent replication claim.'})
    results=[]
    for case in cases:
        m=run_case(case,a.out/case['id'])
        results.append({'id':case['id'],'calculations':m['calculations'],'elapsed_seconds':m['elapsed_seconds'],
                        'checkpoint_restoration_equal':m['technical']['save_load_physical_and_operational_equal'],
                        'primary':case['id']+'/MEASUREMENTS.json','primary_sha256':sha(a.out/case['id']/'MEASUREMENTS.json')})
    put(a.out/'REFERENCE.json',{'schema':'CPC7.reference.capacity65.v1','status':'MEASURED','technical_preparations':2,
        'not_new_scientific_replicates':True,'repertoire_integrated_in_central_U0':False,
        'same_source_as_published_CPC5':sha(ROOT/'src/repertoire_reference.py'),'results':results,
        'scope':'65 opaque forms with two directional content classes, not65 NSM meanings. Control has no paired physical event.'})

if __name__=='__main__':main()
