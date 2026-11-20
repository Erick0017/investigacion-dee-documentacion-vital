"""Verify transitions already recorded, without computing a new trajectory."""
import gzip,json
from collections import Counter
from leer_estado import fields,frame_arrays,index

def examine(ix,objects):
    stream=next(e for e in ix['entries']if e['id']=='PC/PROCEDENCIA_01/reference_trace/stream')
    lines=gzip.decompress(objects[stream['member']]).splitlines();previous=None;trace=Counter();fail=[];first=None;last=None
    for line in lines:
        f=json.loads(line);r,c=frame_arrays(f);t=f['tick'];q=[(t+23)%67,11,11];v=fields(r[index(q,67)])
        trace['whole_field_frames_verified']+=1
        if first is None:first=t
        last=t
        if not(v['state']==1 and v['semantic']==1 and v['s_reg']==5 and v['direction']==[1,0,0]):fail.append({'tick':t,'site':q,'observed':v})
        if previous:
            pt,pr,pc,pq=previous
            if t==pt+1:
                incoming=[]
                for dx in(-1,0,1):
                    for dy in(-1,0,1):
                        for dz in(-1,0,1):
                            if(dx,dy,dz)==(0,0,0):continue
                            site=[(q[j]+[dx,dy,dz][j])%67 for j in range(3)];raw=pr[index(site,67)];d=fields(raw)['direction']
                            if d!=[0,0,0]and[(site[j]+d[j])%67 for j in range(3)]==q:incoming.append({'site':site,'raw':str(raw)})
                if len(incoming)==1 and incoming[0]['site']==pq and int(incoming[0]['raw'])==r[index(q,67)]and pr[index(q,67)]==0:
                    trace['unique_incoming_empty_destination_links']+=1
                else:fail.append({'tick':t,'incoming':incoming,'destination_pre':str(pr[index(q,67)])})
                trace['consecutive_links']+=1
                if pq[0]==66 and q[0]==0:trace['observed_x_boundary_crossings']+=1
                if t>=first+67:trace['observed_spatial_revisits_after_67_ticks']+=1
            else:trace['gaps']+=1
        previous=(t,r,c,q)
    window={'from':first,'to':last,'counts':dict(trace),'unresolved_links_or_mismatches':fail,'scope':'Bounded unique directional-source links in existing full fields, not proof of unique ancestry across the unrecorded intervals back to T476 or forward to T45028. Clocks advance, so spatial revisits are not identical microstates.'}
    routes=[]
    for e in ix['entries']:
        if e['role']!='recorded_route_stream':continue
        rows=[json.loads(line)for line in gzip.decompress(objects[e['member']]).splitlines()];edges=Counter();cross=[0,0,0];bad=[];multi=[];prev=None;not_parent=[];candidate_chain=0;longest=0;suffix_from=None;suffix_cross=[0,0,0]
        for q in rows:
            s=q['source_candidate'];d=fields(int(s['raw']))['direction'];target=[(s['site'][j]+d[j])%67 for j in range(3)]
            if q['post_tick']!=q['pre_tick']+1:bad.append(['time',q['pre_tick']])
            parent=any(z['site']==s['site']and z['raw']==s['raw']for z in q['incoming_sources'])and target==q['destination']
            if parent and q['edge'].startswith('EXACT_'):
                if candidate_chain==0:suffix_from=q['pre_tick'];suffix_cross=[0,0,0]
                candidate_chain+=1;longest=max(longest,candidate_chain)
                for j in range(3):suffix_cross[j]+=abs(q['crossings_candidate'][j])
            else:
                not_parent.append(q['pre_tick']);candidate_chain=0;suffix_from=None;suffix_cross=[0,0,0]
            for j in range(3):cross[j]+=abs(q['crossings_candidate'][j])
            edges[q['edge']]+=1
            if q['edge']=='EXACT_EMPTY_TRANSPORT':
                if len(q['incoming_sources'])!=1 or q['post']['raw']!=q['incoming_sources'][0]['raw']:bad.append(['transport',q['pre_tick']])
            elif q['edge']=='EXACT_MULTIPARENT_REDUCER':
                fs=[fields(int(z['raw']))for z in q['incoming_sources']];post=fields(int(q['post']['raw']));sreg=min(sum(z['s_reg']for z in fs),19664);vector=[(v>0)-(v<0)for v in[sum(z['direction'][j]for z in fs)for j in range(3)]]
                if post['s_reg']!=sreg or post['direction']!=vector:bad.append(['reducer',q['pre_tick']])
                multi.append({'tick':q['post_tick'],'site':q['destination'],'parents':q['incoming_sources'],'post':q['post']})
            prev=q
        routes.append({'id':e['id'],'candidate_projection_steps':len(rows),'from':rows[0]['pre_tick'],'to':rows[-1]['post_tick'],'recorded_edges':dict(edges),'candidate_projection_boundary_crossings_by_axis_NOT_LINEAGE':cross,'candidate_not_a_physical_parent_count':len(not_parent),'candidate_not_a_physical_parent_ticks':not_parent,'longest_candidate_as_parent_chain':longest,'final_verified_candidate_chain':{'from':suffix_from,'to':rows[-1]['post_tick'],'steps':candidate_chain,'boundary_crossings_by_axis':suffix_cross},'actual_incoming_algebra_errors':bad,'multiparent_events':multi,'scope':'A valid destination transport need not originate at source_candidate. The original tracer explicitly labelled that coordinate as a hypothesis, not an identity.'})
    return window,routes
