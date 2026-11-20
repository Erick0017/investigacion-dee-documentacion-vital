"""Declared new geometry: N67 non-opposed sensory directions; R02 kept intact."""
import importlib.util,sys,time,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('common_r02_exact',HERE/'enrutador_comun_sin_giros.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.N=67;b.I=(33,33,33);b.V=[(1,0,0),(0,1,0),(1,1,0),(-1,1,0)]
if __name__=='__main__':
    b.put(b.OUT/'PROTOCOLO_ENRUTADOR_COMUN_R03.json',{'before_run_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'changes_from_R02':'NEW T0 N67, non-opposed radial directions1,0;0,1;1,1;-1,1; no output-turn inputs','hypothesis':'Reduce geometry crossings of opposed request routes; no guarantee from N alone. Same fixed all-hub observer, no token-indexed expert.', 'criterion':'all3first+all4retention first-use native response signs; receipt applied indispensable; ambiguous/stale all-hub signatures not counted', 'scope':'prepared sensory-routing test, not a continuation of R02/U0/EO02'})
    b.run('MA_COMMON_R03_PAIRED',[1,-1,1,-1]);b.run('MA_COMMON_R03_OPPOSITE',[-1,1,-1,1]);b.run('MA_COMMON_R03_NOEVENT',[1,-1,1,-1],'no_event')
