"""Exact local evidence for directional reception + source survival and XNOR.

Auditor predicates reproduce only the declared empty-target branches of the
frozen source. They never feed the participant or replace native evolution.
"""
from pathlib import Path
from itertools import product
from collections import Counter
import argparse,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import legacy_class
from app.native_tools import atomic_json,digest_file,physical
from app.process_control import protect_current,current_resources
MOORE=[v for v in product((-1,0,1),repeat=3)if any(v)]
PAIRS=[v for v in MOORE if v>tuple(-x for x in v)]
def decode(v):
    ds=[(v>>k)&15 for k in(48,52,56)];return{'raw':str(v),'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':(v>>60)&15,'direction':[x-16 if x&8 else x for x in ds]}
def index(q,n):return(q[0]*n+q[1])*n+q[2]
def coord(i,n):return[i//(n*n),(i//n)%n,i%n]
def plus(q,v,n):return[(q[k]+v[k])%n for k in range(3)]
def local(raw,clocks,q,n):return[{'site':p,'clock':str(clocks[index(p,n)]),**decode(raw[index(p,n)])}for v in[(0,0,0)]+MOORE for p in[plus(q,v,n)]]
def rules(raw,q,n):
    ns=[(v,decode(raw[index(plus(q,v,n),n)]))for v in MOORE];alive=lambda x:x['state']>0 and x['semantic']!=5;grad=[-sum(v[k]*x['s_reg']for v,x in ns if x['state']>0)for k in range(3)];act=sum(alive(x)for v,x in ns);sym=sum(alive(decode(raw[index(plus(q,v,n),n)]))==alive(decode(raw[index(plus(q,tuple(-z for z in v),n),n)]))for v in PAIRS);orphan=any(x['semantic']==5 for v,x in ns);crystal=act>0 and sum(abs(z)for z in grad)//19665>=int(9.887**3)and not orphan
    incoming=[{'site':plus(q,v,n),'record':x}for v,x in ns if any(x['direction'])and plus(plus(q,v,n),x['direction'],n)==q]
    return{'gradient':grad,'active_neighbors':act,'symmetric_pairs':sym,'orphan_neighbor':orphan,'crystal_branch':crystal,'XNOR_branch':not crystal and sym==13 and act>=8,'incoming':incoming}
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();protect_current();a.out.mkdir(parents=True,exist_ok=False);src=ROOT/'evidencia/telemetria/INTERFERENCIA_R1/K65_R1_BASE/T1912.deetsnap.gz';s=legacy_class().load(src);n=int(s.world.runtime.dimension);ref=json.loads((src.parent/'MEDICIONES.json').read_bytes());references={f['tick']:f['physical']for f in ref['frames']};by_name={x.name:[x.channel.injection_site.x,x.channel.injection_site.y,x.channel.injection_site.z]for x in s.world.interfaces};start=time.perf_counter();report={'schema':'DCS1.1.expansion.local_evidence.r1','source_sha256':digest_file(src),'source_tick':1912,'end_tick':2305,'kind':'DIAGNOSTIC_EXACT_CONTINUATION_NO_EDIT','sampling':'Allticks1912..2305counts; first4validatedsurvival/receptionwitnesses per tick until16total; first4empty-XNORwitnesses per tick until16total. Samplecount is not replica count.','coverage_limits':'Local branch identification plus exact source/target direction and full pre/postMoore, not a wholeworld unique ancestry. Externalinputs near each witness are explicitly excluded. No single locus is declared a global cause.','steps':[],'survival_reception_witnesses':[],'XNOR_witnesses':[],'reference_matches':[]}
    raw=s.world.runtime.raw_copy();cl=s.world.runtime.clock_copy()
    for before_tick in range(1912,2305):
        s.run_until(before_tick+1);new=s.world.runtime.raw_copy();nc=s.world.runtime.clock_copy();occupied=[i for i,v in enumerate(raw)if(v&0xffffffff)>0];entered=[i for i,v in enumerate(new)if(v&0xffffffff)>0 and(raw[i]&0xffffffff)==0];born7=[i for i in entered if((new[i]>>60)&15)==7];inputs=[by_name[name]for rr in s.world.runtime.receipts if rr.effective_tick==before_tick and str(rr.status)=='applied'for name in rr.channels if name in by_name];count=0
        for i in occupied:
            v=decode(raw[i]);q=coord(i,n)
            if v['semantic']!=1 or not any(v['direction'])or not(new[i]&0xffffffff):continue
            target=plus(q,v['direction'],n);j=index(target,n)
            if(raw[j]&0xffffffff)!=0 or((raw[j]>>60)&15)==4 or not(new[j]&0xffffffff):continue
            post=decode(new[j])
            if post['semantic']!=1 or post['state']!=1 or post['s_reg']!=v['s_reg']or post['direction']!=v['direction']:continue
            region={tuple(x['site'])for p0 in(q,target)for x in local(raw,cl,p0,n)}
            if any(tuple(p0)in region for p0 in inputs):continue
            branch=rules(raw,target,n)
            if branch['crystal_branch']or branch['XNOR_branch']or len(branch['incoming'])!=1 or branch['incoming'][0]['site']!=q:continue
            count+=1
            if len(report['survival_reception_witnesses'])<16 and count<=4:report['survival_reception_witnesses'].append({'pre_tick':before_tick,'source':q,'target':target,'source_post':{'clock':str(nc[i]),**decode(new[i])},'target_post':{'clock':str(nc[j]),**post},'branch_reconstruction':branch,'pre_source_Moore27':local(raw,cl,q,n),'pre_target_Moore27':local(raw,cl,target,n),'post_target_Moore27':local(new,nc,target,n),'nearby_material_input_this_step':False})
        for i in born7[:4]:
            if len(report['XNOR_witnesses'])>=16:break
            q=coord(i,n);branch=rules(raw,q,n);report['XNOR_witnesses'].append({'pre_tick':before_tick,'site':q,'reconstructed':branch,'pre_Moore27':local(raw,cl,q,n),'post_Moore27':local(new,nc,q,n),'native_post':decode(new[i]),'branch_match':branch['XNOR_branch']})
        report['steps'].append({'pre_tick':before_tick,'post_tick':before_tick+1,'occupied_pre':len(occupied),'occupied_post':sum((v&0xffffffff)>0 for v in new),'newly_occupied_sites':len(entered),'empty_to_semantic7':len(born7),'validated_source_survival_with_unique_receiver':count,'applied_input_sites':inputs})
        if before_tick+1 in references:
            ph=physical(s.world);old=references[before_tick+1];report['reference_matches'].append({'tick':before_tick+1,'full_RAW_clocks_tick_equal':all(ph[k]==old[k]for k in('N','tick','RAW_sha256','clocks_sha256'))})
        raw,cl=new,nc
        if(before_tick-1912)%100==0:print(before_tick+1,report['steps'][-1]['occupied_post'],flush=True)
    report['final']=physical(s.world,occupation=True);report['seconds']=time.perf_counter()-start;report['resources']=current_resources();atomic_json(a.out/'MICRO_EXPANSION.json',report);print(json.dumps({'witnesses':len(report['survival_reception_witnesses']),'XNORwitnesses':len(report['XNOR_witnesses']),'references_all_equal':all(x['full_RAW_clocks_tick_equal']for x in report['reference_matches']),'seconds':report['seconds']}))
if __name__=='__main__':main()
