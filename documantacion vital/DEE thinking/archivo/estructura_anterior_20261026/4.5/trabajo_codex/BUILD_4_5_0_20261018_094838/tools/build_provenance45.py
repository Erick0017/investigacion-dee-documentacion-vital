"""Small provenance record, not a copy of caches/toolchains or an outcome oracle."""
import ctypes,hashlib,importlib.metadata,json,platform,struct,sys,sysconfig,zipfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cache_fields(path):
    keys={'CMAKE_BUILD_TYPE','CMAKE_CXX_COMPILER','CMAKE_CXX_FLAGS','CMAKE_CXX_FLAGS_RELEASE',
      'CMAKE_EXE_LINKER_FLAGS_RELEASE','CMAKE_MODULE_LINKER_FLAGS_RELEASE','CMAKE_MAKE_PROGRAM',
      'CMAKE_LINKER','CMAKE_AR','CMAKE_RC_COMPILER','CMAKE_MT','DEE_THINKING_PYTHON_VERSION',
      'Python_EXECUTABLE','DEE_THINKING_BUILD_PYTHON'};out={}
    for line in path.read_text(encoding='utf-8').splitlines():
        if ':' in line and '=' in line:
            name=line.split(':',1)[0]
            if name in keys:out[name]=line.split('=',1)[1]
    return out
def main():
    budget=read(ROOT/'BUDGET.json');current=ctypes.c_longlong();ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(current))
    elapsed=(current.value-budget['start_qpc'])/budget['qpc_frequency']
    buildroot=Path(__import__('os').environ['TEMP'])/'dt45_20261018_094838'
    wheel=ROOT/'candidate_final/wheel/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
    with zipfile.ZipFile(wheel) as z:native=next(n for n in z.namelist() if n.endswith('.pyd'));native_sha=hashlib.sha256(z.read(native)).hexdigest()
    deps={n:importlib.metadata.version(n) for n in ('setuptools','wheel','build','pybind11')}
    history=[]
    for label,rel,role in [('toolchain-only','candidate_early/wheel','provisional before native consolidation'),
          ('candidate1','candidate_history/candidate1','compiled consolidation before final resources'),
          ('candidate2','candidate_02/wheel','resource pass before final remote facade'),
          ('candidate3','candidate_03/wheel','UTF8 I/O correction; before defensive interface preflight'),
          ('candidate4','candidate_history/candidate4','final native preflight; Python source mismatch detected and rejected'),
          ('final6','candidate_final/wheel','only final distributed wheel; source/resource strict match')]:
        p=ROOT/rel/wheel.name
        if p.is_file():
            try:
                with zipfile.ZipFile(p) as z:n=next(n for n in z.namelist() if n.endswith('.pyd'));h=hashlib.sha256(z.read(n)).hexdigest()
            except PermissionError as error:
                if label=='final6':raise
                history.append({'candidate':label,'role':role,'distributed':False,
                    'inspection_status':'UNREADABLE_PERMISSION; identity not asserted','error':str(error)})
                continue
            history.append({'candidate':label,'role':role,'wheel_sha256':sha(p),'bytes':p.stat().st_size,'native_sha256':h,'distributed':label=='final6'})
    if (ROOT/'validation/WHEEL_INSPECTION_CANDIDATE5.json').exists():
        c=read(ROOT/'validation/WHEEL_INSPECTION_CANDIDATE5.json');history.append({'candidate':'candidate5','role':'source frozen; contract name/scope corrected before final6','wheel_sha256':c['wheel_sha256'],'native_sha256':c['native_sha256'],'distributed':False,'bytes_not_claimed_in_delivery':True})
    data={'schema':'DEE45.build-provenance.v1','utc':datetime.now(timezone.utc).isoformat(),
      'budget':budget,'elapsed_monotonic_seconds_at_record':elapsed,
      'final_product_version':'4.5.0','kernel_version':27,'kernel_source_sha256':sha(ROOT/'source/src/kernel_v27.cpp'),
      'python':{'executable':sys.executable,'version':sys.version,'implementation':platform.python_implementation(),
          'pointer_bytes':struct.calcsize('P'),'platform':sysconfig.get_platform(),'gil_disabled':bool(sysconfig.get_config_var('Py_GIL_DISABLED'))},
      'build_dependencies':deps,'build_environment':'isolated venv with read-only system build dependencies; no global package updates',
      'runtime_environments':'separate no-system-site-packages venvs; final installation .venv45_6; no source PYTHONPATH',
      'native_and_cpp_configuration':{name:cache_fields(buildroot/name/'CMakeCache.txt') for name in ('cpp','wheel_native')},
      'compiler':'MSVC19.50.35729 x64, discovered VS18 Community; _MSC_FULL_VER195035729',
      'effective_language':'C++20','msvc_target_options':['/W4','/permissive-','/EHsc','/bigobj'],
      'build_parallel_jobs':2,'kernel_compile_warnings':'inherited constant truncation/unused function retained; no kernel edits',
      'io_compile_warnings':'C++20 u8path deprecation warning retained; tested functionality, no warning-suppression flags',
      'wheel':{'name':wheel.name,'bytes':wheel.stat().st_size,'sha256':sha(wheel),'native_member':native,'native_sha256':native_sha},
      'candidate_history':history,'scientific_status':'software consolidation; no new cognitive capability claim from version change',
      'commands':'jobs/*/COMMAND.json and tools/build45.ps1; command/timeout failures are retained',
      'source_diff':'validation/SOURCE_DIFF.json and SOURCE_CHANGES.patch; four I/O path conversions exactly reversible; no microscopic change'}
    (ROOT/'BUILD_INFO.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'wheel_sha256':sha(wheel),'native_sha256':native_sha,'elapsed_seconds':elapsed,'history_records':len(history)}))
if __name__=='__main__':main()
