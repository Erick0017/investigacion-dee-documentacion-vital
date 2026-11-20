"""Recompute acquired-regulation function from exact pre/post operands."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def locus(p):return{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def run():
 rows=[]
 for name in('RE_P01','RE2_P01','RE2_H01','RE2_N01','RE2_C01','RE2_R01_TOKEN_REPAIR'):
  path=ROOT/'resultados/integracion'/name/'MEASUREMENTS.json';m=read(path);opts=m['configuration']['options'];ref=opts.get('quantity_reference',31);objects=opts.get('quantity_objects',[16,45,31]);new=ref+5+opts.get('addition_value',11);late=opts.get('late_object',36);f={x['tick']:x for x in m['observations']};trials=[]
  for t,reference,obj in zip((70,137,204,539),(ref+5,ref+5,ref+5,new),[*[x+5 for x in objects],late+5]):
   pre=f[t-1]['quantity'];out=f[t]['quantity']['center'];r=pre['reference_site'];o=pre['object_site'];expected=[(reference>obj)-(reference<obj),0,0]
   operands=bool(r['active']and r['direction']==[0,1,0]and r['s_reg']==reference and o['active']and o['direction']==[0,1,0]and o['s_reg']==obj)
   trials.append({'tick':t,'pre_reference':r,'pre_object':o,'output':out,'expected_reference_auditor':reference,'expected_current_object_auditor':obj,'expected_direction_auditor':expected,'operands_preserved':operands,'qualified_function':bool(operands and out['active']and out['semantic']==1 and out['state']==1 and out['s_reg']==7 and out['direction']==expected)})
  word=[{'bank':k,'reading':v['delivery_site']}for k,v in f[549]['joint'].items()if v['delivery_site']['active']and v['delivery_site']['direction']==[0,1,1]and v['delivery_site']['s_reg']>11]
  maint=[x for x in m['inputs']if x.get('origin')in('EXTERNAL_MAINTENANCE_REEXPOSURE_COUNTED','ACTUAL_DIRECTION_EVENT_REEXPOSURE_NOT_NATIVE_POLICY')]
  rows.append({'id':name,'source':locus(path),'trials':trials,'correct_count':sum(x['qualified_function']for x in trials),'denominator':4,'old_word549':word,'external_maintenance_packets_requested':len(maint),'external_maintenance_payload_requested':sum(x['payload']for x in maint),'external_maintenance_receipts':maint,'preparations':1,'independent_replication':'Distinct histories/control conditions; deterministic repeated technical execution is not a new independent replicate.'})
 cp=ROOT/'resultados/integracion/RE2_CAUSAL_RESTORE/MEASUREMENTS.json';c=read(cp)
 summary={'schema':'CPC8R.finiteE1.acquiredRegulation.audit.v1','data':rows,'causal_and_restoration':{'source':locus(cp),'results':[{'mode':x['mode'],'parent_unchanged':x['parent_unchanged'],'exact_physical549':x['full_physical549_equal_baseline'],'exact_receipts549':x['native_receipts549_equal'],'new_word616':None if x['mode']!='restore'else x['frames'][-1]['joint'],'late_quantity539':next(f['quantity']for f in x['frames']if f['tick']==539)}for x in c['results']]},
 'formulas':{'direction':'sign((acquired reference payload +format5+actual added payload) - (current object payload+format5))','function':'exact acquired operand +exact current operand +active state1 semantic1 load7 output with fixedexpectedvector; absent0neverequalsvalidzero','retention':'one acquired composite word decoded after intervening quantity update and maintenance, not an assertion that all historicalrepertoires survived'},
 'provisional_interpretation':'Finite R1coexistence demonstrated: acquired counterflow directions and FOUR EXTRA externally scheduled paired teaching episodes protect quantity539 while old composite word549 remains. Opposite/unpaired/omitted maintenance fails late quantity. v1fails without those later exposures. This is not autonomous replay, R2strategy selection, nor identical resource/exposure budget to the fixedguard IUEprofile.',
 'technical_failure':'RE2_R01 wrong actor token free rejected beforeRuntime; originalCONFIG/source/stderr preserved, corrected token offpath produces separately identified technical execution, not new scientific reserve selected from results.'}
 (ROOT/'revision/REGULACION_E1_FINITA.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps([{'id':x['id'],'correct':x['correct_count'],'n':4,'word':len(x['old_word549'])}for x in rows]))
if __name__=='__main__':run()
