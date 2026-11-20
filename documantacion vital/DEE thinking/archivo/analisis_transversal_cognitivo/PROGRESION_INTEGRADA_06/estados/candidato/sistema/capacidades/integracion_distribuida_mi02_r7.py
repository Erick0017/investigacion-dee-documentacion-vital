"""R7 exact frontend; anatomy is prepared, histories are acquired in this life."""
from capacidades import integracion_distribuida_mi02_r6 as prior
saved=prior.saved
put=prior.put
state=prior.state

def acquire(a,*,geometry,own=(11,11),private=(61,19)):
    result=prior.acquire(a,geometry=geometry,own=own,private=private)
    s=saved(a);s['schema']='MI02.unified.r7';s['candidate_reader']='Native ephemeral B reader with prepared recurrent zero-load support';put(a,s)
    result['after']=state(a);return result

def live(a,**kw):
    s=saved(a)
    if not s or s['schema']!='MI02.unified.r7':raise ValueError('Actual R7 life required')
    return prior.live(a,**kw)
