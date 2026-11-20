"""Prospective reserved U0 acquisition, order contrast, retention and sham.
This uses only the frozen official IntegratedSession descriptor/protocol.
"""
import gzip,hashlib,json,time
from pathlib import Path
import dee_thinking as d
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA/mecanismo'
def put(p,x):
    if p.exists():raise FileExistsError(p)
    b=json.dumps(x,ensure_ascii=False,sort_keys=True).encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def run(label,order,signs,mode='paired',revision='treatment'):
    s=d.IntegratedSession.create(identifier=label);rows=[]
    def record(op,extra=None):rows.append({'operation':op,'tick':s.tick,'detail':extra,'physical':s.observe(),'receipts':s.receipts()})
    def snap(label):
        p=OUT/(s.identifier+'.'+label+'.deetsnap.gz');proof=s.save_snapshot(p,compress=True)
        return{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'proof':str(proof)}
    initial=snap('T0')
    s.experience_order(order);s.consequence(1);s.action();s.teach_form()
    for form,sign in zip(('L03','L04','L05'),signs[:3]):s.acquire(form,sign,0,mode=mode)
    for t in(3,5,15,19,70,72,75):s.run_until(t);record('native_chain_boundary')
    first=s.query(['L04','L05','L03'],134);record('first_three_use',first)
    s.acquire('L06',signs[3],201,mode=mode);s.run_until(204);record('fourth_acquired')
    retention=s.query(['L05','L03','L06','L04'],268);record('first_retention',retention)
    s.revise('L03',-signs[0],402,method='double_teacher',mode=revision);s.run_until(405);record('revision',{'mode':revision})
    updated=s.query(['L06','L03','L04','L05'],469);record('first_use_after_update',updated)
    final=snap('T472')
    result={'schema':'MA.U0.reserved.1','identifier':s.identifier,'new_T0':True,'parent':None,'order':order,'mode':mode,'revision_mode':revision,'geometry':s.geometry,'expected_for_evaluator_only':dict(zip(('L03','L04','L05','L06'),signs)),'initial_snapshot':initial,'final_snapshot':final,'rows':rows,'engine':d.__file__,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Four accumulated directional associations, upper native order/comparison/question/action; lower addresses externally requested, no autonomous four-procedure selection.'}
    put(OUT/(s.identifier+'.json.gz'),result)
    print(json.dumps({'life':s.identifier,'first':[(r['form'],r['value'],r['status'])for r in first['responses']],'retention':[(r['form'],r['value'],r['status'])for r in retention['responses']],'revision':[(r['form'],r['value'],r['status'])for r in updated['responses']]},ensure_ascii=False),flush=True)
if __name__=='__main__':
    put(OUT/'PROTOCOLO_RESERVA_U0.json',{'before_run_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'reader':'official read_form_response unchanged, panel order permuted from pilot; no teacher at first-use probes','arms':[['MA_U0_RES_AB','AB',[1,1,-1,-1],'paired','treatment'],['MA_U0_RES_BA','BA',[-1,-1,1,1],'paired','treatment'],['MA_U0_RES_OMIT','AB',[1,1,-1,-1],'no_event','offpath_sham'],['MA_U0_RES_SHAM','AB',[1,1,-1,-1],'paired','offpath_sham']],'criterion':'3/3 first learned forms; 4/4 first after fourth; updatedL03 opposite while other3 preserve; no_event not credit content; record/sham may fail genuine update','chain_snapshots_at':[3,5,15,19,70,72,75],'scope':'NO claim all four associations feed one native selector. Addresses prepared, operator requested; U0 comparison-conditioned question distinguished from these addressed queries.'})
    for args in [('MA_U0_RES_AB','AB',[1,1,-1,-1]),('MA_U0_RES_BA','BA',[-1,-1,1,1]),('MA_U0_RES_OMIT','AB',[1,1,-1,-1],'no_event','offpath_sham'),('MA_U0_RES_SHAM','AB',[1,1,-1,-1],'paired','offpath_sham')]:run(*args)
