"""Complete a post-write verification without overwriting prepared R04 files.

The first FS-only preparation created the five sources but its final source
hash check raised AttributeError(str.read_bytes), before writing the witness.
Every existing output must equal its deterministic preparation bytes; no source
is recreated, no Native/model/MCP call occurs and no old runtime is touched.
"""
from pathlib import Path
import hashlib
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import preparar_referencias_lease_R04 as preparation

def verify_existing(path,source):
    if not path.is_file()or path.read_bytes()!=source.encode('utf-8'):
        raise ValueError('Existing prepared output differs; preserve and inspect: '+str(path))
    compile(source,str(path),'exec')
    return{'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
           'bytes':path.stat().st_size,'existing_bytes_verified_without_overwrite':True}

if __name__=='__main__':
    preparation.create=verify_existing
    preparation.main()
