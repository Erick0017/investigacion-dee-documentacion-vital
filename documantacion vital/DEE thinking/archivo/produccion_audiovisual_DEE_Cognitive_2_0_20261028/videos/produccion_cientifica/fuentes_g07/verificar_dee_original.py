"""Verification companion to Procesamiento Nativo DEE.
New launcher; original imported constructors remain byte-for-byte unchanged.
Modes explicitly distinguish native demonstrations, original-constructor replays,
and recalculation of supplied telemetry. No training result is calculated for the kernel.
"""
from __future__ import annotations
import argparse, hashlib, importlib, importlib.util, itertools, json, math, platform, sys, time
from collections import Counter
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'fuentes'
WHEEL_SHA='69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939'
SOURCE_SHA='44a80f7863d78f596099ddf7d41c9947fa8513503f65067097f1f3b05a8207ab'
BINARY_SHA='0b17ba32037935a255b0f2182a52137bceab424f7e09126b761076b63e42c6ff'
PACKAGE_SHA='7e2991b1fc8a053ee44ead6e177b129855ae9265dea68505a8e545f0c3fdf8b4'
B=4096; CAP=19664

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def array_sha(a):return hashlib.sha256(np.ascontiguousarray(a,dtype='<u8').tobytes()).hexdigest()
def loadj(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def one(key,name):
    hits=sorted((SRC/key).rglob(name))
    if not hits:raise FileNotFoundError(f'{key}/{name}')
    return hits[0]
def original(key,path,name=None):
    p=SRC/key/path
    if not p.is_file():p=one(key,path)
    sys.path.insert(0,str(p.parent))
    spec=importlib.util.spec_from_file_location(name or ('original_'+key+'_'+p.stem),p)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def check(cond,msg):
    if not cond:raise AssertionError(msg)

def pack(state,sreg,d=(0,0,0),sem=1):
    if not 0<=int(state)<2**32 or not 0<=int(sreg)<2**16:raise ValueError('field range')
    if len(d)!=3 or any(not -8<=int(v)<=7 for v in d):raise ValueError('direction range')
    return np.uint64(int(state)|(int(sreg)<<32)|((int(d[0])&15)<<48)|((int(d[1])&15)<<52)|((int(d[2])&15)<<56)|((int(sem)&15)<<60))
def decode(v):
    v=int(v); ds=[]
    for sh in [48,52,56]:
        d=(v>>sh)&15;ds.append(d-16 if d>=8 else d)
    return {'state':v&0xffffffff,'sreg':(v>>32)&65535,'d':ds,'semantic':(v>>60)&15}
def add(q,d,t,n):return tuple((int(q[i])+int(d[i])*t)%n for i in range(3))
def occupied(raw):return (raw&np.uint64(0xffffffff))>0
class World:
    def __init__(self,kernel,n=None,raw=None,clock=None):
        if raw is None:raw=np.zeros((n,n,n),np.uint64)
        self.a=np.ascontiguousarray(raw,dtype=np.uint64).copy();self.b=self.a.copy()
        self.c=np.zeros_like(self.a) if clock is None else np.ascontiguousarray(clock,dtype=np.uint64).copy()
        self.d=self.c.copy();self.n=self.a.shape[0];self.kernel=kernel;self.t=0
    def put(self,q,state,sreg,d=(0,0,0),sem=1,clock=0):
        check(int(self.a[q])==0,'input port is occupied')
        self.a[q]=pack(state,sreg,d,sem);self.b[q]=self.a[q]
        self.c[q]=np.uint64(clock);self.d[q]=np.uint64(clock)
    def step(self,count=1,lazy=True):
        for _ in range(count):
            fn=self.kernel.tick_universo_lazy if lazy else self.kernel.tick_universo
            fn(self.a,self.b,self.c,self.d,self.n,1);self.t+=1
    def arrival(self,q,t,d,s,state=1):self.put(add(q,d,-(t-self.t),self.n),state,s,d)

_ATOMS=None
def atoms(fragment):
    global _ATOMS
    if _ATOMS is None:
        _ATOMS=[json.loads(line) for line in (SRC/'U1/C06_C07_EVIDENCE_ATOMS.jsonl').open(encoding='utf-8')]
    return [x for x in _ATOMS if fragment.lower() in x['source_internal_path'].lower()]
def records(fragment):return [x['raw_measurement'] for x in atoms(fragment) if x.get('experiment_id','').startswith('cases[')]

def g01(k):
    check(sha(SRC/'U1/dee_kernel_v27.cpp')==SOURCE_SHA,'source identity')
    n=7;w=World(k,n);q=(3,3,3);w.put(q,19,65535,(-1,0,1),4,2**64-1);r=int(w.a[q]);w.step()
    check(int(w.a[q])==r,'semantic4 raw persistence');check(int(w.c[q])==0,'uint64 clock wrap')
    check(decode(pack(37,111,(-8,7,-1),7))=={'state':37,'sreg':111,'d':[-8,7,-1],'semantic':7},'packing')
    return {'kind':'native_identity_and_packing','source_sha256':SOURCE_SHA,'checks':3}

def g02(k):
    dirs=[d for d in itertools.product([-1,0,1],repeat=3) if d!=(0,0,0)];checks=0
    for n in (11,13):
        for d in dirs:
            w=World(k,n);q=(n//2,)*3;w.put(q,1,7,d);v=int(w.a[q])
            for t in range(1,n+1):
                w.step();check(np.count_nonzero(w.a)==1 and int(w.a[add(q,d,t,n)])==v,'ballistic exact shift');checks+=1
    return {'kind':'independent_native_demonstration','directions':26,'N':[11,13],'exact_checkpoints':checks}

def g03(k):
    dirs=[d for d in itertools.product([-1,0,1],repeat=3) if d!=(0,0,0)];ct=0
    for a,b in itertools.combinations(dirs,2):
        w=World(k,7);q=(3,3,3);w.arrival(q,1,a,7);w.arrival(q,1,b,11);w.step();v=decode(w.a[q])
        expected=[int(np.sign(a[i]+b[i])) for i in range(3)]
        check(v=={'state':1,'sreg':18,'d':expected,'semantic':1},'two-source fiber');ct+=1
    w=World(k,9);q=(4,4,4);w.arrival(q,1,(1,0,0),15000);w.arrival(q,1,(0,1,0),9000);w.step();check(decode(w.a[q])['sreg']==CAP,'cap')
    return {'kind':'independent_native_demonstration','unordered_direction_pairs':ct,'saturation_input':24000,'saturation_output':CAP,'overflow_payload_discarded':4336}

def g04(k):
    w=World(k,23);q=(2,11,11);w.put(q,3,7,(1,0,0),4,31);v=int(w.a[q]);seq=[]
    for t in range(1,13):w.step();check(int(w.a[q])==v,'persistent source');seq.append(bool(occupied(w.a)[3,11,11]))
    check(seq==[True,False]*6,'alternating near-source emission')
    return {'kind':'independent_native_demonstration','ticks':12,'adjacent_occupation':seq,'raw_source_fixed':True,'clock_final':int(w.c[q])}

def g05(k):
    mod=original('C05','RUNNERS/run_nrd05_relational_scale_discovery.py')
    rows=[]
    for delta in range(-3,4):
        rows.append(mod.run_case(k,61,(27,29),5,7,8,list(range(-3,4)),delta,'native',(2,3),(0,11)))
    check(all(x['correct'] and x['initial_hubs_empty'] for x in rows),'original delay construction')
    ctrl=mod.run_case(k,61,(27,29),5,7,8,list(range(-3,4)),2,'reversed_calibration',(2,3),(0,11))
    check(ctrl['measured_delta']==-2 and not ctrl['correct'],'reversed calibration')
    return {'kind':'original_constructor_replay_selected_discovery_design','N':61,'treatments_exact':7,'treatments':7,'destroyed_measured':-2,'input_delta_control':2,'bits_uniform':math.log2(7),'source':'C05/RUNNERS/run_nrd05_relational_scale_discovery.py'}

def learn_query(k,delta,q,mode='trained',x=11):
    n=41;J=(15,12,20);cue=(1,0,0);teacher=(-1,1,0);mem=(0,1,0);w=World(k,n)
    if mode!='untrained':
        w.arrival(J,5,cue,B-x);w.arrival(J,5 if mode!='asynchronous' else 6,teacher,x+delta)
    w.step(5);training=decode(w.a[J]);R=add(J,mem,8,n)
    w.step(5);w.arrival(R,13,cue,q);w.step(3)
    v=decode(w.a[R]);return {'delta':delta,'q':q,'mode':mode,'training':training,'output':v,'decoded':v['sreg']-B}

def g06(k):
    out=[]
    for delta in (-4,1,3,7):
        for q in (0,2,7,15,22,35):
            r=learn_query(k,delta,q);check(r['training']['sreg']==B+delta and r['decoded']==q+delta,'translation');out.append(r)
    for mode in ['untrained','asynchronous']:
        r=learn_query(k,3,20,mode);check(r['decoded']!=23,'causal control');out.append(r)
    rs=records('RESULTS/C6H03_native_successor_translation_holdout.json');treated=[r for r in rs if r['mode']=='trained'];res=[]
    for r in treated:
        res.extend(int(v)-(int(r['query'])+int(r['delta'])) for v in r['decoded'])
    check(len(treated)==24 and len(res)==96 and max(map(abs,res))==0,'historical translation records')
    return {'kind':'independent_native_demonstration_and_recovered_telemetry','native_trials_exact':24,'native_controls':2,'historical_worlds':len(treated),'historical_channels':len(res),'historical_max_residual':0,'examples':out[:3]}

def g07(k):
    # Directly execute two learned memories in the same lattice, query crossing both.
    out=[]
    for d1,d2,q in [(3,7,20),(-4,1,15),(1,-4,15),(7,3,20)]:
        n=67;w=World(k,n);J=(20,15,30);R=add(J,(0,1,0),8,n);R2=add(R,(1,1,0),7,n);J2=add(R2,(0,0,1),-15,n)
        for j,te,d in [(J,(-1,1,0),d1),(J2,(-1,0,1),d2)]:
            w.arrival(j,5,(1,0,0),B-11);w.arrival(j,5,te,11+d)
        w.step(10);w.arrival(R,13,(1,0,0),q);w.step(10)  # Query and second memory meet at global tick20.
        v=decode(w.a[R2]);check(v['sreg']==2*B+q+d1+d2,'native composition')
        out.append({'d1':d1,'d2':d2,'query':q,'output_sreg':v['sreg'],'decoded':v['sreg']-2*B})
    rs=records('RESULTS/C6H04_compositional_translation_holdout.json');pos=[r for r in rs if r['mode']=='both_trained']
    check(len(pos)==30 and all(r['composition_exact'] is True for r in pos),'historic composition')
    return {'kind':'independent_native_demonstration_and_recovered_telemetry','native_exact':4,'historical_positive':30,'historical_controls':len(rs)-30,'examples':out}

def g08(k):
    # Learned y-directed payload meets a zero-load routing carrier; s_reg is preserved.
    n=53;J=(20,15,20);relay=(20,22,20);receiver=(31,22,20);w=World(k,n)
    w.arrival(J,5,(1,0,0),B-7);w.arrival(J,5,(-1,1,0),2)
    w.arrival(relay,12,(1,-1,0),0);w.step(18);w.arrival(receiver,23,(0,1,0),4);w.step(5)
    v=decode(w.a[receiver]);check(v['sreg']-B==-1,'zero-load functional relay')
    rs=records('RESULTS/C7H01_functional_learning_transfer.json');pos=[r for r in rs if r['mode']=='transferred']
    check(pos and all(r['exact_function'] is True for r in pos),'historic transferred repertoire')
    rp=records('RESULTS/C7H03_reprogrammable_functional_matter.json');pp=[r for r in rp if r['mode']=='reprogrammed']
    check(pp and all(int(r['decoded'])==int(r['query'])+int(r['delta'])+int(r['update']) for r in pp),'reprogrammed relation')
    return {'kind':'native_relay_demonstration_and_recovered_telemetry','native_relay_decoded':-1,'historical_transfer_treatments':len(pos),'historical_reprogrammed_treatments':len(pp),'transfer_relation':'q+delta','updated_relation':'q+delta+update'}

def g09(k):
    xs=atoms('RESULTS/C7H02_destination_fiber_capacity_budget.json');check(len(xs)==1,'capacity source')
    data=xs[0]['raw_measurement']
    sep=data['separated']
    channels=sum(int(r['channels']) for r in sep)
    exact=sum(int(r['exact_channels']) for r in sep)
    check(channels==86 and exact==86 and max(int(r['spec']['k']) for r in sep)==40,'separated capacity')
    for r in sep:
        check(int(r['initial']['support'])-int(r['after_training']['support'])==int(r['channels']),'training support budget')
        check(int(r['after_injection']['support'])-int(r['after_query']['support'])==int(r['channels']),'read support budget')
    rs=records('RESULTS/C7H04_internal_feedback_resource_closure.json')
    pos=[r for r in rs if r['feedback_exact'] is True]
    check(len(rs)==40 and len(pos)==12,'feedback record count')
    for r in pos:
        check(int(r['initial']['sreg_sum'])==int(r['final']['sreg_sum']),'feedback sreg balance')
        check([int(x) for x in r['support_sequence']]==[6,5,4,3,2,1,1],'support contraction')
    return {'kind':'recovered_telemetry_recalculation','feedback_positive':12,'feedback_controls':28,'support_sequence':[6,5,4,3,2,1,1],'capacity_summary':{'channels':channels,'exact':exact,'max_K':40,'registered_overlap_panels':int(data['sample_sizes']['overlap_panels'])},'capacity_record_evidence_id':xs[0]['evidence_id']}

def g10(k):
    p=one('I01','R04_RESET_CORRECTED_HOLDOUT.json');j=loadj(p)
    # Corrected constructor is local to the frozen corrected holdout runner.
    mod=original('I01','REWRITE_WORK/RUNNERS/run_r04_reset_corrected_holdout.py')
    fn=getattr(mod,'run_reset_case',None)
    if fn is None:
        fn=original('I01','REWRITE_WORK/RUNNERS/reset_apparatus_v1.py').run_reset_case
    challenges=loadj(one('I01','R04_RESET_CORRECTED_CHALLENGES.json'))['challenges']
    expected_by_id={r['challenge_id']:r for r in j['rows']}
    selected=[(ch,expected_by_id[ch['challenge_id']]) for ch in challenges]
    out=[]
    for ch,expected in selected:
        observed=fn(k,ch)
        baseline=expected.get('result',expected)
        check(observed['first_failure_tick']==baseline['first_failure_tick'],'original recurrence first failure')
        check(observed['exact_half_cycles']==baseline['exact_half_cycles'],'original recurrence cycles')
        out.append({'mode':ch['mode'],'cycles':ch['cycles'],'first_failure_tick':observed['first_failure_tick'],'exact_half_cycles':observed['exact_half_cycles']})
    return {'kind':'original_constructor_all_frozen_rows','rows':out,'full_registered_summary':j['summary']}

def g11(k):
    mod=original('I02','RUNNERS/temporal_order_apparatus_v1.py')
    expected=loadj(SRC/'I02/HOLDOUT/ING02_FINAL_HOLDOUT.json');counts=Counter();checks=0
    for r in expected['rows']:
        actual=mod.run_case(k,r['challenge']);check(actual['terminal']['full_sha256']==r['result']['terminal']['full_sha256'],'I02 terminal full-state hash')
        check(actual['trace']==r['result']['trace'],'I02 full selected trace');checks+=1;counts[r['challenge']['role']]+=1
    return {'kind':'original_constructor_all_frozen_challenges','exact_worlds':checks,'by_role':dict(counts),'horizon':64,'source_sha256':sha(SRC/'I02/RUNNERS/temporal_order_apparatus_v1.py')}

def g12(k):
    z=np.load(one('I05','NRD04_ALL_SUBSET_RESPONSES.npz'),allow_pickle=False);out={}
    for h,bits in [('H1',8),('H2',7)]:
        tags=sorted(x.removesuffix('_response_h32_raw_xor') for x in z.files if x.startswith(h+'_') and x.endswith('_response_h32_raw_xor'))
        hashes=[]
        for t in tags:
            d=hashlib.sha256()
            for tail in ['h32_raw_xor','h32_clock_xor','h64_raw_xor','h64_clock_xor']:d.update(np.ascontiguousarray(z[t+'_response_'+tail]).tobytes())
            hashes.append(d.hexdigest())
        ctr=Counter(hashes);H=-sum((v/len(tags))*math.log2(v/len(tags)) for v in ctr.values())
        check(len(tags)==2**bits and len(ctr)==(131 if h=='H1' else 19),'observational quotient')
        out[h]={'preparations':len(tags),'response_classes':len(ctr),'uniform_input_entropy_bits':bits,'response_entropy_bits':H,'conditional_entropy_bits':bits-H}
    return {'kind':'primary_telemetry_recalculation','domains':out}

def g13(k):
    z=np.load(one('I05','NRD06_SPECIFICITY_STATES_AND_FUTURES.npz'),allow_pickle=False);out={}
    for tail in ['raw_a','clock_a','C0_h32_raw','C0_h64_raw','C3_h32_raw','C3_h64_raw']:
        effects=[]
        for h in ['H0','HB']:
            p='MAIN_S0_D0_'+h+'_';effects.append(z[p+'PROBE_'+tail]^z[p+'CONTROL_'+tail])
        out[tail]=int(np.count_nonzero(effects[0]!=effects[1]))
    check(out=={'raw_a':0,'clock_a':0,'C0_h32_raw':56,'C0_h64_raw':70,'C3_h32_raw':56,'C3_h64_raw':74},'same immediate delta/contextual future')
    return {'kind':'primary_telemetry_recalculation','differences':out}

def g14(k):
    out={}
    for tag in ['MAIN_S0','FRESH_V1']:
        z=np.load(one('I06','ING06_CAUSAL_LOAD_16_REUSE_'+tag+'.npz'),allow_pickle=False)
        p='POST_E_NEW_16_';a=z[p+'FULL_raw_a'];c=z[p+'FULL_clock_a'];sigs=[]
        for i in range(1,17):
            b=z[p+f'OMIT_{i}_raw_a'];d=z[p+f'OMIT_{i}_clock_a'];sigs.append(hashlib.sha256((a^b).tobytes()+(c^d).tobytes()).hexdigest())
        sigs.append(hashlib.sha256((a^z[p+'NO_NEW_raw_a']).tobytes()+(c^z[p+'NO_NEW_clock_a']).tobytes()).hexdigest())
        clock_only={'raw_sites':int(np.count_nonzero(a!=z[p+'OMIT_13_raw_a'])),'clock_sites':int(np.count_nonzero(c!=z[p+'OMIT_13_clock_a']))}
        check(len(set(sigs))==17 and clock_only=={'raw_sites':0,'clock_sites':1},'history distinctions')
        out[tag]={'omission_signatures':17,'omission13':clock_only}
    return {'kind':'primary_snapshot_recalculation','domains':out}

def g15(k):
    zp=np.load(one('P01','HB_P2_MAIN_STATE_CHECKPOINTS.npz'),allow_pickle=False);result={'parent':{},'augmented':{},'replay':{}}
    for label in ['HB_FULL','HB_OMIT_P2']:
        a=zp['T512_'+label+'_raw_a'];result['parent'][label]=int(occupied(a).sum())
        # Continue each supplied t32 checkpoint and compare every later saved state.
        w=World(k,raw=zp['T32_'+label+'_raw_a'],clock=zp['T32_'+label+'_clock_a']);w.t=32
        ticks=sorted(int(x.split('_')[0][1:]) for x in zp.files if x.endswith('_'+label+'_raw_a') and int(x.split('_')[0][1:])>32)
        checked=0
        for t in ticks:
            w.step(t-w.t);check(np.array_equal(w.a,zp[f'T{t}_{label}_raw_a']) and np.array_equal(w.c,zp[f'T{t}_{label}_clock_a']),'P01 checkpoint replay');checked+=1
        result['replay'][label]={'ticks_executed':480,'checkpoints_exact':checked}
    ea=zp['T512_HB_OMIT_P2_raw_a'];la=zp['T512_HB_FULL_raw_a']
    result['parent']['mask_differences']=int(np.count_nonzero(occupied(ea)!=occupied(la)));result['parent']['raw_differences']=int(np.count_nonzero(ea!=la))
    check(result['parent']['mask_differences']==836 and result['parent']['raw_differences']==58540,'parent contrasts')
    z=np.load(SRC/'P02/telemetry.npz',allow_pickle=False);mod=original('P02','runner_procesos02.py');cfg=loadj(SRC/'P02/config.json');diag={}
    for name in ['MAIN_S0','FRESH_V1','FRESH_V2']:
        cfg['active_configuration']=name;g=mod.component_geometry(cfg);vals=[]
        for branch,t in [('HB_FULL',0),('HB_OMIT_P2',512),('HB_FULL',512)]:
            prefix=name+'__'+branch+'_AUGMENTED_t'+str(t)
            snap=(z[prefix+'_raw'],z[prefix+'_clock']);v=mod.diagnostic_center_restoration(k,snap,g,1);vals.append(v['centers_occupied_after_one_tick'])
        check(vals==[2,0,2],'contextual restoration 2/0/2');diag[name]=vals
    a=z['MAIN_S0__HB_OMIT_P2_AUGMENTED_t512_raw'];b=z['MAIN_S0__HB_FULL_AUGMENTED_t512_raw']
    result['augmented']={'occupied_early':int(occupied(a).sum()),'occupied_late':int(occupied(b).sum()),'raw_differences':int(np.count_nonzero(a!=b)),'mask_differences':int(np.count_nonzero(occupied(a)!=occupied(b))),'diagnostics':diag}
    check(result['augmented']['occupied_early']==58890 and result['augmented']['occupied_late']==58890,'equal counts')
    return {'kind':'primary_snapshot_replay_and_original_diagnostic',**result}

GROUPS={f'{i:02d}':globals()[f'g{i:02d}'] for i in range(1,16)}
TELEMETRY={'09','12','13','14'}
def load_kernel(args):
    if args.source_module:
        check(sha(SRC/'U1/dee_kernel_v27.cpp')==SOURCE_SHA,'source verification')
        sys.path.insert(0,str(Path(args.source_module).resolve()));k=importlib.import_module('dee_kernel_v27')
        return k,{'mode':'same_source_linux_build_not_windows_binary','module_sha256':sha(k.__file__),'source_sha256':SOURCE_SHA}
    if args.wheel:
        check(sha(args.wheel)==WHEEL_SHA,'official wheel SHA256 mismatch')
    check(sys.version_info[:2]==(3,13),'CPython 3.13 required by supplied binary')
    import dee_universe_v27 as p
    from dee_universe_v27 import dee_kernel_v27 as k
    check(sha(p.__file__)==PACKAGE_SHA,'package identity');check(sha(k.__file__)==BINARY_SHA,'Windows kernel identity')
    return k,{'mode':'official_windows_binary','module_sha256':sha(k.__file__),'package_sha256':sha(p.__file__),'wheel_verified':bool(args.wheel)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--groups',default='all');ap.add_argument('--solo-telemetria',action='store_true');ap.add_argument('--wheel',type=Path);ap.add_argument('--source-module',type=Path);ap.add_argument('--out',type=Path,default=Path('resultados_verificacion.json'));args=ap.parse_args()
    groups=sorted(TELEMETRY) if args.solo_telemetria else (list(GROUPS) if args.groups=='all' else [s.strip().zfill(2) for s in args.groups.split(',')])
    k=None;env={'mode':'telemetry_only'}
    if any(g not in TELEMETRY for g in groups):k,env=load_kernel(args)
    report={'schema':'DEE.PN.verification.v1','runtime':{'python':sys.version,'numpy':np.__version__,'platform':platform.platform(),**env},'groups':{}}
    for g in groups:
        if g not in GROUPS:raise ValueError('unknown group '+g)
        start=time.monotonic()
        try:
            val=GROUPS[g](k);report['groups'][g]={'status':'PASS','seconds':time.monotonic()-start,**val};print(g,'PASS',flush=True)
        except Exception as exc:
            report['groups'][g]={'status':'FAIL','error':str(exc),'exception':type(exc).__name__};print(g,'FAIL',repr(exc),flush=True)
    report['all_pass']=all(x['status']=='PASS' for x in report['groups'].values());args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    return 0 if report['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
