"""Finite path compatibility test; primary state hashes, no world reconstruction."""
import argparse,hashlib,json,tempfile,time,traceback
from array import array
from pathlib import Path
import dee_thinking as d

def state(w):
    r=w.runtime if hasattr(w,'runtime') else w
    return {'tick':r.current_tick,'raw_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
            'clock_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();rows=[]
    with tempfile.TemporaryDirectory(prefix='DEE45_ñ_日本 espacios_') as temp:
        path=Path(temp)
        for case in ('runtime_unicode','session_gzip_unicode','trace_unicode'):
            t=time.monotonic()
            try:
                if case=='runtime_unicode':
                    w=d.Runtime(7);w.advance(2);file=path/'física ñ_日本.deetsnap';w.save_snapshot(str(file))
                    loaded=d.Runtime.load_snapshot(str(file));before=state(w);assert state(loaded)==before
                    w.advance(3);loaded.advance(3);after=state(w);assert state(loaded)==after
                elif case=='session_gzip_unicode':
                    s=d.RepertoireSession.create(count=2);s.acquire('L01',-1,0);s.acquire('L02',1,0)
                    s.run_until(3);s.schedule_query(['L01','L02'],67);s.run_until(68)
                    file=path/'sesión ñ_日本.deetsnap.gz';s.save_snapshot(file)
                    loaded=d.RepertoireSession.load_snapshot(file);before=state(s.world);assert state(loaded.world)==before
                    s.run_until(70);loaded.run_until(70);after=state(s.world);assert state(loaded.world)==after
                else:
                    w=d.Runtime(7);w.advance(2);before=state(w)
                    trace=d.TraceSession();trace.sites={'local':d.Coordinate(1,1,1)};trace.capture(w)
                    file=path/'traza ñ_日本.deetrace';trace.export_trace(str(file))
                    loaded=d.TraceSession.load_trace(str(file));other=path/'traza restaurada_日本.deetrace'
                    loaded.export_trace(str(other));assert file.read_bytes()==other.read_bytes()
                    assert len(loaded.samples)==len(trace.samples)==1
                    x,y=trace.samples[0].observation,loaded.samples[0].observation
                    assert (x.raw,x.clock,x.tick)==(y.raw,y.clock,y.tick)
                    after=state(w);assert before==after
                rows.append({'case':case,'status':'PASS','seconds':time.monotonic()-t,'before':before,'after':after,'file_sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
            except Exception:
                rows.append({'case':case,'status':'FAIL','seconds':time.monotonic()-t,'error':traceback.format_exc()})
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps({'version':d.__version__,'import_path':d.__file__,'cases':rows},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(rows,ensure_ascii=False));return int(any(x['status']!='PASS' for x in rows))
if __name__=='__main__':raise SystemExit(main())
