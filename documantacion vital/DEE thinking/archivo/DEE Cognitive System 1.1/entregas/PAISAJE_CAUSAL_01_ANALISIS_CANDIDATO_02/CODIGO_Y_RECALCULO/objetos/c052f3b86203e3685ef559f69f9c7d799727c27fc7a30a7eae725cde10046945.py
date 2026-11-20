"""Engine-free ancestry recalculation WITH admitted input-boundary writes.

This corrects the possible omission of freshly admitted material from a
pre-boundary RAW frame. It does not change any trajectory or decoder.
"""
from pathlib import Path
from collections import defaultdict,Counter
import argparse,gzip,json,sys,math
sys.path.insert(0,str(Path(__file__).parent))
from instrumentos_pc01 import packed,idx,coord,sha
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);a=p.parse_args();root=a.evidence;agenda=json.loads((root/'AGENDAS_Y_CANALES_20/passive/PRIMARIOS.json').read_bytes())['states'];out={'schema':'PC01.admitted.inputs.ancestry.v1','not_time_inversion':True,'cases':{}}
def requests(value,found):
    if isinstance(value,dict):
        if type(value.get('id'))is int and type(value.get('payload'))is int and('port'in value or'channel'in value):
            eid=value['id'];port=value.get('port',value.get('channel'));row={'id':eid,'port':port,'payload':value['payload']}
            if eid in found and found[eid]!=row:raise ValueError('Conflictingrequestlog')
            found[eid]=row
        for k,v in value.items():
            if k not in('parent','commit'):requests(v,found)
    elif isinstance(value,list):
        for v in value:requests(v,found)
def pack_input(c,L):
    v=c['state']|L<<32|c['semantic']<<60
    for b,k in zip(c['direction'],(48,52,56)):v|=(b&15)<<k
    return str(v)
def admitted(prim,parent,child):
    ps=agenda[parent]['queue_state'];cs=agenda[child]['queue_state'];new={};requests(prim,new);writes=defaultdict(list);missing=[];initial={r['id']:r for r in ps['pending']};newids=[]
    for r in agenda[child]['receipts']:
        eid=r['id']
        if r['status']!='applied':continue
        if eid in initial:
            for w in initial[eid]['writes']:writes[r['effective_tick']].append({**w,'id':eid,'origin':'INITIAL_PENDING_COMPLETE_NATIVE_QUEUE'})
        elif eid>=ps['next_event_id']:
            newids.append(eid)
            if eid not in new:missing.append(eid);continue
            q=new[eid];c=cs['channels'][q['port']];writes[r['effective_tick']].append({'site':c['site'],'raw':pack_input(c,q['payload']),'id':eid,'port':q['port'],'payload':q['payload'],'origin':'APPLIED_RECEIPT_PLUS_EXECUTED_REQUEST_AND_NATIVE_CHANNEL'})
    return writes,{'new_applied_count':len(newids),'missing_payload_records':missing,'initial_pending_count':len(initial),'request_records':len(new),'native_parent_snapshot_sha256':ps['native_snapshot_sha256'],'native_child_snapshot_sha256':cs['native_snapshot_sha256']}
for label,parent,child,folder in(('reference','ES01_MAIN_04','PC01_ORIGEN01_reference_trace','PROCEDENCIA_01/reference_trace'),('near','ES01_LONG7_D_no_material_queries','PC01_ORIGEN01_near_trace','PROCEDENCIA_01/near_trace'),('early','ES01_MAIN_05','PC01_INFLUENCIA04_early','INFLUENCIA_ANTERIOR_04/early'),('long','ES01_LEXICAL5_source_guards_strict','PC01_INFLUENCIA04_long','INFLUENCIA_ANTERIOR_04/long')):
    base=root/folder;prim=json.loads((base/'PRIMARIOS.json').read_bytes());writes,coverage=admitted(prim,parent,child);case={'coverage':coverage,'applied_boundary_writes':dict(writes),'source':{'path':str(base/'PRIMARIOS.json'),'sha256':sha(base/'PRIMARIOS.json')}}
    if label in('early','long'):
        counts=Counter();changes=[]
        with gzip.open(base/'RUTA_CANDIDATA.jsonl.gz','rt',encoding='utf8')as f:
            for line in f:
                r=json.loads(line);t=r['pre_tick'];dest=r['destination'];n=67;incoming={tuple(v['site']):v for v in r['incoming_sources']};pre=r['destination_pre'];overlay=[]
                for w in writes.get(t,[]):
                    q=w['site'];v=packed(int(w['raw']));item={'site':q,**v,'admitted_input_id':w['id']}
                    if q==dest:pre=item
                    if any(v['direction'])and all(abs(d)<=1 for d in v['direction'])and[(q[k]+v['direction'][k])%n for k in range(3)]==dest:incoming[tuple(q)]=item;overlay.append(item)
                values=list(incoming.values());sums=[sum(q['direction'][k]for q in values)for k in range(3)];d=values[0]['direction']if len(values)==1 else[(z>0)-(z<0)for z in sums];L=min(19664,sum(q['s_reg']for q in values));post=r['post'];exact=pre['state']==0 and pre['semantic']!=4 and bool(values)and post['state']==1 and post['semantic']==1 and post['direction']==d and post['s_reg']==L and L<19664
                new='EXACT_EMPTY_TRANSPORT'if exact and len(values)==1 else'EXACT_MULTIPARENT_REDUCER'if exact else'OCCUPIED_CONTEXT'if pre['state']else'NO_EXACT_EMPTY_EDGE';counts[new]+=1
                if new!=r['edge']or overlay:changes.append({'tick':r['post_tick'],'old_class':r['edge'],'input_complete_class':new,'new_contributors':overlay,'destination':dest})
        case['input_complete_edge_counts']=dict(counts);case['changed_or_enriched_edges']=changes
    if label=='reference':
        with gzip.open(base/'CAMPO_COMPLETO.jsonl.gz','rt',encoding='utf8')as f:fr=next(r for line in f if(r:=json.loads(line))['tick']==9919)
        raw={i:int(v)for i,v,c in fr['rows']};site=[50,35,36];readset=[]
        for dx in(-1,0,1):
            for dy in(-1,0,1):
                for dz in(-1,0,1):
                    if(dx,dy,dz)!=(0,0,0):
                        q=[(site[0]+dx)%67,(site[1]+dy)%67,(site[2]+dz)%67];v=packed(raw.get(idx(q,67),0));readset.append({'offset':[dx,dy,dz],'site':q,**v})
        tests={}
        for mode in('all_admitted','omit_only_material_probe'):
            rs=[dict(r)for r in readset]
            for w in writes.get(9919,[]):
                if mode=='omit_only_material_probe'and w.get('port','').endswith('material_probe1'):continue
                for r in rs:
                    if r['site']==w['site']:r.update(packed(int(w['raw'])))
            n=sum(r['state']>0 and r['semantic']!=5 for r in rs);grad=[-sum(r['offset'][k]*r['s_reg']for r in rs if r['state']>0)for k in range(3)];rule=(5*n+26)//52
            tests[mode]={'active_neighbors':n,'gradient':grad,'ordinary_no_tetra_rule_value':rule,'current_record':packed(raw[idx(site,67)]),'nonzero_neighbors':[r for r in rs if r['raw']!='0'],'tetra_caveat':'AxisXneighborsareabsent, excludingalltetra_patterns; ordinary2.5tensionapplies. Radius3savedinphysicalcontrols.'}
        case['source_gate_9919']=tests
    out['cases'][label]=case
dest=root/'ADMISIONES_Y_LINAJES_21.json';dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:{'coverage':v['coverage'],'edge_counts':v.get('input_complete_edge_counts'),'enriched_edges':len(v.get('changed_or_enriched_edges',[])),'gate':{g:{z:r[z]for z in('active_neighbors','gradient','ordinary_no_tetra_rule_value')}for g,r in v.get('source_gate_9919',{}).items()}}for k,v in out['cases'].items()}))
