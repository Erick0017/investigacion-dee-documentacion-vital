"""Non-physical campaign accounting, byte identities and process isolation."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, sys, time, uuid, zipfile

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parents[1]
CANONICAL=PARENT.parents[1]/'CPC4_COMUNICACION_NATIVA_Y_META_ROSETTA_RESULTADOS.zip'
PARENT_SHA='2bcf02b6c9b195acf9e2f95751d1bd02014a8b0c6a737a18e310cd0cc0dcf5dd'
WHEEL_SHA='17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623'
PYD_SHA='20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066'
KERNEL_SHA='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def put(path,value):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    q=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
    q.write_text(json.dumps(value,ensure_ascii=False,indent=2,default=str),encoding='utf-8');os.replace(q,p)

def append(path,value):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('a',encoding='utf-8') as f:f.write(json.dumps(value,ensure_ascii=False,default=str)+'\n');f.flush()

def identity():
    import dee_thinking as d
    wheel=PARENT/'runtime'/'dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
    assert sha(wheel)==WHEEL_SHA
    assert sha(d._native.__file__)==PYD_SHA
    assert d.__version__=='4.0.0' and d.kernel_identity()['kernel_version']==27
    assert sys.version_info[:2]==(3,13) and sys.maxsize>2**32
    assert 'site-packages' in d.__file__ and 'dee_universe_v27' not in sys.modules
    kernels=list((PARENT/'referencias').rglob('kernel_v27.cpp'))
    assert kernels and all(sha(x)==KERNEL_SHA for x in kernels)
    product=PARENT.parents[2]/'4.0'/'DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip'
    old_cpc3=PARENT.parents[1]/'CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip'
    return {'utc':datetime.now(timezone.utc).isoformat(),'python':sys.executable,'python_version':sys.version,
            'module':d.__file__,'native':d._native.__file__,'version':d.__version__,'kernel':d.kernel_identity(),
            'wheel_sha256':sha(wheel),'pyd_sha256':sha(d._native.__file__),'kernel_source_sha256':KERNEL_SHA,
            'immutable_artifacts':{str(x):sha(x) for x in (product,old_cpc3) if x.exists()},
            'no_product_recompilation':True,'actor_response_source':'native evolution; identities are auditor-only'}

def parent_inventory():
    actual=sha(CANONICAL)
    if actual!=PARENT_SHA:raise RuntimeError('Canonical parent changed: '+actual)
    rows=[]
    with zipfile.ZipFile(CANONICAL) as z:
        assert z.testzip() is None
        for i in z.infolist():
            h=hashlib.sha256()
            with z.open(i) as f:
                for b in iter(lambda:f.read(1048576),b''):h.update(b)
            rows.append({'path':i.filename,'bytes':i.file_size,'sha256':h.hexdigest(),'crc32':i.CRC})
    return {'parent_sha256':actual,'members':len(rows),'expanded_bytes':sum(r['bytes'] for r in rows),'files':rows}

if __name__=='__main__':
    put(ROOT/'PROVENANCE.json',identity())
    put(ROOT/'PARENT_MEMBERS.json',parent_inventory())
    print(json.dumps({'identity':'verified','parent_members':1289,'version':'4.0.0','kernel':27}))
