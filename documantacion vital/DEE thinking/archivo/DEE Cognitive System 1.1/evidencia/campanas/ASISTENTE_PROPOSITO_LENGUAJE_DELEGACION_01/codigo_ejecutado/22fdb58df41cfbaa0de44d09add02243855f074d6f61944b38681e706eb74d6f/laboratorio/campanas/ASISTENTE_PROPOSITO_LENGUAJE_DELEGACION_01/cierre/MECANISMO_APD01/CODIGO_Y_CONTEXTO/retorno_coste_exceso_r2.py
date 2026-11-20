"""APD01 prepared excess-cost gate -> one physical environmental channel.

This is a new declared transducer, not a learned credit-assignment algorithm.
No action, intended route, correct answer or expected sign is an input. The
environment may supply its actual fixed-law modelled cost, never a gradient.
"""
from capacidades import mente_unificada_01 as mu
from capacidades import mente_acumulativa_r02 as ma
from capacidades import selector_acrecion_nativo as sel

VERSION = 'APD01.fixed_excess_common_return.candidate.R2'
MODELLED_BUDGET = 2
S = (14,15,16)
SHAM = (14,15,20)


def next_even_window(tick):
    k=(int(tick)+12+390)//391
    if k%2:k+=1
    return {'boundary':391*k,'multiplier':k,'parity':'even',
            'query_tick':391*k-4,'datum_tick':391*k-1,
            'information':'Integer calendar only, never cost/action/target/RAW'}


def references(a):return[mu.observation(a,p)for p in((14,14,15),(16,14,15))]


def return_cost(a,cost,*,mode='real'):
    timing=next_even_window(a.tick)
    if not mu.get(a).get('current_frontend'):
        raise ValueError('Existing current frontend required; no silent installation')
    if type(cost)is not int or not 0<=cost<=32:
        raise ValueError('Actual environment modelled cost must be an exact scalar0..32')
    if mode not in('real','omit','sham'):
        raise ValueError('Frozen environmental/control return modalities only')
    excess=cost>MODELLED_BUDGET
    pre=references(a);requests=[];q=timing['query_tick']
    if excess and mode!='omit':
        p=S if mode=='real'else SHAM
        # One common literal-cost channel. Its site is not selected by action.
        ma.submit(a,'APD.excess.'+('S'if mode=='real'else'sham'),p,(0,0,0),cost,timing['datum_tick'],requests)
    qr=sel.query(a.world,q,5,'MU.selector')
    frames=[]
    for tick in range(q-1,q+9):
        a.run_until(tick)
        frames.append({'tick':a.tick,'references':references(a),
                       'S':mu.observation(a,S),'sham':mu.observation(a,SHAM)})
        if tick==q+6:reader=mu.current_read(a)
    return {'kind':'prepared_common_excess_cost_return','version':VERSION,
            'actual_modelled_cost':cost,'fixed_modelled_budget':MODELLED_BUDGET,
            'excess_flag_environment_not_actor_answer':excess,'control_mode':mode,
            'timing':timing,'references_before':pre,'references_after':references(a),
            'reader_during_environmental_return':reader,'frames':frames,
            'requests':ma.receipts(a,requests)+[sel.receipt(a.world,r)for r in qr],
            'assistance':'Calendar, excess threshold, physical S interface and native-biased '
                         'local plasticity are prepared. Every arm/cost gets the same '
                         'wait and three generic queries; low cost omits only S. No '
                         'Python A/B selection, correct route or memory update.',
            'scope':'Conditional acquired state/choice can be attributed only after '
                    'actual task/omission/sham contrasts. Not general R2, optimal '
                    'credit assignment, bidirectional adaptation or physical energy.'}
