"""Compact, passive calibration and retrospective readings of saved worlds.

This tool never advances, edits, probes or reconstructs a native world. Six
SEM01 historical states are separate saved worlds, not new physical replicas.
New prospective observer preparations are run by the campaign's native runner.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import digest, put, sha, NATIVE_SHA
from src.observers import o1_ports,o2_fields,o4_torus,moore_context,patch_sites,torus_distance,o3_segments

PARENT_SHA='1c10b8501ff0bb9756d6b1ebe5876a63ae7300ec4722d651e94dfe9e8f45a0f6'
PREFIX='CPC3/experimentos/SEM01_SIGNIFICADO_ADQUIRIDO/'
SELECTIONS={
 'A':'resultados/confirmacion/A_future_UV',
 'B':'resultados/confirmacion/B_future_UV',
 'LESION':'resultados/causal_memory02/MEM_REMOVE',
 'SHAM':'resultados/causal_memory02/SHAM_REMOVE',
 'RESERVED_A':'resultados/confirmacion/RESERVED_A_codec7_shift',
 'RESERVED_B':'resultados/confirmacion/RESERVED_B_codec7_order_shift',
}
OUT=ROOT/'resultados/observadores'
REF=ROOT/'referencias/SEM01/seleccionados'

def frozen_config():
    path=ROOT/'configuraciones/OBSERVER_CALIBRATION_CONFIG.json'
    value={'id':'CPC4.observer_calibration.v1','created_utc':datetime.now(timezone.utc).isoformat(),
      'modality':'A_RETROSPECTIVE_READING_OF_HISTORICAL_SAVED_WORLDS',
      'selection':SELECTIONS,'N':67,'scales':[1,2,4,8],
      'normalization':'integer coordinates on actual torus; port-relative displacement; no RAW/clock floats',
      'nodes':'RAW!=0 including inactive and orphan; activity is a separate state>0 and semantic!=5 field',
      'functional_feature':'active and emitter+4*direction modulo67 equals declared native cost meeting',
      'evaluation':'compare native optional-resource delivery measured later, not learned-class labels',
      'scope':'No native execution; old reserves remain historical calibration; new reserve config separate',
      'persistent_homology':'NOT_EXECUTED_NETWORK_PERMISSION; no GUDHI or PH result claimed'}
    if path.exists():
        old=json.loads(path.read_text(encoding='utf-8'))
        assert old['selection']==SELECTIONS
    else:put(path,value)
    return path

def extract(parent):
    assert sha(parent)==PARENT_SHA,'Parent identity differs'
    config=frozen_config()
    provenance={'parent_zip':str(parent),'parent_sha256':PARENT_SHA,'config_sha256':sha(config),
                'extraction':'Twelve targeted members only; originals untouched','members':[]}
    with zipfile.ZipFile(parent) as z:
        lines=z.read(PREFIX+'HASHES.sha256').decode('utf-8-sig').splitlines()
        expected={}
        for line in lines:
            if not line.strip():continue
            h,name=line.split(maxsplit=1);expected[name.lstrip('*').replace('\\','/')]=h
        for label,rel in SELECTIONS.items():
            for filename in ('MEASUREMENTS.json','EMISSION_S1.deetsnap'):
                member=PREFIX+rel+'/'+filename;payload=z.read(member)
                h=hashlib.sha256(payload).hexdigest();key=rel+'/'+filename
                candidates=[key,'SEM01_SIGNIFICADO_ADQUIRIDO/'+key,PREFIX+key]
                found=next((expected[x] for x in candidates if x in expected),None)
                assert found==h,(member,'Internal hash absent or different',found,h)
                target=REF/label/filename;target.parent.mkdir(parents=True,exist_ok=True)
                if target.exists():assert sha(target)==h
                else:target.write_bytes(payload)
                provenance['members'].append({'label':label,'member':member,'path':str(target.relative_to(ROOT)),
                                               'sha256':h,'bytes':len(payload),'internal_manifest_verified':True})
    put(REF/'PROVENANCE.json',provenance)
    return provenance

def action_ray(record,meeting,n=67):
    endpoint=[(record['site'][i]+4*record['direction'][i])%n for i in range(3)]
    return {'active':record['active'],'endpoint_after_four_ticks':endpoint,
            'cost_meeting':meeting,'candidate':bool(record['active'] and endpoint==meeting),
            'scope':'Frozen kinematic candidate; later physical resource delivery is an independent readout'}

def historical():
    import dee_thinking as d
    results=[]
    for label in SELECTIONS:
        m=json.loads((REF/label/'MEASUREMENTS.json').read_text(encoding='utf-8'))
        use=next(x for x in m['uses'] if x['signal']=='S1')
        center=use['anticipation']['emission']['physical']['site']
        w=d.OrganizationalWorld.load_snapshot(str(REF/label/'EMISSION_S1.deetsnap'))
        before=digest(w)
        ports=o1_ports(w,{'emission':center})
        full=o2_fields(w,max_nonzero=4096)
        local=o2_fields(w,patch_sites(center,67,1))
        graph=o4_torus(full,(1,2,4,8),{'emission':center})
        local_graph=o4_torus(local,(1,2,4),{'emission':center})
        context=moore_context(w,center)
        # A second observation is deliberately redundant to check passivity.
        assert ports==o1_ports(w,{'emission':center})
        after=digest(w);assert before==after
        live=ports['emission'];assert live==use['anticipation']['emission']['physical'] | {'nonzero_raw':live['raw']!=0}
        prediction=action_ray(live,use['bank']['cost_meeting'])
        evaluation=use['evaluation']
        row={'id':'SEM01_'+label,'type':'A_RETROSPECTIVE_PASSIVE_READING','evidence':str((REF/label).relative_to(ROOT)),
             'port':live,'action_geometry':prediction,'observed_optional_delivery':evaluation['resource_delivery'],
             'observed_primary_delivery':evaluation['function_delivery'],'physical_profile':evaluation['profile'],
             'geometry_agrees_with_observed_cost':prediction['candidate']==(not evaluation['resource_delivery']),
             'full_O4':graph,'local_O4':local_graph,'passive_digest_before':before,'passive_digest_after':after,
             'passive_equal':before==after,'snapshot_is_distinct_saved_world':True,
             'all_tick_clocks_integers':all(type(x['clock']) is int for x in full['records'])}
        put(OUT/'SEM01'/label/'O1_O2_O3.json',{'ports':ports,'full_integer_frame':full,'local_context':context})
        put(OUT/'SEM01'/label/'MEASUREMENTS.json',row);results.append(row)
    a,b=results[0],results[1]
    counter={'comparison':['SEM01_A','SEM01_B'],
             'same_local_support':a['local_O4']['support_sha256']==b['local_O4']['support_sha256'],
             'same_emission_site':a['port']['site']==b['port']['site'],
             'same_load':a['port']['s_reg']==b['port']['s_reg'],
             'same_clock':a['port']['clock']==b['port']['clock'],
             'directions':[a['port']['direction'],b['port']['direction']],
             'physical_profiles':[a['physical_profile'],b['physical_profile']],
             'scope':'Spatial occupancy alone does not retain the measured directional action distinction. Full worlds need not be identical.'}
    summary={'historical_worlds_read':len(results),'new_native_runs':0,'passive_equal':all(x['passive_equal'] for x in results),
             'counterexample':counter,'functional_feature_matches_cost':sum(x['geometry_agrees_with_observed_cost'] for x in results),
             'rows':[{k:v for k,v in x.items() if k not in ('full_O4','local_O4')} for x in results]}
    put(OUT/'SEM01_CALIBRATION.json',summary)
    return summary

def saved_frame(trace):
    records={tuple(r['site']):dict(r,nonzero_raw=r['raw']!=0) for r in trace['samples'].values()}
    return {'N':67,'tick':trace['tick'],'records':list(records.values()),'truncated':False,
            'scope':'Declared sampled ports only; not complete universe, missing nodes are unknown rather than absent'}

def native_reread():
    names=['FULL_PLUS','MAIN_MINUS','A_NAIVE','B_NAIVE','B_WRONG_RELATION',
           'B_ROUTE_COMPONENT_REMOVED','B_ACQUIRED_COMPONENT_REMOVED','CUT_PLUS','CUT_MINUS',
           'RESERVED_TRANSLATION_PLUS','RESERVED_TRANSLATION_MINUS_SWAPPED',
           'OBSERVER_NEW_PLUS','OBSERVER_NEW_MINUS_WRONG_Z']
    rows=[]
    for name in names:
        path=ROOT/'resultados/confirmacion'/name/'MEASUREMENTS.json'
        if not path.exists():
            # New reserves may be saved in their own finite appendix.
            path=next(iter(ROOT.glob('resultados/observer_reserved*/'+name+'/MEASUREMENTS.json')),path)
        if not path.exists():continue
        saved=json.loads(path.read_text(encoding='utf-8'));p=saved.get('physical',saved)
        if 'B_common_responses' not in p:continue
        responses={}
        for part,r in p['B_common_responses'].items():
            side='plus' if part=='Bplus' else 'minus'
            responses[side]={'record':r,'action_geometry':action_ray(r,p['spec']['banks'][side]['cost_meeting']),
                             'native_effect':p['evaluations'][side]}
        frames=[saved_frame(t) for t in p['trace']]
        graph_frames=[{'scope':'SAMPLED_PORT_GRAPH_NOT_COMPLETE','O4':o4_torus(f,(1,2,4,8))}
                      for f in frames if f['tick'] in (70,82,88,149,155,162,169)]
        row={'id':name,'analysis_type':'A_RETROSPECTIVE_READING' if not name.startswith('OBSERVER_NEW') else 'FROZEN_OBSERVER_RESERVE',
             'source':str(path.relative_to(ROOT)),'source_sha256':sha(path),'case':p['case'],
             'emission':p['A_emission'],'contacts':p['B_contacts'],'responses':responses,
             'external_utility':p['external_utility'],'diagnostic_edits':p['diagnostic_edits'],
             'graph_frames':graph_frames,'coverage':'Observed ports plus explicitly saved local contexts; not complete causal graph'}
        put(OUT/'R2'/(name+'.json'),row);rows.append(row)
    lookup={r['id']:r for r in rows}
    dy=lookup.get('B_ROUTE_COMPONENT_REMOVED');dz=lookup.get('B_ACQUIRED_COMPONENT_REMOVED')
    contrast=None
    if dy and dz:
        a=dy['responses']['minus']['record'];b=dz['responses']['minus']['record']
        contrast={'ids':[dy['id'],dz['id']],
            'same_site_clock_load_after_query':all(a[k]==b[k] for k in ('site','clock','s_reg','state','semantic')),
            'directions_after_common_query':[a['direction'],b['direction']],
            'utility':[dy['external_utility'],dz['external_utility']],
            'profiles':[dy['responses']['minus']['native_effect']['profile'],dz['responses']['minus']['native_effect']['profile']],
            'mechanism':'The common query supplies Y and compensates the removed dy component; it does not supply Z. Acquired dz persists as an independently necessary route component in this tested background.',
            'limit':'The single-field interventions establish these conditional contrasts, not universal necessity or information measure.'}
    summary={'read_cases':len(rows),'new_native_runs':0,'ids':[r['id'] for r in rows],
             'direction_context_compensation':contrast,'rows':[{'id':r['id'],'utility':r['external_utility'],
               'response_directions':{s:x['record']['direction'] for s,x in r['responses'].items()},
               'action_candidates':{s:x['action_geometry']['candidate'] for s,x in r['responses'].items()}} for r in rows]}
    put(OUT/'R2_REANALYSIS.json',summary)
    return summary

def lexical_reread():
    path=ROOT/'resultados/INVERSE_MECHANISM/SUMMARY.json'
    if not path.exists():return None
    m=json.loads(path.read_text(encoding='utf-8'));rows=[]
    for w in m['windows']:
        h=w['frozen_hypothesis'];frames=[]
        for sample in w['samples']:
            records=[dict(v,nonzero_raw=v['raw']!=0) for k,v in sample.items() if isinstance(v,dict) and 'raw' in v]
            frames.append({'N':67,'tick':sample['tick'],'records':records,'truncated':False})
        segments=[{'id':'forward','start_site':h['hub'],'start_tick':h['forward_birth'],'direction':h['forward_direction']},
                  {'id':'unpaired_teacher','start_site':h['hub'],'start_tick':h['teacher_birth'],'direction':h['teacher_direction']}]
        rows.append({'id':h['id'],'source':str(path.relative_to(ROOT)),'classification':w['classification'],
                     'window':[h['start_tick'],h['end_tick']],'predicted_meeting':h['meeting'],
                     'collision_tick':h['collision_tick'],'segments':o3_segments(frames,segments,67),
                     'meeting_context':[{k:v for k,v in s.items() if k in ('tick','candidate_meeting','next_meeting')} for s in w['samples'] if s['tick']>=h['collision_tick']-1],
                     'scope':'Reanalysis of saved replay samples. Kinematic compatibility plus observed meeting is not a hidden stored lexical response; missing late readout must be interpreted with this finite interference window.'})
    refinement=ROOT/'resultados/INVERSE_MECHANISM/OCCUPIED_REFINEMENT/MATERIAL_BRANCH.json'
    occupied=None
    if refinement.exists():
        x=json.loads(refinement.read_text(encoding='utf-8'))
        occupied={'source':str(refinement.relative_to(ROOT)),'source_sha256':sha(refinement),
          'classification':x['classification'],'pending_inputs_at_source':x['pending_inputs_at_source'],
          'external_operation_journal_unchanged':x['external_operation_journal_unchanged'],
          'transition':[286,287],
          'centers':{name:{k:v for k,v in value.items() if k!='moore26'} for name,value in x['pre286'].items()},
          'post':x['post287'],'technical_field_checks':x['technical_field_checks'],
          'mechanism':x['mechanism'],'distinction_from_W1':x['distinction_from_W1'],'scope':x['scope']}
    put(OUT/'LEXICAL_TEMPORAL_CONTEXT.json',{'source_sha256':sha(path),'new_native_runs':0,
        'windows':rows,'occupied_destination_refinement':occupied,
        'interpretation_update':'The W2 ballistic meeting at320 is not the true transition: saved refinement localizes loss at occupied destinations286→287. Context and branch precedence invalidate extrapolating an unobserved free segment.'})
    return rows

def prospective_reserves():
    import dee_thinking as d
    config_path=ROOT/'configuraciones/OBSERVER_RESERVED_CONFIG.json'
    config=json.loads(config_path.read_text(encoding='utf-8'));rows=[]
    assert sha(config_path)=='500b6b78e61899e9a4009e6ea5dfa3e56266317e70fa60c63306754a75be7be8'
    for expected in config['cases']:
        folder=ROOT/'resultados/observer_reserved'/expected['id']
        if not (folder/'MEASUREMENTS.json').exists():continue
        m=json.loads((folder/'MEASUREMENTS.json').read_text(encoding='utf-8'));p=m.get('physical',m)
        comparisons=[]
        for key,actual in [('predicted_A_emission',p['A_emission']),
                           ('predicted_B_contact',p['B_contacts'][expected['predicted_B_contact']['role']]),
                           ('predicted_common_response',p['B_common_responses'][expected['predicted_common_response']['role']])]:
            for field,value in expected[key].items():
                if field=='role':continue
                comparisons.append({'component':key,'field':field,'expected':value,'observed':actual[field],
                                    'exact_equal':value==actual[field]})
        response_role=expected['predicted_common_response']['role']
        response_side='PLUS' if response_role=='Bplus' else 'MINUS'
        snapshot=folder/'NATIVO'/('AFTER_COMMON_QUERY_'+response_side+'.deetsnap')
        world=d.OrganizationalWorld.load_snapshot(str(snapshot));before=digest(world)
        full=o2_fields(world,max_nonzero=4096)
        ports=o1_ports(world,p['spec']['centers'])
        o4=o4_torus(full,(1,2,4,8),p['spec']['centers'])
        after=digest(world);assert before==after
        response=p['B_common_responses'][response_role]
        assert ports[response_role]==dict(response,nonzero_raw=response['raw']!=0)
        candidates={}
        for role,r in p['B_common_responses'].items():
            side='plus' if role=='Bplus' else 'minus'
            feature=action_ray(r,p['spec']['banks'][side]['cost_meeting'])
            candidates[side]=feature['candidate']
        for side,value in expected['predicted_action_candidates'].items():
            comparisons.append({'component':'action_candidates','field':side,'expected':value,
                                'observed':candidates[side],'exact_equal':value==candidates[side]})
        for side,value in expected['predicted_profiles'].items():
            observed=p['evaluations'][side]['profile']
            comparisons.append({'component':'physical_profiles','field':side,'expected':value,
                                'observed':observed,'exact_equal':value==observed})
        comparisons.append({'component':'external_evaluator_only','field':'utility','expected':expected['predicted_utility'],
                            'observed':p['external_utility'],'exact_equal':expected['predicted_utility']==p['external_utility']})
        row={'id':expected['id'],'classification':'PROSPECTIVE_OBSERVER_RESERVE_FROZEN_BEFORE_EXECUTION',
          'source':str((folder/'MEASUREMENTS.json').relative_to(ROOT)),
          'config_sha256':sha(config_path),'checks':comparisons,'exact_equal_fields':sum(x['exact_equal'] for x in comparisons),
          'total_fields':len(comparisons),'all_exact':all(x['exact_equal'] for x in comparisons),
          'snapshot':str(snapshot.relative_to(ROOT)),'snapshot_sha256':sha(snapshot),'passive_before':before,'passive_after':after,
          'passive_equal':before==after,'physical_profile':{s:p['evaluations'][s]['profile'] for s in ('plus','minus')},
          'scope':'Two distinct finite preparations, not repeated ticks or independent bits. Geometry classifier was frozen, not fitted. Known historical reserves remain retrospective.'}
        put(OUT/'RESERVES'/(expected['id']+'_O1_O2_O4.json'),{'ports':ports,'frame':full,'O4':o4})
        put(OUT/'RESERVES'/(expected['id']+'.json'),row);rows.append(row)
    summary={'config_sha256':sha(config_path),'read_preparations':len(rows),'expected_preparations':2,
        'native_runs_by_observer_tool':0,'cases':rows,
        'all_exact':len(rows)==2 and all(r['all_exact'] for r in rows),
        'scope':'Frozen finite geometric and field predictions tested on two new native worlds generated by the campaign runner. No PH or global state classifier claim.'}
    put(OUT/'OBSERVER_RESERVED_VALIDATION.json',summary)
    return summary

def main():
    import dee_thinking as d
    assert d.__version__=='4.0.0' and d.kernel_identity()['kernel_version']==27
    assert sha(d._native.__file__)==NATIVE_SHA
    parser=argparse.ArgumentParser();parser.add_argument('--parent',type=Path);parser.add_argument('--reanalyze-only',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    if not args.reanalyze_only:
        assert args.parent is not None
        provenance=extract(args.parent)
        # Save extraction first, before loading any historical state.
        put(OUT/'INCREMENTAL_STATUS.json',{'status':'REFERENCES_EXTRACTED','members':len(provenance['members'])})
        sem=historical()
    else:sem=json.loads((OUT/'SEM01_CALIBRATION.json').read_text(encoding='utf-8')) if (OUT/'SEM01_CALIBRATION.json').exists() else None
    native=native_reread();lex=lexical_reread();reserves=prospective_reserves()
    summary={'status':'MEASURED','SEM01_historical_worlds':sem['historical_worlds_read'] if sem else 0,
      'CPC4_saved_trajectories_read':native['read_cases'],
      'CPC4_retrospective_trajectory_reanalyses':native['read_cases']-reserves['read_preparations'],
      'new_native_trajectories_created_by_this_tool':0,
      'observer_code_sha256':sha(ROOT/'src/observers.py'),'calibration_runner_sha256':sha(__file__),
      'instrument':{'library':d.__version__,'kernel':27,'native_sha256':NATIVE_SHA,
                    'python':sys.executable,'module':d.__file__},
      'passive_checks_equal':sem['passive_equal'] if sem else None,
      'persistent_homology':'NOT_EXECUTED_NETWORK_PERMISSION','GUDHI':'not installed; socket WinError10013; permitted attempt aborted; no further attempt',
      'prospective_observer_reserves':reserves['read_preparations'],'frozen_reserve_predictions_exact':reserves['all_exact'],
      'remaining':'No persistent-homology execution; graph and directional results have the finite coverage stated in each artifact',
      'lexical_windows':len(lex) if lex else 0}
    put(OUT/'RUN_SUMMARY.json',summary);print(json.dumps(summary))

if __name__=='__main__':main()
