"""Pruebas puras del suplemento Source0 y enlaces CLI; ningún estado se abre."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,subprocess,sys
H=Path(__file__).resolve().parent;P=H.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sp=importlib.util.spec_from_file_location('pure_D_admin_source0',H/'incorporar_D_PI09_misma_identidad_R02.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
flags=('physical_unchanged','causal_prefix_equal','operational_state_valid','pending_reconciled','stock_unchanged','all_scientific_metadata_literal_unchanged','source_code_unchanged','current_principal_unchanged','owner_closed','closed')
zero={'schema':'DEE.PI09.D.mature_source.public_reopening0.R01','life_id':m.LIFE,'selected':False,'new_ticks':0,'new_Native_inputs':0,'initial_tick':920000,'final_tick':920000,'snapshot_sha256':'a'*64,'after_snapshot':{'sha256':'a'*64},'stock_before':{'D':{'ordinal':7,'total':12,'remaining':5}},'stock_after':{'D':{'ordinal':7,'total':12,'remaining':5}},'Native_field_equalities':{k:True for k in('physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase')},**{k:True for k in flags}}
d={'D_source_zero_reopening_proof':{},'source_tick':920000,'source_snapshot_sha256':'a'*64,'source_D_ordinal':7};checks=[]
m.m.evidence=lambda ref:zero;m.validate_source_zero(d);checks.append('source0_dynamic_stock7_12_accepted')
for key in flags:
 bad=copy.deepcopy(zero);bad[key]=False;m.m.evidence=lambda ref,bad=bad:bad
 try:m.validate_source_zero(d)
 except ValueError:checks.append('reject_false_'+key)
 else:raise AssertionError(key)
for key,value in(('new_ticks',1),('new_Native_inputs',1),('snapshot_sha256','b'*64),('selected',True),('life_id','OTHER')):
 bad=copy.deepcopy(zero);bad[key]=value;m.m.evidence=lambda ref,bad=bad:bad
 try:m.validate_source_zero(d)
 except ValueError:checks.append('reject_'+key)
 else:raise AssertionError(key)
for name in('incorporar_D_PI09_misma_identidad_R02.py','construir_decision_D_PI09_R01.py','usar_principal_NATIVE_EP12_PI09_R01.py'):
 ast.parse((H/name).read_bytes());checks.append('AST_'+name)
needles={'construir_decision_D_PI09_R01.py':['--aprobar','D_source_zero_reopening_proof','m.code(d)','m.base().selector_cas(d)'],'usar_principal_NATIVE_EP12_PI09_R01.py':['--confirmar-no-adopcion-D',"'--retorno','real'","'ordinal_before':12","'ordinal_after':13","'Native_field_equalities':fields"]}
for name,parts in needles.items():
 text=(H/name).read_text('utf8');assert all(n in text for n in parts);checks.append('CLI_contract_'+name)
for name in('incorporar_D_PI09_misma_identidad_R02.py','usar_principal_NATIVE_EP12_PI09_R01.py'):
 r=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(H/name)],capture_output=True,text=True,check=True);json.loads(r.stdout);checks.append('actual_default_no_state_'+name)
# Immutable source/code-only closure; does not call inventory/decision/Store.
plan=json.loads((H/'DELTA_D_OPERATIVO_R01_PROPUESTO/PLAN.json').read_text('utf8'));rows=m.code({'new_contract':plan['new_contract'],'approved_code_files':plan['approved_code_files']});checks.append('actual_immutable_D_source_product_code_CAS_'+str(len(rows)))
out=P/'control/PRUEBA_CIERRE_PREPARADO_D_PI09_R02.json';assert not out.exists()
result={'schema':'DEE.PI09.D.prepared_admin_source0.pure_checks.R02','passed':True,'checks':checks,'count':len(checks),'Native_imports':False,'Native_ticks':0,'product_writes':False,'state_SQL_or_live_card_reads':False,'code_only_CAS_files':len(rows),'source_sha256':{name:sha(H/name)for name in('incorporar_D_PI09_misma_identidad_R01.py','incorporar_D_PI09_misma_identidad_R02.py','construir_decision_D_PI09_R01.py','usar_principal_NATIVE_EP12_PI09_R01.py')}}
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'proof':str(out),'sha256':sha(out),'count':len(checks),'passed':True}))
