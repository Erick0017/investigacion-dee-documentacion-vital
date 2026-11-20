"""Last bounded relay-field revision: compensate the measured X-relay -Y.
An existing SEM4 anchor at E+(2,-1,0) changes P0 scalar0 to1 at new T0.
It is outside E's Moore neighborhood, so it cannot directly choose E's access.
"""
import hashlib,time,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('p1_cycle_r03',HERE/'selector_consecuencia_ciclo_r03.py');r=importlib.util.module_from_spec(sp);sp.loader.exec_module(r)
prior=r.c.b.design
def design():
    recipe,frame=prior();p=r.c.add(r.c.E,(2,-1,0))
    if p not in frame or frame[p]!=0:raise ValueError('Expected exact already prepared scalar0 anchor')
    frame[p]=1;return recipe,frame
r.c.b.design=design;r.c.__file__=__file__
if __name__=='__main__':
    r.c.b.put(r.c.OUT/'PROTOCOLO_SELECTOR_CONSECUENCIA_R04.json',{'frozen_before_ticks_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'dependencies':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in[HERE/'selector_consecuencia_ciclo_r02.py',HERE/'selector_consecuencia_ciclo_r03.py',HERE/'selector_huella_p1_piloto.py']},'measured_problem_R03':'First X relay135 receives X but136 changes to(1,-1,0), diverting later emission.','single_change':'Existing prepared SEM4 at E+(2,-1,0), outside E Moore, scalar0→1 only in this new T0. Gradient about relayX adds(-X,+Y,0), predicted remaining(+X,0,0).','unchanged':'Both taught contents; one initial current activation130; both routes/sign resources each67; all4 decoder138+67j; actual transaction worker and rejected-service touch0;4windows','scope':'Prepared relay engineering remains P0. Only actual later history-dependent change could support a local consequence-conditioned decision.'})
    r.c.run('MA02_P1_R04_GUARDED');r.c.run('MA02_P1_R04_RETURN_OMIT',feedback=False);r.c.run('MA02_P1_R04_OPPOSITE',contents=(-1,1))
