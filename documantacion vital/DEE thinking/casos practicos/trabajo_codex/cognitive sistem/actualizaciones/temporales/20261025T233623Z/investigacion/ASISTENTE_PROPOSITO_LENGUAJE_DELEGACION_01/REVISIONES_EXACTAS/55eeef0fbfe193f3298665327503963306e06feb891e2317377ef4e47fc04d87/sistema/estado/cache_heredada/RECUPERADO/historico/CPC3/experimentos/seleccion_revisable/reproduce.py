"""Portable fresh evolution then audit comparison. Fixtures never answer inputs."""
import argparse,hashlib,json,sys
from array import array
from pathlib import Path
def main(package,case,output):
    sys.path.insert(0,str(package/'src'));import dee_thinking as d
    from core.revisable_selection import run
    config=json.loads((package/'experimentos/seleccion_revisable/EXPERIMENT_CONFIG.json').read_text());source=package/'src/core/revisable_selection.py';assert hashlib.sha256(source.read_bytes()).hexdigest()==config['frozen_core_sha256']
    spec=next(c for c in config['cases'] if c['id']==case);args={k:v for k,v in spec.items() if k not in ('id','kind')};fresh=run(args,output)
    # The reference is opened only AFTER the new Runtime finished its real
    # evolution. It is evaluation evidence, never a constructor/decoder input.
    ref=package/'experimentos/seleccion_revisable/casos'/case;expected=json.loads((ref/'MEASUREMENTS.json').read_text());trace_equal=fresh['trace']==expected['trace'];measure_equal=fresh['measurements']==expected['measurements']
    def digest(path):
        w=d.OrganizationalWorld.load_snapshot(str(path));return {'tick':w.runtime.current_tick,'raw':hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest(),'clock':hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest()}
    a=digest(output/'FINAL_T15.deetsnap');b=digest(ref/'FINAL_T15.deetsnap');report={'case':case,'fresh_evolution_ticks':15,'trace_equal':trace_equal,'measurement_equal':measure_equal,'full_raw_clock_tick_equal':a==b,'fresh_physical':a,'reference_physical':b,'module_file':d.__file__,'runtime_version':d.__version__,'reference_not_read_until_after_evolution':True};(output/'REPRODUCTION_CHECK.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=True));assert trace_equal and measure_equal and a==b
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--package-root',required=True,type=Path);a.add_argument('--case',default='R_TRANSLATED_BAD');a.add_argument('--output',required=True,type=Path);x=a.parse_args();main(x.package_root.resolve(),x.case,x.output.resolve())
