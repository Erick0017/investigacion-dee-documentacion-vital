"""Explicit P0 generic phase perturbation; not autonomous regulation.

Equal packets on both sensory sides carry no remembered sign/reference.
They can interrupt a motor stream briefly and change its subsequent phase.
This can help or harm a fixed opportunity schedule, so it is never automatic.
"""
from capacidades import arquitectura_distribuida_mi02_r8 as n
from capacidades import integracion_distribuida_mi02_r6 as shared
from app.native_tools import physical

def pulse(a,*,mode='treatment',load=1000):
    if mode not in('treatment','sham','none')or type(load)is not int or not 1<=load<=1000:raise ValueError('Declared bounded material resource and control required')
    s=shared.saved(a)
    if not s or s['schema']!='MI02.unified.r6':raise ValueError('Exact R6 body required; no inferred universal phase repair')
    g=s['geometry'];start=a.tick;before=shared.state(a);requests=[]
    if mode!='none':
        for p in g['external_sensors'][:2]:
            v=p['direction']if mode=='treatment'else[-x for x in p['direction']]
            requests.append(n.send(a,'MI02.phase.'+mode+'.'+p['name'],p['origin'],v,start+1,load))
    frames=[]
    for t in range(start+1,start+20):
        a.run_until(t);frames.append({'tick':t,'A':n.obs(a,g['A']),'M':[n.obs(a,p)for p in n.get(a)['memories']],'ports':[n.obs(a,n.xyz(a,g['A'],(r,-1,-1)))for r in(-1,0,1)],'social_context':[n.obs(a,p['context'])for p in g['social']['routes']]})
    return{'mode':mode,'load_each':load,'before':before,'requests':n.receipts(a,requests),'frames':frames,'after':shared.state(a),'assistance':'Operator initiates a fixed symmetric material perturbation. No target, private value, word, desired sign, snapshot or learned-field edit is supplied. P0 only; may harm an already matched phase.','not_a_reteaching':'Native learned scalar values are not injected or refreshed.'}
