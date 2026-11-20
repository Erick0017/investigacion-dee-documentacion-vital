"""Real C++/Python operational continuation, pending inputs and captured trace."""
import argparse
from array import array
import hashlib
import json
from pathlib import Path
import subprocess
import dee_thinking as d

def identity(w):
    return {"tick":w.runtime.current_tick,"raw":hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest(),
            "clock":hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest(),
            "channels":w.runtime.channel_names,"receipts":[(r.id,str(r.status),r.requested_tick,r.effective_tick,r.channels) for r in w.runtime.receipts],
            "protocols":[{"id":p.id,"next":p.next_capture,"captures":[[(o.raw,o.clock,o.tick) for o in s.captured] for s in p.steps]} for p in w.protocols],
            "trace":[(s.id,s.tick,s.observation.raw,s.observation.clock,s.coverage) for s in w.trace().samples]}

def main(a):
    folder=Path(a.output);folder.mkdir(parents=True,exist_ok=True);cpp=str(Path(a.consumer).resolve())
    mid=folder/'CPP_MID.deetsnap';py=folder/'PYTHON_MID.deetsnap';end=folder/'CPP_FINAL.deetsnap';bridge=folder/'CPP_BRIDGE.deetsnap'
    calls=[]
    def command(*args):
        r=subprocess.run([cpp,*map(str,args)],text=True,capture_output=True);calls.append({"argv":[cpp,*map(str,args)],"exit_code":r.returncode,"stdout":r.stdout,"stderr":r.stderr});assert r.returncode==0,r.stderr
    command('create',mid)
    w=d.OrganizationalWorld.load_snapshot(str(mid));assert w.runtime.current_tick==13 and w.protocols[0].next_capture==1
    assert w.decoder('load').version=='1.0.0' and len(w.organization_ids)==4 and w.trace().samples
    reference=w.fork();reference.run_until(21)
    w.run_until(16);assert w.protocols[0].next_capture==2;w.save_snapshot(str(py));command('continue',py,end)
    final=d.OrganizationalWorld.load_snapshot(str(end));assert identity(final)==identity(reference),'cross-language operational future'
    command('bridge',d.reference_seed_path(),bridge);b=d.OrganizationalWorld.load_snapshot(str(bridge));p=d.create_organization('mobile_basal');p.advance(6)
    assert identity(b)==identity(p),'C++ physical inter-family preparation/evolution'
    assert b.view('body').observe().delta==1 and b.observe('body','comparator').record.s_reg==12
    result={"version":d.__version__,"cpp_to_python":True,"python_to_cpp":True,"other_process_restoration":True,
            "shared_views":True,"pending_input_continuation":True,"protocol_cursor_readouts":True,"trace_preserved":True,
            "interfamily_native_bridge_equal":True,"final":identity(final),"commands":calls,
            "checkpoints":[{"name":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in (mid,py,end,bridge)]}
    (folder/'CROSS_LANGUAGE_RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--consumer',required=True);p.add_argument('--output',required=True);main(p.parse_args())
