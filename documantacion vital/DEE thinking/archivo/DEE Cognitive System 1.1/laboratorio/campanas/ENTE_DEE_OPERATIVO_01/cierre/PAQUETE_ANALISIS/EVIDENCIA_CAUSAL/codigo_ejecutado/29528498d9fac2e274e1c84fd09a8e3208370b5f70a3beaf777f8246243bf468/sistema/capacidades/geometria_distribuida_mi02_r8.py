"""Separate neutral reader resource from the generic social code carrier load."""
from capacidades.geometria_distribuida_mi02_r7 import unified_recipe as baseline
from capacidades.geometria_distribuida_mi02 import compile_geometry

def unified_recipe(control='intact'):
    _,g=baseline('intact'if control=='no_private_history'else control)
    anchors={tuple(x['site']):(x['load'],tuple(x['direction']))for x in g['anchors']}
    gate=g['query'][-1];p=tuple(gate['source']);anchors[p]=(0,anchors[p][1]);gate['source_load']=0
    for x in g['prepared_sources']:
        if x['id']=='query.5':x['load']=0
        if x['id']in('B.-1.first','B.1.first'):
            p=tuple(x['site']);anchors[p]=(5,anchors[p][1]);x['load']=5
    g.update({'schema':'MI02.unified.r8','control':control,'anchors':[{'site':list(k),'load':v[0],'direction':list(v[1])}for k,v in sorted(anchors.items())],'prepared':'R7-derived NEW T0 geometry. A neutral zero-load B reader is initiated by the native query; both symmetric first-turn sources add the same generic5 only after the private-dependent output is formed. No remembered sign is in those supplies.','hypothesis':'The neutral B reader can release its site after native computation while its outgoing sign receives a generic transport load5. Separation of content and reading resource may permit recurrent use. R7 did NOT empty its5load reader; that failed hypothesis is retained.'})
    return compile_geometry(g['N'],g['opened'],anchors,g['pinned']),g
