"""Finite native body emission -> consequence comparison -> source access.

Expectation is never read and re-injected. The body and its entire adapter
coexist before T0. Consequence is an independently observed explicit binary
report (two present physical codes), not Python inference from a timeout.
"""
from pathlib import Path
import json
import dee_thinking as d
from core.comparison import coordinate,plus,make_placement,make_interface,observed


def local_context(w,site):
    return [observed(w.runtime.observe(coordinate(plus(site,(x,y,z)))))
            for x in (-1,0,1) for y in (-1,0,1) for z in (-1,0,1)]


def capture(w,m):
    t=w.runtime.current_tick;p=w.view('body').observe();pts=w.view('adapter').spec.ports
    row={'tick':t,'delta':p.delta,'centers_available':p.centers_available,'supports_intact':p.supports_intact,
         'ports':{k:observed(w.runtime.observe(q)) for k,q in pts.items()}}
    # These are geometric reference paths, not externally imposed identities.
    # Observed deviations are retained; no emitter or signal is moved.
    if 37<=t<=m['arrival_tick']:
        row['geometric_fronts']={str(e):observed(w.runtime.observe(coordinate(
                plus(m['read_target'],(e,1,0),t-37)))) for e in (-1,1)}
    if t in (37,38,m['arrival_tick']-1,m['arrival_tick'],m['arrival_tick']+3,
             m['arrival_tick']+4,m['arrival_tick']+8,m['arrival_tick']+9):
        row['local_context']={k:local_context(w,q) for k,q in m['hubs'].items()}
    return row


def decode_current_state(w,m):
    """Passive fixed presentation; does not consult history or hidden context.

    Addresses and declared read windows are interface metadata. Returned
    substantive values are exclusively current physical records. Outside a
    window, no terminal result is fetched from a log or response table.
    """
    tick=w.runtime.current_tick
    body=observed(w.runtime.observe(coordinate(m['read_target'])))
    prediction=None
    if body['active'] and body['direction'][1:]==[1,0]:
        prediction=1 if body['direction'][0]>0 else -1 if body['direction'][0]<0 else None
    comparisons=[];accesses=[]
    if tick==m['arrival_tick']:
        for tag,site in m['hubs'].items():
            o=observed(w.runtime.observe(coordinate(site)))
            if o['active'] and o['direction'][1:]==[1,1]:
                dx=o['direction'][0]
                comparisons.append({'port':tag,'physical_output':o,
                    'presentation':'coincidencia' if dx==0 else 'discrepancia_positiva' if dx>0 else 'discrepancia_negativa'})
    if tick==m['arrival_tick']+9:
        for key,info in m['branches'].items():
            o=observed(w.runtime.observe(coordinate(info['access'])))
            if o['active'] and o['direction'][0]!=0 and o['direction'][1:]==[1,0]:
                accesses.append({'port':key,'source':info['source'],'physical_output':o,
                    'interface_information_load':o['load']-37,
                    'accounting':'Native expectation7 + consequence17 + common query13 = fixed transport37; not an oracle'})
    return {'tick':tick,'current_prediction':prediction,'current_body_output':body,
            'current_comparison_products':comparisons,'current_information_products':accesses,
            'comparison_window':m['arrival_tick'],'information_window':m['arrival_tick']+9,
            'operational_forks':0,'mode':'PASSIVE_OBSERVATION_AND_FIXED_PRESENTATION',
            'not_claimed':'Optimal informative-source policy or rewrite/relearning after this encounter'}


def prepare_native_loop(*,origin=(15,15,15),context=0,report=23,consequence=1,
                        history='AB',query=True,consequence_enabled=True,
                        selected_cut=None,distance=10,source_enabled=True):
    if consequence not in (-1,1) or context not in (0,1):raise ValueError('Finite signed domain')
    r=d.OrganizationRecipe.relational(d.reference_seed_path(),d.BasalHistory.H0,False,coordinate(origin))
    r.execution=d.TickOptions(d.Backend.LAZY,1)
    placements=[make_placement(plus(origin,(0,2,1)),0,(0,0,0),state=7000,
                               semantic=4,clock=71,role='finite_initial_reader_support')]
    target=plus(origin,(0,1,0));inlet=plus(origin,(0,3,0))
    first_emission=37;arrival=first_emission+distance
    meta={'origin':list(origin),'read_target':list(target),'read_inlet':list(inlet),
          'first_expected_emission_tick':first_emission,'arrival_tick':arrival,
          'history':history,'consequence':consequence,'context':context,'report':report,
          'query_enabled':query,'consequence_enabled':consequence_enabled,
          'selected_cut':selected_cut,'distance':distance,'hubs':{},'branches':{},
          'scope':'Native learned relational emission compared physically; finite information-access adapter',
          'consequence_codec':'External actual observed explicit binary report, not computed forecast error'}
    channels=[];ports={'body_output':coordinate(target)}
    for e in (-1,1):
        h=plus(target,(e,1,0),distance);tag='negative' if e<0 else 'positive'
        meta['hubs'][tag]=list(h);ports[tag+'_meeting']=coordinate(h)
        cd=(-consequence,0,1);src=plus(h,cd,-4)
        channels.append(make_interface('observed_consequence.'+tag,src,cd))
        # A common query is installed in every candidate branch before T0.
        # It cannot inspect which sign will later be emitted by the body.
        for dx in (-1,0,1):
            kt=tag+'_'+str(dx);qt=plus(h,(dx,1,1),4);qd=(0,-1,-1)
            placements.append(make_placement(plus(qt,qd,-(arrival+4-32)),13,qd,
                                              role='prepared_common_future_query'))
            ports[kt+'_query']=coordinate(qt)
            if dx:
                action=(dx,0,0);it=plus(qt,action,5)
                source='Q' if dx>0 else 'P';informative='P' if context==0 else 'Q'
                load=report if source==informative else 5
                if source_enabled and selected_cut!=source:
                    placements.append(make_placement(plus(it,(0,1,0),-(arrival+9-32)),load,(0,1,0),
                                                      role='prepared_information_'+source))
                ports[kt+'_'+source+'_access']=coordinate(it)
                meta['branches'][kt]={'source':source,'query':list(qt),'access':list(it),
                                      'informative':source==informative,'source_load':load}
    r.placements=placements
    s=d.OrganizationSpec();s.id='adapter';s.recipe_id='native_binary_feedback_adapter.cpc3.v1';s.ports=ports
    r.organizations=[s]
    w=d.OrganizationalWorld.create(r)
    # Recipe construction also appends its body view; all views share one
    # Runtime. Declaring interfaces installs no physical material.
    for c in channels:w.declare_interface(c)
    spec=w.view('body').spec
    for name,center,offset,dr in [('A',spec.a,(0,-1,0),(0,0,-1)),
                                 ('B',spec.b,(0,1,0),(0,0,1))]:
        q=(center.x,center.y,center.z)
        w.declare_interface(make_interface('sensor.'+name,plus(q,offset),dr))
    w.declare_interface(make_interface('read.offaxis',inlet,(0,-1,0)))
    return w,meta


def run_native_loop(spec,output):
    w,m=prepare_native_loop(**spec);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    w.save_snapshot(str(output/'T0.deetsnap'));trace=[];receipts=[];writes=[]
    history={'AB':['A','B'],'BA':['B','A'],'H0':[]}[m['history']]
    horizon=m['arrival_tick']+16
    while w.runtime.current_tick<=horizon:
        t=w.runtime.current_tick
        if t in (32,33) and t-32<len(history):
            name='sensor.'+history[t-32];rr=w.submit(name,0,t);receipts.append(rr.id)
            writes.append({'tick':t,'interface':name,'load':0,'modality':'EXPERIENCE_PROTOCOL'})
        if t==34 and m['query_enabled']:
            rr=w.probe('read.offaxis',7,t);receipts.append(rr.id)
            writes.append({'tick':t,'interface':'read.offaxis','load':7,'modality':'PHYSICAL_PROBE_ON_MAIN'})
        if t==m['arrival_tick']-4 and m['consequence_enabled']:
            for tag in ('negative','positive'):
                name='observed_consequence.'+tag;rr=w.submit(name,17,t);receipts.append(rr.id)
                writes.append({'tick':t,'interface':name,'load':17,'modality':'OBSERVED_EXTERNAL_EXPLICIT_REPORT'})
        trace.append(capture(w,m))
        if t in (34,37,m['arrival_tick'],m['arrival_tick']+9):
            w.save_snapshot(str(output/('T'+str(t)+'.deetsnap')))
        if t==horizon:break
        w.advance()
    w.save_snapshot(str(output/'FINAL.deetsnap'))
    result={'metadata':m,'trace':trace,'host_writes':writes,
            'receipts':[{'id':i,'status':str(w.runtime.receipt(i).status),
                         'requested_tick':w.runtime.receipt(i).requested_tick,
                         'effective_tick':w.runtime.receipt(i).effective_tick,
                         'reason':w.runtime.receipt(i).reason} for i in receipts],
            'external_operations':list(w.external_operations),
            'operational_forks':0,'postT0_direct_RAW_or_clock_edits':0,
            'limits':'Multiple native reader emissions and context may overlap; parentage is not assigned by equal load alone'}
    (output/'MEASUREMENTS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result
