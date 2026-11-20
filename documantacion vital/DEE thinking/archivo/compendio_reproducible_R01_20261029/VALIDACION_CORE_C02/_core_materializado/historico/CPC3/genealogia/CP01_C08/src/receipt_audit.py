"""Passive audit of actual retained native admission receipts, not declared zeros."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import dee_thinking as d
from laboratorio import receipt
from supervision import atomic_json


def main(root):
    root=Path(root).resolve();rows=[]
    for cp in sorted((root/'casos').rglob('*.deetsnap')):
        w=d.OrganizationalWorld.load_snapshot(str(cp));metadata=w.runtime.snapshot_metadata('cp01.session.v1')
        if not metadata:continue
        s=json.loads(metadata);events=[]
        for event in s['events']:
            events.append({'recorded_host_operation':event,'actual_native_receipts':[receipt(w.runtime.receipt(i)) for i in event.get('receipt_ids',[])]})
        rows.append({'checkpoint':cp.relative_to(root).as_posix(),'tick':w.runtime.current_tick,'host_operations_and_effective_admission':events,'pending_protocol_inputs':s['pending'],
                     'external_habitat_state':s['environment'],'scope':'native receipts retained by snapshot; the same operation may occur in several checkpoints and is not recounted as a new experience'})
    atomic_json(root/'resultados/ACTUAL_RECEIPT_AUDIT.json',{'role':'passive technical audit','session_checkpoints':rows,'direct_memory_clock_edits_in_session_runner':False,
        'evidence_for_last_property':'src/sesion.py uses submit/probe for physical input and set_snapshot_metadata for observer/protocol persistence; diagnostic edits are explicit in src/causal_lab.py and laboratory forks','zeros_are_not_absence':True})
    print(json.dumps({'session_checkpoints_with_native_receipts':len(rows)}))


if __name__=='__main__':main(sys.argv[1])
