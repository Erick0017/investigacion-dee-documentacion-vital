"""Frozen sparse E1 acquired-regulation candidates and history controls."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from integracion.regulated_finite_e1 import RegulatedFiniteE1Session
from integracion.relational_pair import physical,move
CASES={'RE_P01':{},'RE_H01':{'directions':(1,1)},'RE_H02':{'directions':(-1,-1)},'RE_N01':{'regulation':'omitted'},'RE_C01':{'regulation':'unpaired'},'RE_R01':{'order':'BA','actor_mode':'free','quantity_reference':17,'quantity_objects':(9,37,17),'addition_value':19,'late_object':27}}

def run(case,out):
 out.mkdir(parents=True,exist_ok=False);options=dict(CASES[case]);actor=options.pop('actor_mode','contact');cfg={'case_id':case,'actor_mode':actor,'options':options,'frozen_before_create':True,'scope':'New life; sparse late quantity use, no368/405/472 reads; explicit additional acquired regulator experiences, not interchangeable with LCE/IUE seven-query exposure.'}
 (out/'CONFIG.json').write_text(json.dumps(cfg,indent=2)+'\n',encoding='utf-8')
 s=RegulatedFiniteE1Session.create(identifier=case,actor_mode=actor);s.curriculum(**options);s.save(out/'T0.deetsnap.gz');rows=[]
 for t in(3,31,69,70,73,74,75,103,136,137,140,141,142,143,165,170,203,204,206,227,235,268,270,271,281,348,415,538,539,549):
  s.run_until(t);v=s.view();v['regulator_regions']=[{'id':r['id'],'hub':s.observe(r['hub']),'meeting':s.observe(r['neutralization_site']),'Moore27':[s.observe(move(r['neutralization_site'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for r in s.geometry['acquired_regulation']];rows.append(v)
  if t in(73,140,271,549):s.save(out/f'T{t}.deetsnap.gz')
 data={'case_id':case,'configuration':cfg,'preparations':1,'continuations':0,'diagnostic_forks':0,'geometry':s.geometry,'inputs':s.receipts(),'observations':rows,'final':physical(s.world),'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in(Path(__file__),ROOT/'src/integracion/regulated_finite_e1.py')},'MAIN_RAW_clock_edits':[]}
 (out/'MEASUREMENTS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'case_id':case,'quantity':[(x['tick'],x['quantity']['center']['direction'],x['quantity']['center']['s_reg'])for x in rows if x['tick']in(70,137,204,539)],'old_word549':rows[-1]['joint']}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',choices=CASES,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.case,a.out)
