"""Read-only CPC3 evidence index. Writes only resultados/CASE_COVERAGE.json.

No native import, experiment execution, relabelled timepoint replication or
changes to primary evidence. Re-run after the final measured selection case.
"""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import argparse,hashlib,json,os


def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);a=ap.parse_args()
    root=Path(a.root).resolve();entries=[];alternatives=[];missing=[]
    def rel(p):return Path(p).resolve().relative_to(root).as_posix()
    def descriptor(p,selector=None):
        p=Path(p);v={'path':rel(p),'exists':p.is_file()}
        if selector is not None:v['json_selector']=selector
        if p.is_file():v.update(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
        return v
    def snaps(folder):return [rel(p) for p in sorted(Path(folder).glob('*.deetsnap'))]
    def add(local,area,kind,evidence,*,configuration=None,selector=None,checkpoint_folder=None,
            configuration_inline=None,fresh_preparation=False,purpose='SCIENTIFIC_CONTRAST',
            parent=None,notes=None):
        ident=area+'/'+local
        row={'id':ident,'local_id':local,'area':area,'trajectory_type':kind,
             'purpose':purpose,'evidence':descriptor(evidence,selector),
             'configuration':descriptor(configuration) if configuration else None,
             'configuration_inline':configuration_inline,
             'checkpoints':snaps(checkpoint_folder) if checkpoint_folder else [],
             'fresh_world_preparation_executed':fresh_preparation,
             'parent_reference':parent,'notes':notes or [],
             'timepoints_are_not_replicates':True,
             'independent_statistical_replication_claimed':False}
        entries.append(row);return row
    base=root/'experimentos/comparacion_seleccion'
    groups=[('DIRECTIONAL_COMPARISON','resultados'),('FINITE_SELECTION_COMPONENT','seleccion'),
            ('OFFAXIS_NATIVE_DISCOVERY','native_discovery'),('OFFAXIS_NATIVE_CONFIRMATION','native_confirmation'),
            ('OFFAXIS_LATE_DIAGNOSTICS','late_controls'),('INFORMATION_REUSE','post_information'),
            ('CENTRAL_DISCOVERY','central_discovery'),('CENTRAL_CONFIRMATION','central_confirmation'),
            ('CENTRAL_FOLLOWUP','central_followup')]
    for group,directory in groups:
        folder=base/directory;cfg=(base if directory=='resultados' else folder)/'EXPERIMENT_CONFIG.json'
        for file in sorted(folder.glob('*/MEASUREMENTS.json')):
            case=file.parent.name;x=read(file);kind='FRESH_PROTOCOL'
            parent=None;fresh=True
            if directory=='late_controls' or (directory=='post_information' and case in ('late_information_remove','identical_copy_sham')):
                kind='DIAGNOSTIC_FORK';fresh=False
                parent='comparacion_seleccion/native_discovery/AB_changed' if directory=='late_controls' else 'comparacion_seleccion/post_information/AB/T56'
            elif directory=='central_followup':
                kind='RESTORED_SCIENTIFIC_CONTINUATION' if '_changed_' in case else 'DIAGNOSTIC_FORK'
                fresh=False;parent='comparacion_seleccion/central_discovery/'+('closed_changed' if case.startswith('closed') else 'open_changed')+'/BEFORE_REPORT'
            add(group+'/'+case,'comparacion_seleccion',kind,file,configuration=cfg,
                checkpoint_folder=file.parent,fresh_preparation=fresh,parent=parent,
                configuration_inline=x.get('case',x.get('configuration',x.get('metadata'))))
    continuity=root/'experimentos/continuidad';cfg=continuity/'EXPERIMENT_CONFIG.json'
    if cfg.is_file():
        for case in read(cfg)['cases']:
            file=continuity/'casos'/(case['id']+'.json')
            if not file.is_file():missing.append({'area':'continuidad','id':case['id'],'reason':'CONFIGURED_WITHOUT_PRIMARY_RESULT'});continue
            x=read(file);diag=x.get('mode')=='DIAGNOSTIC_FORK'
            add(case['id'],'continuidad','DIAGNOSTIC_FORK' if diag else 'FRESH_PROTOCOL',file,
                configuration=cfg,configuration_inline=case,checkpoint_folder=root/'checkpoints/continuidad'/case['id'],
                fresh_preparation=True,purpose='MAIN_CONTINUITY' if not diag else 'CAUSAL_HISTORY_CONTROL',
                parent='checkpoints/continuidad/'+case['id']+'/FIRST_READ.deetsnap' if diag else None,
                notes=['This case prepares fresh, then evaluates a diagnostic fork; counted once as a fork target, not as two individuals.'] if diag else [])
    language=root/'experimentos/comunicacion';cfg=language/'EXPERIMENT_CONFIG.json'
    if cfg.is_file():
        for case in read(cfg)['cases']:
            file=language/'casos'/case['id']/'MEASUREMENTS.json'
            if not file.is_file():missing.append({'area':'comunicacion_asociaciones','id':case['id'],'reason':'CONFIGURED_WITHOUT_PRIMARY_RESULT'});continue
            x=read(file)
            if x.get('status')=='TECHNICAL_ERROR':missing.append({'area':'comunicacion_asociaciones','id':case['id'],'reason':'PRIMARY_TECHNICAL_ERROR','evidence':descriptor(file)});continue
            row=add(case['id'],'comunicacion_asociaciones','FRESH_PROTOCOL',file,
                    configuration=cfg,configuration_inline=case,checkpoint_folder=file.parent,
                    fresh_preparation=True,purpose='INTERFACE_EQUIVALENCE' if case['id']=='association_alias_forms' else 'ASSOCIATION_OR_COMPOSITION')
            if case['id']=='association_alias_forms':
                reference=read(language/'casos/association_forward/MEASUREMENTS.json')
                row['physically_equivalent_reference']='comunicacion_asociaciones/association_forward'
                row['same_response_RAW_clock_digest']=x['response']['physical']==reference['response']['physical']
                row['notes'].append('Real fresh preparation with different external label aliases; no extra acquired association or independent physical mechanism is inferred.')
    # Finite R14 investigation is indexed only when actual primary files exist.
    revisable=root/'experimentos/seleccion_revisable';cfg=revisable/'EXPERIMENT_CONFIG.json'
    config_cases={x['id']:x for x in read(cfg).get('cases',[])} if cfg.is_file() else {}
    measured=set()
    for file in sorted((revisable/'casos').glob('*/MEASUREMENTS.json')):
        x=read(file);case=file.parent.name;measured.add(case)
        if x.get('status')=='TECHNICAL_ERROR':
            missing.append({'area':'seleccion_revisable','id':case,'reason':'PRIMARY_TECHNICAL_ERROR','evidence':descriptor(file)});continue
        diagnostic=bool(x.get('diagnostic_forks'))
        add(case,'seleccion_revisable','DIAGNOSTIC_FORK' if diagnostic else 'FRESH_PROTOCOL',file,configuration=cfg if cfg.is_file() else None,
            configuration_inline=x.get('configuration',config_cases.get(case)),checkpoint_folder=file.parent,
            fresh_preparation=True,purpose='R14_BOUNDED_SELECTION_INVESTIGATION',
            parent=rel(file.parent/'FIRST_ACTION_T1.deetsnap') if diagnostic else None,
            notes=['Fresh prefix, followed by one late diagnostic action cut. It is one fork target, not a second independent native individual.'] if diagnostic else [])
    for case in sorted(set(config_cases)-measured):missing.append({'area':'seleccion_revisable','id':case,'reason':'CONFIGURED_NOT_YET_MEASURED'})
    # Reader/absorber discovery is separate from the frozen scientific panel.
    aggregate_files=[('DISCOVERY_READER.json','src/core/discovery_reader.py'),
                     ('DISCOVERY_OFFAXIS.json','src/core/discovery_offaxis.py'),
                     ('DISCOVERY_ZERO_READER.json','src/core/discovery_zero_reader.py'),
                     ('OFFAXIS_SELECTIVE.json','src/core/offaxis_selective.py'),
                     ('ABSORBER_SELECTIVE.json','src/core/absorber_selective.py')]
    for name,runner in aggregate_files:
        file=continuity/name
        if not file.is_file():continue
        for j,x in enumerate(read(file)):
            parameters={k:v for k,v in x.items() if k in ('offset','keep_reader','extra','persistent','payload','history','new_event','new_inlet')}
            alternatives.append({'id':'reader_discovery/'+name[:-5]+'/'+str(j),'trajectory_type':'DISCOVERY_PREPARATION',
                'evidence':descriptor(file,'/'+str(j)),'configuration_inline':parameters,'recipe_source':runner,
                'checkpoints':[],'status':'TECHNICAL_ERROR' if x.get('error') else 'MEASURED',
                'excluded_from_frozen_scientific_totals':True,'timepoints_are_not_replicates':True})
    for file in sorted((continuity/'absorber').glob('*.json')):
        x=read(file);alternatives.append({'id':'reader_discovery/absorber/'+file.stem,
            'trajectory_type':'DISCOVERY_PREPARATION','evidence':descriptor(file),
            'configuration_inline':{k:x[k] for k in ('id','offsets','payload') if k in x},
            'recipe_source':'src/core/discovery_absorber.py','checkpoints':[],
            'status':'MEASURED','excluded_from_frozen_scientific_totals':True,'timepoints_are_not_replicates':True})
    # Do not relabel API suites, transcript replays, clean-install checks or
    # read-only analyses as additional scientific individuals.
    technical=[]
    proof_paths=[continuity/'TECHNICAL_CHECKS.json',continuity/'comparison_profile/VALIDATION.json',
                 continuity/'CAUSAL_GATE.json',language/'tecnica/TECHNICAL_CHECKS.json',
                 base/'technical/TECHNICAL_CHECKS.json',base/'post_information/CONTINUITY.json',
                 base/'OPEN_POLICY_RETROSPECTIVE.json',revisable/'R14_REVALIDATION.json',
                 root/'resultados/INFORMATION_FLOW_CHECK.json',root/'resultados/CLEAN_REPRODUCTION.json',
                 root/'resultados/referencia_heredada/REFERENCE_CHECK.json']
    proof_paths += sorted(language.glob('interfaz*/GRAMMAR_TESTS.json'))
    proof_paths += sorted((root/'resultados/CLEAN_REPRODUCTION_EVIDENCE').glob('*/PROOF.json'))
    for file in proof_paths:
        if file.is_file():technical.append({'id':'technical/'+rel(file),
            'trajectory_type':'RETROSPECTIVE_ANALYSIS' if file.name=='OPEN_POLICY_RETROSPECTIVE.json' else 'TECHNICAL_OR_REPLAY_CONTRAST',
            'evidence':descriptor(file),'excluded_from_scientific_individual_totals':True})
    dialogues=[];dialogue_identities={}
    dialogue_paths=list(language.glob('DIALOGOS*.jsonl'))
    dialogue_paths += [root/'DIALOGOS.jsonl'] if (root/'DIALOGOS.jsonl').is_file() else []
    for file in sorted(dialogue_paths):
        if '.native.' in file.name:continue
        signature=hashlib.sha256(file.read_bytes()).hexdigest()
        if signature in dialogue_identities:
            dialogue_identities[signature].setdefault('identical_evidence_aliases',[]).append(rel(file));continue
        native=file.with_name(file.stem+'.native.jsonl')
        row={'id':'communication_session/'+file.stem,'evidence':descriptor(file),
            'native_event_companion':descriptor(native) if native.is_file() else None,
            'counts_as_scientific_individual':False,'scope':'Usability/session/replay evidence, not another association or cognitive replicate'}
        dialogue_identities[signature]=row;dialogues.append(row)
    supervision=[]
    for folder in (root/'experimentos/supervision',root/'resultados/supervision'):
        for file in sorted(folder.glob('*.json')):
            x=read(file);supervision.append({'path':rel(file),'name':x.get('name'),
                'status':x.get('status'),'exit_code':x.get('exit_code'),'duration_seconds':x.get('duration_seconds'),
                'counts_as_individual':False})
    area_counts={}
    for area in sorted({x['area'] for x in entries}):
        subset=[x for x in entries if x['area']==area]
        area_counts[area]={'target_case_records':len(subset),'trajectory_types':dict(Counter(x['trajectory_type'] for x in subset)),
                           'fresh_world_preparations_executed':sum(x['fresh_world_preparation_executed'] for x in subset)}
    ids=[x['id'] for x in entries];assert len(ids)==len(set(ids)),'Duplicate case identity'
    missing_evidence=[x['id'] for x in entries if not x['evidence']['exists']]
    assert not missing_evidence,missing_evidence
    result={'schema':'CPC3_CASE_COVERAGE_v1','generated_utc':datetime.now(timezone.utc).isoformat(),
        'generator':'compartido/index_coverage.py','classification_rule':'One primary result per case ID. Aggregate summaries, repeated ticks, dialogues and technical replays do not create independent individuals.',
        'scientific_summary':{'target_case_records':len(entries),'trajectory_types':dict(Counter(x['trajectory_type'] for x in entries)),
            'fresh_world_preparations_executed':sum(x['fresh_world_preparation_executed'] for x in entries),
            'world_preparations_note':'A fresh preparation may subsequently become a diagnostic target. BA_MEMORY_EQUALIZED and R14 D_LATE_ACTION_CUT each have one fresh prefix then one fork target, not two cases.',
            'by_area':area_counts,'independent_statistical_sample_size_not_claimed':True},
        'scientific_cases':entries,
        'reader_apparatus_discovery':{'measured_preparations':sum(x['status']=='MEASURED' for x in alternatives),
            'cases':alternatives,'excluded_from_frozen_scientific_totals':True,
            'incomplete_geometry_sweep':{'planned':9,'completed_saved':len(read(continuity/'DISCOVERY_READER.json')) if (continuity/'DISCOVERY_READER.json').is_file() else 0,
                'planned_without_completed_record':[[0,1,0],[0,1,1]],
                'supervision':'experimentos/supervision/discovery_reader_geometry.json','status':'TIMEOUT; saved completed variants retained; unfinished variants are not measured negatives'}},
        'technical_replays_and_analyses':technical,'communication_sessions':dialogues,
        'process_attempts_not_individuals':supervision,'configured_unmeasured':missing,
        'supplemental_causal_gate_note':'CAUSAL_GATE is one matched diagnostic contrast reusing BA_FULL: unedited fork, edited fork and direct channel continuation; its branches are not new independent individuals.',
        'no_inference_from_counts':'Case counts are coverage, not numbers of capacities, memories or independent statistical replications.'}
    out=root/'resultados/CASE_COVERAGE.json';out.parent.mkdir(parents=True,exist_ok=True)
    temp=out.with_suffix('.json.tmp');temp.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8');os.replace(temp,out)
    print(json.dumps({'scientific_summary':result['scientific_summary'],
                      'discovery_measured':result['reader_apparatus_discovery']['measured_preparations'],
                      'technical_artifacts':len(technical),'communication_sessions':len(dialogues),
                      'configured_unmeasured':missing},ensure_ascii=True))


if __name__=='__main__':main()
