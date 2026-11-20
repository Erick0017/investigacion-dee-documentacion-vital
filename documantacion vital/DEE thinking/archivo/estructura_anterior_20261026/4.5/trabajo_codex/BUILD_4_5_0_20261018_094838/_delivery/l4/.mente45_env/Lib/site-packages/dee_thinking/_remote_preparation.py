"""Experimental finite CPC6 remote-reader preparation, not a new physics.

Only initial geometry builders were ported (no runner/evaluator/results table).
The order-body placements originate in the compiled 4.5 native constructor;
research assembly and preT0 support phases are explicit below. A new call is a
new individual. No function here advances, clears or updates a living Runtime.
"""
from types import SimpleNamespace
from . import _native as d
from .persistence import encode_metadata, decode_metadata
import json

SOURCE_FUNCTIONS = [
  {
    "source": "action_feedback.py",
    "sha256": "a0682a12fbb406c5da44ccfe9d681efc02a1350eeed70b578cf8dd5eb57efbe2",
    "function": "_adapter_geometry"
  },
  {
    "source": "language.py",
    "sha256": "2d0cd32287fb61f6c6702db69442437a5ba3703b667f9352a30bbd3cf2b70c8f",
    "function": "_language_geometry"
  },
  {
    "source": "consolidation.py",
    "sha256": "e448743f7b615891e202007400b4bbdb79bda6d98be31d4051097a16e29b6825",
    "function": "_consolidation_geometry"
  },
  {
    "source": "order_language.py",
    "sha256": "425ec57006659727a9b68b01ba4bc0abdecb9cacfd8cf0303f18b984a016c17a",
    "function": "_order_form_geometry"
  }
]

def moved(q,v,k=1,n=67):
    return tuple((int(q[i])+int(v[i])*k)%n for i in range(3))

def _add(q,v):
    return moved(q,v)

# The selected historical order-form builder uses this local spelling.
# Both aliases are the same fixed toroidal coordinate operation beforeT0.
add=_add

def interface(name,site,direction,state=1,semantic=1):
    ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*site)
    ch.direction=d.Direction(*direction);ch.state=state;ch.semantic=semantic
    ch.allow_experience=True;ch.allow_probe=True
    p=d.InterfaceSpec();p.name=name;p.channel=ch;return p

def _body(center=(33,25,33),phase=260):
    o=d.IntegratedOptions();o.center=d.Coordinate(*center)
    o.guard_mode="none";o.body_source_load=7;o.revision_interfaces=False
    native=d.prepare_integrated_u0(o);r=native.recipe
    ps=list(r.placements);ports=[p for p in r.interfaces if p.name in ("event.A","event.B","order.read")]
    a=moved(center,(-1,0,0));b=moved(center,(1,0,0))
    bysite={(p.site.x,p.site.y,p.site.z):p for p in ps}
    pa=((-1,0,0),(-1,1,1),(0,0,1),(0,1,0));pb=((0,-1,0),(0,0,-1),(1,-1,-1),(1,0,0))
    ordered=[a,b]+[moved(a,v) for v in pa]+[moved(b,v) for v in pb]+[moved(center,(0,0,1))]
    ps=[bysite[q] for q in ordered]
    for p in ps:
        if (p.site.x,p.site.y,p.site.z) in (a,b):p.clock=phase
    return {"placements":ps,"interfaces":ports,"geometry":{"n":67,"center":list(center),
       "A":list(a),"B":list(b),"emission_site":list(moved(center,(0,-1,0))),
       "emission_tick":5,"initial_phase":phase,"initial_relation":0,"resource_sites":11}}
order_memory=SimpleNamespace(prepare_geometry=_body,add=_add)

def _adapter_geometry(*, n=67, origin=(33, 24, 33), emission_tick=5, distance=10):
    """Return placements/interfaces/JSON geometry, never construct a Runtime.

    Contract incoming U0 record: semantic1, positive state, direction(s,-1,0),
    arriving at origin at emission_tick. Its load is not read by this builder.
    """
    from . import _native as d
    if n != 67 or emission_tick != 5 or distance != 10:
        raise ValueError('First CPC6 feedback cut is N67, emission5, distance10')
    origin = tuple(origin)
    if len(origin) != 3 or any((type(x) is not int for x in origin)):
        raise ValueError('Three integer origin coordinates')
    placements = []
    ports = []
    occupied = {}
    shared = []
    hubs = {}
    branches = {}
    codecs = {}
    late = {}
    compare = emission_tick + distance
    write = compare + 4
    select = write + 1
    info = select + 3
    read = info + 10

    def place(q, load, dr, role):
        q = tuple(q)
        raw = d.pack_record(1, load, *dr, 1)
        if q in occupied:
            if occupied[q]['raw'] != raw:
                raise ValueError('Conflicting initial adapter placement ' + str(q))
            shared.append({'site': q, 'existing': occupied[q]['role'], 'shared': role})
            return
        p = d.InitialPlacement()
        p.site = d.Coordinate(*q)
        p.raw = raw
        p.clock = 0
        p.role = role
        placements.append(p)
        occupied[q] = {'raw': raw, 'role': role}

    def arrival(target, tick, dr, load, role):
        place(moved(target, dr, -tick, n), load, dr, role)
    for s in (-1, 1):
        lane = 'left' if s < 0 else 'right'
        hub = moved(origin, (s, -1, 0), distance, n)
        hubs[lane] = hub
        for c in (-1, 1):
            dr = (-c, 0, 1)
            name = f"feedback.actual.{lane}.{('plus' if c > 0 else 'minus')}"
            ports.append(interface(name, moved(hub, dr, -4, n), dr))
        for dx in (0, s):
            key = f"{lane}.{('match' if dx == 0 else 'mismatch')}"
            compare_direction = (dx, -1, 1)
            policy_site = moved(hub, compare_direction, 4, n)
            normalizer = (1, 1, -1) if dx == 0 else (-dx, 0, -1)
            arrival(policy_site, write, normalizer, 11, 'Prepared finite R14 reflected-Y policy normalizer ' + key)
            branches[key] = {'lane': lane, 'sign_reference': s, 'comparison_direction_reference': compare_direction, 'policy_site': policy_site, 'normalizer': normalizer, 'sources': {}}
            for source, policy, action in (('P', (1, 0, 0), (0, 0, 1)), ('Q', (0, -1, 0), (-1, -1, 1))):
                query_site = moved(policy_site, policy, 1, n)
                arrival(query_site, select, (-1, 0, 1), 17, 'Prepared symmetric source query ' + key + '.' + source)
                information = moved(query_site, action, 3, n)
                branch = {'query_site': query_site, 'policy_direction': policy, 'action_direction': action, 'information_site': information}
                branches[key]['sources'][source] = branch
                for v in (-1, 1):
                    value = 'positive' if v > 0 else 'negative'
                    parts = []
                    vectors = [(v, -1, -1)] if source == 'P' else [(0, 0, -1)] if v < 0 else [(1, 0, -1), (1, 0, 0)]
                    for j, dr in enumerate(vectors):
                        hub_data = moved(information, dr, -(info - 3), n)
                        if source == 'P':
                            pair = ((0, -1, 0), (v, 0, -1))
                        elif dr == (0, 0, -1):
                            pair = ((-1, 0, 0), (1, 0, -1))
                        else:
                            pair = ((0, -1, 0), (1, 1, dr[2]))
                        base = f'feedback.source.{key}.{source}.{value}.{j}'
                        for label, direction in zip(('cue', 'event'), pair):
                            ports.append(interface(base + '.' + label, moved(hub_data, direction, -3, n), direction))
                        parts.append({'base': base, 'source': source, 'value_direction': v, 'part': j, 'direction': dr, 'hub': hub_data, 'loads': [5, 18 + j], 'scope': 'One separately acquired current environmental-data carrier, not a free clone or a computed correct action'})
                    codecs[key + '.' + source + '.' + value] = parts
                    late_target = moved(information, (v, -1, 0), 10, n)
                    late_name = f'feedback.late.{key}.{source}.{value}'
                    ports.append(interface(late_name, moved(late_target, (0, 1, 1), -3, n), (0, 1, 1)))
                    late[late_name] = {'site': late_target, 'information_site': information, 'value_direction': v, 'source': source, 'branch': key, 'request_tick': read - 3, 'read_tick': read, 'scope': 'Common physical query of updated information carrier; unselected source rays differ in z and/or y'}
    g = {'schema': 'CPC6.action_feedback.geometry.v1', 'N': n, 'origin': origin, 'emission_tick': emission_tick, 'ticks': {'comparison': compare, 'policy': write, 'selection': select, 'information': info, 'late_request': read - 3, 'late_read': read}, 'comparison_hubs': hubs, 'branches': branches, 'source_codecs': codecs, 'late_queries': late, 'prepared_material_sites': len(placements), 'shared_identical_placements': shared, 'prepared_function': 'Finite reflected-Y comparison/R14 source controller with symmetric queries. Comparison, policy, action and received information are native state transitions, not host decisions.', 'input_contract': 'Incoming learned U0 output(s,-1,0). actual c is a current external observation encoded as(-c,0,+1), duplicated into two fixed lanes, never an error calculated by host.', 'information_contract': 'P/Q current contents use acquired directional source carriers taught at0; each physical opportunity receives separate exposures. Positive-Q code has two contributors and unequal codec cost.', 'preservation_scope': 'U0 order remains in its original body. Comparator dx0/s encodes match/mismatch; later information carries source value, not a permanent copy of the original participant/order tuple.'}
    return {'placements': placements, 'interfaces': ports, 'geometry': g}

def _language_geometry(g):
    ports = []
    items = {}
    n = g['N']
    t = g['ticks']['late_read']
    for late, p in g['late_queries'].items():
        v = p['value_direction']
        start = p['site']
        hub = moved(start, (v, 0, 1), 10, n)
        query = moved(hub, (v, -1, 1), 10, n)
        key = late.removeprefix('feedback.late.')
        name = 'language.teach.' + key
        read = 'language.query.' + key
        ports.append(interface(name, moved(hub, (0, -1, 0), -3, n), (0, -1, 0)))
        ports.append(interface(read, moved(query, (0, 1, 0), -3, n), (0, 1, 0)))
        items[key] = {'teach_port': name, 'query_port': read, 'teach_site': hub, 'query_site': query, 'teach_request_tick': t + 7, 'teach_tick': t + 10, 'query_request_tick': t + 17, 'query_tick': t + 20, 'value_direction': v, 'native_information_path': late}
    return {'placements': [], 'interfaces': ports, 'geometry': {'schema': 'CPC6.language.v1', 'items': items, 'alias': 'FORMA_01', 'encoding': 'Simultaneous equal-dose pulses on every predeclared candidate lane; no lane chosen using history or decoder.', 'scope': 'Later opaque-sign association with a received directional relation, not a dictionary or 65 semantic meanings.'}}

def _consolidation_geometry(phase=171, landing='closed'):
    if landing == 'bilateral':
        right = _consolidation_geometry(phase, 'open')
        from . import _native as d
        left = _consolidation_geometry(phase, 'open')

        def translated(q):
            return order_memory.add(q, (-28, 0, 0))
        for p in left['placements']:
            p.site = d.Coordinate(*translated((p.site.x, p.site.y, p.site.z)))
        for p in left['interfaces']:
            p.name = p.name.replace('consolidated.', 'consolidated.left.')
            p.channel.name = p.name
            q = p.channel.injection_site
            p.channel.injection_site = d.Coordinate(*translated((q.x, q.y, q.z)))
        g = left['geometry']
        for key in ('center', 'A', 'B', 'emission_site'):
            g[key] = list(translated(g[key]))
        g['domain'] = 'Left mismatch Q; independently prepared support, not a cloned acquired memory'
        right['placements'] += left['placements']
        right['interfaces'] += left['interfaces']
        right['geometry']['left'] = g
        right['geometry']['landing_geometry'] = 'bilateral'
        return right
    p = order_memory.prepare_geometry(center=(44, 53, 30), phase=phase)
    if landing not in ('closed', 'open'):
        raise ValueError('Unknown declared landing geometry')
    if landing == 'open':
        from . import _native as d
        b = p['geometry']['B']
        pattern = ((0, 1, 0), (0, 0, 1), (1, 1, 1), (1, 0, 0))
        for item, v in zip(p['placements'][6:10], pattern):
            item.site = d.Coordinate(*order_memory.add(b, v))
    for port in p['interfaces']:
        port.name = 'consolidated.' + port.name
        port.channel.name = port.name
    p['geometry']['mode'] = 'PREPARED_BASAL_SUPPORT_NATIVE_LATE_EXPERIENCE'
    p['geometry']['domain'] = 'Right mismatch Q path after name53; native +/-x information reaches a common center at90'
    p['geometry']['forecast_contact_tick'] = 90
    p['geometry']['landing_geometry'] = landing
    return p

def _order_form_geometry(body):
    r = add(body['center'], (0, 0, -1))
    ports = []
    items = {}
    for h in (-1, 1):
        key = 'negative' if h < 0 else 'positive'
        hub = add(r, (10, 10 * h, -10))
        query = add(r, (10, 20 * h, -20))
        name = 'order_form.teach.' + key
        read = 'order_form.query.' + key
        ports.append(interface(name, add(hub, (3, 0, 0)), (-1, 0, 0)))
        ports.append(interface(read, add(query, (-3, 0, 0)), (1, 0, 0)))
        items[key] = {'teach_port': name, 'query_port': read, 'teach_site': list(hub), 'query_site': list(query), 'history_direction': h}
    return {'interfaces': ports, 'geometry': {'schema': 'CPC6.order_form.v1', 'items': items, 'alias': 'FORMA_02', 'prepared_reader_tick': 69, 'native_history_emission_tick': 70, 'teach_request_tick': 77, 'teach_tick': 80, 'query_request_tick': 87, 'query_tick': 90, 'scope': 'Fixed directional expression of distributed A/B event-order history, renewed before the second sign; not arbitrary ANTES/DESPUES or speaker roles.'}}

def build(backend="LAZY",threads=1):
    body=_body();adapter=_adapter_geometry();language=_language_geometry(adapter["geometry"])
    secondary=_consolidation_geometry(171,"bilateral")
    placements=body["placements"]+adapter["placements"]+secondary["placements"]
    ports=body["interfaces"]+adapter["interfaces"]+language["interfaces"]+secondary["interfaces"]
    g={"schema":"dee_thinking.remote_reader.experimental.v1","N":67,
       "body":body["geometry"],"adapter":adapter["geometry"],"language":language["geometry"],
       "consolidation":secondary["geometry"],"renewed_interfaces":{}}
    for name,part in (("original",g["body"]),("consolidated",g["consolidation"]),("consolidated.left",g["consolidation"]["left"])):
        site=_add(part["center"],(0,0,-1));port="renewed."+name
        ports.append(interface(port,site,(0,0,-1)))
        g["renewed_interfaces"][name]={"port":port,"site":list(site),"direction":[0,0,-1]}
    second=_order_form_geometry(g["body"]);ports+=second["interfaces"];g["order_language"]=second["geometry"]
    balanced={}
    for key,b in g["adapter"]["branches"].items():
        info=b["sources"]["Q"]["information_site"];dr=(-1,0,0);hub=moved(info,dr,-20)
        base="balanced.source."+key+".Q.negative.1";pair=((0,-1,0),(-1,1,0))
        for label,direction in zip(("cue","event"),pair):ports.append(interface(base+"."+label,moved(hub,direction,-3),direction))
        balanced[key]={"base":base,"hub":list(hub),"directions":[list(x) for x in pair],"loads":[5,19]}
    g["balanced_source_codec"]={"parts":balanced,"scope":"Q+ and Q- have equal contributor count/dose; current observation codec, not a correct-answer computation"}
    bus={}
    for name,part in (("right",g["consolidation"]),("left",g["consolidation"]["left"])):
        target=_add(part["center"],(0,0,-1));site=_add(target,(0,0,-44));port="word_bus."+name
        ports.append(interface(port,site,(0,0,1)))
        bus[name]={"port":port,"source":list(site),"target":list(target),"direction":[0,0,1],"native_delay":44,"center":part["center"]}
    g["word_bus"]={"parts":bus,"scope":"Additional fixed physical reader supply, not a renewable-language guarantee"}
    sites=[(p.site.x,p.site.y,p.site.z) for p in placements]
    if len(sites)!=len(set(sites)):raise ValueError("Experimental initial material overlaps")
    if len({p.name for p in ports})!=len(ports):raise ValueError("Experimental interface names overlap")
    # Initial support in the left second body is reflected exactly as the
    # published open-landing preparation; not an edit in a living world.
    recipe=d.OrganizationRecipe.research(67,placements,0);recipe.interfaces=ports
    recipe.execution=d.TickOptions(getattr(d.Backend,backend) if isinstance(backend,str) else backend,threads)
    g=decode_metadata(json.dumps(g,separators=(",",":")))
    recipe.options={"dee_thinking.remote_reader.geometry.v1":encode_metadata(g)}
    recipe.domain="EXPERIMENTAL fixed CPC6 N67 remote reader, validated reference window162; no65NSM or stable indefinite dialogue claim"
    return recipe,g

