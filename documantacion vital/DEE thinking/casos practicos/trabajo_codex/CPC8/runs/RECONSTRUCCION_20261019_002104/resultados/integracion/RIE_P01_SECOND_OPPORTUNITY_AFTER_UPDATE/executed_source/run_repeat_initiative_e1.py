"""Fresh longitudinal repeat protocol; no outcome-dependent input callback."""
import argparse,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion import run_longitudinal_e1 as core
from integracion.repeat_initiative_e1 import RepeatInitiativeE1Session
from integracion.relational_pair import physical

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();holder={};extra=[]
 class Prepared(RepeatInitiativeE1Session):
  @classmethod
  def create(cls,**options):s=super().create(**options);holder['s']=s;return s
  def run_until(self,tick):
   for t in sorted(x for x in(3,89,271,338,340,345,354,357)if self.tick<x<=tick):
    super().run_until(t);path=a.out/('EXTRA_T'+str(t)+'.deetsnap.gz');storage=self.save(path);extra.append({'path':path.name,'tick':t,'sha256':core.sha(path),'physical':physical(self.world),'storage':storage})
   return super().run_until(tick)
 paths=(Path(__file__),ROOT/'src/integracion/repeat_initiative_e1.py',ROOT/'src/integracion/initiative_use_e1.py',ROOT/'src/integracion/initiative_e1.py',ROOT/'src/integracion/contact_renewal_e1.py',ROOT/'src/iniciativa_accion/solicitud.py',ROOT/'src/iniciativa_accion/return_use.py');adapter={'factory':'integracion.repeat_initiative_e1.RepeatInitiativeE1Session','source_sha256':{p.name:core.sha(p)for p in paths},'scope':'Same frozen physical geometry with a second externally scheduled opportunity and current provider experience; all events fixed before evolution.'};original=core.put
 def put(path,value):
  if Path(path).name=='MEASUREMENTS.json':value={**value,'factory_adapter':adapter,'extra_snapshots':extra}
  return original(path,value)
 core.LongitudinalE1Session=Prepared;core.put=put;sys.argv=[sys.argv[0],'--config',str(a.config),'--case-id',a.case_id,'--out',str(a.out)];core.main()
 s=holder['s'];m=json.loads((a.out/'MEASUREMENTS.json').read_text(encoding='utf8'));m.update(renewal_observations=s.state['renewal_observations'],initiative_captures=s.initiative.state['captures'],initiative_windows=s.state['initiative_windows'],return_use_observations=s.state['return_use_observations'],repeat_initiative_observations=s.state['repeat_initiative_observations']);m['snapshots']+=extra;m.pop('extra_snapshots',None);m['factory_adapter']=adapter;original(a.out/'MEASUREMENTS.json',m)
 for path in paths:shutil.copyfile(path,a.out/'executed_source'/path.name)
 print(json.dumps({'id':s.identifier,'repeat357':next(r for r in m['repeat_initiative_observations']if r['tick']==357)}),flush=True)
if __name__=='__main__':main()
