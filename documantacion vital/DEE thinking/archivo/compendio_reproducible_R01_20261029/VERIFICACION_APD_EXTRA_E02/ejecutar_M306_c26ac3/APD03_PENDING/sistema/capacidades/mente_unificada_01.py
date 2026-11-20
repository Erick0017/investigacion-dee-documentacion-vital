"""Integrated shared-world candidate: preserved MA02 memory and native P1 access.

Prepared R06 anatomy is installed with legal interfaces in vacant RAW sites.
No trained fields are transplanted. Selection reads physical actuator sites,
never the memory catalogue or expected worker. Outcome feedback is a fixed
failure contact, not an instruction telling DEE which action would be correct.
"""
from pathlib import Path
import base64,hashlib,json,subprocess,sys,time
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from dee_thinking.consolidated import exact_observation,exact_receipt
from app.native_tools import physical
from capacidades import selector_acrecion_nativo as sel
from capacidades import mente_acumulativa_r02 as ma

KEY='DEE.Cognitive.System.1.1.MENTE_UNIFICADA_01.v1'
VERSION='MUFI01.shared_world_selector.R2.transient_current'
PHASE_PROTECTION_VERSION='MUFI01.sensor_calendar.R3P0'
ORIGIN=(15,15,15);N=67
CURRENT_SITE=(14,15,16)
CURRENT_STOPS=[sel.at(ORIGIN,(3*x,3,3*z))for x in(-1,0,1)for z in(0,-1)]
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
    result={'version':VERSION,'sensor_access_protocol':m.get('phase_protection',{}).get('version',VERSION),'physical':physical(a.world,occupation=True),'origin':list(ORIGIN),
      'references':[observation(a,sel.at(ORIGIN,p))for p in[(-1,-1,0),(1,-1,0)]],
      'operational':m,'assistance':{'P0':'Prepared supports, absorbers, three generic query routes and fixed file-worker conversion; operator chooses operation, not selected sign or bank.',
      'P1':'Only when demonstrated for this own life: experience-conditioned relative reference and repeated native choice.',
      'P2_R2':'Not certified by installation or metadata; causal consequence contrasts required.'},
      'memory_contract':ma.state(a),'no_answer_catalogue_read':True}
    from capacidades import asistente_proposito_01 as apd
    if apd.KEY in dict(a.world.runtime.snapshot_metadata_entries):result['assistant']=apd.state(a)
    from capacidades import asistente_apd02 as apd02
    if apd02.KEY in dict(a.world.runtime.snapshot_metadata_entries):result['assistant_quality']=apd02.state(a)
    from capacidades import asistente_apd03 as apd03
    if apd03.KEY in dict(a.world.runtime.snapshot_metadata_entries):result['assistant_autonomy']=apd03.state(a)
    return result
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
def prepare_current(a):
    """Explicit P0 extension validated in FI01 BT.S1 R2, never a repair loop."""
    m=get(a)
    if m.get('current_frontend'):raise ValueError('Current frontend already prepared; never reinstall over a lived future')
    inert=int(d.pack_record(0,0,0,0,0,4));before=[observation(a,p)for p in CURRENT_STOPS]
    if any(int(o['raw'])not in(0,inert)for o in before):raise ValueError('Stop intersects causal RAW, including inactive fields; no overwrite')
    rs=[];at=a.tick+2
    for j,o in enumerate(before):
        if int(o['raw'])==inert:continue
        name='MU.current.stop.'+str(j);c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*CURRENT_STOPS[j]);c.direction=d.Direction(0,0,0);c.state=0;c.semantic=4;c.allow_experience=True;c.allow_probe=False
        i=d.InterfaceSpec();i.name=name;i.channel=c;a.world.declare_interface(i);r=a.world.submit(name,0,at)
        rs.append({'id':int(r.id),'port':name,'payload':0,'tick':at,'site':list(CURRENT_STOPS[j])})
    a.run_until(at+1);receipts=[sel.receipt(a.world,r)for r in rs]
    if any(r['receipt']['status']!='applied'for r in receipts):raise ValueError('Frontend preparation incomplete; retain future, no implicit retry')
    m['current_frontend']={'version':'BT.S1.R2','prepared_tick':a.tick,'site':list(CURRENT_SITE),'reader':'All six fixed E+2*(x,1,z), x=-1/0/+1 z=0/-1, at query+6; no target argument.'};save(a,m)
    return {'before':before,'after':[observation(a,p)for p in CURRENT_STOPS],'requests':receipts,'classification':'Prepared generic sensor and equal output termination P0, not learned magnitude or autonomous routing.'}
def current_read(a):
    observations=[];cs=[]
    for x in(-1,0,1):
        for z in(0,-1):
            o=observation(a,sel.at(ORIGIN,(2*x,2,2*z)));observations.append(o)
            if o['state']>0 and o['semantic']==1 and o['direction']==[x,1,z]:cs.append({'choice':x,'observation':o})
    return {'tick':a.tick,'observations':observations,'candidates':cs,'choice':cs[0]['choice']if len(cs)==1 else None,'information':'Six frozen direction/position classes. No current value, expected action, target, token or history is a reader argument.'}

def protect_phase(a):
    """Explicit operator-prepared calendar only; no physical memory repair."""
    m=get(a)
    if not m.get('current_frontend'):raise ValueError('A physically admitted current frontend is required; never install it silently')
    if m.get('phase_protection'):raise ValueError('Phase protection already explicitly admitted; no reset or replacement')
    clocks=[observation(a,p)['clock']for p in((14,14,15),(16,14,15))]
    if any(int(c)!=int(a.tick)for c in clocks):raise ValueError('Outside R3P0 aligned local A/B clock domain; no clock edit or implicit alignment')
    m['phase_protection']={'version':PHASE_PROTECTION_VERSION,'enabled':True,'admitted_tick':int(a.tick),'admission_local_clocks':clocks,
      'domain':'N67, admitted current frontend, local A/B clocks aligned to the complete-world tick at admission.',
      'calendar':'Before any sensory input, move the complete protocol by0..10ticks so inclusive query-1..query+8 contains no multiple391.',
      'attribution':'Explicit prepared P0 scheduling, not acquired regulation, content recovery, general R2 or an autonomous strategy. Existing paths/readers/codec are unchanged.'}
    save(a,m)
    return {'version':PHASE_PROTECTION_VERSION,'physical':physical(a.world),'phase_protection':m['phase_protection'],'native_ticks_advanced':0,'learned_fields_edited':False}

def calendar_query_timing(requested,protected=False):
    """Pure integer calendar: receives no sensor value, target or native field."""
    if type(requested)is not int or requested<2:raise ValueError('Exact positive requested query tick required')
    effective=requested
    if protected:
        boundary=((requested-2)//391+1)*391
        if boundary<=requested+8:effective=boundary+2
    wait=effective-requested
    if not 0<=wait<=10:raise AssertionError('Calendar displacement exceeded the prepared bound')
    if protected and(effective-2)//391!=(effective+8)//391:raise AssertionError('Inclusive protected window still contains a391boundary')
    return {'protocol':PHASE_PROTECTION_VERSION if protected else VERSION,'enabled':bool(protected),'requested_query_tick':requested,
      'effective_query_tick':effective,'wait_ticks':wait,'critical_window_inclusive':[effective-1,effective+8],
      'phase_selection_information':'Exact integer calendar only; no raw sensor value, target, expected response, reader output or memory content.'}

def query_timing(a,requested):
    m=get(a);guard=m.get('phase_protection')
    if guard and(guard.get('version')!=PHASE_PROTECTION_VERSION or guard.get('enabled')is not True):raise ValueError('Unknown phase protection contract; no silent fallback')
    return calendar_query_timing(requested,bool(guard))

def current(a,value,*,detail=False):
    m=get(a)
    if not m.get('current_frontend'):raise ValueError('Explicit unificada-preparar-dato required on a compatible fork; never install silently')
    if type(value)is not int or not 0<=value<=512:raise ValueError('Current sensor accepts one exact raw scalar0..512, no externally calculated action')
    timing=query_timing(a,int(a.tick)+8);q=timing['effective_query_tick'];before=physical(a.world);rs=[];datum_pre=observation(a,CURRENT_SITE)
    ma.submit(a,'MU.current.datum',CURRENT_SITE,(0,0,0),value,q+3,rs)
    qr=sel.query(a.world,q,5,'MU.selector');frames=[]
    for t in range(q-1,q+9):
        a.run_until(t)
        if detail:
            points={sel.at(ORIGIN,(x,y,z))for x in range(-3,4)for y in range(-3,5)for z in range(-4,4)}
            frames.append({'tick':a.tick,'sites':[observation(a,p)for p in sorted(points)]})
        if t==q+6:answer=current_read(a)
    return {'kind':'native_current_selection','raw_sensor_value':value,'query_tick':q,'read_tick':q+6,'timing':timing,'reader':answer,'before':before,'after':physical(a.world),'datum_pre':datum_pre,'datum_after':observation(a,CURRENT_SITE),'requests':ma.receipts(a,rs)+[sel.receipt(a.world,r)for r in qr],'frames':frames,'scope':'Prepared fixed scalar sensor plus acquired relative reference in the same world. The host does not compute a comparison or choose an action. Explicit R3P0 calendar, when admitted, is prepared assistance and never learned regulation.'}
def job(a,row,situation,directory,m,*,actuator='closed',feedback='real'):
    values=situation.get('valores')
    if not isinstance(values,list)or len(values)!=2 or any(type(x)is not int or not 0<=x<=64 for x in values):raise ValueError('Two bounded public work values required')
    domain=situation.get('dominio','trabajadores')
    if domain not in('trabajadores','transaccion'):raise ValueError('Only admitted local synthetic worker domains')
    if m.get('external_uncertain'):raise ValueError('An external action has uncertain outcome; examine its actual receipt/effect before any new execution, never auto-retry')
    choice=row['reader']['choice'];executed=choice if actuator=='closed'and choice in(-1,1)else None
    folder=Path(directory);folder.mkdir(parents=True,exist_ok=True);m['jobs']+=1;worker=None
    if executed is not None:
        cmd=[sys.executable,'-I','-B','-X','utf8',str(Path(__file__).with_name('eo02_trabajador_local.py'))]
        data={'domain':domain,'executed_worker':executed,'raw_observations':values,'capacity_credit':0,
          'pending_transaction':m['external_pending']if domain=='transaccion'else None,'attempt':m['jobs'],'native_tick':a.tick,'output_directory':str(folder.resolve())}
        m['external_uncertain']={'attempt':m['jobs'],'native_tick':a.tick,'output_directory':str(folder.resolve()),'worker':executed,'state':'Intent persisted before process launch; receipt not yet reconciled.'};save(a,m)
        start=time.monotonic();p=subprocess.run(cmd,input=json.dumps(data),encoding='utf8',text=True,capture_output=True,timeout=15)
        if p.returncode:raise RuntimeError('External tool failed; result uncertain, do not retry automatically: '+p.stderr)
        worker=json.loads(p.stdout);worker['argv']=cmd;worker['host_seconds']=time.monotonic()-start;m['external_uncertain']=None
        if domain=='transaccion':m['external_pending']=worker['pending_transaction']
        save(a,m)
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
def chain_begin(a,situation,directory,m,*,actuator='closed',detailed=False):
    """Assisted first request; the acquired memory, not the host, selects worker.

    The operator supplies a public context. No claim of learned context routing
    or autonomous planning is made. The next request is separately explicit.
    """
    if m.get('cascade_pending')or m.get('external_pending'):raise ValueError('An actual transaction is already pending; finish it or inspect it, never replace its past')
    values=situation.get('valores')
    if not isinstance(values,list)or len(values)!=2 or any(type(v)is not int or not 0<=v<=64 for v in values):raise ValueError('Two public bounded raw values required before material use')
    context=situation.get('contexto')
    memory=ma.session(a,situations=[{'contexto':context,'modo':'usar'}],directory=directory,detailed=detailed)
    mr=memory['rows'][0];row={'reader':{'choice':mr['reader']['formed_native_command']}}
    execution=job(a,row,{'valores':values,'dominio':'transaccion'},Path(directory)/('chain_prepare_'+str(m['jobs']+1)),m,actuator=actuator,feedback='omit')
    if m.get('external_pending'):
        m['cascade_pending']={'values':values,'prepared_tick':a.tick,'context_public':context,'stage':'Actual artifact prepared; awaiting explicit generic sensor/use request. No correct second worker stored.'}
    save(a,m)
    return {'kind':'assisted_chain_begin','memory_use':memory,'external':execution,'next_stage_available':bool(m.get('cascade_pending')),'scope':'One acquired opaque association selects a real first worker. Operator context addressing and separate stage request remain P0; no automatic learned planner.'}
def chain_finish(a,directory,m,*,actuator='closed',detailed=False):
    pending=m.get('external_pending');cascade=m.get('cascade_pending')
    if not pending or not cascade:raise ValueError('No actual prepared chain to sense; no substituted fixture')
    payload=base64.b64decode(pending['prepared_output_base64']);name=pending['prepared_output_name']
    if Path(name).name!=name:raise ValueError('External artifact name must be a relative local member')
    folder=Path(directory)/'chain_sensor';folder.mkdir(parents=True,exist_ok=True)
    artifact=folder/(pending['prepared_output_sha256']+'_'+name)
    restored=not artifact.exists()
    if restored:artifact.write_bytes(payload)
    measured=artifact.read_bytes()
    if measured!=payload or hashlib.sha256(measured).hexdigest()!=pending['prepared_output_sha256']:raise ValueError('Actual pending artifact bytes differ; no silent repair or correct-answer substitution')
    # Identity sensor. No sign, threshold, desired worker, eligibility or
    # compression-vs-hash label is computed here. The acquired physical
    # reference plus six-site fixed native reader determine the second sign.
    row=current(a,len(measured),detail=detailed)
    execution=job(a,row,{'valores':cascade['values'],'dominio':'transaccion'},Path(directory)/('chain_verify_'+str(m['jobs']+1)),m,actuator=actuator,feedback='omit')
    if execution['worker_receipt']and execution['worker_receipt'].get('transaction_completed'):m['cascade_pending']=None
    save(a,m)
    return {'kind':'assisted_chain_finish','measurement':{'actual_file':str(artifact),'bytes':len(measured),'sha256':hashlib.sha256(measured).hexdigest(),'restored_exact_serialized_external_state':restored,'transduction':'Exact byte count -> one raw native scalar, without action calculation.'},'native_use':row,'external':execution,'scope':'Prepared two-request environmental composition of acquired context and acquired scalar reference in one life. No learned stage selection, no abstraction or autonomous planner claimed.'}
def session(a,*,situations,directory,actuator='closed',feedback='real',detailed=False):
    m=get(a)
    if not isinstance(situations,list)or not 1<=len(situations)<=64:raise ValueError('1..64 typed situations')
    if actuator not in('closed','nulled')or feedback not in('real','omit'):raise ValueError('Explicit admitted actuator/return mode')
    out=[]
    for i,s in enumerate(situations):
        mode=s.get('modo','usar')
        if isinstance(mode,str)and mode.startswith('apd03'):
            from capacidades import asistente_apd03 as apd03
            if actuator!='closed':raise ValueError('APD03 currently admits only its declared closed actuator; no silently ignored nulling control')
            if mode=='apd03-admitir':r=apd03.admit(a,consequence_mode=s.get('consecuencia','local_useful'))
            elif mode=='apd03-docencia':r=apd03.teach(a,s['texto'],s['senal'],revision=s.get('revision',False))
            elif mode=='apd03-lenguaje':r=apd03.language(a,s['texto'],s['valor'],s['contexto'],detailed=detailed)
            elif mode=='apd03-panel':r=apd03.panel(a,new_forms=s.get('nuevas',False),memories=s.get('memorias',False),detailed=detailed)
            elif mode=='apd03-tarea-iniciar':r=apd03.start_task(a,s['texto'],s['operandos'],s['segundo_visible'],Path(directory)/('apd03_goal_'+str(m['episodes']+1)),context=s.get('contexto_ambiente',0))
            elif mode=='apd03-paso':r=apd03.step(a,s['oportunidades'],Path(directory)/('apd03_step_'+str(m['episodes']+1)),feedback=feedback,detailed=detailed)
            else:raise ValueError('Unknown declared APD03 mode')
            m=get(a)
        elif isinstance(mode,str)and mode.startswith('apd02'):
            from capacidades import asistente_apd02 as apd02
            if mode=='apd02-admitir':r=apd02.admit(a)
            elif mode=='apd02-ruta-admitir':r=apd02.upgrade_route(a)
            elif mode=='apd02-ruta04-admitir':r=apd02.upgrade_route04(a)
            elif mode=='apd02':r=apd02.execute(a,s['texto'],s['operandos'],Path(directory)/('apd02_'+str(m['episodes']+1)),feedback=feedback,actuator=actuator,detailed=detailed)
            elif mode=='apd02-ambiente':r=apd02.configure(a,s['configuracion'])
            elif mode=='apd02-docencia':r=apd02.words.teach(a,s['texto'],s['senal'],revision=s.get('revision',False))
            elif mode=='apd02-lenguaje':r=apd02.words.use_relation(a,s['texto'],s['valor'],s['contexto'],detailed=detailed)
            elif mode=='apd02-acumular':r=apd02.accumulator.accumulate(a,s['valor'],delay_periods=s.get('demora_periodos',0))
            elif mode=='apd02-componer':r=apd02.compose(a,s['formas'],s['datos'],Path(directory)/('apd02_composition_'+str(m['episodes']+1)),feedback=feedback,actuator=actuator,detailed=detailed)
            elif mode in('apd02-meta','apd02-meta-iniciar'):r=apd02.start_goal(a,s['texto'],s['operandos'],s['segundo_visible'],Path(directory)/('apd02_goal_'+str(m['episodes']+1)),run=mode=='apd02-meta',feedback=feedback,detailed=detailed)
            elif mode=='apd02-meta-paso':r=apd02.continue_goal(a,s['oportunidades'],Path(directory)/('apd02_goal_resume_'+str(m['episodes']+1)),feedback=feedback,detailed=detailed)
            else:raise ValueError('Unknown declared APD02 mode')
            m=get(a)
        elif mode in('apd','apd-docencia','apd-ambiente','apd-conteo','apd-componer','apd-ruta-docencia'):
            from capacidades import asistente_proposito_01 as apd
            if mode=='apd':r=apd.execute(a,s['texto'],s['operandos'],Path(directory)/('apd_'+str(m['episodes']+1)),actuator=actuator,feedback=feedback,detailed=detailed)
            elif mode=='apd-componer':r=apd.compose(a,s['formas'],s['datos'],Path(directory)/('apd_composition_'+str(m['episodes']+1)),actuator=actuator,feedback=feedback,detailed=detailed)
            elif mode=='apd-conteo':
                from capacidades import aritmetica_apd_01 as ar
                r=ar.native_count(a,s['presencias'],detailed=detailed)
            elif mode=='apd-ruta-docencia':r=apd.teach_route(a,s['lado'])
            elif mode=='apd-docencia':r=apd.teach(a,s['texto'],s['senal'],revision=s.get('revision',False))
            else:r=apd.configure(a,s['configuracion'])
            m=get(a)
        elif mode in('usar','trabajo'):
            r=use(a,detail=detailed);m['queries']+=1
            if mode=='trabajo':r['external']=job(a,r,s,Path(directory)/('episode_'+str(m['episodes']+1)),m,actuator=actuator,feedback=feedback)
        elif mode=='experiencia':
            r=experience(a,s.get('lado'));m=get(a)
        elif mode=='dato':
            r=current(a,s.get('valor'),detail=detailed);m['queries']+=1
        elif mode=='crudos':
            from capacidades import percepcion_cruda_fi01 as pc
            r=pc.frame(a,s.get('componentes'),detailed=detailed);m['queries']+=1
        elif mode=='cadena-iniciar':
            r=chain_begin(a,s,directory,m,actuator=actuator,detailed=detailed)
        elif mode=='cadena-finalizar':
            r=chain_finish(a,directory,m,actuator=actuator,detailed=detailed)
        elif mode=='memoria':
            q={k:v for k,v in s.items()if k!='modo'};q['modo']=s.get('operacion_memoria','usar');q.pop('operacion_memoria',None)
            r={'kind':'explicit_operator_memory_access','result':ma.session(a,situations=[q],directory=directory,actuator=actuator,feedback=feedback,detailed=detailed),
              'assistance':'Operator chose context; native selector did NOT choose this bank.'}
        else:raise ValueError('Only usar/trabajo/experiencia/dato/crudos/memoria/cadena-iniciar/cadena-finalizar; no implicit planner or target lookup')
        m['episodes']+=1;out.append(r);save(a,m)
    return {'version':VERSION,'rows':out,'final':state(a),'one_shared_native_world':True,'no_global_P2_R2_or_mind_claim':True}

def additional_operational_state(a):
    from capacidades import asistente_proposito_01 as apd
    if apd.KEY not in dict(a.world.runtime.snapshot_metadata_entries):return {}
    s=apd.state(a)
    result={'APD01':{'environment':s['operational'],'external_uncertain':s['external_uncertain']}}
    from capacidades import asistente_apd02 as apd02
    if apd02.KEY in dict(a.world.runtime.snapshot_metadata_entries):
        s2=apd02.state(a);m2=apd02.get(a)
        result['APD02']={'environment':s2['operational_environment'],'external_uncertain':s2['external_uncertain'],'goal_operational_state':m2.get('goal_pending')}
    from capacidades import asistente_apd03 as apd03
    if apd03.KEY in dict(a.world.runtime.snapshot_metadata_entries):
        m3=apd03.get(a)
        result['APD03']={'goal_operational_state':m3.get('goal_pending'),'external_uncertain':m3.get('external_uncertain')}
    return result

def external_uncertainty(a):
    if bool(get(a).get('external_uncertain')):return True
    extra=additional_operational_state(a)
    return bool(extra.get('APD01',{}).get('external_uncertain')or extra.get('APD02',{}).get('external_uncertain')or extra.get('APD03',{}).get('external_uncertain'))
