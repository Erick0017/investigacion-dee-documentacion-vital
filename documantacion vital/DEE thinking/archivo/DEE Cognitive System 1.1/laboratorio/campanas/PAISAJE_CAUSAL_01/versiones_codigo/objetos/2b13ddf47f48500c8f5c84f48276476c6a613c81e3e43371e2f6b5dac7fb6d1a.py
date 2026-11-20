"""Read-only local witnesses for the newly separated failure mechanisms."""
from pathlib import Path
import argparse,gzip,json,sys
sys.path.insert(0,str(Path(__file__).parent))
from instrumentos_pc01 import packed,idx,coord,sha
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);a=p.parse_args();out={}
def load(p):
    with gzip.open(p,'rt',encoding='utf8')as f:return{r['tick']:r for line in f if(r:=json.loads(line))}
def local(fr,t,site,radius=3):
    n=fr[t]['N'];rs={i:(v,c)for i,v,c in fr[t]['rows']};found=[]
    for i,(v,c)in rs.items():
        q=coord(i,n)
        if all(min((q[k]-site[k])%n,(site[k]-q[k])%n)<=radius for k in range(3)):found.append({'site':q,'clock':c,**packed(int(v))})
    return{'tick':t,'site':site,'radius':radius,'nonzero_records':found,'other_RAW_within_radius':'Exactly0 in the complete saved frame, not an omitted-state assumption','clock_default':fr[t]['clock_default'],'clock_exceptions':fr[t]['clock_exceptions']}
def incoming(fr,t,site):
    n=fr[t]['N'];r=[]
    for i,v,c in fr[t]['rows']:
        q=coord(i,n);f=packed(int(v));v=f['direction']
        if any(v)and all(abs(z)<=1 for z in v)and[(q[k]+v[k])%n for k in range(3)]==site:r.append({'site':q,'clock':c,**f})
    return r
p=a.evidence/'SEGUNDO_FALLO_PALABRAS_11/guard_trace/CAMPO_PALABRAS.jsonl.gz'
if p.exists()and(p.parent/'PRIMARIOS.json').exists():
    fr=load(p);v=[1,1,-1];origin=[53,35,35];t0=10458;loss=None
    for t in range(t0+1,max(fr)+1):
        site=[(origin[k]+(t-t0)*v[k])%67 for k in range(3)];row=next((packed(int(r))for i,r,c in fr[t]['rows']if i==idx(site,67)),packed(0))
        if row['state']!=1 or row['semantic']!=1 or row['direction']!=v:
            loss={'pre_tick':t-1,'post_tick':t,'site':site,'post_record':row,'incoming_pre':incoming(fr,t-1,site),'pre_radius3':local(fr,t-1,site),'post_radius3':local(fr,t,site),'scope':'Firstdeparturefromtheactuallyqualifiedmenoscarrierpath, not identity byload.'};break
    orig=json.loads((a.evidence/'REFERENCIA_CAUSAL_05/guard/PRIMARIOS.json').read_bytes());new=json.loads((p.parent/'PRIMARIOS.json').read_bytes());out['later_word_failure']={'source':str(p),'sha256':sha(p),'same_physical_as_prior_guard_trial':{k:orig['post'][k]==new['post'][k]for k in('tick','RAW_sha256','clocks_sha256')},'first_departure':loss,'native_comparison_still_valid':[{'label':x['label'],'native_comparison':x['result']['ENTE']['native_comparison'],'translation':x['result']['TRADUCCION']}for x in new['phases']if x['label'].startswith('new_magnitude')]}
p=a.evidence/'FUENTE_CONTEXTO_09/full/CAMPO_COMPLETO.jsonl.gz'
if p.exists()and(p.parent/'PRIMARIOS.json').exists():
    fr=load(p);events=[]
    for t,site in((10800,[42,60,18]),(10928,[42,54,12])):
        events.append({'post_tick':t,'site':site,'incoming_pre':incoming(fr,t-1,site),'pre_radius3':local(fr,t-1,site),'post_radius3':local(fr,t,site)})
    out['context_ancestry']={'source':str(p),'sha256':sha(p),'events':events,'warning':'Admittedinputsattheboundaryareidentifiedinthereceipts+ports/protocol, not inferredabsentbecauseRAWframesarebeforeapplication.'}
dest=a.evidence/'CAUSAS_DETALLADAS_13.json';dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:({'same':v['same_physical_as_prior_guard_trial'],'first_departure':{z:v['first_departure'][z]for z in('pre_tick','post_tick','site','post_record','incoming_pre')}}if k=='later_word_failure'and v['first_departure']else{'events':[{'post_tick':e['post_tick'],'site':e['site'],'incoming':e['incoming_pre']}for e in v.get('events',[])]})for k,v in out.items()},ensure_ascii=False))
