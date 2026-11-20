"""Finite native MAIN reader discovery. No post-T0 raw/clock edits."""
from pathlib import Path
import json, sys, time
import dee_thinking as d

def xyz(q): return (q.x,q.y,q.z)
def obs(rt,q):
    o=rt.observe(d.Coordinate(*q));r=o.record
    return {'tick':o.tick,'site':list(q),'raw':o.raw,'clock':o.clock,'state':r.state,'s_reg':r.s_reg,'semantic':r.semantic,'direction':[r.dx,r.dy,r.dz],'active':r.state>0 and r.semantic!=5}
def add(a,b):return tuple((x+y)%47 for x,y in zip(a,b))
def channel(w,name,q,dr):
    i=d.InterfaceSpec();i.name=name;c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*q);c.direction=d.Direction(*dr);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True;i.channel=c;w.declare_interface(i)
def rec(r):return {'id':r.id,'status':str(r.status),'reason':r.reason,'requested_tick':r.requested_tick,'effective_tick':r.effective_tick}
def make(offset,keep=False,origin=(15,15,15)):
    w=d.create_organization('relational',history=d.BasalHistory.H0,keep_reader=keep,origin=origin);s=w.view('body').spec
    channel(w,'sensor.A',add(xyz(s.a),(0,-1,0)),(0,0,-1));channel(w,'sensor.B',add(xyz(s.b),(0,1,0)),(0,0,1))
    target=add(origin,offset)
    # All geometries use one inlet twice; no extra port per episode.
    dr=(0,1,0) if offset[1]<=0 else (0,-1,0)
    inlet=add(target,tuple(-2*x for x in dr));channel(w,'read.renewed',inlet,dr)
    return w,target,inlet,dr
def panel(w,target):
    s=w.view('body').spec;a=obs(w.runtime,xyz(s.a));b=obs(w.runtime,xyz(s.b));p=w.view('body').observe()
    return {'tick':w.runtime.current_tick,'a':a,'b':b,'delta':a['s_reg']-b['s_reg'] if a['active'] and b['active'] else None,'output':obs(w.runtime,target),'support':p.supports_intact,'reader':p.reader_available}
def run(offset,keep=False):
    w,target,inlet,dr=make(offset,keep);rows=[];receipts=[]
    for tick,key in [(32,'A'),(33,'B')]:
        r=w.submit('sensor.'+key,0,tick);w.run_until(tick+1);receipts.append(rec(w.runtime.receipt(r.id)))
    rows.append({'phase':'history1','panel':panel(w,target)})
    if not keep:
        r=w.probe('read.renewed',7,34);w.run_until(37);receipts.append(rec(w.runtime.receipt(r.id)))
    else:w.run_until(37)
    rows.append({'phase':'read1','panel':panel(w,target)})
    sample_ticks={37,40,50,100,150,200,292,293,300,552,553,560,812,813,820,900,1000,1032}
    for tick in range(38,1033):
        if tick in (292,552,812):
            w.run_until(tick);r=w.submit('sensor.B',0,tick);w.advance();receipts.append(rec(w.runtime.receipt(r.id)))
        if tick in (295,555,815) and not keep:
            w.run_until(tick);r=w.probe('read.renewed',7,tick);w.advance();receipts.append(rec(w.runtime.receipt(r.id)))
        w.run_until(max(tick,w.runtime.current_tick))
        if tick in sample_ticks:rows.append({'phase':'follow','panel':panel(w,target)})
    return {'offset':list(offset),'keep_reader':keep,'inlet':inlet,'direction':dr,'receipts':receipts,'samples':rows}
def main():
    root=Path(sys.argv[1]);out=root/'experimentos/continuidad/DISCOVERY_READER.json';out.parent.mkdir(parents=True,exist_ok=True)
    variants=[(0,-1,-1),(0,-1,0),(0,-1,1),(0,0,-1),(0,0,0),(0,0,1),(0,1,-1),(0,1,0),(0,1,1)]
    rows=[]
    for off in variants:
        try:r=run(off);rows.append(r);print(json.dumps({'offset':off,'deltas':[(x['panel']['tick'],x['panel']['delta']) for x in r['samples']],'receipts':[x['status'] for x in r['receipts']],'read1':r['samples'][1]['panel']['output']},ensure_ascii=True),flush=True)
        except Exception as e:rows.append({'offset':off,'error':repr(e)});print(repr(e),flush=True)
        out.write_text(json.dumps(rows,indent=2),encoding='utf-8')
if __name__=='__main__':main()
