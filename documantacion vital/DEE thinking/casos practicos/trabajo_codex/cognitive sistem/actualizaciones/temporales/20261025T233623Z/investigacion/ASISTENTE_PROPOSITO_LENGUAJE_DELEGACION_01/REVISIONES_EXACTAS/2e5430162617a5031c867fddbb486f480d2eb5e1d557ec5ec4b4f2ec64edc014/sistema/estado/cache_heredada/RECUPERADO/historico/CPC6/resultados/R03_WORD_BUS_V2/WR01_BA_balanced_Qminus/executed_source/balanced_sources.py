"""Equal-charge, equal-contributor Q data codec for a reserved new history.

Two acquired source products in BOTH directions. Only a vector differs, not
total source load. An input codec describes a present observation; it never
examines a forecast or computes the receiver's correct action.
"""
from common import interface,digest
from action_feedback import moved,source_protocol

def prepare(s):
    w=s.world;g=s.geometry['adapter'];before=digest(w);parts={}
    for key,b in g['branches'].items():
        info=b['sources']['Q']['information_site'];dr=(-1,0,0);hub=moved(info,dr,-20)
        base='balanced.source.'+key+'.Q.negative.1'
        pair=((0,-1,0),(-1,1,0))
        for label,direction in zip(('cue','event'),pair):
            w.declare_interface(interface(base+'.'+label,moved(hub,direction,-3),direction))
        parts[key]={'base':base,'hub':list(hub),'directions':[list(x) for x in pair],'loads':[5,19]}
    assert digest(w)==before
    s.geometry['balanced_source_codec']={'schema':'CPC6.balanced-Q.v1','parts':parts,
        'scope':'Q+ and Q- both have two paired acquired products, loads23+24. Each branch has its own exposures; no free replicas. P codec unchanged.',
        'registered_at':0,'physical_preparation_unchanged':True}

def protocol(s,values,mode='paired'):
    if values['Q']==1:return source_protocol(s.geometry['adapter'],values,mode=mode)
    if values['Q']!=-1:raise ValueError('Only current directional source values +/-1')
    g=s.geometry['adapter'];entries=source_protocol(g,values,mode=mode,omit=('Q',))
    for key,item in s.geometry['balanced_source_codec']['parts'].items():
        # First contributor is identical to Q+'s acquired first contributor.
        first=g['source_codecs'][key+'.Q.positive'][0]
        for part in (first,item):
            for label,load in zip(('cue','event'),part['loads']):
                entries.append({'port':part['base']+'.'+label,'payload':load,'tick':int(mode=='unpaired') if label=='cue' else 0,
                   'kind':'submit','origin':'BALANCED_CURRENT_SOURCE_CUE' if label=='cue' else 'BALANCED_CURRENT_SOURCE_EVENT'})
    return entries
