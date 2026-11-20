"""Extract recorded acquisition/use costs of the bounded accumulator; stdlib, zero ticks."""
import argparse,ast,collections,gzip,hashlib,json
from pathlib import Path
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def walk(x):
 if isinstance(x,dict):
  yield x
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)
def requests(x):
 found={}
 for n in walk(x):
  if 'id'in n and isinstance(n.get('receipt'),dict):
   i=int(n['id'])
   if i in found and found[i]!=n:raise ValueError('Different request views inside one phase')
   if int(n['receipt']['id'])!=i:raise ValueError('Receipt identity differs')
   found[i]=n
 return found
def counts(x,final=None):
 r=requests(x);s=collections.Counter(str(n['receipt']['status'])for n in r.values())
 out={'requested_unique_within_this_world_phase':len(r),'receipt_statuses_at_recorded_capture':dict(sorted(s.items())),'request_ids':sorted(r)}
 if final is not None:
  values=[final[i]for i in r]
  out['later_final_receipt_statuses']=dict(sorted(collections.Counter(str(v['status'])for v in values).items()))
 return out
def calculate(root):
 sources=[]
 def source(rel,selectors):
  p=root/rel;sources.append({'file':rel,'bytes':p.stat().st_size,'sha256':sha(p),'JSON_locators':selectors});return read(p)
 p16=source('MAIN/P16_DOCENTE_CALCULO_MAIN.json.gz',['/elapsed_seconds','/result/result/preparation/nominal_corridor_before','/result/result/explicit_teacher_tool','/result/result/lesson/requests','/result/physical'])
 p17=source('MAIN/P17_NOVEDAD_SIN_DOCENTE_MAIN.json.gz',['/elapsed_seconds','/result/result/*/requests','/result/result/*/current_increment','/result/result/*/numeric_result','/result/physical'])
 for p in(p16,p17):
  if p['returncode']!=0 or p['timed_out']or json.loads(p['stdout'])!=p['result']:raise ValueError('Original supervised command incomplete or duplicate result differs')
 teach=p16['result']['result'];uses=p17['result']['result']
 ticks={int(n['tick'])for n in teach['preparation']['nominal_corridor_before']}
 if len(ticks)!=1 or teach['preparation']['new_native_ticks']!=0:raise ValueError('Initial tick is not uniquely witnessed')
 initial=ticks.pop();after=p16['result']['physical']['tick'];end=p17['result']['physical']['tick']
 if after!=teach['lesson']['arrival']or end!=uses[-1]['read_tick']:raise ValueError('Main phase boundary differs')
 tool=teach['explicit_teacher_tool']
 if tool.get('not_a_DEE_operation')is not True:raise ValueError('Teaching tool attribution differs')
 # Static executed-branch check, not a new application import or invocation.
 branches=source('FUENTES/REVISIONES_MAIN.json',['/*/primary','/*/included','/*/sha256'])
 checked=[]
 for primary,action in(('P16_DOCENTE_CALCULO_MAIN.json.gz','offset-docente'),('P17_NOVEDAD_SIN_DOCENTE_MAIN.json.gz','offset-usos')):
  row=next(x for x in branches if x['primary']==primary and x['original_relative'].endswith('/experimento_inicial.py'))
  file=root/'FUENTES'/row['included'];b=file.read_bytes()
  if sha(file)!=row['sha256']:raise ValueError('Executed source revision changed')
  nodes=[n for n in ast.walk(ast.parse(b.decode('utf-8-sig')))if isinstance(n,ast.If)and isinstance(n.test,ast.Compare)and any(isinstance(v,ast.Constant)and v.value==action for v in n.test.comparators)]
  if len(nodes)!=1:raise ValueError('Executed action branch not uniquely found')
  calls=[n for n in ast.walk(nodes[0])if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)]
  calc=sum(n.func.attr=='external_calculator'for n in calls)
  if calc!=(1 if action=='offset-docente'else 0):raise ValueError('Unexpected external calculator in executed branch')
  checked.append({'primary':primary,'relative_source':'FUENTES/'+row['included'],'source_sha256':row['sha256'],'executed_action_branch':action,'external_calculator_calls_in_branch':calc})
 last=after;urows=[]
 for u in uses:
  if u['step']!=len(urows):raise ValueError('Use order differs')
  urows.append({'step':u['step'],'initial_tick':last,'final_tick':u['read_tick'],'tick_delta':u['read_tick']-last,'current_increment':u['current_increment'],'numeric_result':u['numeric_result'],'abstention':u['abstention'],'native_inputs':counts(u),'external_calculator_calls_in_evaluation_branch':0})
  last=u['read_tick']
 main={'life':'ASISTENTE_MAIN','teaching':{'initial_tick':initial,'final_tick':after,'tick_delta':after-initial,'native_inputs':counts(teach['lesson']),'external_inline_teacher_calls':1,'external_tool':tool,'host_command_elapsed_seconds_recorded':p16['elapsed_seconds'],'teacher_pair_after_external_tool':teach['lesson']['teaching_pair'],'teacher_result_not_supplied_again_in_P17':True},'five_uses':{'initial_tick':after,'final_tick':end,'tick_delta':end-after,'native_inputs':counts(uses),'external_calculator_calls':0,'host_command_elapsed_seconds_recorded':p17['elapsed_seconds'],'uses':urows},'two_supervised_commands_elapsed_sum_not_contiguous_CPU_seconds':p16['elapsed_seconds']+p17['elapsed_seconds'],'native_preparation_ticks':0}
 final=source('CONTROLES/DELTA_RECIBOS_FINALES_COMPLETOS.json.gz',['/cases/*/id','/cases/*/pending','/cases/*/final_receipts_of_requested_events'])
 fcases={c['id']:c for c in final['cases']};controls=[];all_final=collections.Counter()
 for h in('T','U','D','H','CUT','SHAM'):
  d=source('CONTROLES/'+h+'/05_RESULTADO_COMPLETO.json.gz',['/result/parent_physical/tick','/result/lesson','/result/uses','/result/after_five_uses/tick','/result/old_six','/result/after_panel/tick'])['result']
  f=fcases[h];fm={int(n['id']):n['final_receipt']for n in f['final_receipts_of_requested_events']}
  if f['pending']:raise ValueError('Control retains unmatched pending native inputs')
  start=d['parent_physical']['tick'];at=d['lesson']['arrival'];five=d['after_five_uses']['tick'];panel=d['after_panel']['tick']
  phases=[('lesson',d['lesson']),('uses',d['uses']),('old_panel',d['old_six'])]
  c={name:counts(v,fm)for name,v in phases};whole=requests(d)
  if set(whole)!=set(fm):raise ValueError('Final receipt set differs from recorded full control')
  all_final.update(str(v['status'])for v in fm.values())
  controls.append({'history':h,'initial_tick':start,'after_teaching_tick':at,'after_five_uses_tick':five,'final_after_old_panel_tick':panel,'teaching_tick_delta':at-start,'five_uses_tick_delta':five-at,'old_panel_tick_delta':panel-five,'whole_tick_delta':panel-start,'phases':c,'whole_requested':len(whole),'teaching_mode':d['lesson']['teacher'],'intervention':d['lesson']['intervention'],'teacher_pair':d['lesson']['teaching_pair'],'outputs':[r['numeric_result']for r in d['uses']],'abstentions':[r['abstention']for r in d['uses']],'external_calculator_invocation_in_this_control':0,'teacher_contributions_are_explicit_prepared_inputs':True,'per_phase_or_per_control_host_elapsed_seconds':None})
 global_summary=source('CONTROLES/RESULTADOS.json',['/elapsed_seconds','/scope'])
 if dict(all_final)!={'2':325}:raise ValueError('325 final applied native receipts expected in existing archive')
 return {'schema':'APD01.recorded_accumulator_costs.N0.v1','native_ticks_executed_for_this_calculation':0,'main':main,'controls':controls,'control_final_native_receipts_status_enum_2_is_applied':dict(all_final),'control_supervisor_elapsed_seconds_all_six_with_panels_and_IO':global_summary['elapsed_seconds'],'executed_branches_checked_without_import':checked,'sources':sources,'limits':['Recorded supervised command wall times include import/load/save/instrumentation and are not CPU-only arithmetic times. No per-use latency, per-phase control CPU time or amortized speedup was recorded.','Six correlated control forks are not independent learners and their ticks are never added as one life age.','Native SUM with prepared two-operand tree is not the same task as an acquired offset plus cumulative increments; no matched break-even or saved-cost claim is established.','Five prepared opportunities were used. No sixth was tested; protocol exhaustion does not establish physical erasure or a universal five-use limit.','Control teaching pairs were explicit experimental inputs without the inline teaching-calculator call used once by MAIN P16. No teacher/reference/answer was supplied again during the recorded five evaluation uses.'],'amortized_savings':'INDETERMINATE_NO_COMPARABLE_DOMAIN_AND_CPU_MEASUREMENT','issues':[]}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--evidencia',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
 if a.salida.exists():raise FileExistsError('Keep earlier result')
 result=calculate(a.evidencia);a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8');print(json.dumps({'issues':len(result['issues']),'controls':len(result['controls']),'main_teaching_ticks':result['main']['teaching']['tick_delta'],'main_five_use_ticks':result['main']['five_uses']['tick_delta'],'new_ticks':0}))
if __name__=='__main__':main()

