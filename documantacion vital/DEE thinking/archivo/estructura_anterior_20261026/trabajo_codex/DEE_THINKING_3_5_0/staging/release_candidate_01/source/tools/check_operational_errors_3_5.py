"""Supplemental malformed metadata/resource checks on installed public API."""
import argparse
from pathlib import Path
import json
import tempfile
import dee_thinking as d


def main(a):
    checks=[]
    def rejects(label,f):
        try:f()
        except (ValueError,RuntimeError,OverflowError) as e:checks.append({'check':label,'rejected':True,'exception':type(e).__name__,'message':str(e)});return
        raise AssertionError('Invalid operation accepted: '+label)
    w=d.create_organization('mobile_pair');w.submit('l0.cue',5,0);w.submit('l0.teacher',7,0);w.run_until(6)
    identity=(w.runtime.current_tick,w.runtime.raw_copy(),w.runtime.clock_copy())
    with tempfile.TemporaryDirectory(prefix='dt35-malformed-') as folder:
        root=Path(folder);valid=root/'valid.deetsnap';w.save_snapshot(str(valid))
        key='dee_thinking.organizational.v1.'
        for name,operation in [
            ('unsupported_schema',lambda r:r.set_snapshot_metadata(key+'0','0200000000000000'+r.snapshot_metadata(key+'0')[16:])),
            ('invalid_chunk_count',lambda r:r.set_snapshot_metadata(key+'chunks','257')),
            ('missing_chunk',lambda r:r.erase_snapshot_metadata(key+'0')),
            ('invalid_hex',lambda r:r.set_snapshot_metadata(key+'0','gg')),
        ]:
            r=d.Runtime.load_snapshot(str(valid));operation(r);bad=root/(name+'.deetsnap');r.save_snapshot(str(bad))
            rejects(name,lambda:d.OrganizationalWorld.load_snapshot(str(bad)))
        plain=root/'runtime_only.deetsnap';d.Runtime(7).save_snapshot(str(plain))
        rejects('no_silent_repreparation',lambda:d.OrganizationalWorld.load_snapshot(str(plain)))
        for budget in (0,65537):
            t=d.TraceSession();t.sample_budget=budget;t.sites={'one':d.Coordinate(1,1,1)}
            rejects('trace_budget_'+str(budget),lambda:w.set_trace(t))
        t=d.TraceSession();t.sites={str(j):d.Coordinate(1,1,1) for j in range(129)}
        rejects('trace_site_budget_129',lambda:w.set_trace(t))
        codec=d.InputCodec();codec.version='future';rejects('unsupported_codec_version',lambda:codec.encode_integer(7))
        codec=d.InputCodec();codec.minimum=2;codec.maximum=1;rejects('invalid_codec_range',lambda:codec.encode_integer(1))
        decoder=d.OutputDecoder();decoder.version='future';rejects('unsupported_decoder_version',lambda:w.declare_decoder('future',decoder))
        e=d.ResearchStateEdit();e.coordinate=d.Coordinate(1,1,1);e.raw=0
        rejects('diagnostic_requires_explicit_authority',lambda:w.diagnostic_fork([e],False))
        self_state=(w.runtime.current_tick,w.runtime.raw_copy(),w.runtime.clock_copy())
        assert self_state==identity,'Invalid operations changed MAIN physical state'
    result={'version':d.__version__,'checks':checks,'main_physical_unchanged':True}
    Path(a.output).write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);main(p.parse_args())
