"""Diagnostic replay of a measured main prefix, never returned to MAIN.

Tests whether the later non-equal route cancels the marker of an earlier
equality form on a toroidal return. A predicted route is only a hypothesis;
actual pre/post Moore neighborhoods and a selective guard/sham are retained.
"""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe,moore27
from app.process_control import protect_current
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from capacidades import espanol_funcional_01 as e,igualdad_fisica_03 as f
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_MAIN_04';life='ES01_EQUAL_INTERFERENCE5_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY')
data={'case':a.case,'life':life,'parent':s.record(parent),'frames':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'hypothesis_before':'More-than-reference side product[-1,-1,1] could meet the older acquired[1,-1,1] word32ticks afterT9990, cancelingX. Guard only the first route; the sham adds equal material away from it. Do not assume this route hypothesis is true.'}
def trial(x):
 data['prefix']=[];data['prefix'].append(f.present(x,value=86,teacher=True,probe_lead=1))
 for _ in range(3):data['prefix'].append(f.query(x))
 for value in(86,56,110):data['prefix'].append(f.context(x,value=value,probe_lead=1))
 data['replayed_more_boundary']=physical(x.world,occupation=True);start=x.tick;hub=f.prepare(x)['hub'];newpoint=e.move(hub,(-1,0,0),3);guard_site=e.move(newpoint,(-1,-1,1),10)
 if a.case=='sham':guard_site=e.move(guard_site,(0,1,0),9)
 if a.case in('cut_route','sham'):
  ch=d.ChannelSpec();ch.name='EF01.EQ.INTERFERENCE5';ch.injection_site=d.Coordinate(*guard_site);ch.direction=d.Direction(0,0,0);ch.state=1;ch.semantic=4;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=ch.name;p.channel=ch;x.world.declare_interface(p);r=x.world.submit(ch.name,0,start+8);data['guard']={'site':guard_site,'tick':start+8,'id':int(r.id)}
 for dt in range(1,68):
  expected_word=e.move(hub,(1,-1,1),dt);expected_new=e.move(newpoint,(-1,-1,1),dt)
  x.run_until(start+dt)
  data['frames'].append({'tick':x.tick,'dt':dt,'predicted_old_word_site':expected_word,'predicted_more_route_site':expected_new,
   'old_route_record':observe(x.world,expected_word),'new_route_record':observe(x.world,expected_new),
   'word_neighbors':moore27(x.world,expected_word),'more_neighbors':moore27(x.world,expected_new)})
 if'guard'in data:data['guard']['receipt']=exact_receipt(x.world.runtime.receipt(data['guard']['id']))
 data['passive_old_hub_after67']=observe(x.world,hub);data['reexpression_probe']=f.query(x);data['old_words']=e.query_words(x);data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'prefix_more_tick':start,'passive_at_old_hub':data['passive_old_hub_after67'],'reexpression':data['reexpression_probe']['SPANISH_DECODED'],'old_words':data['old_words']['FORMAS_ACCESIBLES']}
data['commit']=s.mutate(life,'EF01_EQUAL_MARKER_INTERFERENCE_DIAGNOSTIC_REPLAY',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
