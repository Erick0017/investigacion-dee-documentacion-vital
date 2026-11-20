"""Fresh N67/N101 auxiliaries: own acquired reference plus raw128 tree.

New T0 lives, never resized or transplanted MAIN. Same relative preparation,
experiences, raw vectors, fixed reader and absolute opportunities in both N.
"""
from __future__ import annotations
import gc,os
from ensayar_arbol_b05_r1 import (HERE,LAB,ROOT,E,sha,dump,native_imports,
    internal_A_close,memory_guard)
from arbol_umbral_adquirido_b01 import plan as auxiliary_plan

REVISION='FI01.B07.fresh_dimensions67_101.raw128.r1'
LEAVES=(1000,1300,1600,1900)

def plan(N):
    old=auxiliary_plan(128,N);od=old['datum_site'];D=(14,15,15)
    shift=[(D[i]-(od[1],od[2],od[0])[i])%N for i in range(3)]
    def xyz(p):
        v=(p[1],p[2],p[0]);return[(v[i]+shift[i]+(-2,2,3)[i])%N for i in range(3)]
    def vec(v):return[v[1],v[2],v[0]]
    def source(s):
        q={**s,'site':xyz(s['site']),'direction':vec(s['direction'])}
        if 'head'in s:q['head']=xyz(s['head'])
        return q
    raw=[source(s)for s in old['raw_sources']];generic=[source(s)for s in old['generic_sources']]
    C=[12,17,18];S=[14,15,16]
    generic.append({'id':'remote_root.constant_exit_X_minusY_minusZ','site':[11,18,19],
      'direction':[1,-1,-1],'injection_tick_relative':35,'payload':0})
    return {'revision':REVISION,'N':N,'level':128,'E':list(E),'datum_site':S,'remote_aggregate_site':C,
      'raw_sources':raw,'generic_sources':generic,'nodes':[{**q,'site':xyz(q['site'])}for q in old['nodes']],
      'raw_relative_tick':old['leaf_relative_tick'],'datum_relative_tick':38,
      'scope':'New auxiliary geometry; source coordinates change only by periodic representation. No lived-world resize.'}

def reader(a,ni):
    body=ni[7];obs=[];candidates=[]
    for x in(-1,0,1):
        for z in(0,-1):
            o=body.obs(a,(15+2*x,17,15+2*z));obs.append(o)
            if o['state']>0 and o['semantic']==1 and o['direction']==[x,1,z]:candidates.append({'choice':x,'observation':o})
    return {'tick':a.tick,'observations':obs,'candidates':candidates,
      'choice':candidates[0]['choice']if len(candidates)==1 else None}

def execute(N,history,ni,out):
    d,encode,decode,Store,Adapter,now,physical,body,ep=ni
    from capacidades import selector_acrecion_nativo as sel
    g=plan(N);placements=sel.placements(E,N);occupied={tuple(p['site'])for p in sel.geometry(E,N)}
    stops=[(15+3*x,18,15+3*z)for x in(-1,0,1)for z in(0,-1)]+[(15,14,15)]
    for site in stops:
        if site in occupied:continue
        q=d.InitialPlacement();q.site=d.Coordinate(*site);q.raw=d.pack_record(0,0,0,0,0,4);q.clock=0;q.role='Declared P0 actuator termination, not acquired knowledge';placements.append(q)
    recipe=d.OrganizationRecipe.research(N,placements,0);recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    a=Adapter(d.OrganizationalWorld.create(recipe));memory_guard();sel.declare(a.world,E,N,'B07.selector')
    life='FI01_B07_NEW_N'+str(N)+'_TOUCH_'+history
    a.world.runtime.set_snapshot_metadata('MUFI01.B07',encode({'life_id':life,'new_T0':True,'N':N,
      'architecture':REVISION,'history_scope':'Own native contact acquisition; no imported snapshot or old6 memory.'}))
    requests=[sel.experience(a.world,history,391,'B07.selector')]
    def snap(label):
        p=out/(life+'.'+label+'.T'+str(a.tick)+'.deetsnap.gz');a.save(p)
        return {'path':str(p),'sha256':sha(p),'tick':a.tick}
    snapshots=[snap('initial')];frames=[]
    pts={'E':E,'D':g['datum_site'],'C':g['remote_aggregate_site'],'A':[14,14,15],'B':[16,14,15]}
    pts.update({n['id']:n['site']for n in g['nodes']})
    for t in(0,387,388,390,391,392,393):
        a.run_until(t);memory_guard();frames.append({'tick':a.tick,'fields':{k:body.obs(a,p)for k,p in pts.items()}})
    snapshots.append(snap('own_acquired'))
    episodes=[]
    for index,leaf in enumerate(LEAVES):
        raw=[0]*128 if index%2==0 else[2]+[0]*127
        root=leaf-g['raw_relative_tick'];datum=root+38;q=datum-3;ids=[]
        for s in g['raw_sources']:ids.append(body.send(a,'B07.raw.'+s['id'],s['site'],s['direction'],root+s['injection_tick_relative'],raw[s['component_index']]))
        for s in g['generic_sources']:ids.append(body.send(a,'B07.raw.'+s['id'],s['site'],s['direction'],root+s['injection_tick_relative'],0))
        ids+=sel.query(a.world,q,5,'B07.selector');requests+=ids
        schedule={leaf-1,leaf,leaf+1,datum-2,datum-1,datum,datum+1,q+6,q+8}
        schedule.update(root+n['join_tick_relative']+dt for n in g['nodes']for dt in(-1,0,1))
        schedule.update(root+s['injection_tick_relative']+dt for s in g['generic_sources']for dt in(0,1,2))
        answer=None
        for t in sorted(schedule):
            a.run_until(t);memory_guard();frames.append({'tick':a.tick,'fields':{k:body.obs(a,p)for k,p in pts.items()}})
            if t==q+6:answer=reader(a,ni)
        # All opportunities predeclared; no retries or branches chosen by output.
        episodes.append({'index':index,'leaf_tick':leaf,'datum_tick':datum,'query_tick':q,
          'raw_components':raw,'reader':answer,'requests':ids})
    final_tick=LEAVES[-1]-g['raw_relative_tick']+38+5+202
    a.run_until(final_tick);memory_guard();snapshots.append(snap('after_common_horizon'))
    result={'revision':REVISION,'life':life,'new_T0':True,'N':N,'history_for_auditor_only':history,
      'preparation':sel.geometry(E,N),'extra_P0_stops':stops,'geometry':g,'frames':frames,'episodes':episodes,
      'requests':[{**r,'receipt':sel.exact_receipt(a.world.runtime.receipt(r['id']))}for r in requests],
      'snapshots':snapshots,'final':physical(a.world,occupation=True),'peak_process_bytes':memory_guard(),
      'scope':'Fresh auxiliary scale contrast, NOT MAIN continuation or inherited old6retention. Same final age>=2*N after last read. Global391 phase fixed; different N may change periodic context.'}
    dump(out/(life+'.json.gz'),result)
    summary={'life':life,'N':N,'history':history,'choices':[x['reader']['choice']for x in episodes],
      'requested':len(result['requests']),'applied':sum(x['receipt']['status']=='applied'for x in result['requests']),
      'refs392':next(z['fields']for z in frames if z['tick']==392),'final_tick':a.tick,'final':result['final'],
      'snapshot':snapshots[-1]}
    print(__import__('json').dumps(summary),flush=True);del a;gc.collect();memory_guard();return summary

def main():
    authorization=internal_A_close(LAB/'CIERRE_INTERNO_A.json');os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    ni=native_imports();out=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento/B07_FRESH_N67_N101_R1'
    dump(out/'PROTOCOLO.json',{'revision':REVISION,'authorization':authorization,'fixed_before_first_tick':ni[5](),
      'script_sha256':sha(__file__),'dimensions':[67,101],'histories':['A','B'],'raw_frame_leaf_ticks':LEAVES,
      'raw_vectors':['all128zero','first2_rest0','all128zero','first2_rest0'],'same_fixed_query_payload':5,
      'teaching':'Own contact0arrivesA-Z/B-Z at391, submitted388; never reference field write.',
      'reader':'Six fixed spatial classes at datum+3. No target/history/metadata read.',
      'scope':'New T0 comparison, no old6, no migration. Sequential one-Runtime execution; RSSguard512MiB.'})
    rows=[]
    for N in(67,101):
        for history in('A','B'):rows.append(execute(N,history,ni,out))
    dump(out/'RESUMEN.json',{'rows':rows,'finished_utc':ni[5](),'scope':'Four distinct new lives, not fourexperiences of MAIN.'})
if __name__=='__main__':main()
