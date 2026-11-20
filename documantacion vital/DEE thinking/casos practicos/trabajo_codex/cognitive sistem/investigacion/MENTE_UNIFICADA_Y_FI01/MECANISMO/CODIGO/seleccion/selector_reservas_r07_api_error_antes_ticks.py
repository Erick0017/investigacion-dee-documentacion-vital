"""Frozen reserves from R06 fullT910, no re-teaching or target-fed reader."""
import gzip,hashlib,importlib.util,json,time
from pathlib import Path
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation
from dee_thinking.persistence import load_world_snapshot,save_world_snapshot,encode_metadata
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/seleccion'
spec=importlib.util.spec_from_file_location('accretion',HERE/'selector_acrecion_base.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
E=(33,33,33);A=(32,32,33);B=(34,32,33);QS=(930,951,997,1123,1256)
def put(p,x):
    if p.exists():raise FileExistsError(p)
    b=json.dumps(x,ensure_ascii=False,sort_keys=True).encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(side,mode):
    label='MUFI_S07_'+side+'_'+mode.upper();parent=OUT/('MUFI_S06_TOUCH_'+side+'.T910.deetsnap.gz');w=load_world_snapshot(parent);obs=lambda p:exact_observation(w.runtime.observe(d.Coordinate(*p)))
    pre={'A':obs(A),'B':obs(B)};edit_record=None
    if mode in('equalized','sham'):
        ed=d.ResearchStateEdit();ed.coordinate=d.Coordinate(*A);ed.clock=int(pre['A']['clock']);ed.label='Diagnostic only: equalize scalar while preserving geometry, or sham exactsameRAW'
        ed.raw=int(pre['A']['raw'])if mode=='sham'else d.pack_record(pre['A']['state'],pre['B']['s_reg'],*pre['A']['direction'],pre['A']['semantic'])
        edit_record={'site':A,'pre':pre['A'],'post_raw':str(ed.raw),'sham':mode=='sham'};w=w.diagnostic_fork([ed],True)
    a.declare(w,prefix='reserve');requests=[]
    for q in QS:requests+=a.query(w,q,5,prefix='reserve',supports=mode!='no_support')
    rows=[];readings=[]
    for t in sorted({910,1266,*[q+k for q in QS for k in range(10)]}):
        w.run_until(t);rows.append({'tick':t,'A':obs(A),'B':obs(B),'E':obs(E),'local':[obs(a.at(E,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)],'reader':a.read(w)})
        if t in[q+6 for q in QS]:readings.append(a.read(w))
    w.runtime.set_snapshot_metadata('MUFI01.selector.reserve.r07',encode_metadata({'identity':label,'parent_sha256':sha(parent),'parent_tick':910,'mode':'evaluationcopy'+mode,'requests':requests,'scope':'No re-teaching; observer neverreadsparenthistoryorinterventionlabel'}))
    final=OUT/(label+'.T1266.deetsnap.gz');save_world_snapshot(w,final,compress=True)
    r={'identifier':label,'schema':'MUFI01.selector.reserve.r07','parent':{'path':str(parent),'sha256':sha(parent),'tick':910},'history_for_evaluator_only':side,'mode':mode,'before':pre,'edit':edit_record,'rows':rows,'readings':readings,'requests':[a.receipt(w,x)for x in requests],'snapshot':{'path':str(final),'sha256':sha(final),'tick':1266},'source_sha256':sha(Path(__file__)),'apparatus_source_sha256':sha(HERE/'selector_acrecion_base.py'),'scope':'Same learnedT910world, querypayload5,newtimings; equalizing/sham diagnostic only. No native policy claim.'}
    put(OUT/(label+'.json.gz'),r);print(json.dumps({'label':label,'choices':[x['choice']for x in readings],'loads':[[z['observation']['s_reg']for z in x['candidates']]for x in readings],'refs':{'A':obs(A),'B':obs(B)}}),flush=True)
if __name__=='__main__':
    put(OUT/'PROTOCOLO_RESERVAS_R07.json',{'fixed_before_ticks_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'parent':'R06 acquiredoppositehistories T910 complete worlds','queries':list(QS),'payload':5,'all_routes_fixed_reader':'bothsignsandcentralY, unique SEM1statepositive matchingroute atq+6; no caseinput','arms':['Aretained','Bretained','AequalizeAtoB','BequalizeAtoB','Asham','Bsham','AnoSupport','BnoSupport'],'prediction':'Retained/sham Anegative/Bpositive; equalizationcentralY0; nosupportnoemission. Nativequerypacket5 shouldremain5 unlessknownaccretionphase, requesttimingsfrozenbeforeobserving.','horizon':1266})
    for mode in('retained','equalized','sham','no_support'):
        for side in('A','B'):run(side,mode)
