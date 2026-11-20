"""Research candidate: native received information contacts a second basal store.

All support is prepared at T0. The later history is not copied or injected by
Python. Phase171 aligns its write opportunity with the measured T89 approach.
This is a bounded N67/right-mismatch-Q physical-domain candidate.
"""
import order_memory
from common import record

def prepare_geometry(phase=171,landing='closed'):
    p=order_memory.prepare_geometry(center=(44,53,30),phase=phase)
    if landing not in ('closed','open'):raise ValueError('Unknown declared landing geometry')
    if landing=='open':
        import dee_thinking as d
        # New prepared candidate, not an in-life edit. Original B's semantic4
        # support occupied its incoming -z cell. Reflect its support in y/z to
        # make both +/-x approaches physically available at equal inventory.
        b=p['geometry']['B']
        pattern=((0,1,0),(0,0,1),(1,1,1),(1,0,0))
        for item,v in zip(p['placements'][6:10],pattern):item.site=d.Coordinate(*order_memory.add(b,v))
    for port in p['interfaces']:
        port.name='consolidated.'+port.name;port.channel.name=port.name
    p['geometry']['mode']='PREPARED_BASAL_SUPPORT_NATIVE_LATE_EXPERIENCE'
    p['geometry']['domain']='Right mismatch Q path after name53; native +/-x information reaches a common center at90'
    p['geometry']['forecast_contact_tick']=90
    p['geometry']['landing_geometry']=landing
    return p

def capture(world,g):return order_memory.observations(world,g)

def query(tick=94,payload=7):
    return [{'port':'consolidated.order.read','payload':payload,'tick':tick,'kind':'probe',
             'origin':'COMMON_QUERY_OF_NATIVE_ACQUIRED_SECOND_RELATION_NO_RETEACHING'}]
