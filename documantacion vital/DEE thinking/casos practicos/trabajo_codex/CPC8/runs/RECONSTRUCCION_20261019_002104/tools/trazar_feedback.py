"""Passive diagnostic continuation of an adverse feedback candidate."""
import argparse,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from feedback_regulador import FeedbackSession
from cantidad_renovable import physical,move
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(out):
 out.mkdir(parents=True,exist_ok=False);shutil.copyfile(Path(__file__),out/'EXECUTED_SOURCE.py');source=ROOT/'resultados/regulacion/FB2_P01/T83.deetsnap.gz';s=FeedbackSession.load(source);c=s.geometry['center'];start=move(c,(1,0,0),12);rows=[];first=None
 for t in range(83,140):
  s.run_until(t);q=move(start,(1,0,0),t-83);o=s.observe(q);expected=o['active']and o['s_reg']==7 and o['direction']==[1,0,0]
  row={'tick':t,'predicted_uninteracted_site':q,'reading':o,'matches_uninteracted_carrier':expected,'intended_next_site':move(q,(1,0,0)),'destination_pre':s.observe(move(q,(1,0,0)))}
  if not expected and first is None:first=t
  if t in(135,136,137,138):row['Moore27']=[s.observe(move(q,v))for v in((x,y,z)for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1))];s.save(out/f'T{t}.deetsnap.gz')
  rows.append(row)
 put(out/'MEASUREMENTS.json',{'case_id':'FB2_PASSIVE_ROUTING_DIAGNOSIS','parent':source.relative_to(ROOT).as_posix(),'preparations':0,'continuations':1,'diagnostic_forks':0,'new_inputs':[],'trace':rows,'first_uninteracted_prediction_miss':first,'final':physical(s.world),
 'scope':'Tracks a predeclared counterflow prediction; a directionfield is not proof of successful transport into an occupied destination. No assertion that all physical information vanished elsewhere.'});print(json.dumps({'first_miss':first,'pre_first_miss':rows[first-84]if first else None}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.out)
