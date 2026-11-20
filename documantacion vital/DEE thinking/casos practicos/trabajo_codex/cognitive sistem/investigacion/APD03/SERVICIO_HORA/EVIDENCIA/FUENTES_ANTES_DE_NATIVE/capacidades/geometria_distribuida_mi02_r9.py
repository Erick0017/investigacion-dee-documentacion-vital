"""R9 new preparation: prevent the removed-frame gap from birthing a sixth support."""
from capacidades.geometria_distribuida_mi02_r8 import unified_recipe as baseline
from capacidades.geometria_distribuida_mi02 import compile_geometry
from capacidades.distribucion_social_mi02_r2 import SUPPORT

def unified_recipe(control='intact'):
    _,g=baseline(control);N=g['N'];B=g['B'];anchors={tuple(x['site']):(x['load'],tuple(x['direction']))for x in g['anchors']};opened={tuple(x)for x in g['opened']};pinned={tuple(x)for x in g['pinned']}
    changed=[]
    for v in SUPPORT:
        p=tuple((B[i]+v[i])%N for i in range(3))
        if p not in anchors:
            opened.discard(p);pinned.add(p);changed.append(list(p))
    g.update({'schema':'MI02.unified.r9','removed_frame_gaps_pinned_from_T0':changed,'opened':[list(p)for p in sorted(opened)],'pinned':[list(p)for p in sorted(pinned)],'hypothesis':'Saved-state diagnostic43 located a new alive middle support at B+(0,1,1), initially raw0. R9 uses native inert SEM4 boundary at removed frame positions, exactly as the auxiliary ephemeral preparation. This is external anatomy at newT0, never cleaning an existing life.','new_preparation_not_recovery_of_R8':True})
    return compile_geometry(N,opened,anchors,pinned),g
