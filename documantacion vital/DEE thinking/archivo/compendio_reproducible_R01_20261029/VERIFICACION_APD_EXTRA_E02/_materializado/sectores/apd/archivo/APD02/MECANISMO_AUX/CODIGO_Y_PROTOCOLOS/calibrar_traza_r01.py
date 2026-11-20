"""Bounded native action-trace/FAILURE routing sensitivity, never a host switch.

Physical AUX branches only. Native full-state snapshots are preserved; this
does not claim to clone or continue the parent's persistent service SQLite.
"""
import argparse, gc, gzip, hashlib, json, shutil, sys, time
from pathlib import Path


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    data=json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2).encode('utf8')+b'\n'
    with p.open('xb')as f:f.write(gzip.compress(data,mtime=0)if p.suffix=='.gz'else data)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--parent',default='APD02_BASELINE');a=p.parse_args()
    if a.out.exists():raise FileExistsError('Fresh result revision only')
    a.out.mkdir(parents=True);sys.path.insert(0,str(a.system.resolve()))
    from app.lives import Store
    from app.native_tools import physical
    from app.process_control import protect_current,current_resources
    from dee_thinking import _native as d
    from dee_thinking.consolidated import exact_observation,exact_receipt
    from capacidades import selector_acrecion_nativo as sel
    protect_current(output=a.out/'RECURSOS.json',memory_limit=512*1024*1024)
    protocol=Path(__file__).with_name('PROTOCOLO_TRAZA_R01.json');proto=json.loads(protocol.read_bytes())
    O=tuple(proto['origin']);N=67;P='APD02.trace.R01'
    def at(v):return sel.at(O,v,N)
    def obs(w,pos):return exact_observation(w.world.runtime.observe(d.Coordinate(*pos)))
    def refs(w):return[obs(w,at(v))for v in((-1,-1,0),(1,-1,0))]
    def declare(w,name,pos,direction,state=1,semantic=1):
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*pos);c.direction=d.Direction(*direction)
        c.state=state;c.semantic=semantic;c.allow_experience=True;c.allow_probe=False
        i=d.InterfaceSpec();i.name=name;i.channel=c;w.world.declare_interface(i)
    def submit(w,name,value,tick):
        r=w.world.submit(name,value,tick);return{'id':int(r.id),'port':name,'value':value,'tick':tick}
    def receipts(w,rs):return[{**r,'receipt':exact_receipt(w.world.runtime.receipt(r['id']))}for r in rs]
    store=Store(a.system);parent=store.record(a.parent);sources=[]
    for i,f in enumerate((Path(__file__),protocol,a.system/'capacidades/selector_acrecion_nativo.py',a.system/'app/process_control.py')):
        target=a.out/'CODIGO_EJECUTADO'/(str(i).zfill(2)+'_'+f.name);target.parent.mkdir(exist_ok=True);shutil.copyfile(f,target)
        sources.append({'source':str(f),'file':target.relative_to(a.out).as_posix(),'sha256':sha(target),'bytes':target.stat().st_size})
    emit(a.out/'ANTES_DEL_PRIMER_TICK.json',{'parent':parent,'protocol':proto,'sources':sources,'native_not_yet_started':True,'resources':current_resources()})
    started=time.monotonic();prep='APD02_TRACE_R01_PREP'
    emit(a.out/'00_FORK_PREP.json.gz',store.fork(a.parent,prep,kind='APD02_PHYSICAL_AUX_COMPLETE_SNAPSHOT_NO_SERVICE_CLONE'))
    def prepare(w):
        rows={tuple(r['site']):r for r in sel.geometry(O,N)if tuple(r['site'])not in(at((-3,3,0)),at((3,3,0)))}
        for sign in(-1,1):
            for v in((5*sign,5,0),(4*sign,4,-3),(6*sign,6,0),(sign,1,1)):
                pos=at(v);rows[pos]={'site':pos,'state':0,'s_reg':0,'semantic':4,'direction':(0,0,0),'raw':int(d.pack_record(0,0,0,0,0,4))}
        rows=[rows[k]for k in sorted(rows)];pre=[obs(w,r['site'])for r in rows]
        route_points={at((sign*k,k,-2))for sign in(-1,1)for k in range(4,66)}
        route_pre=[obs(w,pos)for pos in sorted(route_points)]
        if any(int(o['raw'])for o in pre+route_pre):raise ValueError('Nonzero RAW intersects frozen new anatomy/route; no cleanup or relocation')
        rs=[];tick=w.tick+2
        for n,r in enumerate(rows):
            name=P+'.prepare.'+str(n);declare(w,name,r['site'],(0,0,0),r['state'],r['semantic']);rs.append(submit(w,name,0,tick))
        w.run_until(tick+1);sel.declare(w.world,O,N,P)
        for sign in(-1,1):
            suffix='p'if sign==1 else'm'
            declare(w,P+'.fail.'+suffix,at((4*sign,4,1)),(0,0,-1))
            declare(w,P+'.sham.'+suffix,at((4*sign,4,5)),(0,0,-1))
            declare(w,P+'.restoreZ.'+suffix,at((6*sign,6,-3)),(0,0,1))
            declare(w,P+'.contact.'+suffix,at((2*sign,-2,-3)),(0,0,1))
        return{'pre':pre,'route_pre':route_pre,'geometry':rows,'requests':receipts(w,rs),'after':physical(w.world,occupation=True),'references':refs(w)}
    preparation=store.mutate(prep,'APD02_TRACE_R01_PREPARE_NO_LEARNED_CONTENT',prepare)
    emit(a.out/'01_PREPARACION.json.gz',preparation)
    seeds={}
    for label,side in(('positive','B'),('negative','A')):
        life='APD02_TRACE_R01_'+label+'_SEED';emit(a.out/(label+'_FORK.json.gz'),store.fork(prep,life,kind='APD02_EXPLICIT_MATCHED_SEED'))
        def teach(w,side=side):
            k=(w.tick+5)//391+1;k=k if k%2 else k+1;arrival=k*391
            before=refs(w);r=sel.experience(w.world,side,arrival,P);w.run_until(arrival+2)
            return{'side_explicit_teacher':side,'arrival':arrival,'before':before,'after':refs(w),'request':sel.receipt(w.world,r),'physical':physical(w.world)}
        result=store.mutate(life,'APD02_TRACE_R01_ONE_EXPLICIT_SEED',teach);emit(a.out/(label+'_SEED.json.gz'),result);seeds[label]=life
    outcomes=[]
    for index,(seed,mode,query)in enumerate(proto['arms']):
        if time.monotonic()-started>proto['budget_seconds']:
            outcomes.append({'arm':index,'not_executed':'Frozen300s limit'});continue
        life='APD02_TRACE_R01_ARM'+str(index);folder=a.out/('ARM'+str(index));folder.mkdir()
        emit(folder/'00_FORK.json.gz',store.fork(seeds[seed],life,kind='APD02_NATIVE_TRACE_SENSITIVITY_CONTROL'))
        def trial(w):
            k=(w.tick+75+390)//391;k=k if k%2 else k+1;boundary=k*391;q=boundary-70
            w.save(folder/'ANTES_COMPLETO.deetsnap.gz');before=refs(w);rs=[]
            if query:rs+=sel.query(w.world,q,5,P)
            for suffix in('m','p'):
                rs+=[submit(w,P+'.restoreZ.'+suffix,0,q+9),submit(w,P+'.contact.'+suffix,0,q+68)]
            frames=[]
            points={at(v)for v in((-1,-1,0),(1,-1,0),(-1,-1,-1),(1,-1,-1),(0,0,0))}
            for sign in(-1,1):
                points|={at((sign*t,t,z))for t,z in((2,0),(3,0),(4,0),(5,-1),(6,-2),(65,-2))}
                points|={at((2*sign,-2,-2)),at((2*sign,-2,-1))}
            w.run_until(q+6);reader=sel.read(w.world,O,N)
            # The actual native action has been read/committed before a generic
            # synthetic FAILURE enters; neither input port depends on its sign.
            if mode!='omit':
                for suffix in('m','p'):rs.append(submit(w,P+('.fail.'if mode=='real'else'.sham.')+suffix,0,q+7))
            for tick in list(range(q+6,q+15))+list(range(q+64,boundary+4)):
                w.run_until(tick);frames.append({'tick':w.tick,'references':refs(w),'sites':[obs(w,p)for p in sorted(points)]})
            w.save(folder/'DESPUES_CONTACTO_COMPLETO.deetsnap.gz');after=refs(w)
            rq=w.tick+4;qr=sel.query(w.world,rq,5,P);w.run_until(rq+6);later=sel.read(w.world,O,N);w.run_until(rq+8)
            w.save(folder/'DESPUES_CONSULTA_COMPLETO.deetsnap.gz')
            return{'seed':seed,'mode':mode,'query_present':query,'boundary':boundary,'query_tick':q,
                    'before':before,'committed_action_reader':reader,'after_contact':after,'later_common_reader':later,
                    'requests':receipts(w,rs)+[sel.receipt(w.world,r)for r in qr],
                    'frames':frames,'physical_final':physical(w.world,occupation=True),
                    'scope':'Forced generic FAILURE calibration, not a task result, useful policy or service clone. Both zero-return sources/resources fixed, no action-dependent host port.'}
        try:
            result=store.mutate(life,'APD02_TRACE_R01_FROZEN_FAILURE_SENSITIVITY',trial)
            emit(folder/'RESULTADO.json.gz',result);v=result['result']
            summary={'arm':index,'seed':seed,'mode':mode,'query':query,'action':v['committed_action_reader']['choice'],
                     'refs_before':[o['s_reg']for o in v['before']],'refs_after':[o['s_reg']for o in v['after_contact']],
                     'later':v['later_common_reader']['choice'],'final_record':store.record(life)}
        except Exception as error:
            summary={'arm':index,'seed':seed,'mode':mode,'query':query,'error':{'type':type(error).__name__,'message':str(error)},'reached':store.record(life),'no_rollback':True}
            emit(folder/'ERROR_CONSERVADO.json',summary)
        outcomes.append(summary);print(json.dumps(summary,ensure_ascii=False),flush=True);gc.collect()
    emit(a.out/'RESULTADOS.json',{'protocol':proto,'parent':parent,'outcomes':outcomes,'elapsed_seconds':time.monotonic()-started,'resources':current_resources(),'new_organization':'New P0 selector region in physical AUX descendant, no inherited selector knowledge or service cloned claim'})
    return 0


if __name__=='__main__':raise SystemExit(main())
