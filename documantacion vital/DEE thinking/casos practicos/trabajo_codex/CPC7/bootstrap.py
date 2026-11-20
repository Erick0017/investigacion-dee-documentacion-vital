"""Campaign-local selective source extraction and runtime installation."""
import hashlib,json,sys,zipfile,subprocess,time,ctypes
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CASES=ROOT.parents[1]
EXPECTED='9d8c72a2536a7d8a782e0f3885d6d9ceba48b5f3d9111f618386def13fff708b'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    source=CASES/'CPC6_MENTE_DEE_INTEGRADA_APRENDIZAJE_Y_COMUNICACION_RESULTADOS.zip'
    assert sha(source)==EXPECTED
    names=['common.py','supervisor.py','snapshot_storage.py','integrated.py','order_memory.py','action_feedback.py','language.py','consolidation.py','curriculum.py','order_language.py','balanced_sources.py','word_bus.py','action_feedback_access.py','life.py']
    rows=[]
    with zipfile.ZipFile(source) as z:
        for name in names:
            member='CPC6/src/'+name;p=ROOT/'src'/name;p.parent.mkdir(parents=True,exist_ok=True)
            assert not p.exists();blob=z.read(member);p.write_bytes(blob)
            rows.append({'source_archive_sha256':EXPECTED,'member':member,'sha256':hashlib.sha256(blob).hexdigest(),'destination':p.relative_to(ROOT).as_posix(),'status':'COPIED_UNMODIFIED'})
        member='CPC6/runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
        p=ROOT/'runtime'/Path(member).name;p.parent.mkdir(exist_ok=True);assert not p.exists();p.write_bytes(z.read(member))
        assert sha(p)=='17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623'
    (ROOT/'genealogia').mkdir(exist_ok=True)
    (ROOT/'genealogia/BASE_SOURCE_IDENTITY.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    assert sha(source)==EXPECTED
    print(json.dumps({'source_unchanged':True,'selected_modules':len(names),'wheel_hash_verified':True}))
if __name__=='__main__':main()
