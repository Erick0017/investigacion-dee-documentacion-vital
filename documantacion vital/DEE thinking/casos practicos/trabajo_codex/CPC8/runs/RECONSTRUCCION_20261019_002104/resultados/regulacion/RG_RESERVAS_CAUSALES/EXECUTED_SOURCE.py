"""Frozen native counterflow reserves and exact selective causal forks."""
import argparse,gc,json,shutil,sys
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from dee_thinking import _native as d
from regulacion_adquirida import RegulatedQuantitySession
from cantidad_renovable import physical,move
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reading(s,pre,post,reference,obj):
 q=pre['reference'];v=pre['object'];o=post['center'];expected=[(reference>obj)-(reference<obj),0,0]
 refok=q['active']and q['s_reg']==reference+5 and q['direction']==[0,1,0];objok=v['active']and v['s_reg']==obj+5 and v['direction']==[0,1,0]
 return{'tick':post['tick'],'reference_available':refok,'current_object_preserved':objok,'observed_output':o,'correct_function':bool(refok and objok and o['active']and o['state']==1 and o['semantic']==1 and o['s_reg']==7 and o['direction']==expected),'expected_auditor_only':expected}
def run(out):
 out.mkdir(parents=True,exist_ok=False);shutil.copyfile(Path(__file__),out/'EXECUTED_SOURCE.py')
 cfg={'schema':'CPC8R.acquired_counterflow.reserve_and_causal.v1','frozen_before_execution':True,
 'reserves':[{'id':'RG_R101','center':[43,31,39],'reference':17,'objects':[9,37,17],'offset':0},{'id':'RG_R102','center':[30,30,30],'reference':43,'objects':[27,61,43],'offset':13}],
 'forks':[{'id':'RG_F101','parent_tick':73,'regulator':0,'mode':'cut'},{'id':'RG_F102','parent_tick':73,'regulator':0,'mode':'sham'},{'id':'RG_F103','parent_tick':140,'regulator':1,'mode':'cut'},{'id':'RG_F104','parent_tick':140,'regulator':1,'mode':'sham'}],
 'scope':'Finite R1direction-dependentregulation; reserve shiftsgeometry/magnitudes orentireexperienceonset, neverclocks/RAW inMAIN. No R2utilityselection claimed.'}
 put(out/'CONFIG.json',cfg);results=[]
 for c in cfg['reserves']:
  s=RegulatedQuantitySession.create(center=c['center']);off=c['offset'];s.experience_reference(c['reference'],tick=off);s.reader_opportunity(reference_time=off);s.acquire_other(110+off)
  for k,v in enumerate(c['objects']):s.present_object(v,reference_time=off,round_index=k)
  for r,sign in zip(s.geometry['regulators'],(-1,1)):
   t=r['teaching_tick']+off;s.input(r['cue_port'],5,t);s.input(r['event_ports'][str(sign)],11,t)
  rows=[]
  for k,t in enumerate((70,137,204)):
   s.run_until(t+off-1);pre=s.capture();s.run_until(t+off);post=s.capture();rows.append({'pre':pre,'post':post,'calculation':reading(s,pre,post,c['reference'],c['objects'][k])})
  s.save(out/(c['id']+'_FINAL.deetsnap.gz'));results.append({'id':c['id'],'preparations':1,'frames':rows,'inputs':s.receipts(),'final':physical(s.world)});del s;gc.collect()
 for c in cfg['forks']:
  path=ROOT/f'resultados/regulacion/RG_P01/T{c["parent_tick"]}.deetsnap.gz';parent=RegulatedQuantitySession.load(path);before=physical(parent.world);r=parent.geometry['regulators'][c['regulator']];q=move(r['neutralization_site'],(1 if c['regulator']==0 else -1,0,0));pre=parent.observe(q)
  e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=0 if c['mode']=='cut'else int(pre['raw']);e.label='AUDITOR_SELECTIVE_COUNTERFLOW_'+c['mode']
  child=parent.world.diagnostic_fork([e],True);s=RegulatedQuantitySession(child,parent.geometry,deepcopy(parent.state));trace=[]
  for t in sorted(set((c['parent_tick'],r['neutralization_tick'],r['neutralization_tick']+1,203,204))):
   if t<s.tick:continue
   s.run_until(t);row=s.capture();row['counterflow_meeting']=s.observe(r['neutralization_site']);trace.append(row)
  results.append({'id':c['id'],'preparations':0,'diagnostic_forks':1,'parent_path':path.relative_to(ROOT).as_posix(),'parent_unchanged':before==physical(parent.world),'intervention':{'pre':pre,'requested_raw':str(e.raw),'clock_edit':None},'frames':trace,'inputs':s.receipts(),'final':physical(s.world)});s.save(out/(c['id']+'_FINAL.deetsnap.gz'));del s,child,parent;gc.collect()
 baseline=json.loads((ROOT/'resultados/regulacion/RG_P01/MEASUREMENTS.json').read_text(encoding='utf-8'))['final']
 put(out/'MEASUREMENTS.json',{'schema':cfg['schema'],'config':cfg,'results':results,'shams_equal_fullphysical204':{r['id']:r['final']==baseline for r in results if r['id']in('RG_F102','RG_F104')},'resource_scope':'Two actual learned c16 pulses and fixed preparation/schedule; no independentenergymeasurement.'})
 print(json.dumps({'reserves':[{'id':r['id'],'correct':[x['calculation']['correct_function']for x in r['frames']]}for r in results if r['preparations']],
 'causal_final204':[{'id':r['id'],'reading':r['frames'][-1]['center'],'parent_unchanged':r['parent_unchanged']}for r in results if not r['preparations']]}))
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.out)
