"""Finite external curriculum and auditor; no target feedback to the world."""
import argparse,hashlib,json,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cantidad_renovable import QuantitySession,physical
CASES={'Q5_P01':(31,[16,45,31],'paired'),'Q5_H01':(11,[16,45,31],'paired'),'Q5_N01':(31,[16,45,31],'no_cue'),'Q5_N02':(31,[16,45,31],'unpaired'),
 'Q5_R01':(17,[10,39,17],'paired'),'Q5_R02':(31,[54,6,31],'paired'),'Q5_C01':(31,[16,45,31],'paired')}
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(name,out):
 out.mkdir(parents=True,exist_ok=False);r,objects,history=CASES[name]
 cfg={'case_id':name,'reference':r,'current_objects':objects,'history':history,'compare_ticks':[70,137,204],'other_acquisition_tick':110,'frozen_before_constructor':True,
 'criterion':'At each comparison native X sign from acquired reference vs actual new object. No Z bias. Zero X is an observed equality state, never silence. Reference availability is separately checked, not inferred from an apparently correct direction.',
 'reserve':'R01/R02 held-out magnitudes, no feedback or re-teaching reference between tests within each world. Each world separately identified.'}
 write(out/'CONFIG.json',cfg)
 for p in(Path(__file__),ROOT/'src/cantidad_renovable.py'):shutil.copyfile(p,out/p.name)
 s=QuantitySession.create(guards='off_path'if name=='Q5_C01'else'on_path');s.experience_reference(r,mode=history);s.reader_opportunity();s.acquire_other()
 for k,value in enumerate(objects):s.present_object(value,round_index=k)
 s.save(out/'T0.deetsnap.gz');rows=[]
 for tick in(3,68,69,70,71,74,110,113,135,136,137,138,180,202,203,204,205):
  s.run_until(tick);rows.append(s.capture())
  if tick in(69,70,137,180,204):s.save(out/f'T{tick}.deetsnap.gz')
 readings=[]
 for k,t in enumerate(cfg['compare_ticks']):
  obs=next(x for x in rows if x['tick']==t);expected=(r>objects[k])-(r<objects[k]);ref=next(x for x in rows if x['tick']==t-1)['reference']
  readings.append({'tick':t,'raw_reading':obs['center'],'reference_pre':ref,'expected_auditor_only':expected,'correct_direction':obs['center']['direction']==[expected,0,0],
   'acquired_reference_available':ref['active']and ref['s_reg']==r+5,'world_received_target':False})
 result={'schema':'CPC8R.quantity.recurrent.measurements.v2','case_id':name,'preparations':1,'modality':'NEW_INDEPENDENT_LIFE_NOT_E1_UNTIL_PHYSICALLY_INTEGRATED',
 'config':cfg,'geometry':s.geometry,'inputs':s.receipts(),'observations':rows,'calculations':readings,'final':physical(s.world),'RAW_clock_edits':[],
 'scope':'Gradient law and geometry prepared, reference history acquired. Actual current quantities are not computed comparison answers; no reinforcement rule learned.'}
 write(out/'MEASUREMENTS.json',result);print(json.dumps({'case_id':name,'results':[{'tick':x['tick'],'direction':x['raw_reading']['direction'],'reference_present':x['acquired_reference_available'],'correct_direction':x['correct_direction']}for x in readings]}))
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('--case',required=True,choices=CASES);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.case,a.out)
