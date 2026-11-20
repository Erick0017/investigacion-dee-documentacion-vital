"""Directed repeat in a different working location; no private paths or fixtures."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import dee_thinking as d
from laboratorio import learned_mobile,mobile_query,physical,reading
from sesion import Session


def main(a):
    package=Path(a.package).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    w,_=learned_mobile((12,16),cue=0);q,_=mobile_query(w,17,protocol='directed_reproduction');got=[r['s_reg'] for r in q['responses']];assert got==[29,33]
    saved=package/'casos/C08_INTERFACE_V2/C08_MAIN_FINAL.deetsnap';s=Session.load(saved);loaded=physical(s.world);assert loaded['tick']==26
    s.signal('s1',4);s.advance_to(31);outputs=[o['s_reg'] for o in s.state['frames'][-1]['outputs']];assert outputs==[106,110]
    s.save(out/'C08_CONTINUED_T31.deetsnap');c=Session.load(out/'C08_CONTINUED_T31.deetsnap');assert physical(c.world)==physical(s.world) and c.state==s.state
    result={'version':d.__version__,'module':d.__file__,'native_module':d.build_info(),'working_directory':str(Path.cwd()),'output_directory':str(out),'package_root':str(package),
            'fresh_case_C02_query17':q,'C08_loaded':loaded,'C08_continued':physical(s.world),'C08_response_after_real_advance':outputs,'continued_not_reconstructed':True,
            'checkpoint_sha256':hashlib.sha256((out/'C08_CONTINUED_T31.deetsnap').read_bytes()).hexdigest(),'source_roles':'C02 replay is technical reproducibility, not an independent scientific sample; C08 advances the saved lineage'}
    (out/'REPRODUCTION_CHECK.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({'C02':got,'C08':outputs,'restoration_same_future':True},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package',required=True);p.add_argument('--output',required=True);main(p.parse_args())
