"""New T0 candidate only: recurrent generic support for an ephemeral B reader."""
from capacidades.geometria_distribuida_mi02_r6 import unified_recipe as baseline
from capacidades.geometria_distribuida_mi02 import compile_geometry
from capacidades.distribucion_social_mi02_r2 import SUPPORT

def unified_recipe(control='intact'):
    base_control='intact'if control=='no_refresh_source'else control
    _,g=baseline(base_control);N=g['N'];B=g['B']
    def p(v):return tuple((B[i]+v[i])%N for i in range(3))
    anchors={tuple(x['site']):(x['load'],tuple(x['direction']))for x in g['anchors']};opened={tuple(x)for x in g['opened']};pinned={tuple(x)for x in g['pinned']}
    for v in SUPPORT:
        anchors.pop(p(v),None);opened.add(p(v))
    for v,load in[((-1,0,1),2),((0,0,1),0),((1,0,1),0)]:anchors[p(v)]=(load,(0,0,0))
    for r in(-1,1):
        for v in((2*r,1,1),(2*r,2,1),(r,2,1),(0,2,1)):anchors[p(v)]=(0,(0,0,0))
    datum=p((1,-1,1));source=p((1,-1,2));stop=p((1,-1,0));opened.add(datum);pinned.add(stop)
    if control!='no_refresh_source':anchors[source]=(0,(0,0,-1))
    else:opened.add(source)
    g.update({'schema':'MI02.unified.r7','control':control,'B_reader':'Five coplanar baseline neighbours. A prepared generic zero-load SEM4 source supplies the sixth neighbour on alternate ticks; no private code is supplied by it. Reader decay and readmission are to be measured, not assumed.','B_refresh':{'source':list(source),'target':list(datum),'stop':list(stop),'load':0,'direction':[0,0,-1]},'anchors':[{'site':list(k),'load':v[0],'direction':list(v[1])}for k,v in sorted(anchors.items())],'opened':[list(x)for x in sorted(opened)],'pinned':[list(x)for x in sorted(pinned)],'hypothesis':'Repeated native queries can activate, use and release B without host clearing. Own A learned consequences and B private relation remain physically coupled.','new_preparation_not_MAIN_repair':True})
    return compile_geometry(N,opened,anchors,pinned),g
