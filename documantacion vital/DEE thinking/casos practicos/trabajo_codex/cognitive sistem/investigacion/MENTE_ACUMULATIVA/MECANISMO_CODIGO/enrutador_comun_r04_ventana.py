"""R04 prospective reader revision: fixed RAW-change window over all hubs.
No token/target enters the reader; clock-only changes do not count arrivals.
The observer does not feed any selection or answer back into the DEE world.
"""
import importlib.util,json,time,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('common_r02_exact',HERE/'enrutador_comun_sin_giros.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.N=67;b.I=(33,33,33);b.V=[(1,0,0),(0,1,0),(1,1,0),(-1,1,0)]
class WindowCommon(b.Common):
    def query(self,i,t):
        receipt=self.send('common.token.'+str(i),b.I,b.V[i],5,t)
        self.world.run_until(t+2);pre=[self.observe(b.add(b.I,v,3))for v in b.V]
        self.world.run_until(t+3);post=[self.observe(b.add(b.I,v,3))for v in b.V]
        applied=b.exact_receipt(self.world.runtime.receipt(receipt.id))['status']=='applied'
        candidates=[];stale=[]
        for j,(p0,p1)in enumerate(zip(pre,post)):
            qualifies=p1['state']>0 and p1['semantic']==1 and p1['direction'][:2]==list(b.V[j][:2])and p1['direction'][2]in(-1,1)
            if qualifies:
                row={'site':p1['site'],'sign':p1['direction'][2],'raw_pre':p0['raw'],'raw_post':p1['raw']}
                (candidates if p0['raw']!=p1['raw'] else stale).append(row)
        decoded=candidates[0]['sign']if applied and len(candidates)==1 else None
        row={'kind':'query','request_token':i,'input_tick':t,'tick':t+3,'entry_applied':applied,'pre_fixed_panel':pre,'post_fixed_panel':post,'fresh_candidates':candidates,'stale_candidates_excluded':stale,'decoded_sign':decoded,'reader':'fixed all hubs, require RAW(notclock)change between q+2 andq+3; one candidate and admitted entry; no request token or expected sign used'}
        self.rows.append(row);return row
    def export(self,initial,final):
        receipts=[{**r,'receipt':b.exact_receipt(self.world.runtime.receipt(r['id']))}for r in self.requests]
        result={'label':self.label,'geometry':{'N':b.N,'common_input':b.I,'token_directions':b.V,'passive_panel':[b.add(b.I,v,3)for v in b.V]},'initial':initial,'final':final,'rows':self.rows,'receipts':receipts,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Prepared physical token addressing plus new EXTERNAL passive arrival observer. Contents can be learned; reader is not capacity of participant and does not trigger action.'}
        b.put(b.OUT/(self.label+'.json.gz'),result);return result
def run(label,signs,mode='paired'):
    s=WindowCommon(label);initial=s.save('T0')
    for i in range(3):s.teach(i,signs[i],i*b.N,mode)
    for q,i in enumerate((2,0,1),start=3):s.query(i,q*b.N)
    s.teach(3,signs[3],6*b.N,mode);before_retention=s.save('T405_BEFORE_RETENTION')
    for q,i in enumerate((3,1,0,2),start=7):s.query(i,q*b.N)
    final=s.save('T'+str(s.tick));s.export(initial,final)
    print(json.dumps({'label':label,'tick':s.tick,'queries':[{k:r[k]for k in('request_token','decoded_sign','tick','entry_applied')}for r in s.rows if r['kind']=='query']},ensure_ascii=False),flush=True)
if __name__=='__main__':
    b.put(b.OUT/'PROTOCOLO_ENRUTADOR_R04_VENTANA.json',{'before_run_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'geometry':'exact prospective R03 N67 geometry, new T0 lives (not rewound R03)','reader_frozen':'all4hubs atq+2 andq+3. Valid new native signature requires raw_pre!=raw_post, state>0semantic1, nativeXYmatchesitsphysicalhub andZ±1; exactlyonecandidate and entryreceiptapplied. No target or requestedtoken passed into read decision. Clock-only difference ignored. No observer feedback to DEE.', 'criterion':'3/3firstuse,4/4firstafterfourth; retain failure/reject denominators. Any success limited prepared routing, acquired association and external arrival observation, not action or learned routing policy.', 'arms':'paired(+,-,+,-), opposite(-,+,-,+),no_event(+,-,+,-); samefuturequeries', 'scope':'one bounded observer correction after R03 stale-positive ambiguity, not posthoc reinterpretation of R03 success'})
    run('MA_COMMON_R04_PAIRED',[1,-1,1,-1]);run('MA_COMMON_R04_OPPOSITE',[-1,1,-1,1]);run('MA_COMMON_R04_NOEVENT',[1,-1,1,-1],'no_event')
