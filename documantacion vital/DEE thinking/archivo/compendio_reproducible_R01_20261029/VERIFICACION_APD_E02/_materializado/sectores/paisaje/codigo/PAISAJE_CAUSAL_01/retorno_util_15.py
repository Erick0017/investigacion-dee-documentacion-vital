"""Calibrated useful recurrence, subsequent composition and receiver use.

No Spanish label or cognitive verdict is an input. H/I/J/Bare actual native
carriers. The same return is retained, intercepted or equal-material sham.
"""
from pathlib import Path
import argparse,sys,json,gzip
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
import dee_thinking as d
from app.native_tools import physical,observe
from app.process_control import protect_current
from dee_thinking.persistence import save_world_snapshot
from instrumentos_pc01 import frame,receipts,sha,native_digest
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);n=17;recipe=d.OrganizationRecipe.research(n,[],0);recipe.execution=d.TickOptions(d.Backend.LAZY,1);w=d.OrganizationalWorld.create(recipe)
ports=[('H',[0,5,5],(1,0,0),1),('I',[3,2,5],(0,1,0),1),('J',[3,8,5],(0,-1,0),1),('Bcue',[11,5,1],(-1,0,1),1),('Bquery',[4,2,5],(1,1,0),1),('action',[15,13,9],(-1,-1,0),1),('cut',[16,5,5],(0,0,0),4),('sham',[16,8,5],(0,0,0),4)]
for name,site,v,sem in ports:
    ch=d.ChannelSpec();ch.name='PC01.RETURN15.'+name;ch.injection_site=d.Coordinate(*site);ch.direction=d.Direction(*v);ch.state=1;ch.semantic=sem;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=ch.name;p.channel=ch;w.declare_interface(p)
data={'case':a.case,'life':'PC01_RETURN15_'+a.case,'parent':'NEW_T0_CALIBRATION_REVISION','type':'simple_transported_history_with_material_receiver; not autonomous cognitive body','N':n,'source_sha256':sha(__file__),'ports':[{'name':k,'site':q,'direction':list(v),'semantic':sem}for k,q,v,sem in ports],'requests':[],'milestones':[],'criteria_before':'HcirculatesoneNandIjoinsatN+3; jointXYreturnsNlater. Jzero-load cancelsYonlywhen the combined history exists, allowingXdeliverytoB. BcuecancelsXandstoresZ, laterBqueryqualifiesXYZ, fixed action gives+Zconsequence. NoH/noI and native routecut/sham must isolate these contributions. This is physical composition/communication calibration, not learned grammar or65meanings.'}
def send(name,load,t):
    r=w.submit('PC01.RETURN15.'+name,load,t);data['requests'].append({'port':name,'payload':load,'tick':t,'id':int(r.id)})
if a.case not in('W00','W01'):send('H',9,0)
if a.case not in('W00','W10'):send('I',7,n)
if a.case=='CUT':send('cut',0,n-2)
if a.case=='SHAM':send('sham',0,n-2)
send('J',0,2*n);send('Bcue',5,2*n+3);send('Bquery',7,3*n+4);send('action',11,3*n+7)
path=a.out/'CAMPO_COMPLETO.jsonl.gz'
with gzip.open(path,'wt',encoding='utf8',compresslevel=6)as f:
    for t in range(3*n+12):
        w.run_until(t);fr=frame(w);f.write(json.dumps(fr,separators=(',',':'))+'\n')
        if t in(n,n+3,2*n+3,2*n+7,3*n+7,3*n+11):data['milestones'].append({'tick':t,'native':native_digest(w.runtime),'records':{'joint':[observe(w,[3,5,5])][0],'B':observe(w,[7,5,5]),'effect':observe(w,[11,9,9])},'physical':physical(w,occupation=True)})
        if t==2*n+3:data['snapshot_before_receiver_acquisition']=save_world_snapshot(w,a.out/'ANTES_RECEPTOR_COLA_COMPLETA.deetsnap.gz',compress=True)
data['post']=physical(w,occupation=True);data['receipts']=receipts(w.runtime);data['snapshot_final']=save_world_snapshot(w,a.out/'FINAL_COMPLETO.deetsnap.gz',compress=True);data['trace']={'file':path.name,'sha256':sha(path)}
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'case':a.case,'milestones':[{'tick':r['tick'],'B':r['records']['B']['direction'],'effect':r['records']['effect']['direction'],'effect_load':r['records']['effect']['s_reg']}for r in data['milestones']]}))
