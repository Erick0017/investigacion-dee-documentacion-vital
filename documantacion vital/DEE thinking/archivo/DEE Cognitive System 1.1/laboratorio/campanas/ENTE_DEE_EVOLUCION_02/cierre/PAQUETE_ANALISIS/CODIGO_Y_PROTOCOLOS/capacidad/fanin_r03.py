"""Eight raw components meet materially in the inherited two sensory sites.

No changed anatomy and no host aggregate. Two formerly zero-cancel resources
carry independent raw components. Two additional opened edge sites add others.
Direction is no longer exactly vertical, so retention/interference is tested.
"""
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import ente_operativo_01_core as core
REVISION='EO02.fanin8.peripheral.r03'
SPECS=[('left.edge',(4,13,16),(1,0,-1),2),
       ('right.edge',(8,13,16),(-1,0,-1),3),
       ('left.high',(4,14,16),(1,-1,-1),4),
       ('right.high',(8,14,16),(-1,-1,-1),5),
       ('left.center',(6,13,15),(-1,0,0),6),
       ('right.center',(6,13,16),(1,0,-1),7)]
def submit_extra(a,values):
    if len(values)!=8 or any(type(v)is not int or not 0<=v<=32 for v in values):
        raise ValueError('Exactly eight raw integers0..32 required')
    tick=core._plan(a)['critical_tick']-18
    rows=[body.send(a,'EO02.fanin8.'+name,site,direction,tick,values[index])for name,site,direction,index in SPECS]
    return{'revision':REVISION,'tick':tick,'requests':rows,'sums_not_supplied':True,
           'prepared_zero_resources':0,'targets':[[5,13,15],[7,13,15]],'expected_arrival':tick+1,
           'grammar':'x1,x3,x5,x7 contribute left; x2,x4,x6,x8 contribute right through v27 reducer.'}
