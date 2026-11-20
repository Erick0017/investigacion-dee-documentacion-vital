"""No engine: trace the new +1 marker only over the globally observed window."""
from pathlib import Path
import argparse,gzip,json,sys
sys.path.insert(0,str(Path(__file__).parent));from instrumentos_pc01 import packed,idx,coord,sha
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);a=p.parse_args();out={}
for path in sorted((a.evidence/'FACTORES_ADQUISICION_38').glob('*/PRIMARIOS.json')):
    prim=json.loads(path.read_bytes());source=path.parent/prim['trace']['file'];birth=prim['lessons'][0]['ENTE']['post_signal']['d1'];born=birth['tick'];n=67
    with gzip.open(source,'rt',encoding='utf8')as f:frames={r['tick']:r for line in f if(r:=json.loads(line))}
    def nominal(t):return[(birth['site'][j]+t-born)%n for j in range(3)]
    def values(t):return{i:int(v)for i,v,c in frames[t]['rows']}
    def requests(q):
        if isinstance(q,dict):
            if type(q.get('id'))is int and type(q.get('payload'))is int and type(q.get('tick'))is int and('port'in q or'channel'in q):yield q
            for k,v in q.items():
                if k not in('parent','commit'):yield from requests(v)
        elif isinstance(q,list):
            for v in q:yield from requests(v)
    req=list(requests(prim));steps=[];first=None
    for t in range(born+1,max(frames)+1):
        pre=values(t-1);post=values(t);p0=nominal(t-1);q=nominal(t);incoming=[]
        for i,v in pre.items():
            r=packed(v);site=coord(i,n)
            if any(r['direction'])and all(abs(z)<=1 for z in r['direction'])and[(site[j]+r['direction'][j])%n for j in range(3)]==q:incoming.append({'site':site,**r})
        current=packed(post.get(idx(q,n),0));before=packed(pre.get(idx(q,n),0));active_inputs=[r for r in req if r['tick']==t-1 and r.get('receipt',{}).get('status')=='applied'];row={'pre_tick':t-1,'post_tick':t,'source':{'site':p0,**packed(pre.get(idx(p0,n),0))},'destination':q,'target_pre':before,'post':current,'incoming':incoming,'applied_inputs_at_boundary':active_inputs,'raw_initial_target_and_incoming_need_overlay':bool(active_inputs)};steps.append(row)
        if current['state']!=1 or current['semantic']!=1 or current['direction']!=[1,1,1]:first=row;break
    out[prim['case']]={'source':str(path),'sha256':sha(path),'trace_sha256':sha(source),'birth':birth,'stored_global_window':[min(frames),max(frames)],'steps_until_first_signature_loss':steps,'first_departure':first,'scope':'Exactnativeobservations; nominalsignaturetraceisnotanassumeduniqueidentityaftermergesoroccupied-targetupdates. Inputsatthedecisiveboundaryarelistedandanymissingoverlayisflagged. No learningclaimfromrawdifferencealone.'}
(a.evidence/'RETENCION_NUEVA_Y_LECTOR_38.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:{'birth':v['birth'],'first':v['first_departure']}for k,v in out.items()},ensure_ascii=False))
