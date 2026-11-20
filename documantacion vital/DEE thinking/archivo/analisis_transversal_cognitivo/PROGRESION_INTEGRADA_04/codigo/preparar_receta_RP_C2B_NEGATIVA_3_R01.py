"""Documentary recipe draft for the ACTUAL three-opportunity C2B failure.

No RP/product write, Native import or execution. A twenty-opportunity positive
recipe is explicitly blocked because the original trial stopped after three.
Root will later provide the exact preserved compatible code capsule.
"""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

if __name__=='__main__':
    folder=P/'codigo/REPRODUCIBILIDAD_C2B_NEGATIVA_R01'
    if folder.exists():raise ValueError('Preserve prior documentary recipe draft')
    folder.mkdir()
    actual=[];unique={}
    for i in range(3):
        file=P/'ensayos'/('PI04_C2B_REAL_DEV_R01_OP_'+str(i)+'.json')
        outer=json.loads(file.read_text(encoding='utf8'));native=json.loads(outer['result']);r=native['result']['rows'][0]
        if r['ordinal']!=i:raise ValueError('Actual three-opportunity order differs')
        groups=[r['requests'],r['native_arithmetic']['native_operation']['native_trial']['requests'],r['second_native_use']['requests']]
        for group in groups:
            for q in group:
                receipt=q['receipt'];rid=q['id']
                if rid!=receipt['id']or not r['before_tick']<=receipt['requested_tick']<=r['after_tick']:raise ValueError('Invalid/inherited receipt scope')
                if rid in unique and unique[rid]!=receipt:raise ValueError('Contradictory alias')
                unique[rid]=receipt
        actual.append({'ordinal':i,'file':str(file),'sha256':sha(file),'native':native,'row':r})
    statuses=[r['status']for r in unique.values()]
    expected={'unique_requested':len(unique),'applied':sum(x=='applied'for x in statuses),
              'rejected':sum(x.startswith('rejected')for x in statuses),
              'pending_or_other':sum(x!='applied'and not x.startswith('rejected')for x in statuses)}
    if expected!={'unique_requested':561,'applied':559,'rejected':2,'pending_or_other':0}:raise ValueError('Negative closure differs from original evidence')
    step=lambda label,literal,**kw:{'label':label,'literal':literal,'feedback':'omit',**kw}
    steps=[step('prepare',{'modo':'eci01-pi04-c2b-preparar'},require_zero_ticks=True),
           step('admit',{'modo':'eci01-pi04-c2b-admitir','brazo':'real'},require_zero_ticks=True)]
    checks=[]
    receipt_paths=[['result','rows',0,'requests'],['result','rows',0,'native_arithmetic','native_operation','native_trial','requests'],['result','rows',0,'second_native_use','requests']]
    for item in actual:
        i=item['ordinal'];label='opportunity_%02d'%i
        steps.append(step(label,{'modo':'eci01-pi04-c2b-oportunidad'},read_path=['result','rows',0,'first_reader','choice'],
                          receipt_paths=receipt_paths,stop_on_NULL=True))
        checks.append({'label':'actual_product_%02d'%i,'operation':'value',
                       'values':[{'step':label,'path':['result','rows',0,'useful_product']}],
                       'expected':item['row']['useful_product']})
    # The third response has terminal FI rejections. No fourth material step
    # is present. The existing generic runner closes its owner after this list.
    physical=actual[-1]['native']['committed_snapshot']['physical']
    for key in('N','tick','RAW_sha256','clocks_sha256'):
        checks.append({'label':'exact_negative_final_'+key,'operation':'value',
                       'values':[{'step':'opportunity_02','path':['committed_snapshot','physical',key]}],
                       'expected':physical[key]})
    recipe={'schema':'DEE.reproduction.recipe.v1','id':'pi04_c2b_fallo_admision_3_R01',
        'title':'PI04 C2B: reproducción acotada del cierre adverso tras3ofertas; no capacidad positiva validada',
        'revision':'PREPARED_BLOCKED_PENDING_ROOT_EXACT_CAPSULE','prefix':'PI03_PI04_C2_NULL_T798033',
        'code_capsule_key':'PI04_C2B_R01_NEGATIVA_ROOT_PENDING','required_life_prefix':'ECI02_PI03_REPRO_PI04_',
        'reproduction_enabled':False,'variants':{'real_tres_con_rechazos':{'batches':[steps],
            'final_checks':checks,'native_receipt_expectations':expected}},
        'modalities':{'A':'Actual three primary JSONs and known561/559/2 receipt groups read and deduplicated passively',
            'B':'Prepared bounded Native reproduction from genuine full inherited798033 prefix, NOT RUN through RP',
            'C':'Three attempted contextual experiences, stopped before acquisition/reserve completed; not twenty validated cases',
            'D':'No new ability or principal adoption inferred','E':'No recovery claim'},
        'assistance':'Prepared symmetric sensor, sequence/codecs/calendar/environment; Root original produced every action with Native. This recipe copies no acquired state into another life.',
        'limitations':'NEGATIVE scientific target:1/3real products,3formed25 scalars,2terminal FI occupied-register rejections in third opportunity. Matching these observables is reproduction of a failure, not a cognitive/global PASS. Original metadata uncertainFalse covered only outer7; all FI/MU receipts are explicitly included here. No fourth material step, retries, cleanup or twenty-case claim.',
        'verification':{'state':'DOCUMENTARY_DRAFT_NOT_NATIVE_EXECUTED','actual_original_root_opportunities':3,
            'actual_original_products':1,'exact_original_Native_receipts':expected,'exact_original_final_physical':physical,
            'primary_refs':[{'path':r['file'],'sha256':r['sha256']}for r in actual],
            'generic_RP_Native_replay':False,'Source_original_code':'pi04_coordinacion_simetrica_C2B.py d77dea2b...; exact compatible preserved capsule must be selected by Root'},
        'usage':{'listar':'sistema/gestionar.py reproducibilidad listar',
            'verificar':'sistema/gestionar.py reproducibilidad verificar pi04_c2b_fallo_admision_3_R01',
            'reproducir':'sistema/gestionar.py reproducibilidad reproducir pi04_c2b_fallo_admision_3_R01 --variante real_tres_con_rechazos --vida ECI02_PI03_REPRO_PI04_RP_C2B_NEG_01 --destino <NUEVO_DESTINO_DIAGNOSTICO>'},
        'blockers':['Root has not yet selected/preserved the exact compatible final or historical code capsule for this recipe','This draft is NOT installed in RP and cannot be executed','No new twenty-opportunity C2B evidence exists; positive acquisition20 must remain unclaimed']}
    target=folder/'pi04_c2b_fallo_admision_3_R01.json';target.write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    blocked={'schema':'PI04.C2B.twenty_recipe.NOT_EXECUTED.v1','status':'BLOCKED_NO_20_CASES','planned_prefix':'PI03_PI04_C2_NULL_T798033',
        'actual_original_completed':3,'actual_original_tick':800379,'reserve_executed':False,'Native_RP_replay':False,
        'scope':'Design may be preserved, but cannot stand for a reproduced/validated20-case capability. Any later C2C continuation has a different instrument, key and genuine800379 parent.'}
    (folder/'C2B_ADQUISICION20_NO_REALIZADA.json').write_text(json.dumps(blocked,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    proof={'schema':'PI04.C2B.negative_recipe.documentary_prepared.R01','recipe':str(target),'recipe_sha256':sha(target),
        'actual_original_receipts':expected,'actual_original_products':sum(x['row']['useful_product']for x in actual),
        'actual_original_final_tick':physical['tick'],'Native_ticks_executed_by_helper':0,'RP_modified':False,
        'source_originals_unchanged':True,'status':'PREPARED_DISABLED_NOT_NATIVE_REPLAYED'}
    out=P/'control/RP_C2B_NEGATIVA3_PREPARADA_R01.json';out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(proof,ensure_ascii=False,indent=2))
