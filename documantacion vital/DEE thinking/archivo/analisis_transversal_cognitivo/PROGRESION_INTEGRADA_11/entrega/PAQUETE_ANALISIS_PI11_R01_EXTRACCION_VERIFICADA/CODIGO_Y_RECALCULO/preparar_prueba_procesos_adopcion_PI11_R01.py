"""Fresh read-only scoped PI11 movement proof using the preserved strict guard.

No DEE, Native, Owner or Store import and no state/queue/process modification.
The existing checker alone inspects PID/locks and immutable read-only SQLite.
Run only under the exclusive Root coordinator after the actual owners close.
--phase before-move checks selected PI10 + diagnostic MAIN; after-move checks
selected PI10 + moved MAIN. Stdout is the exact motor proof schema. Optional
--output creates a previously nonexistent JSON inside this PI11 campaign.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json

H = Path(__file__).resolve().parent
P = H.parent
C = P.parents[2] / 'DEE Cognitive 2.0'
S = C / 'sistema'
PARENT = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
MAIN = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_MAIN01'
CHECKER = H / 'comprobar_proceso_PI11_R01.py'
CHECKER_SHA = 'e7fa5a807ec334b001150b858b88fe2e14a738053322f19ee41552a164764f27'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def regular(path):
    for node in (Path(path), *Path(path).parents):
        need(not node.is_symlink() and not (node.exists() and getattr(node.lstat(), 'st_file_attributes', 0) & 1024), 'Linked/reparse process-proof path refused')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--phase', choices=('before-move', 'after-move'), required=True)
    ap.add_argument('--source-system', type=Path)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    need(sha(CHECKER) == CHECKER_SHA, 'Preserved PI11 strict process guard changed')
    if args.phase == 'before-move':
        need(args.source_system is not None, 'Exact diagnostic MAIN source required before movement')
        regular(args.source_system)
        candidate_system = args.source_system.resolve(strict=True)
        need(candidate_system.name == 'sistema' and candidate_system.parent.parent == (P / 'estados').resolve()
             and not (candidate_system / 'estado/ACTIVO.json').exists(), 'Unselected PI11 diagnostic source only')
    else:
        need(args.source_system is None, 'After movement MAIN is inspected only in the product')
        candidate_system = S.resolve(strict=True)
    if args.output:
        regular(args.output)
        output = args.output.resolve(strict=False)
        need(output.is_relative_to(P.resolve()) and output.suffix == '.json'
             and output.parent.is_dir() and not output.exists(), 'New campaign JSON output only')
    spec = importlib.util.spec_from_file_location('PI11_exact_strict_process_guard_for_final_movement', CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    evidence = [checker.inspect('PI11_adoption_protected_PI10', S, PARENT),
                checker.inspect('PI11_adoption_MAIN_' + args.phase, candidate_system, MAIN)]
    need(all(row.get('no_live_affected_writer') is True for row in evidence), 'A scoped writer/queue/marker check failed; preserve the condition and do not move/adopt')
    proof = {'schema': 'DEE.PI11.fresh_scoped_adoption_process_proof.R01',
             'recorded_utc': datetime.now(timezone.utc).isoformat(), 'no_live_affected_writers': True,
             'scope': {'phase': args.phase, 'protected_system': str(S.resolve()),
                       'candidate_system': str(candidate_system), 'checker_sha256': CHECKER_SHA,
                       'valid_for_seconds': 600, 'intended_use': 'Exact PI11 administrative relocation/adoption; regenerate immediately before each phase'},
             'evidence': evidence, 'affected_life_ids': [PARENT, MAIN],
             'DEE_imported': False, 'Native_executed': False, 'new_Native_ticks': 0,
             'states_queues_locks_processes_modified': False}
    if args.output:
        with output.open('x', encoding='utf8', newline='\n') as f:
            json.dump(proof, f, ensure_ascii=False, indent=2)
            f.write('\n')
    print(json.dumps(proof, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
