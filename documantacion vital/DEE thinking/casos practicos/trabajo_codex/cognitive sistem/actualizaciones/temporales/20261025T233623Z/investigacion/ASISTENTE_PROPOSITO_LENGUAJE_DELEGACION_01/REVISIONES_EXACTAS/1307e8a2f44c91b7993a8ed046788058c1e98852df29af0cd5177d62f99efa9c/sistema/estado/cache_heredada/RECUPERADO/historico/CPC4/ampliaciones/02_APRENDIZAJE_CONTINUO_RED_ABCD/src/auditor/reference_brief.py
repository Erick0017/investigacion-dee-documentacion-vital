"""One-tick reproduction of an inherited CPC4 reference, not its whole suite."""
import hashlib,json
from pathlib import Path
import sys,time
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT.parents[1]
sys.path.insert(0,str(ROOT))
from src.auditor.passive import digest,fields,operation_state

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    import dee_thinking as d
    folder=BASE/'resultados/confirmacion/FULL_PLUS';source=folder/'NATIVO/BEFORE_COMMON_QUERY_PLUS.deetsnap'
    expected=folder/'NATIVO/AFTER_COMMON_QUERY_PLUS.deetsnap'
    out=ROOT/'resultados/auditor/INHERITED_REFERENCE148_149';out.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();world=d.OrganizationalWorld.load_snapshot(str(source));reference=d.OrganizationalWorld.load_snapshot(str(expected))
    assert world.runtime.current_tick==148 and reference.runtime.current_tick==149
    before=digest(world);world.run_until(149)
    physical_equal=digest(world)==digest(reference);assert physical_equal
    operations_equal=operation_state(world)==operation_state(reference)
    spec=json.loads((folder/'MEASUREMENTS.json').read_text(encoding='utf-8'))['physical']['spec']
    samples=fields(world,spec['centers']);world.save_snapshot(str(out/'REPLAY_T149.deetsnap'))
    report={'classification':'ONE_TICK_INHERITED_REFERENCE_REPLAY_NOT_NEW_LEARNED_CASE',
        'source':str(source.relative_to(BASE)),'source_sha256':sha(source),
        'historical_target':str(expected.relative_to(BASE)),'historical_target_sha256':sha(expected),
        'native_ticks_advanced':1,'before':before,'after':digest(world),'reference':digest(reference),
        'full_RAW_clocks_equal':physical_equal,'visible_full_operative_state_equal':operations_equal,
        'samples':samples,'elapsed_seconds':time.monotonic()-started,'source_code_sha256':sha(__file__),
        'scope':'One directed inherited transition only. No old preparation or entire campaign rerun, no snapshot terminal read substituted for forward evolution.'}
    (out/'MEASUREMENTS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'physical_equal':physical_equal,'operative_equal':operations_equal,'ticks':1}))

if __name__=='__main__':main()
