"""Pure administrative-rebinding unit checks; no runtime/world imports."""
from pathlib import Path
import copy,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];H=P/'codigo'
source=H/'pi10_vinculo_reproduccion_R01.py';sp=importlib.util.spec_from_file_location('PI10_pure_family_binding',source);b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
template='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL_01';life=b.PREFIX+'TEST202611'
documents={b.FILES[0]:{'schema':'DEE.PI10.exact_inherited_transport_scope.R01','life_id':template,'role':'real','source_main_life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01','unchanged_historical_content':{'a':17}},b.FILES[1]:{'schema':'DEE.PI10.fixed_experiment_scope.R01','life_id':template,'role':'evaluation','arm':'real','trace_control':'none','force_query':None,'protocol_sha256':'a'*64},b.FILES[2]:{'schema':'DEE.PI10.fixed_plugins.v1','plugins':['pi10_consulta_adaptativa_R01'],'files_sha256':{'other_scientific_body.py':'c'*64}}}
before=copy.deepcopy(documents);after=b.rebound_documents(documents,life,template);tests=[]
tests.append({'case':'source_documents_not_mutated','ok':documents==before})
tests.append({'case':'same_three_admin_files_only','ok':set(after)==set(b.FILES)and after[b.FILES[0]]['life_id']==after[b.FILES[1]]['life_id']==life and after[b.FILES[0]]['role']=='reproduction'})
aa=copy.deepcopy(after[b.FILES[0]]);aa.update(life_id=template,role='real');ee=copy.deepcopy(after[b.FILES[1]]);ee['life_id']=template
tests.append({'case':'only_identity_and_diagnostic_role_leaves_changed','ok':aa==before[b.FILES[0]]and ee==before[b.FILES[1]]and after[b.FILES[2]]['files_sha256']['other_scientific_body.py']=='c'*64})
bad=copy.deepcopy(documents);bad[b.FILES[1]]['force_query']=True;denied=False
try:b.rebound_documents(bad,life,template)
except ValueError:denied=True
tests.append({'case':'forced_calibration_cannot_become_real18_reproduction','ok':denied})
denied=False
try:b.rebound_documents(documents,template,template)
except ValueError:denied=True
tests.append({'case':'principal_or_nonfamily_identity_rejected','ok':denied})
assert all(t['ok']for t in tests)
value={'schema':'DEE.PI10.pure_RP_identity_binding_checks.R01','tests':tests,'instrument_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'Native_imports':0,'Native_ticks':0,'synthetic_documents_only':True,'product_modified':False};out=P/'control/PRUEBA_PURA_VINCULO_RP_PI10_R01.json'
if out.exists():assert json.loads(out.read_text('utf-8-sig'))==value
else:
 with out.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(value))
