"""Passive witnesses on diagnostic exact forks; never fed back to MAIN."""
from pathlib import Path
import argparse,json,sys
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import observe,physical,moore27
from app.process_control import protect_current
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);results=[]
def move(p,v,k=1):return[(p[i]+v[i]*k)%67 for i in range(3)]
for zy in [(0,1),(0,-1),(1,-1)]:
 for third in ['none','equal']:
  name='ES01_DIAG_Z'+str(zy[0])+'Y'+('P'if zy[1]==1 else'M')+'_'+third;s.fork('ES01_MAIN_R0',name,kind='DIAGNOSTIC_COPY');data={'case':name,'cue_z':zy[0],'more_cue_y':zy[1],'third':third,'frames':[],'receipts':[]}
  def run(x):
   w=x.world;c=x.quantity.geometry['center'];hubs={'menos':move(c,(1,0,0),2),'mas':move(c,(-1,0,0),2)}
   for word in hubs:
    v=(0,1 if word=='menos'else zy[1],zy[0]);ch=d.ChannelSpec();ch.name='EF01.DIAG.'+word;ch.injection_site=d.Coordinate(*move(hubs[word],v,-3));ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True;i=d.InterfaceSpec();i.name=ch.name;i.channel=ch;w.declare_interface(i)
   for k,val,word in [(48,50,'menos'),(49,82,'mas')]:
    x.quantity.present_object(val,round_index=k);center=70+67*k;x.quantity.input('quantity.reader',7,center-1,True);data['receipts'].append(exact_receipt(w.submit('EF01.DIAG.'+word,5,center-1)))
   if third=='equal':x.quantity.present_object(73,round_index=50);x.quantity.input('quantity.reader',7,3419,True)
   x.run_until(3287)
   for tick in range(3288,3425):
    x.run_until(tick);sites={}
    for word,base,v,start in [('menos',hubs['menos'],(1,1,zy[0]),3288),('mas',hubs['mas'],(-1,zy[1],zy[0]),3355)]:
     if tick>=start:
      loc=move(base,v,tick-start);sites[word]={'site':loc,'physical':observe(w,loc),'neighborhood':moore27(w,loc)}
    raw=w.runtime.raw_copy();active=[{'index':i,'raw':str(v),'clock':str(w.runtime.clock_copy()[i])}for i,v in enumerate(raw)if(v&0xffffffff)>0]if tick in(3355,3356,3418,3419,3420,3421,3422)else[]
    data['frames'].append({'tick':tick,'sites':sites,'selected_full_active_state':active})
   data['post']=physical(w,occupation=True);return{'diagnostic':True,'tick':x.tick}
  data['committed']=s.mutate(name,'EF01_CAUSAL_ROUTE_DIAGNOSTIC',run);results.append(data);(a.out/'RUTAS.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'case':name,'tick':data['post']['tick'],'occupied':data['post']['occupied']}),flush=True)
