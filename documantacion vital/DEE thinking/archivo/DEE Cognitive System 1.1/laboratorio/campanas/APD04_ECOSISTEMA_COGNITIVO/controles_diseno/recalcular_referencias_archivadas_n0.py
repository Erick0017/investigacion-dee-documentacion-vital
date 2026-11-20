"""N0 deterministic audit of conventional primaries and real artifact bytes.

Does not run a DEE world or new comparison trial. Recomputes the already
archived actions/effects from their exact plan using a conventional model.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


def read(path):return json.loads(path.read_text(encoding='utf8'))


def main():
    p=argparse.ArgumentParser();p.add_argument('folder');p.add_argument('output');args=p.parse_args()
    folder=Path(args.folder).resolve(strict=True);out=Path(args.output)
    if out.exists():raise FileExistsError('Keep prior recalc')
    code=Path(__file__).with_name('referencias_taller_n0.py')
    spec=importlib.util.spec_from_file_location('conventional_only_reference_model',code);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    issues=[];checks=0;cases=[]
    for source in sorted(folder.glob('case_*/PRIMARIOS_CONVENCIONALES.json')):
        body=read(source);world=module.Workshop(body['config']);policy=module.POLICIES[body['policy']]();derived=[]
        for row in body['rows']:
            exogenous=world.exogenous();public=world.public();bits=[public['tag'],public['goal_tag']]
            action=policy.choose(tuple(bits));effect,operation=world.commit(action,public)
            category='SUCCESS'if effect['useful']else'FAILURE';policy.outcome(tuple(bits),category)
            for name,expected,actual in [('exogenous',exogenous,row['exogenous_before']),('public',public,row['public_before']),
                ('selector_bits',bits,row['selector_observation']),('action',action,row['chosen_before_effect']),
                ('effect',effect,row['committed_effect']),('operation',operation,row['operation']),('feedback',category,row['feedback'])]:
                checks+=1
                if expected!=actual:issues.append({'case':source.parent.name,'episode':row['episode'],'field':name,'expected':expected,'actual':actual})
            if row['artifact']:
                artifact=source.parent/row['artifact'];actual=read(artifact);checks+=3
                if actual['effect']!=effect or actual['source_id']!=public['source_id']or actual.get('conventional_not_Native')is not True:
                    issues.append({'case':source.parent.name,'episode':row['episode'],'field':'actual_artifact_bytes'})
            derived.append({'action':action,'effect':effect})
        counts={'opportunities':len(derived),'INSPECT':sum(r['action']=='INSPECT'for r in derived),
                'USE':sum(r['action']=='USE'for r in derived),'useful':sum(bool(r['effect']['useful'])for r in derived),
                'new_facts':sum(bool(r['effect']['new_fact'])for r in derived),
                'correct_classifications':sum(bool(r['effect'].get('correct'))for r in derived),
                'gap_reducing_moves':sum(r['effect'].get('gap_after',0)<r['effect'].get('gap_before',0)for r in derived)}
        original=read(source.parent/'RECALCULO_Y_RECURSOS.json')
        for key,value in counts.items():
            checks+=1
            if original.get(key)!=value:issues.append({'case':source.parent.name,'field':key,'calculated':value,'reported':original.get(key)})
        cases.append({'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                      'policy':body['policy'],'equality_policy':body['config']['equality_policy'],'counts':counts})
    # A codec unit check is separate from archived E1/pilot opportunities.
    equality=[]
    for mode in('measured_unformed','conventional_neutral_zero'):
        cfg={'seed':40401,'sources':2,'word':'equilibra','loads':[6,6],'goal_tag':0,'criterion':20,'equality_policy':mode}
        world=module.Workshop(cfg);effect,operation=world.commit('USE',world.public())
        equality.append({'model':mode,'operation':operation,'effect':effect,'scope':'Conventional transduction unit test, NOT a Native calibration or E1 experience'})
        checks+=1
        if operation['conventional_balance']!=(None if mode=='measured_unformed'else 0):issues.append({'field':'conventional_equality_model','mode':mode})
    result={'schema':'APD04.conventional_primary_recalculation.N0.R01','checks':checks,'issues':issues,'cases':cases,
            'new_native_ticks':0,'new_comparison_trajectories':0,'conventional_equality_unit_checks':equality,
            'source_code_sha256':hashlib.sha256(code.read_bytes()).hexdigest(),
            'resource_scope':'Original OS measurements are preserved, not reconstructed from effect values. R01 short monotonic intervals were coarse0/15ms; do not interpret0 as zero cost.',
            'pilot_equality_scope':'Neither model changes pilot scores because no pilot USE invoked equal loads; CALIB_R02 is separate Native evidence.'}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'checks':checks,'issues':len(issues),'archived_cases':len(cases),'new_native_ticks':0}))


if __name__=='__main__':main()
