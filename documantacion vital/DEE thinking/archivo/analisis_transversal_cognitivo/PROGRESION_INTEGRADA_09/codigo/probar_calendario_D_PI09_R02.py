"""Pure finite D timing bound, all782 reference residues; no DEE/Native."""
from pathlib import Path
import ast,hashlib,json,sys
H=Path(__file__).resolve().parent;P=H.parent
file=P.parent/'PROGRESION_INTEGRADA_07/codigo/pi03_credito_generico_R01_BORRADOR.py';data=file.read_bytes();tree=ast.parse(data.decode('utf-8-sig'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='schedule_trial');ns={'N':67,'REF_PERIOD':391,'REF_DOUBLE_PERIOD':782};exec(compile(ast.Module(body=[node],type_ignores=[]),str(file)+':pure_calendar_only','exec'),ns);schedule=ns['schedule_trial']
checks=[]
def require(ok,name):
    if not ok:raise AssertionError(name)
    checks.append(name)
def planned(start,clock,wait):
    body=start+wait;rc=clock+wait;first=schedule(body+16,rc+16,6);q1=first['query_tick'];inter=q1+412
    second=schedule(inter+16,rc+(inter-body)+16,6);q2=second['query_tick'];end=q2+412
    require(q2>=q1+782,'serial_second_'+str(clock)+'_'+str(wait));require(end-body<=2110,'unchanged_core_bound_'+str(clock)+'_'+str(wait));require(end-start<=2510,'whole_wait_plus_core_bound_'+str(clock)+'_'+str(wait))
    return {'start':start,'reference_clock_at_start':clock,'wait':wait,'q1':q1,'q2':q2,'end':end,'whole_ticks':end-start,'core_ticks':end-body,'q1_mod67':q1%67,'q2_mod67':q2%67,'reference_contact_phase':(rc+second['contact_tick']-body)%782}
rows=[]
for clock in range(782):
    base=planned(1000,clock,0);wait=planned(1000,clock,400);require(wait['q1']-base['q1']in(0,782),'prepared_window_shift_only_'+str(clock));rows.append({'reference_residue':clock,'base_whole':base['whole_ticks'],'wait_whole':wait['whole_ticks'],'query_window_shift':wait['q1']-base['q1']})
base=planned(1000,393,0);wait=planned(1000,393,400)
require(wait['q1']-base['q1']==wait['q2']-base['q2']==wait['end']-base['end']==782,'after_previous_settle393_wait400_skips_one782window')
require(base['whole_ticks']==1564 and wait['whole_ticks']==2346,'predicted_actual_age1564_vs2346_not_assumed400extra')
require(base['q1_mod67']!=wait['q1_mod67']and base['reference_contact_phase']==wait['reference_contact_phase']==391,'changes_global67_preserves_TC_contact391')
require(not any(k=='dee_thinking'or k.startswith('dee_thinking.')for k in sys.modules),'no_DEE_import')
out=P/'control/PRUEBA_CALENDARIO_D_PI09_R02.json';result={'schema':'DEE.PI09.D.fixed_wait_calendar.pure_bound.R02','passed':True,'Native_executed':False,'DEE_imported':False,'planning_not_observed_Native_transfer':True,'count':len(checks),'summary':{'reference_residues_checked':782,'waits_checked':[0,400],'max_base_whole':max(r['base_whole']for r in rows),'max_wait_whole':max(r['wait_whole']for r in rows),'source_clock_assumption_for_case3_and8':'Previous second-stage settleclock393 modulo782, if actualrefs retain the inherited contract','case3_and8_prediction':{'baseline':base,'wait400':wait},'scope':'Pure inherited scheduler prediction; record actual q1/q2/refclocks and N67phases after Native. No invariant/globalperiod claim.'},'checks':checks,'calendar_source':str(file),'calendar_source_sha256':hashlib.sha256(data).hexdigest()}
with out.open('x',encoding='utf8')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'count':len(checks),'max_wait_whole':result['summary']['max_wait_whole'],'query_shift_after_settle393':782,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
