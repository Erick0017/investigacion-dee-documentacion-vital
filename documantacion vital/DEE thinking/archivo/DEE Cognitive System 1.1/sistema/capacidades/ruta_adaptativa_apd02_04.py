"""Translated R04 candidate with complete input-port/own-recipe preflight; common quality never receives action/sign.

New geometry is installed only on exact RAW0 in the same complete N67 world.
Native action(a,+Y) circulates on Z−2. A common FAILURE can lift the actual
trace toward its corresponding reference; fixed generic cleanup consumes it.
This is a candidate until the archived controls establish physical behavior.
"""
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,decode_metadata
from capacidades import selector_acrecion_nativo as sel

VERSION='APD02.delayed_action_trace.R04'
KEY='DEE.Cognitive.System.1.1.APD02.delayed_action_trace.R04'
N=67;O=(25,13,53);P='APD02.trace.R04';DELAY=1410
def at(v):return sel.at(O,v,N)
def obs(a,p):return exact_observation(a.world.runtime.observe(d.Coordinate(*p)))
def refs(a):return[obs(a,at(v))for v in((-1,-1,0),(1,-1,0))]
def get(a):
    e=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in e:raise ValueError('Explicit RAW0 candidate preparation required')
    return decode_metadata(e[KEY])
def save(a,m):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
def declare(a,name,pos,direction,state=1,semantic=1):
    c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*pos);c.direction=d.Direction(*direction);c.state=state;c.semantic=semantic;c.allow_experience=True;c.allow_probe=False
    i=d.InterfaceSpec();i.name=name;i.channel=c;a.world.declare_interface(i)
def submit(a,name,payload,tick):
    r=a.world.submit(name,payload,tick);return{'id':int(r.id),'port':name,'payload':payload,'tick':tick}
def receipts(a,rs):return[{**r,'receipt':exact_receipt(a.world.runtime.receipt(r['id']))}for r in rs]
def geometry():
    rows={tuple(r['site']):r for r in sel.geometry(O,N)if tuple(r['site'])not in(at((-3,3,0)),at((3,3,0)))}
    stops=[(-1,-2,-1)]
    for x in(-1,0,1):
        stops += [(5*x,5,0),(4*x,4,-3),(6*x,6,0),(11*x,11,-1),(10*x,10,0),(10*x,10,10)]
    for v in stops:
        pos=at(v);rows[pos]={'site':pos,'state':0,'s_reg':0,'semantic':4,'direction':(0,0,0),'raw':int(d.pack_record(0,0,0,0,0,4))}
    return[rows[k]for k in sorted(rows)]
def port_specs():
    rows=[{'name':name,'site':pos,'direction':v}for name,(pos,v)in sel.ports(O,N,P).items()]
    for x in(-1,0,1):
        label=str(x)
        for kind,pos,v in(('divert',at((4*x,4,1)),(0,0,-1)),('flatten',at((6*x,6,-3)),(0,0,1)),('clear',at((10*x,10,-3)),(0,0,1))):
            rows.append({'name':P+'.'+kind+'.'+label,'site':pos,'direction':v})
        target=(2*x,-2,-2);v=(0,0,1)if x else(-1,0,1);source=tuple(target[i]-v[i]for i in range(3))
        rows.append({'name':P+'.failure.'+label,'site':at(source),'direction':v})
        rows.append({'name':P+'.sham.'+label,'site':at((source[0],source[1],source[2]+8)),'direction':v})
    return rows
def preflight(a):
    if int(a.world.runtime.dimension)!=N:raise ValueError('No resize of a lived world')
    rows=geometry();own={tuple(r['site']):r for r in rows}
    loop={at((x*k,k,-2))for x in(-1,0,1)for k in range(67)}
    geompre=[obs(a,r['site'])for r in rows];looppre=[obs(a,p)for p in sorted(loop)]
    ports=[dict(r,observation=obs(a,r['site']))for r in port_specs()]
    own_conflicts=[{'port':r['name'],'site':r['site'],'prepared_raw':str(own[tuple(r['site'])]['raw'])}for r in ports if tuple(r['site'])in own and own[tuple(r['site'])]['raw']!=0]
    bad_geometry=[r for r in geompre if int(r['raw'])]
    bad_loop=[r for r in looppre if int(r['raw'])]
    bad_ports=[r for r in ports if int(r['observation']['raw'])]
    return{'origin':list(O),'geometry':rows,'pre_geometry':geompre,'pre_loop':looppre,'pre_ALL_injection_ports':ports,
            'self_recipe_port_conflicts':own_conflicts,'nonzero_geometry':bad_geometry,'nonzero_loop':bad_loop,'nonzero_ports':bad_ports,
            'admissible':not(own_conflicts or bad_geometry or bad_loop or bad_ports),
            'scope':'Exact current RAW0 preparation/loop/ALL real-sham-query-teacher-resource injection sources and own-recipe compatibility. Not a future causal-isolation or retention proof.'}
def prepare(a):
    if int(a.world.runtime.dimension)!=N or KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('New N67 candidate preparation only, no reset')
    screen=preflight(a)
    if not screen['admissible']:raise ValueError('R04preflight rejects existing RAW or own-geometry/port conflict; preserve state, never clean/relocate')
    rows=screen['geometry'];rs=[];tick=a.tick+2
    for n,r in enumerate(rows):
        name=P+'.prepare.'+str(n);declare(a,name,r['site'],(0,0,0),r['state'],r['semantic']);rs.append(submit(a,name,0,tick))
    a.run_until(tick+1);sel.declare(a.world,O,N,P)
    for x in(-1,0,1):
        label=str(x)
        declare(a,P+'.divert.'+label,at((4*x,4,1)),(0,0,-1))
        declare(a,P+'.flatten.'+label,at((6*x,6,-3)),(0,0,1))
        declare(a,P+'.clear.'+label,at((10*x,10,-3)),(0,0,1))
        target=(2*x,-2,-2);direction=(0,0,1)if x else(-1,0,1)
        source=tuple(target[i]-direction[i]for i in range(3))
        declare(a,P+'.failure.'+label,at(source),direction)
        declare(a,P+'.sham.'+label,at((source[0],source[1],source[2]+8)),direction)
    save(a,{'version':VERSION,'prepared_tick':a.tick,'pending_window':None,'uses':0,'consequences':0,
            'scope':'P0 trace/quality routing, no host A/B assignment or stored choice. Neutral0 has the predeclared external/help domain and follows the A-inhibition path.'})
    return{'preflight':screen,'geometry':rows,'pre':screen['pre_geometry'],'loop_pre':screen['pre_loop'],'pre_ALL_injection_ports':screen['pre_ALL_injection_ports'],'requests':receipts(a,rs),'references':refs(a)}

def seed(a,side):
    get(a);k=(a.tick+5)//391+1;k=k if k%2 else k+1;arrival=k*391
    before=refs(a);r=sel.experience(a.world,side,arrival,P);a.run_until(arrival+2)
    return{'side_explicit_teacher':side,'arrival':arrival,'before':before,'after':refs(a),'request':sel.receipt(a.world,r),'not_outcome_learning':True}
def read(a):return sel.read(a.world,O,N)
def use(a,*,query=True):
    m=get(a)
    if m['pending_window']is not None:raise ValueError('Existing native trace must complete first; no overwrite')
    k=(a.tick+DELAY+5+390)//391;k=k if k%2 else k+1;boundary=k*391;q=boundary-DELAY
    rs=sel.query(a.world,q,5,P)if query else[]
    for x in(-1,0,1):
        label=str(x)
        rs += [submit(a,P+'.divert.'+label,0,q+7),submit(a,P+'.flatten.'+label,0,q+9),submit(a,P+'.clear.'+label,0,boundary+10)]
    before=refs(a);a.run_until(q+6);reader=read(a)
    m['pending_window']={'query_tick':q,'boundary':boundary,'deadline':boundary-3,'generic_resource_requests':rs}
    m['uses']+=1;save(a,m)
    return{'kind':'native_trace_use','query_present':query,'query_tick':q,'boundary':boundary,'reader':reader,'references':before,
            'requests':receipts(a,rs),'trace_not_reinjected_from_reader':True}
def trace_observations(a,q):
    k=(a.tick-q-4)%67
    return{'tick':a.tick,'offset':a.tick-q,'expected_diagonal_phase_only':k,
            'all_three_potential_trace_sites':[obs(a,at((x*k,k,-2)))for x in(-1,0,1)],'references':refs(a)}
def consequence(a,category,*,mode='real'):
    m=get(a);window=m['pending_window']
    if window is None:raise ValueError('No actual pending native action trace')
    if category not in('SUCCESS','FAILURE')or mode not in('real','omit','sham','desync'):raise ValueError('Fixed category/modality, never action or recommendation')
    boundary=window['boundary']
    if a.tick>window['deadline']:raise ValueError('Outcome arrived beyond declared trace contract; preserve state, no re-injection or silent reschedule')
    before=refs(a);rs=[]
    if category=='FAILURE'and mode!='omit':
        for x in(-1,0,1):rs.append(submit(a,P+('.sham.'if mode=='sham'else'.failure.')+str(x),0,boundary-2+(1 if mode=='desync' else 0)))
    frames=[]
    for tick in range(boundary-3,boundary+16):
        a.run_until(tick);frames.append(trace_observations(a,window['query_tick']))
    m['pending_window']=None;m['consequences']+=1;save(a,m)
    return{'kind':'generic_quality_native_trace_consequence','category':category,'mode':mode,
            'boundary':boundary,'before':before,'after':refs(a),'requests':receipts(a,rs),
            'all_generic_resources':receipts(a,window['generic_resource_requests']),
            'frames':frames,'no_action_or_correct_route_argument':True}
