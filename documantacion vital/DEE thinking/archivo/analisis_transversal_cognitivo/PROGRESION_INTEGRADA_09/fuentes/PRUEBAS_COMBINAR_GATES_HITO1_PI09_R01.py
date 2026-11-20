"""Pure API tests. The reopening input is SYNTHETIC, never evidence of a run."""
from pathlib import Path
import copy,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1]
file=P/'fuentes/COMBINAR_GATES_HITO1_PI09_R01.py'
spec=importlib.util.spec_from_file_location('pure_combiner',file)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
names={'science':'fuentes/EVALUACION_CUATRO_CIERRES_PI09_R01.json','panels':'control/PANELES_HITO1_VERIFICADOS_PI09_R01.json','rp_compare':'control/CONTRASTE_RP_NATIVE12_PI09_R01.json','rp_registration':'control/RP_NATIVE12_REGISTRADA_PI09_R01.json'}
v={};refs={}
for k,n in names.items():v[k],refs[k]=m.load(P/n)
refs['source0']={'path':'SYNTHETIC_REOPENING_NOT_EXECUTED','sha256':'0'*64}
source={'schema':'DEE.PI09.mature_source.public_reopening0.R01','closed':True,'owner_closed':True,'life_id':m.LIFE,'initial_tick':903603,'final_tick':903603,'new_ticks':0,'new_Native_inputs':0,'Native_field_equalities':dict.fromkeys(['physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase'],True),'stock_before':{'PI09':{'ordinal':12,'total':18,'remaining':6},'C2C':{'ordinal':31,'total':32,'remaining':1},'FI':{'ordinal':4,'total':8,'remaining':4}},'snapshot_sha256':'1'*64,'after_snapshot':{'sha256':'1'*64},'public_STATE_rows':[]}
source['stock_after']=copy.deepcopy(source['stock_before'])
source['source_record_after']={'life_id':m.LIFE,'physical':v['rp_compare']['source_physical'],'snapshot_sha256':'1'*64}
source.update(dict.fromkeys(['operational_state_valid','pending_reconciled','physical_unchanged','causal_prefix_equal','stock_unchanged','all_scientific_metadata_literal_unchanged','source_code_unchanged','current_principal_unchanged','same_life_and_world_no_clone'],True))
def run(s=None,p=None,r=None,reg=None):return m.combine(v['science'],p or v['panels'],s or source,r or v['rp_compare'],reg or v['rp_registration'],refs)
checks=[]
def ok(name,fn):fn();checks.append(name)
def rejects(fn):
    try:fn()
    except (ValueError,KeyError):return
    raise AssertionError('Expected rejection')
def base():
    x=run();assert x['all_fixed_evidence_gates_met'] and x['approval'] is False
    assert x['gates']['conservation']['satisfied'] and not v['panels']['P0_public_access_gate']['satisfied']
ok('Synthetic positive schema only; optional P0 gain0 does not reject actual literal conservation',base)
for name,key,val in [('extra ticks','new_ticks',1),('wrong current identity','life_id','OTHER'),('unclosed reopening','closed',False)]:
    x=copy.deepcopy(source);x[key]=val;ok(name,lambda x=x:rejects(lambda:run(s=x)))
x=copy.deepcopy(source);x['Native_field_equalities']['native_receipts']=False;ok('Native field mismatch rejected',lambda:rejects(lambda:run(s=x)))
x=copy.deepcopy(source);x['stock_after']['PI09']['ordinal']=0;ok('Counter reset rejected',lambda:rejects(lambda:run(s=x)))
r=copy.deepcopy(v['rp_compare']);r['overall']=False;ok('Failed strict RP comparator remains failed',lambda:rejects(lambda:run(r=r)))
reg=copy.deepcopy(v['rp_registration']);reg['registered']=False;ok('Prepared/unregistered recipe insufficient',lambda:rejects(lambda:run(reg=reg)))
p=copy.deepcopy(v['panels']);p['legacy']['words_context_correct']=6;p['P0_public_access_gate']['satisfied']=False
ok('Neither conservation route passes => six-gate conjunction false',lambda:None if not run(p=p)['all_fixed_evidence_gates_met'] else (_ for _ in()).throw(AssertionError()))
print(json.dumps({'schema':'DEE.PI09.combined_gates.synthetic_tests.R01','passed':len(checks),'checks':checks,'reopening_fixture':'SYNTHETIC_NOT_AN_ACTUAL_CLOSURE','actual_combined_evaluation_written':False,'Native_executed':False,'DEE_imported':False,'code_sha256':hashlib.sha256(file.read_bytes()).hexdigest()},ensure_ascii=False,indent=2))
