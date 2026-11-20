"""Installed-engine finite revision port, baseline constructors vs native4.5.

No historical measurements/targets are imported. 4.0 uses only the exact
geometry and extra_interfaces preparation functions. The 4.5 branch imports
no historical apparatus and uses the installed native revision implementation.
"""
from __future__ import annotations
import argparse,importlib,json,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from neutral_differential import native,put,sha,exact_array,operative,receipt,observation
from cpc_port import directional

ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=ROOT/'evidence/CPC7/src'
CONFIG=Path(__file__).with_name('revision_port_config.json')

def prepare(case,d,version):
    if version=='4.0.0':
        sys.path.insert(0,str(EVIDENCE))
        ref=importlib.import_module('repertoire_reference');revision=importlib.import_module('update_methods')
        g,ports=ref.geometry(case);ports+=revision.extra_interfaces(g)
        recipe=d.OrganizationRecipe.research(case['N'],[],0);recipe.interfaces=ports;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
        return d.OrganizationalWorld.create(recipe),g,None,{name:sha(EVIDENCE/name) for name in ('repertoire_reference.py','update_methods.py')}
    o=d.RepertoireOptions();o.dimension=case['N'];o.forms=2;o.plane_gap=case['plane_gap'];o.translation=d.Coordinate(*case['translation']);o.revision_interfaces=True;o.revision_form=0;o.execution=d.TickOptions(d.Backend.LAZY,1)
    p=d.prepare_repertoire(o)
    return p.create_world(),p.geometry(),p,{}

def run(case,out,version,config_hash):
    out.mkdir(parents=True,exist_ok=False);started=time.monotonic();d,engine=native(version)
    w,g,p,sources=prepare(case,d,version);r=w.runtime;fs=g['forms'];calls=[];frames=[];reads=[];checkpoints=[];n=case['N'];q=case['query_payload']
    if p is not None and any(name in sys.modules for name in ('repertoire_reference','update_methods')):raise AssertionError('Historical apparatus imported by candidate')
    def submit(port,load,tick,probe=False):
        rr=(w.probe if probe else w.submit)(port,load,tick)
        calls.append({'id':str(rr.id),'port':port,'payload':load,'at':str(tick),'call_tick':str(r.current_tick),'kind':'probe' if probe else 'experience'})
        return int(rr.id)
    def record_native(results,ports,loads,ticks,kind='experience'):
        for rr,port,load,tick in zip(results,ports,loads,ticks):calls.append({'id':str(rr.id),'port':port,'payload':load,'at':str(tick),'call_tick':str(r.current_tick),'kind':kind})
        return [int(rr.id) for rr in results]
    def learn(i,sign,tick):
        name=fs[i]['name'];ports=[name+'.signal',name+'.event.'+('plus' if sign==1 else 'minus')]
        if p is None:return [submit(ports[0],5,tick),submit(ports[1],11,tick)]
        return record_native(d.experience_form(w,p,i,sign,tick),ports,[5,11],[tick,tick])
    def capture(tick,full=False):
        w.run_until(tick);row={'tick':str(tick),'forms':{f['name']:observation(r,f['hub'],d) for f in fs}}
        if full:row.update({'raw':exact_array(r.raw_copy(),out/f'T{tick}.raw.u64.gz'),'clock':exact_array(r.clock_copy(),out/f'T{tick}.clock.u64.gz'),'operative':operative(r)})
        frames.append(row);put(out/'PROGRESS.json',{'case_id':case['id'],'last_tick':str(tick),'frames':frames,'calls':calls,'readouts':reads})
    def save(tick):
        f=out/f'PENDING_T{tick}.deetsnap';w.save_snapshot(str(f));checkpoints.append({'path':f.name,'tick':str(tick),'sha256':sha(f)})
    def panel(tick,label):
        w.run_until(tick);ids=[]
        for i,f in enumerate(fs):
            if p is None:ids.append(submit(f['name']+'.signal',q,tick,True))
            else:ids+=record_native([d.query_form(w,p,i,q,tick)],[f['name']+'.signal'],[q],[tick],'probe')
        capture(tick+3,True)
        for i,(f,rid) in enumerate(zip(fs,ids)):
            rr=receipt(r.receipt(rid));raw=observation(r,f['hub'],d);value=directional(raw,rr,q)
            if p is not None:
                measured=d.read_form_response(w,p,i,rid,q,tick+3)
                if measured.covered!=value['covered'] or measured.value!=value['value']:raise AssertionError('Native physical decoder differs')
            reads.append({'form':f['name'],'panel':label,'tick':str(tick+3),**value})
    put(out/'CONFIG.json',{'case':case,'config_sha256':config_hash,'source_sha256':sha(__file__),'engine':engine,'constructor_sources':sources,'geometry':g,'adapter':'Canonical cue-first receipt ordering on both engines; physical inputs unchanged from documented apparatus. K2 only, offpath z+10 is not treated as a general populated-plane sham.'})
    capture(0,True)
    for i,sign in enumerate(case['initial_signs']):learn(i,sign,0)
    capture(3,True);panel(n,'BEFORE_REVISION')
    at=4*n;sign=case['new_sign'];label='plus' if sign==1 else 'minus';suffix='' if case['mode']=='treatment' else 'sham.'
    names=[];loads=[];times=[]
    if case['method']=='symmetric_counterflow':
        for s in ('plus','minus'):names.append('revision.counter.'+suffix+s);loads.append(0);times.append(at-4)
    names += ['L01.signal','L01.event.'+label];loads += [5,11];times += [at,at]
    if case['method']=='double_teacher':names.append('revision.teacher2.'+suffix+label);loads.append(11);times.append(at)
    if p is None:
        for port,load,tick in zip(names,loads,times):submit(port,load,tick)
    else:record_native(d.revise_form(w,p,0,sign,at,case['method'],case['mode']),names,loads,times)
    save(n+3)
    for tick in (at-4,at-2,at-1,at,at+2,at+3):capture(tick,tick in (at-4,at+3))
    panel(5*n,'AFTER_REVISION');save(5*n+3)
    restored=d.OrganizationalWorld.load_snapshot(str(out/checkpoints[-1]['path']))
    if restored.runtime.raw_copy()!=r.raw_copy() or restored.runtime.clock_copy()!=r.clock_copy() or restored.runtime.current_tick!=r.current_tick:raise AssertionError('Restore differs')
    result={'schema':'DEE45.CPC_native_port.measurements.v1','case_id':case['id'],'kind':'finite_revision','library':version,'status':'PASS','engine':engine,'config_sha256':config_hash,'constructor_sources':sources,'source_sha256':sha(__file__),'frames':frames,'readouts':reads,'calls':[{**c,'final_receipt':receipt(r.receipt(int(c['id'])))} for c in calls],'final_operative':operative(r),'checkpoints':checkpoints,'technical':{'save_load_RAW_clocks_tick_equal':True,'candidate_historical_lab_imports':[] if p is not None else None},'preparations':1,'elapsed_seconds':time.monotonic()-started,'scope':'Software apparatus equivalence, two finite exposed alternatives, not autonomous regulation or new semantic meaning.'}
    put(out/'RESULT.json',result);print(json.dumps({'case':case['id'],'library':version,'readouts':[x['value'] for x in reads],'covered':sum(x['covered'] for x in reads),'seconds':result['elapsed_seconds']}),flush=True)

def suite(a):
    config=json.loads(a.config.read_text(encoding='utf8'));a.out.mkdir(parents=True,exist_ok=True);rows=[]
    for case in config['cases']:
        target=a.out/case['id'];result=target/'RESULT.json'
        if result.exists():value=json.loads(result.read_text(encoding='utf8'))
        else:
            try:
                argv=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'case','--config',str(a.config.resolve()),'--case-id',case['id'],'--expected-version',a.expected_version,'--out',str(target.resolve())]
                process=subprocess.run(argv,capture_output=True,text=True,timeout=180);value={'status':'PASS' if process.returncode==0 and result.exists() else 'FAIL','returncode':process.returncode,'stdout':process.stdout,'stderr':process.stderr}
            except subprocess.TimeoutExpired as e:value={'status':'TIMEOUT','error':str(e)}
            put(a.out/(case['id']+'.PROCESS.json'),value)
        rows.append({'case_id':case['id'],'status':value['status'],'result':case['id']+'/RESULT.json'});put(a.out/'INDEX.json',{'schema':'DEE45.finite_revision_port.index.v1','library':a.expected_version,'config_sha256':sha(a.config),'cases':rows})
    if any(r['status']!='PASS' for r in rows):raise SystemExit(1)

def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='mode',required=True)
    for mode in ('suite','case'):
        a=sub.add_parser(mode);a.add_argument('--config',type=Path,default=CONFIG);a.add_argument('--out',type=Path,required=True);a.add_argument('--expected-version',required=True)
        if mode=='case':a.add_argument('--case-id',required=True)
    a=parser.parse_args()
    if a.mode=='suite':suite(a)
    else:
        config=json.loads(a.config.read_text(encoding='utf8'));run(next(x for x in config['cases'] if x['id']==a.case_id),a.out,a.expected_version,sha(a.config))
if __name__=='__main__':main()
