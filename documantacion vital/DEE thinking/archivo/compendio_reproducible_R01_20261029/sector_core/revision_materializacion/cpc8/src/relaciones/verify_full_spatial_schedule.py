"""Technical basal reproduction using the extra passive observation schedule.

This checks segmentation/observation, not a fourth geometry or scientific replica.
No SPX resources or experiences are installed. It cannot adjudicate which added
SPX support/input caused any interference in a different prepared world.
"""
import argparse,hashlib,json,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--source-primary',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    frozen=a.out/'executed_source';shutil.copytree(a.source_primary/'executed_source',frozen);sys.path.insert(0,str(frozen/'src'))
    from integracion.longitudinal_e1 import LongitudinalE1Session
    from integracion.relational_pair import physical
    old=json.loads((ROOT/'resultados/integracion/LCE_P01_FRESH_LONGITUDINAL/MEASUREMENTS.json').read_text(encoding='utf8'));cfg=json.loads((a.source_primary/'CONFIG.json').read_text(encoding='utf8'));full=json.loads((a.source_primary/'MEASUREMENTS.json').read_text(encoding='utf8'))
    case=old['case'];prepkeys=('guard_mode','actor_mode','include_order','include_contact','event_state_offset','medium_load','actor_state','quantity_guards');s=LongitudinalE1Session.create(identifier='TECHNICAL_PASSIVE_SCHEDULE_ONLY',**{k:v for k,v in case.items()if k in prepkeys});s.curriculum(**{k:v for k,v in case.items()if k not in('id',*prepkeys)})
    checks=[];expected={x['tick']:x['physical']for x in old['snapshots']};start=time.monotonic()
    for tick in sorted({x['tick']for x in full['frames']}|set(expected)):
        s.run_until(tick)
        if tick in expected:
            got=physical(s.world);checks.append({'tick':tick,'reference':expected[tick],'actual':got,'RAW_clocks_tick_equal':got==expected[tick]})
    out={'schema':'CPC8R.full_spatialE1.passive_schedule.technical.v1','preparations':0,'technical_preparations':1,'scientific_replicas':0,'reference_primary':str((ROOT/'resultados/integracion/LCE_P01_FRESH_LONGITUDINAL/MEASUREMENTS.json').relative_to(ROOT)),'reference_sha256':sha(ROOT/'resultados/integracion/LCE_P01_FRESH_LONGITUDINAL/MEASUREMENTS.json'),'source_primary':str(a.source_primary.relative_to(ROOT)),'source_primary_sha256':sha(a.source_primary/'MEASUREMENTS.json'),'passive_schedule_ticks':sorted({x['tick']for x in full['frames']}),'checks':checks,'status':'PASS'if all(x['RAW_clocks_tick_equal']for x in checks)else'FAIL','requests':s.receipts(),'elapsed_seconds':time.monotonic()-start}
    shutil.copyfile(__file__,a.out/Path(__file__).name);(a.out/'MEASUREMENTS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'status':out['status'],'checks':len(checks)}))
if __name__=='__main__':main()
