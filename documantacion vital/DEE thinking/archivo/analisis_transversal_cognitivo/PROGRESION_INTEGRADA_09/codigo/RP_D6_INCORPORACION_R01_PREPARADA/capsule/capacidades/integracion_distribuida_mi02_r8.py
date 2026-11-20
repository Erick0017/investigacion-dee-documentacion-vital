"""R8 social-reader candidate, distinct from return-path bodyR8."""
from capacidades import integracion_distribuida_mi02_r6 as prior
saved=prior.saved
put=prior.put
state=prior.state
def acquire(a,*,geometry,own=(11,11),private=(61,19)):
    r=prior.acquire(a,geometry=geometry,own=own,private=private);s=saved(a);s['schema']='MI02.unified.r8';put(a,s);r['after']=state(a);return r
def live(a,**kw):
    if not saved(a)or saved(a)['schema']!='MI02.unified.r8':raise ValueError('Actual R8 social-reader life required')
    return prior.live(a,**kw)
