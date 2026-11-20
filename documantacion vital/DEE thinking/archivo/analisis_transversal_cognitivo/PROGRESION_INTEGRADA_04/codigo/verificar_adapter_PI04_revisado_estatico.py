"""Static/read-only adapter checks. No decision file, Native or deployment."""
from pathlib import Path
import ast,contextlib,datetime,hashlib,io,json,runpy,sys
P4=Path(__file__).resolve().parents[1]
CODE=P4/'codigo/incorporar_PI04_REVISADO.py'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    output=P4/'control/ADAPTER_PI04_REVISADO_VERIFICACION_ESTATICA_R01.json'
    if output.exists():raise FileExistsError('Preserve previous verification')
    g=runpy.run_path(str(CODE),run_name='pure_PI04_adapter_definition')
    before=ast.parse((CODE.parent/'incorporar_PI04_BORRADOR.py').read_text(encoding='utf-8-sig'))
    after=ast.parse(CODE.read_text(encoding='utf-8-sig'))
    functions=lambda tree:{n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    old=functions(before);new=functions(after)
    changes=[k for k in old if ast.dump(old[k])!=ast.dump(new[k])]
    protected=[g['C']/'PROYECTO.json',g['C']/'CONTINUIDAD_DEE_COGNITIVE_2_0.json',g['S']/'estado/ACTIVO.json',g['S']/'estado/genesis/SELECCION_PERSONAL.json',g['S']/'estado/vidas'/g['PARENT']/'VIDA.json',g['S']/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl',g['C']/'motor/python313/site-packages/dee_thinking/_native.cp313-win_amd64.pyd']
    hashes_before={str(p):sha(p)for p in protected}
    tests=[]
    def check(name,fn,accept=True):
        try:value=fn();passed=True;error=None
        except Exception as e:value=None;passed=False;error=type(e).__name__+': '+str(e)
        if passed!=accept:raise AssertionError(name+' unexpected '+str(error))
        tests.append({'name':name,'expected_accept':accept,'accepted':passed,'error':error})
        return value
    check('three_current_parent_selectors_and_exact_parent_snapshot_readonly',g['protect_parent'])
    check('all_product_identity_subtrees_and_checkpoints_absent',g['require_unused_product_identity'])
    check('missing_storage_budget_blocks_before_copy',lambda:g['storage_gate']({}, {}, {}, []),False)
    for value in ('../outside','C:/outside','a\\b','/rooted'):
        check('unsafe_relative_'+value,lambda value=value:g['safe_relative'](value),False)
    check('resolved_parent_escape_rejected',lambda:g['checked'](P4/'../outside',P4,must_exist=False),False)
    # Literal in-memory invalid decision tests are not historical evidence and
    # are never serialized as DECISION_FINAL_PI04 or passed to a Native phase.
    saved_read=g['load_decision'].__globals__['read']
    try:
        g['load_decision'].__globals__['read']=lambda p:{'adapter_reviewed_for_PI04':False}
        check('no_review_blocks_before_native',lambda:g['load_decision'](Path('NOT_A_DECISION_FILE')),False)
        keys=('approved_for_adoption','life_id','desired_cut','pair','approved_code_files','gates','scope','gains','losses','uncertainties','assistance','evidence','regression_coverage','process_proof','catalog_entry','new_contract','stable_pair_relative_to_product')
        rejected={k:None for k in keys};rejected.update(adapter_reviewed_for_PI04=True,campaign='PROGRESION_INTEGRADA_04',approved_for_adoption=False,life_id=g['LIFE'])
        g['load_decision'].__globals__['read']=lambda p:rejected
        check('explicit_adoption_false_blocks_before_native',lambda:g['load_decision'](Path('NOT_A_DECISION_FILE')),False)
    finally:g['load_decision'].__globals__['read']=saved_read
    # Actual stable export and all3990 files, checked without a Native import.
    export_path=P4/'control/EXPORTACION_ESTABLE_PI03_PI04_C2C_POST_RES_T816019.json'
    export=json.loads(export_path.read_text(encoding='utf-8-sig'))
    assert export['schema']=='DEE.PI04.stable_closed_full_pair.v1'and export['completed']is True
    assert export['actual_owned_process_handle_exit_code']==0 and export['actual_owned_job_closed']is True and export['new_native_ticks']==0
    assert export['copied_full_pair']is False and not Path(export['source']).exists()
    for name in ('zero_tick_export_comparison','export_source_comparison'):
        assert export[name]['physical_equal']is True and export[name]['causal_prefix_equal']is True and export[name]['new_ticks']==0
    pair=Path(export['destination']);manifest=json.loads((pair/'EXPORTACION_SERVICIO.json').read_text(encoding='utf-8-sig'))
    descriptor={'stable_pair_relative_to_product':pair.relative_to(g['C']).as_posix(),'pair':{'manifest_sha256':export['manifest_sha256']},'desired_cut':{'N':67,'tick':export['tick']}}
    stable_path,stable_proof=check('real3990_member_stable_complete_pair',lambda:g['stable_pair'](descriptor))
    assert stable_proof['members_checked']==export['members']and stable_proof['member_bytes']==export['bytes']
    transport=export['paired_export_transport'];result=json.loads(transport['result'])
    assert transport['status']=='completed'and transport.get('error')is None and result['operation']=='exportar'
    assert result['before_tick']==result['after_tick']==export['tick']
    assert result['paired_export']['manifest_sha256']==export['manifest_sha256']
    # Current code-list guard admits exactly the real C2/C2B/C2C protocol names.
    code_items=[]
    for name in ('PROTOCOLO_PI04_C2_R01.json','PROTOCOLO_PI04_C2B_R01.json','PROTOCOLO_PI04_C2C_R01.json'):
        relative='capacidades/'+name;src=g['CS']/relative;target=g['S']/relative
        code_items.append({'file':relative,'sha256':sha(src),'product_before_sha256':sha(target)if target.exists()else None})
    accepted=check('actual_C2_C2B_C2C_protocol_whitelist',lambda:g['approved_code']({'approved_code_files':code_items}))
    assert len(accepted)==3
    wrong={'file':'capacidades/PROTOCOLO_PI04_R01.json','sha256':'0'*64,'product_before_sha256':None}
    check('invented_PI04_protocol_name_refused',lambda:g['approved_code']({'approved_code_files':[wrong]}),False)
    # The actual source card still needs Root's truthful provenance. Reading it
    # is not adding that history. Never fabricate the absent field for a test.
    card=g['read'](g['CS']/'estado/vidas'/g['LIFE']/'VIDA.json')
    provenance_present=bool(card.get('PI04_provenance'))
    parser_that_must_not_be_called=type('BlockedParser',(),{'snapshot_view':lambda self,p:(_ for _ in()).throw(AssertionError('Source gate unexpectedly entered parser'))})()
    source_descriptor={'desired_cut':{'N':card['physical']['N'],'tick':card['physical']['tick'],'snapshot_sha256':card['snapshot_sha256']}}
    if not provenance_present:
        check('actual_missing_source_provenance_blocks_before_parser',lambda:g['source_state'](source_descriptor,parser_that_must_not_be_called),False)
    # Exact maintained contract call signatures, never invocation.
    prepare_ast=new['prepare'];calls=[n for n in ast.walk(prepare_ast)if isinstance(n,ast.Call)]
    imports=[n for n in calls if isinstance(n.func,ast.Name)and n.func.id=='import_pair']
    assert len(imports)==1 and len(imports[0].args)==3 and not imports[0].keywords
    assert ast.unparse(imports[0])=='import_pair(store, localpair, LIFE)'
    assert any(isinstance(n.func,ast.Name)and n.func.id=='storage_gate'for n in calls)
    # Dry-run is informational only, no configuration approval or material call.
    saved_argv=sys.argv;capture=io.StringIO()
    try:
        sys.argv=[str(CODE),'--dry-run']
        with contextlib.redirect_stdout(capture):g['main']()
    finally:sys.argv=saved_argv
    dry=json.loads(capture.getvalue());assert dry['mode']=='READ_ONLY_NO_NATIVE_IMPORT_NO_WRITES'
    forbidden=[name for name in sys.modules if name=='app'or name.startswith(('app.','dee_thinking'))]
    assert not forbidden
    hashes_after={str(p):sha(p)for p in protected}
    if hashes_before!=hashes_after:raise ValueError('A protected product source changed concurrently; reconcile before material use')
    proof={'schema':'PI04.incorporation_adapter.static_verified.NOT_EXECUTED.R01','inspection_local':datetime.datetime.now().astimezone().isoformat(),
           'adapter':{'path':str(CODE.resolve()),'bytes':CODE.stat().st_size,'sha256':sha(CODE)},
           'original_draft_sha256':sha(CODE.parent/'incorporar_PI04_BORRADOR.py'),'changed_existing_functions':changes,
           'new_functions':[k for k in new if k not in old],'tests':tests,'count':len(tests),
           'real_stable_export_witness':{'path':str(export_path.resolve()),'sha256':sha(export_path),'schema':export['schema'],'completed':True,'actual_job_closed':True,'export_new_ticks':0},
           'actual_full_pair_validation':stable_proof,'actual_current_source_card':{'life_id':card['life_id'],'tick':card['physical']['tick'],'snapshot_sha256':card['snapshot_sha256'],'PI04_provenance_present':provenance_present},
           'contract_call':'import_pair(store, localpair, LIFE); Store(S).promote(LIFE, decision_path)',
           'catalog_and_continuity_current_pointer_updates_present':True,'historical_validated_lives_not_rewritten':True,
           'storage_budget_required':['limit_bytes','accounted_bytes_before','estimated_additional_bytes','evidence.path','evidence.sha256'],
           'protected_before_after_hashes':hashes_after,'dry_run':dry,'DEE_or_app_imports':forbidden,
           'new_Native_ticks':0,'adoption':False,'installation':False,'DECISION_file_created':False,
           'limitations':['Static checks and actual full-pair integrity are not Native import, operational reopening or adoption.','Source provenance must be supplied truthfully by Root after the last owner closes; this tool did not add it.','A fresh writer proof, current empirical gates, storage accounting, official interpreter and exact final decision remain required.','Root plans any post-adoption material use separately; this adapter makes no claim about its unexecuted future ticks.']}
    output.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'proof':str(output),'bytes':output.stat().st_size,'sha256':sha(output),'adapter':proof['adapter'],'tests':len(tests),'Native_ticks':0,'deployment':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
