"""A finite in-Runtime habitat for comparison-conditioned information access.

Context controls which source physically carries the world report. It does
not select the native action; the comparison product's direction does that.
No optimal-policy, renewable-organism or closed-loop claim is made here.
"""
from pathlib import Path
import json
import dee_thinking as d
from core.comparison import (coordinate,plus,make_interface,make_placement,
                             physical_comparison_code,observed)


def prepare(expected,consequence,*,context=0,report=23,hub=(23,23,23),
            arrival_tick=8,loads=(30,100),omit=None,query_cut=False,
            source_cut=None,n=47):
    if context not in (0,1):raise ValueError('Two finite contexts are published')
    if not(1<=report<=500):raise ValueError('Report outside finite context domain')
    e,c=physical_comparison_code(expected,consequence)
    r=d.OrganizationRecipe.research(n,[],0);r.execution=d.TickOptions(d.Backend.LAZY,1)
    r.interfaces=[make_interface('expectation',plus(hub,e,-arrival_tick,n),e),
                  make_interface('consequence',plus(hub,c,-(arrival_tick-4),n),c)]
    placements=[];ports={'meeting':coordinate(hub)};branches={}
    # All renewal/query mediators are preinstalled in all three potential
    # branches; they are never chosen by the host after the comparison.
    for name,dx in [('equal',0),('positive',1),('negative',-1)]:
        target=plus(hub,(dx,1,1),4,n);ports[name+'_query']=coordinate(target)
        qd=(0,-1,-1);src=plus(target,qd,-(arrival_tick+4),n)
        if not query_cut:placements.append(make_placement(src,13,qd,role='common_future_query'))
        if dx:
            action=(dx,0,0);target2=plus(target,action,5,n)
            # A positive discrepancy chooses Q; a negative one chooses P.
            source_name='Q' if dx>0 else 'P';informative='P' if context==0 else 'Q'
            payload=report if source_name==informative else 5
            info_dir=(0,1,0);info_src=plus(target2,info_dir,-(arrival_tick+9),n)
            if source_cut!=source_name:
                placements.append(make_placement(info_src,payload,info_dir,role='prepared_source_'+source_name))
            ports[source_name+'_access']=coordinate(target2)
            branches[source_name]={'query':list(target),'access':list(target2),
                                  'source':list(info_src),'payload':payload,
                                  'informative':source_name==informative,
                                  'candidate_action_direction':list(action)}
    r.placements=placements
    spec=d.OrganizationSpec();spec.id='selection';spec.recipe_id='comparison_information_access.cpc3.v1'
    spec.ports=ports;r.organizations=[spec]
    w=d.OrganizationalWorld.create(r)
    return w,{'context':context,'report':report,'expected':expected,'consequence':consequence,
              'hub':list(hub),'arrival_tick':arrival_tick,'loads':list(loads),
              'omit':omit,'query_cut':query_cut,'source_cut':source_cut,
              'branch_contract':branches,'external_codec_directions':[list(e),list(c)],
              'scope':'Finite native comparison -> shared physical query -> native routing -> source encounter',
              'not_claimed':'Learning an arbitrary informative-source policy or autonomous expectation generation'}


def run_case(spec,output):
    w,m=prepare(**spec);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    w.save_snapshot(str(output/'T0.deetsnap'));trace=[];receipts=[]
    for t in range(m['arrival_tick']+14):
        for name,at,j in [('expectation',0,0),('consequence',4,1)]:
            if t==at and m['omit']!=name:receipts.append(w.submit(name,m['loads'][j],at).id)
        ports=w.view('selection').spec.ports
        trace.append({'tick':t,'ports':{k:observed(w.runtime.observe(q)) for k,q in ports.items()}})
        if t in (m['arrival_tick'],m['arrival_tick']+4,m['arrival_tick']+9):
            w.save_snapshot(str(output/('T'+str(t)+'.deetsnap')))
        if t<m['arrival_tick']+13:w.advance()
    read=next(x for x in trace if x['tick']==m['arrival_tick']+9)['ports']
    # A coupled source product must have the physical action's horizontal
    # component AND information mediator's positive y component.
    hits=[]
    for name in ('P','Q'):
        o=read[name+'_access'];dr=o['direction']
        if o['active'] and dr[1]==1 and dr[0] in (-1,1):
            hits.append({'source':name,'native_output':o,
                         'source_payload_field':o['load']-(sum(m['loads'])+13),
                         'derivation':'Fixed accounting of prior participant loads, not an expected answer'})
    result={'metadata':m,'trace':trace,'source_products':hits,
            'receipts':[{'id':i,'status':str(w.runtime.receipt(i).status),'reason':w.runtime.receipt(i).reason}
                        for i in receipts],
            'final_tick':w.runtime.current_tick,'external_operations':list(w.external_operations),
            'writes_after_T0':[{'kind':'EXPERIENCE_PROTOCOL','interface':name,'tick':tick,'load':m['loads'][j]}
                              for name,tick,j in [('expectation',0,0),('consequence',4,1)] if m['omit']!=name],
            'interpretive_limit':'Routing changed with physical comparison history; utility mapping remains designed, not acquired'}
    w.save_snapshot(str(output/'FINAL.deetsnap'))
    (output/'MEASUREMENTS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result
