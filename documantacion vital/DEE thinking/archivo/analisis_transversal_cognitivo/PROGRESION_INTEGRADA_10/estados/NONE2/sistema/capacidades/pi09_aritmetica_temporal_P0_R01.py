"""Prepared clock-only access guard; diagnostic, not learned regulation."""
from pathlib import Path
VERSION='DEE.PI09.prepared_clock_arithmetic_access.P0.R01'
MODES=frozenset({'eci01-pi09-aritmetica-temporal'})

def validate_literal(r):
 if not isinstance(r,dict)or set(r)!={'modo','operacion','izquierda','derecha','espera_previa','guardia_temporal'}:raise ValueError('Exact prepared request; no target/history/answer')
 if r['modo']not in MODES or r['operacion']not in ('suma','diferencia'):raise ValueError('Prepared operation')
 if any(type(r[k])is not int or not 0<=r[k]<=32 for k in ('izquierda','derecha')):raise ValueError('Independent integer operands0..32')
 if type(r['espera_previa'])is not int or not 0<=r['espera_previa']<=145 or type(r['guardia_temporal'])is not bool:raise ValueError('Explicit bounded P0 wait and guard boolean')
 return r

def query(start,protected=True):
 requested=start+56;effective=requested
 if protected:
  boundary=((requested-2)//391+1)*391
  if boundary<=requested+8:effective=boundary+2
 return effective

def challenge_wait(start,protected=True):
 for wait in range(146):
  if query(start+wait,protected)%67==19:return wait
 raise ValueError('No phase19 challenge within prospectively bounded145ticks')

def forecast(start,prewait,guard,protected=True):
 at=start+prewait;paid=0
 while guard and query(at,protected)%67==19:
  if paid>=11:raise ValueError('Clock guard unresolved; preserve, never outcome-retry')
  at+=1;paid+=1
 return {'start_tick':start,'explicit_pre_wait':prewait,'guard_paid_ticks':paid,'body_start_tick':at,'query_tick':query(at,protected),'body_end_tick':query(at,protected)+142}

def validate(a,r):
 validate_literal(r)
 from capacidades import pi09_aritmetica_diagnostica_R01 as base
 base.validate(a,{'modo':'eci01-pi09-aritmetica','operacion':r['operacion'],'izquierda':r['izquierda'],'derecha':r['derecha'],'espera':0})
 return r

def _perform(a,r,*,native_pair,physical,protected):
 before=physical(a.world);start=int(a.tick);prediction=forecast(start,r['espera_previa'],r['guardia_temporal'],protected)
 if r['espera_previa']:a.run_until(start+r['espera_previa'])
 require_tick=start+r['espera_previa']
 if int(a.tick)!=require_tick:raise ValueError('Legal wait mismatch; preserve')
 paid=0
 while r['guardia_temporal']and query(int(a.tick),protected)%67==19:
  if paid>=11:raise ValueError('Clock guard unresolved; preserve')
  next_tick=int(a.tick)+1;a.run_until(next_tick);paid+=1
  if int(a.tick)!=next_tick:raise ValueError('One-tick legal wait mismatch; preserve')
 if int(a.tick)!=prediction['body_start_tick']or paid!=prediction['guard_paid_ticks']:raise ValueError('Clock-only forecast mismatch before material operation; preserve')
 after_wait=physical(a.world);result=native_pair(a,r['operacion'],r['izquierda'],r['derecha'],detailed=True)
 if result['native_trial']['query_tick']!=prediction['query_tick']:raise ValueError('Frozen calendar mismatch; preserve actual future')
 return {'kind':'PI09_clock_only_prepared_arithmetic','version':VERSION,'literal_operator_request':dict(r),'before':before,'after_wait':after_wait,'after':physical(a.world),'forecast':prediction,'P0_guard_paid_ticks':paid,'explicit_pre_wait_ticks':r['espera_previa'],'native_operation':result,'numeric_reader':result['numeric_reader'],'numeric_result':result['numeric_reader']['numeric_result'],'scope':'Operator-selected arithmetic. Clock-only P0 delay; unchanged independent codec/body/C reader. No outcome, target, sensor or prior control result chooses delay; no learned regulation.'}

def dispatch(a,r,*,actuator='closed',directory=None):
 validate(a,r)
 if actuator!='closed':raise ValueError('Closed material protocol only')
 from capacidades import aritmetica_apd_01 as arithmetic,mente_unificada_01 as mu
 from app.native_tools import physical
 protection=mu.get(a).get('phase_protection')
 if protection and(protection.get('version')!='MUFI01.sensor_calendar.R3P0'or protection.get('enabled')is not True):raise ValueError('Unknown inherited calendar')
 return _perform(a,r,native_pair=arithmetic.native_pair,physical=physical,protected=bool(protection))

def code_files():
 home=Path(__file__).resolve().parent
 return tuple(home/n for n in (Path(__file__).name,'pi09_aritmetica_diagnostica_R01.py','aritmetica_directa_eci02.py','aritmetica_apd_01.py','percepcion_cruda_fi01.py','mente_unificada_01.py','selector_acrecion_nativo.py'))

def operational_dependencies(a=None,directory=None):return {'version':VERSION,'present':False,'stateless':True,'pending':None,'uncertain':False}
def uncertain(a=None):return False

def execute_public(a,row,*,actuator='closed'):
 """Legacy four-field request; exact Selected contract gate belongs to caller."""
 from capacidades import aritmetica_directa_eci02 as legacy,aritmetica_apd_01 as arithmetic,mente_unificada_01 as mu
 from app.native_tools import physical
 legacy.validate(a,row)
 if actuator!='closed':raise ValueError('Closed material protocol only')
 protection=mu.get(a).get('phase_protection')
 if protection and(protection.get('version')!='MUFI01.sensor_calendar.R3P0'or protection.get('enabled')is not True):raise ValueError('Unknown inherited calendar')
 internal={'modo':'eci01-pi09-aritmetica-temporal','operacion':row['operacion'],'izquierda':row['izquierda'],'derecha':row['derecha'],'espera_previa':0,'guardia_temporal':True}
 out=_perform(a,internal,native_pair=arithmetic.native_pair,physical=physical,protected=bool(protection))
 out['P0_internal_clock_request']=out.pop('literal_operator_request');out['literal_operator_request']=dict(row)
 out['public_access_scope']='Unchanged four-field operator request; fixed clock guard only. Caller must enforce exact committed selection/contract. No public phase, wait, guard switch or target.'
 return out
