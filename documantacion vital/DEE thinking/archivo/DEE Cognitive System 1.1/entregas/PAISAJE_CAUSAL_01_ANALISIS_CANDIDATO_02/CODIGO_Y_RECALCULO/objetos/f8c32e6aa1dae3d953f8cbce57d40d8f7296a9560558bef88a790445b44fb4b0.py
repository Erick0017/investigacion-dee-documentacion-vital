"""Auditor-only finite native empty-target ancestry from saved global frames.

Never equates load equality with lineage. Stops at occupied destinations,
unexplained increments, window boundaries or missing input-boundary coverage.
Multiple reducer parents remain multiple. Not an inverse kernel.
"""
from pathlib import Path
from collections import Counter
import argparse,gzip,json,sys
sys.path.insert(0,str(Path(__file__).parent))
from instrumentos_pc01 import packed,idx,coord,sha
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);a=p.parse_args();out={}
def unpack_frame(path):
    with gzip.open(path,'rt',encoding='utf8')as f:return{r['tick']:r for line in f if(r:=json.loads(line))}
def predecessors(frames,t,site):
    n=frames[t]['N'];post={i:int(v)for i,v,c in frames[t]['rows']};pre={i:int(v)for i,v,c in frames[t-1]['rows']};k=idx(site,n);v=post.get(k,0);target_pre=pre.get(k,0)
    if not v:return{'status':'POST_RAW_ZERO','parents':[]}
    if target_pre&0xffffffff:return{'status':'OCCUPIED_TARGET_NOT_BALLISTIC_IDENTITY','parents':[],'pre_target':packed(target_pre),'post':packed(v)}
    src=[]
    for i,b in pre.items():
        f=packed(b);d=f['direction'];q=coord(i,n)
        if any(d)and all(abs(x)<=1 for x in d)and[(q[j]+d[j])%n for j in range(3)]==site:
            src.append({'tick':t-1,'site':q,'record':f,'crossings':[1 if q[j]+d[j]>=n else-1 if q[j]+d[j]<0 else 0 for j in range(3)]})
    if not src:return{'status':'NO_SAVED_BALLISTIC_PARENT_CHECK_EVENT_BOUNDARY','parents':[],'post':packed(v)}
    sums=[sum(s['record']['direction'][j]for s in src)for j in range(3)];direction=src[0]['record']['direction']if len(src)==1 else[(x>0)-(x<0)for x in sums];load=src[0]['record']['s_reg']if len(src)==1 else min(19664,sum(s['record']['s_reg']for s in src));f=packed(v)
    if f['state']!=1 or f['semantic']!=1 or f['direction']!=direction or f['s_reg']!=load:return{'status':'NOT_EXACT_NATIVE_EMPTY_REDUCER_OUTPUT','parents':[],'candidates':src,'post':f}
    # An overflow elsewhere can add via DEMUX; under this observed max no
    # register reaches19665 even with the maximum per-tick increment1.
    if any(((b>>32)&65535)>=19664 for b in pre.values()):return{'status':'OVERFLOW_CONTEXT_REQUIRES_FULL_TICK_RECONSTRUCTION','parents':[],'candidates':src}
    return{'status':'UNIQUE_EMPTY_TRANSPORT'if len(src)==1 else'MULTIPARENT_EMPTY_REDUCER','parents':src,'post':f}
def walk(frames,t,site,maxnodes=1500):
    nodes=[];stack=[(t,site)];visited=set();stops=Counter();crossings=[]
    while stack and len(nodes)<maxnodes:
        t,q=stack.pop();key=(t,tuple(q))
        if key in visited:continue
        visited.add(key)
        if t-1 not in frames:info={'status':'WINDOW_BOUNDARY','parents':[]}
        else:info=predecessors(frames,t,q)
        nodes.append({'tick':t,'site':q,**info})
        if not info['parents']:stops[info['status']]+=1
        for s in info['parents']:
            if any(s['crossings']):crossings.append({'from_tick':t-1,'from':s['site'],'to':q,'crossings':s['crossings'],'record':s['record']})
            stack.append((t-1,s['site']))
    return{'nodes':nodes,'nodes_count':len(nodes),'stops':dict(stops),'crossings':crossings,'coverage_exhausted':bool(stack),'min_tick':min(x['tick']for x in nodes),'lineage_claim':'Only exact empty-target transport/reduction edges. An occupied target or missing admitted input stops this inference; no unique identity assigned through a merge.'}
for name,t,q in(('reference',9985,[48,37,34]),('near',22456,[38,58,16])):
    path=a.evidence/'PROCEDENCIA_01'/(name+'_trace')/'CAMPO_COMPLETO.jsonl.gz';frames=unpack_frame(path);x=walk(frames,t,q)
    traced=json.loads((path.parent/'PRIMARIOS.json').read_bytes());plain=json.loads((path.parent.parent/(name+'_plain')/'PRIMARIOS.json').read_bytes());x['passive_invariance']={key:traced[key]==plain[key]for key in('post','post_native','receipts')};x['source']={'path':str(path),'sha256':sha(path)};x['first_frame']=min(frames);x['last_frame']=max(frames)
    x['target']={'tick':t,'site':q,'record':packed(dict((i,int(v))for i,v,c in frames[t]['rows'])[idx(q,67)])};out[name]=x
target=a.evidence/'PROCEDENCIA_01/RECONSTRUCCION_ANTECEDENTES.json';target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:{key:v[key]for key in('nodes_count','stops','min_tick','crossings','passive_invariance')}for k,v in out.items()},ensure_ascii=False))
