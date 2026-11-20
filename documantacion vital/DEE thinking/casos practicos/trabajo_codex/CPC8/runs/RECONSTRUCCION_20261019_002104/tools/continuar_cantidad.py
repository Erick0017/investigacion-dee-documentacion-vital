"""Another-process persistence and a genuinely new post-load interaction."""
import argparse,hashlib,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cantidad_renovable import QuantitySession,physical,move
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(source,out):
 out.mkdir(parents=True,exist_ok=False);shutil.copyfile(Path(__file__),out/'EXECUTED_SOURCE.py')
 cfg={'source':source.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'frozen_before_load':True,
 'new_actual_object':37,'format_matter_load':0,'object_input_tick':601,'reader_input_tick':605,'reading_tick':606,'end_tick':608,
 'criterion':'Restored native reference42 and currentobject37 give activec7dir(+1,0,0). Prediction external and registered before input; no target passed into participant.'}
 put(out/'CONFIG.json',cfg);s=QuantitySession.load(source);initial=physical(s.world);s.run_until(541);before_new=physical(s.world);receipts_before=s.receipts()
 put(out/'PREDICTION.json',{'registered_tick':s.tick,'reading_tick':606,'auditor_expected_direction':[1,0,0],'participant_receives_only_actual_payloads':[0,37,7]})
 s.input('quantity.object.cue',0,601);s.input('quantity.object.resource',37,601);s.input('quantity.reader',7,605,True)
 s.run_until(605);pre=s.capture();s.run_until(606);post=s.capture();s.run_until(608);c=s.geometry['center'];destinations=[{'sign':sgn,'reading':s.observe(move(c,(sgn,0,0),2))}for sgn in(-1,1)]
 s.save(out/'T608.deetsnap.gz');o=post['center'];q=pre['reference'];qualified=q['active']and q['s_reg']==42 and q['direction']==[0,1,0]and o['active']and o['s_reg']==7 and o['direction']==[1,0,0]
 result={'schema':'CPC8R.quantity.restored_new_interaction.v1','config':cfg,'preparations':0,'continuations':1,'diagnostic_forks':0,'initial':initial,'physical541':before_new,'receipts541':receipts_before,'new_pre':pre,'new_post':post,'new_destinations608':destinations,'qualified_new_function':bool(qualified),'final':physical(s.world),'receipts_final':s.receipts(),'channels':sorted(s.world.runtime.channel_names),
 'operational_scope':'Queue execution and all native receipts/channels compared. Passive observation-history metadata may differ because the intermediate process did not re-observe every old tick; it is never used as participant memory.'}
 put(out/'MEASUREMENTS.json',result);print(json.dumps({'source':cfg['source'],'qualified_new_function':qualified,'physical541':before_new,'final':result['final']}))
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.source,a.out)
