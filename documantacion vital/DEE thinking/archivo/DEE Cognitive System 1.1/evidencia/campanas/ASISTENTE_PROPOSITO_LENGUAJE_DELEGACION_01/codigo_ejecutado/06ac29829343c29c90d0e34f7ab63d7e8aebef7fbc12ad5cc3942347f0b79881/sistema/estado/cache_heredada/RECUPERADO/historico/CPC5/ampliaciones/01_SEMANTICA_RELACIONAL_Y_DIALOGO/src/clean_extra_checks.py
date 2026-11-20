"""Additional clean post-trajectory checks; never imported by participants."""
from pathlib import Path
import argparse
import json
import sys

HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from common import ROOT,BASE,put,sha,digest,identity
from capacity import normalized_op


def main():
    import dee_thinking as d
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--generated',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();identity();g=a.generated;checks=[]
    n=json.loads((g/'capacidad/MEASUREMENTS.json').read_text(encoding='utf-8'))
    old=ROOT/'resultados/capacity_discovery/CAP_D08_N67_G8/MEASUREMENTS.json'
    o=json.loads(old.read_text(encoding='utf-8'))
    keys=('case','geometry','calls','receipts','lessons','readouts','final')
    fields={key:n[key]==o[key]for key in keys}
    checks.append({'id':'capacity8_trajectory','fields':fields,'verified':all(fields.values()),
                   'baseline_sha256':sha(old),'scope':'Old envelope diagnostic is preserved; compare measured state/receipts rather than replacing the historical technical flag.'})
    for snap in n['checkpoints']:
        name=snap['file'];new=g/'capacidad'/name;baseline=old.parent/name
        wa=d.OrganizationalWorld.load_snapshot(str(new));wb=d.OrganizationalWorld.load_snapshot(str(baseline))
        ra,rb=wa.runtime,wb.runtime
        f={'N':ra.dimension==rb.dimension,'tick':ra.current_tick==rb.current_tick,
           'RAW_complete':ra.raw_copy()==rb.raw_copy(),'clocks_complete':ra.clock_copy()==rb.clock_copy()}
        checks.append({'id':'capacity8_snapshot_'+name,'fields':f,'verified':all(f.values()),
                       'physical':digest(wa),'generated_sha256':sha(new),'baseline_sha256':sha(baseline)})
        del wa,wb
    references=[]
    for new in sorted((g/'referencia').glob('*.deetsnap')):
        baseline=ROOT/'resultados/referencia_previa_SEM01'/new.name
        assert baseline.is_file()
        wa=d.OrganizationalWorld.load_snapshot(str(new));wb=d.OrganizationalWorld.load_snapshot(str(baseline))
        ra,rb=wa.runtime,wb.runtime
        f={'N':ra.dimension==rb.dimension,'tick':ra.current_tick==rb.current_tick,
           'RAW_complete':ra.raw_copy()==rb.raw_copy(),'clocks_complete':ra.clock_copy()==rb.clock_copy(),
           'operative_without_framework_cache':normalized_op(wa)==normalized_op(wb)}
        references.append({'snapshot':new.name,'fields':f,'verified':all(f.values()),
                           'generated_sha256':sha(new),'baseline_sha256':sha(baseline),'physical':digest(wa)})
        del wa,wb
    assert len(references)==15,'Reference15snapshots required'
    result={'schema':'CPC5.extension.clean.extra-checks.v1','verified':all(c['verified']for c in checks+references),
            'comparisons_after_trajectories_only':True,'capacity_checks':checks,'historical_reference_states':references,
            'reference_snapshot_count':len(references),
            'scope':'Technical deterministic reproduction, not new independent scientific preparations or semantic confirmations.'}
    put(a.output,result);assert result['verified'];print(json.dumps({'verified':True,'capacity_checks':len(checks),'reference_snapshots':len(references)}))


if __name__=='__main__':main()
