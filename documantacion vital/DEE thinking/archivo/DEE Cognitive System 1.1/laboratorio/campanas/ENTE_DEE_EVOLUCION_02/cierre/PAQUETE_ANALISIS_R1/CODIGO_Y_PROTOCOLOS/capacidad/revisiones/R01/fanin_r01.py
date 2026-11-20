"""EO02 peripheral fan-in, first candidate. No sums are supplied to DEE.

Four independent observations retain fixed component ports; two generic zero
carriers cancel lateral momentum at the inherited sensory destinations.
This module only submits raw events, never chooses an action or edits a field.
"""
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import ente_operativo_01_core as core

REVISION='EO02.fanin4.peripheral.r01'

def submit_extra(a,values):
    if len(values)!=4 or any(type(v)is not int or not 0<=v<=32 for v in values):
        raise ValueError('Exactly four raw integers0..32, no solved aggregate')
    plan=core._plan(a);tick=plan['critical_tick']-18
    # x1,x2 use the inherited left/right origins; x3,x4 enter independently.
    specs=[('left',(4,13,16),(1,0,-1),values[2]),
           ('right',(8,13,16),(-1,0,-1),values[3]),
           ('left.cancel',(6,13,15),(-1,0,0),0),
           ('right.cancel',(6,13,16),(1,0,-1),0)]
    rows=[body.send(a,'EO02.fanin4.'+name,site,direction,tick,value)for name,site,direction,value in specs]
    return{'revision':REVISION,'tick':tick,'requests':rows,
           'sums_not_supplied':True,'prepared_zero_resources':2,
           'targets':[[5,13,15],[7,13,15]],'expected_arrival':tick+1}
