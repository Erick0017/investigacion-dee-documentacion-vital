"""One-use native selector-to-memory routing candidate, prepared P0.

No chosen-context callback. Both generic zero-resource routes are queued in
advance. All12 mixed-direction memory gates share one frozen decoder.
"""
import argparse,gc,gzip,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema'
sys.path.insert(0,str(LAB/'transferencia_b'))
import frontend_b01_r2 as f
OUT=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/acceso_nativo_b/R2'
SOURCES={'T':'1cba48105891aa47a0976aa8fadd6f794265b57598b84d767d14c4744bfbc6f7','H':'e71c03d4f5f7b56dc3af43c7d5fdb226e9df19443fb019c0a89d2c004c7f9282'}
JOINS=[('plus.first',(17,17,15),(0,0,1),6),('minus.first',(13,17,15),(0,0,1),6),
 ('plus.turn1',(35,35,33),(0,0,-1),24),('minus.turn1',(62,35,33),(0,0,-1),24),
 ('minus.last',(33,64,33),(1,0,0),53)]
VECTORS=[(1,0,0),(0,1,0),(1,1,0),(-1,1,0),(1,-1,0),(-1,-1,0)]
STOPS=sorted({tuple((p[i]+v[i])%67 for i in range(3))for _,p,v,_ in JOINS}|{((33+5*v[0])%67,(33+5*v[1])%67,(33+2*z)%67)for v in VECTORS for z in(-1,1)})
E=(15,15,15);I=(33,33,33);CUE_TICK=31155;Q=CUE_TICK-89
CASES=[('T','T',False,True,True),('H','H',False,True,True),('H_gamma_minus','H',True,True,True),('no_query','T',False,False,True),('cut_first_turn','T',False,True,False)]

def prepare(a,ni):
    from dee_thinking import _native as d
    from capacidades import selector_acrecion_nativo as sel
    body=ni[7];inert=int(d.pack_record(0,0,0,0,0,4));before=[body.obs(a,p)for p in STOPS];rs=[];t=a.tick+2
    for j,o in enumerate(before):
        if int(o['raw'])==inert:continue
        if int(o['raw'])!=0:raise ValueError('Native route boundary occupied; no cleanup:'+repr(o))
        name='FI01.NR.stop.'+str(j);c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*STOPS[j]);c.direction=d.Direction(0,0,0);c.state=0;c.semantic=4;c.allow_experience=True;c.allow_probe=False
        it=d.InterfaceSpec();it.name=name;it.channel=c;a.world.declare_interface(it);r=a.world.submit(name,0,t);rs.append({'id':int(r.id),'port':name,'payload':0,'tick':t,'site':list(STOPS[j])})
    a.run_until(t+1);return {'before':before,'after':[body.obs(a,p)for p in STOPS],'requests':[sel.receipt(a.world,r)for r in rs]}

def reader(a,ni):
    from capacidades import mente_acumulativa_r02 as ma
    panel=[];cs=[]
    for token,v in ma.codec(a).items():
        for z in(-1,1):
            o=ni[7].obs(a,ma.pos(v,4,z));panel.append({'gate_class':token,'observation':o})
            if o['state']>0 and o['semantic']==1 and o['direction']==[v[0],v[1],z]:cs.append({'sign':z,'gate_class':token,'observation':o})
    return {'tick':a.tick,'panel':panel,'candidates':cs,'formed_native_command':cs[0]['sign']if len(cs)==1 else None,
      'scope':'All12 fixed gate/direction classes. Gate label records location only; it never selects a bank or decoder branch from the expected cue.'}

def execute(a,ni,has_query,first_turns):
    from capacidades import selector_acrecion_nativo as sel
    from capacidades import mente_acumulativa_r02 as ma
    rs=[];start=a.tick
    if start>Q-3:raise ValueError('Frozen common route phase already passed; no rescheduling')
    for name,p,v,t in JOINS:
        if not first_turns and name.endswith('.first'):continue
        source=tuple((p[i]-2*v[i])%67 for i in range(3));rs.append(ni[7].send(a,'FI01.NR.'+name,source,v,Q+t-2,0))
    if has_query:rs.extend(sel.query(a.world,Q,5,'MU.selector'))
    points={sel.at(E,(x,y,z))for x in range(-3,4)for y in range(-3,5)for z in range(-3,4)}
    points.update(STOPS);points.add(I)
    for _,p,v,_ in JOINS:
        points.update(tuple((p[i]+k*v[i])%67 for i in range(3))for k in(-2,-1,0,1))
    for v in ma.codec(a).values():
        for z in range(-3,4):
            for k in(3,4):points.add(ma.pos(v,k,z))
    # Planned routes are coverage coordinates, not asserted actual trajectories.
    for begin,v,n in[((17,17,15),(1,1,1),18),((13,17,15),(-1,1,1),18),((62,35,33),(-1,1,0),29),((33,64,33),(0,1,0),39)]:
        points.update(tuple((begin[i]+k*v[i])%67 for i in range(3))for k in range(n+1))
    schedule=sorted(set(list(range(Q-1,Q+9))+[Q+k for k in(20,21,22,23,24,25,26,27,28,51,52,53,54,55,87,88,89,90,91,92,93,94,95,96)]));frames=[];windows=[]
    for t in schedule:
        f.memory_guard();a.run_until(t);frames.append({'tick':a.tick,'sites':[ni[7].obs(a,p)for p in sorted(points)]})
        if t in(Q+26,Q+93):windows.append(reader(a,ni))
    candidates=[dict(c,window_tick=w['tick'])for w in windows for c in w['candidates']]
    answer={'tick':a.tick,'windows':windows,'candidates':candidates,'formed_native_command':candidates[0]['sign']if len(candidates)==1 else None,
      'rule':'Predeclared two windows, ALL12 gates in each; exactly one total candidate accepted. Two valid events are ambiguous, never select favorable.'}
    return {'query_present':has_query,'first_turn_resources_present':first_turns,'common_query_tick':Q,'fixed_cue_phase_tick':CUE_TICK,
      'start_tick':start,'end_tick':a.tick,'reader':answer,'requests':[sel.receipt(a.world,r)for r in rs],'frames':frames,
      'physical':ni[6](a.world,occupation=True),'scope':'One-use prepared native route. No Python selection of context, stage, learned content or favorable reader. Selected circulating memory may be consumed.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--execute',action='store_true');args=ap.parse_args()
    if not args.execute:
        print(json.dumps({'planned_query_tick':Q,'I_arrival_tick':CUE_TICK,'joins':JOINS,'stops':STOPS,'new_ticks':0}));return
    authorization,ni=f.bootstrap();store=ni[3]();code=f.digest(__file__)
    from capacidades import mente_acumulativa_r02 as ma
    f.dump(OUT/'PROTOCOLO.json',{'schema':'MUFI01.native_route.one_use.R2','frozen_before_first_tick':ni[5](),'code_sha256':code,'authorization':authorization,
      'source_post19_snapshot_shas':SOURCES,'query_tick':Q,'cue_tick':CUE_TICK,'generic_joins':JOINS,'stops':STOPS,'cases':CASES,
      'decoder':'ALL12 mixed v±Z gates at BOTH q+26 andq+93. ExactlyONE total candidate accepted; two valid events ambiguous. No expectedtoken/window argument.',
      'predictions_not_actor_inputs':'Tselector− shouldreachbeta atq+93; Hselector+ shouldreachgamma atq+26. Hnewgamma− shouldchangeonlycontent. Every guidance vectorY=0, soactorY intendedwitness. Noquery+sameresources mustnotformvalidread. First-turn omission blocksactor atoldabsorber.',
      'costs':'No restoration. Added all12 inactive mixed-output stops one step aftergate to prevent a second toroidal event, preparedBEFORE trials. Selected memory consumed, otherlosses measured. No MAIN mutation, field cleanup or T0 rebuild.'})
    summary=[]
    for name,source,teach,has_query,first_turns in CASES:
        life='FI01_NR_R2_'+name
        if store.life_dir(life).exists():raise FileExistsError(life)
        pp=f.OUT.parent/'B02'/(source+'_LESSONS_2.json.gz');ins=json.loads(gzip.decompress(pp.read_bytes()))['INSTRUMENTO']
        cp=[p for p in(SYSTEM/'estado/checkpoints').glob(ins['life_id']+'.T30891.*.deetsnap.gz')if f.digest(p)==SOURCES[source]]
        if len(cp)!=1:raise ValueError('Source complete original not uniquely found')
        store.fork(ins['life_id'],life,kind='NATIVE_ONE_USE_ACCESS_CANDIDATE',checkpoint=str(cp[0].relative_to(SYSTEM)));gc.collect();f.memory_guard()
        prep=store.mutate(life,'NR_P0_FIXED_ROUTES',lambda a:prepare(a,ni),{'code_sha256':code});f.dump(OUT/(name+'_PREP.json.gz'),prep);del prep
        def lesson(a):
            result=ma.teach(a,'gamma',-1,revision=True)if teach else None
            a.run_until(30957);return {'explicit_beta_revision':result,'current_references':[ni[7].obs(a,p)for p in[(14,14,15),(16,14,15)]],'end_tick':a.tick}
        lesson_result=store.mutate(life,'NR_CONTENT_EXPERIENCE_OR_AGE',lesson,{'code_sha256':code,'explicit_teaching':teach});f.dump(OUT/(name+'_LESSON.json.gz'),lesson_result);del lesson_result
        result=store.mutate(life,'NR_NATIVE_ACCESS_RESERVE',lambda a:execute(a,ni,has_query,first_turns),{'code_sha256':code});f.dump(OUT/(name+'_USE.json.gz'),result)
        row={'case':name,'life':life,'reader':result['result']['reader'],'tick':result['physical']['tick'],'snapshot_sha256':result['INSTRUMENTO']['snapshot_sha256']};summary.append(row);print(json.dumps(row),flush=True);del result;gc.collect();f.memory_guard()
        panel=store.mutate(life,'NR_POST_USE_OLD_MEMORY_PANEL',lambda a:{'rows':[ma.query(a,t,detail=False)for t in['alfa','beta','gamma','delta','epsilon','zeta']]},{'code_sha256':code});f.dump(OUT/(name+'_POST_PANEL.json.gz'),panel);del panel;gc.collect();f.memory_guard()
    f.dump(OUT/'RESUMEN.json',{'cases':summary,'scope':'Actual single-use candidate outcomes, not a promotion or a sum of separate-world skills.'})
if __name__=='__main__':main()
