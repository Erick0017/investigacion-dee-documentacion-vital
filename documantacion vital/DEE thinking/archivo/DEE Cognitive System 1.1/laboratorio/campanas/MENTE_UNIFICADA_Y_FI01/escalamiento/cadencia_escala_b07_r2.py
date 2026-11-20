"""N67/N101 paired cadence after own acquisition, fresh auxiliary parents.

No MAIN migration; inherited contact experience is the same prospective R1
recipe. Both raw128 frames and later probes queued before the first window.
"""
import gc,os,json
from escala_n_b07_r1 import HERE,LAB,ROOT,E,sha,dump,plan,reader,native_imports,internal_A_close,memory_guard
REVISION='FI01.B07.dimension_cadence.same_acquired_newT0.r2'

def run(N,delta,ni,out):
    d,encode,decode,Store,Adapter,now,physical,body,ep=ni
    from dee_thinking.persistence import load_world_snapshot
    from capacidades import selector_acrecion_nativo as sel
    parent=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento/B07_FRESH_N67_N101_R1'/('FI01_B07_NEW_N'+str(N)+'_TOUCH_A.own_acquired.T393.deetsnap.gz')
    world,_=load_world_snapshot(parent);a=Adapter(world);del world;g=plan(N);memory_guard()
    life='FI01_B07_CADENCE_NEW_N'+str(N)+'_D'+str(delta)
    a.world.runtime.set_snapshot_metadata('MUFI01.B07.R2',encode({'life_id':life,'exact_fork_parent':str(parent),'parent_sha256':sha(parent),
      'scope':'Exact auxiliary fork after own acquired contact, not another MAIN trajectory.'}))
    initial=physical(a.world,occupation=True);requests=[];episodes=[];schedule=set()
    points={'E':E,'D':g['datum_site'],'C':g['remote_aggregate_site'],'A':[14,14,15],'B':[16,14,15]}
    points.update({n['id']:n['site']for n in g['nodes']})
    for i,leaf in enumerate((1000,1000+delta)):
        raw=[0]*128 if i==0 else[2]+[0]*127;root=leaf-g['raw_relative_tick'];datum=root+38;q=datum-3;req=[]
        for s in g['raw_sources']:req.append(body.send(a,'B07.raw.'+s['id'],s['site'],s['direction'],root+s['injection_tick_relative'],raw[s['component_index']]))
        for s in g['generic_sources']:req.append(body.send(a,'B07.raw.'+s['id'],s['site'],s['direction'],root+s['injection_tick_relative'],0))
        req+=sel.query(a.world,q,5,'B07.selector');requests+=req
        episodes.append({'index':i,'raw_components':raw,'leaf_tick':leaf,'datum_tick':datum,'query_tick':q,'reader_tick':q+6,'request_ids':[r['id']for r in req]})
        schedule.update([leaf-1,leaf,leaf+1,datum-2,datum-1,datum,datum+1,q+6,q+8])
        schedule.update(root+n['join_tick_relative']+dt for n in g['nodes']for dt in(-1,0,1))
    # All arms share final age1379, >=3*101 after the latest reserved read1076.
    probes=[]
    for i,(q,value)in enumerate(((1390,0),(1457,2))):
        rr=[body.send(a,'B07.retention.directS',g['datum_site'],[0,0,0],q+3,value)]+sel.query(a.world,q,5,'B07.selector')
        requests+=rr;probes.append({'index':i,'raw_value':value,'query_tick':q,'reader_tick':q+6,'request_ids':[r['id']for r in rr]})
        schedule.update(range(q+2,q+9))
    before=out/(life+'.ALL_PENDING.T393.deetsnap.gz');a.save(before)
    frames=[];readers=[];probe_readers=[];passive=None;snapshots=[{'path':str(before),'sha256':sha(before),'tick':393}]
    schedule.add(1379)
    for t in sorted(schedule):
        a.run_until(t);memory_guard();frames.append({'tick':a.tick,'fields':{k:body.obs(a,p)for k,p in points.items()}})
        for ep in episodes:
            if t==ep['reader_tick']:readers.append({'episode':ep['index'],**reader(a,ni)})
        for probe in probes:
            if t==probe['reader_tick']:probe_readers.append({'probe':probe['index'],**reader(a,ni)})
        if t==1379:
            passive=physical(a.world,occupation=True);p=out/(life+'.PASSIVE.T1379.deetsnap.gz');a.save(p)
            snapshots.append({'path':str(p),'sha256':sha(p),'tick':a.tick})
    final=physical(a.world,occupation=True);p=out/(life+'.FINAL.T'+str(a.tick)+'.deetsnap.gz');a.save(p);snapshots.append({'path':str(p),'sha256':sha(p),'tick':a.tick})
    result={'revision':REVISION,'life':life,'N':N,'new_T0':False,'new_T0_parent':True,'delta':delta,'label':'N'+str(N)+'_delta'+str(delta),
      'parent_snapshot':str(parent),'parent_sha256':sha(parent),'initial':initial,'geometry':g,'episodes':episodes,'readers':readers,
      'post_3N_probes':probes,'post_3N_probe_readers':probe_readers,'frames':frames,'passive_common_horizon':passive,'snapshots':snapshots,
      'requests':[{**r,'receipt':sel.exact_receipt(a.world.runtime.receipt(r['id']))}for r in requests],
      'final':final,'peak_process_bytes':memory_guard(),'scope':'Paired N/interval test in newly acquired auxiliaries only, no old6. 3N is an observation horizon, not proof of a specific return lineage.'}
    dump(out/(life+'.json.gz'),result)
    row={'life':life,'N':N,'delta':delta,'choices':[r['choice']for r in readers],'post_3N_choices':[r['choice']for r in probe_readers],
      'requested':len(requests),'applied':sum(r['receipt']['status']=='applied'for r in result['requests']),
      'passive_occupied':passive['occupied'],'final':final,'snapshot':snapshots[-1]}
    print(json.dumps(row),flush=True);del a;gc.collect();memory_guard();return row

def main():
    authorization=internal_A_close(LAB/'CIERRE_INTERNO_A.json');os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    ni=native_imports();out=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento/B07_CADENCE_N67_N101_R2'
    dump(out/'PROTOCOLO.json',{'revision':REVISION,'authorization':authorization,'fixed_before_first_tick':ni[5](),'script_sha256':sha(__file__),
      'dependency_sha256':sha(HERE/'escala_n_b07_r1.py'),'N':[67,101],'deltas':[2,16],'raw_leaf1':1000,'raw_leaf2':'1000+delta',
      'same_input_pair':['128zero','first2rest0'],'all_inputs_prequeued':True,'reader':'Same six classes atq+6, no target/phase choice.',
      'common_passive_tick':1379,'post_common_queries':[[1390,0],[1457,2]],'new_T0_parent_with_own_contact':True,
      'scope':'One acquisition prefix per N, paired diagnostic forks. No MAINold6 or worldresize, no3Nstability guarantee.'})
    rows=[]
    for N in(67,101):
        for delta in(2,16):rows.append(run(N,delta,ni,out))
    dump(out/'RESUMEN.json',{'rows':rows,'finished_utc':ni[5]()})
if __name__=='__main__':main()
