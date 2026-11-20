"""Independent installed-engine CPC apparatus equivalence recorder.

Only4.0 baseline preparation reads the selected frozen constructor source.
4.5 preparation and ordinary experiences/queries use the installed native API.
No terminal measurements, teaching logs, targets or returned answers are read.
"""
from __future__ import annotations
from pathlib import Path
import argparse,importlib,json,subprocess,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from neutral_differential import native,put,sha,exact_array,operative,receipt,observation

ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=ROOT/'evidence/CPC7/src'
CONFIG=Path(__file__).with_name('port_config.json')


def baseline(case,d):
    sys.path.insert(0,str(EVIDENCE));sys.path.insert(0,str(EVIDENCE/'endogenous'))
    if case['kind']=='repertoire':
        mod=importlib.import_module('repertoire_reference');g,ports=mod.geometry(case)
        recipe=d.OrganizationRecipe.research(case['N'],[],0);recipe.interfaces=ports
        sources={'repertoire_reference.py':sha(EVIDENCE/'repertoire_reference.py')}
    else:
        mod=importlib.import_module('integrated_revision');p=mod.prepare_geometry(case);g=p['geometry']
        recipe=d.OrganizationRecipe.research(67,p['placements'],0);recipe.interfaces=p['interfaces']
        sources={name:sha(EVIDENCE/name) for name in ('integrated_revision.py','selective_native.py','residue_regulation.py','order_memory.py','endogenous/comparison_need.py','endogenous/body_source.py')}
    recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    return d.OrganizationalWorld.create(recipe),g,None,sources


def candidate(case,d):
    if case['kind']=='repertoire':
        o=d.RepertoireOptions();o.dimension=case['N'];o.forms=case['K'];o.plane_gap=case['plane_gap'];o.translation=d.Coordinate(*case['translation']);o.revision_interfaces=False
        o.execution=d.TickOptions(d.Backend.LAZY,1);p=d.prepare_repertoire(o)
    else:
        o=d.IntegratedOptions();o.guard_mode=case['guard_mode'];o.revision_interfaces=True;o.execution=d.TickOptions(d.Backend.LAZY,1);p=d.prepare_integrated_u0(o)
    return p.create_world(),p.geometry(),p,{}


def prepare(case,d,version):return baseline(case,d) if version=='4.0.0' else candidate(case,d)


def forms(geometry):return geometry['forms']
def xyz(form):return form['hub']


def directional(o,rr,payload):
    applied=rr['status']=='applied';active=o['state']>0 and o['semantic']!=5
    valid=applied and active and o['semantic']==1 and o['s_reg']>payload and o['direction'] in ([-1,-1,0],[-1,1,0])
    return {'physical':o,'receipt':rr,'covered':valid,'value':o['direction'][1] if valid else None,
            'status':'COVERED' if valid else rr['status'] if not applied else 'OUTSIDE_FIXED_DIRECTIONAL_READOUT'}


def run(case,out,version,config_hash):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);start=time.monotonic();d,engine=native(version)
    w,g,p,sources=prepare(case,d,version);r=w.runtime;fs=forms(g);calls=[];frames=[];reads=[];pending={};checkpoints=[]
    if version!='4.0.0' and any(x in sys.modules for x in ('integrated_revision','selective_native','order_memory','repertoire_reference')):
        raise AssertionError('Candidate imported historical apparatus implementation')
    def submit(port,payload,tick,probe=False):
        result=(w.probe if probe else w.submit)(port,payload,tick)
        calls.append({'id':str(result.id),'port':port,'payload':payload,'at':str(tick),'call_tick':str(r.current_tick),'kind':'probe' if probe else 'experience'})
        return int(result.id)
    def lesson(indices,values,tick,mode='paired'):
        for i in indices:
            name=fs[i]['name'];sign=values[i]
            if p is not None and mode=='paired':
                got=d.experience_form(w,p,i,sign,tick)
                for port,load,res in zip((name+'.signal',name+'.event.'+('plus' if sign==1 else 'minus')),(5,11),got):
                    calls.append({'id':str(res.id),'port':port,'payload':load,'at':str(tick),'call_tick':str(r.current_tick),'kind':'experience'})
            else:
                # Same fixed ordinary interface codec in controls; no response is inspected.
                if mode=='paired':
                    submit(name+'.signal',5,tick)
                    submit(name+'.event.'+('plus' if sign==1 else 'minus'),11,tick)
                else:
                    if mode!='no_event':submit(name+'.event.'+('plus' if sign==1 else 'minus'),11,tick)
                    submit(name+'.signal',5,tick+int(mode=='unpaired'))
    def query(indices,tick,payload,label):
        rs=[]
        for i in indices:
            if p is not None:
                res=d.query_form(w,p,i,payload,tick);identifier=int(res.id)
                calls.append({'id':str(identifier),'port':fs[i]['name']+'.signal','payload':payload,'at':str(tick),'call_tick':str(r.current_tick),'kind':'probe'})
            else:identifier=submit(fs[i]['name']+'.signal',payload,tick,True)
            rs.append((i,identifier,payload,label))
        pending.setdefault(tick+3,[]).extend(rs)
    def capture(tick,full=False):
        w.run_until(tick)
        row={'tick':str(tick),'forms':{f['name']:observation(r,xyz(f),d) for f in fs}}
        if case['kind']=='integrated':
            body=g['body'];row['body']={name:observation(r,body[name],d) for name in ('center','A','B','emission_site')}
            row['questions']={name:observation(r,b['request_site'],d) for name,b in g['need']['branches'].items()}
            row['own_banks']={name:observation(r,b['hub'],d) for name,b in g['banks'].items()}
            row['actions']={name:observation(r,b['site'],d) for name,b in g['actions'].items()}
            row['names']={name:observation(r,b['site'],d) for name,b in g['names'].items()}
        if full:
            row['raw']=exact_array(r.raw_copy(),out/f'T{tick}.raw.u64.gz');row['clock']=exact_array(r.clock_copy(),out/f'T{tick}.clock.u64.gz');row['operative']=operative(r)
        frames.append(row)
        for i,identifier,payload,label in pending.get(tick,[]):
            rr=receipt(r.receipt(identifier));physical=observation(r,xyz(fs[i]),d)
            decoded=directional(physical,rr,payload)
            if p is not None:
                native_read=d.read_form_response(w,p,i,identifier,payload,tick)
                if native_read.covered!=decoded['covered'] or native_read.value!=decoded['value']:raise AssertionError('Native readout and frozen physical predicate differ')
            reads.append({'form':fs[i]['name'],'panel':label,'tick':str(tick),**decoded})
        put(out/'PROGRESS.json',{'case_id':case['id'],'last_tick':str(tick),'frames':frames,'readouts':reads,'calls':calls})
    def save(tick):
        path=out/f'PENDING_T{tick}.deetsnap';w.save_snapshot(str(path));checkpoints.append({'path':path.name,'tick':str(tick),'sha256':sha(path)})
    put(out/'CONFIG.json',{'case':case,'config_sha256':config_hash,'source_sha256':sha(__file__),'engine':engine,'constructor_sources':sources,'geometry':g,
        'reference_adapter':'Only frozen preparation constructors are reused. Paired same-boundary cue/event requests use cue-first receipt order on both engines, matching the new native helper; this does not claim the original CPC5 event-first receipt IDs. Physical ports, payloads and event ticks remain those of the apparatus.'})
    if case['kind']=='repertoire':
        k=case['K'];n=case['N'];mode=case['mode'];payload=case['query_payload']
        pattern=case['history_pattern']
        values=[(1 if i%2==0 else -1) if pattern=='alternating_plus_first' else (-1 if i%2==0 else 1) if pattern=='alternating_minus_first' else (-1 if i%3==0 else 1) for i in range(k)]
        capture(0,True)
        if case['curriculum']=='simultaneous3':
            lesson(range(k),values,0,mode);capture(3+int(mode=='unpaired'),True)
            for cycle in (1,2,3):
                at=n*cycle;w.run_until(at);query(range(k),at,payload,'ROUND'+str(cycle))
                if cycle==1:save(at)
                capture(at+3,True)
        else:
            lesson(range(32),values,0,mode);capture(3)
            w.run_until(n);query(range(32),n,payload,'OLD_BEFORE_NEW');capture(n+3)
            w.run_until(n+8);lesson(range(32,k),values,n+8,mode);capture(n+11,True)
            for cycle in (2,3):
                w.run_until(n*cycle);query(range(32),n*cycle,payload,'OLD_AFTER_NEW_'+str(cycle));capture(n*cycle+3)
                w.run_until(n*cycle+8);query(range(32,k),n*cycle+8,payload,'NEW_'+str(cycle))
                if cycle==2:save(n*cycle+8)
                capture(n*cycle+11,cycle==3)
    else:
        # This schedule is the actual CPC7 integrated revision protocol.
        submit('event.'+case['history'][0],3,0);submit('event.'+case['history'][1],3,1);submit('order.read',7,2,True)
        lesson(range(8),case['bank_values'],0)
        full={0,19,70,75,142,338,405,472};times={0,3,5,11,15,19,69,70,72,75,134,137,139,142,201,204,335,338,402,405,469,472}
        for at in sorted(times):
            w.run_until(at)
            if at==11:
                for lane in ('left','right'):submit('need.actual.'+lane+'.'+str(case['actual']),17,11)
            if at==69:
                for port in g['action_inputs']:submit(port,7,69,True)
                save(69)
            if at==72:
                for item in g['names'].values():submit(item['teach_port'],5,72)
            if at==134:lesson(range(8,16),case['bank_values'],134)
            if at==139:
                for item in g['names'].values():submit(item['query_port'],case['name_query_payload'],139,True)
            if at in (201,335):query(range(2,16),at,5,'LOWER_'+str(at+3))
            if at==402:
                if p is not None:
                    results=d.revise_form(w,p,2,case['new_sign'],402,'double_teacher',case['revision_mode'])
                    labels=['L03.signal','L03.event.'+('plus' if case['new_sign']==1 else 'minus'),'revision.second.'+case['revision_mode']+'.'+('plus' if case['new_sign']==1 else 'minus')]
                    for port,res,load in zip(labels,results,(5,11,11)):calls.append({'id':str(res.id),'port':port,'payload':load,'at':'402','call_tick':'402','kind':'experience'})
                else:
                    lesson([2],[case['new_sign']]*16,402)
                    label='plus' if case['new_sign']==1 else 'minus';submit(g['integrated_revision']['auxiliary_ports'][case['revision_mode']+'.'+label],11,402)
            if at==469:query(range(2,16),469,5,'POST_REVISION_472')
            capture(at,at in full)
    final_tick=int(r.current_tick);save(final_tick)
    # Same-process round-trip: no re-preparation and no teachingmap is loaded.
    restored=d.OrganizationalWorld.load_snapshot(str(out/checkpoints[-1]['path']))
    raw_equal=restored.runtime.raw_copy()==r.raw_copy();clock_equal=restored.runtime.clock_copy()==r.clock_copy()
    if not(raw_equal and clock_equal and restored.runtime.current_tick==r.current_tick):raise AssertionError('Physical save/load differs')
    result={'schema':'DEE45.CPC_native_port.measurements.v1','case_id':case['id'],'kind':case['kind'],'library':version,'status':'PASS',
        'engine':engine,'config_sha256':config_hash,'constructor_sources':sources,'source_sha256':sha(__file__),'frames':frames,'readouts':reads,
        'calls':[{**c,'final_receipt':receipt(r.receipt(int(c['id'])))} for c in calls],'final_operative':operative(r),'checkpoints':checkpoints,
        'technical':{'save_load_RAW_clocks_tick_equal':True,'candidate_historical_lab_imports':[] if version!='4.0.0' else None},
        'preparations':1,'elapsed_seconds':time.monotonic()-start,
        'scope':'Finite software port equivalence; physical content classes are two, and named forms are not counted as general NSM meanings.'}
    put(out/'RESULT.json',result);print(json.dumps({'case':case['id'],'library':version,'queries':len(reads),'covered':sum(x['covered'] for x in reads),'seconds':result['elapsed_seconds']}),flush=True)


def suite(args):
    cfg=json.loads(args.config.read_text(encoding='utf-8'));args.out.mkdir(parents=True,exist_ok=True);rows=[]
    for case in cfg['cases']:
        target=args.out/case['id'];result=target/'RESULT.json'
        if result.exists():r=json.loads(result.read_text(encoding='utf-8'))
        else:
            argv=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'case','--config',str(args.config.resolve()),'--case-id',case['id'],'--expected-version',args.expected_version,'--out',str(target.resolve())]
            try:
                p=subprocess.run(argv,capture_output=True,text=True,timeout=600 if case['kind']=='repertoire' else 240)
                r={'status':'PASS' if p.returncode==0 and result.exists() else 'FAIL','returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
            except subprocess.TimeoutExpired as e:r={'status':'TIMEOUT','error':str(e)}
            put(args.out/(case['id']+'.PROCESS.json'),r)
        rows.append({'case_id':case['id'],'status':r['status'],'result':case['id']+'/RESULT.json'})
        put(args.out/'INDEX.json',{'schema':'DEE45.CPC_native_port.index.v1','library':args.expected_version,'config_sha256':sha(args.config),'cases':rows})
    if any(r['status']!='PASS' for r in rows):raise SystemExit(1)


def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='mode',required=True)
    for mode in ('suite','case'):
        a=s.add_parser(mode);a.add_argument('--config',type=Path,default=CONFIG);a.add_argument('--out',type=Path,required=True);a.add_argument('--expected-version',required=True)
        if mode=='case':a.add_argument('--case-id',required=True)
    args=p.parse_args()
    if args.mode=='suite':suite(args)
    else:
        cfg=json.loads(args.config.read_text(encoding='utf-8'));case=next(x for x in cfg['cases'] if x['id']==args.case_id)
        run(case,args.out,args.expected_version,sha(args.config))

if __name__=='__main__':main()
