"""Functional directional consequence of a selective late regulator cut."""
from pathlib import Path
from copy import deepcopy
import argparse
import gc
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from integracion.quantity_core import physical
from regulacion_acoplada.mcts import CoupledMagnitudeCTSSession
from regulacion_acoplada.aparato import move


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    directory = ROOT / 'resultados/regulacion_acoplada/RCAM_R201_FUNCTION_PLUS'
    primary = json.loads((directory / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
    base = directory / 'T77.deetsnap.gz'
    base_hash = hashlib.sha256(base.read_bytes()).hexdigest()
    parent = CoupledMagnitudeCTSSession.load(base)
    parent_physical = physical(parent.world)
    parent_receipts = [exact_receipt(item) for item in parent.world.runtime.receipts]
    site = parent.geometry['coupled_regulation']['counterflows']['P']['pre_interception_site']
    before = parent.observe(site)
    assert before['active'] and before['s_reg'] == 114 and before['direction'] == [-1,0,0]
    pre_Moore27 = [parent.observe(move(site, (x,y,z))) for x in (-1,0,1) for y in (-1,0,1) for z in (-1,0,1)]
    rows = []
    for condition in ('formed_counterflow_RAWcut_T77', 'formed_counterflow_RAWsham_T77'):
        edit = d.ResearchStateEdit()
        edit.coordinate = d.Coordinate(*site)
        edit.raw = int(before['raw']) if 'sham' in condition else 0
        edit.clock = None
        edit.label = condition
        world = parent.world.diagnostic_fork([edit], True)
        session = CoupledMagnitudeCTSSession(world, parent.geometry, deepcopy(parent.state), parent.identifier)
        row = {'case_id': 'RCAM_R201_FUNCTION_PLUS', 'condition': condition, 'modality': 'DIAGNOSTIC_FORK',
               'base': base.relative_to(ROOT).as_posix(), 'base_sha256': base_hash, 'new_inputs': 0,
               'intervention': {'before':before,'after':session.observe(site),'pre_Moore27':pre_Moore27,
                                'clock_preserved':before['clock'] == session.observe(site)['clock']}, 'frames':[]}
        for tick in (77,78,79,136,137,141,147,206,214,281,428,549,554,559,563,616):
            session.run_until(tick)
            frame = session.view()
            frame['mode'].pop('captures',None)
            frame['mode'].pop('social_captures',None)
            row['frames'].append(frame)
        pre = next(frame['coupled_regulation']['quantity'] for frame in row['frames'] if frame['tick'] == 136)
        post = next(frame['coupled_regulation']['quantity'] for frame in row['frames'] if frame['tick'] == 137)
        row['later_reading'] = {'reference':pre['reference_site'],'object':pre['object_site'],'output':post['center'],
                                'actual_operand_criterion':pre['reference_site']['s_reg']==36 and pre['object_site']['s_reg']==42,
                                'directional_task_correct':post['center']['active'] and post['center']['direction']==[-1,0,0]}
        row.update(final_physical=physical(world),full_final_equal_original=physical(world)==primary['final_physical'],
                   receipts_equal_original=[exact_receipt(item) for item in world.runtime.receipts] == sorted([item['receipt'] for item in primary['requests']],key=lambda item:item['id']),
                   parent_unchanged=physical(parent.world)==parent_physical and [exact_receipt(item)for item in parent.world.runtime.receipts]==parent_receipts,
                   base_file_unchanged=hashlib.sha256(base.read_bytes()).hexdigest()==base_hash)
        row['snapshot'] = session.save(args.out / (condition + '_T616.deetsnap.gz'))
        assert row['intervention']['clock_preserved'] and row['parent_unchanged'] and row['base_file_unchanged']
        if 'sham' in condition:
            assert row['full_final_equal_original'] and row['receipts_equal_original']
        rows.append(row)
        put(args.out/'INCREMENTAL.json',rows)
        del session,world
        gc.collect()
    result={'schema':'CPC8R.coupled.regulation.functional.causal.v1','status':'MEASURED','preparations':0,
            'diagnostic_forks':2,'technical_continuations':0,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'configuration_sha256':hashlib.sha256((ROOT/'configuraciones/regulacion_acoplada/PAR_FUNCIONAL_CONGELADO.json').read_bytes()).hexdigest(),'rows':rows}
    put(args.out/'MEASUREMENTS.json',result)
    print(json.dumps({'rows':[(row['condition'],row['later_reading'])for row in rows]}))


if __name__ == '__main__':
    main()
