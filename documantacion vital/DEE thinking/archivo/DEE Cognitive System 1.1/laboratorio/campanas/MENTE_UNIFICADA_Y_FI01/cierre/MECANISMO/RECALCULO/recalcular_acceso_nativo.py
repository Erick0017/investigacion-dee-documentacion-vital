"""Portable mixed-gate causal routing recalculation, no native imports."""
import argparse,gzip,hashlib,json
from pathlib import Path
V={'alfa':(1,0,0),'beta':(0,1,0),'gamma':(1,1,0),'delta':(-1,1,0),'epsilon':(1,-1,0),'zeta':(-1,-1,0)}
def sha(b):return hashlib.sha256(b).hexdigest()
def mixed(r):
    cs=[]
    for p in r['panel']:
        token=p['gate_class'];o=p['observation'];v=V[token]
        if o['state']>0 and o['semantic']==1 and o['direction']in([v[0],v[1],-1],[v[0],v[1],1]):cs.append({'gate_class':token,'sign':o['direction'][2],'observation':o})
    return cs
def pure(r):
    cs=[o['direction'][2]for o in r['panel']if o['state']>0 and o['semantic']==1 and o['direction']in([0,0,-1],[0,0,1])]
    return cs[0]if len(cs)==1 else None
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidencia',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
    files=[];uses=[];post=[];receipts=[];errors=[];raw_count=0;critical=[]
    def walk(o,file,path=''):
        nonlocal raw_count
        if isinstance(o,dict):
            if all(k in o for k in('raw','clock','site','state','direction')):
                raw_count+=1
                if not(0<=int(o['raw'])<2**64 and 0<=int(o['clock'])<2**64):errors.append(file+': non uint64')
            if 'receipt'in o and isinstance(o['receipt'],dict)and 'status'in o['receipt']:receipts.append({'file':file,'path':path,'id':o.get('id'),'status':o['receipt']['status']})
            for k,v in o.items():walk(v,file,path+'/'+k)
        elif isinstance(o,list):
            for i,v in enumerate(o):walk(v,file,path+'/'+str(i))
    for p in sorted(a.evidencia.rglob('*')):
        if not p.is_file()or not(p.name.endswith('.json.gz')or p.name.endswith('.json'))or p.name.startswith(('RECALCULO','INDICE')):continue
        b=p.read_bytes();o=json.loads(gzip.decompress(b)if p.suffix=='.gz'else b);rel=p.relative_to(a.evidencia).as_posix();files.append({'file':rel,'sha256':sha(b),'bytes':len(b)});walk(o,rel)
        r=o.get('result',{})
        if 'common_query_tick'in r:
            rr=r['reader'];windows=rr.get('windows',[rr]);cs=[]
            for w in windows:
                wc=mixed(w)
                if wc!=w['candidates']:errors.append(rel+': mixed candidate mismatch')
                cs.extend([dict(c,window_tick=w['tick'])for c in wc]if 'windows'in rr else wc)
            choice=cs[0]['sign']if len(cs)==1 else None
            if choice!=rr['formed_native_command']or cs!=rr['candidates']:errors.append(rel+': fixed unique-product rule mismatch')
            uses.append({'file':rel,'query_present':r['query_present'],'first_turn_resources_present':r['first_turn_resources_present'],
              'query_tick':r['common_query_tick'],'window_ticks':[w['tick']for w in windows],'candidates':[{'gate_class':c['gate_class'],'sign':c['sign'],'load':c['observation']['s_reg'],'tick':c.get('window_tick',c['observation']['tick'])}for c in cs],
              'unique_command':choice,'final_snapshot_sha256':o['INSTRUMENTO']['snapshot_sha256']})
            for fr in r['frames']:
                for ob in fr['sites']:
                    if ob['site']in([15,15,15],[33,33,33],[33,19,33],[33,19,35])and ob['state']>0:critical.append({'file':rel,'tick':fr['tick'],'site':ob['site'],'s_reg':ob['s_reg'],'direction':ob['direction'],'raw':ob['raw'],'clock':ob['clock']})
            frames={x['tick']:{tuple(y['site']):y for y in x['sites']}for x in r['frames']}
            for w in windows:
                for p0 in w['panel']:
                    ob=p0['observation']
                    if frames[w['tick']].get(tuple(ob['site']))!=ob:errors.append(rel+': fixed decoder differs from frame')
        if p.name.endswith('_POST_PANEL.json.gz'):
            outcomes=[]
            for row in r['rows']:
                actual=pure(row['reader'])
                if actual!=row['reader']['formed_native_command']:errors.append(rel+': postpanel mismatch')
                outcomes.append({'context':row['context_signal'],'native_command':actual})
            post.append({'file':rel,'responses':outcomes,'valid':sum(x['native_command']in(-1,1)for x in outcomes),'requested':len(outcomes),'scope':'Sequential material probes after routing; validity is not semantic correctness or unchanged knowledge.'})
    result={'schema':'MUFI01.native_access.recalculation.v1','native_ticks_executed':0,'files':files,'routing_uses':uses,'post_use_panels':post,'native_receipts':receipts,
      'uint64_observations_checked':raw_count,'critical_observed_fields':critical,'errors':errors,
      'scope':'Verifies fixed all-gate native output, negative no-query controls, primary field identity and post-use losses. A trajectory coordinate is not a unique carrier lineage; prepared routing is not a learned general strategy.'}
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(files),'routing_uses':len(uses),'panels':len(post),'receipts':len(receipts),'uint64_observations':raw_count,'errors':errors,'sha256':sha(a.salida.read_bytes())}))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
