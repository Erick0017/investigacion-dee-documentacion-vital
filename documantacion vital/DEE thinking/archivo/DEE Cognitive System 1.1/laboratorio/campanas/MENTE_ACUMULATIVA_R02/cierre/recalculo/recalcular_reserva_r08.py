"""MA02 R08 reserved global trace/admission analysis, stdlib archived data only."""
import argparse
import importlib.util
import json
from pathlib import Path

spec=importlib.util.spec_from_file_location('reserve_archived',Path(__file__).with_name('recalcular_reserva_r07.py'))
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();x=r.calculate(a.evidencia,revision_name='R08',transpose=False)
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'issues':len(x['issues']),'global_RAW_frames_verified':sum(len(q['joint']['frame_hashes'])for q in x['cases']),
        'matched_revision':x['matched_revision'],'answers':{q['arm']:q['joint']['decoded_sign']for q in x['cases']}},ensure_ascii=False))
    return 1 if x['issues']else 0

if __name__=='__main__':raise SystemExit(main())
