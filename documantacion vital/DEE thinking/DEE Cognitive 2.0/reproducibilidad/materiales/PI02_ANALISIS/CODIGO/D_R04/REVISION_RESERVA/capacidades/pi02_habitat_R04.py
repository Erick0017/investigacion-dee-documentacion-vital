"""PI02 R04 developmental clocked workbench and fixed physical transducers.

No target, private fixture or historical label enters either Native decoder.
The simulator is external: fixed sensors, valve, capacity, costs and resource
laws are preparation. Native recurring directions and an acquired W/U product
select commands; only actual consequences produce generic valence.
"""
from pathlib import Path
import hashlib,json
VERSION='PI02.continuous_workbench.R04_DEV1'
KEY='DEE.Cognitive.PI02.continuous_workbench.R04'
FOLDER='PI02_WORKBENCH_R04';N=67;FEEDBACK=10*N;BUSY=FEEDBACK+40;VALVE_TTL=22*N
RAW_NOISE='PI02.R03.FI.noise.raw0'
def _modules():
    from capacidades import pi01_traza_legal_base as tr
    from capacidades import pi02_diagnostico_base as d
    from capacidades import pi02_advertencia_R03 as w
    from capacidades import fi_async_R04 as fi
    from capacidades import percepcion_cruda_fi01 as p
    from capacidades import mente_unificada_01 as mu
    return tr,d,w,fi,p,mu
def _decode(e):
    from dee_thinking.persistence import decode_metadata
    return decode_metadata(e)
def _save(a,m):
    from dee_thinking.persistence import encode_metadata
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
def get(a):
    e=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in e:raise ValueError('Explicit R04 workbench admission required; no reconstruction')
    m=_decode(e[KEY])
    if m['version']!=VERSION:raise ValueError('R04 protocol revision mismatch')
    return m
def digest(data):return hashlib.sha256(data).hexdigest()
def _record(m,directory,event):
    event={'index':m['log_count'],'tick':m['last_tick'],**event}
    data=(json.dumps(event,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')
    path=Path(directory)/FOLDER/'eventos.jsonl'
    with path.open('ab')as out:out.write(data);out.flush()
    m['log_count']+=1
    m['log_chain_sha256']=digest(bytes.fromhex(m['log_chain_sha256'])+data)
def fixtures(series):
    dev=[(10,4),(7,2),(6,6),(3,12),(14,6),(15,4)]
    reserve=[(12,4),(17,6),(9,3),(18,7),(5,14),(16,3),(19,8),(2,11),(18,5),(4,13),(16,8),(8,8)]
    pairs=dev if series=='development'else reserve
    rows=[]
    for i,(l,r)in enumerate(pairs):
        rows.append({'public':{'left':l,'right':r},'peripheral_active':i not in(7,11),'warning_offered':i in(5,6,7,8,10),'warning_lead':[61,128,195][i%3],'device_wiring':'reverse_close'if i in(8,9)else'normal'})
    return rows
def admit(a,directory,series,history,arm):
    from app.native_tools import physical
    tr,d,w,fi,p,mu=_modules()
    if series not in('development','reserved')or history not in('paired','unpaired','no_training','report_only')or arm not in('real','warning_cut','actuator_null','valence_omit'):raise ValueError('Explicit finite apparatus, history and control arm required')
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('Existing workbench history must continue; never reset')
    tr.get(a)
    if int(a.world.runtime.dimension)!=67:raise ValueError('Inherited N67 only')
    if w.KEY not in dict(a.world.runtime.snapshot_metadata_entries):warning_preparation=w.prepare(a)
    else:
        if w.get(a).get('training')is not None:raise ValueError('This workbench requires acquisition in its own declared first experience, no prototype memory import')
        warning_preparation={'existing_untrained_interfaces':True}
    g=p.geometry(128);raw0=next(x for x in g['raw_sources']if x['component_index']==0)
    p.declare(a,RAW_NOISE,raw0['site'],raw0['direction'],state=1,semantic=1)
    home=Path(directory)/FOLDER
    if home.exists():raise ValueError('Unpaired existing workbench files; preserve and inspect')
    for folder in('reservoir','collected','control_stock','control_spent'):(home/folder).mkdir(parents=True,exist_ok=False)
    bank=[]
    for i in range(len(fixtures(series))):
        payload=hashlib.sha256(('PI02R04 work '+str(i)).encode('ascii')).digest()*2
        file='%04d.bin'%i;(home/'reservoir'/file).write_bytes(payload);bank.append({'episode':i,'file':file,'bytes':64,'sha256':digest(payload)})
    coupons=[]
    for i in range(16):
        payload=hashlib.sha256(('PI02R04 control '+str(i)).encode('ascii')).digest()*2
        file='%04d.bin'%i;(home/'control_stock'/file).write_bytes(payload);coupons.append({'index':i,'file':file,'bytes':64,'sha256':digest(payload)})
    m={'version':VERSION,'series':series,'history':history,'arm':arm,'prepared_tick':int(a.tick),'last_tick':int(a.tick),'enabled':True,'uncertain':False,'episode':0,'fixtures':fixtures(series),'active':None,'resources':0,'resource_bank':bank,'collected':[],'coupons':coupons,'spent':[],'guard_until':None,'sensor_input_phase':0,'training_completed':False,'training_anchor':None,'detector_o_active':False,'detector_h_active':False,'returns':0,'busy_returns':0,'exhausted_returns':0,'close_signatures':0,'false_close_signatures':0,'work_frames':0,'log_count':0,'log_chain_sha256':'00'*32,'native_observations':0,'paused_intervals':[],'opportunity_initiation':'Physical returningOcarrier while clock supplied; recurrence/capacity are prepared, timing is not learned','boundary':'Native state carries policy/content. This metadata is the external workbench/progress, not an actor policy table.'}
    _save(a,m);_record(m,directory,{'kind':'WORKBENCH_ADMITTED','warning_preparation':warning_preparation,'history_arm_is_not_available_to_decoders':True,'physical':physical(a.world,occupation=True)});_save(a,m)
    return {'version':VERSION,'tick':int(a.tick),'new_native_ticks':0,'warning_preparation':warning_preparation,'resource_slots':len(bank),'control_packets':len(coupons),'state':'Admitted external apparatus, no warning product seeded'}
def _plan_fi(a,fixture,minimum_delay):
    tr,d,w,fi,p,mu=_modules();g=p.geometry(128);start=int(a.tick)
    for leaf in range(start+minimum_delay,start+minimum_delay+4*N+1):
        if leaf%N:continue
        timing=mu.query_timing(a,leaf-g['raw_relative_tick']+35)
        if timing['wait_ticks']:continue
        job=fi.start(a,fixture['public']['left'],fixture['public']['right'],start_delay=leaf-start-2)
        if job['input_tick']!=leaf:raise ValueError('Prepared sensor phase not reached; no clock repair')
        return job
    raise ValueError('No admitted prepared calendar slot within finite4N planning bound')
def _guard_active(m,tick):return m['guard_until']is not None and tick<=m['guard_until']
def _device(a,m,directory,command,origin):
    act=m['active'];fixture=act['fixture']if act else {'device_wiring':'normal','peripheral_active':False}
    event={'kind':'DEVICE_COMMAND','origin':origin,'command':command,'native_tick':int(a.tick),'guard_before':_guard_active(m,int(a.tick)),'wiring':fixture['device_wiring']}
    if m['arm']=='actuator_null'or(origin=='learned_warning'and m['arm']=='warning_cut'):
        event.update(applied=False,reason='Declared post-emission actuator cut');_record(m,directory,event);return event
    if len(m['spent'])>=len(m['coupons']):
        event.update(applied=False,reason='Finite control packets unavailable');_record(m,directory,event);return event
    coupon=m['coupons'][len(m['spent'])];home=Path(directory)/FOLDER;src=home/'control_stock'/coupon['file'];dst=home/'control_spent'/coupon['file']
    if dst.exists()or not src.is_file()or digest(src.read_bytes())!=coupon['sha256']:raise ValueError('Uncertain/altered prior device effect; never repeat')
    src.replace(dst)
    m['spent'].append(coupon)
    on=_guard_active(m,int(a.tick))
    if command=='TOGGLE':on=not on
    elif command=='CLOSE':on=fixture['device_wiring']!='reverse_close'
    else:raise ValueError('Unknown fixed actuator command')
    m['guard_until']=int(a.tick)+VALVE_TTL if on else None
    event.update(applied=True,guard_after=on,guard_until=m['guard_until'],actual_control_packet=coupon,resource_cost_bytes=64)
    _record(m,directory,event);return event
def _effect(m,directory,physical_choice,fixture):
    l=fixture['public']['left'];r=fixture['public']['right'];nl,nr=l,r
    command=physical_choice if m['arm']!='actuator_null'else None;blocked=False
    if command is not None and(type(command)is not int or command not in(-1,0,1)):raise ValueError('Invalid physical work actuator')
    if command==1:
        if l>0 and r<32:nl-=1;nr+=1
        else:blocked=True
    elif command==-1:
        if r>0 and l<32:nr-=1;nl+=1
        else:blocked=True
    useful=command is not None and not blocked and(abs(nl-nr)<abs(l-r)or(l==r and command==0))
    effect={'kind':'WORK_EFFECT','physical_choice':physical_choice,'applied_command':command,'loads_before':[l,r],'loads_after':[nl,nr],'blocked_by_external_capacity':blocked,'useful':useful,'zero_is_not_NULL':True,'resource':None}
    if useful:
        item=m['resource_bank'][m['episode']];home=Path(directory)/FOLDER;payload=(home/'reservoir'/item['file']).read_bytes();dest=home/'collected'/item['file']
        if dest.exists():raise ValueError('Already materialized resource; no duplicate actuation')
        with dest.open('xb')as f:f.write(payload)
        if digest(dest.read_bytes())!=item['sha256']:raise ValueError('Resource artifact mismatch')
        m['collected'].append(item);m['resources']+=1;effect['resource']=item
    return effect
def _start_event(a,m,directory,route,observation):
    tr,d,w,fi,p,mu=_modules();q=int(a.tick);fixture=m['fixtures'][m['episode']]
    act={'episode':m['episode'],'q':q,'route':route,'request_observation':observation,'fixture':fixture,'feedback_tick':q+FEEDBACK,'busy_until':q+BUSY,'feedback_request':None,'negative':None,'effect':None,'job':None,'noise_request':None,'noise_gate_decision':None,'report_checked':False,'warning_requests':[],'is_training':not m['training_completed'],'work_finalized':False}
    m['active']=act
    if route==1:
        act['effect']={'kind':'DEVICE_COST_OPPORTUNITY','device':_device(a,m,directory,'TOGGLE','native_return_B'),'useful':False,'reason':'A real control packet is spent, no work product formed in this opportunity'}
        act['negative']=True
    else:
        training=act['is_training'];lead=fixture['warning_lead'];minimum=90 if training else max(90,lead+12)
        job=_plan_fi(a,fixture,minimum);act['job']=job;act['leaf']=job['input_tick'];m['work_frames']+=1
        if job['end_tick']>=act['feedback_tick']-2:raise ValueError('Declared fixed feedback deadline cannot cover planned frame')
        if training:
            anchor=act['leaf']+6;m['training_anchor']=anchor
            # Prelude comes from the source warm-up. U is emitted later only
            # after the real raw0 rejection receipt; no desired action supplied.
            if m['history']in('paired','unpaired'):
                at=act['leaf']-(1 if m['history']=='unpaired'else 2)
                act['warning_requests'].append(w._submit(a,'W',w.WARNING_LOAD,at))
            act['warning_arrival']=anchor+(1 if m['history']=='unpaired'else 0)
        elif fixture['warning_offered']:
            arrival=act['leaf']-lead
            if arrival%N!=6:raise ValueError('Warning calendar outside declared acquired phase; no rescue')
            act['warning_arrival']=arrival
            act['warning_requests'].append(w._submit(a,'W',w.WARNING_LOAD,arrival-8))
            act['warning_requests'].append(w._submit(a,'G',w.NORMALIZER_LOAD,arrival+N-3))
    _record(m,directory,{'kind':'NATIVE_RETURN_ADMITTED','episode':act['episode'],'q':q,'route':route,'origin_observation':observation,'fixture_environment_only':fixture,'input_leaf':act.get('leaf'),'warning_arrival':act.get('warning_arrival'),'is_training':act['is_training'],'feedback_tick':act['feedback_tick'],'busy_until':act['busy_until']})
def _before_tick(a,m,directory,next_tick):
    tr,d,w,fi,p,mu=_modules();act=m['active']
    if not act:return
    if act['job'] is not None and not act['work_finalized']:
        leaf=act['leaf']
        if next_tick==leaf and act['noise_gate_decision']is None:
            peripheral=act['fixture']['peripheral_active'];guard=_guard_active(m,int(a.tick))
            act['noise_gate_decision']={'offered':peripheral,'guard_closed':guard,'native_submit':peripheral and not guard,'at_tick':int(a.tick),'source_tick':leaf}
            if peripheral and not guard:
                raw0=act['job']['noise_plan_auditor_environment_only']['raw_component0_source']
                receipt=a.world.submit(RAW_NOISE,7,leaf)
                act['noise_request']={'id':int(receipt.id),'port':RAW_NOISE,'tick':leaf,'payload':7,'site':raw0['site'],'direction':raw0['direction']}
            _record(m,directory,{'kind':'PERIPHERAL_GATE','episode':act['episode'],**act['noise_gate_decision']})
    if next_tick==act['feedback_tick']-1 and act['feedback_request']is None:
        if act['negative']is None:raise ValueError('Actual consequence absent at frozen feedback deadline')
        if act['negative']and m['arm']!='valence_omit':
            name=tr.get(a)['prefix']+'penalty'+str(act['route'])
            receipt=tr.submit_arrival(a,name,5,act['feedback_tick'])
            act['feedback_request']=int(receipt.id)
            _record(m,directory,{'kind':'NEGATIVE_VALENCE_SUBMITTED','episode':act['episode'],'id':int(receipt.id),'arrival':act['feedback_tick'],'actual_route_echo':act['route'],'load':5})
def _after_tick(a,m,directory,o,h):
    tr,d,w,fi,p,mu=_modules();t=int(a.tick);act=m['active']
    if act and act['job']is not None and not act['work_finalized']:
        leaf=act['leaf']
        if act['is_training']and t==leaf+1 and not act['report_checked']:
            rid=act['job']['noise_plan_auditor_environment_only']['raw_component0_source']['receipt_id'];receipt=tr.rr(a,type('ReceiptID',(),{'id':rid})())
            if receipt['status']!='applied'and not receipt['status'].startswith('rejected'):raise ValueError('Input sensor lacks a terminal receipt at its frozen observation tick; preserve future, no semantic rescue')
            failed=receipt['status'].startswith('rejected');report=None
            if failed and m['history']!='no_training':report=w._submit(a,'U',w.REPORT_LOAD,leaf+3);act['warning_requests'].append(report)
            wm=w.get(a);wm['training']={'history_record_only':m['history'],'anchor_external':leaf+6,'end_tick':None,'source':'Actual sampled-input rejection transduced after its terminal receipt; no expected action/content in this report','actual_raw0_receipt':receipt,'report_request_id':None if report is None else report['id']};w._save(a,wm)
            act['report_checked']=True;m['training_completed']=True
            _record(m,directory,{'kind':'ACTUAL_INPUT_FAILURE_SENSOR','episode':act['episode'],'raw0_receipt':receipt,'U_request':report,'training_anchor':leaf+6})
        event=fi.observe_at_tick(a,act['job'])
        if event is not None:
            act['effect']=_effect(m,directory,event['physical_choice'],act['fixture']);act['negative']=not act['effect']['useful']
            _record(m,directory,{'kind':'FI_EMISSION_AND_EFFECT','episode':act['episode'],'emission':event,'effect':act['effect'],'guard_at_effect':_guard_active(m,t)})
        if t==act['job']['end_tick']:
            trial=fi.finish(a,act['job']);act['work_finalized']=True
            noise=None if act['noise_request']is None else tr.rr(a,type('ReceiptID',(),{'id':act['noise_request']['id']})())
            _record(m,directory,{'kind':'FI_FRAME_FINISHED','episode':act['episode'],'trial':trial,'noise_receipt':noise,'gate':act['noise_gate_decision']})
    if act and t==act['busy_until']:
        feedback=None if act['feedback_request']is None else tr.rr(a,type('ReceiptID',(),{'id':act['feedback_request']})())
        warning_receipts=w._receipts(a,act['warning_requests'])
        _record(m,directory,{'kind':'OPPORTUNITY_COMPLETED','episode':act['episode'],'q':act['q'],'route':act['route'],'effect':act['effect'],'feedback':feedback,'warning_receipts':warning_receipts,'resources_total':m['resources'],'control_packets_spent':len(m['spent'])})
        m['episode']+=1;m['active']=None
    r=d.route(o);oactive=r is not None;onew=oactive and not m['detector_o_active'];m['detector_o_active']=oactive
    close=w.decode_fixed(h) is not None;hnew=close and not m['detector_h_active'];m['detector_h_active']=close
    if onew:
        m['returns']+=1
        if m['active']is not None:m['busy_returns']+=1
        elif m['episode']>=len(m['fixtures']):m['exhausted_returns']+=1
        else:_start_event(a,m,directory,r,o)
    if hnew:
        m['close_signatures']+=1
        if m['active']is None or not m['active']['fixture']['peripheral_active']:m['false_close_signatures']+=1
        _record(m,directory,{'kind':'LEARNED_WARNING_SIGNATURE','observation':h,'active_episode':None if m['active']is None else m['active']['episode'],'scope':'Fixed physical signature. Its acquired origin and usefulness require controls; no automatic verdict.'})
        _device(a,m,directory,'CLOSE','learned_warning')
def advance(base,target,directory):
    from app.native_tools import physical
    tr,d,w,fi,p,mu=_modules();m=get(base);target=int(target)
    if target<int(base.tick):raise ValueError('No rewind')
    if m['uncertain']:raise ValueError('Preserved R04 uncertainty; no implicit retry')
    if not m['enabled']:
        before=int(base.tick);base.run_until(target);m['last_tick']=int(base.tick);m['paused_intervals']=(m['paused_intervals']+[{'from':before,'to':int(base.tick),'external_bridge_disabled_not_native_world_frozen':True}])[-16:];_save(base,m);return
    if m['last_tick']!=int(base.tick):raise ValueError('An unobserved active-bridge time gap exists; no reconstruction')
    origin=tuple(tr.get(base)['origin'])
    try:
        for tick in range(int(base.tick)+1,target+1):
            _before_tick(base,m,directory,tick);base.run_until(tick);m['last_tick']=tick
            o=tr.obs(base,origin);h=w._observation(base,w.H);m['native_observations']+=2
            if o['state']>0 or h['state']>0:_record(m,directory,{'kind':'FIXED_PORT_OBSERVATIONS','O':o,'H':h})
            _after_tick(base,m,directory,o,h)
        _save(base,m)
    except BaseException:
        m['uncertain']=True;_save(base,m);raise
def set_enabled(a,enabled):
    m=get(a)
    if m['uncertain']or m['active']is not None:raise ValueError('No apparatus pause/restart over an uncertain or active transaction')
    m['enabled']=enabled;m['last_tick']=int(a.tick);_save(a,m)
    return {'external_bridge_enabled':enabled,'native_tick':int(a.tick),'native_memory_reset':False,'operator_change_not_learned_regulation':True}
def status(a,directory):
    m=get(a)
    return {k:m[k]for k in('version','series','history','arm','enabled','episode','resources','guard_until','returns','busy_returns','exhausted_returns','close_signatures','false_close_signatures','work_frames','training_completed','training_anchor','uncertain','log_count','log_chain_sha256')}
def extend_retention(a,directory):
    """Two new external opportunities, no Native reconstruction or memory edit."""
    m=get(a)
    if m['uncertain']or m['active']is not None or m['episode']!=len(m['fixtures'])or m.get('retention_extension'):raise ValueError('Only once after a completed stable bank, never reset progress')
    rows=[{'public':{'left':13,'right':5},'peripheral_active':True,'warning_offered':True,'warning_lead':128,'device_wiring':'normal'}, {'public':{'left':7,'right':16},'peripheral_active':True,'warning_offered':True,'warning_lead':195,'device_wiring':'normal'}]
    home=Path(directory)/FOLDER;start=len(m['fixtures'])
    for j,row in enumerate(rows):
        i=start+j;payload=hashlib.sha256(('PI02R04 work '+str(i)).encode('ascii')).digest()*2;file='%04d.bin'%i
        with(home/'reservoir'/file).open('xb')as out:out.write(payload)
        m['resource_bank'].append({'episode':i,'file':file,'bytes':64,'sha256':digest(payload)})
        m['fixtures'].append(row)
    m['retention_extension']={'tick':int(a.tick),'new_environment_opportunities':2,'Native_content_reintroduced':False}
    _record(m,directory,{'kind':'RETENTION_BANK_EXTENDED',**m['retention_extension']});_save(a,m)
    return m['retention_extension']
def operational_dependencies(a,directory):
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:return {'R04_not_admitted':True}
    m=get(a);home=Path(directory)/FOLDER
    for item in m['resource_bank']:
        path=home/'reservoir'/item['file']
        if not path.is_file()or digest(path.read_bytes())!=item['sha256']:raise ValueError('Missing/altered R04 reservoir')
    for item in m['collected']:
        path=home/'collected'/item['file']
        if not path.is_file()or digest(path.read_bytes())!=item['sha256']:raise ValueError('Missing/altered actual R04 product')
    spent={x['index']for x in m['spent']}
    for item in m['coupons']:
        path=home/('control_spent'if item['index']in spent else'control_stock')/item['file']
        if not path.is_file()or digest(path.read_bytes())!=item['sha256']:raise ValueError('Missing/altered actual control packet')
    expected={'reservoir':{x['file']for x in m['resource_bank']},'collected':{x['file']for x in m['collected']},'control_spent':{x['file']for x in m['spent']},'control_stock':{x['file']for x in m['coupons']if x['index']not in spent}}
    for folder,names in expected.items():
        if {x.name for x in(home/folder).iterdir()if x.is_file()}!=names:raise ValueError('Unindexed R04 artifact; do not reconstruct or replay')
    chain=bytes(32);count=0
    with(home/'eventos.jsonl').open('rb')as f:
        for line in f:
            if json.loads(line)['index']!=count:raise ValueError('R04 journal progress differs from snapshot')
            chain=hashlib.sha256(chain+line).digest();count+=1
    if count!=m['log_count']or chain.hex()!=m['log_chain_sha256']:raise ValueError('R04 world and external journal are not paired')
    return status(a,directory)|{'active_event':None if m['active']is None else{'episode':m['active']['episode'],'q':m['active']['q'],'busy_until':m['active']['busy_until']},'pending_async_job_is_complete_operational_state':True}
def uncertain(a):
    e=dict(a.world.runtime.snapshot_metadata_entries)
    return KEY in e and bool(_decode(e[KEY])['uncertain'])
