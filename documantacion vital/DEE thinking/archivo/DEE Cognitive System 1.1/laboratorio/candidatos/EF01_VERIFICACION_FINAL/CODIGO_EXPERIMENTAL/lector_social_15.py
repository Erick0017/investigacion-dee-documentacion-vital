"""Targeted query intervention controls for the old S04 access, not a CPC rerun."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe,moore27
from app.process_control import protect_current
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from capacidades import puente_adquirible as b
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='E1_SOCIAL_11';life='ES01_SOCIAL_READER15_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'contract_before':'Same actual object81, quantity/two-memory queries and final readT5673 as the recorded no-new-Spanish control. Change only early social access: +X, omitted, or equal-load offpath -X. Original -X control is already recorded and not rerun.'}
def trial(x):
 if a.case=='plus_reader':data['early']=b.read_transformed(x.world,3194,axis=1,payload=7)
 elif a.case=='sham_minus':
  req=[]
  for f in b.geometry(x.world)['forms']:
   for br in f['branches']:
    site=b.move(b.move(br['use_site'],(-1,0,0),-3),(0,0,1),9);ch=d.ChannelSpec();ch.name='EF01.SOCREADER15.'+f['id']+'.'+br['id'];ch.injection_site=d.Coordinate(*site);ch.direction=d.Direction(-1,0,0);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=ch.name;p.channel=ch;x.world.declare_interface(p);r=x.world.probe(ch.name,7,3191);req.append({'port':ch.name,'tick':3191,'id':int(r.id)})
  x.run_until(3194);data['sham_requests']=[{**r,'receipt':exact_receipt(x.world.runtime.receipt(r['id']))}for r in req]
 else:x.run_until(3194)
 x.quantity.present_object(81,round_index=47);x.quantity.input('quantity.reader',7,3218,True);x.two_memory.input('quantity.reader',7,3220,True);x.run_until(3221)
 data['common_early_quantities']={'tick':x.tick,'quantity':observe(x.world,x.quantity.geometry['center']),'two':observe(x.world,x.two_memory.geometry['center'])}
 data['final']=b.read_transformed(x.world,5673,axis=-1,payload=7);g=b.geometry(x.world)
 data['S04_neighbors']={br['id']:moore27(x.world,br['use_site'])for br in next(f for f in g['forms']if f['id']=='S04')['branches']};data['quantity_receipts']=x.quantity.receipts();data['two_receipts']=x.two_memory.receipts();data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'final':data['final']['ENTE']}
data['commit']=s.mutate(life,'EF01_OLD_SOCIAL_QUERY_DIRECTION_AND_DOSE_CAUSAL15',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
