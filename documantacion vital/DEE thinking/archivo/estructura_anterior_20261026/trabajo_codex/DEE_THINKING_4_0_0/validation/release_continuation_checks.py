"""Source/file-only continuation audit. It imports no DEE module and evolves nothing.

Numerical trajectories below validate declared free-transport geometry, not the
result of a material transition. Actual measurements remain separate evidence.
"""
from __future__ import annotations
import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import zipfile
from xml.etree import ElementTree

KERNEL='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def assigned(function,name):
    for node in ast.walk(function):
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets):return node.value
    raise ValueError('Missing frozen source assignment: '+name)

def planned_cases(tree):
    cases={}
    for node in ast.walk(tree):
        if not isinstance(node,ast.Dict):continue
        fields={k.value:v for k,v in zip(node.keys,node.values) if isinstance(k,ast.Constant) and isinstance(k.value,str)}
        if not all(isinstance(fields.get(k),ast.Constant) and isinstance(fields[k].value,str) for k in ('id','family')):continue
        identity=fields['id'].value;family=fields['family'].value
        if identity in cases:assert cases[identity]['family']==family, 'Conflicting frozen case ID'
        cases[identity]={'id':identity,'family':family,'evidence':'planned source configuration, not an executed trajectory'}
    return sorted(cases.values(),key=lambda x:x['id'])

def online_geometry(tree):
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='online_signal_case')
    n=ast.literal_eval(assigned(fn,'n'));inputs=ast.literal_eval(assigned(fn,'recipe_inputs'))
    points={}
    declared=assigned(fn,'declared')
    for k,v in zip(declared.keys,declared.values):points[ast.literal_eval(k)]=ast.literal_eval(v.args[0])
    probes=[]
    for row in assigned(fn,'probes').elts:
        probes.append({'port':ast.literal_eval(row.elts[0]),'source':ast.literal_eval(row.elts[1]),'tick':ast.literal_eval(row.elts[2])})
    assert n==47 and len(inputs)==3 and len(probes)==2
    def move(point,direction,ticks):return [(x+d*ticks)%n for x,d in zip(point,direction)]
    def sign(x):return (x>0)-(x<0)
    def direction(*directions):return [sign(sum(v)) for v in zip(*directions)]
    contact_a=move(inputs[0][0],inputs[0][2],5);contact_b=move(inputs[1][0],inputs[1][2],5)
    contact_direction=direction(inputs[0][2],inputs[1][2])
    contact_at8=move(contact_a,contact_direction,3);cue_at8=move(inputs[2][0],inputs[2][2],8)
    acquired_direction=direction(contact_direction,inputs[2][2])
    relation_at16=move(contact_at8,acquired_direction,8);query1_at16=move(probes[0]['source'],[-1,0,0],16-probes[0]['tick'])
    post_query_direction=direction(acquired_direction,[-1,0,0])
    relation_at21=move(relation_at16,post_query_direction,5);query2_at21=move(probes[1]['source'],[-1,0,0],21-probes[1]['tick'])
    checks={'contact_declared_at5':contact_a==contact_b==points['environment_contact'],
            'cue_and_contact_trajectory_meet_at8':contact_at8==cue_at8==points['acquisition_encounter'],
            'probe1_declared_intersection16':relation_at16==query1_at16==points['common_response_1'],
            'probe2_declared_intersection21':relation_at21==query2_at21==points['common_response_2'],
            'two_distinct_probe_ports':probes[0]['port']!=probes[1]['port'],
            'initial_sites_distinct':len({tuple(row[0]) for row in inputs})==len(inputs),
            'all_initial_loads_uint16':all(0<=row[1]<=65535 for row in inputs)}
    calls=[node for node in ast.walk(fn) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute)]
    request=assigned(fn,'requests');advance_lines=[node.lineno for node in calls if node.func.attr=='advance']
    forbidden=[{'method':node.func.attr,'line':node.lineno} for node in calls if node.func.attr in ('set_raw','set_clock','import_research_state','diagnostic_fork')]
    checks['requests_syntactically_declared_before_advance']=request.lineno<min(advance_lines)
    checks['no_direct_edit_helpers_in_online_function']=not forbidden
    assert all(checks.values()), checks
    translated={name:[(x+s)%n for x,s in zip(point,[2,3,1])] for name,point in points.items()}
    return {'scope':'INSTRUMENT_GEOMETRY_ONLY_NO_NATIVE_EXECUTION_OR_MATERIAL_OUTPUT_PREDICTION',
            'checks':checks,'dimension':n,'basic_four_buffers_bytes':32*n**3,
            'declared_points':points,'reserved_translation_points':translated,'probes':probes,
            'branch_effects_not_computed':['survival','protection','reducer','DEMUX','new active records','retained function'],
            'snapshot_T16_boundary':'pre-application of request at16; Runtime applies it before transition16->17',
            'forbidden_edit_helpers':forbidden}

def cpp_identity(root,build_source):
    rows=[]
    if not build_source or not build_source.is_dir():return {'status':'BUILD_SOURCE_NOT_AVAILABLE','files':[],'reuse_not_proven_by_this_check':True}
    for folder,pattern in [('include','*.hpp'),('src','*.cpp'),('bindings','*.cpp')]:
        for path in sorted((root/'source'/folder).rglob(pattern)):
            relative=path.relative_to(root/'source');original=build_source/relative
            rows.append({'path':relative.as_posix(),'delivered_sha256':sha(path),
                         'compiled_source_sha256':sha(original) if original.is_file() else None,
                         'identical':original.is_file() and sha(path)==sha(original)})
    assert rows and all(x['identical'] for x in rows), 'C++ source no longer matches the measured compiled input'
    header=(root/'source/include/dee_thinking/cognitive.hpp').read_text(encoding='utf-8-sig')
    cpp=(root/'source/src/cognitive.cpp').read_text(encoding='utf-8-sig')
    ownership={'public_move_declared':'CognitiveSession(CognitiveSession&&) noexcept = default' in header,
               'explicit_deep_world_fork':'child.world_=world_.fork()' in cpp,
               'ordinary_copy_private':'private:\n    // A plain C++ copy' in header,
               'native_association_deep_fork':'NativeAssociationSession child(world_.fork())' in cpp}
    assert all(ownership.values()), ownership
    return {'status':'CPP_HEADERS_BINDINGS_IDENTICAL_TO_COMPILED_INPUT','files':rows,'ownership_source_checks':ownership,
            'scope':'source identity supports reuse; it does not replace binary/install checks'}

def cpp_tests(root):
    result={};reports=[]
    for name in ('ctest.xml','ctest_timeout_retry.xml'):
        path=root/'validation'/name
        if not path.exists():continue
        reports.append({'path':'validation/'+name,'sha256':sha(path)})
        for case in ElementTree.parse(path).getroot().iter('testcase'):
            key=case.get('name');failed=bool(case.findall('failure') or case.findall('error') or case.findall('skipped'))
            result[key]={'name':key,'technical_pass':not failed,'source_report':name,'time':case.get('time')}
    return {'reports':reports,'distinct_final_tests':len(result),'final_pass_count':sum(x['technical_pass'] for x in result.values()),
            'cases':list(result.values()),'scope':'later unchanged-source retry replaces its matching earlier timeout, not additional independent tests'}

def wheel_identity(root,wheel):
    if not wheel or not wheel.is_file():return {'status':'WHEEL_NOT_AVAILABLE'}
    mismatches=[];rows=[];native=[]
    with zipfile.ZipFile(wheel) as archive:
        assert archive.testzip() is None
        for name in archive.namelist():
            if name.endswith('.pyd'):native.append({'path':name,'sha256':hashlib.sha256(archive.read(name)).hexdigest()})
            if not name.startswith('dee_thinking/') or not name.endswith(('.py','.pyi')):continue
            relative=Path(name).relative_to('dee_thinking');path=root/'source/python/dee_thinking'/relative
            digest=hashlib.sha256(archive.read(name)).hexdigest();same=path.is_file() and sha(path)==digest
            row={'member':name,'wheel_sha256':digest,'source_sha256':sha(path) if path.exists() else None,'equal':same};rows.append(row)
            if not same:mismatches.append(row)
    source_package=root/'source/python/dee_thinking'
    represented={row['member'] for row in rows}
    source_extras=['dee_thinking/'+path.relative_to(source_package).as_posix() for path in source_package.rglob('*')
                   if path.is_file() and path.suffix in ('.py','.pyi') and '__pycache__' not in path.parts
                   and 'dee_thinking/'+path.relative_to(source_package).as_posix() not in represented]
    prior=root/'validation/cognitive_parity_01/native/RESULTS.json'
    prior_hash=load(prior).get('native_binary_sha256') if prior.is_file() else None
    return {'wheel':str(wheel),'sha256':sha(wheel),'python_source_matches_wheel':not mismatches and not source_extras,
            'source_wheel_differences':mismatches,'python_members_checked':rows,'native_members':native,
            'source_code_members_absent_from_wheel':source_extras,
            'native_binary_identical_to_cognitive_parity_candidate':len(native)==1 and native[0]['sha256']==prior_hash,
            'scope':'artifact/source bytes only; no installation, import or evolution performed'}

def measured_inventory(root,cases):
    required={'movement':['T0.deetsnap','MAIN_FINAL.deetsnap'],
              'contact':['T0.deetsnap','T5.deetsnap','T6.deetsnap','FINAL.deetsnap'],
              'online_signal':['T0_PENDING_PROBES.deetsnap','STATE_T5.deetsnap','STATE_T8.deetsnap','ACQUIRED_PENDING_T9.deetsnap','STATE_T16.deetsnap','STATE_T21.deetsnap','MAIN_FINAL.deetsnap'],
              'acquired':['T0.deetsnap','ACQUIRED_T6.deetsnap','SEQUENCE_T11.deetsnap','MAIN_FINAL.deetsnap'],
              'composition':['T0.deetsnap','ACQUIRED_T6.deetsnap','MAIN_FINAL.deetsnap'],
              'observer_cut':['DIAGNOSTIC_CUT_FINAL.deetsnap','DIAGNOSTIC_INTACT_FINAL.deetsnap'],
              'dialogue':['DIALOGOS.jsonl','antes_pregunta_nueva.deetsnap','MAIN_FINAL.deetsnap']}
    rows=[]
    for case in cases:
        folder=root/'experiments/BLOCK_II'/case['id'];measurement=folder/'MEASUREMENTS.json'
        row={**case,'measurement_present':measurement.is_file(),'checkpoints_to_preserve_when_executed':required[case['family']]}
        if measurement.is_file():
            data=load(measurement);row['measurement_sha256']=sha(measurement);row['measurement_status']=data.get('status','DATA_PRESENT_WITHOUT_GLOBAL_VERDICT')
            row['missing_expected_evidence']=[name for name in required[case['family']] if not (folder/name).is_file()]
            row['qualified_wheel_sha256']=data.get('product',{}).get('wheel_sha256')
        rows.append(row)
    return {'planned_cases':len(cases),'measurement_records_present':sum(x['measurement_present'] for x in rows),
            'by_family':dict(Counter(x['family'] for x in cases)),'records':rows,
            'scope':'file inventory only; blocked/inconclusive records remain valid evidence and are not native capability passes'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--build-source',type=Path);p.add_argument('--wheel',type=Path);p.add_argument('--require-wheel-sync',action='store_true')
    p.add_argument('--expected-case-count',type=int,help='Optional explicit frozen-count assertion; otherwise report the actual distinct source IDs')
    a=p.parse_args()
    root=a.root.resolve();source=root/'experiments/run_block_ii.py';tree=ast.parse(source.read_text(encoding='utf-8-sig'))
    cases=planned_cases(tree)
    if a.expected_case_count is not None:assert len(cases)==a.expected_case_count,(len(cases),cases)
    build_source=a.build_source
    if build_source is None and (root/'BUILD_PATHS.json').exists():build_source=Path(load(root/'BUILD_PATHS.json')['source'])
    wheel=a.wheel or root/'wheel/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
    result={'scope':'SOURCE_AND_FILE_ONLY_NOT_RELEASE_QUALIFICATION','native_evolution_executed':False,
            'kernel_source_sha256':sha(root/'source/src/kernel_v27.cpp'),'runner_sha256':sha(source),
            'cpp_identity':cpp_identity(root,build_source),'historical_cpp_reports':cpp_tests(root),
            'online_geometry':online_geometry(tree),'wheel_source':wheel_identity(root,wheel),
            'block_II_evidence_to_preserve':measured_inventory(root,cases)}
    assert result['kernel_source_sha256']==KERNEL
    if a.require_wheel_sync:assert result['wheel_source'].get('python_source_matches_wheel') is True, 'New Python fixes not synchronized into wheel'
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'scope':result['scope'],'native_jobs':0,'planned_cases':len(cases),
                      'source_cpp_identical':result['cpp_identity']['status'],
                      'python_wheel_equal':result['wheel_source'].get('python_source_matches_wheel'),
                      'historical_cpp_final_pass_count':result['historical_cpp_reports']['final_pass_count']}))

if __name__=='__main__':main()
