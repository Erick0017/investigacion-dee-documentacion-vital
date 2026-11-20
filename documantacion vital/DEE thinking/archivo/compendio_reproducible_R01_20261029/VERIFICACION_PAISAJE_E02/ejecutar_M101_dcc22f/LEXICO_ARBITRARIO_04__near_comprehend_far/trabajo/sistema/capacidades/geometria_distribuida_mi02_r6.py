"""R3 separates social context from motor and query ports in one N26 world."""
from types import SimpleNamespace
from capacidades import arquitectura_distribuida_mi02_r8 as n
from capacidades import distribucion_social_mi02_r2 as social
from capacidades.geometria_distribuida_mi02 import return_geometry,compile_geometry

def unified_recipe(control='intact'):
    if control not in('intact','cut_query','cut_message','cut_return','sham_query','no_gate_resource'):raise ValueError('Declared R3 physical control')
    N=26;A=[6,14,14];B=[19,14,14];f=SimpleNamespace(world=SimpleNamespace(runtime=SimpleNamespace(dimension=N)));opened=set();anchors={};pinned=set();sources=[]
    def pos(c,v,k=1):return tuple(n.xyz(f,c,v,k))
    def source(label,head,v,lag,load=0,ghost_stop=True):
        origin=pos(head,v,-lag);anchors[origin]=(load,tuple(v))
        for k in range(lag+1):opened.add(pos(origin,v,k))
        if ghost_stop:pinned.add(pos(head,v))
        sources.append({'id':label,'site':list(origin),'head':list(head),'direction':list(v),'distance':lag,'load':load,'prepared_native_recurrent_source':True})
    def wire(head,v,length):
        for k in range(length+1):opened.add(pos(head,v,k))
    for C in(A,B):
        for v in social.SUPPORT:anchors[pos(C,v)]=(1 if v in((-1,0,1),(-1,1,0))else 0,(0,0,0))
        for v in((0,0,0),(-1,1,1),(1,1,1)):opened.add(pos(C,v))
    for sign in(-1,1):anchors[pos(B,(2*sign,2,2))]=(0,(0,0,0))
    rg=return_geometry(N,A,'cut_return'if control=='cut_return'else'intact',include_zero=True);opened.update(rg['opened']);anchors.update(rg['anchors']);pinned.update(rg['pinned'])
    # Two blank recipients retain whichever B sign actually arrives. Their
    # eight-neighbour support lies below A and outside local learned-memory
    # neighbourhoods. No payload or sign is prepared in either recipient.
    for r in(-1,1):
        for v in((2*r,0,-2),(2*r,1,-2),(2*r,2,-2),(2*r,2,-1),(2*r,1,-1)):anchors[pos(A,v)]=(0,(0,0,0))
    # B's reader is activated at odd ticks by the fixed query wire below.
    # Both signs have equal total travel length in this even torus.
    routes=[]
    for r in(-1,1):
        H=pos(B,(3*r,-3,-3));K=pos(B,(5*r,-3,-3));L=pos(B,(5*r,-1,-5));M=pos(B,(5*r,5,-5));C=pos(A,(-3*r,5,-5));J=pos(A,(0,2,-2))
        wire(B,(r,-1,-1),3);source('B.'+str(r)+'.first',H,(0,1,1),3);wire(H,(r,0,0),2)
        source('B.'+str(r)+'.rise',K,(-r,1,-1),3);wire(K,(0,1,-1),2)
        source('B.'+str(r)+'.vertical',L,(0,0,1),3);wire(L,(0,1,0),6)
        source('B.'+str(r)+'.bus',M,(r,-1,0),3);distance=(r*(C[0]-M[0]))%N;wire(M,(r,0,0),distance)
        source('B.'+str(r)+'.approach',C,(0,-1,1),4);wire(C,(r,-1,1),4)
        cut=pos(M,(r,0,0),max(2,distance//2))
        if control=='cut_message':anchors[cut]=(0,(0,0,0))
        routes.append({'sign':r,'first_turn':list(H),'second_turn':list(C),'heads':[list(v)for v in(H,K,L,M,C,J)],'bus_steps':distance,'context':list(pos(J,(r,-1,1))),'cut':list(cut)})
    # Query request x0 is separate from both motor directions. Gate resource
    # load5 is generic prepared matter, not B's private relation or a solution.
    points=[([6,11,11],(0,0,1),0,4,(0,-1,0),7),
            ([6,4,11],(1,1,1),0,3,(1,0,1),3),
            ([9,4,14],(0,0,-1),0,4,(1,0,0),7),
            ([16,4,14],(-1,1,0),0,3,(0,1,0),4),
            ([16,8,14],(1,0,0),0,3,(1,1,0),3),
            ([19,11,14],(-1,0,0),5,4,(0,1,0),3)]
    wire(A,(0,-1,-1),3);query=[]
    for j,(head,v,load,lag,out,length)in enumerate(points):
        source('query.'+str(j),head,v,lag,load,ghost_stop=True);wire(head,out,length);query.append({'stage':j,'head':head,'source':list(pos(head,v,-lag)),'source_direction':list(v),'source_load':load,'source_distance':lag,'outgoing':list(out),'outgoing_length':length})
        if j==5 and control=='no_gate_resource':anchors.pop(pos(head,v,-lag))
    query_cut=pos(A,(0,-1,-1),2)
    if control=='cut_query':anchors[query_cut]=(0,(0,0,0))
    if control=='sham_query':anchors[pos(query_cut,(0,0,1),7)]=(0,(0,0,0))
    sensors=[]
    for name,r,variable,scale in[('sin',-1,1,1),('cos',1,0,1)]:
        target=pos(A,(r,-1,1));origin=pos(target,(0,0,-1),-5);wire(origin,(0,0,-1),5);sensors.append({'name':name,'observation_index':variable,'scale':scale,'origin':list(origin),'direction':[0,0,-1],'target':list(target),'travel':5})
    target=pos(A,(0,-1,1));origin=pos(target,(0,0,-1),-5);wire(origin,(0,0,-1),5);sensors.append({'name':'omega','observation_index':2,'scale':8,'origin':list(origin),'direction':[0,0,-1],'target':list(target),'travel':5})
    conflicts=[{'site':list(p),'anchored':True}for p in sorted(pinned&set(anchors))]
    if conflicts:raise ValueError('Pinned ghost stop would erase prepared anchor '+str(conflicts))
    sg={'schema':'MI02.social_context_separated.r3','A':A,'B':B,'N':N,'control':control,'routes':routes,'history':[],'current_tick':0,'classification':'One compound A organization and a private-information B participant in a shared world. Prepared context channels, not an external coordinator.'}
    g={'schema':'MI02.unified.r6','N':N,'A':A,'B':B,'social':sg,'query':query,'control':control,'query_cut':list(query_cut),'external_sensors':sensors,'prepared_sources':sources,'opened':[list(p)for p in sorted(opened)],'pinned':[list(p)for p in sorted(pinned)],'anchors':[{'site':list(k),'load':v[0],'direction':list(v[1])}for k,v in sorted(anchors.items())],'prepared':'Blank persistent context recipients with supports outside Q/local-memory neighbourhoods. Social bus approaches from outside their support plane. Motors and transient sensory ports are spatially distinct. Generic native sources contain no private sign.','hypothesis':'Own failed-action consequences can initiate query; acquired private B content then travels around the receiver-support obstruction and combines with A history.','limits':'Dual-role x0 is not an exclusive learned act-versus-ask policy. Persistent sign recipients do not imply arbitrary content overwrite or general missing-information detection.'}
    return compile_geometry(N,opened,anchors,pinned),g
