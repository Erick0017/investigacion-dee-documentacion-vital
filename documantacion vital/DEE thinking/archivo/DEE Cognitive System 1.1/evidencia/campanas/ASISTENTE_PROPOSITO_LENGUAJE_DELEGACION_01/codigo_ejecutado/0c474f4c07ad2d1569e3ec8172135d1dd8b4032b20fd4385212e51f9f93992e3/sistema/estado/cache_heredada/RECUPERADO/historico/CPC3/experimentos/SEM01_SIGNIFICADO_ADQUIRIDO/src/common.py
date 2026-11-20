"""Passive audit helpers for SEM01. No DEE update rule or response oracle."""
from array import array
from datetime import datetime, timezone
import hashlib, json, sys, zipfile
from pathlib import Path

WHL='17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623'
NATIVE='20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066'
KERNEL='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda:f.read(1048576),b''):h.update(part)
    return h.hexdigest()
def put(path,value):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
def append(path,value):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('a',encoding='utf-8') as f:f.write(json.dumps(value,ensure_ascii=False,default=str)+'\n');f.flush()
def identity(wheel):
    import dee_thinking as d
    assert d.__version__=='4.0.0' and d.build_info()['kernel_version']==27
    assert sha(wheel)==WHL and sha(d._native.__file__)==NATIVE
    assert 'site-packages' in str(Path(d.__file__).resolve()) and Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    with zipfile.ZipFile(wheel) as z:
        assert z.testzip() is None
        for name in z.namelist():
            if name.startswith('dee_thinking/') and not name.endswith('/'):
                f=Path(d.__file__).parent/Path(name).relative_to('dee_thinking')
                assert f.read_bytes()==z.read(name), name
    forbidden=[]
    for key,module in sys.modules.items():
        if key.startswith(('dee_universe_v27','src.core','src.habitat','src.lenguaje','core.entity','core.policy_session','habitat.native_loop','lenguaje.association')):
            path=getattr(module,'__file__',None)
            # SEM01 has its own new src.habitat; reject hidden historical
            # imports by actual origin, not a coincident module basename.
            if not path or not Path(path).resolve().is_relative_to(Path(__file__).resolve().parent):forbidden.append(key)
    assert not forbidden,forbidden
    return {'utc':datetime.now(timezone.utc).isoformat(),'version':d.__version__,'kernel':27,'python':sys.executable,'module':d.__file__,'wheel_sha256':WHL,'native_sha256':NATIVE,'installed_payload_identical':True,'hidden_old_implementation_imports':forbidden}
def digest(world):
    r=world.runtime if hasattr(world,'runtime') else world
    return {'tick':r.current_tick,'raw_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clock_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
def obs(world,site):
    import dee_thinking as d
    r=world.runtime if hasattr(world,'runtime') else world;o=r.observe(d.Coordinate(*site));v=o.record
    return {'tick':o.tick,'site':[o.coordinate.x,o.coordinate.y,o.coordinate.z],'raw':o.raw,'clock':o.clock,'state':v.state,'semantic':v.semantic,'s_reg':v.s_reg,'direction':[v.dx,v.dy,v.dz],'active':v.state>0 and v.semantic!=5}
def receipt(world,event):
    r=world.runtime if hasattr(world,'runtime') else world
    x=r.receipt(event if isinstance(event,int) else event.id)
    return {'id':x.id,'requested_tick':x.requested_tick,'effective_tick':x.effective_tick,'status':str(x.status),'kind':str(x.kind),'channels':x.channels,'reason':x.reason} if x is not None else {'status':'MISSING'}
