"""Public-demo continuation and external checks; never used as a participant."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import identity, digest, operational, receipt, put, sha
from compound import CompoundSession


def continuation(snapshot,output):
    if output.exists():raise FileExistsError('Continuation output is protected')
    output.mkdir(parents=True)
    engine=identity();session=CompoundSession.load(snapshot)
    before=digest(session.world);operative_before=operational(session.world)
    ids=[session.query(name,payload=7) for name in ('K1','K2','K3','K4')]
    at=session.world.runtime.receipt(ids[0]).requested_tick
    session.run_until(at+3)
    result={'schema':'CPC5.demo.other_process.v1','kind':'TECHNICAL_PUBLIC_CONTINUATION',
            'engine':engine,'input_snapshot':snapshot.name,'snapshot_sha256':sha(snapshot),
            'before':before,'operative_before':operative_before,
            'input_tick':at,'readout':session.observe(),
            'receipts':[receipt(session.world,i) for i in ids],
            'after':digest(session.world),'operative_after':operational(session.world),
            'scope':'A new physical query after restoring the same operative individual; no teaching map or measurements loaded.'}
    session.save(output/'CONTINUED.deetsnap')
    put(output/'CONTINUATION.json',result)
    return result


def verify(output,reference=None):
    result=json.loads((output/'DEMO_RESULT.json').read_text(encoding='utf-8'))
    rows=[json.loads(x) for x in (output/'DIALOGO.jsonl').read_text(encoding='utf-8').splitlines()]
    checks={'no_command_rejections':not any('rejected_command' in row['result'] for row in rows),
            'commands_match_summary':len(rows)==result['commands'],'physical_tick':result['final_physics']['tick'],
            'origin_labels_present':all('origin' in row['result'] or row['result'].get('kind')=='EXPERIENCE_PROTOCOL' for row in rows)}
    if reference:
        prior=json.loads(reference.read_text(encoding='utf-8'))
        checks['same_frozen_demo_physics']=prior['final_physics']==result['final_physics']
    if any(v is False for v in checks.values()):raise AssertionError(checks)
    return checks


def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['continue','verify'])
    p.add_argument('--input',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--reference',type=Path)
    a=p.parse_args();result=continuation(a.input,a.output) if a.mode=='continue' else verify(a.output,a.reference)
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
