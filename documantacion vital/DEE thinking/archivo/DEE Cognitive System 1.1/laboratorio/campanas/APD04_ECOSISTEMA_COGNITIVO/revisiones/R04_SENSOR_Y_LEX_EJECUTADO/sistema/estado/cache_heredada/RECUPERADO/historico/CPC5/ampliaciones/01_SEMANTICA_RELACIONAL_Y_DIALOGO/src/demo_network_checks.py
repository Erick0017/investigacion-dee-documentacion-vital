"""Post-trajectory checks only. Never imported by a participant or renderer."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,digest,operational

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def observations(data):
    return [{'tick':r['response']['readout']['tick'],'readout':r['response']['readout']}
            for r in data['commands'] if 'readout' in r.get('response',{})]
def normalized(world):
    op=operational(world);cache={k:v for k,v in op['metadata'].items() if k.startswith('dee_thinking.organizational.')}
    op['metadata']={k:v for k,v in op['metadata'].items() if not k.startswith('dee_thinking.organizational.')}
    return op,cache
def main():
    p=argparse.ArgumentParser();p.add_argument('--generated',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    import dee_thinking as d
    rows=[]
    for label,baseline,checkpoint in [('red','demo_red3_01','RED3_T204.deetsnap'),('red_continuado','demo_red3_continuacion_01','RED3_T338.deetsnap')]:
        actual_dir=a.generated/label;expected_dir=ROOT/'resultados'/baseline
        actual=read(actual_dir/'DEMO_RESULT.json');expected=read(expected_dir/'DEMO_RESULT.json')
        wa=d.OrganizationalWorld.load_snapshot(str(actual_dir/checkpoint));wb=d.OrganizationalWorld.load_snapshot(str(expected_dir/checkpoint))
        oa,ca=normalized(wa);ob,cb=normalized(wb)
        checks={'no_rejected_commands':actual['rejected_commands']==0,'readouts_exact':observations(actual)==observations(expected),
                'RAW_complete':wa.runtime.raw_copy()==wb.runtime.raw_copy(),'clocks_complete':wa.runtime.clock_copy()==wb.runtime.clock_copy(),
                'tick':wa.runtime.current_tick==wb.runtime.current_tick,'operative_and_network_session':oa==ob}
        rows.append({'run':label,'verified':all(checks.values()),'checks':checks,'framework_cache_equal_separately':ca==cb,
                     'checkpoint':checkpoint,'physical':digest(wa),'baseline_sha256':sha(expected_dir/'DEMO_RESULT.json'),
                     'actual_sha256':sha(actual_dir/'DEMO_RESULT.json')})
    report={'schema':'CPC5.extension.public-network-checks.v1','verified':all(r['verified'] for r in rows),
            'comparisons_after_trajectories_only':True,'rows':rows,
            'scope':'Technical replay of the exact three-role public walkthrough and its other-process continuation, not additional independent learning worlds. Only opaque framework serialization cache is compared separately; no physical field is normalized.'}
    put(a.output,report);assert report['verified'];print(json.dumps({'verified':True,'states':len(rows)}))
if __name__=='__main__':main()
