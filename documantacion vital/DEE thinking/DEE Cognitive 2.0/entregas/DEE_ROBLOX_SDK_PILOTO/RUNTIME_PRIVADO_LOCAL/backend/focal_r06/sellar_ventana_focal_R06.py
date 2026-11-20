"""Seal only a new focal subset window. FS-only; no identity, owner or Native."""
from pathlib import Path
import argparse,time
from sdk_common import RUNTIME,atomic,read,sha,verify_focal_sources,canonical

def seal(runtime=RUNTIME, *, execute=False, now=None):
    runtime=Path(runtime).resolve(strict=True);current=int(time.time()) if now is None else int(now)
    original=runtime/'configuracion/VENTANA_R06.json';g=read(original)
    source_sha=verify_focal_sources(runtime)
    start=current;hard=min(g['hardFinishUtcEpoch'],start+21600)
    last=min(g['lastNewUtcEpoch'],hard-3600)
    if not g['startUtcEpoch']<=start<last<hard or last<=current+300:
        raise RuntimeError('NO_PROSPECTIVE_FOCAL_WINDOW_REMAINS')
    c={**g,'startUtcEpoch':start,'lastNewUtcEpoch':last,'hardFinishUtcEpoch':hard,
       'globalWindowSha256':sha(original),'focalSourcesSha256':source_sha}
    output=runtime/'configuracion/VENTANA_FOCAL_R06.json'
    if output.exists():raise FileExistsError('FOCAL_WINDOW_NEVER_RESEALED')
    if execute:atomic(output,c,new=True)
    return {'status':'SEALED' if execute else 'PLAN_ONLY','window':c,'output':str(output),
            'NativeImported':False,'identityCreated':False,'ledgerReset':False}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute-fs-only',action='store_true')
    a=p.parse_args();print(canonical(seal(execute=a.execute_fs_only)))
