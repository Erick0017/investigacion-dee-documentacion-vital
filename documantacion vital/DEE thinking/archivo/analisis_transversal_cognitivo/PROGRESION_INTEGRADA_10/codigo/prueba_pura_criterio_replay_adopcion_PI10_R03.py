"""Synthetic acceptance/rejection checks only; never invokes base()/Store/DEE."""
from pathlib import Path
from datetime import datetime,timezone
import ast,copy,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;P=H.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def info(p):return {'path':str(p),'sha256':sha(p)}
actor=H/'incorporar_PI10_misma_identidad_R03.py';ast.parse(actor.read_bytes())
sp=importlib.util.spec_from_file_location('pure_PI10_staged_adopter_R03',actor);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
v={'schema':'DEE.PI10.actual_real12_RPF12.full_passive_comparison.R03','physical_equal':True,'overall':True,'unexpected_metadata_changes':[],
 'source_causal_prefix_sha256':'a'*64,'replay_causal_prefix_sha256':'b'*64,'binary_causal_prefix_equal':False,'causal_prefix_equal':False,
 'Native_structured_correspondence':{'normalized_equal':True,'unexplained_different_paths':[],'all_other_fields_and_fixed_bytes_preserved':True,'entire_original_prefix_hashes_preserved':True,'components_source':{'interfaces':4,'pending_agenda':0,'receipts':8,'phase':'advance'},'components_replay':{'interfaces':4,'pending_agenda':0,'receipts':8,'phase':'advance'},'exact_current_ID_label_paths_source':['/interfaces/0/name'],'exact_current_ID_label_paths_replay':['/interfaces/0/name']},
 'closed_replay_verified':{'status':'COMPLETED','owner_closed_coherently':True,'SQLite_integrity':'ok','unresolved_requests':0,'no_nonempty_WAL_or_journal':True,'result_criteria_met':True},
 'three_administrative_bindings_verified':{'files':sorted(m.BINDING_FILES),'proof_sha256':'c'*64,'all_other_capsule_files_literal':True,'Native_or_learned_state_files_changed':False}}
checks=[]
def check(name,x,expected):
 try:m.replay_comparison_admissible(x);accepted=True
 except ValueError:accepted=False
 assert accepted is expected,name
 checks.append({'name':name,'synthetic_input_only':True,'expected_accepted':expected,'actual_accepted':accepted,'passed':True})
check('exact transport-label correspondence distinct from binary equality',v,True)
x=copy.deepcopy(v);x['replay_causal_prefix_sha256']='a'*64;x['binary_causal_prefix_equal']=x['causal_prefix_equal']=True;check('exact binary alternative',x,True)
x=copy.deepcopy(v);x['binary_causal_prefix_equal']=True;check('reject false binary claim',x,False)
x=copy.deepcopy(v);x['Native_structured_correspondence']['unexplained_different_paths']=['/receipts/3/all_fixed_bytes_hex'];check('reject changed receipt payload',x,False)
x=copy.deepcopy(v);x['Native_structured_correspondence']['exact_current_ID_label_paths_source']=['/phase'];x['Native_structured_correspondence']['exact_current_ID_label_paths_replay']=['/phase'];check('reject phase normalization',x,False)
x=copy.deepcopy(v);x['Native_structured_correspondence']['exact_current_ID_label_paths_replay']=['/interfaces/1/name'];check('reject different ID paths',x,False)
x=copy.deepcopy(v);x['unexpected_metadata_changes']=['learned_bank'];check('reject learned metadata difference',x,False)
x=copy.deepcopy(v);x['three_administrative_bindings_verified']['files'][0]='memories.json';check('reject other administrative file binding',x,False)
x=copy.deepcopy(v);x['closed_replay_verified']['unresolved_requests']=1;check('reject pending request',x,False)
stamp=datetime.now(timezone.utc).isoformat();out=P/'control/PRUEBA_PURA_CRITERIO_ADOPCION_REPLAY_PI10_R03.json'
proof={'schema':'DEE.PI10.synthetic_adoption_replay_criterion_checks.R03','at':stamp,'Native_executed':False,'DEE_imported':False,'Store_called':False,'actual_replay_result_evaluated':False,'adopter':info(actor),'comparator':info(H/'comparar_reproduccion_PI10_R03.py'),'checks':checks,'passed':len(checks),'actual_Native_or_promotion_claimed':False}
with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
clar=P/'control/ACLARACION_PROSPECTIVA_COMPARACION_PI10_R03.json'
value={'schema':'DEE.PI10.prospective_replay_adoption_criterion_alignment.R03','recorded_utc':stamp,'reason':'Before cold acquisition replay, align the staged adopter with the already prospectively fixed complete R03 Native comparator. R02 demanded a binary hash equality that the R03 comparator correctly distinguishes from exact current-ID-label correspondence. No experimental result motivates this correction.','prior_adopter_preserved':info(H/'incorporar_PI10_misma_identidad_R02.py'),'new_staged_adopter':info(actor),'prospective_comparator':info(H/'comparar_reproduccion_PI10_R03.py'),'criterion':{'exact_physical':True,'complete_structured_Native_correspondence':True,'unexplained_different_paths':[],'all_other_fields_and_fixed_bytes_preserved':True,'both_original_causal_prefix_hashes_preserved':True,'metadata_strict':True,'either':'Exact binary causal prefix equality OR the same explicitly listed current transport-ID-label paths only; a normalized match is NEVER called binary equality.','allowed_label_paths_regex':r'^/(?:interfaces/\d+/name|pending/\d+/tags/\d+|receipts/\d+/(?:tags/\d+|detail))$','three_preimport_administrative_JSON_bindings_only':sorted(m.BINDING_FILES),'closed_operational_replay_and_existing_witness_criteria_required':True},'synthetic_verification':info(out),'actual_replay_result':None,'actual_replay_not_claimed':True,'product_or_state_modified':False,'Native_executed':False,'adoption_executed':False}
with clar.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'pure_checks':len(checks),'proof':info(out),'prospective_clarification':info(clar),'Native':0},ensure_ascii=False))
