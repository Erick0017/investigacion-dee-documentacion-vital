"""Integrated shared-world candidate: preserved MA02 memory and native P1 access.

Prepared R06 anatomy is installed with legal interfaces in vacant RAW sites.
No trained fields are transplanted. Selection reads physical actuator sites,
never the memory catalogue or expected worker. Outcome feedback is a fixed
failure contact, not an instruction telling DEE which action would be correct.
"""
from pathlib import Path
import hashlib,json,subprocess,sys,time
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from dee_thinking.consolidated import exact_observation,exact_receipt
from app.native_tools import physical
from capacidades import selector_acrecion_nativo as sel
from capacidades import mente_acumulativa_r02 as ma

KEY='DEE.Cognitive.System.1.1.MENTE_UNIFICADA_01.v1'
VERSION='MUFI01.shared_world_selector.R1'
ORIGIN=(15,15,15);N=67
def get(a):
    e=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in e:raise ValueError('This life has no physically admitted unified preparation; no silent T0 or substitute')
    if int(a.world.runtime.dimension)!=N:raise ValueError('Unified selector contract is N67 only')
    return decode_metadata(e[KEY])
def save(a,m):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
def observation(a,p):return exact_observation(a.world.runtime.observe(d.Coordinate(*p)))
def next_contact(t):
    # Fixed anatomical writing window inherited from R06/R08, not an auditor
    # searching future responses. Both data and failure use the same odd gate.
    k=(int(t)+5)//391+1
    return (k if k%2 else k+1)*391
def state(a):
    m=get(a)
    return {'version':VERSION,'physical':physical(a.world,occupation=True),'origin':list(ORIGIN),
      'references':[observation(a,sel.at(ORIGIN,p))for p in[(-1,-1,0),(1,-1,0)]],
      'operational':m,'assistance':{'P0':'Prepared supports, absorbers, three generic query routes and fixed file-worker conversion; operator chooses operation, not selected sign or bank.',
      'P1':'Only when demonstrated for this own life: experience-conditioned relative reference and repeated native choice.',
      'P2_R2':'Not certified by installation or metadata; causal consequence contrasts required.'},
      'memory_contract':ma.state(a),'no_answer_catalogue_read':True}
def prepare(a):
    ma.get(a)
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('Already admitted; never reinstall to repair a future')
    rows=sel.geometry(ORIGIN,N)
    before=[observation(a,r['site'])for r in rows]
    if any(int(o['raw'])!=0 for o in before):raise ValueError('Prepared region intersects nonzero RAW; inactive records are not free space')
    requests=[];at=a.tick+2
    for j,r in enumerate(rows):
        name='MU.geometry.r06.'+str(j)
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*r['site']);c.direction=d.Direction(0,0,0);c.state=r['state'];c.semantic=r['semantic'];c.allow_experience=True;c.allow_probe=False
        i=d.InterfaceSpec();i.name=name;i.channel=c;a.world.declare_interface(i)
        rr=a.world.submit(name,r['s_reg'],at);requests.append({'id':int(rr.id),'channel':name,'tick':at,'value':r['s_reg'],'site':r['site'],'state':r['state'],'semantic':r['semantic']})
    a.run_until(at+1)
    receipts=[dict(r,receipt=exact_receipt(a.world.runtime.receipt(r['id'])))for r in requests]
    if any(r['receipt']['status']!='applied'for r in receipts):raise ValueError('Anatomy admission incomplete; preserve reached state rather than retry/overwrite')
    sel.declare(a.world,ORIGIN,N,'MU.selector')
    m={'version':VERSION,'prepared_tick':a.tick,'anatomy':'R06 relative equal-baseline reference, not learned content','origin':list(ORIGIN),
      'episodes':0,'queries':0,'jobs':0,'explicit_teaching_events':0,'external_pending':None,
      'worker_assistance':'Native sign selects worker; only bounded public measurements enter external tool. Actual failure maps to same zero-contact A; no correct action in return.',
      'decoder':'Three fixed physical sites/direction classes at query+6; no history/target arguments'}
    save(a,m)
    return {'classification':'External P0 anatomical extension of this exact shared world. No knowledge copied or clock reset.',
      'pre':before,'prepared':rows,'post':[observation(a,r['site'])for r in rows],'requests':receipts,'state':state(a)}
def experience(a,side):
    m=get(a);arrival=next_contact(a.tick)
    pre=physical(a.world);r=sel.experience(a.world,side,arrival,'MU.selector');frames=[]
    a.run_until(arrival-1)
    for t in range(arrival-1,arrival+3):
        a.run_until(t);frames.append({'tick':a.tick,'references':[observation(a,sel.at(ORIGIN,p))for p in[(-1,-1,0),(1,-1,0)]],
          'contact':[observation(a,sel.at(ORIGIN,p))for p in[(-1,-1,-1),(1,-1,-1)]]})
    m['explicit_teaching_events']+=1;save(a,m)
    return {'kind':'explicit_context_experience','side_declared_by_teacher':side,'arrival_tick':arrival,'before':pre,'after':physical(a.world),
      'frames':frames,'request':sel.receipt(a.world,r),'scope':'Explicit zero-load material contact, native reference change. Not reward-learning by itself.'}
def use(a,*,detail=False):
    get(a);q=a.tick+4;pre=physical(a.world);rs=sel.query(a.world,q,5,'MU.selector');frames=[]
    for t in range(q,q+8):
        a.run_until(t)
        if detail:
            points={sel.at(ORIGIN,(x,y,z))for x in range(-3,4)for y in range(-3,5)for z in range(-4,4)}
            frames.append({'tick':a.tick,'sites':[observation(a,p)for p in sorted(points)]})
        if t==q+6:answer=sel.read(a.world,ORIGIN,N)
    return {'kind':'native_selection','query_tick':q,'read_tick':q+6,'before':pre,'after':physical(a.world),'reader':answer,
      'requests':[sel.receipt(a.world,r)for r in rs],'frames':frames,'not_selected_by_host':True}
def job(a,row,situation,directory,m,*,actuator='closed',feedback='real'):
    values=situation.get('valores')
    if not isinstance(values,list)or len(values)!=2 or any(type(x)is not int or not 0<=x<=64 for x in values):raise ValueError('Two bounded public work values required')
    domain=situation.get('dominio','trabajadores')
    if domain not in('trabajadores','transaccion'):raise ValueError('Only admitted local synthetic worker domains')
    choice=row['reader']['choice'];executed=choice if actuator=='closed'and choice in(-1,1)else None
    folder=Path(directory);folder.mkdir(parents=True,exist_ok=True);m['jobs']+=1;worker=None
    if executed is not None:
        cmd=[sys.executable,'-I','-B','-X','utf8',str(Path(__file__).with_name('eo02_trabajador_local.py'))]
        data={'domain':domain,'executed_worker':executed,'raw_observations':values,'capacity_credit':0,
          'pending_transaction':m['external_pending']if domain=='transaccion'else None,'attempt':m['jobs'],'native_tick':a.tick,'output_directory':str(folder.resolve())}
        start=time.monotonic();p=subprocess.run(cmd,input=json.dumps(data),encoding='utf8',text=True,capture_output=True,timeout=15)
        if p.returncode:raise RuntimeError('External tool failed; result uncertain, do not retry automatically: '+p.stderr)
        worker=json.loads(p.stdout);worker['argv']=cmd;worker['host_seconds']=time.monotonic()-start
        if domain=='transaccion':m['external_pending']=worker['pending_transaction']
    # Environmental law: an opportunity not completed by its deadline is a
    # failure, including no-action. It never substitutes an intelligent action.
    completed=bool(worker and worker.get('accepted'))
    returned=None
    if feedback=='real'and not completed:
        arrival=next_contact(a.tick);r=sel.experience(a.world,'A',arrival,'MU.selector')
        a.run_until(arrival-1);pre=[observation(a,sel.at(ORIGIN,p))for p in[(-1,-1,0),(1,-1,0)]]
        a.run_until(arrival+2)
        returned={'codec':'Actual failed/noncompleted opportunity -> one zero-load contact on the SAME fixed A peripheral port. No optimal action or correct bank encoded.',
          'arrival_tick':arrival,'request':sel.receipt(a.world,r),'reference_pre':pre,'reference_post':[observation(a,sel.at(ORIGIN,p))for p in[(-1,-1,0),(1,-1,0)]]}
    return {'native_choice':choice,'executed_worker':executed,'actuator':actuator,'feedback':feedback,'worker_receipt':worker,
      'opportunity_completed':completed,'no_action_deadline_is_not_native_wait_decision':executed is None,'return':returned,
      'scope':'Actual bounded local synthetic file action. Learned usefulness needs matched intact/omitted/null histories; not inferred from an isolated success.'}
def session(a,*,situations,directory,actuator='closed',feedback='real',detailed=False):
    m=get(a)
    if not isinstance(situations,list)or not 1<=len(situations)<=64:raise ValueError('1..64 typed situations')
    if actuator not in('closed','nulled')or feedback not in('real','omit'):raise ValueError('Explicit admitted actuator/return mode')
    out=[]
    for i,s in enumerate(situations):
        mode=s.get('modo','usar')
        if mode in('usar','trabajo'):
            r=use(a,detail=detailed);m['queries']+=1
            if mode=='trabajo':r['external']=job(a,r,s,Path(directory)/('episode_'+str(m['episodes']+1)),m,actuator=actuator,feedback=feedback)
        elif mode=='experiencia':
            r=experience(a,s.get('lado'));m=get(a)
        elif mode=='memoria':
            q={k:v for k,v in s.items()if k!='modo'};q['modo']=s.get('operacion_memoria','usar');q.pop('operacion_memoria',None)
            r={'kind':'explicit_operator_memory_access','result':ma.session(a,situations=[q],directory=directory,actuator=actuator,feedback=feedback,detailed=detailed),
              'assistance':'Operator chose context; native selector did NOT choose this bank.'}
        else:raise ValueError('Only usar/trabajo/experiencia/memoria; no implicit planner or target lookup')
        m['episodes']+=1;out.append(r);save(a,m)
    return {'version':VERSION,'rows':out,'final':state(a),'one_shared_native_world':True,'no_global_P2_R2_or_mind_claim':True}
