"""Run an installed structured CLI in a fresh owned working directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


def main():
    p=argparse.ArgumentParser();p.add_argument('--events',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();events=a.events.resolve();a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=False)
    import dee_thinking as d
    from dee_thinking.consolidated_dialogue import main as conversation
    assert d.__version__=='4.5.0' and Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    os.chdir(a.out)
    code=conversation(['--events',str(events),'--transcript',str(a.out/'TRANSCRIPT.json'),'--strict'])
    value={'version':d.__version__,'module':d.__file__,'python':sys.executable,
           'events':str(events),'events_sha256':hashlib.sha256(events.read_bytes()).hexdigest(),
           'native_sha256':hashlib.sha256(Path(d._native.__file__).read_bytes()).hexdigest(),
           'exit_code':code,'working_directory':str(a.out),
           'generated_snapshots':[p.name for p in a.out.glob('*.deetsnap.gz')]}
    (a.out/'RESULT.json').write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    raise SystemExit(code)


if __name__=='__main__':main()
