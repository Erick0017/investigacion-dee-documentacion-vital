"""Explicit fresh initiativeE1 adapter with passive source/question boundaries."""
import argparse,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion import run_longitudinal_e1 as core
from integracion.initiative_e1 import InitiativeE1Session
from integracion.relational_pair import physical
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();holder={};extra=[]
 class Prepared(InitiativeE1Session):
  @classmethod
  def create(cls,**options):s=super().create(**options);holder['s']=s;return s
  def run_until(self,tick):
   for t in sorted(x for x in(3,70,72,77,86,340,344,417,428,436,484)if self.tick<x<=tick):
    super().run_until(t);path=a.out/('EXTRA_T'+str(t)+'.deetsnap.gz');storage=self.save(path);extra.append({'path':path.name,'tick':t,'sha256':core.sha(path),'physical':physical(self.world),'storage':storage})
   return super().run_until(tick)
 paths=(Path(__file__),ROOT/'src/integracion/initiative_e1.py',ROOT/'src/integracion/contact_renewal_e1.py',ROOT/'src/iniciativa_accion/solicitud.py');adapter={'factory':'integracion.initiative_e1.InitiativeE1Session','source_sha256':{p.name:core.sha(p)for p in paths},'scope':'FreshT0zero-materialports, questionconditionalonnativequantityproduct, sourceactualpostT0experience; nohostdecideswhetherorwhomtoask'};original=core.put
 def put(path,value):
  if Path(path).name=='MEASUREMENTS.json':value={**value,'factory_adapter':adapter,'extra_snapshots':extra}
  return original(path,value)
 core.LongitudinalE1Session=Prepared;core.put=put;sys.argv=[sys.argv[0],'--config',str(a.config),'--case-id',a.case_id,'--out',str(a.out)];core.main()
 s=holder['s'];m=json.loads((a.out/'MEASUREMENTS.json').read_text(encoding='utf8'));m.update(renewal_observations=s.state['renewal_observations'],initiative_captures=s.initiative.state['captures'],initiative_windows=s.state['initiative_windows']);m['snapshots']+=extra;m.pop('extra_snapshots',None);m['factory_adapter']=adapter;original(a.out/'MEASUREMENTS.json',m)
 for path in paths:shutil.copyfile(path,a.out/'executed_source'/path.name)
 print(json.dumps({'id':s.identifier,'initiative':[(r['tick'],[(b['question']['direction'],b['source']['direction'],{p:v['direction']for p,v in b['return'].items()})for b in r['branches']])for r in m['initiative_captures']if r['tick']in(72,77,86)]}),flush=True)
if __name__=='__main__':main()
