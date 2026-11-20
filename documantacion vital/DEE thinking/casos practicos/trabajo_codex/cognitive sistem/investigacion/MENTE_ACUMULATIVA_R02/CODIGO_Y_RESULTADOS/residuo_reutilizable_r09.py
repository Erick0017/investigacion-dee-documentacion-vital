"""R09: función prospectiva de la señal que bloqueó la entrada común.
Reproduce tramo desde completo MAIN2955, luego corta sólo señal ya formada.
No avanza MAIN; preserva el fallo previo y no reenseña ocultamente.
"""
import gzip,hashlib,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];S=ROOT/'sistema';EV=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA_R02'
sys.path.insert(0,str(S))
from app.lives import Store
from app.native_tools import physical,observe
from capacidades import mente_acumulativa_r02 as ma
from dee_thinking import _native as d
from dee_thinking.persistence import save_world_snapshot

def run(label,cut=False):
    store=Store(S);source=list((S/'estado/checkpoints').glob('MA02_MAIN.T2955.*.deetsnap.gz'))
    if len(source)!=1:raise ValueError('Need one exact complete pre-reacquisition source2955')
    rec=store.fork('MA02_MAIN',label,kind='DIAGNOSTIC_COPY',checkpoint=source[0].relative_to(S).as_posix())
    def body(a):
        before=physical(a.world);frames=[];intervention=None;original=a.run_until
        def traced(target):
            nonlocal intervention
            for tick in range(a.tick+1,target+1):
                original(tick)
                if tick==3017:
                    site=(35,33,33);pre=observe(a.world,site)
                    cp=EV/'residuo'/f'{label}.pre_edit_T3017.deetsnap.gz';cp.parent.mkdir(parents=True,exist_ok=True);save_world_snapshot(a.world,cp,compress=True)
                    ed=d.ResearchStateEdit();ed.coordinate=d.Coordinate(*site);ed.raw=0 if cut else int(pre['raw']);ed.clock=int(pre['clock']);ed.label='R09 old formed cue cut'if cut else'R09 exact sham formed cue'
                    a.world=a.world.diagnostic_fork([ed],True)
                    intervention={'pre':pre,'post':observe(a.world,site),'snapshot':str(cp),'sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'modality':'External diagnostic cut/sham; not MAIN repair'}
                if 3013<=tick<=3018:
                    pts={(x,y,z)for x in range(33,40)for y in range(32,35)for z in range(30,37)}
                    frames.append({'tick':tick,'sites':[observe(a.world,p)for p in sorted(pts)],'physical':physical(a.world)})
        a.run_until=traced
        teacher=ma.teach(a,'alfa',-1,revision=False)
        teaching_after=physical(a.world)
        # First use of other information then of the reacquired target, no more
        # teachers or feedback. These uses are own consequences on the copy.
        queries=[ma.query(a,k,detail=True)for k in('gamma','delta','alfa')]
        return {'label':label,'source':rec['parent'],'before':before,'teach':teacher,'teaching_after':teaching_after,'intervention':intervention,'frames':frames,'queries':queries,'after':physical(a.world),'first_use_tests_not_independent_learners':True}
    out=store.mutate(label,'MA02_R09_REUSE_RESIDUAL_CAUSAL',body,{'diagnostic_only':True,'original_MAIN_unchanged':True,'fixed_cut_site':[35,33,33],'fixed_cut_tick':3017})
    path=EV/'residuo'/(label+'.json.gz');path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise FileExistsError(path)
    path.write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False,sort_keys=True).encode(),mtime=0))
    r=out['result'];print(json.dumps({'label':label,'hub':r['teach']['hub'],'receipt_statuses':[x['receipt']['status']for x in r['teach']['requests']],'queries':[{x['context_signal']:x['reader']['formed_native_command']}for x in r['queries']]},ensure_ascii=False),flush=True)
if __name__=='__main__':
    p=HERE/'PROTOCOLO_RESIDUO_R09.json'
    if p.exists():raise FileExistsError(p)
    p.write_text(json.dumps({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'exploratory_observation':'MAIN20 alpha common injection rejected, yet hub−Zload16 forms after teacher11. Candidate prior cue5 participates rather than new admitted query.','test_frozen_before_new_native_run':'From exactMAIN2955, same future alpha teaching, preserve actual native admission rejection, cut formed cue5 at3017(35,33,33) vs exactsham withclockpreserved','criterion':'Sham hub−Z then later pureZ− answer; cut leaves teacher−X−Z not a valid signed memory and removes that answer while gamma/delta still operate','reader':'Unchanged all-eight fixed gate observer; no target/token passed','scope':'Selective causal diagnostic reproduction, not independent reacquisition added to MAIN; normal MAIN reacquisition already occurred once.'},ensure_ascii=False,indent=2),encoding='utf-8')
    run('MA02_R09_RESIDUO_SHAM',False);run('MA02_R09_RESIDUO_CUT',True)
