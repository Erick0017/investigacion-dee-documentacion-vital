"""Prepared common access repair, never a content-specific answer or policy."""
from app.native_tools import observe,physical
from . import delayed_social as social,ic_native_core as core,ic_external as external

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
