"""Post-trajectory physical-readout checks for the finite renewed public demo.

This auditor does not supply a target, select a lane or alter participant state.
It compares actual products in the already-ended T53/T90/T162 windows.
"""
import argparse,json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import put,sha


def load(path):return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line]


def find(rows,command):
    matches=[(i,x) for i,x in enumerate(rows) if x['command']==command]
    assert len(matches)==1,(command,len(matches));return matches[0]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--demo',type=Path,required=True)
    p.add_argument('--continued',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    main_path=a.demo/'DIALOGOS.jsonl';continuation_path=a.continued/'DIALOGOS.jsonl'
    rows,continuation=load(main_path),load(continuation_path)
    i1,r1=find(rows,'avanzar 53');i2,r2=find(rows,'avanzar 90');ir,rr=find(continuation,'avanzar 162')
    ip,rp=find(rows,'avanzar 5');ifin,rf=find(continuation,'avanzar 170')
    first=r1['result']['emissions'];second=r2['result']['order_emissions'];later=rr['result']['renewed_emissions']
    first_values=sorted(x['directional_relation'] for x in first);later_values=sorted(x['directional_relation'] for x in later)
    before_delta=rp['result']['observation']['body']['delta'];after_delta=rf['result']['observation']['body']['delta']
    cp=json.loads((a.continued/'CONTINUATION.json').read_text(encoding='utf-8'))
    checks={'first_opaque_sign_product53':bool(first),'second_opaque_sign_product90':bool(second),
      'renewed_product162':bool(later),'same_directional_relation53_and162':bool(first_values) and first_values==later_values,
      'original_relation_still_measurable170':before_delta is not None and before_delta==after_delta,
      'continuity105_to170':cp['initial_physical']['tick']==105 and cp['final_physical']['tick']==170 and cp['continuation_completed']}
    receipts={int(x['id']):x['receipt'] for x in cp['requests_and_receipts']};counts={}
    for value in receipts.values():counts[value['status']]=counts.get(value['status'],0)+1
    report={'schema':'CPC6.public-output-check.v1','classification':'POST_TRAJECTORY_INSTRUMENT',
      'verified':all(checks.values()),'checks':checks,'first_sign':first,'second_sign':second,'renewed_first_sign':later,
      'original_body_delta':{'tick5':before_delta,'tick170':after_delta,'scope':'Passive relation; prior function also expressed by the physical FORM02 product90.'},
      'receipt_counts_unique_native_ids':counts,'receipts_total':len(receipts),
      'primary_pointers':{'first':{'file':'demo/DIALOGOS.jsonl','line_1_based':i1+1,'pointer':'/result/emissions'},
        'second':{'file':'demo/DIALOGOS.jsonl','line_1_based':i2+1,'pointer':'/result/order_emissions'},
        'renewed':{'file':'continued/DIALOGOS.jsonl','line_1_based':ir+1,'pointer':'/result/renewed_emissions'}},
      'source_sha256':sha(Path(__file__)),'input_sha256':{'demo_dialogue':sha(main_path),'continued_dialogue':sha(continuation_path)},
      'scope':'Finite physical responses and continuity only. Opaque forms are not automatically NSM meanings. Rejected/absent/ambiguous input statuses are retained rather than coerced to zero. No reference or calculation was returned to the participant.'}
    put(a.output,report);print(json.dumps({'verified':report['verified'],'checks':checks,'native_receipts':counts}));assert report['verified']


if __name__=='__main__':main()
