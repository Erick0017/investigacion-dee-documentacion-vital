"""Finite persistent PI11 host environment, not a DEE policy or Native memory.

Pure standard library. No engine, process, network, shell or cognitive lookup.
The caller supplies actual observations/outputs. Only fixed environmental laws
consume permissions, occupy access, refresh a certificate and move resource bytes.
All paths are confined to the explicit home. One writer is required by contract.
"""
from pathlib import Path
import hashlib,json,os

VERSION='DEE.PI11.persistent_habitat.R01'
FOLDER='PI11_HABITAT_R01'
DEFAULTS={'stock':24,'initial_permissions':4,'permission_cap':4,
          'replenish_ticks':4687,'query_busy_ticks':233,'certificate_ticks':4200}

def need(ok,why):
    if not ok:raise ValueError(why)

def sha(data):return hashlib.sha256(data).hexdigest()

def encoded(value):return (json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf8')

def _root(home):
    base=Path(home).absolute();need(base.is_dir(),'Explicit existing artifact home required')
    p=base/FOLDER
    for a in(p,*p.parents):
        need(not a.is_symlink()and not(getattr(a.lstat(),'st_file_attributes',0)&1024)if a.exists()else not a.is_symlink(),'No linked/reparse environment paths')
    return base.resolve(strict=True)/FOLDER

def _read(p):return json.loads(p.read_text('utf-8-sig'))

def _new(p,value):
    with p.open('xb')as f:f.write(encoded(value));f.flush();os.fsync(f.fileno())

def _replace(p,value):
    temporary=p.with_name(p.name+'.next')
    need(not temporary.exists(),'Partial environmental write preserved; reconcile before continuing')
    with temporary.open('xb')as f:f.write(encoded(value));f.flush();os.fsync(f.fileno())
    os.replace(temporary,p)

def _config(protocol):
    need(isinstance(protocol,dict),'Protocol dictionary required')
    cfg={**DEFAULTS,**protocol.get('habitat',{})}
    need(set(cfg)==set(DEFAULTS)and all(type(v)is int and v>0 for v in cfg.values()),'Exact finite positive habitat parameters')
    need(cfg['stock']<=32 and cfg['initial_permissions']<=cfg['permission_cap']<=32,'Finite stock<=32 and initial permissions<=cap<=32')
    rows=protocol.get('events')
    need(isinstance(rows,list)and rows and len(rows)<=128,'Finite exogenous events required')
    previous=-1
    for row in rows:
        need(isinstance(row,dict)and set(row)=={'at_offset','mode','cue'},'Event must contain only at_offset/mode/cue')
        need(type(row['at_offset'])is int and row['at_offset']>previous,'Events strictly increase by Native offset')
        need(row['mode']in('need','bypass')and row['cue']in('z','x','none'),'Fixed physical cue and availability modes')
        previous=row['at_offset']
    need(rows[0]['at_offset']==0,'Environment begins at offset0')
    return cfg

def init(home,protocol,start_tick):
    """Install one NEW supply/clock. Never reset or overwrite an existing habitat."""
    cfg=_config(protocol);need(type(start_tick)is int and start_tick>=0,'Actual initial Native tick')
    root=_root(home);need(not root.exists(),'Habitat already exists; no resource/clock reset')
    root.mkdir();(root/'reservoir').mkdir();(root/'delivered').mkdir();(root/'offers').mkdir();(root/'intents').mkdir()
    _new(root/'PROTOCOLO.json',protocol)
    slots=[]
    for n in range(cfg['stock']):
        name='slot_%02d.bin'%n;data=bytes(64)
        with(root/'reservoir'/name).open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
        slots.append({'id':n,'name':name,'delivered':False,'payload_sha256':sha(data),'preparations':0})
    manifest={'schema':VERSION+'.manifest','protocol_sha256':sha(encoded(protocol)),'config':cfg,'start_tick':start_tick,
              'resource_law':'One common reservoir. Before an offer the next unconsumed slot is transduced to actual sampled RAW little-endian8bytes repeated8; failures retain the slot. Successful selected-bin transfer consumes it.',
              'external_accounting':'Permissions and certificates are host-environment state, not energy/metabolism or Native learned memory.'}
    _new(root/'MANIFIESTO.json',manifest)
    state={'schema':VERSION+'.state','start_tick':start_tick,'tick':start_tick,'replenishment_epoch':0,
           'permissions':cfg['initial_permissions'],'occupied_until':start_tick,'certificate':None,'slots':slots,
           'next_ordinal':0,'open_offer':None,'prepared':0,'completed':0,'queries_granted':0,'queries_denied':0,
           'physical_deliveries':0,'attributed_deliveries':0,'FI_refreshes':0,'certificate_reuses':0,'replenishments':0}
    _new(root/'ESTADO.json',state)
    return status(home)

def _load(home):
    root=_root(home);need(root.is_dir(),'Habitat has not been installed')
    manifest=_read(root/'MANIFIESTO.json');protocol=_read(root/'PROTOCOLO.json');state=_read(root/'ESTADO.json')
    need(manifest['schema']==VERSION+'.manifest'and state['schema']==VERSION+'.state','Own exact schemas')
    need(sha(encoded(protocol))==manifest['protocol_sha256']and _config(protocol)==manifest['config'],'Protocol/config integrity')
    need(state['start_tick']==manifest['start_tick'],'Persistent origin differs')
    return root,manifest,protocol,state

def _at(protocol,state,tick):
    offset=tick-state['start_tick'];result=protocol['events'][0]
    for row in protocol['events']:
        if row['at_offset']>offset:break
        result=row
    return {**result,'absolute_start_tick':state['start_tick']+result['at_offset'],'tick':tick,'elapsed_ticks':offset,
            'auditor_environment_not_actor_input':True}

def _advance(state,cfg,tick):
    need(type(tick)is int and tick>=state['tick'],'No environmental rewind; actual Native ticks must be monotone')
    epoch=(tick-state['start_tick'])//cfg['replenish_ticks'];count=epoch-state['replenishment_epoch']
    if count:
        state['permissions']=min(cfg['permission_cap'],state['permissions']+count)
        state['replenishments']+=count;state['replenishment_epoch']=epoch
    state['tick']=tick

def status(home):
    """Passive JSON read only; does not advance clocks or replenish."""
    _,m,_,s=_load(home)
    return {**s,'remaining_stock':sum(not x['delivered']for x in s['slots']),'config':m['config'],'new_Native_ticks':0,
            'certificate_is_external':True}

def advance(home,tick):
    """Apply all elapsed fixed-law replenishments, including periods without action."""
    root,m,_,s=_load(home);_advance(s,m['config'],tick);_replace(root/'ESTADO.json',s)
    return status(home)

def environment_at(home,tick):
    """Auditor/environment scheduler only; mode/cue are never policy inputs."""
    advance(home,tick);_,_,p,s=_load(home);return _at(p,s,tick)

def can_access(home,tick):
    advance(home,tick);_,_,_,s=_load(home)
    return {'tick':tick,'allowed':s['permissions']>0 and tick>=s['occupied_until'],
            'permissions':s['permissions'],'occupied_until':s['occupied_until'],'fixed_transducer_rule_not_policy':True}

def _sample(sample,q1tick):
    need(isinstance(sample,dict),'Actual Native observation required')
    value=sample['raw'];need(type(value)is int or(isinstance(value,str)and value.isdecimal()),'Exact uint64 RAW, not a target')
    raw=int(value);need(0<=raw<2**64,'RAW uint64 range')
    ds=[(raw>>n)&15 for n in(48,52,56)];direction=[v-16 if v&8 else v for v in ds]
    decoded={'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,'semantic':raw>>60,'direction':direction}
    for key,value in decoded.items():need(key not in sample or sample[key]==value,'Observation mismatch for '+key)
    if raw==0:bit=0
    elif decoded['state']>0 and decoded['semantic']==1 and direction==[0,0,1]:bit=1
    elif decoded['state']>0 and decoded['semantic']==1 and direction==[1,0,0]:bit=0
    else:raise ValueError('Unknown/NULL preview signature, no expected-bit fallback')
    sampletick=sample.get('tick',q1tick-1);need(type(sampletick)is int and sampletick<q1tick,'Sample must precede actual query')
    return raw,bit,sampletick,decoded

def prepare_offer(home,ordinal,sample,q1tick):
    """Prepare from actual current RAW; availability comes from tick, never ordinal."""
    root,m,p,s=_load(home)
    need(type(ordinal)is int and ordinal==s['next_ordinal']and s['open_offer']is None,'One fresh sequential offer; no retry or overlapping intent')
    need(type(q1tick)is int and q1tick>s['tick'],'Actual future query tick required')
    raw,bit,sampletick,decoded=_sample(sample,q1tick);need(sampletick>=s['tick'],'Sample cannot precede current habitat tick')
    _advance(s,m['config'],sampletick);env=_at(p,s,sampletick)
    slot=next((row for row in s['slots']if not row['delivered']),None);need(slot is not None,'Finite resource stock exhausted')
    data=raw.to_bytes(8,'little')*8;path=root/'reservoir'/slot['name']
    need(path.is_file()and sha(path.read_bytes())==slot['payload_sha256'],'Common reservoir resource missing/changed')
    offer={'schema':VERSION+'.offer','ordinal':ordinal,'q1_tick':q1tick,'sample_tick':sampletick,'sample':sample,
           'decoded':decoded,'actual_preview_bit':bit,'available_bin':0 if env['mode']=='bypass'else bit,
           'environment':env,'slot_id':slot['id'],'payload_sha256':sha(data),'bytes':64,'access':None,
           'technical_register_not_Native_memory':True,'frozen_mode_at_offer':True}
    _new(root/'intents'/('prepare_%04d.json'%ordinal),offer)
    temporary=path.with_name(path.name+'.next');need(not temporary.exists(),'Partial reservoir write preserved')
    with temporary.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
    os.replace(temporary,path);slot.update(payload_sha256=sha(data),preparations=slot['preparations']+1)
    _new(root/'offers'/('offer_%04d.json'%ordinal),offer)
    s.update(open_offer=ordinal,prepared=s['prepared']+1);_replace(root/'ESTADO.json',s)
    return offer

def _offer(root,s,ordinal):
    need(type(ordinal)is int and s['open_offer']==ordinal,'Exact active prepared offer required')
    return _read(root/'offers'/('offer_%04d.json'%ordinal))

def request_access(home,ordinal,actualnativegate,questionphysicalvalid,tick):
    """Charge only actual admitted material query. can_access is its preflight."""
    root,m,_,s=_load(home);offer=_offer(root,s,ordinal)
    need(type(questionphysicalvalid)is bool,'Explicit actual physical signature validity')
    need(actualnativegate is None or type(actualnativegate)is int and actualnativegate in(-1,0,1),'Native gate is -1/0/+1 or NULL')
    need(offer['access']is None,'Access was already adjudicated; no silent repeated query')
    need(not questionphysicalvalid or actualnativegate==1,'Material question cannot be attributed to absent Native positive gate')
    _advance(s,m['config'],tick);capacity=s['permissions']>0 and tick>=s['occupied_until']
    allowed=actualnativegate==1 and questionphysicalvalid and capacity
    need(not questionphysicalvalid or capacity,'Material question occurred despite blocked fixed port; reconcile instrumentation')
    row={'tick':tick,'native_gate':actualnativegate,'question_physical_valid':questionphysicalvalid,
         'capacity_available':capacity,'allowed':allowed,'permissions_before':s['permissions'],'occupied_until_before':s['occupied_until']}
    _new(root/'intents'/('access_%04d.json'%ordinal),row)
    if allowed:s['permissions']-=1;s['occupied_until']=tick+m['config']['query_busy_ticks'];s['queries_granted']+=1
    elif actualnativegate==1:s['queries_denied']+=1
    offer['access']=row;_replace(root/'offers'/('offer_%04d.json'%ordinal),offer);_replace(root/'ESTADO.json',s)
    return row

def execute(home,ordinal,route,q1valid,commandvalid,actualFIchoice_orNone,do_refresh_bool,tick):
    """Apply observed route. A real fresh FI+ renews a shared finite certificate.

    do_refresh_bool is the fixed transduction of a Native output, not a desired
    result. No refresh requires FI=None and may use an unexpired earlier result.
    """
    root,m,_,s=_load(home);offer=_offer(root,s,ordinal)
    need(route is None or type(route)is int and route in(0,1),'Actual observed route or silence')
    need(type(q1valid)is bool and type(commandvalid)is bool and type(do_refresh_bool)is bool,'Explicit physical validity/refresh flags')
    need(actualFIchoice_orNone is None or type(actualFIchoice_orNone)is int and actualFIchoice_orNone in(-1,0,1),'Actual FI result -1/0/+1 or NULL')
    need(do_refresh_bool or actualFIchoice_orNone is None,'No FI result can be supplied for an omitted interaction')
    need(offer['access']is not None,'Access decision must precede action even for NoQuery')
    need(not commandvalid or route is not None,'Valid command requires a physical route')
    _advance(s,m['config'],tick)
    cert_before=s['certificate'];fresh=do_refresh_bool and actualFIchoice_orNone==1
    if fresh:
        s['certificate']={'acquired_tick':tick,'valid_until':tick+m['config']['certificate_ticks'],
                          'actual_FI_choice':actualFIchoice_orNone,'source_ordinal':ordinal,
                          'result_sha256':sha(encoded({'tick':tick,'ordinal':ordinal,'actual_FI_choice':actualFIchoice_orNone}))}
        s['FI_refreshes']+=1
    valid_cert=s['certificate']is not None and tick<=s['certificate']['valid_until']
    # A physically failed refresh is a failed present interaction, not rescued
    # by silently replacing its result with the earlier certificate.
    work_ok=bool(fresh if do_refresh_bool else valid_cert)
    selected=route==offer['available_bin']if commandvalid else False
    physical=bool(selected and work_ok);attributed=bool(physical and q1valid)
    row={'schema':VERSION+'.result','ordinal':ordinal,'tick':tick,'actual_route':route,'q1_valid':q1valid,'command_valid':commandvalid,
         'do_refresh':do_refresh_bool,'actual_FI_choice':actualFIchoice_orNone,'fresh_FI_plus':fresh,
         'certificate_before':cert_before,'certificate_after':s['certificate'],'certificate_valid':valid_cert,'FI_work_satisfied':work_ok,
         'available_bin':offer['available_bin'],'mode':offer['environment']['mode'],'selected_bin_had_resource':selected,
         'physical_delivered':physical,'attributed_useful':attributed,'actual_failed':not attributed,'product':None,
         'permissions_before_delivery':s['permissions'],'payload_sha256':offer['payload_sha256']}
    _new(root/'intents'/('execute_%04d.json'%ordinal),row)
    slot=s['slots'][offer['slot_id']];source=root/'reservoir'/slot['name']
    need(not slot['delivered']and source.is_file()and sha(source.read_bytes())==offer['payload_sha256'],'Actual shared resource integrity before effect')
    if physical:
        target=root/'delivered'/('resource_%04d_slot_%02d.bin'%(ordinal,slot['id']))
        need(not target.exists(),'Destination exists; no duplicate physical delivery')
        os.replace(source,target);need(target.stat().st_size==64 and sha(target.read_bytes())==offer['payload_sha256'],'Actual delivered file readback')
        slot['delivered']=True;s['physical_deliveries']+=1;s['permissions']=min(m['config']['permission_cap'],s['permissions']+1)
        if attributed:s['attributed_deliveries']+=1
        if not do_refresh_bool:s['certificate_reuses']+=1
        row['product']={'relative_file':str(target.relative_to(root)).replace('\\','/'),'bytes':64,'sha256':sha(target.read_bytes())}
    row.update(permissions_after_delivery=s['permissions'],remaining_stock=sum(not x['delivered']for x in s['slots']))
    _new(root/'offers'/('result_%04d.json'%ordinal),row)
    s.update(open_offer=None,next_ordinal=ordinal+1,completed=s['completed']+1);_replace(root/'ESTADO.json',s)
    return row

def verify(home):
    """Passive resource/counter/hash verification; never acts or replenishes."""
    root,m,_,s=_load(home);delivered=0
    for slot in s['slots']:
        if slot['delivered']:delivered+=1;need(not(root/'reservoir'/slot['name']).exists(),'Consumed slot remains in reservoir')
        else:need((root/'reservoir'/slot['name']).is_file()and sha((root/'reservoir'/slot['name']).read_bytes())==slot['payload_sha256'],'Unconsumed reservoir mismatch')
    need(delivered==s['physical_deliveries'],'Delivery count differs from common stock')
    for n in range(s['completed']):
        result=_read(root/'offers'/('result_%04d.json'%n))
        if result['physical_delivered']:
            p=root/result['product']['relative_file'];need(p.is_file()and p.stat().st_size==64 and sha(p.read_bytes())==result['product']['sha256'],'Delivered actual payload missing/changed')
    return {'schema':VERSION+'.verification','verified':True,'completed':s['completed'],'remaining_stock':len(s['slots'])-delivered,
            'physical_deliveries':delivered,'protocol_sha256':m['protocol_sha256'],'new_Native_ticks':0}
