"""Clock algebra, validation and orchestration pures. Native0, no DEE imports."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parents[1]


def main():
 forbidden=[]
 def audit(event,args):
  if event=='import'and str(args[0]).split('.')[0]in {'dee_thinking','app','capacidades','_native'}:
   forbidden.append(str(args[0]));raise RuntimeError('Native import forbidden')
 sys.addaudithook(audit)
 source=P/'codigo/pi09_aritmetica_temporal_P0_R01.py'
 ast.parse(source.read_text('utf8'))
 s=importlib.util.spec_from_file_location('P0clockpure',source);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 maxima={'challenge_wait':0,'guard_wait':0};cases=0
 for tick in range(52394):
  pre=m.challenge_wait(tick);maxima['challenge_wait']=max(maxima['challenge_wait'],pre)
  assert 0<=pre<=145 and m.query(tick+pre)%67==19
  for protected in (False,True):
   for guard in (False,True):
    x=m.forecast(tick,pre,guard,protected);assert 0<=x['guard_paid_ticks']<=11
    if guard:assert x['query_tick']%67!=19
    maxima['guard_wait']=max(maxima['guard_wait'],x['guard_paid_ticks']);cases+=1
 # Only the known official arithmetic calendar is copied: comparison uses the
 # previously verified forecast module, imported without any DEE/app entry.
 b=P/'codigo/pi09_aritmetica_diagnostica_R01.py';sp=importlib.util.spec_from_file_location('oldclockpure',b);base=importlib.util.module_from_spec(sp);sp.loader.exec_module(base)
 for tick in range(52394):
  for protected in (False,True):assert m.query(tick,protected)==base.forecast(tick,0,protected)['effective_query_tick']
 valid={'modo':'eci01-pi09-aritmetica-temporal','operacion':'suma','izquierda':2,'derecha':8,'espera_previa':0,'guardia_temporal':True}
 assert m.validate_literal(valid)is valid
 for change in ({'espera_previa':146},{'espera_previa':True},{'guardia_temporal':1},{'izquierda':True},{'target':10}):
  try:m.validate_literal({**valid,**change})
  except ValueError:pass
  else:raise AssertionError(change)
 class Fake:
  def __init__(self,tick):self.tick=tick;self.world=self;self.advances=[]
  def run_until(self,target):self.advances.append(target-self.tick);self.tick=target
 def physical(world):return {'N':67,'tick':world.tick,'MOCK':True}
 spies=[]
 def native(a,operation,left,right,*,detailed):
  spies.append((operation,left,right,detailed));q=m.query(a.tick);a.tick=q+142
  return {'native_trial':{'query_tick':q},'numeric_reader':{'numeric_result':None,'MOCK_NULL':True}}
 for tick in (1438,884835,884899):
  for guard in (False,True):
   a=Fake(tick);pre=m.challenge_wait(tick);r={**valid,'espera_previa':pre,'guardia_temporal':guard}
   out=m._perform(a,r,native_pair=native,physical=physical,protected=True)
   assert out['numeric_result']is None and spies[-1]==('suma',2,8,True)
   x=m.forecast(tick,pre,guard);assert a.tick==x['body_end_tick']and out['P0_guard_paid_ticks']==x['guard_paid_ticks']
   assert all(step==1 for step in a.advances[(1 if pre else 0):])
 output={'schema':'DEE.PI09.F1.P0_clock_access_pures.R01','all_passed':True,
         'period_start_ticks_checked':52394,'guard_forecasts_checked':cases,
         'existing_calendar_comparisons':104788,'maxima':maxima,
         'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'prior_unsealed_pure_negative':{'bound78_insufficient':True,'first_failure_tick':1438,'required_wait':133,'scope':'Host challenge alignment only; fixed before Native, no world was run.'},
         'orchestration_checks':'Six MOCK calls preserve literal operands/NULL and use only legal wait+unchanged native_pair callback; not engine evidence.',
         'Native':0,'DEE_imports':forbidden}
 out=P/'fuentes/PRUEBAS_PURAS_ACCESO_TEMPORAL_P0_PI09_R01.json'
 with out.open('x',encoding='utf8')as stream:json.dump(output,stream,ensure_ascii=False,indent=2);stream.write('\n')
 print(json.dumps({'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_sha256':output['source_sha256'],'maxima':maxima,'Native':0}))


if __name__=='__main__':main()
