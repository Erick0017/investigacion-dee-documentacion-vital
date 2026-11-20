"""Prepared common access repair, never a content-specific answer or policy."""
from app.native_tools import observe,physical
from . import delayed_social as social,ic_native_core as core,ic_external as external

def _access_banks(p,bridge,support):
    if support not in('original','recovered'):raise ValueError('Explicit original/recovered support geometry required, not a response-selected sign')
    if support=='recovered':
        alt=[{**b,'target':core.move(b['target'],(0,0,-1),3)}for b in p['plan']['banks']]
        declared=all(any(z['sign']==b['sign']and z['target']==b['target']for z in bridge.get('social_ports',[]))for b in alt)
        if not bridge.get('generic_access_recovery')and not declared:raise ValueError('No declared zminus3 parallel geometry in this life; geometry does not by itself certify acquired content')
        return alt
    if p.get('generic_access_recovery')or bridge.get('generic_access_recovery'):
        raise ValueError('OUT_OF_DOMAIN for original support after zminus3 recovery; request the declared recovered geometry explicitly, never infer it from the expected sign')
    return list(p['plan']['banks'])

def preposition_social_access(a,*,name,anchor_tick=None,sham=False,enabled=True,support='original',layers=1):
    """Prepared generic resources BEFORE a loss, not an if-failure repair.

    Both prospective paths/decoders are fixed symmetrically. The native zero
    resources carry no acquired sign. They can circulate until a later native
    encounter consumes/transforms them; no observer triggers their use.
    P0 anatomy/supply, at most P1 history-conditioned use, never P2 by name.
    """
    import re
    if not isinstance(name,str)or not re.fullmatch(r'[A-Za-z0-9_.-]{1,48}',name):raise ValueError('Explicit new short preparation ID required')
    if type(sham)is not bool or type(enabled)is not bool:raise ValueError('Explicit physical controls required')
    if type(layers)is not int or layers not in(1,2):raise ValueError('Only the validated finite one/two-layer preparations are admitted')
    if layers==2 and support!='original':raise ValueError('Two-layer extension is validated only from original support; no silent extrapolation to a third recovered geometry')
    p=social.get(a);bridge=external.saved(a)
    if not p or not bridge or bridge['readout']!='magnitude':raise ValueError('Existing original social support and magnitude bridge required; no world or learned content is created')
    banks=_access_banks(p,bridge,support)
    if bridge.get('prepositioned_social_access'):raise ValueError('A prepositioned resource history already exists; no silent reseeding or replacement')
    if anchor_tick is None:anchor_tick=70+67*max(0,(a.tick+34-70+66)//67)
    if type(anchor_tick)is not int or anchor_tick%67!=3 or anchor_tick-30<a.tick:
        raise ValueError('Future fixed phase3 anchor with at least30ticks of lead required; no response-dependent timing')
    parallel=list(bridge.get('social_ports')or p['plan']['banks']);rr=[];layout=[]
    for b in banks:
        for layer in range(1,layers+1):
            alt={**b,'target':core.move(b['target'],(0,0,-1),3*layer),'access':'fixed_prepositioned_alternative_layer'+str(layer)}
            if not any(z['sign']==alt['sign']and z['target']==alt['target']for z in parallel):parallel.append(alt)
            target=core.move(core.move(b['target'],(b['sign'],0,-1),3),(0,0,-1),3*(layer-1))
            site=core.move(target,(0,0,1),-33)
            if sham:site=core.move(site,(0,1,0),19)
            port='C02.preposition.'+name+'.'+str(b['sign'])+(''if layer==1 else'.layer'+str(layer))
            if enabled:rr.append(core.submit(a,port,site,(0,0,1),anchor_tick-30,0))
            layout.append({'bank':b['sign'],'layer':layer,'anchor_meeting_site':target,'zero_launch_site':site,'launch_tick':anchor_tick-30,'first_anchor_meeting_tick':anchor_tick+3})
    spec={'name':name,'prepared_at_tick':a.tick,'anchor_tick':anchor_tick,'support':support,'layers':layers,'base_banks':banks,'sham':sham,'enabled':enabled,'requests':rr,'layout':layout,
          'parallel_ports':parallel,'classification':'P0 prepositioned generic access opportunities; native history-conditioned use is P1 only when contrasted. Not a learned loss detector or P2/R2.',
          'renewal':'Finite two zero-load resources per layer; no automatic replenishment and no promise after they are consumed or transformed.'}
    bridge['social_ports']=parallel;bridge['prepositioned_social_access']=spec;external.store(a,bridge)
    return spec

def query_social_access(a,*,name,support='original',query_tick=None,scope='base'):
    """One common material query, not an observer or a repair decision.

    It sends the same zero-load Z- probe to both declared signs, with no new B
    input, old sign or correct answer. A later interaction may use previously
    prepared resources; no host callback runs after detecting a failed read.
    """
    import re
    if not isinstance(name,str)or not re.fullmatch(r'[A-Za-z0-9_.-]{1,48}',name):raise ValueError('Explicit new common query ID')
    p=social.get(a);bridge=external.saved(a)
    if not p or not bridge:raise ValueError('Existing social world and bridge required')
    banks=_access_banks(p,bridge,support)
    if scope not in('base','base-and-first'):raise ValueError('Explicit bounded query footprint required')
    if scope=='base-and-first':
        prep=bridge.get('prepositioned_social_access')
        if not prep or prep.get('layers',1)!=2 or support!='original':raise ValueError('The two-input-plane query requires the declared original two-layer preparation')
        banks=[z for b in banks for z in(b,{**b,'target':core.move(b['target'],(0,0,-1),3)})]
    if query_tick is None:query_tick=70+67*max(0,(a.tick+8-70+66)//67)
    if type(query_tick)is not int or query_tick%67!=3 or query_tick-3<a.tick:raise ValueError('Future common phase3 query required')
    if any(q['name']==name for q in bridge.get('common_access_queries',[])):raise ValueError('Query already declared; no hidden duplicate dose')
    rr=[]
    for index,b in enumerate(banks):
        suffix=''if scope=='base'else'.plane'+str(index//1)
        rr.append(core.arrive(a,'C02.common_access_query.'+name+'.'+str(b['sign'])+suffix,b['target'],(0,0,-1),query_tick,0))
    query={'name':name,'support':support,'scope':scope,'query_tick':query_tick,'base_banks':banks,'requests':rr,'operator_initiated_query':True,
           'no_repair_command_after_failed_read':True,'fixed_content_free_probes':True}
    bridge.setdefault('common_access_queries',[]).append(query);external.store(a,bridge)
    return query

def recover_social(a,*,sham=False):
    p=social.get(a)
    if not p or p['plan']['mode']!='no_partner' or a.tick!=p['plan']['end_tick']:raise ValueError('This bounded procedure requires the reached generic no-new-partner query boundary, not an arbitrary failed state')
    if p.get('generic_access_recovery'):raise ValueError('This exact recovery opportunity was already used; do not duplicate doses or silently change the protocol')
    bridge=external.saved(a)
    if not bridge or bridge['readout']!='magnitude':raise ValueError('Declared magnitude+social bridge required; no new world or readout fallback')
    start=a.tick;old_ports=p['plan']['banks'];parallel=list(old_ports);requests=[];locations=[];before=[observe(a.world,b['target'])for b in old_ports]
    for b in old_ports:
        parallel.append({**b,'target':core.move(b['target'],(0,0,-1),3),'access':'fixed_alternative_zminus3'})
        target=core.move(b['target'],(b['sign'],0,-1),3);locations.append({'bank':b['sign'],'target':target})
        if sham:target=core.move(target,(0,1,0),19)
        requests.append(core.arrive(a,'IC01.generic_recovery.T'+str(start)+'.'+str(b['sign']),target,(0,0,1),start+3,0))
    frames=[]
    for t in range(start+1,start+4):
        a.run_until(t);frames.append({'tick':t,'regions':[{'bank':b['bank'],'read':observe(a.world,b['target'])}for b in locations]})
    p['generic_access_recovery']={'start_tick':start,'end_tick':a.tick,'sham':sham,'requests':requests,'parallel_ports':parallel,'classification':'P0 prepared common access transformation; output content depends on acquired physical history, not a learned P2 failure detector'};p['last_tick']=a.tick;social.put(a,p)
    bridge['social_ports']=parallel;bridge['generic_access_recovery']={'start_tick':start,'end_tick':a.tick,'sham':sham,'prepared':True};external.store(a,bridge)
    return{'before':before,'frames':frames,'requests':core.receipts(a,requests),'parallel_ports':parallel,'final':physical(a.world,occupation=True),'scope':'Zero-load inputs at both candidate branches; no old sign, teacher, reference, trained copy or raw edit. Parallel fixed ports are external apparatus, not autonomous selection. Native-only3tick interval is explicit and remains inside the next67tick motor interval.'}
