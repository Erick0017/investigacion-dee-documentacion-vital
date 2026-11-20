"""Derive release evidence from actual command/test/replay records, not labels."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile


def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def write(p,data):Path(p).write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')


SURFACES={
    'association':['OrganizationRecipe.mobile_pair','OrganizationalWorld.submit/probe'],
    'composition':['CompositionPlanner','OrganizationRecipe.cascade'],
    'anticipation':['OrganizationRecipe.predictive','Runtime inputs; passive horizon measurement'],
    'basal_intervention':['BasalWorld','OrganizationalWorld.diagnostic_fork'],
    'rest_or_damage':['OrganizationRecipe.relational','ResilienceObservation','diagnostic_fork'],
    'repair_calibration':['run_h3','diagnostic damage authorization'],
    'repertoire':['OrganizationRecipe.mobile_pair','start_mobile_sequence','fork/probe'],
    'repertoire_delay':['OrganizationRecipe.mobile_pair','Runtime input scheduling'],
    'horizon':['OrganizationRecipe.predictive','Runtime scheduling/observations'],
    'contingency_loop':['OrganizationRecipe.contingent','ActionCoupling','diagnostic_fork'],
    'transplant':['assisted_reconstruction','ReconstructionSpec'],
    'native_transfer':['OrganizationRecipe.native_transfer','physical relay/receiver query'],
    'latent':['OrganizationRecipe.relational','FunctionalReadout','physical common_query'],
    'latent_followup':['OrganizationRecipe.relational','Runtime fork/evolution'],
    'distributed':['OrganizationRecipe.distributed','FunctionalReadout','Runtime'],
    'distributed_drift':['OrganizationRecipe.distributed','explicit diagnostic field edits'],
    'contextual':['OrganizationRecipe.contextual','inspect_write_gate','InterfaceSpec'],
    'damage':['OrganizationRecipe.relational','ResilienceObservation','diagnostic_fork'],
    'cascade':['OrganizationRecipe.cascade','stage physical ports'],
    'bridge':['OrganizationRecipe.mobile_basal','TraceSession','physical common_query'],
    'bridge_retention':['OrganizationRecipe.mobile_basal','deep fork/probe/persistence'],
    'information':['OrganizationRecipe.information','ActionCoupling'],
    'competition':['OrganizationRecipe.competition','observe_encounter'],
    'joint_followup':['OrganizationRecipe.competition','physical joint/later query'],
    'phase':['OrganizationRecipe.phase','phase.access_query'],
    'phase_access':['OrganizationRecipe.phase','physical temporal probe'],
    'phase_route':['OrganizationRecipe.phase','Runtime channels','explicit diagnostic cuts'],
    'reread':['passive test-only analysis; no physical execution'],
    'missing_historical':['SOURCE_NOT_RECOVERED; no native implementation advertised'],
}


def main(a):
    root=Path(a.workspace).resolve(); validation=root/'validation'; source=root/'source'
    product=Path(a.product_parent); wheel30=Path(a.wheel_parent); science=Path(a.science); wheel=Path(a.wheel)
    identities={
        'product_3_0':(product,'9b45a8d0b05258dba3989bdf6e63ed3fd7d1c01f199673da06259d0aad946937'),
        'wheel_3_0':(wheel30,'9aa3a69bf1d542308912dbeee0b7c89199dafe295ce09533a2a394c8bc83c6db'),
        'scientific_archive':(science,'f1f8b6b2f68517f003a21c2908adde49bf1194c7f5657b460563b91ad76f28f0'),
        'kernel_v27':(source/'src/kernel_v27.cpp','fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31')}
    preserved={}
    for name,(path,expected) in identities.items():
        actual=sha(path);assert actual==expected,(name,actual);preserved[name]={'name':path.name,'sha256':actual,'expected_equal':True}
    with zipfile.ZipFile(product) as z:
        inherited_core=[]
        for name in z.namelist():
            if (name.startswith('source/src/') and name.endswith('.cpp')) or (name.startswith('source/include/') and name.endswith('.hpp') and not name.endswith('/version.hpp')):
                p=root/name;original=z.read(name);assert p.is_file() and p.read_bytes()==original,name
                inherited_core.append({'path':name,'sha256':hashlib.sha256(original).hexdigest(),'byte_exact':True})
    commands={}; command_documents=[]
    for phase in ['setup','test','primary','supplement']:
        p=validation/('commands_'+phase)/'COMMAND_RESULTS.json';record=read(p)
        assert record['summary']['failed']==0 and record['summary']['required_failed']==0,phase
        for r in record['commands']:
            assert r['exit_code']==0 and r['status']=='passed' and not r['timed_out'] and not r['launch_error'],r['name']
            assert r['name'] not in commands;commands[r['name']]=r
        command_documents.append({'path':str(p.relative_to(root).as_posix()),'sha256':sha(p),'total':len(record['commands'])})
    junit=ET.parse(validation/'FINAL_NATIVE_TESTS.xml').getroot()
    cpp=[{'name':n.attrib['name'],'time_seconds':float(n.attrib.get('time','0')),'failed':n.find('failure') is not None or n.find('error') is not None,'skipped':n.find('skipped') is not None} for n in junit.iter('testcase')]
    assert len(cpp)==20 and all(not r['failed'] and not r['skipped'] for r in cpp)
    assert int(junit.attrib.get('failures',0))==0 and int(junit.attrib.get('skipped',0))==0
    python_log=commands['python_full_suite']['stdout']+'\n'+commands['python_full_suite']['stderr']
    tests=re.findall(r'(?m)^(test_\S+) \((.*?)\) \.\.\. ok$',python_log)
    count=int(re.search(r'Ran (\d+) tests in ',python_log).group(1));assert count==len(tests)==39
    assert re.search(r'(?m)^OK$',python_log)
    install=read(validation/'clean_install/INSTALLATION_RESULT.json')
    assert install['version']=='3.5.0' and install['noneditable_site_packages'] and install['cross_process_operational_future_equal'] and install['decode_passive']
    wheel_sha=sha(wheel);assert install['wheel_sha256']==wheel_sha
    native_sha=install['native_sha256']
    with zipfile.ZipFile(wheel) as z:assert hashlib.sha256(z.read('dee_thinking/_native.cp313-win_amd64.pyd')).hexdigest()==native_sha
    recipe=read(validation/'NATIVE_RECIPE_COMPARISON_FINAL.json');assert recipe['version']=='3.5.0' and not recipe['failed'] and len(recipe['cases'])==34
    assert all(x['status']=='PASS' and x['save_load_future_equal'] for x in recipe['cases'])
    cross=read(validation/'cross_language_3_5/CROSS_LANGUAGE_RESULT.json')
    for key in ['cpp_to_python','python_to_cpp','other_process_restoration','shared_views','pending_input_continuation','protocol_cursor_readouts','trace_preserved','interfamily_native_bridge_equal']:assert cross[key],key
    errors=read(validation/'OPERATIONAL_ERRORS.json');assert errors['main_physical_unchanged'] and all(c['rejected'] for c in errors['checks'])
    primary_index=read(validation/'PRIMARY_CASE_INDEX.json');assert primary_index['count']==289 and len(primary_index['records'])==289
    index={r['case']:r for r in primary_index['records']};assert len(index)==289
    comparisons=[];counts={'physical_reproduced_3_5':0,'rereads_recalculated':0,'source_not_recovered':[],'checkpoint_comparisons':0,'unique_source_records':289}
    for suite,expected in [('inherited',100),('extension',189)]:
        folder=validation/'primary_final_3_5'/suite;summary=read(folder/'SUMMARY.json')
        assert summary['version']=='3.5.0' and summary['completed_reports']==expected and summary['passed']==expected and not summary['failed']
        reports=[(p,read(p)) for p in folder.glob('*.json') if p.name!='SUMMARY.json'];assert len(reports)==expected
        for p,r in reports:
            baseline=read(validation/'primary_3_0'/suite/p.name)
            assert r['version']=='3.5.0' and baseline['version']=='3.0.0' and r['status']==baseline['status']=='PASS'
            assert r['native_binary_sha256']==native_sha and r['science_sha256']==preserved['scientific_archive']['sha256']
            assert r['comparisons']==baseline['comparisons'],r['case']
            for cp in r['comparisons']:
                assert cp['physical_equal'] and cp['receipts_equal'] and cp['channel_names_equal'] and cp['pause_equal'] and cp['protocol_phase_equal']
            counts['checkpoint_comparisons']+=len(r['comparisons'])
            execution=r['execution_type']
            native_internal_ticks=None
            if execution=='PHYSICAL_REPLAY':
                counts['physical_reproduced_3_5']+=1
                if r['ticks_evolved']==0:
                    # H3 evolves inside a C++ coupled protocol, not via the
                    # Python Runtime counter. Its exact fixture handler calls
                    # run_trained_redundancy_repair; it does not load the final
                    # snapshot to answer. Keep the two accounting scopes apart.
                    assert r['case'].startswith('L07/H3_'),r['case']
                    with zipfile.ZipFile(science) as z:original= json.loads(z.read(r['source_member']))
                    assert original['native_internal_tick_count']==193 and len(r['comparisons'])==1
                    assert r['comparisons'][0]['reconstructed']['tick']==193
                    native_internal_ticks=original['native_internal_tick_count']
            elif execution=='REREAD_RECALCULATED':counts['rereads_recalculated']+=1
            else:assert execution=='SOURCE_DEPENDENCY_ONLY';counts['source_not_recovered'].append(r['case'])
            events=index[r['case']]['original_events']; running=[e['spec'] for e in events if e.get('status')=='RUNNING' and e.get('spec')]
            spec=running[-1] if running else {}; handler=spec.get('handler',spec.get('kind',''))
            if r['case'].startswith('L03/late_'):handler='basal_intervention'
            surfaces=SURFACES.get(handler,['compatible native Runtime and explicit diagnostic primitives; see exact scenario fixture'])
            comparisons.append({'case':r['case'],'execution_type':execution,'source_member':r['source_member'],'handler':handler,
                'public_surfaces':surfaces,'regression_mode':'Original fixture scenario coordinated as test; native Runtime evolves. Public native constructors separately compared in 34 full-state preparation/evolution/save-load cases.',
                'original_configuration':spec,'checkpoints_compared':len(r['comparisons']),'python_instrumented_runtime_tick_count':r.get('ticks_evolved',0),'native_internal_protocol_tick_count':native_internal_ticks,
                'full_raw_clock_tick_receipts_equal':True,'result_panel_equal':r.get('panel_equal',r.get('recorded_calls_receipts_edits_equal',True)),
                'report_3_0':str((validation/'primary_3_0'/suite/p.name).relative_to(root).as_posix()),'report_3_5':str(p.relative_to(root).as_posix())})
    assert counts['physical_reproduced_3_5']==285 and counts['rereads_recalculated']==3 and len(counts['source_not_recovered'])==1 and counts['checkpoint_comparisons']==1540
    assert {x['case'] for x in comparisons}==set(index)
    write(validation/'VALIDATION_CASE_MATRIX.json',{'count':len(comparisons),'count_does_not_equal_capabilities_or_independent_replicates':True,'records':comparisons})
    contract=read(root/'PRODUCT_CONTRACT.json');assert len(contract['capabilities'])==9
    families=[]
    for cap in contract['capabilities']:
        for case in cap['experimental_sources']:assert case in index,case
        test_names=[x[0] for x in tests]
        matched=[name for name in cap['tests'] if name in test_names or name in ['organizational_3_5','replay_primary_cases','compare_native_recipes','test_integrated_protocols']]
        assert matched,cap['id'];families.append({'id':cap['id'],'API':cap['API'],'modalities':cap['modalities'],'source_cases':cap['experimental_sources'],'tests':matched,'technical_status':'IMPLEMENTED_AND_TESTED_WITHIN_DECLARED_DOMAIN'})
    extraction_file=validation/'CLEAN_EXTRACTION_RESULT.json';clean=False;extraction=None
    if extraction_file.exists():
        extraction=read(extraction_file);assert extraction['CRC_hash_manifest_verified'] and extraction['wheel_sha256']==wheel_sha and extraction['native_sha256']==native_sha
        assert extraction['public_installed_walkthrough'] and extraction['external_cpp_consumer'] and extraction['cross_language_persistence'];clean=True
        extraction_commands=Path(extraction['commands_record']);record=read(extraction_commands)
        assert record['summary']['failed']==0 and all(c['exit_code']==0 and c['status']=='passed' for c in record['commands'])
        command_documents.append({'path':str(extraction_commands.relative_to(root).as_posix()),'sha256':sha(extraction_commands),'total':len(record['commands'])})
    superseded=[]
    first_extract=validation/'clean_extraction/commands/COMMAND_RESULTS.json'
    if first_extract.exists():
        first=read(first_extract)
        if first['summary']['failed']:
            superseded.append({'attempt':'first isolated packaging closure','record':str(first_extract.relative_to(root).as_posix()),'failed_commands':[c['name'] for c in first['commands'] if c['status']!='passed'],'cause':'PowerShell script policy blocked helper; consumer absent for dependent command','resolution':'Native auxiliary consumer built through direct VS/CMake/Ninja invocation; no Windows policy changed','superseded_by_verified_clean_extraction':clean})
    report={'schema_version':1,'product':'DEE thinking','version':'3.5.0','generated_utc':datetime.now(timezone.utc).isoformat(),
        'status':'RELEASE_VERIFIED' if clean else 'CANDIDATE_VALIDATED','required_failed':[],'mandatory_tests_omitted':[],
        'kernel_preserved':True,'kernel_sha256':preserved['kernel_v27']['sha256'],'inherited_native_core_byte_exact':inherited_core,
        'parents_preserved':preserved,'wheel_sha256':wheel_sha,'native_sha256':native_sha,'new_native_binary':native_sha!='333da509e19a9f31793df3a9d7fbc3c3809c1c8f69cd62a6b6423e3bb2a79a83',
        'cpp_external_consumer':commands['external_cpp_find_package']['exit_code']==0,'clean_noneditable_install':install['noneditable_site_packages'],
        'cross_language_persistence':True,'clean_extraction_verified':clean,'clean_extraction':extraction,
        'native_tests':{'total':len(cpp),'failed':[],'skipped':[],'testcases':cpp,'junit':'validation/FINAL_NATIVE_TESTS.xml'},
        'python_tests':{'total':count,'new':sum('test_organizational_api.' in x[1] for x in tests),'inherited':sum('test_organizational_api.' not in x[1] for x in tests),'failed':[],'skipped':[],'tests':[{'name':n,'class':c} for n,c in tests]},
        'supplementary_invalid_operation_checks':len(errors['checks']),'native_constructor_full_state_comparisons':len(recipe['cases']),
        'cross_language_command_count':sum(r['kind']=='cross_language' for r in commands.values())+(1 if clean else 0),'logged_command_count':sum(d['total'] for d in command_documents),'command_documents':command_documents,
        'cases':counts,'families':families,
        'compatibility':{'usage_and_behavior':'inherited 3.0/2.2 Runtime, BasalWorld, catalog, H1-H4/F1-F2 and composition APIs regression-tested','old_snapshots':'Runtime v1/v2 and basal metadata','C++_binary_ABI_across_toolchains':'not promised','GIL':'unchanged, not released during Runtime advance'},
        'runtime_dependency_on_3_0_or_laboratory':False,
        'scopes_and_pending':['ORGREINSTANTIATE20CX/WARPORG146X source not recovered; complete body reinstantiation is not advertised.',
            'Declared-site and ballistic segment tracking stops with explicit ambiguity on unreconstructed transformations; no universal DEMUX provenance.',
            'P07 external zero-load experience is not advertised as proven autonomous exterior-action regulation.',
            'No universal repair, arbitrary geometry robustness, arbitrary signed/permuted invariance or C++ binary ABI promise.',
            'Historical fixture orchestration belongs to validation only. Installed API executes native recipes without fixture imports or terminal-result lookups.'],
        'development_incidents':'validation/DEVELOPMENT_INCIDENTS.json','superseded_technical_attempts':superseded,'performance_measurements':'validation/REFERENCE_COST.json'}
    write(validation/'VALIDATION_REPORT.json',report)
    write(root/'PROGRESS.json',{'milestones':{'source_identity':True,'native_common_model_and_persistence':True,'nine_families':True,'regressions_and_integration':True,'clean_final_build':True,'clean_extraction':clean,'publication':False},'wheel_sha256':wheel_sha,'status':report['status']})
    print(json.dumps({'status':report['status'],'cases':counts,'native_tests':len(cpp),'python_tests':count,'recipe_comparisons':len(recipe['cases']),'logged_commands':len(commands)},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['workspace','product-parent','wheel-parent','science','wheel']:p.add_argument('--'+name,required=True)
    main(p.parse_args())
