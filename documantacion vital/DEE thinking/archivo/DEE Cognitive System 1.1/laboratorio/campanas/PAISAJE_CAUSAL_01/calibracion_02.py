"""Small native transport/history/return factorial; no Spanish target labels."""
from pathlib import Path
from array import array
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
import dee_thinking as d
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from dee_thinking.persistence import save_world_snapshot
from instrumentos_pc01 import native_digest,frame,guard,receipts,sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
n=int(a.case.removeprefix('N'));data={'case':a.case,'N':n,'source_sha256':sha(__file__),'definition':'Same declared transport mechanism at two finite dimensions, no trained state transplantation. Four-world factorial plus selective native route cut and equal-material sham. History H is a physically circulating input; I is a later fixed input.','worlds':{},'criteria_before':'H[+X] atT0 returns afterN, crosses boundaries, then meetsI[+Y] atT(N+3). Expect exact joint directionXY versus separateX/Y; compare late use and full RAW/clocks XOR, not a label-based answer. At cut/sham identical H/I; SEM4 zero-load route obstacle atT(N-2).'}
def build():
    recipe=d.OrganizationRecipe.research(n,[],0);recipe.execution=d.TickOptions(d.Backend.LAZY,1);w=d.OrganizationalWorld.create(recipe)
    for name,site,v,sem in(('H',[0,5,5],(1,0,0),1),('I',[3,2,5],(0,1,0),1),('future',[7,1,1],(0,0,1),1),('cut',[n-1,5,5],(0,0,0),4),('sham',[n-1,8,5],(0,0,0),4)):
        ch=d.ChannelSpec();ch.name='PC01.CAL.'+name;ch.injection_site=d.Coordinate(*site);ch.direction=d.Direction(*v);ch.state=1;ch.semantic=sem;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=ch.name;p.channel=ch;w.declare_interface(p)
    return w
worlds={name:build()for name in('W00','W10','W01','W11','CUT','SHAM')};snapshots={}
for name,w in worlds.items():
    w.submit('PC01.CAL.future',0,5*n+9)
    if name in('W10','W11','CUT','SHAM'):w.submit('PC01.CAL.H',9,0)
    if name in('CUT','SHAM'):w.submit('PC01.CAL.'+name.lower(),0,n-2)
    frames=[]
    for t in range(n+1):w.run_until(t);frames.append(frame(w))
    before=native_digest(w.runtime);before_phys=physical(w);passive=frame(w);observe(w,[3,5,5]);after=native_digest(w.runtime)
    row={'identity':{'life':'PC01_CAL_'+a.case+'_'+name,'parent':'COMMON_T0_RECIPE_NOT_A_PRIOR_LIFE','type':'simple_native_transport_with_environmental_inputs','Runtime':'single_for_this_case','N':n,'initial_tick':0,'initial_material':0,'host_decides':'Input timing, fixed sites and whether to supplyH/I, never computes the participant output'},'before_I':{'physical':before_phys,'native':before,'receipts':receipts(w.runtime)},'passive_no_advance_identity':before==after}
    if name in('W01','W11','CUT','SHAM'):w.submit('PC01.CAL.I',7,n)
    for t in range(n+1,4*n+4):w.run_until(t);frames.append(frame(w))
    row['at_first_joint']=next(f for f in frames if f['tick']==n+3);row['at_later_return']=next(f for f in frames if f['tick']==2*n+3);row['post']=physical(w,occupation=True);row['receipts']=receipts(w.runtime);row['full_snapshot']=save_world_snapshot(w,a.out/(name+'.deetsnap.gz'),compress=True)
    import gzip
    path=a.out/(name+'_CAMPO.jsonl.gz')
    with gzip.open(path,'wt',encoding='utf8',compresslevel=6)as f:
        for fr in frames:f.write(json.dumps(fr,separators=(',',':'))+'\n')
    row['trace']={'file':path.name,'sha256':sha(path),'frames':len(frames)};data['worlds'][name]=row;snapshots[name]={f['tick']:f for f in frames}
data['before_I_pair_equality']={x+'_'+y:{k:data['worlds'][x]['before_I'][k]==data['worlds'][y]['before_I'][k]for k in('physical','native','receipts')}for x,y in(('W00','W01'),('W10','W11'))}
data['history_effects']=[]
for t in(n+1,n+3,2*n+3,4*n+3):
    f={k:snapshots[k][t]for k in('W00','W10','W01','W11')};r={k:{i:int(v)for i,v,c in q['rows']}for k,q in f.items()};keys=set().union(*(set(x)for x in r.values()));interaction=[{'index':i,'delta_I_no_H':str(r['W01'].get(i,0)^r['W00'].get(i,0)),'delta_I_with_H':str(r['W11'].get(i,0)^r['W10'].get(i,0))}for i in sorted(keys)if(r['W01'].get(i,0)^r['W00'].get(i,0))!=(r['W11'].get(i,0)^r['W10'].get(i,0))];data['history_effects'].append({'tick':t,'differing_XOR_effect_sites':len(interaction),'differences':interaction})
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'N':n,'pairs':data['before_I_pair_equality'],'XOR_counts':[r['differing_XOR_effect_sites']for r in data['history_effects']]}))
