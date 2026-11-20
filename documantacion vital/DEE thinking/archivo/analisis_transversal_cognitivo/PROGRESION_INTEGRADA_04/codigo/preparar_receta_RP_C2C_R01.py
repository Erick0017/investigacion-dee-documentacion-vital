"""Prepare C2C acquisition20 recipe from exact CLOSED originals, or a blocked template.

No Native/RP/product mutation. Root supplies the final compatible capsule after
operational guard review. Observed expectations are added only from closed20
primary records, never guessed from a desired score or a planned protocol.
"""
from pathlib import Path
import argparse,hashlib,json
P=Path(__file__).resolve().parents[1];R=P.parent.parent.parent
RP=R/'DEE Cognitive 2.0/reproducibilidad'
RECIPE='pi04_c2c_adquisicion_20_R01'
PREFIX='PI03_PI04_C2B_STOP_T800379'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def bounded(file):
    p=Path(file).resolve(strict=True)
    if not p.is_relative_to(P.resolve())or p.is_symlink():raise ValueError('Directed original within PI04 only')
    return p
def value_at(value,path):
    for part in path:value=value[part]
    return value

def steps(arm,plan=None):
    admit={'modo':'eci01-pi04-c2c-admitir','brazo':arm}
    if arm=='yoked':
        if type(plan)is not str or not plan.startswith('E3Z1:'):raise ValueError('Original frozen packed20-signal control plan required')
        admit['plan']=plan
    zero=lambda label,literal:{'label':label,'literal':literal,'feedback':'omit','require_zero_ticks':True}
    first=[zero('prepare',{'modo':'eci01-pi04-c2c-preparar'}),zero('admit',admit)]
    last=[]
    for i in range(20):
        row={'label':'opportunity_%02d'%i,'literal':{'modo':'eci01-pi04-c2c-oportunidad'},'feedback':'omit',
            'read_path':['result','rows',0,'first_reader','choice'],'stop_on_NULL':True,'stop_on_unapplied_receipt':True,
            'preserved_stop_paths':[['result','rows',0,'first_NULL_preserved'],['result','rows',0,'first_rejected_preserved']],
            'receipt_paths':[['result','rows',0,'requests']],
            'nullable_receipt_paths':[['result','rows',0,'native_arithmetic','native_operation','native_trial','requests'],
                                      ['result','rows',0,'second_native_use','requests']]}
        (first if i<12 else last).append(row)
    last.append(zero('final_state',{'modo':'eci01-pi04-c2c-estado'}))
    return [first,last]

def inspect_closed_batches(files,arm):
    if not files:return None
    rows=[];batch_refs=[]
    for name in files:
        file=bounded(name);b=read(file)
        if b.get('schema')!='DEE.PI04.C2C.actual_batch.R01'or b.get('owner_closed')is not True or b.get('arm')!=arm:
            raise ValueError('Actual closed C2C batch/arm required')
        if b.get('stop_reason')is not None or b.get('status')!='COMPLETED_REQUESTED_BATCH':
            raise ValueError('A stopped partial history is not a completed20 acquisition recipe')
        rows.extend(b['rows']);batch_refs.append({'path':str(file),'sha256':sha(file)})
    if [r['ordinal']for r in rows]!=list(range(20)):raise ValueError('Exactly the actual first20, no duplicates/omissions/retention')
    receipts={};actual=[];life=None;last_tick=800379
    for i,row in enumerate(rows):
        file=bounded(row['primary']);raw=read(file)
        if raw.get('status')!='completed':raise ValueError('A completed outer transport primary required')
        native=json.loads(raw['result'])if isinstance(raw['result'],str)else raw['result']
        r=native['result']['rows'][0]
        if r['ordinal']!=i or r['before_tick']!=last_tick:raise ValueError('Native genealogy/window is not consecutive from800379')
        if r.get('first_NULL_preserved')or r.get('first_rejected_preserved'):raise ValueError('A preserved failure must remain a negative recipe, not20positive acquisition')
        actual_life=native['committed_snapshot']['life_id']
        if life is None:life=actual_life
        if life!=actual_life:raise ValueError('Multiple lives cannot be merged as one twenty-opportunity acquisition')
        last_tick=r['after_tick']
        groups={'outer':r['requests'],'FI':r['native_arithmetic']['native_operation']['native_trial']['requests'],'MU':r['second_native_use']['requests']}
        local={}
        for group,items in groups.items():
            for request in items:
                rid=request['id'];receipt=request['receipt']
                if type(rid)is not int or rid!=receipt['id']or not r['before_tick']<=receipt['requested_tick']<=r['after_tick']:raise ValueError('Inherited/outside-window receipt')
                if rid in local and local[rid]!=receipt:raise ValueError('Contradictory stage alias')
                local[rid]=receipt
                if rid in receipts and receipts[rid]!=receipt:raise ValueError('Contradictory global Native alias')
                receipts[rid]=receipt
        summary=r['native_input_summary']
        if summary['unique_requested']!=len(local)or summary['applied']!=sum(q['status']=='applied'for q in local.values()):raise ValueError('Native quality gate differs from direct new-call groups')
        if any(q['status']!='applied'for q in local.values()):raise ValueError('Complete acquisition requires all direct Native inputs admitted')
        actual.append({'ordinal':i,'primary':str(file),'sha256':sha(file),'row':r,'physical':native['committed_snapshot']['physical']})
    statuses=[q['status']for q in receipts.values()]
    return {'life':life,'actual':actual,'batches':batch_refs,'physical':actual[-1]['physical'],
            'receipt_expectations':{'unique_requested':len(receipts),'applied':sum(x=='applied'for x in statuses),
                                    'rejected':sum(x.startswith('rejected')for x in statuses),
                                    'pending_or_other':sum(x!='applied'and not x.startswith('rejected')for x in statuses)}}

def expectations(history):
    checks=[]
    for item in history['actual']:
        checks.append({'label':'actual_product_%02d'%item['ordinal'],'operation':'value',
            'values':[{'step':'opportunity_%02d'%item['ordinal'],'path':['result','rows',0,'useful_product']}],
            'expected':item['row']['useful_product']})
        checks.append({'label':'actual_number_%02d'%item['ordinal'],'operation':'value',
            'values':[{'step':'opportunity_%02d'%item['ordinal'],'path':['result','rows',0,'actual_numeric_result']}],
            'expected':item['row']['actual_numeric_result']})
    checks.append({'label':'exact_twenty_completed','operation':'value',
        'values':[{'step':'final_state','path':['result','rows',0,'progress','ordinal']}],'expected':20})
    checks.append({'label':'exact26resources_six_remain','operation':'value',
        'values':[{'step':'final_state','path':['result','rows',0,'device','ordinal']}],'expected':20})
    for key in('N','tick','RAW_sha256','clocks_sha256'):
        checks.append({'label':'exact_final_physical_'+key,'operation':'value',
            'values':[{'step':'final_state','path':['committed_snapshot','physical',key]}],
            'expected':history['physical'][key]})
    return checks

def build(capsule_key,histories,plan=None,analysis=None):
    variants={};blockers=[]
    for arm in('real','none','yoked'):
        history=histories.get(arm)
        if arm=='yoked'and plan is None:continue
        variant={'batches':steps(arm,plan if arm=='yoked'else None)}
        if history is not None:
            variant.update(final_checks=expectations(history),native_receipt_expectations=history['receipt_expectations'])
        else:
            variant['final_checks']=[]
            variant['not_yet_executed_original_reference']=True
        variants[arm]=variant
    if histories.get('real')is None:blockers.append('No complete actual closed real DEV12+RES8; expected results remain absent')
    if capsule_key=='ROOT_FINAL_CAPSULE_PENDING':blockers.append('Root must preserve/select the final compatible capsule after operational guards')
    r={'schema':'DEE.reproduction.recipe.v1','id':RECIPE,'title':'PI04 C2C: adquisición contextual20 en copia desde el prefijo real800379',
        'revision':'R01_PREPARED_NOT_NATIVE_CLI_RUN','prefix':PREFIX,'code_capsule_key':capsule_key,
        'required_life_prefix':'ECI02_PI03_REPRO_PI04_','reproduction_enabled':False,'variants':variants,
        'modalities':{'A':'Documentary direct-record recalculation, not a new DEE experiment',
            'B':'Use of inherited physical history, with one original scalar datum and fixed earlyQ reader',
            'C':'New C2C acquisition relative to genuine pre-C2C800379 state; not reconstruction/acquisition of the whole life fromT0',
            'D':'Available in a principal only if Root actually adopts the complete successor; not implied by recipe registration',
            'E':'No autonomous repair. Earlier reader and two-tick output hold are prepared instrumentation'},
        'assistance':'Prepared query0, one datumq3, fixed centralQq4 signature held toq6, efferenceq7, output-to-function/route codecs, sequence, environment law and finite26resource supply. Only actual Native outputs select operations/routes; reference expectations never enter material literals.',
        'limitations':'PREPARED recipe, not a Native RP replay or global PASS. Original20 and future cold-clone replay are separate modalities. Old C2 halted11 and C2B failed3 histories remain untouched. Stop on any NULL/rejected/unreconciled inner-stage input; no retries, favourable readers, input restoration or T0.26prepared,20consumed leaves6external offers; no metaphorical metabolism. Same-prefix controls are not independent organisms.',
        'verification':{'state':'PREPARED_NO_NEW_NATIVE_CLI_REPLAY','original_histories':{
            k:None if v is None else{'life':v['life'],'batches':v['batches'],'opportunities':20,
                'products':sum(q['row']['useful_product']for q in v['actual']),'expected_final_physical':v['physical'],
                'exact_direct_receipts':v['receipt_expectations']}for k,v in histories.items()},
            'new_generic_RP_Native_replay':False,'all_original_expectations_recalculated_from_closed_primaries':histories.get('real')is not None},
        'usage':{'listar':'sistema/gestionar.py reproducibilidad listar',
            'verificar':'sistema/gestionar.py reproducibilidad verificar '+RECIPE,
            'recalcular':'sistema/gestionar.py reproducibilidad recalcular --receta '+RECIPE+' --destino <DIRECTORIO_NUEVO>',
            'reproducir':'sistema/gestionar.py reproducibilidad reproducir '+RECIPE+' --variante real --vida ECI02_PI03_REPRO_PI04_RP_C2C_01 --destino <DESTINO_DIAGNOSTICO_NUEVO>'},
        'blockers':blockers}
    if analysis is not None:r['analysis']=analysis
    return r

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--destino',type=Path,required=True)
    ap.add_argument('--capsule-key',default='ROOT_FINAL_CAPSULE_PENDING')
    for arm in('real','none','yoked'):ap.add_argument('--'+arm+'-batch',action='append',type=Path,default=[])
    ap.add_argument('--yoked-plan',type=Path);ap.add_argument('--analysis-entry',type=Path)
    a=ap.parse_args();dest=a.destino.resolve()
    if not dest.is_relative_to(P.resolve())or dest.exists():raise ValueError('New explicit PI04 destination only, no overwrite')
    histories={arm:inspect_closed_batches(getattr(a,arm+'_batch'),arm)for arm in('real','none','yoked')}
    plan=read(bounded(a.yoked_plan))if a.yoked_plan else None
    if plan is not None and(type(plan)is not str or not plan.startswith('E3Z1:')):raise ValueError('Only original packed control string')
    analysis=read(bounded(a.analysis_entry))if a.analysis_entry else None
    r=build(a.capsule_key,histories,plan,analysis)
    if a.capsule_key!='ROOT_FINAL_CAPSULE_PENDING':
        resources=read(RP/'RECURSOS.json')
        if a.capsule_key not in resources.get('code_capsules',{}):raise ValueError('Root final capsule not yet preserved; no fabricated resource reference')
    dest.mkdir(parents=True)
    file=dest/(RECIPE+'.json');file.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    proof={'schema':'PI04.C2C.RP_recipe.prepared.v1','recipe':str(file),'sha256':sha(file),
        'actual_real20_reference_present':histories['real']is not None,'capsule_key':a.capsule_key,
        'reproduction_enabled':False,'RP_modified':False,'Native_ticks':0,
        'next':'Root preserves portable evidence/final capsule, statically verifies and installs; then Root alone executes cold-clone Native20 and registers actual proof. No acquisition claimed from this builder.'}
    (dest/'PREPARACION_SIN_NATIVE.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(proof,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
