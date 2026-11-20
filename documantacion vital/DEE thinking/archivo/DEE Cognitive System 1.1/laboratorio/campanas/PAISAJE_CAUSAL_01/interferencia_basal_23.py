"""Engine-free exact empty-target countercarrier chain in the passive window."""
from pathlib import Path
import argparse,json,gzip,sys
sys.path.insert(0,str(Path(__file__).parent));from instrumentos_pc01 import packed,coord,idx,sha
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);a=p.parse_args();out={}
for mode in('counter_events','counter_passive'):
    path=a.evidence/'INTERFERENTE_Y_BASAL_20'/mode/'CAMPO_OCUPACION_CRITICA.jsonl.gz'
    with gzip.open(path,'rt',encoding='utf8')as f:frames={r['tick']:r for line in f if(r:=json.loads(line))}
    node=(26165,[59,1,20]);chain=[]
    while node[0]-1 in frames:
        t,q=node;pre={i:int(v)for i,v,c in frames[t-1]['rows']};post={i:int(v)for i,v,c in frames[t]['rows']};raw=pre.get(idx(q,67),0);src=[]
        for i,v in pre.items():
            z=coord(i,67);r=packed(v)
            if any(r['direction'])and[(z[k]+r['direction'][k])%67 for k in range(3)]==q:src.append({'tick':t-1,'site':z,**r})
        current=packed(post.get(idx(q,67),0));status='EXACT_SINGLE_EMPTY_TRANSPORT'if raw&0xffffffff==0 and len(src)==1 and current['state']==1 and current['semantic']==1 and current['direction']==src[0]['direction']and current['s_reg']==src[0]['s_reg']else'CONTEXT_OR_MULTIPARENT_STOP'
        chain.append({'tick':t,'site':q,'record':current,'pre_target':packed(raw),'parents':src,'status':status})
        if status!='EXACT_SINGLE_EMPTY_TRANSPORT':break
        node=(t-1,src[0]['site'])
    critical={}
    for t in(26160,26161,26162,26163,26164,26165,26166):
        r={i:int(v)for i,v,c in frames[t]['rows']};critical[str(t)]={','.join(map(str,q)):packed(r.get(idx(q,67),0))for q in([57,1,20],[58,1,20],[59,1,20],[60,0,21])}
    out[mode]={'source':str(path),'sha256':sha(path),'window':[min(frames),max(frames)],'chain':chain,'oldest_node':node,'critical_records':critical,'scope':'Strictemptytransportonly. Passivearmhadnoprotocolinputsinsidewindowandinitialqueuewasmeasuredempty; eventarmusesidenticalactualcounterpathobservationsbutunrelatedworldfieldsneednotmatch. Noidentitybyloadorpositionalone.'}
dest=a.evidence/'INTERFERENCIA_BASAL_23.json';dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:{'chain_length':len(v['chain']),'oldest':v['oldest_node'],'critical26163':v['critical_records']['26163'],'critical26165':v['critical_records']['26165'],'critical26166':v['critical_records']['26166']}for k,v in out.items()}))
