"""One isolated-process installation/reproduction check from the extracted cut.

Expected frames are read only AFTER native evolution. The audit hook is a
Python-read diagnostic, not an OS security sandbox or a native fopen monitor.
"""
from pathlib import Path
from array import array
import argparse,hashlib,json,sys,time,tempfile,shutil

ROOT=Path(__file__).resolve().parents[1];PARENT=ROOT.parents[1]
sys.path.insert(0,str(ROOT/'src'))
from campaign import identity,put,sha

def physical(w):
    r=w.runtime
    return {'tick':r.current_tick,'RAW':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
            'clocks':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}

def operative(w):
    import dee_thinking as d
    # The live world may carry an earlier serialized OrganizationalWorld envelope;
    # load exposes the freshly serialized one. Compare complete Runtime bytes on
    # independent technical clones after removing only that derived envelope and
    # normalizing the explicitly compared execution backend. Actual channels,
    # pending queue, receipts, protocol metadata and all physical buffers remain.
    q=w.runtime.fork()
    for key in dict(q.snapshot_metadata_entries):
        if key.startswith('dee_thinking.organizational.v1.'):q.erase_snapshot_metadata(key)
    q.execution_options=d.TickOptions(d.Backend.LAZY,1)
    with tempfile.TemporaryDirectory(prefix='cpc4_state_',dir=SNAP_ROOT) as td:
        snap=Path(td)/'normalized.deetsnap';q.save_snapshot(str(snap));full=sha(snap)
    return {'physical':physical(w),'metadata':{k:v for k,v in dict(w.runtime.snapshot_metadata_entries).items() if not k.startswith('dee_thinking.organizational.v1.')},
            'normalized_complete_runtime_sha256':full,
            'channels':list(w.runtime.channel_names),'operations':list(w.external_operations),
            'receipts':[(r.id,r.requested_tick,r.effective_tick,str(r.status),list(r.channels),r.reason) for r in w.runtime.receipts]}

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);started=time.monotonic();identity_record=identity()
    shutil.copyfile(__file__,a.output/'EXECUTED_SOURCE.py')
    global SNAP_ROOT;SNAP_ROOT=a.output
    import dee_thinking as d
    from red.session_v3 import NetworkSession
    from red import recipe_v3 as recipe
    protected={'on':False};reads=[]
    def audit(event,args):
        if event!='open' or not protected['on'] or not isinstance(args[0],(str,bytes)):return
        path=str(args[0]);mode=args[1] or ''
        if isinstance(mode,str) and any(c in mode for c in 'wax+'):return
        reads.append(path)
        if any(s in path.upper() for s in ('MEASUREMENTS.JSON','RUN_SUMMARY.JSON','CAPACIDADES.JSON','RETENCION.JSON')):
            raise RuntimeError('Participant attempted to read a result table: '+path)
    sys.addaudithook(audit)
    case_path=ROOT/'resultados/red/confirmacion03/casos/FULL_U.json'
    case=json.loads(case_path.read_text(encoding='utf-8'));translation=tuple(case.pop('translation',(0,0,0)))
    protected['on']=True
    s=NetworkSession.create(case,translation)
    for t in (85,94,161):
        s.run_until(t);s.save(a.output/f'GENERATED_T{t}.deetsnap')
    restored=NetworkSession.load(a.output/'GENERATED_T161.deetsnap')
    assert operative(restored.world)==operative(s.world)
    s.run_until(431);restored.run_until(431)
    assert operative(s.world)==operative(restored.world)
    s.save(a.output/'GENERATED_T431.deetsnap')
    pre=operative(s.world)
    for _ in range(3):s.observe()
    assert operative(s.world)==pre
    modes={}
    for label,backend in (('lazy',d.Backend.LAZY),('dense',d.Backend.DENSE_SEQUENTIAL),('parallel',d.Backend.DENSE_PARALLEL)):
        q=NetworkSession.load(a.output/'GENERATED_T85.deetsnap');q.world.runtime.execution_options=d.TickOptions(backend,1)
        q.run_until(94);modes[label]=operative(q.world)
    assert modes['lazy']==modes['dense']==modes['parallel']
    protected['on']=False
    expected=NetworkSession.load(ROOT/'resultados/red/confirmacion03/FULL_U/T431.deetsnap')
    assert operative(s.world)==operative(expected.world)
    # An inherited one-step physical reference, not a replay of its later host
    # protocol. The old runner adds new environmental requests after149.
    old=PARENT/'resultados/confirmacion/MAIN_MINUS/NATIVO'
    candidates=[old/'BEFORE_COMMON_QUERY_PLUS.deetsnap'];post_candidates=[old/'AFTER_COMMON_QUERY_PLUS.deetsnap']
    historical={'status':'SOURCE_BOUNDARY_NOT_FOUND','searched':str(old)}
    if candidates[0].is_file() and post_candidates[0].is_file():
        w=d.OrganizationalWorld.load_snapshot(str(candidates[0]));w.run_until(149)
        post=d.OrganizationalWorld.load_snapshot(str(post_candidates[0]))
        assert physical(w)==physical(post)
        historical={'status':'PHYSICAL_REFERENCE_EQUAL','physical':physical(w),'operative_equal':operative(w)==operative(post),
                    'scope':'One native tick. Later historical host environment calls were not silently supplied.'}
    module_paths={n:getattr(m,'__file__',None) for n,m in sys.modules.items() if n.startswith(('red','lenguaje','dee_thinking'))}
    for name,path in module_paths.items():
        if path and name.startswith(('red','lenguaje')):assert Path(path).resolve().is_relative_to(ROOT)
    report={'identity':identity_record,'native_generated_state_matches_published_reference':True,
            'save_load_same_operative_future':True,'passive_observation_same_state':True,'backend_window85_94_equal':True,
            'complete_state431':operative(s.world),'historical_reference':historical,
            'python_read_guard':'No result-table reads during participant construction/evolution/queries; native I/O is outside this audit hook.',
            'container_comparison':'Complete native Runtime snapshots equal on technical clones after explicit backend normalization and removal of the derived organizational envelope; public operations and validated interfaces compared independently. RAW/clocks/tick/pending/receipts/own protocol metadata are not normalized.',
            'audited_python_reads':reads,'module_paths':module_paths,'elapsed_seconds':time.monotonic()-started}
    put(a.output/'CLEAN_REPRODUCTION.json',report)
    print(json.dumps({'clean_reproduction':'completed','elapsed':report['elapsed_seconds'],'final_tick':431}))

if __name__=='__main__':main()
