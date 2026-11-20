"""Compare completed fresh replays to frozen primary data, after trajectories.

The expected directory is never passed to the participant or scenario runner.
Negative controls must reproduce their actual states, not be converted to wins.
"""
import argparse,json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import put,sha
from check_snapshot_equivalence import compare


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--actual',type=Path,required=True)
    p.add_argument('--expected',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    cases=sorted(path.parent.name for path in a.actual.glob('*/MEASUREMENTS.json'));assert cases
    rows=[]
    for case in cases:
        current=a.actual/case;reference=a.expected/case
        actual_path=current/'MEASUREMENTS.json';expected_path=reference/'MEASUREMENTS.json'
        x=json.loads(actual_path.read_text(encoding='utf-8'));y=json.loads(expected_path.read_text(encoding='utf-8'))
        checks={name:x[name]==y[name] for name in ('case','geometry','rows','requests','predictions','summary','final_physical')}
        current_last=x['snapshots'][-1]['path'];previous_last=y['snapshots'][-1]['path']
        assert Path(current_last).name==current_last and Path(previous_last).name==previous_last
        snapshot=compare(current/current_last,reference/previous_last)
        checks['complete_final_snapshot_physical_and_operative']=snapshot['verified']
        rows.append({'case_id':case,'checks':checks,'verified':all(checks.values()),
          'actual_measurement_sha256':sha(actual_path),'primary_measurement_sha256':sha(expected_path),
          'snapshot_comparison':snapshot,
          'scope':'All measured rows and receipts, including silence/rejection/negative controls, must reproduce. Elapsed seconds and source-container paths are not physical observables.'})
    result={'schema':'CPC6.fresh-scientific-replay.v1','verified':all(x['verified'] for x in rows),'cases_compared':len(rows),
      'classification':'TECHNICAL_REPRODUCTION_NOT_NEW_INDEPENDENT_SAMPLES','cases':rows,
      'comparisons_after_trajectories_only':True,'source_sha256':sha(Path(__file__))}
    put(a.output,result);print(json.dumps({'verified':result['verified'],'cases_compared':len(rows)}));assert result['verified']


if __name__=='__main__':main()
