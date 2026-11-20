"""R06 fixed four-scalar transduction, no computed scalar aggregate.

The first pair uses the two inherited sources. The extra raw pair meets it
through v27 at two fixed sites. The failed central cancel resources R01/R03
are not supplied; no acquired matter, RAW or clock is removed or overwritten.
"""
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import ente_operativo_01_core as core
REVISION='EO02.fanin4.no_center_cancel.r06'
def submit_extra(a,values):
    if len(values)!=4 or any(type(v)is not int or not 0<=v<=64 for v in values):raise ValueError('Four raw bounded scalars required')
    t=core._plan(a)['critical_tick']-18
    rows=[body.send(a,'EO02.fanin4nocancel.'+name,site,v,t,values[index])for name,site,v,index in
       [('left',(4,13,16),(1,0,-1),2),('right',(8,13,16),(-1,0,-1),3)]]
    return{'revision':REVISION,'tick':t,'requests':rows,'expected_arrival':t+1,'sums_not_supplied':True,'prepared_zero_resources':0,'central_positions_not_injected':True}
