"""Causal auditor branches only; edits never returned to any operational MAIN."""
import argparse,gc,hashlib,json,shutil,sys
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cantidad_renovable import QuantitySession,physical,move
from dee_thinking import _native as d
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(out):
 out.mkdir(parents=True,exist_ok=False);shutil.copyfile(Path(__file__),out/'EXECUTED_SOURCE.py')
 pp=ROOT/'resultados/cantidad/Q6_P01/T69.deetsnap.gz';parent=QuantitySession.load(pp);before=physical(parent.world);c=parent.geometry['center'];site=parent.geometry['reference_site']
 cfg={'case_id':'Q6_REFERENCE_CAUSAL_CUT','parent':str(pp.relative_to(ROOT)),'sha256':hashlib.sha256(pp.read_bytes()).hexdigest(),'frozen_before_load':True,'fork_tick':69,
 'intervention':'Remove only acquired reference at native comparison boundary; same-register byte-identical sham and local current-object cut. No clocks edited; no fork answer returned to parent.',
 'criterion':'At70 active normal1 load7 direction(+1,0,0) requires both actual material operands; capacity of other independent learned cue checked180 in all branches.'}
 put(out/'CONFIG.json',cfg);rows=[]
 for kind in('no_edit','reference_sham','reference_cut','object_cut'):
  edits=[]
  if kind!='no_edit':
   q=parent.geometry['object_site']if kind=='object_cut'else site;pre=parent.observe(q);e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=int(pre['raw'])if kind=='reference_sham'else 0;e.label='AUDITOR_DIAGNOSTIC_'+kind;edits=[e]
  child=parent.world.diagnostic_fork(edits,True);s=QuantitySession(child,deepcopy(parent.geometry),deepcopy(parent.state));trace=[]
  for t in(69,70,71,113,180):
   s.run_until(t);q=move(s.geometry['auxiliary_hub'],(0,1,0),t-113)
   trace.append({'tick':t,'frame':s.capture(),'other_relation_at_predicted_mobile_site':s.observe(q)})
  s.save(out/(kind+'_T180.deetsnap.gz'));rows.append({'condition':kind,'trace':trace,'inputs':s.receipts(),'final':physical(s.world)});del s,child;gc.collect()
 result={'case_id':cfg['case_id'],'config':cfg,'preparations':0,'diagnostic_forks':4,'continuations':0,'parent_before':before,'parent_after':physical(parent.world),'conditions':rows,
 'sham_full_physical_equal':rows[0]['final']==rows[1]['final'],'sham_all_receipts_equal':rows[0]['inputs']==rows[1]['inputs'],'parent_unchanged':before==physical(parent.world)}
 put(out/'MEASUREMENTS.json',result)
 print(json.dumps({'case_id':cfg['case_id'],'sham_equal':result['sham_full_physical_equal'],'parent_unchanged':result['parent_unchanged'],'observed70':[{ 'condition':x['condition'],'reading':x['trace'][1]['frame']['center'],'other180':x['trace'][-1]['other_relation_at_predicted_mobile_site']}for x in rows]}))
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.out)
