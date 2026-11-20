"""Root-authorized standalone48-trajectory budget/source comparison, zero Native.

Uses existing reference policies and workshop. Only tag/goal bits plus own
post-effect binary feedback reach choose(). Prepared reference20 and correct
tool map are supplied, not learned. Empty initial cache differs from lived E1.
Artifacts remain exactly regenerable from grouped rows; no thousands of files.
"""
from pathlib import Path
import argparse,copy,gzip,hashlib,importlib.util,json,shutil

HERE=Path(__file__).resolve().parent
OUT=HERE/'REFERENCIAS_CUATRO_NIVELES_CERRADO_R03'
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
def dump(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(canonical(v))
def model(path):
    spec=importlib.util.spec_from_file_location('standalone_existing_conventional_model',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def plan():
    trials=[]
    for n in(2,5,10,20):
        for arm in('constant20','twenty_per_source'):
            h=20 if arm=='constant20'else 20*n;u=h//20
            for seed in(40411,40412):
                trials.append({'sources':n,'dose_arm':arm,'opportunities':h,'seed':seed,'goal_tag':0,'word':'clasifica',
                    'loads':[8,4],'criterion':20,'equality_policy':'measured_unformed',
                    'agenda':[{'at':5*u+1,'goal_tag':1,'replace_values':True},
                              {'at':12*u+1,'goal_tag':0,'replace_values':True,'rotar':1}]})
    return {'schema':'APD04.conventional_budget.fixed_goal_only.R03','status':'CERRADO_PARA_REFERENCIAS_CONVENCIONALES',
        'authorization':'Root GO option(b):fixed clasifica,0→1→0 goals5:7:8,48trajectories,4920opportunities,one execution,no Native.',
        'policies':['fija_ciclo_INSPECT_INSPECT_USE','WSLS_estandar_global','WSLS_adaptativa_por_dos_bits_publicos'],
        'trials':trials,'prepared_relation20':True,'training_acquisition_cost_excluded':True,
        'equality_NULL_no_extra_zero_arm':True,'not_matched_to_lived_MAIN_or_its_incremental_world':True,
        'no_actor_control':'No Native module/world/process; these supplied conventional policies never act for E1.',
        'selector_information':['current tag bit','current goal_tag bit','own past actions and binary actual-effect feedback'],
        'executor_information':'Prepared relation20, actual legitimate cache and task mapping. Auditor fields recorded only after effect.',
        'cache':'Initially empty; value replacement increments versions WITHOUT clearing old cache or bins. Second inversion rotates environmental object ordering by1, without policy reset.',
        'inferences_excluded':['No learned word association','No matched historical training cost','No20simultaneous full variables','NoNative superiority/inferiority from these synthetic runs']}
def artifact(row):
    if row['chosen_before_effect']!='USE':return None
    return canonical({'schema':'APD04.synthetic.conventional.effect.v1','episode':row['episode'],
        'source_id':row['public_before']['source_id'],'tool_emitted':row['public_before']['word'],
        'effect':row['committed_effect'],'conventional_not_Native':True})
def metrics(rows):
    return {'opportunities':len(rows),'elemental_selector_samples':2*len(rows),
        'INSPECT':sum(r['chosen_before_effect']=='INSPECT'for r in rows),'USE':sum(r['chosen_before_effect']=='USE'for r in rows),
        'useful':sum(bool(r['committed_effect']['useful'])for r in rows),
        'new_facts':sum(bool(r['committed_effect']['new_fact'])for r in rows),
        'correct_classifications':sum(bool(r['committed_effect'].get('correct'))for r in rows),
        'incorrect_classifications':sum(r['committed_effect'].get('correct')is False for r in rows),
        'unformed':sum(r['committed_effect'].get('reason')=='no_unique_conventional_classification_model_of_measured_Native_gap'for r in rows),
        'stale_cached_facts_before':sum(r['auditor_only_after_effect']['cached_version_before']is not None and r['auditor_only_after_effect']['cached_version_before']!=r['auditor_only_after_effect']['actual_version']for r in rows),
        'artifact_count':sum(r['artifact']is not None for r in rows),
        'regenerated_artifact_bytes':sum(r['artifact']['bytes']for r in rows if r['artifact'])}
def trajectory(m,config,policy_name):
    world=m.Workshop(config);policy=m.POLICIES[policy_name]();rows=[]
    for _ in range(config['opportunities']):
        ex=world.exogenous();public=world.public();bits=[public['tag'],public['goal_tag']]
        action=policy.choose(tuple(bits))
        # Private source version is NOT available to choose or the executor.
        actual=copy.deepcopy(next(o for o in world.objects if o['id']==public['source_id']))
        effect,operation=world.commit(action,copy.deepcopy(public));category='SUCCESS'if effect['useful']else'FAILURE'
        policy.outcome(tuple(bits),category)
        row={'episode':world.episode,'exogenous_before':ex,'public_before':public,'selector_observation':bits,
            'chosen_before_effect':action,'operation':operation,'committed_effect':effect,'feedback':category,
            'auditor_only_after_effect':{'actual_value':actual['value'],'actual_version':actual['version'],
                'cached_version_before':None if actual['observed']is None else actual['observed']['version'],'criterion':world.criterion}}
        b=artifact(row);row['artifact']=None if b is None else{'sha256':sha(b),'bytes':len(b),'template':'APD04.synthetic.conventional.effect.v1/canonical_sorted_indent2_UTF8_LF'}
        if b is not None and artifact(row)!=b:raise ValueError('Artifact bytes failed regeneration before file exclusion')
        rows.append(row)
    return rows
def run():
    if OUT.exists():raise FileExistsError('Preserve existing conventional grid; do not repeat')
    OUT.mkdir();source=HERE/'referencias_taller_n0.py';m=model(source);start=m.resources()
    shutil.copy2(Path(__file__),OUT/Path(__file__).name);shutil.copy2(source,OUT/source.name)
    closed=plan();dump(OUT/'PLAN_CERRADO_ANTES_EJECUCION.json',closed)
    reports=[]
    for config in closed['trials']:
        for policy_name in closed['policies']:
            key='case_'+str(len(reports)).zfill(3);r0=m.resources();rows=trajectory(m,config,policy_name)
            packet={'schema':'APD04.conventional_grouped_primary.R03','config':config,'policy':policy_name,'rows':rows,'new_native_ticks':0}
            b=canonical(packet);z=gzip.compress(b,compresslevel=9,mtime=0);p=OUT/'TRAYECTORIAS'/(key+'.json.gz');p.parent.mkdir(exist_ok=True);p.write_bytes(z)
            if gzip.decompress(p.read_bytes())!=b:raise ValueError('Primary compression is not lossless')
            r1=m.resources();reports.append({'id':key,'policy':policy_name,'config':config,'metrics':metrics(rows),
                'primary':p.relative_to(OUT).as_posix(),'primary_sha256':sha(z),'primary_decompressed_sha256':sha(b),
                'compressed_bytes':len(z),'expanded_bytes':len(b),'resources_before':r0,'resources_after':r1,
                'cpu_ns':r1['process_cpu_ns']-r0['process_cpu_ns'],'wall_ns':r1['monotonic_ns']-r0['monotonic_ns']})
    end=m.resources();dump(OUT/'RESULTADOS_Y_RECURSOS.json',{'schema':'APD04.conventional_grid_report.R03','reports':reports,
        'new_native_ticks':0,'sources_sha256':{source.name:sha(source.read_bytes()),Path(__file__).name:sha(Path(__file__).read_bytes())},
        'whole_process_resources_before':start,'whole_process_resources_after':end,
        'whole_process_cpu_ns':end['process_cpu_ns']-start['process_cpu_ns'],'whole_process_wall_ns':end['monotonic_ns']-start['monotonic_ns'],
        'scope':'Own conventional process, including grouped encoding/writes; not matched historical training, Native CPU, environment-wide energy or realtime.',
        'artifact_exclusion':'Each USE artifact reconstructed identically before exclusion; canonical template+effect+episode+source+word+hash+size exported. No unique artifact content discarded.'})
    dump(OUT/'RECALCULO_INDEPENDIENTE.json',replay(OUT))
    manifest=[{'file':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in sorted(OUT.rglob('*'))if p.is_file()]
    dump(OUT/'MANIFIESTO.json',{'members':manifest,'self_hash_excluded':True})
    print(json.dumps({'trajectories':len(reports),'opportunities':sum(r['metrics']['opportunities']for r in reports),'files':len(manifest)+1,
        'bytes':sum(r['bytes']for r in manifest),'output':str(OUT),'new_native_ticks':0},ensure_ascii=False))
def replay(base):
    m=model(base/'referencias_taller_n0.py');closed=json.loads((base/'PLAN_CERRADO_ANTES_EJECUCION.json').read_bytes());report=json.loads((base/'RESULTADOS_Y_RECURSOS.json').read_bytes());checks=[]
    for r in report['reports']:
        p=base/r['primary'];z=p.read_bytes();b=gzip.decompress(z);packet=json.loads(b)
        checks.extend([{'case':r['id'],'check':'primary_encoded_sha256','ok':sha(z)==r['primary_sha256']},
            {'case':r['id'],'check':'primary_decoded_sha256','ok':sha(b)==r['primary_decompressed_sha256']}])
        repeated=trajectory(m,packet['config'],packet['policy'])
        checks.append({'case':r['id'],'check':'exact_rows_from_closed_plan','ok':repeated==packet['rows']})
        checks.append({'case':r['id'],'check':'metrics_from_rows','ok':metrics(packet['rows'])==r['metrics']})
        for row in packet['rows']:
            a=artifact(row)
            checks.append({'case':r['id'],'episode':row['episode'],'check':'excluded_artifact_exact_regeneration',
                'ok':a is None if row['artifact']is None else sha(a)==row['artifact']['sha256']and len(a)==row['artifact']['bytes']})
        if packet['config']not in closed['trials']or packet['policy']not in closed['policies']:raise ValueError('Unplanned trajectory')
    return {'schema':'APD04.conventional_grid_replay.R03','checks':checks,'check_count':len(checks),'issues':[x for x in checks if not x['ok']],
        'new_native_ticks':0,'scope':'Recalculation of archived conventional protocol/effects/artifacts; not new Native experiment or independent acquisition sample.'}
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run-authorized-once',action='store_true');ap.add_argument('--replay',type=Path);a=ap.parse_args()
    if a.run_authorized_once:run()
    elif a.replay:
        r=replay(a.replay);print(json.dumps({'new_native_ticks':0,'checks':r['check_count'],'issues':r['issues']},ensure_ascii=False))
    else:ap.error('Choose explicit authorized execution or archived replay')
