"""MI01: bounded operational reuse, not an external mind/controller.

Acquisition and composition use the official runtime and existing AA01/IC01
mechanisms. Protocol metadata is not a response table. No lab/evidence input.
"""
from dee_thinking.persistence import encode_metadata,decode_metadata
from app.native_tools import physical
from capacidades import acceso_adaptativo_01 as aa,espanol_funcional_01 as ef
from capacidades.integracion_situada_01 import ic_native_core as native

KEY='DEE.Cognitive.System.1.1.MI01.v1'
VERSION='MI01.operational.bounded.1'

def saved(a):
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    return decode_metadata(entries[KEY])if KEY in entries else {'schema':VERSION,'episodes':[]}

def put(a,state):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(state))

def material_command(row):
    return row['state']==1 and row['semantic']==1 and row['direction'][0]==1 and abs(row['direction'][1])==1 and row['direction'][2]==0

def state(a):
    if physical(a.world)['N']!=67:raise ValueError('Explicit late N67 inherited domain only')
    return {'version':VERSION,'physical':physical(a.world,occupation=True),'protocol':saved(a),
      'selector_native':native.obs(a,native.configuration(a)['center']),
      'assistance':'Prepared geometry, experience calendar and common query. Selection/content must exist physically; this observer never supplies them.',
      'limits':'Material direction at zero load can be causal but is NOT automatically an action-dependent policy. No general language/autonomy claim.'}

def compose(a,*,episode,availability=(1,-1),contents=(-1,1),feedback='paired',delay=None):
    if a.tick<21778:raise ValueError('MI01 extension validated on late inherited E1 branches; earlier AA01 contracts remain separate')
    ef.prepare(a) # empty interface declaration, not teaching
    lag=ef.tick_at_or_after(a.tick,phase=6,lead=4)-a.tick if delay is None else delay
    start=physical(a.world,occupation=True)
    plan=aa.prepare_local_episode(a,episode=episode,availability=availability,contents=contents,feedback=feedback,delay=lag,recipient_mode='immediate_yz')
    stages=[aa.advance_local_episode(a,stage=stage)for stage in('first','learned','content','access','received','use')]
    result={'initial':start,'plan':plan,'stages':stages,'final':physical(a.world,occupation=True),
       'attribution':'Two experienced routes and independent oriented contents meet natively at a prepared common access and are used by a receiver. The operator initiates the curriculum/query; code combinations are not computed by Python.',
       'not_claimed':['Spanish/NSM acquisition','recipient long-term memory','self-initiated question','general policy learning']}
    cfg=saved(a);cfg['episodes'].append({'episode':episode,'kind':'NATIVE_ROUTE_CONTENT_COMPOSITION','initial_tick':start['tick'],'final_tick':a.tick,'operator_initiated':True});put(a,cfg)
    return result

def train(a,**options):
    result=native.train(a,**options)
    cfg=saved(a);cfg['episodes'].append({'episode':options['episode'],'kind':'NATIVE_CONSEQUENCE_CONDITIONED_SELECTION','final_tick':a.tick,'law_prepared':True});put(a,cfg);return result
