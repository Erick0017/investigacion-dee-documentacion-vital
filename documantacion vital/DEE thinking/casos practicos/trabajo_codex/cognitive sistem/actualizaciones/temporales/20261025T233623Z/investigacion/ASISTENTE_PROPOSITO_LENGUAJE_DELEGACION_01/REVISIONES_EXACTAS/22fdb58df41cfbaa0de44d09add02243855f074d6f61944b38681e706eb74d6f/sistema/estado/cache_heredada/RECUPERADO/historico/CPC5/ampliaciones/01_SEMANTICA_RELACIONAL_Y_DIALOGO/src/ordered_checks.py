"""Post-trajectory calculations for ordered composition; never feeds MAIN."""
from pathlib import Path
import argparse
import json
import sys

HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from common import put,sha,digest,operational
from ordered_composition import OrderedSession,KEY


def measure(path):
    x=json.loads(path.read_text(encoding='utf-8'));order=x['geometry']['order']
    primary=x['primary_observations'];first=primary['first_encounter']['sites'][order[0]+'.meeting']
    second=primary['second_encounter']['sites'][order[1]+'.meeting']
    banks={k:v for k,v in primary['environment_contact']['sites'].items()if k.startswith('bank.')}
    backups={k:v for k,v in primary['retention']['sites'].items()if k.endswith('backup_post_query')}
    return {'case_id':x['case']['id'],'phase':x['case']['phase'],'file':str(path),
            'sha256':sha(path),'source_sha256':x['source_sha256'],'order':order,
            'first':first,'second':second,'banks':banks,'backups':backups,
            'resources':x['resources'],'interventions':x['interventions'],'technical_original':x['technical'],
            'exact_loads_not_float':True,'same_scalar_does_not_imply_same_vector_or_route':True}


def reanalyse(path,out):
    x=json.loads(path.read_text(encoding='utf-8'));session=OrderedSession.load(path.parent/'T73.deetsnap')
    saved=x['operative_final']['metadata'][KEY]
    loaded=session.world.runtime.snapshot_metadata(KEY)
    comparisons={'physical_equal':digest(session.world)==x['final'],
                 'literal_saved_metadata_equal_after_load':loaded==saved,
                 'canonical_JSON_session_equal':session.state==json.loads(saved),
                 'channels_receipts_equal':{k:operational(session.world)[k]for k in('channels','receipts','protocols')}=={k:x['operative_final'][k]for k in('channels','receipts','protocols')}}
    assert all(comparisons.values())
    result={'schema':'CPC5.extension.ordered.technical-reanalysis.v1','status':'VERIFIED',
            'original_measurement':str(path),'original_sha256':sha(path),'original_technical':x['technical'],
            'correction':'The first implementation compared in-memory tuple coordinates to their JSON-restored list representation. Canonical serialized JSON and the actual persisted metadata match; physics and calls are unchanged.',
            'comparisons':comparisons,'new_evolution_ticks':0,'new_inputs':0,
            'original_record_preserved':True,'scope':'Technical reanalysis, not a new independent physical execution'}
    put(out,result);print(json.dumps(result,ensure_ascii=False,indent=2))


def reconstruct_transitions(paths,root):
    """Audit only: complete saved Moore prestates, not participant computation."""
    result=[]
    for path in paths:
        x=json.loads(path.read_text(encoding='utf-8'))
        for component,pre_tick,post_tick in ((x['geometry']['order'][0],10,11),(x['geometry']['order'][1],15,16)):
            context=next(w for w in x['local_transition_windows']if w['tick']==pre_tick and w['component']==component)
            center=tuple(context['site']);neighbors=context['neighborhood']
            assert len(neighbors)==27 and len({tuple(r['site'])for r in neighbors})==27
            c=next(r for r in neighbors if tuple(r['site'])==center)
            others=[r for r in neighbors if tuple(r['site'])!=center]
            active=[r for r in others if r['state']>0 and r['semantic']!=5]
            def offset(row):
                return tuple(((row['site'][i]-center[i]+33)%67)-33 for i in range(3))
            gradients=[-sum(offset(r)[i]*r['s_reg']for r in others if r['state']>0)for i in range(3)]
            grad_mag=sum(abs(v)for v in gradients)
            orphan=any(r['semantic']==5 for r in others)
            crystallization=bool(active)and grad_mag//19665>=int(9.887**3)and not orphan
            # All 26 neighbors are covered; less than eight active neighbors
            # suffices to exclude XNOR regardless of the symmetric-pair count.
            xnor_excluded_by_active_minimum=len(active)<8
            incoming=[r for r in others if any(r['direction'])and
                      tuple((r['site'][i]+r['direction'][i])%67 for i in range(3))==center]
            actual=next(r for r in x['trace']if r['tick']==post_tick)['sites'][component+'.meeting']
            branch='NOT_RESOLVED_BY_THIS_AUDITOR';predicted=None
            if c['state']==0 and c['semantic']!=4 and not crystallization and xnor_excluded_by_active_minimum:
                if incoming:
                    summed=[sum(r['direction'][i]for r in incoming)for i in range(3)]
                    direction=[(v>0)-(v<0)for v in summed]
                    predicted={'state':1,'semantic':1,'s_reg':min(19664,sum(r['s_reg']for r in incoming)),
                               'direction':direction,'clock':str(int(c['clock'])+1)}
                    branch='VACUUM_DIRECTIONAL_REDUCER_'+str(len(incoming))+'_SOURCES'
                else:
                    predicted={'state':0,'semantic':0,'s_reg':0,'direction':[0,0,0],'clock':str(int(c['clock'])+1)}
                    branch='VACUUM_NO_DIRECTIONAL_SOURCE'
            matches=None if predicted is None else {k:actual[k]==v for k,v in predicted.items()}
            result.append({'case_id':x['case']['id'],'source':str(path.relative_to(root)),
                'source_sha256':sha(path),'component':component,'pre_tick':pre_tick,'post_tick':post_tick,
                'coverage':'Complete center plus26Moore neighbors saved; raw/clocks remain exact decimal strings.',
                'center_pre':c,'n_active':len(active),'gradients':gradients,'gradient_magnitude':grad_mag,
                'crystallization_guard':crystallization,'XNOR_excluded_by_active_less_than8':xnor_excluded_by_active_minimum,
                'incoming_directional_records':incoming,'branch_reconstructed_from_code_and_prestate':branch,
                'passive_inspector_original':context['gate'],'predicted_fields_in_auditor_only':predicted,
                'observed_post':actual,'field_matches':matches,
                'causal_attribution':'Local branch reconstruction. Necessity and sufficiency require the separate interventions; a matching branch is not unique whole-history genealogy.'})
    return {'schema':'CPC5.extension.ordered-local-reconstruction.v1','transitions':result,
            'kernel_source':'CPC5/referencias/producto4/kernel_v27.cpp',
            'kernel_source_sha256':'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31',
            'scope':'Post-trajectory external calculations. The public session never imports or consumes this reconstruction.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=HERE.parent)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--reanalyse',type=Path)
    args=p.parse_args()
    if args.reanalyse:return reanalyse(args.reanalyse,args.output)
    rows=[];paths=[]
    for path in sorted(args.root.glob('resultados/ordered*/**/MEASUREMENTS.json')):
        if json.loads(path.read_text(encoding='utf-8')).get('schema')=='CPC5.extension.ordered-composition.measurements.v1':rows.append(measure(path));paths.append(path)
    mapping={r['case_id']:r for r in rows};a=mapping.get('ORDERED_D01_AB');b=mapping.get('ORDERED_D02_BA')
    comparison=None
    if a and b:
        comparison={'cases':[a['case_id'],b['case_id']],
            'same_final_load':a['second']['s_reg']==b['second']['s_reg'],
            'different_final_directions':a['second']['direction']!=b['second']['direction'],
            'AB_direction':a['second']['direction'],'BA_direction':b['second']['direction'],
            'same_initial_material_and_component_budget':a['resources']==b['resources'],
            'preparation_difference':'Nominal first/second encounter geometry encodes the operation order; not autonomous inference of temporal order',
            'physical_law':'Each simultaneous reducer is commutative. Sign normalization between temporally separate encounters makes the ordered composition noncommutative for these vectors.'}
    result={'schema':'CPC5.extension.ordered.post-trajectory.v1','primary_records':len(rows),
            'rows':rows,'equal_inventory_order_comparison':comparison,
            'formulas':{'second_direction':'direct exact dx/dy/dz observation after the second encounter',
                        'retention':'one common backup query at67 reaches each separately experienced support at70; report state/load/direction without coding silence as zero'},
            'scope':'Ordered physical operation; no automatic accreditation of ANTES/DESPUES, pronouns or abstract semantic composition',
            'calculations_do_not_return_to_MAIN':True}
    put(args.output,result)
    put(args.output.with_name('ORDERED_TRANSITION_RECONSTRUCTION.json'),reconstruct_transitions(paths,args.root))
    print(json.dumps({'records':len(rows),'output':str(args.output),'sha256':sha(args.output)}))


if __name__=='__main__':main()
