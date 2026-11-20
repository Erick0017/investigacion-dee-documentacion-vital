"""Native U0 two-own-bank selector + four lower associations, one Runtime.
The missing link in the first U0 pilot was that its high own banks were empty.
This declared revision teaches them via ordinary experience; it never writes RAW.
"""
import gzip,hashlib,json,time
from pathlib import Path
import dee_thinking as d
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA/mecanismo'
def put(p,x):
    if p.exists():raise FileExistsError(p)
    b=json.dumps(x,ensure_ascii=False,sort_keys=True).encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def run(label,history,actual,values,ownmode='paired'):
    s=d.IntegratedSession.create(identifier=label);rows=[]
    def record(op,extra=None):rows.append({'operation':op,'tick':s.tick,'detail':extra,'physical':s.observe(),'receipts':s.receipts()})
    def snap(label):
        p=OUT/(s.identifier+'.'+label+'.deetsnap.gz');proof=s.save_snapshot(p,compress=True)
        return{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'proof':str(proof)}
    initial=snap('T0');s.experience_order(history);s.consequence(actual);s.action();s.teach_form()
    for form,value in zip(('L01','L02'),values):s.acquire(form,value,0,mode=ownmode)
    for form,value in [('L03',1),('L04',-1),('L05',-1)]:s.acquire(form,value,0)
    for t in(3,5,15,19,20,69,70,71,72,75):
        s.run_until(t);record('chain_boundary')
        if t==20:before_message=snap('T20')
    first=s.query(['L05','L04','L03'],134);record('first_three',first)
    # Name query is all candidates, not a bank selected by expected content.
    names=s.query_form(139);record('post_native_use_opaque_sign',names)
    s.acquire('L06',1,201);s.run_until(204);record('fourth_acquisition')
    panel=s.query(['L06','L04','L03','L05'],268);record('retention_after_fourth',panel)
    s.revise('L03',-1,402,method='double_teacher',mode='treatment');s.run_until(405);record('revision')
    finalpanel=s.query(['L03','L06','L05','L04'],469);record('after_revision',finalpanel)
    final=snap('T472')
    result={'schema':'MA.U0.native_selector.1','life':s.identifier,'N':67,'profile':'u0_integrado_4_5','new_T0':True,'history':history,'actual':actual,'own_values_for_auditor_only':values,'own_experience_mode':ownmode,'initial_snapshot':initial,'message_snapshot_T20':before_message,'final_snapshot':final,'rows':rows,'geometry':s.geometry,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Native comparison-conditioned question selects one of two acquired own banks; physical returned answer combines with common action resources, then later opaque cues. Four lower forms accumulate in same world but remain operator-addressed, not part of autonomous two-bank selector.'}
    put(OUT/(s.identifier+'.json.gz'),result)
    def compact(t):
        r=next(r for r in rows if r['tick']==t and r['operation']=='chain_boundary')
        return{k:v for k,v in r['physical']['sites'].items()if k.startswith(('question.','bank.','action.'))and v['state']}
    print(json.dumps({'life':s.identifier,'question19':compact(19),'banks70':compact(70),'actions72':compact(72),'retention':[(r['form'],r['value'],r['status'])for r in panel['responses']]},ensure_ascii=False),flush=True)
if __name__=='__main__':
    put(OUT/'PROTOCOLO_SELECTOR_U0.json',{'before_run_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'hypothesis':'Acquired order plus current consequence yields native conditional question. Two own high banks taught through experience provide content, then common action supplies produce a native transformed action. Host never chooses question lane, bank answer, action input subset, or later name-cue subset.', 'arms':[['MA_U0_SEL_BA_PLUS','BA',1,[1,-1],'paired'],['MA_U0_SEL_AB_MINUS','AB',-1,[1,-1],'paired'],['MA_U0_SEL_BA_REVERSED','BA',1,[-1,1],'paired'],['MA_U0_SEL_BA_NOOWN','BA',1,[1,-1],'no_event']], 'reader_frozen':'all four question sites at19; both banks70; both action sites72. Native question means exact horizontal ±X direction with noY/Z, not any activity. Native transformed action means exact nonzero X and Y±1 andZ+1, load greater than generic7. Old target not decoderinput.', 'retention':'allfourlowerforms firstuse268/read271, afterrevision469/read472; no targets/teachers in queries', 'scope':'two natively selected acquired own banks, four additional lower retained correspondences. NO claim four-bank autonomous selector or semantic language.'})
    for args in [('MA_U0_SEL_BA_PLUS','BA',1,[1,-1]),('MA_U0_SEL_AB_MINUS','AB',-1,[1,-1]),('MA_U0_SEL_BA_REVERSED','BA',1,[-1,1]),('MA_U0_SEL_BA_NOOWN','BA',1,[1,-1],'no_event')]:run(*args)
