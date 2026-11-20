"""Fresh basal relative-order body; real event pulses acquire its distinction.

Adapted from CPC5 order_stream's documented geometry, not a trained snapshot.
No function in this module receives the history's expected answer.
"""
from common import interface, record

PA=((-1,0,0),(-1,1,1),(0,0,1),(0,1,0))
PB=((0,-1,0),(0,0,-1),(1,-1,-1),(1,0,0))

def add(q,v,n=67): return tuple((int(q[i])+int(v[i]))%n for i in range(3))

def prepare_geometry(n=67, center=(33,25,33), phase=260):
    import dee_thinking as d
    if n!=67: raise ValueError('This version publishes only the verified N67 preparation')
    a=add(center,(-1,0,0),n); b=add(center,(1,0,0),n)
    placements=[]; used=set()
    def place(q,state,load,semantic,clock):
        if q in used: raise ValueError('Overlapping basal support')
        used.add(q); p=d.InitialPlacement(); p.site=d.Coordinate(*q)
        p.raw=d.pack_record(state,load,0,0,0,semantic);p.clock=clock
        p.role='Fresh relative-order support, not an acquired association';placements.append(p)
    place(a,1000,100,1,phase); place(b,2000,100,1,phase)
    for q,pattern,state,clock in ((a,PA,3000,31),(b,PB,4000,41)):
        for i,v in enumerate(pattern): place(add(q,v,n),state+i,0,4,clock+i)
    place(add(center,(0,0,1),n),6100,7,4,19)
    ports=[interface('event.A',add(a,(0,-1,0),n),(0,-1,0),state=5000),
           interface('event.B',add(b,(0,1,0),n),(0,1,0),state=5001),
           interface('order.read',add(center,(0,-1,0),n),(0,1,0))]
    return {'placements':placements,'interfaces':ports,
            'geometry':{'n':n,'center':list(center),'A':list(a),'B':list(b),
                        'emission_site':list(add(center,(0,-1,0),n)), 'emission_tick':5,
                        'initial_phase':phase,'initial_relation':0,
                        'resource_sites':len(placements)}}

def observations(world, geometry):
    a,b=record(world,geometry['A']),record(world,geometry['B'])
    return {'A':a,'B':b,'delta':a['s_reg']-b['s_reg'] if a['active'] and b['active'] else None,
            'center':record(world,geometry['center']),
            'emission':record(world,geometry['emission_site'])}

def experience(order='AB',load=3,gap=1,onset=0):
    if order not in ('AB','BA'): raise ValueError('Only the declared two-event grammar AB/BA is admitted')
    if not 0<load<19665 or gap<1 or onset<0: raise ValueError('Invalid physical event protocol')
    return [{'port':'event.'+letter,'payload':load,'tick':onset+i*gap,'kind':'submit',
             'origin':'CURRENT_LOCAL_EVENT'} for i,letter in enumerate(order)]
