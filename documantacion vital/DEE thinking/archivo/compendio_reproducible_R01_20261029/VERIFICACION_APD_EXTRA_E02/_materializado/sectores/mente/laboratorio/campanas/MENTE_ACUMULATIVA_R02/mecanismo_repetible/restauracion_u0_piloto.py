"""New explicit request/read/use/return protocol on one official U0 world.
All support pulses are content-blind. Request-route provisioning is operator
prepared P0; it is NOT a learned access policy or a native common-input selector.
"""
import gzip,hashlib,json,time
from pathlib import Path
import dee_thinking as d
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA_R02/mecanismo_repetible';OUT.mkdir(parents=True,exist_ok=True)
def put(p,x):
    if p.exists():raise FileExistsError(p)
    b=json.dumps(x,ensure_ascii=False,sort_keys=True).encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def xyz(p,v,k=1):return tuple((p[i]+k*v[i])%67 for i in range(3))
def snap(s,label):
    p=OUT/(s.identifier+'.'+label+'.deetsnap.gz');proof=s.save_snapshot(p,compress=True)
    return{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'proof':proof}
def specs(s,j,bank):
    R=70+67*j;g=s.geometry;h=tuple(g['banks'][bank]['hub']);dx=g['banks'][bank]['request_direction'];result=[]
    for sign in(-1,1):
        for stage,(offset,dt,v)in enumerate([((3*dx,3*sign,1),3,(-dx,0,-1)),((3*dx,4*sign,1),4,(-dx,0,-1)),((2*dx,5*sign,0),5,(0,0,1)),((0,7*sign,0),7,(dx,0,0))]):
            target=xyz(h,offset);source=xyz(target,v,-3)
            result.append({'name':'MA02.restore.'+bank+'.'+str(sign)+'.'+str(stage),'site':source,'direction':v,'tick':R+dt-3,'load':0,'target':target,'contact_tick':R+dt})
    return result
def run(label,restore='requested',queries=True,values=(1,-1)):
    s=d.IntegratedSession.create(identifier=label);initial=snap(s,'T0');rows=[];sent=[]
    def send(spec):
        name=spec['name']
        if name not in set(s.world.runtime.channel_names):
            c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*spec['site']);c.direction=d.Direction(*spec['direction']);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True
            it=d.InterfaceSpec();it.name=name;it.channel=c;s.world.declare_interface(it)
        r=s.submit(name,spec['load'],spec['tick']);sent.append({**spec,'receipt_id':r['id']})
    s.experience_order('BA');s.consequence(1)
    for form,v in zip(('L01','L02'),values):s.acquire(form,v,0)
    request_order=['left','right','left','right','left']
    for j,bank in enumerate(request_order):
        R=70+67*j
        if j and queries:
            g=s.geometry['banks'][bank];h=tuple(g['hub']);dx=g['request_direction']
            send({'name':'MA02.current.request.'+bank,'site':xyz(h,(dx,0,0),-3),'direction':(dx,0,0),'tick':R-3,'load':37,'role':'Current requested route, no remembered content'})
        for name in s.geometry['action_inputs']:s.submit(name,7,R-1,probe=True)
        banks=[bank]if restore=='requested'else['left','right']if restore=='all'else[]
        unique=set()
        for b in banks:
            for q in specs(s,j,b):
                key=(q['site'],q['direction'],q['tick'])
                if key not in unique:send(q);unique.add(key)
    times=sorted({70+67*j+dt for j in range(5)for dt in(0,2,3,4,5,6,7,8)})
    for tick in times:s.run_until(tick);rows.append({'tick':tick,'physical':s.observe(),'receipts':s.receipts()})
    rounds=[]
    for j,bank in enumerate(request_order):
        R=70+67*j;action=next(r for r in rows if r['tick']==R+2)['physical']['sites'];mem=next(r for r in rows if r['tick']==R)['physical']['sites']
        acts={k:p for k,p in action.items()if k.startswith('action.')and p['state']>0 and p['semantic']==1 and p['s_reg']>7 and p['direction'][0]in(-1,1)and p['direction'][1]in(-1,1)and p['direction'][2]==1}
        rounds.append({'round':j,'requested_bank_prepared':bank,'information_tick':R,'native_banks':{k:p for k,p in mem.items()if k.startswith('bank.')},'actions':acts})
    final=snap(s,'T'+str(s.tick));result={'schema':'MA02.U0.restore.pilot.1','identifier':label,'new_T0':True,'mode':restore,'queries_present':queries,'initial_own_consequences':values,'initial_snapshot':initial,'final_snapshot':final,'rows':rows,'rounds':rounds,'requests':sent,'receipts':s.receipts(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'External prepared request-route provisioning and content-blind both-sign restoration. Content acquired natively, no learned route selection or common input claimed.'}
    put(OUT/(label+'.json.gz'),result)
    print(json.dumps({'label':label,'tick':s.tick,'rounds':[{'round':r['round'],'request':r['requested_bank_prepared'],'actions':{k:p['direction']for k,p in r['actions'].items()}}for r in rounds]},ensure_ascii=False),flush=True)
if __name__=='__main__':
    put(OUT/'PROTOCOLO_RESTAURACION_U0_PILOTO.json',{'before_first_tick_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'schedule':'Initial BA/+ selects left natively. Later explicit prepared current requests right,left,right,left; high banks initially L01+,L02-. Every round actionbothgeneric7 and restorationmarkers0 bothcontent-signs.', 'hypothesis':'Four post-action generic encounters restore the used carrier to its original +/-Y ring and phase; unrequested bank resources may instead interfere.','phases':'memory R=70+67j, actionR+2, turn/resetcontactsR+3,+4,+5,+7, fixed all-bank/all-action reader','arms':'requested-bank restoration, no restoration, all-bank restoration, no new request with requested-bank resources','horizon':346,'scope':'Exploratory new port protocol. Operator chooses generic request identity in advance; not native common selector, not official API extension or learned autonomy. Controls and failures preserved.'})
    run('MA02_U0_RESTORE_REQUESTED','requested');run('MA02_U0_RESTORE_NONE','none');run('MA02_U0_RESTORE_ALL','all');run('MA02_U0_RESTORE_NOQUERY','requested',False)
