"""External comparison AFTER clean native trajectories; never imported by actors."""
import argparse
from array import array
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,BASE,put,sha,identity,operational

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))

def compare_snapshot(a,b):
    import dee_thinking as d
    wa=d.OrganizationalWorld.load_snapshot(str(a));wb=d.OrganizationalWorld.load_snapshot(str(b))
    ra,rb=wa.runtime,wb.runtime
    fields={'N':ra.dimension==rb.dimension,'tick':ra.current_tick==rb.current_tick,
            'RAW_complete':ra.raw_copy()==rb.raw_copy(),'clocks_complete':ra.clock_copy()==rb.clock_copy()}
    oa,ob=operational(wa),operational(wb)
    full_meta_equal=oa['metadata']==ob['metadata']
    oa['metadata']={k:v for k,v in oa['metadata'].items() if not k.startswith('dee_thinking.organizational.')}
    ob['metadata']={k:v for k,v in ob['metadata'].items() if not k.startswith('dee_thinking.organizational.')}
    fields['operative_without_framework_cache']=oa==ob
    return {'generated':str(a),'baseline':str(b),'fields':fields,'all_verified':all(fields.values()),
            'framework_cached_metadata_equal':full_meta_equal,
            'physical_hashes':{'raw_sha256':hashlib.sha256(array('Q',ra.raw_copy()).tobytes()).hexdigest(),
                               'clock_sha256':hashlib.sha256(array('Q',ra.clock_copy()).tobytes()).hexdigest()},
            'scope':'Physical arrays/tick compared exactly. Cached framework envelope equality is separately reported, never normalized into physical state.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--generated',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();g=a.generated
    identity();measurements=[];states=[]
    pairs=[(g/'principal/LONGITUDINAL_LOWER/MEASUREMENTS.json',ROOT/'resultados/dialogue_longitudinal/LONGITUDINAL_LOWER/MEASUREMENTS.json',
           ['case','geometry','inputs','receipts','trace','messages','final_physics','final_operative']),
          (g/'longitudinal/DEMO_RESULT.json',ROOT/'resultados/demo_longitudinal_01/DEMO_RESULT.json',['rejected_commands','final_physical','final_operative']),
          (g/'orden/DEMO_RESULT.json',ROOT/'resultados/demo_orden_01/DEMO_RESULT.json',['rejected_commands','final_physical','final_operative']),
          (g/'referencia/MEASUREMENTS.json',ROOT/'resultados/referencia_previa_SEM01/MEASUREMENTS.json',['initial','teaching','uses','final','external_operations_actual','diagnostic_edits_actual'])]
    for new,old,keys in pairs:
        n,o=read(new),read(old);f={k:n[k]==o[k] for k in keys}
        measurements.append({'generated':str(new),'baseline':str(old),'baseline_sha256':sha(old),'fields':f,'verified':all(f.values())})
    for name in ('NAME_CF_REMOVE','NAME_CF_SHAM'):
        new,old=g/f'causal/{name}/MEASUREMENTS.json',ROOT/f'resultados/order_forks/{name}/MEASUREMENTS.json'
        n,o=read(new),read(old);keys=('case','rows','raw_sites_changed','clock_sites_changed','MAIN_unchanged','final_physical');f={k:n[k]==o[k] for k in keys}
        measurements.append({'generated':str(new),'baseline':str(old),'fields':f,'verified':all(f.values())})
    snapshot_pairs=[(g/'principal/LONGITUDINAL_LOWER/T338.deetsnap',ROOT/'resultados/dialogue_longitudinal/LONGITUDINAL_LOWER/T338.deetsnap'),
                    (g/'longitudinal/LONGITUDINAL_T338.deetsnap',ROOT/'resultados/demo_longitudinal_01/LONGITUDINAL_T338.deetsnap'),
                    (g/'orden/ORDEN_T92.deetsnap',ROOT/'resultados/demo_orden_01/ORDEN_T92.deetsnap'),
                    (g/'continuado/CONTINUADO_T405.deetsnap',ROOT/'resultados/demo_longitudinal_continuacion_01/CONTINUADO_T405.deetsnap')]
    for x,y in snapshot_pairs:states.append(compare_snapshot(x,y))
    demonstration=read(g/'continuado/DEMO_RESULT.json');continuation_good=demonstration['rejected_commands']==0 and demonstration['final_physical']['tick']==405
    result={'schema':'CPC5.extension.clean.comparisons.v1','verified':all(x['verified'] for x in measurements) and all(x['all_verified'] for x in states) and continuation_good,
            'comparisons_after_trajectories_only':True,'measurement_checks':measurements,'state_checks':states,
            'continued_from_newly_generated_checkpoint':True,'continuation_tick405_and_grammar_accepted':continuation_good}
    put(a.output,result);assert result['verified'];print(json.dumps({'verified':True,'measurements':len(measurements),'states':len(states)}))

if __name__=='__main__':main()
