"""Explicit external Runtime protocol for repeated U0 contacts.

The official finite order/action convenience APIs are NOT called outside their
published times. Repetition is a new experiment through already declared legal
ports, preserving one world/owner and every receipt (including rejection).
"""
import gzip,hashlib,json,time
from pathlib import Path
import dee_thinking as d
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA_R02/mecanismo_repetible'
OUT.mkdir(parents=True,exist_ok=True)
def put(p,x):
    if p.exists():raise FileExistsError(p)
    b=json.dumps(x,ensure_ascii=False,sort_keys=True).encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def snapshot(s,label):
    p=OUT/(s.identifier+'.'+label+'.deetsnap.gz');proof=s.save_snapshot(p,compress=True)
    return{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'proof':proof}
def native_action(p):return p['state']>0 and p['semantic']==1 and p['s_reg']>7 and p['direction'][0]in(-1,1)and p['direction'][1]in(-1,1)and p['direction'][2]==1
def run(label,repeat_reader=True):
    s=d.IntegratedSession.create(identifier=label);rows=[];initial=snapshot(s,'T0')
    s.experience_order('BA');s.acquire('L01',1,0);s.acquire('L02',-1,0)
    for j in range(5):
        base=j*67
        if j and repeat_reader:s.submit('order.read',7,base+2,probe=True)
        for lane in('left','right'):s.submit('need.actual.'+lane+'.1',17,base+11)
        # Both generic action opportunities are supplied; no host bank choice.
        for name in s.geometry['action_inputs']:s.submit(name,7,base+69,probe=True)
    for tick in sorted({base+t for base in range(0,5*67,67)for t in(5,15,19,70,72)}):
        s.run_until(tick);rows.append({'tick':tick,'observation':s.observe(),'receipts':s.receipts()})
    results=[]
    for j in range(5):
        tick=j*67+72;frame=next(r for r in rows if r['tick']==tick);sites=frame['observation']['sites']
        acts={name:p for name,p in sites.items()if name.startswith('action.')and native_action(p)}
        questions=next(r for r in rows if r['tick']==j*67+19)['observation']['sites']
        qs={name:p for name,p in questions.items()if name.startswith('question.')and p['state']>0 and p['semantic']==1 and p['s_reg']>13 and p['direction']in([-1,0,0],[1,0,0])}
        results.append({'round':j,'action_tick':tick,'native_questions':qs,'native_actions':acts})
    final=snapshot(s,'T'+str(s.tick));result={'schema':'MA02.U0.repeatable.pilot.1','identifier':s.identifier,'new_T0':True,'N':67,'repeat_order_reader':repeat_reader,'preparation':'Official IntegratedSession unchanged. New external repeated-port protocol, not official extension of order/action API contract.','initial_snapshot':initial,'final_snapshot':final,'geometry':s.geometry,'rows':rows,'rounds':results,'receipts':s.receipts(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'engine_import':d.__file__}
    put(OUT/(label+'.json.gz'),result)
    print(json.dumps({'label':label,'tick':s.tick,'rounds':[{'round':r['round'],'questions':list(r['native_questions']),'actions':{k:v['direction']for k,v in r['native_actions'].items()}}for r in results]},ensure_ascii=False),flush=True)
if __name__=='__main__':
    put(OUT/'PROTOCOLO_PILOTO_REPETIBLE.json',{'before_first_tick_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'hypothesis':'Native own-memory ring phaseN67 can support repeated comparison/question/use when new actuals and both action resources are scheduled at corresponding phases. An additional body reader may or may not be needed.','arms':'new BA U0 taughtL01+/L02-: repeat order.read every67 vs only initial reader. Both receive five currentactual+ and both generic action resources, same fixed observer.','horizon':340,'reader':'all question branches at19+67j and both action sites72+67j. Transformed action requires SEM1,state>0,s_reg>7,dx±1,dy±1,dz1. No target input or host-selected bank.','status':'exploratory finite screen; all failures retained; not declared a reusable function before actual result'})
    run('MA02_U0_REPEAT_READ',True);run('MA02_U0_SINGLE_READ',False)
