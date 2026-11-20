"""PI10 prepared first-query TC and fixed delayed physical feedback.

Pure Python on import. No engine, world, owner or life is created. Mutators
require the caller's explicit existing clone owner and official PI03 helper.
No RAW/clock setter, diagnostic edit, target action or learned-bank copy.
The P0 anatomy and return wiring are engineering, not acquired content.
"""
from __future__ import annotations
import argparse, hashlib, json

N=67
PERIOD=782
Q1_LAPS=18
Q2_LAPS=6
OLD_ORIGIN=(8,40,50)
OLD_PREFIX='PI07.TC.R01'
SYSTEM_KEY='DEE.Cognitive.System.1.1.life.v1'
PROTECTED_IDS={
 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01',
 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01',
 'ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'}
CUT_OFFSETS=((-4,-1,-2),(4,-1,-2))
SHAM_OFFSETS=((-4,2,-2),(4,2,-2))

def need(ok,message):
    if not ok:raise ValueError(message)

def at(origin,delta):return tuple((int(origin[i])+int(delta[i]))%N for i in range(3))

def fixed_schedule(now,clock,delay_laps):
    need(type(now)is int and type(clock)is int and delay_laps in(6,18),'Exact current clock/tick and frozen laps6/18')
    delay=delay_laps*N
    earliest=now+7+delay+3
    residue=(391-(clock-now))%PERIOD
    contact=earliest+(residue-earliest)%PERIOD
    collision=contact-1;seed=collision-delay
    return {'query_tick':seed-7,'query_read_tick':seed-1,'seed_tick':seed,
      'outcome_injection_tick':collision-1,'collision_tick':collision,
      'contact_tick':contact,'settled_after_tick':contact+2,
      'delay_ticks':delay,'delay_laps':delay_laps}

def two_selector_calendar(now,q1_reference_clock,q2_reference_clock):
    """Fixed planning from present clocks, never clock edits or a solution.

    q2 is planned from q1+16, after the material query at q1+7/releaseq1+8.
    Its nonfailure disposal is complete before q1's final feedback injection.
    Equal phases yield q2-q1=22; other phases are retained and reported.
    """
    first=fixed_schedule(now+16,q1_reference_clock+16,Q1_LAPS)
    next_now=first['query_tick']+16
    second=fixed_schedule(next_now,q2_reference_clock+(next_now-now),Q2_LAPS)
    need(second['query_tick']>first['query_tick']+8,'No q2 before access/release')
    need(second['settled_after_tick']<first['outcome_injection_tick'],'Fixed geometry has no return margin; no adaptive clock repair')
    need(first['settled_after_tick']-now<=2016,'Fixed whole-op planning bound2016 exceeded')
    return {'first':first,'second':second,
      'q2_minus_q1':second['query_tick']-first['query_tick'],
      'fixed_whole_tick_bound':2016,'phase67_q1':first['query_tick']%67,
      'phase391_q1':first['query_tick']%391,'phase782_q1':first['query_tick']%782,
      'phase67_q2':second['query_tick']%67,'phase391_q2':second['query_tick']%391,
      'phase782_q2':second['query_tick']%782,
      'query1_return_is_after_the_actual_q2_action':True,
      'second_return':'fixed nonfailure disposal, independent of actual task success',
      'first_return':'same generic actual-failure law and same fixed q1 hub; Native efference chooses bank'}

def prepared_frame(tc_helper,origin):
    rows={tuple(r['site']):dict(r) for r in tc_helper.frame_rows(origin,N)}
    # PI03 symmetrical0/0 references are preparation, not a learned copy.
    for side in(-1,1):need(rows[at(origin,(side,-1,0))]['payload']==0,'Only unlearned P0 zero references')
    # Same local output stops as PI07, omitting inherited environmental sinks.
    for x in(-1,0,1):
        for z in(0,-1):
            site=at(origin,(3*x,3,3*z))
            row={'site':site,'state':0,'payload':0,'semantic':4,'direction':(0,0,0)}
            if site in rows:need(all(rows[site][k]==row[k] for k in('state','payload','semantic','direction')),'Inconsistent prepared TC stop')
            rows[site]=row
    return [rows[k]for k in sorted(rows)]

def ports(tc_helper,origin,prefix):
    rows=[dict(r)for r in tc_helper.port_rows(origin,prefix,N)]
    rows.append({'name':prefix+'.datum','site':at(origin,(-1,0,1)),
       'direction':(0,0,0),'state':1,'semantic':1})
    for kind,offsets in(('cut',CUT_OFFSETS),('sham',SHAM_OFFSETS)):
        for index,delta in enumerate(offsets):
            rows.append({'name':prefix+'.'+kind+'.'+str(index),'site':at(origin,delta),
               'direction':(0,0,0),'state':0,'semantic':4})
    return rows

def footprint(tc_helper,origin):
    points=set(tc_helper.geometry_footprint(origin,N,halo=1))
    extra={tuple(r['site'])for r in prepared_frame(tc_helper,origin)}
    extra.update(at(origin,d)for d in(*CUT_OFFSETS,*SHAM_OFFSETS))
    for site in extra:
        points.update(at(site,(x,y,z))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1))
    return sorted(points)

def passive_preflight(tc_helper,origin,lookup):
    observations=[{'site':list(p),**lookup(p)}for p in footprint(tc_helper,origin)]
    conflicts=[r for r in observations if int(r['raw'])!=0]
    refs=[lookup(at(origin,d))for d in((-1,-1,0),(1,-1,0))]
    serial=json.dumps(observations,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf8')
    return {'origin':list(origin),'N':N,'checked_sites':len(observations),
      'conflicts':conflicts,'reference_clocks':[int(r['clock'])for r in refs],
      'observations_sha256':hashlib.sha256(serial).hexdigest(),
      'eligible':not conflicts and int(refs[0]['clock'])%PERIOD==int(refs[1]['clock'])%PERIOD,
      'scope':'Current full RAW plus clocks and local halo; no guarantee of future isolation.'}

def _clone_identity(owner,expected_life):
    identity=json.loads(dict(owner.world.runtime.snapshot_metadata_entries)[SYSTEM_KEY])
    need(identity['life_id']==expected_life and identity['profile']=='fisica_directa' and expected_life not in PROTECTED_IDS,'Explicit current diagnostic descendant only; original principal protected')
    need(int(owner.world.runtime.dimension)==N,'Continue existing N67; never enlarge/recreate')
    return identity

def install_first_tc(owner,tc_helper,origin,prefix,expected_life):
    """NATIVE MUTATION only on Root-supplied loaded clone; future birth APIs.

    No retry after partial admission, no component move/cleanup, clocks kept.
    Caller must preserve/save any adverse reached state and a finite lot.
    """
    _clone_identity(owner,expected_life)
    _,exact,receipt=tc_helper._native()
    native=tc_helper._native()[0]
    def observe(site):return exact(owner.world.runtime.observe(native.Coordinate(*site)))
    check=passive_preflight(tc_helper,origin,observe)
    need(check['eligible'],'Refuse occupied whole-RAW/phase footprint, no clearing or relocation')
    frame=prepared_frame(tc_helper,origin);new_ports=ports(tc_helper,origin,prefix)
    names={prefix+'.prepare.'+str(i)for i in range(len(frame))}|{r['name']for r in new_ports}
    need(not names.intersection(set(owner.world.runtime.channel_names)),'Fresh fixed namespace only; no reinstallation')
    start=int(owner.tick);arrival=start+2;requests=[]
    for index,row in enumerate(frame):
        name=prefix+'.prepare.'+str(index)
        tc_helper._channel(owner.world,name,row['site'],row['direction'],row['state'],row['semantic'])
        r=owner.world.submit(name,row['payload'],arrival)
        requests.append({'id':int(r.id),'channel':name,'requested_tick':arrival,'payload':row['payload'],'site':list(row['site'])})
    owner.run_until(arrival+1)
    for r in requests:r['receipt']=receipt(owner.world.runtime.receipt(r['id']))
    ready=all(r['receipt']['status']=='applied'for r in requests)
    if ready:
        for r in new_ports:tc_helper._channel(owner.world,r['name'],r['site'],r['direction'],r['state'],r['semantic'])
    return {'version':'PI10.first_query_TC.legal_additive_P0.R01','ready':ready,'preflight':check,
      'requests':requests,'before_tick':start,'after_tick':int(owner.tick),'new_ticks':int(owner.tick)-start,
      'initial_reference_payloads':{'A':0,'B':0},'physical_bank_copy':False,'clock_edits':False,
      'prepared_unlearned_support_not_learning':True,'no_automatic_retry':True}

def read_central(owner,native,exact,origin,query_tick):
    need(int(owner.tick)==query_tick+4,'Frozen centralq+4 reader only')
    observation=exact(owner.world.runtime.observe(native.Coordinate(*origin)))
    direction=list(observation['direction'])
    valid=int(observation['state'])>0 and int(observation['semantic'])==1 and len(direction)==3 and direction[0]in(-1,0,1)and direction[1]==1 and direction[2]in(-1,0)
    return {'tick':int(owner.tick),'site':list(origin),'observation':observation,
      'choice':direction[0]if valid else None,'zero_is_not_NULL':True,
      'fixed_signature':'activeSEM1 direction[dx,+1,z], dx-1/0/+1,z-1/0'}

def actual_motor(choice):
    return (-1 if choice==0 else choice)if type(choice)is int and choice in(-1,0,1)else None

def barrier_requests(world,prefix,seed_tick,kind):
    """Two fixed legal future births after query/efference formation.

    No action/history/outcome argument; same doses and times cut/sham.
    This control is external P0 intervention, never acquired protection.
    """
    need(kind in('cut','sham'),'Only prospectively declared postformed cut/sham')
    result=[]
    for index in range(2):
        name=prefix+'.'+kind+'.'+str(index);r=world.submit(name,0,seed_tick+2)
        result.append({'id':int(r.id),'channel':name,'payload':0,'requested_tick':seed_tick+2,
          'control_kind':kind,'not_selected_by_actual_choice':True})
    return result

def bank_observations(owner,native,exact,origin):
    values=[exact(owner.world.runtime.observe(native.Coordinate(*at(origin,d))))for d in((-1,-1,0),(1,-1,0))]
    return {'tick':int(owner.tick),'A':values[0],'B':values[1],
      'A_minus_B':int(values[0]['s_reg'])-int(values[1]['s_reg']),
      'reference_clocks':[int(x['clock'])for x in values]}

def trace_stencil(owner,native,exact,origin):
    offsets=[(x,-1,-2)for x in range(-5,6)]+[(0,-1,-3),(0,0,-2)]
    return {'tick':int(owner.tick),'observations':[{'site':list(at(origin,d)),**exact(owner.world.runtime.observe(native.Coordinate(*at(origin,d))))}for d in offsets],
      'scope':'Passive fixed stencil, not unique physical lineage identifiers'}

def self_check():
    checked=0
    for now in(0,922371,1000003):
        for offset1 in(0,13,781):
            for offset2 in(0,17,779):
                value=two_selector_calendar(now,now+offset1,now+offset2)
                for key,clock in(('first',now+offset1),('second',now+offset2)):
                    c=value[key]
                    need((clock+c['contact_tick']-now)%PERIOD==391,'Scheduled gate mismatch')
                    need(c['collision_tick']-c['seed_tick']==c['delay_laps']*N,'Toroidal delay mismatch')
                checked+=1
    need(actual_motor(0)==-1 and actual_motor(None)is None,'Zero/NULL codec differs')
    return {'static_only':True,'Native_imported':False,'Native_executed':False,
      'calendars_checked':checked,'not_yet_verified':['late legal installation','q1phase741 readout','18lap eligibility survival','q2bank delta stability','functional acquisition','physical cut/sham causal selectivity']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--self-check',action='store_true',required=True);p.parse_args()
    print(json.dumps(self_check(),ensure_ascii=False,indent=2))
