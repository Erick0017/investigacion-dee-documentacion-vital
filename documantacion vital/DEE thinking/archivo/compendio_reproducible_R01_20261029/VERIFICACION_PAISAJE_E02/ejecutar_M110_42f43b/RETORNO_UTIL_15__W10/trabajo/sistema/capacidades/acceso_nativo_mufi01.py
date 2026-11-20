"""Operational auxiliary: one destructive P1 choice over a P0 basal query.

Requires an already acquired, already prepared complete world. No world
creation, historical-file import, target lookup, context choice or answer table.
Compatibility hashes are admission guards only; output always comes from all12
physical mixed-direction gates. The validated domain is finite, not general.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from dee_thinking.consolidated import exact_receipt
from app.native_tools import physical
from capacidades import selector_acrecion_nativo as sel
from capacidades import mente_acumulativa_r02 as ma
from capacidades import arquitectura_distribuida_mi02_r8 as body
KEY='DEE.Cognitive.System.1.1.NATIVE_ACCESS_ONE_USE.v1'
VERSION='MUFI01.native_access.basal_selection.R1'
Q=31046;READ=31092;END=31095
RAW_COMPATIBILITY={
 '3c76d97dfc47f6dd40b9e2a937943fb3dbde07da6a78fbe1d6de1400aaa57f0a',
 'da3d409d880d1e0fbf7ea71f063b410654a8556e9239ff01022277ab66ae4695',
 'e29f04805f97cac7123ad0e8bdadf97b37559aa74d4f1570cd73e732478b93fc'}
CLOCK_COMPATIBILITY='53f090cf737714f9b91f2e982cf0ca408552a7b3d986119faea5a2d13ab1cde5'
JOINS=[('plus.first',(17,17,15),(0,-1,1),6),('minus.first',(13,17,15),(1,0,1),6),
 ('plus.turn1',(33,17,31),(-1,1,0),22),('minus.turn1',(13,33,31),(1,-1,0),22),
 ('plus.excursion',(33,19,33),(0,-1,0),24),('minus.turn2',(15,33,33),(0,0,-1),24),
 ('plus.reverseA',(33,19,35),(1,0,-1),26),('plus.reverseB',(33,19,35),(-1,0,-1),26),
 ('plus.return',(33,19,33),(0,1,1),28)]
STOPS=sorted({tuple((p[i]+v[i])%67 for i in range(3))for _,p,v,_ in JOINS})

def compatible(a):
    p=physical(a.world)
    if p['N']!=67 or p['tick']!=30957 or p['RAW_sha256']not in RAW_COMPATIBILITY or p['clocks_sha256']!=CLOCK_COMPATIBILITY:
        raise ValueError('Outside the exact validated pre-use physical domain; no rebuild, rewind or answer substitution')
    ma.get(a)
    inert=int(d.pack_record(0,0,0,0,0,4))
    if any(int(body.obs(a,p)['raw'])!=inert for p in STOPS):raise ValueError('Prepared P0 boundary absent or changed')
    return p

def admit(a):
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('Already admitted; do not reset its one-use flag')
    p=compatible(a);m={'version':VERSION,'used':False,'admitted_tick':a.tick,'use_domain':'Exact30957preparedprefix, one execution atq31046, fixed12-gate reader31092; destructive costs declared.',
      'assistance':'Operator initiates. Generic zero routes create a basal query even without actor; acquired selector can alter which content it reaches. Not native initiative or learned general strategy.'}
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m));return {'physical':p,'operational':m}

def get(a):
    e=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in e:raise ValueError('Not admitted as the bounded auxiliary; no silent preparation')
    return decode_metadata(e[KEY])

def state(a):
    return {'version':VERSION,'physical':physical(a.world,occupation=True),'operational':get(a),
      'knowledge_scope':'Whole acquired world belongs to this actual fork. No knowledge from another individual is installed here.',
      'limits':'One destructive use; P0 basal query and externally scheduled supplies. P1 history-dependent bank selection, not learned strategy or self-initiated access.'}

def read(a):
    panel=[];cs=[]
    for token,v in ma.codec(a).items():
        for z in(-1,1):
            o=body.obs(a,ma.pos(v,4,z));panel.append({'gate_class':token,'observation':o})
            if o['state']>0 and o['semantic']==1 and o['direction']==[v[0],v[1],z]:cs.append({'sign':z,'gate_class':token,'observation':o})
    return {'tick':a.tick,'panel':panel,'candidates':cs,'formed_native_command':cs[0]['sign']if len(cs)==1 else None,
      'scope':'All12 fixed mixed-direction gates; no selected context or expected response is an argument.'}

def use(a,*,detail=False):
    m=get(a)
    if m['used']:raise ValueError('One-use auxiliary already consumed; preserve this future, fork an explicitly identified pre-use state if needed')
    compatible(a);m['used']=True;a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
    rs=[]
    for name,p,v,t in JOINS:
        source=tuple((p[i]-2*v[i])%67 for i in range(3));rs.append(body.send(a,'FI01.NR.'+name,source,v,Q+t-2,0))
    rs.extend(sel.query(a.world,Q,5,'MU.selector'))
    frames=[];answer=None
    points={sel.at((15,15,15),(x,y,z))for x in range(-3,4)for y in range(-3,5)for z in range(-4,4)}
    for _,p,v,_ in JOINS:points.update(tuple((p[i]+k*v[i])%67 for i in range(3))for k in(-2,-1,0,1))
    for v in ma.codec(a).values():
        for z in range(-3,4):
            for k in(3,4):points.add(ma.pos(v,k,z))
    schedule=sorted(set(list(range(Q-1,Q+9))+[Q+k for k in(20,21,22,23,24,25,26,27,28,29,40,41,42,43,44,45,46,47,49)]))
    for t in schedule:
        a.run_until(t)
        if detail:frames.append({'tick':a.tick,'sites':[body.obs(a,p)for p in sorted(points)]})
        if t==READ:answer=read(a)
    return {'version':VERSION,'common_query_tick':Q,'read_tick':READ,'end_tick':a.tick,'reader':answer,'frames':frames,
      'requests':[dict(r,receipt=exact_receipt(a.world.runtime.receipt(r['id'])))for r in rs],'state':state(a),
      'scope':'Prepared basal access plus physically acquired selector/content, one destructive use. Bank is not selected by Python. No self-initiation or general P2/R2 assertion.'}
