"""Auxiliary physical calibration: a travelling carrier completes an XNOR pair.
Prepared stationary SEM4 frame is anatomy, not learned content or a new law.
No claim of copying a semantic memory; test whether another material effect can
be formed while the original packet continues with its exact raw payload.
"""
import gzip,hashlib,json,time
from pathlib import Path
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,save_world_snapshot
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA_R02/mecanismo_repetible';OUT.mkdir(parents=True,exist_ok=True)
N=17;D=(8,8,8);P=(9,8,8);V=(0,0,1)
def add(p,v,k=1):return tuple((p[i]+k*v[i])%N for i in range(3))
def put(p,x):
    if p.exists():raise FileExistsError(p)
    b=json.dumps(x,ensure_ascii=False,sort_keys=True).encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def run(label,frame='full',packet=True,payload=37):
    support=[(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1),(1,1,1),(-1,-1,-1)]
    if frame=='pair6':support=support[1:]
    if frame=='none':support=[]
    placements=[]
    for v in support:
        z=d.InitialPlacement();z.site=d.Coordinate(*add(D,v));z.raw=d.pack_record(1,0,0,0,0,4);z.clock=0;z.role='Prepared XNOR detector support; zero material load';placements.append(z)
    recipe=d.OrganizationRecipe.research(N,placements,0);recipe.execution=d.TickOptions(d.Backend.LAZY,1);w=d.OrganizationalWorld.create(recipe)
    requests=[]
    if packet:
        ch=d.ChannelSpec();ch.name='generic.travel';ch.injection_site=d.Coordinate(*add(P,V,-1));ch.direction=d.Direction(*V);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True
        it=d.InterfaceSpec();it.name=ch.name;it.channel=ch;w.declare_interface(it);r=w.submit(ch.name,payload,0);requests.append(int(r.id))
    rows=[]
    for t in range(7):
        w.run_until(t);rows.append({'tick':t,'detector':exact_observation(w.runtime.observe(d.Coordinate(*D))),'expected_packet_site':add(P,V,t-1),'packet':exact_observation(w.runtime.observe(d.Coordinate(*add(P,V,t-1)))),'roi':[exact_observation(w.runtime.observe(d.Coordinate(*add(D,(dx,dy,dz)))))for dx in(-1,0,1)for dy in(-1,0,1)for dz in(-1,0,1)]})
    w.runtime.set_snapshot_metadata('MA02.XNOR.TAP.v1',encode_metadata({'label':label,'support':[list(v)for v in support],'packet':packet,'payload':payload,'requests':requests,'tick':6,'not_a_learned_memory':True}))
    snap=OUT/(label+'.T6.deetsnap.gz');proof=save_world_snapshot(w,snap,compress=True)
    result={'schema':'MA02.physical_tap.pilot.1','label':label,'N':N,'new_auxiliary_T0':True,'frame':frame,'packet_supplied':packet,'payload':payload,'support':[add(D,v)for v in support],'rows':rows,'receipts':[exact_receipt(w.runtime.receipt(i))for i in requests],'snapshot':{'path':str(snap),'sha256':hashlib.sha256(snap.read_bytes()).hexdigest(),'bytes':snap.stat().st_size,'proof':proof},'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Prepared passive-material detector calibration. Birth is an event trace, not copied semantic content or a learned strategy. Original travelling carrier preservation must be measured, not assumed.'}
    put(OUT/(label+'.json.gz'),result)
    print(json.dumps({'label':label,'detector':[{'tick':r['tick'],'state':r['detector']['state'],'sem':r['detector']['semantic']}for r in rows],'parent':[{'tick':r['tick'],'raw':r['packet']['raw'],'direction':r['packet']['direction'],'load':r['packet']['s_reg']}for r in rows]},ensure_ascii=False),flush=True)
if __name__=='__main__':
    put(OUT/'PROTOCOLO_TAP_NO_CONSUMO.json',{'before_first_tick_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'native_mechanism':'Frozen v27 empty XNOR: thirteen opposite-neighbour pair equalities and at least8alive. Seven fixed SEM4 zero-load support sites have one missing opposite carrier. A current packet completes the eighth.','criterion':'Detector SEM7birth onlyfullframe+packet, while parent packet remains SEM1 and exact originalpayload/direction atitsnextsitesT2..6; compare pair6+packet,fullframewithoutpacket,packetwithoutframe,secondpayload.','horizon':6,'scope':'Auxiliary calibration, not cognitive result or MAIN improvement. A separate material effect could later couple use without consuming the content trajectory.'})
    run('MA02_TAP_FULL');run('MA02_TAP_NO_PACKET',packet=False);run('MA02_TAP_PAIR6','pair6');run('MA02_TAP_NO_FRAME','none');run('MA02_TAP_PAYLOAD53',payload=53)
