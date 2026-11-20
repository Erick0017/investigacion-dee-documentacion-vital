"""One new anatomy revision: balanced fixed fields keep X/Y relays directional.

R02 showed that the first selected neighbor became SEM1 direction0, obstructing
later emissions. These are prepared scalar1 anchors, NOT acquired actions or a
host policy. The native gradient at E still compares fixed offset1 with a native
past-touch latch1. Added anchor pairs balance E's field before/after touch.
"""
import hashlib,time,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('p1_cycle_r02',HERE/'selector_consecuencia_ciclo_r02.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
original=c.b.design
def design():
    recipe,frame=original()
    # Eight equal scalar anchors form balanced XZ/YZ pairs about E. Counterpart
    # sites about D preserve opposite-neighbor activity of the XNOR frame;
    # their scalar can stay zero because XNOR uses activity, not equal load.
    for x,y,z in[(0,-1,-1),(0,-1,1),(0,1,-1),(0,1,1),(-1,0,-1),(-1,0,1),(1,0,-1),(1,0,1)]:
        p=c.add(c.E,(x,y,z));frame[p]=1
        rel=tuple(p[i]-c.D[i]for i in range(3))
        if all(-1<=v<=1 for v in rel):
            mirror=c.add(c.D,tuple(-v for v in rel))
            if mirror not in frame:frame[mirror]=0
    # Balanced diagonal pair cancels relay-Y lateral offset from the original
    # counteranchor while preserving E's scalar gradient exactly.
    frame[c.add(c.E,(1,1,0))]=1;frame[c.add(c.E,(-1,-1,0))]=1
    if c.E in frame or c.D in frame:raise ValueError('No prepared actor/trace')
    return recipe,frame
c.b.design=design
# The primary records this executed wrapper hash. Its R02 dependency is fixed
# explicitly in the prospective protocol and must travel with reproduction.
c.__file__=__file__
if __name__=='__main__':
    c.b.put(c.OUT/'PROTOCOLO_SELECTOR_CONSECUENCIA_R03.json',{'frozen_before_ticks_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'dependency_r02_sha256':hashlib.sha256((HERE/'selector_consecuencia_ciclo_r02.py').read_bytes()).hexdigest(),'question':'Does a balanced prepared relay field permit repeated native access and the actual generic rejection-touch cycle, rather than relay blockage seen in R02?','change':'Prepared balanced scalar1 anchors in XZ/YZ planes; opposite active counterparts about D where necessary; diagonal balanced pair; new T0, never an edit of R02 life.','unchanged':'Both acquired contents, single activation130, all4 marker routes every67, fixed all4 observer138+67j, actual worker, fixed rejected-service touch0. Four windows, no target-dependent scheduling.','criteria':'Every native absence/conflict remains abstention; no policy claim without later changed useful action and return controls; prepared relay field remains P0.'})
    c.run('MA02_P1_R03_GUARDED');c.run('MA02_P1_R03_RETURN_OMIT',feedback=False);c.run('MA02_P1_R03_OPPOSITE',contents=(-1,1))
