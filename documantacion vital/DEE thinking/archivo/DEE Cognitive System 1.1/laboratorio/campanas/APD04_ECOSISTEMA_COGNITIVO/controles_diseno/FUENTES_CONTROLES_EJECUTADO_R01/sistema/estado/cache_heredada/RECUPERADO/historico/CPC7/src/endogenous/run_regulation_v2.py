"""Explicit preT0 selection of the corrected guard; original v1 stays intact."""
from pathlib import Path
import sys,shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_regulation,need_regulation_v2
from common import put,sha

if __name__=='__main__':
    run_regulation.need_regulation=need_regulation_v2
    run_regulation.main()
    output=Path(sys.argv[sys.argv.index('--out')+1])
    for folder in output.iterdir():
        if folder.is_dir() and (folder/'MEASUREMENTS.json').exists():
            for name in ('need_regulation_v2.py','run_regulation_v2.py'):shutil.copyfile(Path(__file__).parent/name,folder/name)
            put(folder/'GUARD_ADAPTER_IDENTITY.json',{'guard':'need_regulation_v2','source_sha256':sha(Path(__file__).parent/'need_regulation_v2.py'),
                 'selector_sha256':sha(__file__),'selection_modality':'Declared before creation; no runtime policy from auditor'})
