"""Alternative admitted native supply for current equality-route expression.

Baseline scalar-existing is already recorded from the same parent and inputs;
it is not rerun. The native amplitude-normalized decoder is new/frozen here,
not used to change the scores of older strict-decoder tests.
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
if a.case not in('twin4','twin4_offroute','twin4_no_material_probe','twin8_reserved'):raise ValueError('Unknown finite supply comparison')
s=Store(a.system);parent='ES01_MAIN_05';life='ES01_EQUAL_READER6_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'episodes':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'decoder_before':'Acquired nativeword[1,-1,1] prior/current; current word increment must equal positive directly observed native comparison carrier amplitude. Decoder never compares the environmental value with a reference or uses comparison direction.'}
def trial(x):
 entry=f.prepare(x);w=x.world;c=entry['center'];ports=[]
 for sign in(-1,1):
  v=(sign,0,1);site=e.move(c,v,-1)
  if a.case=='twin4_offroute':site=e.move(site,(0,1,0),8)
  ch=d.ChannelSpec();ch.name='EF01.EQUAL.READER6.'+str(sign);ch.injection_site=d.Coordinate(*site);ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=ch.name;p.channel=ch;w.declare_interface(p);ports.append(ch.name)
 for j,value in enumerate((86,56,110,86)):
  base=e.tick_at_or_after(x.tick,phase=7)
  if base>x.tick:x.run_until(base)
  before=observe(w,entry['hub']);target=base+67;T=target-4;req=[];first=len(x.quantity.state['requests'])
  x.quantity.present_object(value,round_index=(T-70)//67)
  for port in ports:
   r=w.probe(port,4 if a.case=='twin8_reserved'else 2,T-1);req.append({'port':port,'payload':4 if a.case=='twin8_reserved'else 2,'tick':T-1,'id':int(r.id)})
  if a.case!='twin4_no_material_probe':
   r=w.probe(entry['ports']['material_probe1'],0,T);req.append({'port':entry['ports']['material_probe1'],'payload':0,'tick':T,'id':int(r.id)})
  x.run_until(T-1);pre={'tick':x.tick,'center':observe(w,c),'moore':moore27(w,c)}
  x.run_until(T);comparison=observe(w,c);compmoore=moore27(w,c)
  x.run_until(T+1);route=observe(w,entry['route_slot']);routemoore=moore27(w,entry['route_slot'])
  x.run_until(target);after=observe(w,entry['hub']);delta=after['s_reg']-before['s_reg'];decoded=['igual']if comparison['s_reg']>0 and e.valid(before,entry['signature'])and e.valid(after,entry['signature'])and delta==comparison['s_reg']else[]
  data['episodes'].append({'episode':j+1,'current_environmental_value':value,'comparison_tick':T,'word_tick':target,'prior_word':before,'current_word':after,'word_increment':delta,'native_current_comparison':comparison,'native_current_route':route,'SPANISH_DECODED':decoded,
   'requests':[{**r,'receipt':exact_receipt(w.runtime.receipt(r['id']))}for r in req],'quantity_requests':x.quantity.receipts()[first:],'pre':pre,'comparison_moore':compmoore,'route_moore':routemoore,'physical':physical(w,occupation=True)})
 data['word_recall']=f.query(x);data['older_comparison_forms']=e.query_words(x);data['post']=physical(w,occupation=True)
 return {'tick':x.tick,'responses':[r['SPANISH_DECODED']for r in data['episodes']],'native_comparisons':[r['native_current_comparison']['direction']for r in data['episodes']],'native_amplitudes':[r['native_current_comparison']['s_reg']for r in data['episodes']],'word_recall':data['word_recall']['SPANISH_DECODED'],'older_words':data['older_comparison_forms']['FORMAS_ACCESIBLES']}
data['commit']=s.mutate(life,'EF01_CURRENT_EQUALITY_ALTERNATIVE_NATIVE_READER_SUPPLY6',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
