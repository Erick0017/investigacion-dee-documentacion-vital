"""External post-trajectory replay checks; no observations return to a world."""
import argparse
from array import array
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import put, sha


def physical(world):
    r=world.runtime
    return {'tick':r.current_tick,'N':r.dimension,
            'raw_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
            'clock_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}


def operative(world):
    r=world.runtime
    return {'tick':r.current_tick,'channels':list(r.channel_names),
            'receipts':[{'id':x.id,'kind':str(x.kind),'status':str(x.status),
                        'requested_tick':x.requested_tick,'effective_tick':x.effective_tick,
                        'channels':list(x.channels),'reason':x.reason} for x in r.receipts],
            'metadata':dict(r.snapshot_metadata_entries),'paused':r.paused,
            'protocol_phase':r.protocol_phase,
            'external_operations':list(world.external_operations),
            'protocols':[{'id':x.id,'completed':x.completed,'next_index':x.next_index} for x in world.protocols]}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--generated',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    checks=[]
    for generated,baseline,fields in (
        ('compuesto/DEMO_RESULT.json','resultados/demo_compuesto_01/DEMO_RESULT.json',
         ['commands','rejected_commands','final_physics','final_operative']),
        ('principal/MEASUREMENTS.json','resultados/compound_D02/MEASUREMENTS.json',
         ['lessons','readouts','native_windows','receipts','final_physics']),
        ('integrado/DEMO_RESULT.json','resultados/demo_integrado_01/DEMO_RESULT.json',
         ['commands','rejected_commands','final_physics','final_operative']),
        ('referencia/MEASUREMENTS.json','resultados/references/SEM01_A_future_UV/MEASUREMENTS.json',
         ['initial','teaching','uses','final','external_operations_actual','diagnostic_edits_actual'])):
        new=json.loads((a.generated/generated).read_text(encoding='utf-8'))
        old=json.loads((a.baseline/baseline).read_text(encoding='utf-8'))
        row={'generated':generated,'baseline':baseline,'fields':{k:new[k]==old[k] for k in fields}}
        checks.append(row)
        assert all(row['fields'].values()),row
    import dee_thinking as d
    states=[]
    for generated,baseline in (
        ('compuesto/COMPUESTO_T204.deetsnap','resultados/demo_compuesto_01/COMPUESTO_T204.deetsnap'),
        ('compuesto/COMPUESTO_DESPUES_PANEL.deetsnap','resultados/demo_compuesto_01/COMPUESTO_DESPUES_PANEL.deetsnap'),
        ('principal/ACQUIRED_K4_T204.deetsnap','resultados/compound_D02/ACQUIRED_K4_T204.deetsnap'),
        ('principal/MAIN_FINAL_T338.deetsnap','resultados/compound_D02/MAIN_FINAL_T338.deetsnap'),
        ('integrado/INTEGRADO_T222.deetsnap','resultados/demo_integrado_01/INTEGRADO_T222.deetsnap'),
        ('integrado/INTEGRADO_DESPUES_PANEL.deetsnap','resultados/demo_integrado_01/INTEGRADO_DESPUES_PANEL.deetsnap'),
        ('referencia/MAIN_FINAL.deetsnap','resultados/references/SEM01_A_future_UV/MAIN_FINAL.deetsnap')):
        w1=d.OrganizationalWorld.load_snapshot(str(a.generated/generated))
        w2=d.OrganizationalWorld.load_snapshot(str(a.baseline/baseline))
        p1,p2=physical(w1),physical(w2)
        o1,o2=operative(w1),operative(w2)
        row={'generated':generated,'baseline':baseline,'physics':p1,
             'full_RAW_clock_tick_equal':p1==p2,'operational_equal':o1==o2}
        states.append(row)
        assert row['full_RAW_clock_tick_equal'] and row['operational_equal'],row
    continued=json.loads((a.generated/'continuado/CONTINUATION.json').read_text(encoding='utf-8'))
    assert continued['after']['tick']>continued['before']['tick']
    assert continued['receipts'] and all(x['status']=='applied' for x in continued['receipts'])
    integrated=json.loads((a.generated/'integrado_continuado/CONTINUATION.json').read_text(encoding='utf-8'))
    assert integrated['after']['tick']>integrated['before']['tick']
    assert integrated['receipts'] and all(x['status']=='applied' for x in integrated['receipts'])
    result={'schema':'CPC5.clean-primary-comparison.v1','status':'VERIFIED',
            'comparisons_after_trajectories_only':True,'measurement_checks':checks,'state_checks':states,
            'other_process_continuation':{'before':continued['before'],'after':continued['after'],
                                        'all_query_receipts_applied':True},
            'integrated_other_process_continuation':{'before':integrated['before'],'after':integrated['after'],
                                        'all_query_receipts_applied':True}}
    put(a.output,result)
    print(json.dumps({'status':result['status'],'measurements':len(checks),'states':len(states),
                      'continued_tick':continued['after']['tick']}))


if __name__=='__main__':main()
