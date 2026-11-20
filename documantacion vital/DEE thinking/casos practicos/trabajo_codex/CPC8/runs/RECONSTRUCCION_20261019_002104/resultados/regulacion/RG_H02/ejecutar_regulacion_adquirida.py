"""Finite causal history contrasts, never a hidden feedback policy."""
import argparse,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from regulacion_adquirida import RegulatedQuantitySession
from cantidad_renovable import physical,move
CASES={'RG_P01':((-1,1),'paired'),'RG_H01':((1,1),'paired'),'RG_H02':((-1,-1),'paired'),'RG_N01':((-1,1),'unpaired'),'RG_N02':((-1,1),'omitted')}
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(case,out):
 out.mkdir(parents=True,exist_ok=False);directions,mode=CASES[case];cfg={'case_id':case,'directions':directions,'experience':mode,'frozen_before_constructor':True,
 'criterion':'Compare actualquantityreadings70/137/204 and referencepresence. For neutralization74/141, save exact pre/post neighborhood and nextstate; never infer annihilation by equalpayload alone.',
 'modality':'R1experimental acquired direction under fixed opportunities; no learnedstrategy, no hostcorrection, no permanent onpathguards.'}
 put(out/'CONFIG.json',cfg)
 for p in(Path(__file__),ROOT/'src/regulacion_adquirida.py',ROOT/'src/cantidad_renovable.py'):shutil.copyfile(p,out/p.name)
 s=RegulatedQuantitySession.create();s.experience_reference(31);s.reader_opportunity();s.acquire_other();s.regulation_experience(directions,mode)
 for k,v in enumerate((16,45,31)):s.present_object(v,round_index=k)
 s.save(out/'T0.deetsnap.gz');rows=[]
 for t in(3,69,70,73,74,75,103,136,137,140,141,142,180,203,204):
  s.run_until(t);row=s.capture();row['regulators']=s.regulation_view();row['neutralization_windows']=[]
  for r in s.geometry['regulators']:
   q=r['neutralization_site'];row['neutralization_windows'].append({'id':r['id'],'center':q,'Moore27':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
  rows.append(row)
  if t in(69,73,74,103,140,141,204):s.save(out/f'T{t}.deetsnap.gz')
 readings=[]
 for k,t in enumerate((70,137,204)):
  pre=next(x for x in rows if x['tick']==t-1)['reference'];o=next(x for x in rows if x['tick']==t)['center'];expected=[1,-1,0][k]
  readings.append({'tick':t,'reading':o,'reference_pre':pre,'correct_with_reference':bool(pre['active']and pre['s_reg']==36 and pre['direction']==[0,1,0]and o['active']and o['s_reg']==7 and o['direction']==[expected,0,0])})
 put(out/'MEASUREMENTS.json',{'case_id':case,'config':cfg,'geometry':s.geometry,'preparations':1,'continuations':0,'diagnostic_forks':0,'observations':rows,'inputs':s.receipts(),'readings':readings,'final':physical(s.world),'RAW_clock_edits_on_MAIN':[]})
 print(json.dumps({'case_id':case,'readings':readings},ensure_ascii=False))
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('--case',choices=CASES,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.case,a.out)
