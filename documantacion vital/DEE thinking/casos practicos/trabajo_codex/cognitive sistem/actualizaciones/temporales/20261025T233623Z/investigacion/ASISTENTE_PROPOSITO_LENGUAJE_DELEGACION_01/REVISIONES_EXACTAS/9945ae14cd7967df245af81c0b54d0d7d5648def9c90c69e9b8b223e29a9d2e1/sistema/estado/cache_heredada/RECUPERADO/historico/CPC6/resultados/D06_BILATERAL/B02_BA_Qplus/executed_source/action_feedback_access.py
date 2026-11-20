"""Fixed physical alias admission, independent of participant state/results.

All logical lanes remain observable. Identical simultaneous physical requests
are one external intervention, not multiple competing events. Nonidentical
requests are deliberately retained for Runtime admission to decide.
"""


def deduplicate_requests(world,requests):
    """Return {requests, groups}; examine public interface declarations ONLY.

    Does not read RAW, clocks, receipts, history, source values or predictions.
    Key: site, direction, state, semantic, requested tick, payload and kind.
    Logical aliases with different request data are not silently resolved.
    """
    specs={item.name:item for item in world.interfaces}
    kept=[];groups=[];seen={}
    for index,request in enumerate(requests):
        name=request['port']
        if name not in specs:raise ValueError('Unknown declared interface '+name)
        item=specs[name];c=item.channel;p=c.injection_site;v=c.direction
        payload=request['payload'];tick=request['tick'];kind=request.get('kind','submit')
        if type(payload) is not int or type(tick) is not int:raise TypeError('Exact integer request data required')
        if kind not in ('submit','probe'):raise ValueError('Only declared physical requests')
        key=((p.x,p.y,p.z),(v.dx,v.dy,v.dz),c.state,c.semantic,tick,payload,kind)
        if key not in seen:
            seen[key]=len(groups);kept.append(dict(request))
            groups.append({'canonical_port':name,'canonical_request_index':index,
               'physical_key':{'site':list(key[0]),'direction':list(key[1]),'state':c.state,
                  'semantic':c.semantic,'tick':str(tick),'payload':payload,'kind':kind},
               'logical_requests':[{'index':index,'port':name}]})
        else:groups[seen[key]]['logical_requests'].append({'index':index,'port':name})
    return {'requests':kept,'groups':groups,'requested_count':sum(len(g['logical_requests']) for g in groups),
            'physical_request_count':len(kept),
            'scope':'Exact public-channel aliases only. No participant state inspection; nonidentical host conflicts remain for Runtime.'}
